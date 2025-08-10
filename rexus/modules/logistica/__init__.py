"""Módulo de Logística"""

from .controller import LogisticaController
from .model import LogisticaModel
from .view import LogisticaView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ["LogisticaModel", "LogisticaView", "LogisticaController"]
