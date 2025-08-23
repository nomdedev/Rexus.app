"""Módulo de Administracion"""


import logging
logger = logging.getLogger(__name__)

from .controller import AdministracionController
from .model import AdministracionModel
from .view import AdministracionView

__all__ = [, "AdministracionView", "AdministracionController"]
