"""
Submódulos de Inventario - Rexus.app

Importa submódulos refactorizados para mayor compatibilidad.
"""

# Importar submódulos refactorizados si están disponibles, sino los originales
try:
    from .consultas_manager_refactorizado import ConsultasManager
    from .movimientos_manager_refactorizado import MovimientosManager
    from .productos_manager_refactorizado import ProductosManager

    print("[SUBMÓDULOS INVENTARIO] ✅ Submódulos refactorizados cargados")
except ImportError as e:
    print(f"[SUBMÓDULOS INVENTARIO] ⚠️ Error importando refactorizados: {e}")
    try:
        from .consultas_manager import ConsultasManager
        from .movimientos_manager import MovimientosManager
        from .productos_manager import ProductosManager

        print("[SUBMÓDULOS INVENTARIO] ✅ Submódulos originales cargados como fallback")
    except ImportError as e2:
        print(f"[SUBMÓDULOS INVENTARIO] ❌ Error importando submódulos: {e2}")

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
