"""
Módulo de Auditoría

Gestiona el registro y seguimiento de todas las acciones críticas
realizadas en el sistema de inventario.
"""

from .controller import AuditoriaController
from .model import AuditoriaModel
from .view import AuditoriaView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["AuditoriaModel", "AuditoriaView", "AuditoriaController"]
