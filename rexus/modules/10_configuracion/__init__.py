"""Módulo de Configuración"""


import logging
logger = logging.getLogger(__name__)

from .controller import ConfiguracionController
from .model import ConfiguracionModel
from .view import ConfiguracionView

__all__ = ["ConfiguracionModel", "ConfiguracionView", "ConfiguracionController"]
