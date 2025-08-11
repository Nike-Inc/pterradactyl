"""Extract argument values from Terraform configuration and convert to variables"""
import hashlib
from typing import Any, Dict, Tuple


class VariableExtractor:
    """Extracts leaf values and converts them to variables"""
    
    # Paths where strings must remain literal (checked from end of path)
    LITERAL_PATHS = {
        ('module', '*', 'source'),
        ('provider', '*', 'alias'),
        ('*', 'depends_on'),
        ('*', 'count'),
        ('*', 'for_each'),
        ('*', 'providers'),
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
            
        # Check if string should remain literal
        if isinstance(value, str) and self._is_literal_path(path):
            return value
            
        # Convert to variable
        return self._to_variable(value)
    
    def _is_expression(self, value: Any) -> bool:
        """Check if value is already a Terraform expression"""
        return isinstance(value, str) and '${' in value
    
    def _is_literal_path(self, path: list) -> bool:
        """Check if path matches any literal pattern"""
        clean_path = [p for p in path if not p.startswith('[')]  # Remove array indices
        
        for pattern in self.LITERAL_PATHS:
            # Match pattern from end of path
            if len(clean_path) >= len(pattern):
                if all(p == '*' or p == clean_path[-(i+1)] 
                       for i, p in enumerate(reversed(pattern))):
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