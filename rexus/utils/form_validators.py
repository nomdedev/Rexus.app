"""
Sistema de validación de formularios para Rexus.app

Proporciona validadores comunes para campos de formularios
con feedback visual integrado.
"""


import logging
logger = logging.getLogger(__name__)

import re
            def validacion_direccion(campo, direccion: str) -> Tuple[bool, str]:
    """Validación específica para direcciones."""
    # Manejar None y convertir a string si es necesario
    if direccion is None:
        direccion = ""
    elif not isinstance(direccion, str):
        direccion = str(direccion)
        
    if not direccion.strip():
        FormValidator._aplicar_estilo_error(campo)
        return False, "La dirección es obligatoria"

    if len(direccion.strip()) < 10:
        FormValidator._aplicar_estilo_error(campo)
        return False, "La dirección debe ser más específica (mínimo 10 caracteres)"

    FormValidator._aplicar_estilo_success(campo)
    return True, ""


def validacion_codigo_producto(campo, codigo: str) -> Tuple[bool, str]:
    """Validación para códigos de producto."""
    # Manejar None y convertir a string si es necesario
    if codigo is None:
        codigo = ""
    elif not isinstance(codigo, str):
        codigo = str(codigo)
    
    # Validar que no esté vacío después de limpiar espacios
    codigo_limpio = codigo.strip()
    if not codigo_limpio:
        FormValidator._aplicar_estilo_error(campo)
        return False, "El código es obligatorio"

    # Formato esperado: ABC-1234 o similar
    if not re.match(r'^[A-Z]{2,4}-\d{3,6}$', codigo_limpio.upper()):
        FormValidator._aplicar_estilo_error(campo)
        return False, "Formato de código inválido (ej: VID-1234, HER-5678)"

    FormValidator._aplicar_estilo_success(campo)
    return True, ""
