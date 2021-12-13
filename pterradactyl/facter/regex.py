import re
import phiera
from jinja2 import Environment
from .base import BaseFacter
from pterradactyl.config import Config


class RegexFacter(BaseFacter):

    def __init__(self, config):
        # XXX - todo config syntax check
        self.config = Config()
        self.source = config['source']
        self.expression = config['expression']
        # XXX - should be optional
        self.transforms = config['transforms']

    def facts(self, facts={}):
        new_facts = {}
        match = re.search(self.expression, facts[self.source])
        if match:
            for fact, value in match.groupdict().items():
                for transform in self.transforms:
                    if fact in transform:
                        context = {**facts, **new_facts, **{fact: value}}

                        hiera = phiera.Hiera(self.config.get('hiera'), context=context, base_path=self.config.dir)

                        value = Environment().from_string(transform[fact]).render({**context, **{
                            'lookup': lambda key: hiera.get(key, {}, merge=dict, merge_deep=True),
                            'config': self.config
                        }})

                new_facts[fact] = value
        return new_facts
