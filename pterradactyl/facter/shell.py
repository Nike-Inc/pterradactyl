import subprocess
import json
import jsonpath_ng
import os

from .base import BaseFacter


def jsonpath(data, path):
  match = jsonpath_ng.parse(path).find(json.loads(data))
  if len(match) == 0:
    return None
  elif len(match) == 1:
    return match[0].value
  else:
    return [m.value for m in match]


class ShellFacter(BaseFacter):

  postprocessors = {
    'jsonpath': jsonpath
  }

  def __init__(self, config):
    self.commands = config

  def __postprocess(self, data, spec):
    for name, processor in self.postprocessors.items():
      if name in spec:
        data = processor(data, spec[name])
    return data

  def __run_fact(self, spec, facts):
    script = spec['command'] if type(spec) is dict else spec
    # We are copying the facts into another variable so that we don't merge the env vars to the pterradactyl facts, but only use them for the subprocess call
    env_vars = facts.copy()
    return self.__postprocess(subprocess.run(script, shell=True, text=True, env=env_vars.update(os.environ), stdout=subprocess.PIPE).stdout.rstrip(), spec)

  def facts(self, facts={}):
    return {
      fact: self.__run_fact(spec, facts)
        for fact, spec in self.commands.items()
    }
