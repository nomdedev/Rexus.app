"""
Sistema de Mensajes de Error Contextualizados Mejorado - Rexus.app
Proporciona mensajes de error específicos con sugerencias de solución
"""

import logging
                code = error_codes.get(error_type, "E4001")
    contextual_error_manager.show_error(code, context, parent)


def show_business_error(
    error_type: str = "stock",
    context: Optional[Dict] = None,
    parent: Optional[QWidget] = None,
):
    """Muestra un error de lógica de negocio contextualizado."""
    error_codes = {"stock": "E7001", "price": "E7002"}
    code = error_codes.get(error_type, "E7001")
    contextual_error_manager.show_error(code, context, parent)
