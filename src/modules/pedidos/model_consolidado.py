# Compatibility shim for legacy import path:
# from src.modules.pedidos.model_consolidado import PedidosModel
try:
    from rexus.modules.pedidos.model_consolidado import PedidosModel  # type: ignore
    __all__ = ["PedidosModel"]
except Exception:
    try:
        from rexus.modules.pedidos.model import PedidosModel  # type: ignore
        __all__ = ["PedidosModel"]
    except Exception:
        class PedidosModel:  # type: ignore
            def __init__(self, *args, **kwargs):
                raise ImportError("PedidosModel not found in rexus.modules.pedidos; please map the implementation or update legacy tests")
        __all__ = ["PedidosModel"]
