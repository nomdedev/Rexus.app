#!/usr/bin/env python3
"""
Sistema de Validación de Entrada Completa - Rexus.app

Proporciona validación robusta para todos los tipos de entrada del usuario
para prevenir inyecciones SQL, XSS, y otros ataques de seguridad.

Fecha: 15/08/2025
Componente: Seguridad - Validación de Entrada
"""

import re
import html
import json
import logging
from typing import Union, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validador de entrada robusto para Rexus.app
    """

    # Patrones de validación
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{8,20}$')
    ALPHA_PATTERN = re.compile(r'^[a-zA-Z\sáéíóúÁÉÍÓÚñÑ]+$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ\-\.]+$')
    NUMERIC_PATTERN = re.compile(r'^\d+$')
    DECIMAL_PATTERN = re.compile(r'^\d+(\.\d{1,2})?$')

    # Listas de palabras peligrosas
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'EXEC', 'EXECUTE', 'UNION', 'JOIN', 'WHERE', 'FROM', 'INTO',
        'VALUES', 'SET', 'DECLARE', 'BEGIN', 'END', 'COMMIT', 'ROLLBACK'
    ]

    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>'
    ]

    def __init__(self):
        """Inicializar validador"""
        self.logger = logging.getLogger(__name__)

    def sanitize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitiza texto eliminando caracteres peligrosos y limitando longitud.

        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida

        Returns:
            str: Texto sanitizado
        """
        if not text:
            return ""

        try:
            # Convertir a string si no lo es
            if not isinstance(text, str):
                text = str(text)

            # Escapar HTML
            text = html.escape(text)

            # Remover caracteres de control
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

            # Limitar longitud
            if len(text) > max_length:
                text = text[:max_length]

            return text.strip()

        except Exception as e:
            self.logger.error(f"Error al sanitizar texto: {str(e)}")
            return ""

    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        Valida una dirección de email.

        Args:
            email: Email a validar

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if not email:
            return False, "El email es requerido"

        try:
            email = email.strip().lower()

            if not self.EMAIL_PATTERN.match(email):
                return False, "Formato de email inválido"

            # Verificar longitud
            if len(email) > 254:
                return False, "Email demasiado largo"

            # Verificar que no contenga palabras peligrosas
            if self._contains_dangerous_content(email):
                return False, "Email contiene contenido peligroso"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error al validar email: {str(e)}")
            return False, "Error al validar email"

    def validate_phone(self, phone: str) -> tuple[bool, str]:
        """
        Valida un número de teléfono.

        Args:
            phone: Teléfono a validar

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if not phone:
            return False, "El teléfono es requerido"

        try:
            phone = phone.strip()

            if not self.PHONE_PATTERN.match(phone):
                return False, "Formato de teléfono inválido"

            # Verificar que no contenga palabras peligrosas
            if self._contains_dangerous_content(phone):
                return False, "Teléfono contiene contenido peligroso"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error al validar teléfono: {str(e)}")
            return False, "Error al validar teléfono"

    def validate_text(self, text: str, field_name: str = "campo",
                     min_length: int = 1, max_length: int = 1000,
                     allow_empty: bool = False) -> tuple[bool, str]:
        """
        Valida texto genérico.

        Args:
            text: Texto a validar
            field_name: Nombre del campo para mensajes
            min_length: Longitud mínima
            max_length: Longitud máxima
            allow_empty: Permitir campo vacío

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        try:
            if not allow_empty and (text is None or str(text).strip() == ""):
                return False, f"El {field_name} es requerido"

            if text is None:
                text = ""

            text_str = str(text).strip()

            if not allow_empty and len(text_str) < min_length:
                return False, f"El {field_name} debe tener al menos {min_length} caracteres"

            if len(text_str) > max_length:
                return False, f"El {field_name} no puede tener más de {max_length} caracteres"

            # Verificar contenido peligroso
            if self._contains_dangerous_content(text_str):
                return False, f"El {field_name} contiene contenido peligroso"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error al validar texto: {str(e)}")
            return False, f"Error al validar {field_name}"

    def validate_number(self, value: Union[str, int, float, Decimal],
                       field_name: str = "número", min_value: Optional[float] = None,
                       max_value: Optional[float] = None, allow_zero: bool = True) -> tuple[bool, str]:
        """
        Valida un número.

        Args:
            value: Valor a validar
            field_name: Nombre del campo
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            allow_zero: Permitir valor cero

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        try:
            if value is None or str(value).strip() == "":
                return False, f"El {field_name} es requerido"

            # Convertir a float
            try:
                num_value = float(value)
            except (ValueError, TypeError):
                return False, f"El {field_name} debe ser un número válido"

            if not allow_zero and num_value == 0:
                return False, f"El {field_name} no puede ser cero"

            if min_value is not None and num_value < min_value:
                return False, f"El {field_name} debe ser mayor o igual a {min_value}"

            if max_value is not None and num_value > max_value:
                return False, f"El {field_name} debe ser menor o igual a {max_value}"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error al validar número: {str(e)}")
            return False, f"Error al validar {field_name}"

    def validate_date(self, date_str: str, field_name: str = "fecha",
                     date_format: str = "%Y-%m-%d") -> tuple[bool, str]:
        """
        Valida una fecha.

        Args:
            date_str: Fecha como string
            field_name: Nombre del campo
            date_format: Formato esperado

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        try:
            if not date_str:
                return False, f"La {field_name} es requerida"

            datetime.strptime(date_str, date_format)
            return True, ""

        except ValueError:
            return False, f"Formato de {field_name} inválido. Use {date_format}"
        except Exception as e:
            self.logger.error(f"Error al validar fecha: {str(e)}")
            return False, f"Error al validar {field_name}"

    def _contains_dangerous_content(self, text: str) -> bool:
        """
        Verifica si el texto contiene contenido peligroso.

        Args:
            text: Texto a verificar

        Returns:
            bool: True si contiene contenido peligroso
        """
        if not text:
            return False

        text_upper = text.upper()

        # Verificar palabras clave SQL
        for keyword in self.SQL_KEYWORDS:
            if keyword in text_upper:
                self.logger.warning(f"Contenido peligroso detectado (SQL): {keyword}")
                return True

        # Verificar patrones XSS
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Contenido peligroso detectado (XSS): {pattern}")
                return True

        # Verificar caracteres de control peligrosos
        if re.search(r'[\x00-\x1f\x7f-\x9f]', text):
            self.logger.warning("Caracteres de control peligrosos detectados")
            return True

        return False

    def validate_json(self, json_str: str) -> tuple[bool, str]:
        """
        Valida que un string sea JSON válido.

        Args:
            json_str: String JSON a validar

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        try:
            if not json_str:
                return False, "JSON es requerido"

            json.loads(json_str)
            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error al validar JSON: {str(e)}")
            return False, "Error al validar JSON"

    def create_safe_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea parámetros seguros para consultas SQL.

        Args:
            params: Parámetros a sanitizar

        Returns:
            dict: Parámetros sanitizados
        """
        safe_params = {}

        try:
            for key, value in params.items():
                if isinstance(value, str):
                    # Sanitizar strings
                    safe_params[key] = self.sanitize_text(value, max_length=500)
                elif isinstance(value, (int, float, Decimal)):
                    # Los números son seguros
                    safe_params[key] = value
                elif isinstance(value, (datetime, date)):
                    # Las fechas son seguras
                    safe_params[key] = value
                elif value is None:
                    # None es seguro
                    safe_params[key] = value
                else:
                    # Convertir otros tipos a string y sanitizar
                    safe_params[key] = self.sanitize_text(str(value), max_length=500)

        except Exception as e:
            self.logger.error(f"Error al crear parámetros seguros: {str(e)}")
            return {}

        return safe_params


