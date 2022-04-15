# Complex/Production Ready Pterradyctal setup


This example has following additional capabilities in addition to the simple example.
* S3 backend
* Encrypted secrets
* Streamlined tags support

---

Table of content
* [Creating infrastructure for a new AWS account](#newaccount)
* [Infra folder](#infrafolder)
* [Creating stacks for new projects](#newstack)
* [Remote S3 backend support](#remotebackend)
* [Encrypted files support (sops)](#sops)
* [Streamlined tags support](#tags)

# <a name="newaccount"></a> Creating infrastructure for a new AWS account
Before we start creating stacks for our projects, we need to define a new AWS account and create basic infrastructure for it. See [infra](../complex/vars/project/infra/) example.
Let's call new AWS account a `common` one

1. Create mapping for your new account:
   - edit [common.yaml](../complex/vars/common.yaml):
    ```
  deployment:
    product: '%{product}'
    n: '%{n}'
    account_families:
      'teama-aws-account': 'teama'
      'teamb-aws-account': 'teamb'
      '_default_': 'common' # <-- add default for common account.
    account_family_code: 
      teama: 'a'
      teamb: 'a'
      common: 'c' # --> new account
    account_type_code: 
      test: 't'
      prod: 'p'
    ```

3. Add your account ID.
   - edit [common.yaml](../complex/vars/common.yaml)
   ```yaml
   account_ids:
      - '123456789011'   # <-- account id for common account
      - '123456789012'
   ```
4. Apply changes defined here [infra](../complex/vars/project/infra) via Pterradactyl:
    ```bash
    pt apply ct-infra0-uswest2
    ```
   This will create all the AWS resources including backend bucket for TF.

   **Note**: If you need to apply it for prod account or for different region, the procedure is exactly the same.

5. Workaround for remote bucket creation.

   TF needs a bucket to save its state in the new account but the bucket is created using TF.\
   To solve this, go to [common.yaml](../complex/vars/common.yaml), and comment out the terraform backend:
   - ```yaml
     terraform:
     #backend:
       #s3:
         #bucket: '%{account_prefix}-infra0-global-terraform'
         #dynamodb_table: '%{account_prefix}-infra0-uswest2-terraform'
         #region: us-west-2
         #key: '%{state_prefix}'
     ```
   - Again run the pt apply command: 
     - `pt apply ct-infra0-uswest2`
   - Revert changes in [common.yaml](../complex/vars/common.yaml)
   - Again run the pt apply command:
     - `pt apply ct-infra0-uswest2`

# <a name="infrafolder"></a> Infra folder
We are supposed to create a basic deployment to keep our stacks backend remotely on S3 bucket.
In general, we deploy only one infra and share it among stacks.
Take a look into [infra](../complex/vars/project/infra) folder to see what is the minimum for deploying infra stack.

# <a name="newstack"></a> Creating stacks for new projects
A below complex example of creating new projects based on AWS provider. 

We have an organization named complex\
They have 2 teams
- teama
    - teama has only one project going on, named projecta and it's deployed both in test and prod account
- teamb
    - teamb have 2 projects
        - projectb - deployed in test and prod
        - projectc - This is a long project to put out the projectc, it's still in test.

This is how the stack looks like for teams

|  Team | Project  | Account Type  |  Stack Name |  Stack contents |
|---|---|---|---|---|
| teama |projecta    | test         | at-projecta       | s3 (bucket-1), dynamodb(stream_enabled: false) |
|       |            | prod         | ep-projecta       | s3 (bucket-1), dynamodb(stream_enabled: true) |
| teamb |projectb | test         | bt-projectb    | s3 (bucket-1), |
|       |            | prod         | vp-projectb    | s3 (bucket-1), SQS ( fifo: false) |
|       |projectc     | test         | bt-projectc        | s3 (bucket-1), s3 (bucket-2), dynamodb(stream_enabled: false), SQS ( fifo: true) |

As you could see [here](../complex/terraform/modules). We are using much more modules than in the Simple project [here](../simple/terraform/modules)
Additional modules used here:
- **resource_metadata** - for streamlined tags support. Example of usage [here](../complex/terraform/modules/s3/metadata.tf)
- **least_privilege** - S3 needs this module to apply policies on a given bucket. Example of usage for KMS module [here](../complex/terraform/modules/kms/main.tf)
- **known_roles** - define list of account IDs and map Okta role names. See [known_roles](../complex/terraform/modules/known_roles) for more details and example of usage [here](../complex/vars/common.yaml).
- **kms** used for encrypted files support. See _Encrypted files support (sops)_ section for more details and review [kms](../complex/terraform/modules/kms) module and example of usage [here](../complex/vars/project/infra/deployment/ct-infra0-uswest2.yaml).
- **deployment** - to propagate common tags, metadata and for naming strategy. See [deployment](../complex/terraform/modules/deployment) module and example of usage [here](../complex/vars/common.yaml).
- **iam_role** - to define required policies for access to given resources. See [iam_role](../complex/terraform/modules/iam_role) module and example of usage [here](../complex/vars/project/infra/deployment/ct-infra0-uswest2.yaml).

Each account can have more than one version of the same stack, meaning you can have integration stack running in the test account. \
These different stacks could be effectively just copies of one another or could have overrides like in prod instance the size of the node or db might be different than the test account.\
The above is a very typical setup where every account needs some common things and Prod and Test are slightly different from each other.\
Now, its time you open up the examples directory and check out the structure for the simple project.\
Lets checkout the state of the stack for teama in the test accounts using the following command

`pt plan at-projecta0-uswest2.yaml`

- e - teama
- projecta - project
- 0 - version of the stack
- uswest2 - region of the deployment

Similarly as for [Simple](../simple) project let's understand the file that rules it all - pterra.yaml
```yaml
---
# This is standard hiera config though the ruby :symbols are optional
hiera:
  # List all supported backend types
  backends:
    - yaml
    - json
    - yaml.enc

# Hierarchy dictates the order of overrides
# e.g. if s3 bucket name is specified in common and for the same bucket a different name is given in `project/%{project}/deployment/%{deployment}`, 
# the bucket gets created with the name specified in `project/%{project}/deployment/%{deployment}`

# NOTE: Remember that files names under account directory (according to below hierarchy) should match your aws account aliases
# e.g. projecta-test.yaml, projecta-prod.yaml.enc

hierarchy:
    - common
    - account/%{aws_account_alias}
    - account_type/%{account_type}
    - project/%{project}/common
    - project/%{project}/account/%{aws_account_alias}
    - project/%{project}/account_type/%{account_type}
    - project/%{project}/deployment/%{deployment}

  yaml:
    datadir: vars

  json:
    datadir: vars

  yaml.enc:
    datadir: vars

# Specify acronyms here
# This is derived from stack name e.g. vt acronym in bt-projecta-na-uswest2 stack name.
simple:
  family:
    a: teama
    b: teamb
  account_type:
    t: test
    p: production

# Facter expects arrays of dicts. this is used for ordering.
# If you want to ensure one fact is processed after another. This is because
# some types of facters can reference values of facts defined by other facters.
facter:
  # Arguments facter simply defines command line arguments whose values are directly used as facts
  - arguments:
      deployment:
        positional: true
        description: Deployment ID
      stage:
        alias: s
        description: Stage name (test, dev, stage, prod)
      project:
        alias: p
        description: project name (projecta, write_poetry, ...)

# Specify regex to extract variables from the stack name
  - regex:
      source: deployment
      expression: (?P<family>\w)(?P<account_type>\w)-(?P<project>[a-z]+)(?P<n>\d+)-(?P<region>\w+)
      transforms:
        - account_type: "{{ config['simple']['account_type'][account_type] }}"
        - family: "{{ config['simple']['family'][family] }}"
        - region: '{{ region[0:2] }}-{{region[2:-1]}}-{{region[-1]}}'

    # sets facts based on the output of an arbitrary shell command, this should be a one line output
    # and will be trimmed
  - shell:
      git_sha: git rev-parse HEAD
      aws_account_alias:
        command: echo "projecta-test" #aws iam list-account-aliases
        #jsonpath: $.AccountAliases[0]

    # facts set from the value of an environment variable
    environment:
      deploy_user: USER

  # State backend facts
  - regex:
      source: deployment
      expression: (?P<account_prefix>\w\w)
      transforms: {}

  - jinja:
      state_prefix: |
        {{ deployment }}.tfstate.json

terraform:
  # Set the Terraform version required in this repo. pterradactyl will automatically fetch it
  version: 0.13.1
  cache_key: deployment
  plugins:
  # List the plugins which are not available through Terraform plugin registry
    - repo: terraform-provider-kubectl
      owner: gavinbunney
      version: '>=1.10.0'
  module_path:
   # Terraform plugin relative directory
    - terraform/modules

pterradactyl: <-- version of the pterradctyl library
  version: '>=1.2.0'

```



Similarly, you can do all the terraform commands (apply, state, etc) on any of these stacks.

e.g. do apply on teamb projectc project
`pt apply bt-projectc0-useast1.yaml` 

This stack has a remote backend, type: S3.

# <a name="remotebackend"></a> Remote S3 backend support

To store your backend remotely, in one of your common.yaml top hierarchy file, e.g. [here](../complex/vars/common.yaml), one have to provide below information: 
```yaml
terraform:
  backend:
    s3:
      bucket: '%{account_prefix}-infra0-global-terraform'
      dynamodb_table: '%{account_prefix}-infra0-uswest2-terraform'
      region: us-west-2
      key: '%{state_prefix}'
```
Variables to provide:

**bucket** - name of S3 bucket that will be created to store your remote backend.\
**dynamodb_table** - name of a dynamodb table where Terraform puts information regarding state locking.\
**region** - region where your infra is getting created.\
**key** - name of a state file, set to '%{state_prefix}' e.g. _ct-infra0-uswest2.tfstate.json_

Under S3 bucket '_%{account_prefix}-infra0-global-terraform_' you will see backend state file e.g. _ct-infra0-uswest2.tfstate.json_


# <a name="sops"></a> Encrypted files support (sops)
Installation guide for installing sops under Mac OS can be found [here](https://formulae.brew.sh/formula/sops)
Installation guide for installing sops from pypi can be found [here](https://pypi.org/project/sops/)

If you want to provide encrypted credentials as YAML configuration one should create separate file with .enc extension.
E.g. [here](../complex/vars/account/projectb-prod.yaml.enc)

#### Encrypting

First add you secrets in the YAML file [example](../complex/vars/account/projectb-prod.yaml.enc) in the following way:

```yaml
module:
    dynamodb:
        secret_key: <secret_value>
```

If you are done, encrypt content of a file using _sops_ tool:

```bash
sops -e -i --input-type=yaml --output-type=yaml -kms=arn:aws:kms:us-west-2:<accoutn-id>:alias/common-alias vars/account/projectb-prod.yaml.enc
```
Note: If you are not sure what should be common-alias, simply get it from the command:

```bash
 aws iam list-account-aliases
```

As a response, you should get something like this:

```json
{
    "AccountAliases": [
        "projectb-test"
    ]
}
```

Once encryption process was successful, your file should be encrypted and at the very end sops content should be added:

```yaml
sops:
    kms:
        - arn: arn:aws:kms:us-west-2:<account-id>:alias/common-alias
          created_at: "2021-09-24T02:48:33Z"
          enc:
          aws_profile: ""
    gcp_kms: []
    azure_kv: []
    hc_vault: []
    age: []
    lastmodified: "2021-09-24T02:48:34Z"
    mac: ENC[]
    pgp: []
    unencrypted_suffix: _unencrypted
    version: 3.7.1
```

#### Decrypting
Decrypting is as simple as running below sops command:

```bash
sops -d -i --input-type=yaml --output-type=yaml vars/account/projectb-prod.yaml.enc
```

# <a name="tags"></a> Streamlined tags support.
To propagate tags, metadata across all resources look at [resource_metadata](../complex/terraform/modules/resource_metadata) generic module.

Any tags you want to propagate across all resources, simply create metadata.tf file like for [s3](../complex/terraform/modules/s3/metadata.tf) module.

which uses generic Terraform module (resource_metadata): 

```terraform
module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata
  tags     = var.tags
  instanced_resources = {
    "s3"                = [var.name]
  }
}
```

When you use this module in your stack, simply pass tags or/and metadata:

```yaml
---
manifest:
  modules:
    - s3
      
module:
  s3:
    tags: local.tags
    metadata: local.metadata
```
