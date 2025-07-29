"""Módulo de Compras/Pedidos"""

from .controller import ComprasPedidosController
from .model import PedidosModel
from .view import PedidosView

__all__ = ["PedidosModel", "PedidosView", "ComprasPedidosController"]
