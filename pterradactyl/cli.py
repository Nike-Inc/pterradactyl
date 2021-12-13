import argparse
import pkg_resources
import os

import pterradactyl

from pterradactyl.config import Config
from pterradactyl.util import package

SKIP_PTERRA_YAML_ENC = os.environ.get("SKIP_PTERRA_YAML_ENC", False)


def dispatch(argv):
    parser = argparse.ArgumentParser(prog="pterradactyl")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {}".format(pterradactyl.__version__)
    )

    config = Config(skip_pterra_yaml_enc=SKIP_PTERRA_YAML_ENC)
    os.chdir(config.dir)

    subparsers = parser.add_subparsers(title="commands", dest="command")

    commands = {}
    for name, module in package.entry_points('pterradactyl.registered_commands').items():
        Command = module.load()
        subparser = subparsers.add_parser(name, help='{} help'.format(name))
        command = Command(config, subparser)
        commands[name] = command

    args, extra_args = parser.parse_known_args(argv)

    if not args.command:
        parser.print_help()
        exit(1)

    command = commands[args.command]
    command.execute(args, extra_args)
