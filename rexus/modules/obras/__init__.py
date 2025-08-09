"""Módulo de Obras"""

from .controller import ObrasController
from .model import ObrasModel
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Importar modelo refactorizado principal
from .model_refactorizado import ModeloObras, ModeloObrasRefactorizado

# Importar submódulos especializados
from .submodules import ConsultasManager, ProyectosManager, RecursosManager
from .view import ObrasView

__all__ = [
    "ObrasModel",
    "ObrasView",
    "ObrasController",
    "ProyectosManager",
    "RecursosManager",
    "ConsultasManager",
    "ModeloObrasRefactorizado",
    "ModeloObras",
]
