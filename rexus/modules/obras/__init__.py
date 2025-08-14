"""Módulo de Obras"""

from .controller import ObrasController
from .model import ObrasModel

# Importar submódulos especializados
try:
    pass
except ImportError:
    print("[OBRAS] Warning: Some submodules not available")
from .view import ObrasModernView as ObrasView

__all__ = [
    "ObrasModel",
    "ObrasView",
    "ObrasController",
]
