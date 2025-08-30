"""
Utilidades de validación extendidas - Rexus.app v2.0.0

Proporciona validadores avanzados y reglas de negocio comunes.
"""

import logging
import re
from typing import Any, Optional, Union, Callable


logger = logging.getLogger(__name__)


class AdvancedValidator:
    """
    Validador avanzado con reglas de negocio específicas para Rexus.app
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email básico

        Args:
            email: Email a validar

        Returns:
            True si es válido, False en caso contrario
        """
        if not email or not isinstance(email, str):
            return False

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email.strip()))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida formato de teléfono (admite varios formatos)

        Args:
            phone: Número de teléfono a validar

        Returns:
            True si es válido, False en caso contrario
        """
        if not phone or not isinstance(phone, str):
            return False

        # Eliminar espacios, guiones y paréntesis
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone.strip())

        # Patrones para diferentes formatos de teléfono
        patterns = [
            r'^\+?54\d{10}$',  # Argentina con código de país
            r'^\d{10}$',       # 10 dígitos
            r'^\d{8}$',        # 8 dígitos
        ]

        return any(re.match(pattern, clean_phone) for pattern in patterns)

    @staticmethod
    def validate_positive_number(value: Any, field_name: str = "Valor") -> Union[float, str]:
        """
        Valida que un valor sea un número positivo

        Args:
            value: Valor a validar
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor numérico si es válido, mensaje de error si no lo es
        """
        try:
            if value is None or value == "":
                return f"{field_name} es requerido"

            numeric_value = float(value)

            if numeric_value < 0:
                return f"{field_name} debe ser un número positivo"

            return numeric_value

        except (ValueError, TypeError):
            return f"{field_name} debe ser un número válido"

    @staticmethod
    def validate_number_range(value: Any, min_val: Optional[float],
                            max_val: Optional[float], field_name: str = "Valor") -> Union[float, str]:
        """
        Valida que un número esté dentro de un rango específico

        Args:
            value: Valor a validar
            min_val: Valor mínimo (None para sin límite inferior)
            max_val: Valor máximo (None para sin límite superior)
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor numérico si es válido, mensaje de error si no lo es
        """
        try:
            if value is None or value == "":
                return f"{field_name} es requerido"

            numeric_value = float(value)

            if min_val is not None and numeric_value < min_val:
                return f"{field_name} debe ser mayor o igual a {min_val}"

            if max_val is not None and numeric_value > max_val:
                return f"{field_name} debe ser menor o igual a {max_val}"

            return numeric_value

        except (ValueError, TypeError):
            return f"{field_name} debe ser un número válido"

    @staticmethod
    def validate_cuit(cuit: str) -> bool:
        """
        Valida formato de CUIT/CUIL argentino

        Args:
            cuit: CUIT/CUIL a validar

        Returns:
            True si es válido, False en caso contrario
        """
        if not cuit or not isinstance(cuit, str):
            return False

        # Eliminar guiones y espacios
        clean_cuit = re.sub(r'[\-\s]', '', cuit.strip())

        # Debe tener 11 dígitos
        if not re.match(r'^\d{11}$', clean_cuit):
            return False

        # Algoritmo de validación de CUIT
        try:
            base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            total = 0

            for i in range(10):
                total += int(clean_cuit[i]) * base[i]

            verificador = (11 - (total % 11)) % 11
            return verificador == int(clean_cuit[10])

        except (ValueError, IndexError):
            return False

    @staticmethod
    def validate_text_length(text: str, min_length: int = 0,
                           max_length: int = 255, field_name: str = "Texto") -> Union[str, str]:
        """
        Valida longitud de texto

        Args:
            text: Texto a validar
            min_length: Longitud mínima
            max_length: Longitud máxima
            field_name: Nombre del campo

        Returns:
            Texto si es válido, mensaje de error si no lo es
        """
        if not text or not isinstance(text, str):
            if min_length > 0:
                return f"{field_name} es requerido"
            return ""

        text_length = len(text.strip())

        if text_length < min_length:
            return f"{field_name} debe tener al menos {min_length} caracteres"

        if text_length > max_length:
            return f"{field_name} no puede tener más de {max_length} caracteres"

        return text.strip()

    @staticmethod
    def validate_date_format(date_str: str, field_name: str = "Fecha") -> Union[str, str]:
        """
        Valida formato de fecha (DD/MM/YYYY o YYYY-MM-DD)

        Args:
            date_str: Fecha a validar
            field_name: Nombre del campo

        Returns:
            Fecha si es válida, mensaje de error si no lo es
        """
        if not date_str or not isinstance(date_str, str):
            return f"{field_name} es requerida"

        # Patrones de fecha
        patterns = [
            r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        ]

        if not any(re.match(pattern, date_str.strip()) for pattern in patterns):
            return f"{field_name} debe tener formato DD/MM/YYYY o YYYY-MM-DD"

        return date_str.strip()


class ValidationManager:
    """
    Gestor de validaciones que permite agregar validadores personalizados
    """

    def __init__(self):
        """Inicializar el gestor de validaciones"""
        self._validators = {}

    def add_field_validator(self, field_name: str, validator: Callable):
        """
        Agrega un validador para un campo específico

        Args:
            field_name: Nombre del campo
            validator: Función validadora
        """
        if field_name not in self._validators:
            self._validators[field_name] = []

        self._validators[field_name].append(validator)

    def validate_field(self, field_name: str, value: Any) -> list:
        """
        Valida un campo usando todos sus validadores

        Args:
            field_name: Nombre del campo
            value: Valor a validar

        Returns:
            Lista de errores (vacía si es válido)
        """
        errors = []

        if field_name in self._validators:
            for validator in self._validators[field_name]:
                try:
                    result = validator(value)
                    if isinstance(result, str):  # Es un mensaje de error
                        errors.append(result)
                except Exception as e:
                    errors.append(f"Error de validación: {str(e)}")

        return errors

    def validate_data(self, data: dict) -> dict:
        """
        Valida un diccionario completo de datos

        Args:
            data: Diccionario con los datos a validar

        Returns:
            Diccionario con errores por campo
        """
        errors = {}

        for field_name, value in data.items():
            field_errors = self.validate_field(field_name, value)
            if field_errors:
                errors[field_name] = field_errors

        return errors


def create_inventory_validation_manager() -> ValidationManager:
    """
    Crea un gestor de validaciones específico para inventario

    Returns:
        ValidationManager configurado para inventario
    """
    manager = ValidationManager()

    # Validaciones para campos de inventario
    manager.add_field_validator("importe", lambda v: AdvancedValidator.validate_positive_number(v, "Importe"))
    manager.add_field_validator("stock_actual", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock actual"))
    manager.add_field_validator("stock_minimo", lambda v: AdvancedValidator.validate_number_range(v, 0, None, "Stock mínimo"))

    return manager
