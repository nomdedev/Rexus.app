"""
Diálogos del módulo de inventario.
"""

from .reserva_dialog import ReservaDialog

# Importar diálogos adicionales con manejo de errores
try:
    from .missing_dialogs import DialogoEditarProducto, DialogoMovimientoInventario, DialogoHistorialProducto
    __all__ = ["ReservaDialog", "DialogoEditarProducto", "DialogoMovimientoInventario", "DialogoHistorialProducto"]
except ImportError as e:
    print(f"[WARNING] Could not import missing dialogs: {e}")
    __all__ = ["ReservaDialog"]
