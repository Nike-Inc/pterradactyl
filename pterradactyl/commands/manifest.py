import os

from pterradactyl.config import Config
from pterradactyl.facter import Facter
from pterradactyl.validator import Validator
from pterradactyl.terraform.terraform import Terraform
from pterradactyl.terraform.config import TerraformConfig

from .base import AbstractBaseCommand


class ManifestCommand(AbstractBaseCommand):
    subcommands = []

    def __init__(self, config, parser):
        super().__init__(config, parser)

        if self.subcommands:
            parser.add_argument('subcommand', choices=self.subcommands, help='sub-command')

        self.facter = Facter()
        self.facter.parser_setup(parser)

    def execute(self, args, terraform_args):
        config = Config()

        facts = self.facter.facts()

        # XXX ugly
        cache_key = facts.get(config.get('terraform')['cache_key'])

        workspace = config.workspace_dir(cache_key)
        terraform_config = TerraformConfig(self.facter.facts(), cwd=workspace)

        if not Validator(terraform_config, facts).validate():
            exit(1)

        terraform_config.write(workspace)

        command = [args.command]

        if self.subcommands:
            command.append(args.subcommand)

        if terraform_args:
            command.extend(terraform_args)

        terraform = Terraform(cwd=workspace)

        if terraform.validate():
            terraform.execute(*command)
        else:
            exit(1)
