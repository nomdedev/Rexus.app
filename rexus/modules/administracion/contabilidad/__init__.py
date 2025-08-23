"""
Submódulo de Contabilidad
"""


import logging
logger = logging.getLogger(__name__)

from .model import ContabilidadModel
from .controller import ContabilidadController

__all__ = ['ContabilidadModel', 'ContabilidadController']
