"""
Módulo de Inventario

Gestiona el inventario de productos, stock, movimientos y reportes.
"""

from .controller import InventarioController
from .model import InventarioModel
from .view import InventarioView

__all__ = ["InventarioModel", "InventarioView", "InventarioController"]
