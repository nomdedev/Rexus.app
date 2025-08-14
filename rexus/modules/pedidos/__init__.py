"""Módulo de Pedidos"""

from .controller import PedidosController
from .model import PedidosModel
from .view_complete import PedidosViewComplete as PedidosView

__all__ = ["PedidosModel", "PedidosView", "PedidosController"]
