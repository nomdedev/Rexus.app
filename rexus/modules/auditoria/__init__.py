"""
Módulo de Auditoría

Gestiona el registro y seguimiento de todas las acciones críticas
realizadas en el sistema de inventario.
"""

from .controller import AuditoriaController
from .model import AuditoriaModel
from .view import AuditoriaView

__all__ = ["AuditoriaModel", "AuditoriaView", "AuditoriaController"]
