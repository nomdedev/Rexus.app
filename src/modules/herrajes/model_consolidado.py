# Compatibility shim for legacy import path:
# from src.modules.herrajes.model_consolidado import HerrajesModel
try:
    from rexus.modules.herrajes.model_consolidado import HerrajesModel  # type: ignore
    __all__ = ["HerrajesModel"]
except Exception:
    try:
        from rexus.modules.herrajes.model import HerrajesModel  # type: ignore
        __all__ = ["HerrajesModel"]
    except Exception:
        class HerrajesModel:  # type: ignore
            def __init__(self, *args, **kwargs):
                raise ImportError("HerrajesModel not found in rexus.modules.herrajes; please map the implementation or update legacy tests")
        __all__ = ["HerrajesModel"]
