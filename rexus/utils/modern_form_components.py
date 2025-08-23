"""
Componentes modernos para formularios con feedback visual mejorado
"""


import logging
logger = logging.getLogger(__name__)

                    """Valida que un campo no esté vacío"""
        if not value or (isinstance(value, str) and not value.strip()):
            return False, "Este campo es obligatorio"
        return True, ""

    @staticmethod
    def email_format(value) -> tuple[bool, str]:
        """Valida formato de email"""
        if not value:
            return True, ""  # Campo opcional

        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Formato de email inválido"
        return True, ""

    @staticmethod
    def numeric_range(value, min_val=None, max_val=None) -> tuple[bool, str]:
        """Valida rango numérico"""
        try:
            num_value = float(value) if isinstance(value, str) else value

            if min_val is not None and num_value < min_val:
                return False, f"El valor debe ser mayor o igual a {min_val}"

            if max_val is not None and num_value > max_val:
                return False, f"El valor debe ser menor o igual a {max_val}"

            return True, ""
        except (ValueError, TypeError):
            return False, "Debe ser un número válido"

    @staticmethod
    def code_format(value) -> tuple[bool, str]:
        """Valida formato de código (ej: ABC-123)"""
        if not value:
            return False, "Código es obligatorio"

        import re
        pattern = r'^[A-Z]{2,4}-\d{3,6}$'
        if not re.match(pattern, value.upper()):
            return False, "Formato: ABC-123456 (letras-números)"
        return True, ""
