"""
Módulo de Gestión de Vidrios - Rexus.app (Refactorizado)

Este módulo maneja todo lo relacionado con el inventario de vidrios:
- Gestión de productos de vidrio (ProductosManager)
- Control de stock y validaciones
- Precios y proveedores
- Asignación a obras (ObrasManager)
- Búsquedas y estadísticas (ConsultasManager)

Arquitectura modular v2.0 con compatibilidad hacia atrás.
"""

# Exportar el modelo principal y vistas
from .controller import VidriosController
from .model import ModeloVidrios, VidriosModel
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Exportar modelo refactorizado
from .model_refactorizado import ModeloVidriosRefactorizado
from .submodules.consultas_manager import ConsultasManager
from .submodules.obras_manager import ObrasManager

# Exportar submódulos especializados
from .submodules.productos_manager import ProductosManager
from .view import VidriosView

__all__ = [
    # Compatibilidad hacia atrás
    "ModeloVidrios",
    "VidriosModel",
    "VidriosView",
    "VidriosController",
    # Nueva arquitectura modular
    "ModeloVidriosRefactorizado",
    "ProductosManager",
    "ObrasManager",
    "ConsultasManager",
]

__all__ = ["VidriosModel", "VidriosView", "VidriosController"]
