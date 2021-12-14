# uncompyle6 version 3.3.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.3 (default, Mar 27 2019, 09:23:15) 
# [Clang 10.0.1 (clang-1001.0.46.3)]
# Embedded file name: /Users/rmk/Projects/pterra/pterradactyl/pterradactyl/facter/manifest_path.py
# Size of source mod 2**32: 1517 bytes
import os, re
from argparse import Action
from .base import BaseFacter
from pterradactyl.config import Config

class ManifestPathFacter(BaseFacter):

    def __init__(self, config):
        self.path_specs = config

    def parser_setup(self, parser):
        self.action = PathFactActionFactory(Config().dir, self.path_specs)
        parser.add_argument('manifest', help='Pterradactyl deployment manifest', action=(self.action))

    def facts(self, facts={}):
        return self.action.facts


class PathFactActionFactory(object):

    def __init__(self, path, path_specs):
        self.path = path
        self.path_specs = path_specs

    def __call__(self, option_strings, dest, nargs=None, **kwargs):
        self.action = (self.PathFactAction)(option_strings, dest, (self.path), (self.path_specs), nargs, **kwargs)
        return self.action

    @property
    def facts(self):
        return self.action.facts

    class PathFactAction(Action):

        def __init__(self, option_strings, dest, path, path_specs, nargs=None, **kwargs):
            self.path = path
            self.path_specs = path_specs
            (super().__init__)(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            self.facts = {}
            path = os.path.relpath(values, self.path)
            builder = re.compile('<([^>/]+)>')
            for facter_path in self.path_specs:
                match = re.match(builder.sub('(?P<\\1>[^/]+)', facter_path), path)
                if match:
                    self.facts.update(match.groupdict())

            setattr(namespace, self.dest, values)
# okay decompiling manifest_path.cpython-37.pyc
