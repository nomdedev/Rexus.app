"""
Componentes modernos para formularios con feedback visual mejorado
"""

import logging
from typing import Any, Optional, Tuple, Dict, List
import re

logger = logging.getLogger(__name__)


class FormValidator:
    """
    Validador moderno para formularios con mensajes de error contextuales
    """

    # Patrones de validación comunes
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{8,20}$')
    CODE_PATTERN = re.compile(r'^[A-Z]{2,4}-\d{3,6}$')
    ALPHA_PATTERN = re.compile(r'^[a-zA-Z\sáéíóúÁÉÍÓÚñÑ]+$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ\-\.]+$')

    @staticmethod
    def required_field(value: Any, field_name: str = "campo") -> Tuple[bool, str]:
        """
        Valida que un campo no esté vacío

        Args:
            value: Valor a validar
            field_name: Nombre del campo para el mensaje

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if value is None:
            return False, f"El {field_name} es obligatorio"

        if isinstance(value, str) and not value.strip():
            return False, f"El {field_name} no puede estar vacío"

        if isinstance(value, (list, dict)) and len(value) == 0:
            return False, f"El {field_name} debe contener al menos un elemento"

        return True, ""

    @staticmethod
    def email_format(value: str) -> Tuple[bool, str]:
        """
        Valida formato de email

        Args:
            value: Email a validar

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            return True, ""  # Campo opcional

        if not FormValidator.EMAIL_PATTERN.match(value.strip()):
            return False, "Formato de email inválido"

        return True, ""

    @staticmethod
    def phone_format(value: str) -> Tuple[bool, str]:
        """
        Valida formato de teléfono

        Args:
            value: Teléfono a validar

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            return True, ""  # Campo opcional

        if not FormValidator.PHONE_PATTERN.match(value.strip()):
            return False, "Formato de teléfono inválido"

        return True, ""

    @staticmethod
    def numeric_range(value: Any, min_val: Optional[float] = None,
                     max_val: Optional[float] = None,
                     field_name: str = "valor") -> Tuple[bool, str]:
        """
        Valida rango numérico

        Args:
            value: Valor a validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            field_name: Nombre del campo

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if value is None or str(value).strip() == "":
            return False, f"El {field_name} es obligatorio"

        try:
            if isinstance(value, str):
                num_value = float(value.strip())
            else:
                num_value = float(value)

            if min_val is not None and num_value < min_val:
                return False, f"El {field_name} debe ser mayor o igual a {min_val}"

            if max_val is not None and num_value > max_val:
                return False, f"El {field_name} debe ser menor o igual a {max_val}"

            return True, ""

        except (ValueError, TypeError):
            return False, f"El {field_name} debe ser un número válido"

    @staticmethod
    def code_format(value: str) -> Tuple[bool, str]:
        """
        Valida formato de código (ej: ABC-123)

        Args:
            value: Código a validar

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            return False, "El código es obligatorio"

        if not FormValidator.CODE_PATTERN.match(value.upper().strip()):
            return False, "Formato: ABC-123456 (letras-números)"

        return True, ""

    @staticmethod
    def text_length(value: str, min_length: int = 1, max_length: int = 1000,
                   field_name: str = "texto") -> Tuple[bool, str]:
        """
        Valida longitud de texto

        Args:
            value: Texto a validar
            min_length: Longitud mínima
            max_length: Longitud máxima
            field_name: Nombre del campo

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            value = ""

        length = len(value.strip())

        if length < min_length:
            return False, f"El {field_name} debe tener al menos {min_length} caracteres"

        if length > max_length:
            return False, f"El {field_name} no puede tener más de {max_length} caracteres"

        return True, ""

    @staticmethod
    def alpha_only(value: str, field_name: str = "campo") -> Tuple[bool, str]:
        """
        Valida que solo contenga letras y espacios

        Args:
            value: Texto a validar
            field_name: Nombre del campo

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            return True, ""  # Campo opcional

        if not FormValidator.ALPHA_PATTERN.match(value.strip()):
            return False, f"El {field_name} solo puede contener letras y espacios"

        return True, ""

    @staticmethod
    def alphanumeric(value: str, field_name: str = "campo") -> Tuple[bool, str]:
        """
        Valida que contenga letras, números y algunos caracteres especiales

        Args:
            value: Texto a validar
            field_name: Nombre del campo

        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not value:
            return True, ""  # Campo opcional

        if not FormValidator.ALPHANUMERIC_PATTERN.match(value.strip()):
            return False, f"El {field_name} contiene caracteres no permitidos"

        return True, ""

    @staticmethod
    def validate_form(form_data: Dict[str, Any], validation_rules: Dict[str, Dict]) -> Dict[str, str]:
        """
        Valida un formulario completo según reglas definidas

        Args:
            form_data: Datos del formulario
            validation_rules: Reglas de validación por campo

        Returns:
            Dict[str, str]: Errores por campo (vacío si todo válido)
        """
        errors = {}

        for field_name, rules in validation_rules.items():
            value = form_data.get(field_name)

            # Aplicar cada regla de validación
            for rule_name, rule_params in rules.items():
                try:
                    if rule_name == "required":
                        is_valid, error_msg = FormValidator.required_field(value, field_name)
                    elif rule_name == "email":
                        is_valid, error_msg = FormValidator.email_format(str(value) if value else "")
                    elif rule_name == "phone":
                        is_valid, error_msg = FormValidator.phone_format(str(value) if value else "")
                    elif rule_name == "numeric_range":
                        min_val = rule_params.get("min")
                        max_val = rule_params.get("max")
                        is_valid, error_msg = FormValidator.numeric_range(value, min_val, max_val, field_name)
                    elif rule_name == "code":
                        is_valid, error_msg = FormValidator.code_format(str(value) if value else "")
                    elif rule_name == "length":
                        min_len = rule_params.get("min", 1)
                        max_len = rule_params.get("max", 1000)
                        is_valid, error_msg = FormValidator.text_length(str(value) if value else "", min_len, max_len, field_name)
                    elif rule_name == "alpha_only":
                        is_valid, error_msg = FormValidator.alpha_only(str(value) if value else "", field_name)
                    elif rule_name == "alphanumeric":
                        is_valid, error_msg = FormValidator.alphanumeric(str(value) if value else "", field_name)
                    else:
                        continue

                    if not is_valid:
                        errors[field_name] = error_msg
                        break  # Primer error encontrado es suficiente

                except Exception as e:
                    logger.error(f"Error validando campo {field_name}: {str(e)}")
                    errors[field_name] = f"Error de validación en {field_name}"

        return errors


