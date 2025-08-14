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

__all__ = ["ProductosManager", "ObrasManager", "ConsultasManager"]
