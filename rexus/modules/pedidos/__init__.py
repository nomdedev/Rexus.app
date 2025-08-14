"""Módulo de Pedidos"""

from .controller import PedidosController
from .model import PedidosModel
from .view_complete import PedidosViewComplete as PedidosView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["PedidosModel", "PedidosView", "PedidosController"]
