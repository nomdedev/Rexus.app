# -*- coding: utf-8 -*-
"""
Helper module for importing Python modules with names starting with numbers.

This module provides utilities to import modules that cannot be imported
using standard dot notation due to Python's syntax restrictions.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Optional, Any, Tuple


def import_module_from_path(module_path: str, module_name: Optional[str] = None) -> Tuple[Any, bool, str]:
    """
    Import a module from its file path using importlib.util.spec_from_file_location.

    This function works around Python's restriction on importing modules with
    names that start with numbers.

    Args:
        module_path: Absolute or relative path to the module file
        module_name: Optional name for the module in sys.modules

    Returns:
        Tuple of (module, success, error_message)
        - module: The imported module object or None if failed
        - success: True if import succeeded, False otherwise
        - error_message: Error message if failed, empty string otherwise
    """
    try:
        path = Path(module_path)
        if not path.exists():
            return None, False, f"File not found: {module_path}"

        if module_name is None:
            # Create a valid module name from the path
            # Replace number prefixes and invalid characters
            module_name = "rexus_module_" + str(path).replace("\\", "_").replace("/", "_").replace(".", "_")

        # Use importlib.util to load the module from file
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None, False, f"Could not create spec for module: {module_path}"

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module, True, ""

    except Exception as e:
        return None, False, f"Error importing module: {str(e)}"


def import_numeric_rexus_module(module_dotted_path: str) -> Tuple[Any, bool, str]:
    """
    Import a Rexus module with numeric prefix using its dotted path.

    Handles paths like 'rexus.modules.02_inventario.controller' by
    constructing the actual file path and importing it.

    Args:
        module_dotted_path: Dotted path to the module (e.g., 'rexus.modules.02_inventario.controller')

    Returns:
        Tuple of (module, success, error_message)
    """
    try:
        # Try standard import first (may work if __init__.py handles it)
        import importlib
        try:
            module = importlib.import_module(module_dotted_path)
            return module, True, ""
        except (ImportError, ValueError) as e:
            # Fall back to file path import
            parts = module_dotted_path.split('.')
            if len(parts) < 3:
                return None, False, f"Invalid module path: {module_dotted_path}"

            # Convert dotted path to file path
            # Assuming the project root is in sys.path
            module_file = module_dotted_path.replace('.', '/') + '.py'

            # Try to find the module in the project
            for path_entry in sys.path:
                full_path = Path(path_entry) / module_file
                if full_path.exists():
                    return import_module_from_path(str(full_path), module_dotted_path.replace('.', '_'))

            return None, False, f"Could not locate module file for: {module_dotted_path}"

    except Exception as e:
        return None, False, f"Error importing module: {str(e)}"


def get_class_from_module(module_path: str, class_name: str) -> Tuple[Any, bool, str]:
    """
    Import a module and get a specific class from it.

    Args:
        module_path: Path to the module file
        class_name: Name of the class to retrieve

    Returns:
        Tuple of (class, success, error_message)
    """
    module, success, error = import_module_from_path(module_path)
    if not success:
        return None, False, error

    if not hasattr(module, class_name):
        return None, False, f"Class '{class_name}' not found in module"

    return getattr(module, class_name), True, ""


# Global flag to track module availability
_module_availability = {}


def check_module_available(module_identifier: str) -> bool:
    """
    Check if a module is available for import.

    Results are cached in _module_availability dict.

    Args:
        module_identifier: Either a file path or dotted module path

    Returns:
        True if module is available, False otherwise
    """
    if module_identifier in _module_availability:
        return _module_availability[module_identifier]

    # Try to determine if it's a path or dotted name
    if '/' in module_identifier or '\\' in module_identifier or module_identifier.endswith('.py'):
        module, success, _ = import_module_from_path(module_identifier)
    else:
        module, success, _ = import_numeric_rexus_module(module_identifier)

    _module_availability[module_identifier] = success
    return success
