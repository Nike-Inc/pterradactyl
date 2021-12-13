import os
import re
from argparse import Action

from .base import BaseFacter
from pterradactyl.config import Config
from pterradactyl.util import as_list, lookup

class ArgumentsFacter(BaseFacter):

  def __init__(self, config):
    self.arg_specs = config
    self.actions = {}

  def parser_setup(self, parser):
    for arg, spec in self.arg_specs.items():
      parser.add_argument(*self.__arg_spec(arg, spec), **self.__arg_options(arg, spec))           

  def facts(self, facts={}):
    return { arg: self.actions[arg].value for arg in self.actions if self.actions[arg].value is not None}

  def __arg_spec(self, arg, spec):
    if 'positional' in spec and spec['positional']:
      return [ arg ]

    return as_list(
      [ '-{}'.format(alias) for alias in as_list(lookup(spec, 'alias', [])) ],
      '--{}'.format(arg)
    )
   
  def __arg_options(self, arg, spec):
    self.actions[arg] = ArgumentFactActionFactory()
    options = {
      'help': lookup(spec, 'description', default=None),
      'action': self.actions[arg],
      'metavar': arg
    }

    if not 'positional' in spec or not spec['positional']:
      options['required'] = lookup(spec, 'required', default=False)

    return options

class ArgumentFactActionFactory(object):

  def __call__(self, option_strings, dest, nargs=None, **kwargs):
    self.action = self.ArgumentFactAction(option_strings, dest, nargs, **kwargs)
    return self.action

  @property
  def value(self):
    return self.action.value

  class ArgumentFactAction(Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
      super().__init__(option_strings, dest, nargs, **kwargs)
      self.value = None

    def __call__(self, parser, namespace, values, option_string=None):
      self.value = values
