"""
Submódulos de Obras - Rexus.app

Arquitectura modular para gestión de obras:
- ProyectosManager: CRUD de proyectos y obras principales
- RecursosManager: Gestión de materiales y personal
- ConsultasManager: Búsquedas, filtros y estadísticas
"""

from .consultas_manager import ConsultasManager
from .proyectos_manager import ProyectosManager
from .recursos_manager import RecursosManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric

__all__ = ["ProyectosManager", "RecursosManager", "ConsultasManager"]
