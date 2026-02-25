"""Módulo de Configuración"""

from .controller import ConfiguracionController
from .model import ConfiguracionModel

try:
	from .view import ConfiguracionView
except (ImportError, RuntimeError):
	ConfiguracionView = None

__all__ = ["ConfiguracionModel", "ConfiguracionView", "ConfiguracionController"]
