import platform
import os
import re
import subprocess
import sys
import json
import glob
import requests
import logging

from pathlib import Path
from semantic_version import SimpleSpec, Version
from pterradactyl.config import Config
from pterradactyl.util import memoize
from pterradactyl.util.download import download
from pterradactyl.util.filesystem import ensure_executable, ensure_directory, sync_local_tf_plugins, check_stderr

logging.basicConfig(level=logging.INFO, encoding='utf-8', format=None)
log = logging.getLogger(__name__)


class Terraform(object):
    RELEASE_URL_PATTERN = 'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{os}_{arch}.zip'
    GITHUB_RELEASES_URL_PATTERN = 'https://api.{domain}/repos/{owner}/{repo}/releases'

    def __init__(self, cwd=None):
        app_config = Config()
        terraform_config = app_config.get('terraform')

        self.cwd = cwd
        self.cache_dir = app_config.cache_dir
        self.plugins = terraform_config.get('plugins', [])
        self.version = terraform_config['version']
        self.auth_headers = terraform_config.get("git_credentials", {})

    def execute(self, *args):
        process = subprocess.Popen([self.terraform] + list(args), close_fds=True, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')

        output = []
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            sys.stdout.write(line)
            output.append(bytes(line, encoding='utf-8'))
            sys.stdout.flush()
        process.communicate()
        if (process.returncode != 0):
            check_stderr(b''.join(output))

    def validate(self):
        # reinitialize if state backend changed
        if not self.__validate_backend():
            self.execute("init")

        # now validate with terraform validate
        result = self.__do_validate()
        # XXX - detect backend change
        if not result['valid']:
            fatal_errors = [entry for entry in result['diagnostics']
                            if ('terraform init' not in entry.get('detail', '')
                                and 'terraform init' not in entry.get('summary', '')
                                and 'plugin' not in entry.get('summary', ''))]

            if fatal_errors:
                # execute 'validate' normally to display errors to user
                self.execute("validate")
                return False

            # if there are no fatal errors, "terraform init" should fix the problem
            self.execute("init", "-upgrade")
            result = self.__do_validate()

            # if it didn't fix it, report back and return False
            if not result['valid']:
                self.execute("validate")
                return False

        return True

    def __validate_backend(self):
        state_path = os.path.join(self.data_dir, 'terraform.tfstate')

        if not os.path.exists(state_path):
            return False

        with open(state_path, 'r') as f:
            state = json.load(f)

        for path in glob.iglob(os.path.join(self.cwd, '*.tf.json')):
            with open(path) as f:
                tf = json.load(f)

            # check state backend
            if 'terraform' in tf and 'backend' in tf['terraform']:
                # state backend not configured
                if 'backend' not in state or 'type' not in state['backend'] or 'config' not in state['backend']:
                    return False

                for backend, config in tf['terraform']['backend'].items():
                    # backend type changed
                    if backend != state['backend']['type']:
                        return False

                    # backend configuration changed
                    if config != dict(filter(lambda i: i[1] is not None, state['backend']['config'].items())):
                        return False
            else:
                # backend config was removed
                if 'backend' in state:
                    return False
        return True

    def __do_validate(self):
        process = subprocess.run([self.terraform, 'validate', '-json'],
                                 capture_output=True, close_fds=True, cwd=self.cwd)
        return json.loads(process.stdout)

    def __log_validation_error(self, error):
        log.error("ERR %s" % error)

    def ensure_plugins(self):
        for plugin in self.plugins:
            self.ensure_plugin(**plugin)

    def ensure_plugin(self, repo, owner, version, domain="github.com"):
        for plugin_bin in os.listdir(self.bin_dir):
            if plugin_bin.startswith(repo):
                found_version = re.search('v(\d+.\d+.\d+)', plugin_bin)
                if found_version and \
                        Version(found_version.groups()[0]) in SimpleSpec(version):
                    break
                else:
                    self.deprecate_plugin(plugin_bin)

        else:
            self.download_plugin(repo, owner, SimpleSpec(version), domain)

    def deprecate_plugin(self, plugin_bin):
        # should we allow for different ways to deprecate a plugin?
        Path(os.path.join(self.bin_dir, 'deprecated')).mkdir(exist_ok=True)
        os.rename(
            os.path.join(self.bin_dir, plugin_bin),
            os.path.join(self.bin_dir, 'deprecated', plugin_bin),
        )
        log.info('Moved {} to the deprecated folder'.format(plugin_bin))

    def download_plugin(self, repo, owner, spec, domain):
        # XXX - currently only downloads from github
        version, release_url = self.get_release_url(owner, repo, spec, domain)
        dest_bin = os.path.join(self.bin_dir, "{}_v{}".format(repo, version))

        # TODO: use better exception class
        if not release_url:
            raise Exception(
                'Not able to satisfy requirement {} on github repo: {}/{}'.format(
                    spec, owner, repo))
        filename = '{repo}_v{version}'.format(repo=repo, version=version)
        download(release_url, self.bin_dir, filename, dest_bin, self.auth_headers.get(domain))
        ensure_executable(dest_bin)
        # sync terraform local plugins
        arch = platform.system().lower() + "_" + self.__architecture_type()
        sync_local_tf_plugins(dest_bin, domain, owner, repo, version, arch)

    def get_release_url(self, owner, repo, spec, domain):
        # return tuple of version: assets, return '' as release url if not found / no valid version found
        latest_release = ['0.0.0', '']
        releases_res = requests.get(self.GITHUB_RELEASES_URL_PATTERN.format(
            domain=domain,
            owner=owner,
            repo=repo
        ), headers=self.auth_headers.get(domain)).json()
        for r in releases_res:
            version = r.get('tag_name').split('v')[1]
            if Version(version) in spec and Version(version) > Version(latest_release[0]):
                for a in r['assets']:
                    asset_url = a['browser_download_url']
                    if platform.system().lower() in asset_url and \
                            self.__architecture_type() in asset_url:
                        latest_release[0] = version
                        latest_release[1] = a['url']
        return latest_release

    @property
    @memoize
    def terraform(self):
        """
      ensures a particular terraform release version exists,
      and returns the path to the executable
    """
        ## XXX - this assumes external things aren't mucking with its dirs, so it doesn't check
        ## that e.g. the tf bin path both exists and is a file
        terraform_bin = os.path.join(self.bin_dir, 'terraform')

        if not os.path.exists(terraform_bin):
            download(self.release_url, self.bin_dir, 'terraform')
            ensure_executable(terraform_bin)

        self.ensure_plugins()

        return terraform_bin

    @property
    def auth_headers(self):
        return self._auth_headers

    @auth_headers.setter
    def auth_headers(self, git_credentials):
        self._auth_headers = {
            k: {'Authorization': 'token {}'.format(v)} for k, v in git_credentials.items()
        }

    @property
    def release_url(self):
        """
      builds a terraform release url from version and architecture type
    """
        return self.RELEASE_URL_PATTERN.format(
            version=self.version,
            os=platform.system().lower(),
            arch=self.__architecture_type())

    def __architecture_type(self):
        """
      returns a terraform build architecture type
    """
        if platform.machine().startswith('arm'):
            return 'arm'
        return 'amd64' if platform.architecture()[0] == '64bit' else '386'

    @property
    @memoize
    def bin_dir(self):
        return ensure_directory(os.path.join(self.cache_dir, 'terraform', self.version))

    @property
    def data_dir(self):
        return ensure_directory(os.path.join(self.cwd, '.terraform'))
