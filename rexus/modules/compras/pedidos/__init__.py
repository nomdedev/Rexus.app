"""Módulo de Compras/Pedidos"""

from .controller import ComprasPedidosController
from .model import PedidosModel
from .view import PedidosView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["PedidosModel", "PedidosView", "ComprasPedidosController"]
