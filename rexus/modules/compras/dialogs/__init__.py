"""
Diálogos del módulo de Compras

Este paquete contiene los diálogos especializados para la gestión de compras.
"""

from .dialog_proveedor import DialogProveedor
from .dialog_seguimiento import DialogSeguimiento
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ['DialogProveedor', 'DialogSeguimiento']