"""
Submódulos de Inventario - Rexus.app

Importa submódulos refactorizados para mayor compatibilidad.
"""

# Importar submódulos disponibles
import logging
logger = logging.getLogger(__name__)

# TODO: Arreglar todos los managers que tienen errores de indentación
# from .base_utilities import BaseUtilities
# from .consultas_manager import ConsultasManager
# from .movimientos_manager import MovimientosManager
# from .productos_manager import ProductosManager

logger.info("[SUBMODULOS INVENTARIO] __init__.py cargado (managers temporalmente deshabilitados)")

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
