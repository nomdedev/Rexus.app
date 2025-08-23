"""Módulo de Compras"""

import logging
logger = logging.getLogger(__name__)

from .view_complete import ComprasViewComplete as ComprasView

__all__ = ['ComprasView']
