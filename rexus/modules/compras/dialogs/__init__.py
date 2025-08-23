"""
Diálogos del módulo de Compras

Este paquete contiene los diálogos especializados para la gestión de compras.
"""


import logging
logger = logging.getLogger(__name__)

from .dialog_proveedor import DialogProveedor
from .dialog_seguimiento import DialogSeguimiento

__all__ = ['DialogProveedor', 'DialogSeguimiento']
