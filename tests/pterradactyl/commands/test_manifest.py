import os
import unittest
import pytest
from pterradactyl.commands.manifest import ManifestCommand
from mock import patch
import argparse
import shutil
import json


class TestManifest(unittest.TestCase):

    def setUp(self) -> None:
        self.deployment = 'ut-test0-na-uswest2'
        self.base_dir = os.path.join(os.getcwd(), 'tests/resources/config')
        self.config = os.path.join(self.base_dir, 'pterra.yaml')
        self.facts = os.path.join(self.base_dir, 'facts.yaml')
        self.facts_invalid = os.path.join(self.base_dir, 'facts_invalid.yaml')
        self.pterra_temp_dir = os.path.join(self.base_dir, '.pterradactyl')
        self.tf_exec_file = os.path.join(self.pterra_temp_dir, 'terraform', '0.13.1', 'terraform')
        self.tf_provider_kubectl_file = os.path.join(self.pterra_temp_dir, 'terraform', '0.13.1', 'terraform-provider-kubectl_v1.13.1')
        self.facts_json_file = os.path.join(self.pterra_temp_dir, 'workspace', self.deployment, 'facts.json')
        self.main_tf_json_file = os.path.join(self.pterra_temp_dir, 'workspace', self.deployment, 'main.tf.json')
        self.parser = self.create_parser()

    def tearDown(self) -> None:
        try:
            shutil.rmtree(self.pterra_temp_dir)
        except OSError:
            ("Directory {} does not exist.".format(self.pterra_temp_dir))

    @pytest.fixture(autouse=True)
    def mock_settings_env_vars(self):
        with patch.dict(os.environ, {"USER": "TEST_USER"}):
            yield

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument('--backend', '-b')
        parser.add_argument('--facts', '-f')
        parser.add_argument('--set')
        parser.add_argument('--command')
        return parser

    def test_execute_and_tf_dir_structure_has_been_created(self):
        """
        Test verifies if terraform creates proper directory structure and place there all plugins
        defined in the phierra.yaml file in the terraform section.
        Test Also verifies if facts are being populated correctly.
        """
        with patch('os.getcwd') as cwd_mock:
            cwd_mock.return_value = self.config
            with patch('requests.Session.get') as get_mock:
                get_mock_instance = get_mock.return_value
                get_mock_instance.response.status_code = 200
                with patch('pterradactyl.terraform.terraform.subprocess') as sub_mock:
                    sub_mock.return_value = None
                    with patch('pterradactyl.terraform.terraform.json') as json_mock:
                        json_mock_instance = json_mock.return_value
                        json_mock_instance.dump.return_value = {}
                        with patch('pterradactyl.terraform.terraform.Terraform') as tf_mock:
                            tf_mock_instance = tf_mock.return_value
                            tf_mock_instance.validate.return_value = True
                            tf_mock_instance.execute.return_value = None
                            mc = ManifestCommand(self.config, self.parser)
                            parsed = self.parser.parse_args((['--backend', 'yaml',
                                                              '-s', 'test_stage',
                                                              '-p', 'test_product', self.deployment,
                                                              '--command', 'test_command']))
                            mc.execute(parsed, [])
                            actual_facts = mc.facter.facts()
                            # Verify directory structure was created with downloaded plugins (mocks)
                            assert os.path.isdir(self.pterra_temp_dir)
                            assert os.path.isfile(self.tf_exec_file)
                            assert os.path.isfile(self.tf_provider_kubectl_file)
                            assert os.path.isfile(self.main_tf_json_file)
                            assert os.path.isfile(self.facts_json_file)

                            self.assertDictEqual(actual_facts, json.load(open(self.facts_json_file)))
