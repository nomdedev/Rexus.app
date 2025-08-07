"""
Submódulos de Vidrios - Rexus.app

Arquitectura modular para gestión de vidrios:

- productos_manager.py: CRUD de productos vidrios, validaciones
- obras_manager.py: Asignaciones de vidrios a obras, pedidos
- consultas_manager.py: Búsquedas, filtros, estadísticas

Cada submódulo es independiente y especializado.
"""

from .consultas_manager import ConsultasManager
from .obras_manager import ObrasManager
from .productos_manager import ProductosManager

__all__ = ["ProductosManager", "ObrasManager", "ConsultasManager"]
