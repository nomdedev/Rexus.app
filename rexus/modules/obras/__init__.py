"""Módulo de Obras"""

from .controller import ObrasController
from .model import ObrasModel
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Importar submódulos especializados
try:
    from .submodules import ConsultasManager, ProyectosManager, RecursosManager
except ImportError:
    print("[OBRAS] Warning: Some submodules not available")
from .view import ObrasView

__all__ = [
    "ObrasModel",
    "ObrasView", 
    "ObrasController",
]
