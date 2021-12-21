Pterradactyl
---

[![codecov](https://codecov.io/gh/Nike-Inc/pterradactyl/branch/master/graph/badge.svg?token=CvHYOh04mZ)](https://codecov.io/gh/Nike-Inc/pterradactyl)
[![Test](https://github.com/Nike-Inc/pterradactyl/actions/workflows/python-test.yaml/badge.svg)](https://github.com/Nike-Inc/pterradactyl/actions/workflows/python-test.yaml)
[![PyPi Release](https://github.com/Nike-Inc/pterradactyl/actions/workflows/python-build.yaml/badge.svg)](https://github.com/Nike-Inc/pterradactyl/actions/workflows/python-build.yaml)
![License](https://img.shields.io/pypi/l/pterradactyl)
![Python Versions](https://img.shields.io/pypi/pyversions/pterradactyl)
![Python Wheel](https://img.shields.io/pypi/wheel/pterradactyl)


Pterradactyl is a library developed to abstract TF configuration from the TF environment setup. Pterradactyl allows to create a hierarchy of TF environments/stacks, hallows an unconstrained number of cloud accounts and stacks to share inherited configuration.

Currently, multiple TF stacks are managed through different TF environments and var files. But this becomes especially tricky to manage when the stacks are vastly different from one another, or even in the case of slightly different stacks, one could question the DRY principal looking at all the repeat vars in the var file! When stacks deviate from one another, by using just the var files, the TF code quickly becomes unreadable with all the conditionals. Using just environments based TF, there is always room of accidental apply of one stack to the other. You can use bash files to safegaurd against that but then there is always the old faithful way of doing by just completely skipping the bash file ! (#fun-stuff)

Pterradactyl takes care of all the pain points described above.

Table of content
* [Some of the Pterradactyl features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Unit Tests](#tests)
* [Examples of creating new projects/prodcuts](#examples)
* [Pterradactyl Directory Structure](#structure)
* [Comparison of other well-known Terraform wrappers:](#tf_wrappers)

# <a name="features"></a> Some of the Pterradactyl features:

- Programatically generated Terraform code using hierarchical YAML files structure. Override only what you have to in your stack file and keep the rest in common YAML.
- Because Pterradactyl uses hierarchy, it becomes simple to provide standard structure to common attributes like `tags` in a uniform manner.
- Secrets support using _sops_ and _AWS KMS_.
- Keeps Terraform versions consistent between stacks.
- As the Terraform file is generated through Pterradactyl, there is no room for the fun `override` :)


Pterradactyl uses [Phiera](https://github.com/Nike-Inc/phiera), to manage the YAML hierarchy configuration for a terraform code base.

Integration of terraform with Phiera is achieved through Pterradactyl.

A primer on [Hiera](https://puppet.com/docs/puppet/latest/hiera_intro.html).


# <a name="installation"></a> Installation:
### From PyPi:
```shell script
pip install pterradactyl
```

### From GitHub:
```shell script
pip install git+https://github.com/Nike-Inc/pterradactyl#egg=pterradactyl
```

### From source
You can always install it from wheel, by running the following commands:

Build package and wheel.
```python
poetry install
poetry build
```

Install
```python
python3 -m pip install dist/*.whl
```

Of course, you can always deploy the package to your corporate Artifactory.

# <a name="usage"></a> Usage:

Pterradyctal supports all of the terraform commands.

#### basic cli
```bash
apply `pt apply <stack-name>`
plan `pt plan <stack-name>`
destroy `pt destroy <stack-name>`
graph `pt graph <stack-name>`
show `pt show <stack-name>`
```

#### Manipulating state
Pterradyctal supports all state commands and they follow the same argument patter as in TF, here are some examples

```bash
state list `pt state list <stack-name>`
state show `pt state show <stack-name> -state <target>`
state rm `pt state rm <stack-name> -state <statefile>`
```
# <a name="tests"></a> Tests:

Run unit tests

```bash
poetry run pytest
```

Run unit tests with coverage report in HTML format.

```bash
poetry run pytest --cov-report=html --cov=pterradactyl --cov-fail-under=80 tests/
```

# <a name="examples"></a> Examples of creating new projects/prodcuts:

Basic Example [here](https://github.com/Nike-Inc/pterradactyl/blob/master/examples/simple/README.md)
- Module setup
- Attribute overriding

Advanced Example [here](https://github.com/Nike-Inc/pterradactyl/blob/master/examples/complex/README.md)
- Create infrastructure for a new AWS account
- Common tag setup
- KMS encryption
- Remote backend
- Module setup
- Attribute overriding


# <a name="structure"></a> Pterradactyl Directory Structure:

After running `pt apply` pterradactyl will create below directory structure,
containing downloaded given Terraform version with all required plugins, and workspace containing all metadata for your stack, e.g.:

```
.pterradactyl
├── terraform
│     └── 0.13.1
│         ├── terraform
│         └── terraform-provider-kubectl_v1.13.1
└── workspace
    └── bt-projectc0-na-useast1
        ├── facts.json
        └── main.tf.json
```

- terraform - directory containing downloaded Terraform given version with downloaded plugins defined in pterra.yaml file.
- workspace - directory containing metadata information for you stack. Each stack has a separate workspace.
- facts.json - JSON file with facts generated by Pterradactyl (e.g. deploy_user, state_prefix, aws_account_alias)
- main.tf.json - metadata information file regarding providers (e.g. aws, kubernetes, helm), moduls (e.g. vpc, kms, eks)and terraform backend information.


# <a name="tf_wrappers"></a> Comparison of other well-known Terraform wrappers:

### Terragrunt:
Some of the key Terragrunt features:

- Execute Terraform commands on multiple modules at once
- Keep your Terraform configuration DRY
- Inputs set as env variables.
- Call custom actions using Before and After Hooks
- Work with multiple AWS accounts
- Lock File Handling
- AWS Auth support
- Caching folder where commands are being executed.
- Auto-retry e.g. when installing provider failed due to connection error.


More info [here](https://terragrunt.gruntwork.io/docs/#features)

### Terraspace:

Some of the key Terraspace features:

- Build-in generators
- Multiple environments
- Deploy Multiple Stacks with a single command
- Build-in secrets support for AWS Secret Manager, AWS SSM Parameter Store, Azure Key
- Configurable CLI Hooks and CLI Args.
- Allows you to create test harness.
- Terraform Cloud and Terraform Enterprise support.


More info [here](https://terraspace.cloud/docs/intro/)

### Comparison between Pterradactyl vs Terragrunt vs Terraspace

|  Feature | Pterradactyl  | Terragrunt  |  Terraspace |  Comment |
|---|---|---|---|---|
| **Organized Structure** | &check; | &check; | &check; |  |
| **Multiple environments** | &check; | &check; | &check; |  |
| **Execute Terraform commands on multiple modules at once** |  &check; |  &check;  |  &check;  |  |
| **Secrets support** | &check; | &check;  | &check; |  |
| **CLI Hooks** | &check; | &check;  | &check;  | [More details](https://terraspace.cloud/docs/config/hooks/) |
| **Automated Backend Creation** | &check; | &check;  | &check;  | |
| **Built-in Test Framework** | &cross; |  &cross; | &check; | [More details](https://terraspace.cloud/docs/testing/) |
| **Native Terraform HCL** | &cross; |  &cross; | &check; | [More details](https://terraspace.cloud/docs/vs/terragrunt/) |

### Summary
It's hard to compare Pterradactyl, Terragrunt and Terraspace on the same level.\
Overall all those tools have some major differences. However above gives you a gist of what you can expect in each tool.\
If you are thinking what is more proper for you, simply deep into the details of each tool.
Terragrut and Pterradactyl are rather thin wrappers for Terraform, whereas Terraspace is rather a huge framework.

