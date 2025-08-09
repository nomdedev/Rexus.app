"""Módulo de Configuración"""

from .controller import ConfiguracionController
from .model import ConfiguracionModel
from .view import ConfiguracionView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["ConfiguracionModel", "ConfiguracionView", "ConfiguracionController"]
