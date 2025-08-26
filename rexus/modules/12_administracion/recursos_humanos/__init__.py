"""
Submódulo de Recursos Humanos
"""


import logging
logger = logging.getLogger(__name__)

from .model import RecursosHumanosModel
from .controller import RecursosHumanosController

__all__ = ['RecursosHumanosModel', 'RecursosHumanosController']
