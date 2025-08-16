# Compatibility shim for legacy import path:
# from src.modules.inventario.model_consolidado import InventarioModel
try:
    # Prefer exact consolidated implementation if migrated
    from rexus.modules.inventario.model_consolidado import InventarioModel  # type: ignore
    __all__ = ["InventarioModel"]
except Exception:
    try:
        # Common alternative names in the migrated code
        from rexus.modules.inventario.model import InventarioModel  # type: ignore
        __all__ = ["InventarioModel"]
    except Exception:
        try:
            from rexus.modules.inventario.model_inventario_refactorizado import InventarioModel  # type: ignore
            __all__ = ["InventarioModel"]
        except Exception:
            # Fallback stub that raises when instantiated to make failures explicit
            class InventarioModel:  # type: ignore
                def __init__(self, *args, **kwargs):
                    raise ImportError("InventarioModel not found in rexus.modules.inventario; please map the implementation or update legacy tests")
            __all__ = ["InventarioModel"]
