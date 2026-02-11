"""
Alias para mantener compatibilidad con imports existentes.
Este archivo redirige a app_logger.py que es el sistema de logging actual.

Migrado desde logging_config.py -> app_logger.py
"""

# Re-exportar todas las funciones y clases desde app_logger
from rexus.utils.app_logger import (
    RexusLogger,
    app_logger,
    get_logger,
    log_info,
    log_warning,
    log_error,
    log_critical,
    log_debug,
    log_security,
    log_database,
    log_performance,
    replace_print_with_logging
)

# Para compatibilidad adicional, exportar también con el nombre original
__all__ = [
    'RexusLogger',
    'app_logger',
    'get_logger',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    'log_debug',
    'log_security',
    'log_database',
    'log_performance',
    'replace_print_with_logging'
]
