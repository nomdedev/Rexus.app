"""Módulo de Obras"""

import logging
from .controller import ObrasController
from .view import ObrasModernView as ObrasView

logger = logging.getLogger(__name__)

# Configuración del módulo
try:
    # Importar submódulos especializados si están disponibles
    pass
except ImportError:
    logger.info("Submódulos especializados no disponibles")

__all__ = [
    "ObrasView",
    "ObrasController",
]
