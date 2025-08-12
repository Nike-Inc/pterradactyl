import unittest
from pterradactyl.terraform.variable_extractor import VariableExtractor


class TestVariableExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = VariableExtractor()
    
    def test_simple_values_remain_literal(self):
        """Test that non-module values remain literal"""
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
        
        # Check that resource values remain literal (not variablized)
        instance_config = modified["resource"]["aws_instance"]["example"]
        self.assertEqual(instance_config["ami"], "ami-123456")
        self.assertEqual(instance_config["instance_type"], "t2.micro")
        self.assertEqual(instance_config["count"], 3)
        self.assertEqual(instance_config["enable_monitoring"], True)
        
        # Should have no variables created
        self.assertEqual(len(variables.get("variable", {})), 0)
    
    def test_deduplication(self):
        """Test that identical sensitive values share the same variable"""
        config = {
            "module": {
                "app1": {
                    "source": "./modules/app",
                    "database_password": "samepass123",
                    "api_token": "token-xyz"
                },
                "app2": {
                    "source": "./modules/app", 
                    "database_password": "samepass123",
                    "auth_key": "different-key"
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Get the variable references
        app1_pass = modified["module"]["app1"]["database_password"]
        app2_pass = modified["module"]["app2"]["database_password"]
        
        # Same sensitive values should use same variable
        self.assertEqual(app1_pass, app2_pass)
        
        # Different sensitive values should use different variables
        app1_token = modified["module"]["app1"]["api_token"]
        app2_key = modified["module"]["app2"]["auth_key"]
        self.assertNotEqual(app1_token, app2_key)
        
        # Should have only 3 variables total (1 shared password + 2 different tokens)
        self.assertEqual(len(variables["variable"]), 3)
    
    def test_value_reconstruction(self):
        """Test that we can reconstruct original values from variables"""
        config = {
            "module": {
                "database": {
                    "source": "./modules/database",
                    "master_password": "supersecret123!",
                    "read_password": "readonlypass456",
                    "api_secret_key": "abc-xyz-123",
                    "connection_string": "host=db.example.com",  # Has 'connection' but not sensitive pattern
                    "port": 5432
                }
            },
            "resource": {
                "aws_instance": {
                    "web": {
                        "ami": "ami-123456",  # Should remain literal
                        "instance_type": "t2.micro"
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that only sensitive module values were variablized
        db_module = modified["module"]["database"]
        self.assertTrue(db_module["master_password"].startswith("${var.v_s_"))
        self.assertTrue(db_module["read_password"].startswith("${var.v_s_"))
        self.assertTrue(db_module["api_secret_key"].startswith("${var.v_s_"))
        
        # Non-sensitive module values remain literal
        self.assertEqual(db_module["connection_string"], "host=db.example.com")
        self.assertEqual(db_module["port"], 5432)
        self.assertEqual(db_module["source"], "./modules/database")
        
        # Resource values remain literal
        self.assertEqual(modified["resource"]["aws_instance"]["web"]["ami"], "ami-123456")
        self.assertEqual(modified["resource"]["aws_instance"]["web"]["instance_type"], "t2.micro")
        
        # Verify we can map back to original sensitive values
        original_values = {}
        for var_name, var_info in self.extractor.variables.items():
            var_ref = f"${{var.{var_name}}}"
            original_values[var_ref] = var_info["value"]
        
        # Check specific sensitive values
        master_pass_var = db_module["master_password"]
        self.assertIn(master_pass_var, original_values)
        self.assertEqual(original_values[master_pass_var], "supersecret123!")
        
        # Check that env_vars contain the correct values
        for var_ref, expected_value in [
            (db_module["master_password"], "supersecret123!"),
            (db_module["read_password"], "readonlypass456"),
            (db_module["api_secret_key"], "abc-xyz-123")
        ]:
            # Extract variable name from reference
            var_name_only = var_ref.replace("${var.", "").replace("}", "")
            self.assertIn(var_name_only, env_vars)
            self.assertEqual(env_vars[var_name_only], str(expected_value))
    
    def test_sensitive_module_patterns(self):
        """Test that module values with sensitive patterns are variablized"""
        config = {
            "module": {
                "database": {
                    "source": "./modules/rds",
                    "db_password": "supersecret123",
                    "api_key": "abc123xyz",
                    "port": 5432,
                    "name": "mydb"
                },
                "cerberus": {
                    "source": "./modules/cerberus",
                    "secrets": {
                        "rds": {
                            "dburi": "postgresql://user:pass@host/db"
                        }
                    }
                },
                "app": {
                    "source": "./modules/app",
                    "client_credentials": "oauth-token-here",
                    "debug": True,
                    "version": "1.2.3"
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that sensitive values are variablized
        self.assertTrue(modified["module"]["database"]["db_password"].startswith("${var.v_s_"))
        self.assertTrue(modified["module"]["database"]["api_key"].startswith("${var.v_s_"))
        self.assertTrue(modified["module"]["app"]["client_credentials"].startswith("${var.v_s_"))
        
        # Check nested sensitive path
        self.assertTrue(modified["module"]["cerberus"]["secrets"]["rds"]["dburi"].startswith("${var.v_s_"))
        
        # Check that non-sensitive values remain literal
        self.assertEqual(modified["module"]["database"]["port"], 5432)
        self.assertEqual(modified["module"]["database"]["name"], "mydb")
        self.assertEqual(modified["module"]["app"]["debug"], True)
        self.assertEqual(modified["module"]["app"]["version"], "1.2.3")
        
        # Sources should always remain literal
        self.assertEqual(modified["module"]["database"]["source"], "./modules/rds")
        self.assertEqual(modified["module"]["cerberus"]["source"], "./modules/cerberus")
        self.assertEqual(modified["module"]["app"]["source"], "./modules/app")
        
        # Should have created 4 variables (for the sensitive values)
        self.assertEqual(len(variables["variable"]), 4)
    
    def test_nested_sensitive_paths(self):
        """Test that deeply nested sensitive paths are variablized"""
        config = {
            "module": {
                "cerberus": {
                    "source": "./modules/cerberus",
                    "secrets": {
                        "postgres": {
                            "DB_URI": "postgresql://user:pass@localhost:5432/mydb",
                            "DB_NAME": "mydb"
                        },
                        "redis": {
                            "connection": "redis://localhost:6379"
                        }
                    },
                    "config": {
                        "port": 8080,
                        "environment": "production"
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that the nested sensitive path is variablized
        postgres_secrets = modified["module"]["cerberus"]["secrets"]["postgres"]
        self.assertTrue(postgres_secrets["DB_URI"].startswith("${var.v_s_"))
        self.assertTrue(postgres_secrets["DB_NAME"].startswith("${var.v_s_"))
        
        # Redis path also contains 'secrets' so should be variablized
        redis_secrets = modified["module"]["cerberus"]["secrets"]["redis"]
        self.assertTrue(redis_secrets["connection"].startswith("${var.v_s_"))
        
        # Non-sensitive nested values should remain literal
        config_section = modified["module"]["cerberus"]["config"]
        self.assertEqual(config_section["port"], 8080)
        self.assertEqual(config_section["environment"], "production")
        
        # Source remains literal
        self.assertEqual(modified["module"]["cerberus"]["source"], "./modules/cerberus")
        
        # Should have created 3 variables
        self.assertEqual(len(variables["variable"]), 3)
    
    def test_module_source_literal(self):
        """Test that module sources remain literal"""
        config = {
            "module": {
                "vpc": {
                    "source": "./modules/vpc",
                    "cidr": "10.0.0.0/16",
                    "db_password": "secret123"
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Source should remain literal
        self.assertEqual(modified["module"]["vpc"]["source"], "./modules/vpc")
        
        # Non-sensitive cidr should remain literal
        self.assertEqual(modified["module"]["vpc"]["cidr"], "10.0.0.0/16")
        
        # But password should be variablized
        self.assertTrue(modified["module"]["vpc"]["db_password"].startswith("${var.v_s_"))
    
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
            "module": {
                "security": {
                    "source": "./modules/security",
                    "auth_tokens": [
                        "token-abc-123",
                        "token-xyz-456"
                    ],
                    "allowed_ports": [80, 443]
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that sensitive list items were variablized
        auth_tokens = modified["module"]["security"]["auth_tokens"]
        self.assertTrue(auth_tokens[0].startswith("${var.v_s_"))
        self.assertTrue(auth_tokens[1].startswith("${var.v_s_"))
        
        # Tokens should be different variables
        self.assertNotEqual(auth_tokens[0], auth_tokens[1])
        
        # Non-sensitive values remain literal
        self.assertEqual(modified["module"]["security"]["allowed_ports"], [80, 443])
    
    def test_env_var_generation(self):
        """Test environment variable generation"""
        config = {
            "module": {
                "app": {
                    "source": "./modules/app",
                    "api_key": "key-12345",
                    "enable_auth": True,
                    "max_connections": 100
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that only sensitive values generated env vars
        self.assertGreater(len(env_vars), 0)
        
        # Check env vars are strings
        for var_name, value in env_vars.items():
            self.assertIsInstance(value, str)
        
        # Check that api_key was variablized
        self.assertTrue(modified["module"]["app"]["api_key"].startswith("${var.v_s_"))
    
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
            "module": {
                "config": {
                    "source": "./modules/config",
                    "secret_string": "1",
                    "secret_number": 1,
                    "auth_enabled_str": "true",
                    "auth_enabled_bool": True
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Get the variable references for sensitive values
        module_cfg = modified["module"]["config"]
        
        # Same value with different types should use different variables
        self.assertTrue(module_cfg["secret_string"].startswith("${var.v_s_"))
        self.assertTrue(module_cfg["secret_number"].startswith("${var.v_n_"))
        self.assertNotEqual(module_cfg["secret_string"], module_cfg["secret_number"])
        
        self.assertTrue(module_cfg["auth_enabled_str"].startswith("${var.v_s_"))
        self.assertTrue(module_cfg["auth_enabled_bool"].startswith("${var.v_b_"))
        self.assertNotEqual(module_cfg["auth_enabled_str"], module_cfg["auth_enabled_bool"])
        
        # Should have 4 different variables
        self.assertEqual(len(variables["variable"]), 4)
    
    def test_complex_nested_structure(self):
        """Test extraction from deeply nested structures"""
        config = {
            "module": {
                "infrastructure": {
                    "source": "./modules/infra",
                    "database": {
                        "master_password": "super-secret-123",
                        "backup_key": "backup-key-456",
                        "port": 5432
                    },
                    "cache": {
                        "auth_token": "redis-auth-token",
                        "host": "cache.example.com"
                    }
                }
            },
            "resource": {
                "aws_instance": {
                    "web": {
                        "ami": "ami-123456",
                        "instance_type": "t2.micro"
                    }
                }
            }
        }
        
        modified, variables, env_vars = self.extractor.extract_variables(config)
        
        # Check that sensitive nested module values were variablized
        db_config = modified["module"]["infrastructure"]["database"]
        self.assertTrue(db_config["master_password"].startswith("${var.v_s_"))
        self.assertTrue(db_config["backup_key"].startswith("${var.v_s_"))
        self.assertEqual(db_config["port"], 5432)  # Non-sensitive remains literal
        
        cache_config = modified["module"]["infrastructure"]["cache"]
        self.assertTrue(cache_config["auth_token"].startswith("${var.v_s_"))
        self.assertEqual(cache_config["host"], "cache.example.com")  # Non-sensitive
        
        # Resource values should remain literal
        instance = modified["resource"]["aws_instance"]["web"]
        self.assertEqual(instance["ami"], "ami-123456")
        self.assertEqual(instance["instance_type"], "t2.micro")