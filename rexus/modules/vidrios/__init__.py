"""
Módulo de Gestión de Vidrios - Rexus.app

Este módulo maneja todo lo relacionado con el inventario de vidrios:
- Gestión de productos de vidrio
- Control de stock y validaciones
- Precios y proveedores
- Asignación a obras
- Búsquedas y estadísticas
"""

# Exportar el modelo principal y vistas

import logging
logger = logging.getLogger(__name__)

from .controller import VidriosController
from .model import ModeloVidrios, VidriosModel
from .view import VidriosModernView as VidriosView

# Exportar submódulos especializados si existen
try:
    _submodules_available = True
except ImportError:
    _submodules_available = False

__all__ = [
    "VidriosModel",
    "VidriosView",
    "VidriosController",
]

if _submodules_available:
    __all__.extend([
        "ProductosManager",
        "ObrasManager",
        "ConsultasManager",
    ])
