"""Módulo de Obras"""

from .controller import ObrasController
from .model import ObrasModel

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
