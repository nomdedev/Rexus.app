"""Módulo de Compras/Pedidos"""


import logging
logger = logging.getLogger(__name__)

from .controller import ComprasPedidosController
from .model import PedidosModel
from .view import PedidosView

__all__ = [, "PedidosView", "ComprasPedidosController"]
