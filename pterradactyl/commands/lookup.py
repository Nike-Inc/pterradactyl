import os
import yaml
import phiera
import logging

from yaml.representer import SafeRepresenter

from pterradactyl.config import Config
from pterradactyl.facter import Facter
from pterradactyl.validator import Validator
from pterradactyl.terraform.terraform import Terraform
from pterradactyl.terraform.config import TerraformConfig

from .base import AbstractBaseCommand

log = logging.getLogger(__name__)


class LookupCommand(AbstractBaseCommand):
    """ Performs a hiera lookup and dumps result as yaml"""
    subcommands = []

    def __init__(self, config, parser):
        super().__init__(config, parser)

        parser.add_argument('--backend', '-b', help='select hiera backend(s)')
        parser.add_argument('--facts', '-f', help='use predefined facts from yaml')
        parser.add_argument('--set', '-s', help='set indivual fact (key=value)', action='append')

    def execute(self, args, lookups):
        config = Config()
        hiera_config = config.get('hiera')
        if args.backend:
            hiera_config['backends'] = args.backend.split(',')

        if args and args.facts:
            with open(args.facts, "r") as f:
                try:
                    facts = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    # XXX - DRY - this is also in config.py
                    if hasattr(e, 'problem_mark'):
                        mark = e.problem_mark
                        log.error("Error in {config_file}: {problem} (line {line}, col {column})".format(
                            config_file=os.path.basename(args.facts),
                            problem=e.problem, line=mark.line, column=mark.column
                        ))
                    else:
                        log.error(e)
                    exit(1)
        else:
            facts = {}

        if args.set:
            for fact in args.set:
                try:
                    key, value = fact.split('=')
                except ValueError:
                    log.error("Facts set from args must be key=value pairs.")
                    exit(1)
                facts[key] = value

        context = {**facts, **{'facts': facts}}
        hiera = phiera.Hiera(config.get('hiera'), context=facts, base_path=config.dir)
        data = hiera.get(lookups[0], {}, merge=dict, merge_deep=True)
        yaml.add_representer(phiera.util.LookupDict, SafeRepresenter.represent_dict)
        log.info(yaml.dump(dict(data), explicit_start=True))
