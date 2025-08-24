"""
Diálogos del módulo de inventario.
"""


import logging
logger = logging.getLogger(__name__)

from .reserva_dialog import ReservaDialog

# Importar diálogos adicionales con manejo de errores
try:
    __all__ = [ "DialogoEditarProducto", "DialogoMovimientoInventario", "DialogoHistorialProducto"]
except ImportError as e:
    logger.info(f"[WARNING] Could not import missing dialogs: {e}")
__all__ = ["ReservaDialog"]
