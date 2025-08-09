"""
Módulo de Inventario

Gestiona el inventario de productos, stock, movimientos y reportes.
Incluye arquitectura modular con submódulos especializados.
"""

from .controller import InventarioController
from .model_inventario_refactorizado import (
    ModeloInventarioRefactorizado as InventarioModel,
)
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Submódulos especializados
from .submodules import ConsultasManager, MovimientosManager, ProductosManager
from .view import InventarioView

__all__ = [
    "InventarioController",
    "InventarioModel",
    "InventarioView",
    "ProductosManager",
    "MovimientosManager",
    "ConsultasManager",
]

__all__ = ["InventarioModel", "InventarioView", "InventarioController"]
