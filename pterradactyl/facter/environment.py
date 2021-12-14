import os
from .base import BaseFacter

class EnvironmentFacter(BaseFacter):

  def __init__(self, config):
    self.vars = config

  def facts(self, facts={}):
    return { fact: os.environ[var] for fact, var in self.vars.items() }
