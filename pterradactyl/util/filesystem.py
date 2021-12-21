import os
import stat
import json
import logging

from pathlib import Path
from shutil import copy

log = logging.getLogger(__name__)

def ensure_executable(path):
  st = os.stat(path)
  os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
  return path


def ensure_directory(path):
  Path(path).mkdir(parents=True, exist_ok=True)
  return path

def get_target_path(domain: str, owner: str, repo: str, version: str, arch):
  # remove terraform-provider- from the repo name to get the plugin name
  plugin_name = repo.replace("terraform-provider-", "")
  target_path = os.path.join(os.path.expanduser('~'),".terraform.d/plugins", domain, owner, plugin_name, version, arch)
  return target_path

def sync_local_tf_plugins(source_dir: str, domain: str, owner: str, repo: str, version: str, arch):
  # We need to sync only the private plugins which are part of the plugins attr in pterr.yaml
  # standard terraform plugins are stored in /plugins/registry.terraform.io
  
  target_path = get_target_path(domain, owner, repo, version, arch)
  if not os.path.exists(target_path):
    os.makedirs(target_path)
  copy(source_dir, target_path)

def check_stderr(std_err):
    yellow = "\x1b[33;21m"
    red = "\x1b[31m\n\x1b[1m\x1b[31m"
    reset = "\x1b[0m"
    try:
      facts_file = os.path.join(os.environ['WORKSPACE_DIR'], 'facts.json')
      stack_facts = get_json(facts_file)
      if 'Access Denied' in str(std_err) and 'aws_account_alias' in stack_facts.keys():
        log.error((
            bytes(red, encoding='utf-8') +
            b'Error: You got Access Denied from AWS (HTTP 403 status code).\n\n' +
            bytes(reset, encoding='utf-8') +
            b'You are probably authenticated to incorrect AWS account.\n' +
            b'Check if your stack workspace is in the logged in AWS account.\n\n').decode('utf-8'))
        log.error((
            b'Current AWS account alias: ' +
            bytes(yellow, encoding='utf-8') +
            b'{},' +
            bytes(reset, encoding='utf-8') +
            b' applying to ' +
            bytes(yellow, encoding='utf-8') +
            b'{}-{}.\n\n' +
            bytes(reset, encoding='utf-8')).decode('utf-8').format(stack_facts['aws_account_alias'], stack_facts['family'], stack_facts['account_type']))
        log.error(
            f"All facts for your stack: {json.dumps(stack_facts, indent=4, sort_keys=True)}")
      else:
        log.error(std_err.decode('utf-8'))
    except:
        log.error("Could not parse facts.json file at location: {}.\n Returning default error message.".format(facts_file))
        log.error(std_err.decode('utf-8'))

def get_json(path):
    with open(path, "r") as stream:
        return json.load(stream)