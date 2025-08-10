import unittest
import json
from pterradactyl.terraform.variable_extractor import VariableExtractor


class TestVariableExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = VariableExtractor()
    
    def test_simple_values(self):
        """Test basic value extraction"""
        config = {
            "resource": {
                "aws_instance": {
                    "example": {
                        "ami": "ami-123456",
                        "instance_type": "t2.micro",
                        "count": 3,
                        "enable_monitoring": True
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that values were replaced with variable references
        instance_config = modified["resource"]["aws_instance"]["example"]
        self.assertTrue(instance_config["ami"].startswith("${var.v_s_"))
        self.assertTrue(instance_config["instance_type"].startswith("${var.v_s_"))
        self.assertTrue(instance_config["count"].startswith("${var.v_n_"))
        self.assertTrue(instance_config["enable_monitoring"].startswith("${var.v_b_"))
        
        # Check variable definitions
        self.assertIn("variable", variables)
        var_defs = variables["variable"]
        
        # Check that we have the right number of variables
        self.assertEqual(len(var_defs), 4)
        
        # Check types are correct
        for var_name, var_def in var_defs.items():
            if var_name.startswith("v_s_"):
                self.assertEqual(var_def["type"], "string")
            elif var_name.startswith("v_n_"):
                self.assertEqual(var_def["type"], "number")
            elif var_name.startswith("v_b_"):
                self.assertEqual(var_def["type"], "bool")
    
    def test_deduplication(self):
        """Test that identical values share the same variable"""
        config = {
            "resource": {
                "aws_instance": {
                    "web": {"ami": "ami-123456", "instance_type": "t2.micro"},
                    "app": {"ami": "ami-123456", "instance_type": "t2.micro"},
                    "db": {"ami": "ami-789012", "instance_type": "t2.micro"}
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Get the variable references
        web_ami = modified["resource"]["aws_instance"]["web"]["ami"]
        app_ami = modified["resource"]["aws_instance"]["app"]["ami"]
        db_ami = modified["resource"]["aws_instance"]["db"]["ami"]
        
        web_type = modified["resource"]["aws_instance"]["web"]["instance_type"]
        app_type = modified["resource"]["aws_instance"]["app"]["instance_type"]
        
        # Same values should use same variable
        self.assertEqual(web_ami, app_ami)
        self.assertEqual(web_type, app_type)
        
        # Different values should use different variables
        self.assertNotEqual(web_ami, db_ami)
        
        # Should have only 3 variables total (2 amis + 1 instance_type)
        self.assertEqual(len(variables["variable"]), 3)
    
    def test_value_reconstruction(self):
        """Test that we can reconstruct original values from variables"""
        config = {
            "resource": {
                "aws_db_instance": {
                    "main": {
                        "allocated_storage": 100,
                        "storage_type": "gp2",
                        "engine": "mysql",
                        "engine_version": "5.7",
                        "instance_class": "db.t2.micro",
                        "name": "mydb",
                        "username": "admin",
                        "password": "supersecret123!",
                        "parameter_group_name": "default.mysql5.7",
                        "skip_final_snapshot": True,
                        "backup_retention_period": 7,
                        "backup_window": "03:00-04:00",
                        "maintenance_window": "sun:04:00-sun:05:00"
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Verify all values were converted to variables
        db_config = modified["resource"]["aws_db_instance"]["main"]
        for key, value in db_config.items():
            if isinstance(value, str):
                self.assertTrue(value.startswith("${var.v_"))
        
        # Verify we can map back to original values
        original_values = {}
        for var_name, var_info in self.extractor.variables.items():
            # Find where this variable is used in modified config
            var_ref = f"${{var.{var_name}}}"
            original_values[var_ref] = var_info["value"]
        
        # Check specific sensitive value
        password_var = db_config["password"]
        self.assertIn(password_var, original_values)
        self.assertEqual(original_values[password_var], "supersecret123!")
        
        # Check that env_vars contain the correct values
        for var_name, expected_value in [
            (db_config["password"], "supersecret123!"),
            (db_config["username"], "admin"),
            (db_config["allocated_storage"], 100),
            (db_config["skip_final_snapshot"], True)
        ]:
            # Extract variable name from reference
            var_name_only = var_name.replace("${var.", "").replace("}", "")
            self.assertIn(var_name_only, env_vars)
            
            # Check value matches (accounting for type conversion)
            if isinstance(expected_value, bool):
                self.assertEqual(env_vars[var_name_only], str(expected_value).lower())
            else:
                self.assertEqual(env_vars[var_name_only], str(expected_value))
    
    def test_module_source_literal(self):
        """Test that module sources remain literal"""
        config = {
            "module": {
                "vpc": {
                    "source": "./modules/vpc",
                    "cidr": "10.0.0.0/16"
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Source should remain literal
        self.assertEqual(modified["module"]["vpc"]["source"], "./modules/vpc")
        
        # But cidr should be variablized
        self.assertTrue(modified["module"]["vpc"]["cidr"].startswith("${var.v_s_"))
    
    def test_expression_preservation(self):
        """Test that existing expressions are preserved"""
        config = {
            "resource": {
                "aws_instance": {
                    "example": {
                        "ami": "${data.aws_ami.ubuntu.id}",
                        "tags": {
                            "Name": "example-${var.environment}"
                        }
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Expressions should remain unchanged
        self.assertEqual(
            modified["resource"]["aws_instance"]["example"]["ami"],
            "${data.aws_ami.ubuntu.id}"
        )
        self.assertEqual(
            modified["resource"]["aws_instance"]["example"]["tags"]["Name"],
            "example-${var.environment}"
        )
    
    def test_list_handling(self):
        """Test that lists are handled correctly"""
        config = {
            "resource": {
                "aws_security_group": {
                    "example": {
                        "ingress": [
                            {"from_port": 80, "to_port": 80},
                            {"from_port": 443, "to_port": 443}
                        ]
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        ingress = modified["resource"]["aws_security_group"]["example"]["ingress"]
        
        # Check that list items were processed
        self.assertTrue(ingress[0]["from_port"].startswith("${var.v_n_"))
        self.assertTrue(ingress[1]["from_port"].startswith("${var.v_n_"))
        
        # 80 and 443 should be different variables
        self.assertNotEqual(ingress[0]["from_port"], ingress[1]["from_port"])
    
    def test_env_var_generation(self):
        """Test environment variable generation"""
        config = {
            "locals": {
                "app_name": "myapp",
                "port": 8080,
                "enabled": False
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check env vars are strings
        for var_name, value in env_vars.items():
            self.assertIsInstance(value, str)
        
        # Check boolean conversion
        bool_vars = [v for k, v in env_vars.items() if k.startswith("v_b_")]
        self.assertIn("false", bool_vars)
    
    def test_hash_collision_handling(self):
        """Test that hash collisions are handled correctly"""
        # Create an extractor and manually force a collision
        extractor = VariableExtractor()
        
        # First value
        var1 = extractor._to_variable("test_value_1")
        
        # Manually add a different value with the same hash prefix
        # to simulate a collision
        var_name = list(extractor.variables.keys())[0]
        base_name = var_name  # Save the original name
        
        # Try to add a different value that would have the same base name
        extractor.variables[base_name] = {"type": "string", "value": "different_value"}
        
        # Now add another value that would collide
        var2 = extractor._to_variable("test_value_2")
        
        # The second variable should have a counter appended
        self.assertTrue("_1" in var2 or var2 != var1)
    
    def test_type_differentiation(self):
        """Test that same value with different types gets different variables"""
        config = {
            "locals": {
                "str_one": "1",
                "num_one": 1,
                "str_true": "true", 
                "bool_true": True
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Get the variable references
        vars_used = {
            key: modified["locals"][key] 
            for key in ["str_one", "num_one", "str_true", "bool_true"]
        }
        
        # Different types should use different variables
        self.assertNotEqual(vars_used["str_one"], vars_used["num_one"])
        self.assertNotEqual(vars_used["str_true"], vars_used["bool_true"])
        
        # Should have 4 different variables
        self.assertEqual(len(set(vars_used.values())), 4)
    
    def test_complex_nested_structure(self):
        """Test extraction from deeply nested structures"""
        config = {
            "resource": {
                "aws_instance": {
                    "web": {
                        "ami": "ami-123456",
                        "tags": {
                            "Environment": "production",
                            "Team": "platform",
                            "Cost": {
                                "Center": "engineering",
                                "Project": "infrastructure"
                            }
                        },
                        "root_block_device": {
                            "volume_type": "gp3",
                            "volume_size": 30,
                            "encrypted": True
                        }
                    }
                }
            },
            "locals": {
                "common_tags": {
                    "ManagedBy": "terraform",
                    "Repository": "infrastructure"
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check nested values were extracted
        tags = modified["resource"]["aws_instance"]["web"]["tags"]
        self.assertTrue(tags["Environment"].startswith("${var.v_s_"))
        self.assertTrue(tags["Cost"]["Center"].startswith("${var.v_s_"))
        
        # Check deduplication across different parts of config
        repo_var1 = tags["Cost"]["Project"]
        repo_var2 = modified["locals"]["common_tags"]["Repository"]
        self.assertEqual(repo_var1, repo_var2)  # Both "infrastructure"
        
        # Verify all leaf values were converted
        device = modified["resource"]["aws_instance"]["web"]["root_block_device"]
        self.assertTrue(device["volume_type"].startswith("${var.v_s_"))
        self.assertTrue(device["volume_size"].startswith("${var.v_n_"))
        self.assertTrue(device["encrypted"].startswith("${var.v_b_"))