import json
import os
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import PropertyMock, patch

from pterradactyl.terraform.terraform import Terraform


class TestTerraformBackendValidation(TestCase):

    def setUp(self):
        self.workspace = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.workspace, '.terraform'), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.workspace)

    def _write_state(self, backend_type='s3', bucket='example-bucket', key='example.tfstate'):
        state = {
            "backend": {
                "type": backend_type,
                "config": {
                    "bucket": bucket,
                    "key": key,
                    "region": "us-west-2"
                }
            }
        }
        with open(os.path.join(self.workspace, '.terraform', 'terraform.tfstate'), 'w') as state_file:
            json.dump(state, state_file)

    def _write_main_tf(self, backend_type='s3', bucket='example-bucket', key='example.tfstate'):
        main_tf = {
            "terraform": {
                "backend": {
                    backend_type: {
                        "bucket": bucket,
                        "key": key,
                        "region": "us-west-2"
                    }
                }
            }
        }
        with open(os.path.join(self.workspace, 'main.tf.json'), 'w') as main_file:
            json.dump(main_tf, main_file)

    def _write_variables_tf(self):
        variables_tf = {
            "variable": {
                "dummy": {
                    "type": "string"
                }
            }
        }
        with open(os.path.join(self.workspace, 'variables.tf.json'), 'w') as variables_file:
            json.dump(variables_tf, variables_file)

    def _create_terraform(self, mock_config, env_vars=None):
        mock_config.return_value.get.return_value = {
            'version': '1.0.0',
            'plugins': []
        }
        mock_config.return_value.cache_dir = self.workspace
        return Terraform(cwd=self.workspace, env_vars=env_vars or {})

    def _exercise_backend_validation(self, mock_config, *, state_bucket, main_bucket, include_variables):
        self._write_state(backend_type='s3', bucket=state_bucket)
        self._write_main_tf(backend_type='s3', bucket=main_bucket)

        if include_variables:
            self._write_variables_tf()

        terraform = self._create_terraform(mock_config)
        with patch.object(type(terraform), 'terraform', new_callable=PropertyMock) as mock_tf_bin, \
             patch.object(terraform, 'execute') as mock_execute, \
             patch.object(terraform, '_Terraform__do_validate', return_value={'valid': True}):
            mock_tf_bin.return_value = '/mock/terraform'
            result = terraform.validate()

        self.assertTrue(result)
        return mock_execute

    @patch('pterradactyl.terraform.terraform.Config')
    def test_backend_requires_init_with_variables_file(self, mock_config):
        execute = self._exercise_backend_validation(
            mock_config,
            state_bucket='bucket-a',
            main_bucket='bucket-b',
            include_variables=True,
        )

        execute.assert_called_once_with('init')

    @patch('pterradactyl.terraform.terraform.Config')
    def test_backend_ok_with_variables_file(self, mock_config):
        execute = self._exercise_backend_validation(
            mock_config,
            state_bucket='bucket-a',
            main_bucket='bucket-a',
            include_variables=True,
        )

        execute.assert_not_called()

    @patch('pterradactyl.terraform.terraform.Config')
    def test_backend_requires_init_without_variables_file(self, mock_config):
        execute = self._exercise_backend_validation(
            mock_config,
            state_bucket='bucket-a',
            main_bucket='bucket-b',
            include_variables=False,
        )

        execute.assert_called_once_with('init')

    @patch('pterradactyl.terraform.terraform.Config')
    def test_backend_ok_without_variables_file(self, mock_config):
        execute = self._exercise_backend_validation(
            mock_config,
            state_bucket='bucket-a',
            main_bucket='bucket-a',
            include_variables=False,
        )

        execute.assert_not_called()

