# Compatibility shim for legacy import path:
# from src.modules.obras.model_consolidado import ObrasModel
try:
    from rexus.modules.obras.model_consolidado import ObrasModel  # type: ignore
    __all__ = ["ObrasModel"]
except Exception:
    try:
        from rexus.modules.obras.model import ObrasModel  # type: ignore
        __all__ = ["ObrasModel"]
    except Exception:
        class ObrasModel:  # type: ignore
            def __init__(self, *args, **kwargs):
                raise ImportError("ObrasModel not found in rexus.modules.obras; please map the implementation or update legacy tests")
        __all__ = ["ObrasModel"]
