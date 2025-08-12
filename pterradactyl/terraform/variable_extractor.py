"""Extract argument values from Terraform configuration and convert to variables"""
import hashlib
from typing import Any, Dict, Tuple


class VariableExtractor:
    """Extracts leaf values and converts them to variables"""
    
    # Patterns that indicate a value might be sensitive (checked case-insensitive)
    SENSITIVE_PATTERNS = [
        'secret',
        'pass',    # Matches password, passwd, passphrase, etc.
        'key',     # Matches key, apikey, access_key, private_key, etc.
        'token',
        'cred',    # Matches credential, credentials, etc.
        'auth',    # Matches auth, authorization, authentication, etc.
        'cert',    # Matches cert, certificate, etc.
    ]
    
    # Context-specific literal paths: (parent_context, key) -> must be literal
    LITERAL_CONTEXTS = {
        # Module meta-arguments
        ('module', 'source'): True,
        ('module', 'version'): True,
        ('module', 'count'): True,
        ('module', 'for_each'): True,
        ('module', 'providers'): True,
        ('module', 'depends_on'): True,
        
        # Provider meta-arguments
        ('provider', 'alias'): True,
        ('provider', 'version'): True,
        
        # Resource meta-arguments
        ('resource', 'count'): True,
        ('resource', 'for_each'): True,
        ('resource', 'depends_on'): True,
        ('resource', 'provider'): True,
        ('resource', 'lifecycle'): True,
        
        # Data source meta-arguments
        ('data', 'count'): True,
        ('data', 'for_each'): True,
        ('data', 'depends_on'): True,
        ('data', 'provider'): True,
        
        # Terraform configuration
        ('terraform', 'required_version'): True,
        ('terraform', 'required_providers'): True,
    }
    
    # Parent paths where ALL child values must be literal
    LITERAL_PARENT_PATHS = {
        ('terraform', 'backend'),  # All backend configuration
        ('terraform', 'required_providers'),  # Provider requirements
    }
    
    def __init__(self):
        self.variables = {}  # var_name -> {type, value}
        self.value_to_var = {}  # (type, value) -> var_name for deduplication
        
    def extract_variables(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, str]]:
        """Extract all leaf values as variables"""
        modified_config = self._process(config, [])
        
        # Build variable definitions and environment variables
        variable_defs = {
            name: {"type": info["type"]} 
            for name, info in self.variables.items()
        }
        
        env_vars = {
            name: str(info["value"]).lower() if info["type"] == "bool" else str(info["value"])
            for name, info in self.variables.items()
        }
        
        return modified_config, {"variable": variable_defs}, env_vars
    
    def _process(self, value: Any, path: list) -> Any:
        """Process any value recursively"""
        # Recursively process containers
        if isinstance(value, dict):
            return {k: self._process(v, path + [k]) for k, v in value.items()}
        if isinstance(value, list):
            return [self._process(item, path + [f'[{i}]']) for i, item in enumerate(value)]
        
        # Handle leaf values
        if value is None or self._is_expression(value):
            return value
            
        # Only variablize module configuration values with sensitive names
        clean_path = [p for p in path if not p.startswith('[')]
        if len(clean_path) >= 3 and clean_path[0] == 'module':
            # This is a module configuration value (e.g., module.vpc.database_password)
            # But skip if it's a literal path (like module.vpc.source)
            if self._is_literal_path(path):
                return value
            
            # Check if any part of the path contains sensitive patterns
            if self._contains_sensitive_pattern(clean_path):
                # Convert to variable
                return self._to_variable(value)
            
        # Everything else remains literal
        return value
    
    def _contains_sensitive_pattern(self, path: list) -> bool:
        """Check if any part of the path contains sensitive patterns"""
        # Join path elements and convert to lowercase for checking
        path_str = '.'.join(path).lower()
        
        # Check if any sensitive pattern appears in the path
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in path_str:
                return True
        
        return False
    
    def _is_expression(self, value: Any) -> bool:
        """Check if value is already a Terraform expression"""
        return isinstance(value, str) and '${' in value
    
    def _is_literal_path(self, path: list) -> bool:
        """Check if this path should remain literal"""
        clean_path = [p for p in path if not p.startswith('[')]  # Remove array indices
        
        if not clean_path:
            return False
            
        # Check if we're inside a literal parent path
        for parent_path in self.LITERAL_PARENT_PATHS:
            if len(clean_path) >= len(parent_path):
                if clean_path[:len(parent_path)] == list(parent_path):
                    return True
        
        # Check context-specific literals
        if len(clean_path) >= 2:
            # Get the context (module, resource, provider, etc.)
            context = clean_path[0]
            key = clean_path[-1]
            
            # For resources and data sources, check one level deeper
            if context in ['resource', 'data'] and len(clean_path) >= 3:
                # Skip the resource type, check the actual key
                if (context, key) in self.LITERAL_CONTEXTS:
                    return True
            else:
                # For module, provider, terraform blocks
                if (context, key) in self.LITERAL_CONTEXTS:
                    return True
                    
        return False
    
    def _to_variable(self, value: Any) -> str:
        """Convert value to variable reference"""
        # Determine type
        type_map = {
            bool: "bool",
            int: "number", 
            float: "number",
            str: "string"
        }
        var_type = type_map.get(type(value), "string")
        
        # Check if we already have this value
        key = (var_type, value)
        if key in self.value_to_var:
            return f"${{var.{self.value_to_var[key]}}}"
        
        # Generate new variable name
        hash_val = hashlib.sha256(f"{var_type}:{value}".encode()).hexdigest()[:8]
        base_name = f"v_{var_type[0]}_{hash_val}"
        
        # Handle hash collisions
        var_name = base_name
        counter = 0
        while var_name in self.variables:
            counter += 1
            var_name = f"{base_name}_{counter}"
        
        # Store the variable
        self.variables[var_name] = {"type": var_type, "value": value}
        self.value_to_var[key] = var_name
        
        return f"${{var.{var_name}}}"
