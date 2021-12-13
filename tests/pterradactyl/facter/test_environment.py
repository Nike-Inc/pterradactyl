import unittest
import os
import pterradactyl.facter.environment as environment
from mock import patch
import pytest


class TestFacterEnvironment(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def mock_settings_env_vars(self):
        with patch.dict(os.environ, {"USER": "TEST_USER"}):
            yield

    def test_environment_facts(self):
        environment_facter_data = {
            'deploy_user': 'USER'
        }
        output_facts = environment.EnvironmentFacter(environment_facter_data).facts()
        assert output_facts.get('deploy_user') == os.environ[environment_facter_data.get('deploy_user')]
