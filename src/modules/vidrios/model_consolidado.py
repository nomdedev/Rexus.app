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
            def __init__(self, *args, **kwargs):
                raise ImportError("VidriosModel not found in rexus.modules.vidrios; please map the implementation or update legacy tests")
        __all__ = ["VidriosModel"]
