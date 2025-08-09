"""Módulo de Producción"""

from .controller import ProduccionController
from .model import ProduccionModel
from .view import ProduccionView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["ProduccionModel", "ProduccionView", "ProduccionController"]
