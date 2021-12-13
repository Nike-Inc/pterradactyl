import os
import re

from pterradactyl.config import Config
from pterradactyl.util import lookup, package, merge_dict

class Validator(object):

  def __init__(self, root_module, facts):
    self.facts = facts
    self.root_module = root_module
    self.validators = package.entry_points('pterradactyl.validators')
    self.rules = []

    #for rule in Config().get('validator', []):
    #  for facter_name, facter_config in rule.items():
    #    # TODO XXX - error if no facter exist
    #    Module = facters.get(facter_name).load()
    #    module = Module(facter_config)
    #    self.rules.append(module)

  def validate(self):
    valid = True 
    for name in self.validators:
      Validator = self.validators.get(name).load()
      validator = Validator(self.root_module, self.facts)
      if validator.validate() is False:
        valid = False
    return valid
