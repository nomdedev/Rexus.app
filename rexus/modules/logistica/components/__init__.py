"""
Componentes del módulo de Logística

Este paquete contiene los componentes modulares extraídos de view.py
para mejorar la mantenibilidad y organización del código.
"""


import logging
logger = logging.getLogger(__name__)

from .table_manager import LogisticaTableManager
from .panel_manager import LogisticaPanelManager
from .transport_manager import LogisticaTransportManager

__all__ = [
    'LogisticaTableManager',
    'LogisticaPanelManager', 
    'LogisticaTransportManager'
]