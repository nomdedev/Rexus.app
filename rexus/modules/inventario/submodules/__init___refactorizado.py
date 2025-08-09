"""
Submódulos de Inventario Refactorizados - Rexus.app v2.0.0

Arquitectura modular para gestión de inventario:

- productos_manager_refactorizado.py: CRUD de productos, validaciones, códigos
- movimientos_manager_refactorizado.py: Movimientos de stock, auditoría
- consultas_manager_refactorizado.py: Búsquedas, paginación, estadísticas

Cada submódulo es independiente y especializado siguiendo la metodología
probada en usuarios, obras y vidrios.
"""

from .consultas_manager_refactorizado import ConsultasManager
from .movimientos_manager_refactorizado import MovimientosManager
from .productos_manager_refactorizado import ProductosManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["ProductosManager", "MovimientosManager", "ConsultasManager"]
