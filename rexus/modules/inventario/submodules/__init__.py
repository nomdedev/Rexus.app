"""
Submódulos de Inventario - Rexus.app

Importa submódulos refactorizados para mayor compatibilidad.
"""

# Importar submódulos disponibles
try:

import logging
logger = logging.getLogger(__name__)

from .consultas_manager import ConsultasManager
from .movimientos_manager import MovimientosManager
from .productos_manager import ProductosManager

logger.info()
except ImportError as e:
    logger.info(f"[SUBMODULOS INVENTARIO] ERROR - Error importando submodulos: {e}")

# Crear clases dummy para evitar errores
class ConsultasManager:
        def __init__(self, db_connection=None):
            pass

class MovimientosManager:
        def __init__(self, db_connection=None):
            pass

class ProductosManager:
        def __init__(self, db_connection=None):
            pass


__all__ = ["ProductosManager", "MovimientosManager", "ConsultasManager"]