class FormField:
    """
    Representa un campo de formulario con validación integrada
    """

    def __init__(self, name: str, field_type: str = "text", required: bool = False,
                 validators: Optional[List[str]] = None, **kwargs):
        """
        Inicializar campo de formulario

        Args:
            name: Nombre del campo
            field_type: Tipo de campo (text, email, number, etc.)
            required: Si el campo es obligatorio
            validators: Lista de validadores adicionales
            **kwargs: Parámetros adicionales
        """
        self.name = name
        self.field_type = field_type
        self.required = required
        self.validators = validators or []
        self.kwargs = kwargs
        self.value = None
        self.error = ""

    def set_value(self, value: Any) -> None:
        """Establecer valor del campo"""
        self.value = value

    def validate(self) -> bool:
        """
        Validar el campo

        Returns:
            bool: True si es válido
        """
        # Validación requerida
        if self.required:
            is_valid, error_msg = FormValidator.required_field(self.value, self.name)
            if not is_valid:
                self.error = error_msg
                return False

        # Validaciones específicas por tipo
        if self.field_type == "email":
            is_valid, error_msg = FormValidator.email_format(str(self.value) if self.value else "")
            if not is_valid:
                self.error = error_msg
                return False

        elif self.field_type == "phone":
            is_valid, error_msg = FormValidator.phone_format(str(self.value) if self.value else "")
            if not is_valid:
                self.error = error_msg
                return False

        # Validaciones adicionales
        for validator in self.validators:
            if validator == "alpha_only":
                is_valid, error_msg = FormValidator.alpha_only(str(self.value) if self.value else "", self.name)
                if not is_valid:
                    self.error = error_msg
                    return False
            elif validator == "alphanumeric":
                is_valid, error_msg = FormValidator.alphanumeric(str(self.value) if self.value else "", self.name)
                if not is_valid:
                    self.error = error_msg
                    return False

        self.error = ""
        return True

    def get_error(self) -> str:
        """Obtener mensaje de error"""
        return self.error

    def is_valid(self) -> bool:
        """Verificar si el campo es válido"""
        return self.validate()


# Funciones de conveniencia
def validate_required(value: Any, field_name: str = "campo") -> Tuple[bool, str]:
    """Función de conveniencia para validar campo requerido"""
    return FormValidator.required_field(value, field_name)


def validate_email(value: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar email"""
    return FormValidator.email_format(value)


def validate_phone(value: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar teléfono"""
    return FormValidator.phone_format(value)


def validate_numeric(value: Any, min_val: Optional[float] = None,
                    max_val: Optional[float] = None) -> Tuple[bool, str]:
    """Función de conveniencia para validar número"""
    return FormValidator.numeric_range(value, min_val, max_val)


def validate_code(value: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar código"""
    return FormValidator.code_format(value)
