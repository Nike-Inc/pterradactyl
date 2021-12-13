import os
import re
import json
import yaml
import phiera

from pterradactyl.config import Config
from pterradactyl.util import merge_dict, lookup


# XXX - this class is too "clever" for its own good. it's hard to follow.

class TerraformConfig(object):
    alias_syntax = re.compile(r'(\S+) as (\S+)')
    properties = ['resource', 'provider', 'variable', 'output',
                  'local', 'module', 'data', 'terraform']

    filters = {
    }

    transforms = {
        'module': lambda self, module, values: self._locate_module(module, values.get(
            module[1] if type(module) == tuple else module, {}))
    }

    key_sources = {
        'module': lambda self, prop: self.modules
    }

    key_transforms = {
        'module': lambda self, key: key[1] if type(key) == tuple else key
    }

    modules = []

    def __init__(self, facts, cwd=os.getcwd()):

        config = Config()
        self.facts = facts
        self.cwd = cwd
        self.terraform_config = config.get('terraform')
        self.module_path = lookup(self.terraform_config, 'module_path', default=[])
        self.root_dir = config.dir
        context = {**facts, **{'facts': facts}}
        self.hiera = phiera.Hiera(config.get('hiera'), context=context, base_path=config.dir)

        manifest = self.hiera.get('manifest', {'modules': []}, merge=dict, merge_deep=True)
        self.modules = self.alias_modules(manifest['modules'])

    def alias_modules(self, modules):
        # modules matching the alias syntax will be added as tuples
        return [next(iter(self.alias_syntax.findall(module)), module) for module in modules]

    def write(self, path):
        with open(os.path.join(path, 'main.tf.json'), 'w') as config:
            json.dump(self.to_dict(), config, indent=2)
        with open(os.path.join(path, 'facts.json'), 'w') as facts:
            json.dump(self.facts, facts, indent=2)

    def to_dict(self):
        return {prop: self._config_property(prop) for prop in self.properties if self.hiera.has(prop)}

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)

    def _config_property(self, prop):
        transform = self.transforms.get(prop, lambda self, key, values: values[key])
        key_source = self.key_sources.get(prop, lambda self, prop: values.keys())
        key_transform = self.key_transforms.get(prop, lambda self, key: key)
        # XXX - design decision, should values in here be authoritative and override hiera? i think so?
        # XXX - hiera expressions don't work here unfortunately
        values = self.hiera.get(prop, {}, merge=dict, merge_deep=True)
        return {key_transform(self, key): transform(self, key, values) for key in key_source(self, prop)}

    def _locate_module(self, module, spec):
        if 'source' in spec:
            return spec

        src_module = module[0] if type(module) == tuple else module
        for module_dir in self.module_path:
            module_path = os.path.join(module_dir, src_module)
            if os.path.isdir(module_path):
                rel_path = os.path.relpath(os.path.abspath(module_path), self.cwd)
                # terraform local modules must start with . even when relative to cwd
                if not rel_path.startswith('.'):
                    rel_path = os.path.join('.', rel_path)
                spec['source'] = rel_path
        # TODO - exception handling
        return spec
