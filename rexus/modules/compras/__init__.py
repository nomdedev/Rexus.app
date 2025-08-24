"""Módulo de Compras"""

from .view_complete import ComprasViewComplete as ComprasView

import logging
logger = logging.getLogger(__name__)

__all__ = ['ComprasView']
