import os
import stat

from pathlib import Path
from shutil import copy

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
