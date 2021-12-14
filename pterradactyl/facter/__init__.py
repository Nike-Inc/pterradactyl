from pterradactyl.config import Config
from pterradactyl.util import lookup, package, merge_dict


class Facter(object):
    config = {}
    facts = {}

    def __init__(self):
        self.config = Config().get('facter')

        facters = package.entry_points('pterradactyl.facters')

        self.rules = []

        for rule in self.config:
            for facter_name, facter_config in rule.items():
                # TODO XXX - error if no facter exist
                Module = facters.get(facter_name).load()
                module = Module(facter_config)
                self.rules.append(module)

    def parser_setup(self, parser):
        for rule in self.rules:
            rule.parser_setup(parser)

    def facts(self):
        # TODO - memoize this?
        facts = {}
        for rule in self.rules:
            facts = {**facts, **rule.facts(facts)}
        return facts

    def to_dict(self):
        return self.facts
