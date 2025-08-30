"""
Sistema de Mensajes de Error Contextualizados Mejorado - Rexus.app
Proporciona mensajes de error específicos con sugerencias de solución
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def show_validation_error(
    error_type: str = "required",
    context: Optional[Dict] = None,
    parent=None,
):
    """Muestra un error de validación contextualizado."""
    logger.error(f"Error de validación ({error_type}): {context}")


def show_business_error(
    error_type: str = "stock",
    context: Optional[Dict] = None,
    parent=None,
):
    """Muestra un error de lógica de negocio contextualizado."""
    logger.error(f"Error de negocio ({error_type}): {context}")


def show_system_error(
    error_type: str = "database",
    context: Optional[Dict] = None,
    parent=None,
):
    """Muestra un error del sistema contextualizado."""
    logger.error(f"Error del sistema ({error_type}): {context}")


def show_permission_error(
    context: Optional[Dict] = None,
    parent=None,
):
    """Muestra un error de permisos contextualizado."""
    logger.error(f"Error de permisos: acceso denegado - {context}")
