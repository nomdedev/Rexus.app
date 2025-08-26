"""Módulo de Administracion"""


import logging
logger = logging.getLogger(__name__)

from .controller import AdministracionController
# Comentado temporalmente hasta corregir sintaxis
# from .model import AdministracionModel
# from .view import AdministracionView

__all__ = ["AdministracionController"]
# Comentado temporalmente: "AdministracionModel", "AdministracionView"
