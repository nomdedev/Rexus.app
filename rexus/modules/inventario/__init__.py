"""
Módulo de Inventario

Gestiona el inventario de productos, stock, movimientos y reportes.
Incluye arquitectura modular con submódulos especializados.
"""


import logging
logger = logging.getLogger(__name__)

from .controller import InventarioController
from .model import (
    InventarioModel,
)

# Submódulos especializados
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
