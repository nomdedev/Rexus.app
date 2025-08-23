"""Módulo de Obras"""


import logging
logger = logging.getLogger(__name__)

from .controller import ObrasController
from .model import ObrasModel

# Importar submódulos especializados
try:
    pass
except ImportError:
    logger.info()
from .view import ObrasModernView as ObrasView

__all__ = [
    ,
    "ObrasView",
    "ObrasController",
]
