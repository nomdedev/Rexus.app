from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric
"""
Submódulos de Inventario - Rexus.app

Importa submódulos refactorizados para mayor compatibilidad.
"""

# Importar submódulos disponibles
try:
    from .consultas_manager import ConsultasManager
    from .movimientos_manager import MovimientosManager
    from .productos_manager import ProductosManager

    print("[SUBMODULOS INVENTARIO] OK - Submodulos cargados correctamente")
except ImportError as e:
    print(f"[SUBMODULOS INVENTARIO] ERROR - Error importando submodulos: {e}")

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
