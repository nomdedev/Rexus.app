"""
Submódulos de Inventario - Rexus.app

Arquitectura modular para gestión de inventario:

- productos_manager.py: CRUD de productos, validaciones, QR
- movimientos_manager.py: Movimientos de stock, auditoría
- consultas_manager.py: Búsquedas, paginación, estadísticas

Cada submódulo es independiente y especializado.
"""

from .consultas_manager import ConsultasManager
from .movimientos_manager import MovimientosManager
from .productos_manager import ProductosManager

__all__ = ["ProductosManager", "MovimientosManager", "ConsultasManager"]
