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
from .controller import VidriosController
from .model import ModeloVidrios, VidriosModel
from .view import VidriosView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Exportar submódulos especializados si existen
try:
    from .submodules.productos_manager import ProductosManager
    from .submodules.obras_manager import ObrasManager
    from .submodules.consultas_manager import ConsultasManager
    _submodules_available = True
except ImportError:
    _submodules_available = False

__all__ = [
    "ModeloVidrios",
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
