"""
Submódulo de Recursos Humanos
"""

from .model import RecursosHumanosModel
from .controller import RecursosHumanosController
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ['RecursosHumanosModel', 'RecursosHumanosController']