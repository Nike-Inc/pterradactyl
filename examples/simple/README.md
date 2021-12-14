# Simple pterradyctal setup


We have an organization named simple
They have 2 teams
- team1
    - team1 has only one project going on, named projecta and its deployed both in test and prod account
- team2
    - team2 have 2 projects
        - projectb - deployed in test and prod
        - projectc - This is a long project to put out the projectc, its still in test.
        
This is how the stack looks like for teams

|  Team | Project  | Account Type  |  Stack Name |  Stack contents |
|---|---|---|---|---|
| team1 | projecta    | test         | et-projecta       | s3 (bucket-1), dynamodb(stream_enabled: false) |
|       |            | prod         | ep-projecta       | s3 (bucket-1), dynamodb(stream_enabled: true) |
| team2 | projectb | test         | vt-projectb    | s3 (bucket-1), | 
|       |            | prod         | vp-projectb    | s3 (bucket-1), SQS ( fifo: false) |
|       |projectc     | test         | vt-projectc        | s3 (bucket-1), s3 (bucket-2), dynamodb(stream_enabled: false), SQS ( fifo: true) |



Each account can have more than one version of the same stack, meaning you can have intergation stack running in the test account. \
These different stacks could be effectively just copies of one another or could have overrides like in prod instance the size of the node or db might be different than the test account.\
The above is a very typical setup where every account needs some common things and Prod and Test are slightly different from each other.\
Now, its time you open up the examples directory and check out the structure for the simple project.\
lets checkout the state of the stack for team1 in the test accounts using the following command

`pt plan et-projecta0-na-uswest2.yaml`

- e - team1
- t - test environment
- projecta - project name
- 0 - version of the stack
- na - serving region
- uswest2 - region of the deployment

Let's understand the file that rules it all - pterra.yaml
```yaml
---
# This is standard hiera config though the ruby :symbols are optional
hiera:
  # list all supported backend types
  backends:
    - yaml
    - json

# Hierarchy dictates the order of overrides
# e.g. if s3 bucket name is specified in common and for the same bucket a different name is given in `project/%{project}/deployment/%{deployment}`,
# the bucket gets created with the name specified in `project/%{project}/deployment/%{deployment}`

# NOTE: Remember that files names under account/ directory (according to below hierarchy) should match your aws account aliases
# e.g. simple-test.yaml, simple-prod.yaml

hierarchy:
    - common
    - account/%{aws_account_alias}
    - account_type/%{account_type}
    - project/%{project}/common
    - project/%{project}/account/%{aws_account_alias}
    - project/%{project}/account_type/%{account_type}
    - project/%{project}/serving_region/%{serving_region}/common
    - project/%{project}/serving_region/%{serving_region}/region/%{region}
    - project/%{project}/deployment/%{deployment}

  yaml:
    datadir: vars

  json:
    datadir: vars

# Specify acronyms here
# This is derived from stack name e.g. vt acronym in vt-projecta-na-uswest2 stack name.
simple:
  family:
    e: team1
    v: team2
  account_type:
    t: test
    p: production

# Facter expects arrays of dicts. this is used for ordering,
# If you want to ensure one fact is processed after another. this is because
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
      expression: (?P<family>\w)(?P<account_type>\w)-(?P<project>[a-z]+)(?P<n>\d+)-(?P<serving_region>\w+)-(?P<region>\w+)
      transforms:
        - account_type: "{{ config['simple']['account_type'][account_type] }}"
        - family: "{{ config['simple']['family'][family] }}"
        - region: '{{ region[0:2] }}-{{region[2:-1]}}-{{region[-1]}}'
        - serving_region: '{{serving_region}}'

    # Sets facts based on the output of an arbitrary shell command, this should be a one line output
    # and will be trimmed
  - shell:
      git_sha: git rev-parse HEAD
      aws_account_alias:
        command: echo "team1-test" # e.g current AWS alias: `aws iam list-account-aliases`
        #jsonpath: $.AccountAliases[0]

    # Facts set from the value of an environment variable
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
  # Set the Terraform version required in this repo. Pterradactyl will automatically fetch it
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

e.g. do apply on team2 projectc project
`pt apply vt-projectc0-na-useast1` 

This stack does not have a remote bucket or encrypted credentials or even a streamlined tags support.
