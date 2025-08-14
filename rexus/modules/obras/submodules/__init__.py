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

__all__ = ["ProyectosManager", "RecursosManager", "ConsultasManager"]
