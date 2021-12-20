import os
import yaml
import logging
import subprocess
from appdirs import AppDirs
from phiera import Merge

log = logging.getLogger(__name__)

"""
TODO - proper doc 
handles config
"""


class Config(object):
    # TODO - this should come from setup.py
    APP_NAME = 'pterradactyl'
    APP_AUTHOR = 'celect'

    # TODO - support multiple filenames (for yaml or yml)/make file configurable
    config_file_name = 'pterra.yaml'

    cache_dir_name = '.pterradactyl'

    # for memoizing config_file property
    __config_file = None

    memo = {}

    path = None

    @classmethod
    def set_config_file(cls, path):
        Config.__config_file = path

    def __init__(self, skip_pterra_yaml_enc=False, config_file_name=None):
        self.appdirs = AppDirs(self.APP_NAME, self.APP_AUTHOR)
        self.skip_pterra_yaml_enc = skip_pterra_yaml_enc
        if config_file_name:
            self.config_file_name = config_file_name

        if 'config' not in self.memo:
            self.__load()

    def get(self, key, default=None):
        if key in self.memo['config']:
            return self.memo['config'][key]
        else:
            return default

    def __getattr__(self, attr):
        return self.get(attr)

    # getters
    def get_facter(self):
        return self.get('facter', [])

    facter = property(get_facter)

    @property
    def dir(self):
        # XXX - should locate dir and append config file rather than building the whole string and removing filename
        return os.path.dirname(self.file)

    @property
    def cache_dir(self, subdir=None):
        cache_dir = os.path.join(self.dir, self.cache_dir_name)
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def workspace_dir(self, cache_key=None):
        # XXX TODO - handle no cache key
        if cache_key:
            workspace_dir = os.path.join(self.cache_dir, "workspace", cache_key)
            os.environ["WORKSPACE_DIR"] = workspace_dir
        else:
            log.error("fail no cache key")
            exit(1)
        os.makedirs(workspace_dir, exist_ok=True)
        return workspace_dir

    def __load(self):
        """
      Loads config file or dies trying
    """
        with open(self.file, 'r') as config:
            try:
                self.memo['config'] = yaml.safe_load(config)

                # Handle pterra.yaml.enc, expects it to be under the same path as pterra.yaml
                if os.path.exists("{}.enc".format(self.file)) and not self.skip_pterra_yaml_enc:
                    self.memo['config'] = Merge(dict, deep=True).deep_merge(
                        self.memo['config'],
                        yaml.safe_load(subprocess.check_output(
                            ['sops', '--input-type=yaml', '--output-type=yaml', '-d', "{}.enc".format(self.file)])
                        )
                    )

            except yaml.YAMLError as e:
                # TODO - do something real here

                if hasattr(e, 'problem_mark'):
                    mark = e.problem_mark
                    log.error("Error in {config_file}: {problem} (line {line}, col {column})".format(
                        config_file=os.path.basename(self.file),
                        problem=e.problem, line=mark.line + 1, column=mark.column + 1
                    ))
                else:
                    log.info(e)

                exit(1)

            except subprocess.CalledProcessError as e:
                log.error("Error reading {}.enc file".format(self.file))
                log.error(e)
                exit(1)

    @property
    def file(self):
        """
      Finds the config file. This will traverse upward until it finds a valid config file
    """
        if self.__config_file:
            return self.__config_file

        path, traversing = os.getcwd(), True
        while traversing:
            log.info(path)
            config_file_path = os.path.join(path, self.config_file_name)
            if os.path.exists(config_file_path):
                Config.set_config_file(config_file_path)
                return config_file_path
            path, traversing = os.path.split(path)

        log.error("Couldn't find {}, are you in a pterradactyl workspace?".format(self.config_file_name))
        exit(1)
