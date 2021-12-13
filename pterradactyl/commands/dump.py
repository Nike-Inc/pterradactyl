import os
import yaml

from pterradactyl.config import Config
from pterradactyl.facter import Facter
from pterradactyl.terraform.terraform import Terraform
from pterradactyl.terraform.config import TerraformConfig

from .base import AbstractBaseCommand


class AbstractDumpCommand(AbstractBaseCommand):

    def __init__(self, config, parser):
        super().__init__(config, parser)

        self.facter = Facter()
        self.facter.parser_setup(parser)


class DumpRootModuleCommand(AbstractDumpCommand):

    def execute(self, args, terraform_args):
        config = Config()

        terraform_config = TerraformConfig(self.facter.facts())

        print(terraform_config.to_json(indent=2))


class DumpFactsCommand(AbstractDumpCommand):
    subcommands = []

    def execute(self, args, terraform_args):
        print(yaml.dump(self.facter.facts()))
