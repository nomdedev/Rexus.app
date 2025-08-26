"""Módulo de Herrajes"""


import logging
logger = logging.getLogger(__name__)

from .controller import HerrajesController
from .model import HerrajesModel
from .view import HerrajesView

__all__ = ["HerrajesModel", "HerrajesView", "HerrajesController"]