# Instancia global para uso común
default_validator = InputValidator()


# Funciones de conveniencia
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitiza entrada de texto usando el validador por defecto."""
    return default_validator.sanitize_text(text, max_length)


def validate_email_format(email: str) -> tuple[bool, str]:
    """Valida formato de email usando el validador por defecto."""
    return default_validator.validate_email(email)


def validate_required_text(text: str, field_name: str, max_length: int = 1000) -> tuple[bool, str]:
    """Valida texto requerido usando el validador por defecto."""
    return default_validator.validate_text(text, field_name, max_length=max_length)


def validate_number_input(value: Union[str, int, float], field_name: str,
                         min_value: Optional[float] = None,
                         max_value: Optional[float] = None) -> tuple[bool, str]:
    """Valida entrada numérica usando el validador por defecto."""
    return default_validator.validate_number(value, field_name, min_value, max_value)


def create_safe_sql_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Crea parámetros SQL seguros usando el validador por defecto."""
    return default_validator.create_safe_query_params(params)


def validate_form_data(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, Dict[str, str], Dict[str, Any]]:
    """
    Valida datos de formulario usando un esquema de validación.

    Args:
        data: Datos a validar
        schema: Esquema de validación

    Returns:
        tuple: (es_valido, errores, datos_sanitizados)
    """
    errors = {}
    sanitized_data = {}

    try:
        for field, rules in schema.items():
            value = data.get(field)

            # Validar campo requerido
            if rules.get('required', False) and (value is None or str(value).strip() == ""):
                errors[field] = f"El campo {field} es requerido"
                continue

            # Sanitizar y validar según tipo
            field_type = rules.get('type', 'str')

            if field_type == 'email':
                is_valid, error_msg = default_validator.validate_email(str(value) if value else "")
                if not is_valid:
                    errors[field] = error_msg
                else:
                    sanitized_data[field] = default_validator.sanitize_text(str(value))

            elif field_type == 'text':
                max_length = rules.get('max_length', 1000)
                is_valid, error_msg = default_validator.validate_text(
                    str(value) if value else "",
                    field,
                    max_length=max_length
                )
                if not is_valid:
                    errors[field] = error_msg
                else:
                    sanitized_data[field] = default_validator.sanitize_text(str(value), max_length)

            elif field_type == 'number':
                if value is None:
                    errors[field] = f"El campo {field} es requerido"
                    continue
                min_val = rules.get('min_value')
                max_val = rules.get('max_value')
                is_valid, error_msg = default_validator.validate_number(
                    value, field, min_val, max_val
                )
                if not is_valid:
                    errors[field] = error_msg
                else:
                    sanitized_data[field] = value

            elif field_type == 'date':
                date_format = rules.get('format', '%Y-%m-%d')
                is_valid, error_msg = default_validator.validate_date(
                    str(value) if value else "", field, date_format
                )
                if not is_valid:
                    errors[field] = error_msg
                else:
                    sanitized_data[field] = str(value)

            else:
                # Para otros tipos, sanitizar como texto
                sanitized_data[field] = default_validator.sanitize_text(str(value) if value else "")

        return len(errors) == 0, errors, sanitized_data

    except Exception as e:
        logger.error(f"Error al validar datos de formulario: {str(e)}")
        return False, {"general": "Error al validar datos"}, {}


def input_validation_decorator(validation_schema: Dict[str, Any]):
    """
    Decorador para validar entrada de funciones.

    Args:
        validation_schema: Esquema de validación para los parámetros

    Returns:
        Decorador configurado
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Obtener argumentos del método (excluyendo 'self')
                func_args = func.__code__.co_varnames[1:func.__code__.co_argcount]
                arg_values = dict(zip(func_args, args[1:]))  # Excluir 'self'
                arg_values.update(kwargs)

                # Validar argumentos
                is_valid, errors, sanitized_data = validate_form_data(arg_values, validation_schema)

                if not is_valid:
                    error_msg = "; ".join(errors.values())
                    raise ValueError(f"Datos de entrada no válidos: {error_msg}")

                # Llamar función original con datos sanitizados
                new_kwargs = {k: v for k, v in sanitized_data.items() if k not in func_args[:len(args)-1]}
                new_args = args[:1] + tuple(sanitized_data.get(arg, args[i+1]) for i, arg in enumerate(func_args[:len(args)-1]))

                return func(*new_args, **new_kwargs)
            except Exception as e:
                logger.error(f"Error en decorador de validación: {str(e)}")
                raise
        return wrapper
    return decorator