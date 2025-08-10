"""
Submódulos de Vidrios - Rexus.app

Arquitectura modular para gestión de vidrios:
- ProductosManager: CRUD de productos de vidrio
- ObrasManager: Asignación de vidrios a obras
- ConsultasManager: Búsquedas, filtros y estadísticas
"""

from .consultas_manager import ConsultasManager
from .obras_manager import ObrasManager
from .productos_manager import ProductosManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric

__all__ = ["ProductosManager", "ObrasManager", "ConsultasManager"]
