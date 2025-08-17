# Compatibility shim for legacy import path:
# from src.modules.vidrios.model_consolidado import VidriosModel
try:
    from rexus.modules.vidrios.model_consolidado import VidriosModel  # type: ignore
    __all__ = ["VidriosModel"]
except Exception:
    try:
        from rexus.modules.vidrios.model import VidriosModel  # type: ignore
        __all__ = ["VidriosModel"]
    except Exception:
        class VidriosModel:  # type: ignore
            def __init__(self, db_connection=None, *args, **kwargs):
                self.db_connection = db_connection
                self._allowed_tables = set(['vidrios', 'vidrios_obra', 'pedidos_vidrios'])

            def obtener_todos_vidrios(self, filtros=None):
                # Demo dataset compatible with legacy expectations
                return []

            def obtener_vidrios_por_obra(self, obra_id):
                return []

            def obtener_estadisticas(self):
                return {'total_vidrios': 0}

        __all__ = ["VidriosModel"]
