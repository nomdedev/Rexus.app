"""Módulo de Logística"""


import logging
logger = logging.getLogger(__name__)

from .controller import LogisticaController
from .model import LogisticaModel
from .view import LogisticaView

__all__ = ["LogisticaModel", "LogisticaView", "LogisticaController"]
