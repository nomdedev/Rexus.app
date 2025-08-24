"""
Submódulos de Vidrios - Rexus.app

Arquitectura modular para gestión de vidrios:
- ProductosManager: CRUD de productos de vidrio
- ObrasManager: Asignación de vidrios a obras
- ConsultasManager: Búsquedas, filtros y estadísticas
"""


import logging
logger = logging.getLogger(__name__)

from .consultas_manager import ConsultasManager
from .obras_manager import ObrasManager
from .productos_manager import ProductosManager

__all__ = [ "ObrasManager", "ConsultasManager"]
