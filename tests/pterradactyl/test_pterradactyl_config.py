import os
import unittest
import logging
import pytest
from pterradactyl.config import Config
import yaml
from mock import patch


class TestPterradactylConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.pterra_config = os.path.join(os.getcwd(), 'tests/resources/config/pterra.yaml')
        self.base_path = os.path.join(os.getcwd(), 'tests/resources/config')

    def load_pterra_yaml(self):
        with open(self.pterra_config, 'r') as config:
            try:
                return yaml.safe_load(config)
            except yaml.YAMLError as e:
                assert False, "failed to load YAML"

    def test_default_config_file(self):
        """
        pterra.yaml exists in the current folder. Config should succeed and should return the config.file location
        config.dir should be equal to the current dir
        Current dir is for the test needs mocked up. See setUp method.
        """
        with patch('os.getcwd') as mock_cwd:
            mock_cwd.return_value = self.base_path
            current_working_dir = self.base_path
            config = Config(skip_pterra_yaml_enc=True)
            assert config.file == os.path.join(current_working_dir, config.config_file_name)
            assert config.dir == current_working_dir
            assert config.cache_dir == os.path.join(current_working_dir, config.cache_dir_name)
            data = self.load_pterra_yaml()
            assert config.get_facter() == data['facter']
            assert config.get('terraform')['plugins'] == data['terraform']['plugins']

    def test_custom_config_file(self):
        """
        Config initialization should fail if the config_file does not exist
        the program should exit.
        """
        with patch('os.getcwd') as mock_cwd:
            mock_cwd.return_value = self.base_path
            with pytest.raises(SystemExit) as e:
                config = Config(skip_pterra_yaml_enc=True, config_file_name="does_not_exist_pterra.yaml")
                assert e.type == SystemExit
                assert e.value.code == 1
