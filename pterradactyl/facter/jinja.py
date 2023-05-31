from functools import reduce

from jinja2 import Environment

from pterradactyl.facter.base import BaseFacter


class JinjaFacter(BaseFacter):

  def __init__(self, config):
    self.templates = config

  def facts(self, facts={}):

    return reduce(lambda memo, item: { **memo, **{ item[0]: Environment().from_string(item[1]).render(memo) } }, 
      self.templates.items(), facts)
