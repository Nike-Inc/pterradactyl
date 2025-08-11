import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, PropertyMock
from pterradactyl.terraform.config import TerraformConfig
from pterradactyl.terraform.terraform import Terraform


class TestTerraformConfigIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.facts = {
            "aws_region": "us-west-2",
            "environment": "test",
            "stack_name": "test-stack"
        }
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    @patch('pterradactyl.terraform.config.Config')
    @patch('pterradactyl.terraform.config.phiera.Hiera')
    def test_write_creates_variable_files(self, mock_hiera, mock_config):
        """Test that write() creates the expected files"""
        # Setup mocks
        mock_config.return_value.get.return_value = {
            'module_path': [],
            'terraform': {}
        }
        mock_config.return_value.dir = self.test_dir
        
        mock_hiera_instance = Mock()
        def mock_get(key, default=None, **kwargs):
            if key == 'manifest':
                return {'modules': []}
            elif key == 'resource':
                return {
                    "aws_s3_bucket": {
                        "test": {
                            "bucket": "my-test-bucket",
                            "region": "us-west-2"
                        }
                    }
                }
            return default
        
        mock_hiera_instance.get.side_effect = mock_get
        mock_hiera_instance.has.return_value = True
        mock_hiera.return_value = mock_hiera_instance
        
        # Create config and write
        config = TerraformConfig(self.facts, cwd=self.test_dir)
        env_vars = config.write(self.test_dir)
        
        # Check files were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'main.tf.json')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'variables.tf.json')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'facts.json')))
        
        # Check main.tf.json contains variable references
        with open(os.path.join(self.test_dir, 'main.tf.json')) as f:
            main_config = json.load(f)
        
        bucket_config = main_config["resource"]["aws_s3_bucket"]["test"]
        self.assertTrue(bucket_config["bucket"].startswith("${var.v_s_"))
        self.assertTrue(bucket_config["region"].startswith("${var.v_s_"))
        
        # Check variables.tf.json has definitions
        with open(os.path.join(self.test_dir, 'variables.tf.json')) as f:
            var_config = json.load(f)
        
        self.assertIn("variable", var_config)
        self.assertGreater(len(var_config["variable"]), 0)
        
        # Check env_vars were returned
        self.assertIsInstance(env_vars, dict)
        self.assertGreater(len(env_vars), 0)
    
    @patch('pterradactyl.terraform.config.Config')
    @patch('pterradactyl.terraform.config.phiera.Hiera')
    def test_no_secrets_in_files(self, mock_hiera, mock_config):
        """Test that no actual values are written to tf files"""
        secret_value = "super-secret-password-12345"
        
        # Setup mocks
        mock_config.return_value.get.return_value = {
            'module_path': [],
            'terraform': {}
        }
        mock_config.return_value.dir = self.test_dir
        
        mock_hiera_instance = Mock()
        def mock_get(key, default=None, **kwargs):
            if key == 'manifest':
                return {'modules': []}
            elif key == 'resource':
                return {
                    "aws_db_instance": {
                        "main": {
                            "password": secret_value,
                            "username": "admin"
                        }
                    }
                }
            return default
        
        mock_hiera_instance.get.side_effect = mock_get
        mock_hiera_instance.has.return_value = True
        mock_hiera.return_value = mock_hiera_instance
        
        # Create config and write
        config = TerraformConfig(self.facts, cwd=self.test_dir)
        env_vars = config.write(self.test_dir)
        
        # Check that secret is NOT in main.tf.json
        with open(os.path.join(self.test_dir, 'main.tf.json')) as f:
            content = f.read()
            self.assertNotIn(secret_value, content)
        
        # Check that secret is NOT in variables.tf.json
        with open(os.path.join(self.test_dir, 'variables.tf.json')) as f:
            content = f.read()
            self.assertNotIn(secret_value, content)
        
        # But the secret SHOULD be in env_vars
        self.assertIn(secret_value, env_vars.values())


class TestTerraformIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    @patch('pterradactyl.terraform.terraform.Config')
    @patch('subprocess.Popen')
    def test_terraform_receives_env_vars(self, mock_popen, mock_config):
        """Test that Terraform subprocess receives TF_VAR_ environment variables"""
        # Setup mocks
        mock_config.return_value.get.return_value = {
            'version': '1.0.0',
            'plugins': []
        }
        mock_config.return_value.cache_dir = self.test_dir
        
        mock_process = Mock()
        mock_process.poll.return_value = 0
        mock_process.stdout.readline.return_value = ''
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Create terraform instance with env vars
        env_vars = {
            "v_s_12345": "test-value",
            "v_n_67890": "42",
            "v_b_abcde": "true"
        }
        
        terraform = Terraform(cwd=self.test_dir, env_vars=env_vars)
        # Mock the terraform property to return a path
        with patch.object(type(terraform), 'terraform', new_callable=PropertyMock) as mock_terraform:
            mock_terraform.return_value = "/mock/terraform"
            terraform.execute("plan")
        
        # Check that Popen was called with correct env
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        
        # Get the env argument
        env = call_args[1]['env']
        
        # Check TF_VAR_ variables are set
        self.assertEqual(env.get('TF_VAR_v_s_12345'), 'test-value')
        self.assertEqual(env.get('TF_VAR_v_n_67890'), '42')
        self.assertEqual(env.get('TF_VAR_v_b_abcde'), 'true')
    
    @patch('pterradactyl.terraform.terraform.Config')
    @patch('subprocess.run')
    def test_terraform_validate_env_vars(self, mock_run, mock_config):
        """Test that validate also receives env vars"""
        # Setup mocks
        mock_config.return_value.get.return_value = {
            'version': '1.0.0',
            'plugins': []
        }
        mock_config.return_value.cache_dir = self.test_dir
        
        mock_run.return_value.stdout = '{"valid": true}'
        
        # Create terraform instance with env vars
        env_vars = {"v_s_test": "value"}
        terraform = Terraform(cwd=self.test_dir, env_vars=env_vars)
        with patch.object(type(terraform), 'terraform', new_callable=PropertyMock) as mock_terraform:
            mock_terraform.return_value = "/mock/terraform"
            terraform._Terraform__do_validate()
        
        # Check that run was called with env
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        env = call_args[1]['env']
        
        self.assertEqual(env.get('TF_VAR_v_s_test'), 'value')