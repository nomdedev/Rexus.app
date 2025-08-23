"""
MIT License

Copyright (c) 2024 Rexus.app

Data Sanitizer - Utilidades para sanitización de datos

Proporciona funciones para limpiar y validar datos de entrada.
"""


import logging
logger = logging.getLogger(__name__)

import re
import html
from typing import Any, Optional, Union


class DataSanitizer:
    @staticmethod
    def sanitize_string(value, max_length=None):
        s = DataSanitizer.sanitize_text(value)
        if max_length is not None:
            return s[:max_length]
        return s

    @staticmethod
    def sanitize_dict(data_dict):
        return DataSanitizer.clean_dict(data_dict)
    """Clase para sanitización de datos de entrada."""

    @staticmethod
    def sanitize_text(text: Union[str, Any]) -> str:
        """
        Sanitiza texto eliminando caracteres peligrosos.

        Args:
            text: Texto a sanitizar

        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Escapar HTML
        text = html.escape(text)

        # Limitar longitud
        if len(text) > 1000:
            text = text[:1000] + "..."

        return text.strip()

    @staticmethod
    def sanitize_sql_input(text: Union[str, Any]) -> str:
        """
        Sanitiza entrada para prevenir SQL injection.

        Args:
            text: Texto a sanitizar

        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Remover caracteres peligrosos para SQL
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]

        for char in dangerous_chars:
            text = text.replace(char, "")

        return text.strip()

    @staticmethod
    def sanitize_filename(filename: Union[str, Any]) -> str:
        """
        Sanitiza nombre de archivo.

        Args:
            filename: Nombre de archivo a sanitizar

        Returns:
            str: Nombre de archivo sanitizado
        """
        if not isinstance(filename, str):
            filename = str(filename) if filename is not None else ""

        # Caracteres peligrosos en nombres de archivo
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Remover puntos al inicio y final
        filename = filename.strip('.')

        # Limitar longitud
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename or "unnamed"

    @staticmethod
    def sanitize_email(email: Union[str, Any]) -> str:
        """
        Sanitiza dirección de email.

        Args:
            email: Email a sanitizar

        Returns:
            str: Email sanitizado
        """
        if not isinstance(email, str):
            email = str(email) if email is not None else ""

        # Patrón básico de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        email = email.strip().lower()

        if not re.match(email_pattern, email):
            return ""

        return email

    @staticmethod
    def sanitize_phone(phone: Union[str, Any]) -> str:
        """
        Sanitiza número de teléfono.

        Args:
            phone: Teléfono a sanitizar

        Returns:
            str: Teléfono sanitizado
        """
        if not isinstance(phone, str):
            phone = str(phone) if phone is not None else ""

        # Mantener solo números, espacios, guiones y paréntesis
        phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)

        return phone.strip()

    @staticmethod
    def sanitize_number(value: Any) -> Optional[float]:
        """
        Sanitiza valor numérico.

        Args:
            value: Valor a sanitizar

        Returns:
            Optional[float]: Valor numérico sanitizado o None
        """
        if value is None:
            return None

        try:
            if isinstance(value, (int, float)):
                return float(value)

            if isinstance(value, str):
                # Remover caracteres no numéricos excepto punto y coma
                value = re.sub(r'[^\d.,\-]', '', value)

                # Reemplazar coma por punto
                value = value.replace(',', '.')

                if value:
                    return float(value)

            return None

        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_boolean(value: Any) -> bool:
        """
        Sanitiza valor booleano.

        Args:
            value: Valor a sanitizar

        Returns:
            bool: Valor booleano sanitizado
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.lower().strip()
            return value in ['true', '1', 'yes', 'on', 'sí', 'verdadero']

        if isinstance(value, (int, float)):
            return bool(value)

        return False

    @staticmethod
    def sanitize_html(html_text: Union[str, Any]) -> str:
        """
        Sanitiza HTML removiendo tags peligrosos.

        Args:
            html_text: HTML a sanitizar

        Returns:
            str: HTML sanitizado
        """
        if not isinstance(html_text, str):
            html_text = str(html_text) if html_text is not None else ""

        # Tags peligrosos
        dangerous_tags = [
            'script', 'iframe', 'object', 'embed', 'form',
            'input', 'button', 'meta', 'link', 'style'
        ]

        for tag in dangerous_tags:
            # Remover tags de apertura y cierre
            html_text = re.sub(f'<{tag}[^>]*>',
'',
                html_text,
                flags=re.IGNORECASE)
            html_text = re.sub(f'</{tag}>',
'',
                html_text,
                flags=re.IGNORECASE)

        # Remover atributos peligrosos
        dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'javascript:']

        for attr in dangerous_attrs:
            html_text = re.sub(f'{attr}[^>]*',
'',
                html_text,
                flags=re.IGNORECASE)

        return html_text.strip()

    @staticmethod
    def validate_input_length(text: Union[str, Any], max_length: int = 1000) -> bool:
        """
        Valida la longitud de entrada.

        Args:
            text: Texto a validar
            max_length: Longitud máxima permitida

        Returns:
            bool: True si la longitud es válida
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        return len(text) <= max_length

    @staticmethod
    def clean_dict(data: dict) -> dict:
        """
        Limpia un diccionario sanitizando todos sus valores de texto.

        Args:
            data: Diccionario a limpiar

        Returns:
            dict: Diccionario con valores sanitizados
        """
        cleaned = {}

        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = DataSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                cleaned[key] = DataSanitizer.clean_dict(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    DataSanitizer.sanitize_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                cleaned[key] = value

        return cleaned
