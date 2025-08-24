"""Módulo de Pedidos"""


import logging
logger = logging.getLogger(__name__)

from .controller import PedidosController
from .model import PedidosModel
from .view_complete import PedidosViewComplete as PedidosView

__all__ = ["PedidosModel", "PedidosView", "PedidosController"]
