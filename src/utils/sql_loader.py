"""
SQL File Loader Utility
Provides secure loading of SQL queries from external files.
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path

class SQLLoader:
    """
    Utility class for loading SQL queries from external files.
    Provides security validation and parameterized query support.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize SQL loader with base path for SQL files.
        
        Args:
            base_path: Base directory path for SQL files. 
                      Defaults to sql_queries/ in project root.
        """
        if base_path is None:
            project_root = Path(__file__).parent.parent.parent
            base_path = project_root / "scripts" / "sql"
        
        self.base_path = Path(base_path)
        self._query_cache = {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure base path exists
        self.base_path.mkdir(exist_ok=True, parents=True)
    
    def load_query(self, module: str, query_name: str) -> str:
        """
        Load SQL query from file.
        
        Args:
            module: Module name (inventario, herrajes, vidrios, etc.)
            query_name: Query file name without .sql extension
            
        Returns:
            SQL query string
            
        Raises:
            FileNotFoundError: If query file doesn't exist
            ValueError: If invalid characters in module/query_name
        """
        # Security validation
        self._validate_path_component(module)
        self._validate_path_component(query_name)
        
        # Create cache key
        cache_key = f"{module}.{query_name}"
        
        # Check cache first
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]
        
        # Construct file path
        query_file = self.base_path / module / f"{query_name}.sql"
        
        if not query_file.exists():
            raise FileNotFoundError(f"SQL query file not found: {query_file}")
        
        try:
            # Load and cache query
            with open(query_file, 'r', encoding='utf-8') as f:
                query = f.read().strip()
            
            self._query_cache[cache_key] = query
            self.logger.debug(f"Loaded SQL query: {module}.{query_name}")
            
            return query
        
        except Exception as e:
            self.logger.error(f"Error loading SQL query {module}.{query_name}: {e}")
            raise
    
    def load_query_with_params(self, module: str, query_name: str, 
                             params: Dict[str, Any]) -> str:
        """
        Load SQL query and replace named parameters.
        
        Args:
            module: Module name
            query_name: Query file name
            params: Dictionary of parameters to replace
            
        Returns:
            SQL query with parameters replaced
        """
        query = self.load_query(module, query_name)
        
        # Replace named parameters safely
        for param_name, param_value in params.items():
            placeholder = f"{{{param_name}}}"
            if placeholder in query:
                # Basic validation for parameter values
                safe_value = self._sanitize_parameter(param_value)
                query = query.replace(placeholder, str(safe_value))
        
        return query
    
    def clear_cache(self):
        """Clear the query cache."""
        self._query_cache.clear()
        self.logger.debug("SQL query cache cleared")
    
    def list_queries(self, module: str) -> list:
        """
        List available queries for a module.
        
        Args:
            module: Module name
            
        Returns:
            List of available query names (without .sql extension)
        """
        self._validate_path_component(module)
        
        module_path = self.base_path / module
        if not module_path.exists():
            return []
        
        queries = []
        for file_path in module_path.glob("*.sql"):
            queries.append(file_path.stem)
        
        return sorted(queries)
    
    def _validate_path_component(self, component: str):
        """
        Validate path component for security.
        
        Args:
            component: Path component to validate
            
        Raises:
            ValueError: If component contains invalid characters
        """
        if not component:
            raise ValueError("Path component cannot be empty")
        
        # Check for path traversal attempts
        if ".." in component or "/" in component or "\\" in component:
            raise ValueError(f"Invalid path component: {component}")
        
        # Check for special characters
        if not component.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Path component contains invalid characters: {component}")
    
    def _sanitize_parameter(self, value: Any) -> str:
        """
        Sanitize parameter value for SQL injection prevention.
        
        Args:
            value: Parameter value to sanitize
            
        Returns:
            Sanitized parameter value
        """
        if value is None:
            return "NULL"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, bool):
            return "1" if value else "0"
        
        # For strings, basic escaping (note: use parameterized queries for production)
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized = value.replace("'", "''").replace(";", "").replace("--", "")
            return f"'{sanitized}'"
        
        return str(value)

# Global SQL loader instance
sql_loader = SQLLoader()

def load_sql(module: str, query_name: str) -> str:
    """
    Convenience function to load SQL query.
    
    Args:
        module: Module name
        query_name: Query name
        
    Returns:
        SQL query string
    """
    return sql_loader.load_query(module, query_name)

def load_sql_with_params(module: str, query_name: str, 
                        params: Dict[str, Any]) -> str:
    """
    Convenience function to load SQL query with parameters.
    
    Args:
        module: Module name
        query_name: Query name
        params: Parameters dictionary
        
    Returns:
        SQL query with parameters replaced
    """
    return sql_loader.load_query_with_params(module, query_name, params)