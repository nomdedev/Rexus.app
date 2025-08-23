"""Módulo de Producción"""


import logging
logger = logging.getLogger(__name__)

from .controller import ProduccionController
from .model import ProduccionModel
from .view import ProduccionView

__all__ = [, "ProduccionView", "ProduccionController"]
