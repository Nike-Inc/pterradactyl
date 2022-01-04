import os
import unittest
import pytest
from pterradactyl.commands.manifest import ManifestCommand
from mock import patch
import argparse
import shutil
import json

from testfixtures import Replacer
from testfixtures.popen import MockPopen


class TestManifest(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setUp(self) -> None:
        self.deployment = 'ut-test0-na-uswest2'
        self.base_dir = os.path.join(os.getcwd(), 'tests/resources/config')
        self.config = os.path.join(self.base_dir, 'pterra.yaml')
        self.facts = os.path.join(self.base_dir, 'facts.yaml')
        self.facts_invalid = os.path.join(self.base_dir, 'facts_invalid.yaml')
        self.pterra_temp_dir = os.path.join(self.base_dir, '.pterradactyl')
        self.tf_exec_file = os.path.join(
            self.pterra_temp_dir, 'terraform', '0.13.1', 'terraform')
        self.tf_provider_kubectl_file = os.path.join(
            self.pterra_temp_dir, 'terraform', '0.13.1', 'terraform-provider-kubectl_v1.13.1')
        self.facts_json_file = os.path.join(
            self.pterra_temp_dir, 'workspace', self.deployment, 'facts.json')
        self.main_tf_json_file = os.path.join(
            self.pterra_temp_dir, 'workspace', self.deployment, 'main.tf.json')
        self.parser = self.create_parser()
        #Popen mock
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace(
            'pterradactyl.terraform.terraform.subprocess.Popen', self.Popen)
        self.addCleanup(self.r.restore)

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

    @patch('os.getcwd')
    @patch('requests.Session.get')
    @patch('pterradactyl.terraform.terraform.json')
    @patch('pterradactyl.terraform.terraform.Terraform')
    def test_execute_and_tf_dir_structure_has_been_created(self, mock_tf, mock_json, mock_get, mock_getcwd):
        """
        Test verifies if terraform creates proper directory structure and place there all plugins
        defined in the phierra.yaml file in the terraform section.
        Test Also verifies if facts are being populated correctly.
        """
        mock_getcwd.return_value = self.config
        mock_get.response.status_code = 200
        self.Popen.set_default()
        mock_json.dump.return_value = {}
        mock_tf.validate.return_value = True
        mock_tf.execute.return_value = None

        mc = ManifestCommand(self.config, self.parser)
        parsed = self.parser.parse_args((['--backend', 'yaml',
                                          '-s', 'test_stage',
                                          '-p', 'test_product', self.deployment,
                                          '--command', 'test_command']))
        mc.execute(parsed, ['apply'])
        actual_facts = mc.facter.facts()
        # Verify directory structure was created with downloaded plugins (mocks)
        assert os.path.isdir(self.pterra_temp_dir)
        assert os.path.isfile(self.tf_exec_file)
        assert os.path.isfile(self.tf_provider_kubectl_file)
        assert os.path.isfile(self.main_tf_json_file)
        assert os.path.isfile(self.facts_json_file)
        self.assertDictEqual(actual_facts, json.load(
            open(self.facts_json_file)))

    @patch('os.getcwd')
    @patch('requests.Session.get')
    @patch('pterradactyl.terraform.terraform.json')
    @patch('pterradactyl.terraform.terraform.Terraform')
    def test_execute_with_non_zero_returncode(self, mock_tf, mock_json, mock_get, mock_getcwd):
        mock_getcwd.return_value = self.config
        mock_get.response.status_code = 200
        self.Popen.set_default(returncode=1, stderr=b'Access Denied from AWS', stdout=b'')
        mock_json.dump.return_value = {}
        mock_tf.validate.return_value = True
        mock_tf.execute.return_value = None

        mc = ManifestCommand(self.config, self.parser)
        parsed = self.parser.parse_args((['--backend', 'yaml',
                                          '-s', 'test_stage',
                                          '-p', 'test_product', self.deployment,
                                          '--command', 'test_command']))
        mc.execute(parsed, ['apply'])
        assert 'Access Denied from AWS' in self._caplog.text
