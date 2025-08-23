"""
MIT License

Copyright (c) 2024 Rexus.app

XSS Protection - Sistema completo de protección contra Cross-Site Scripting

Proporciona decoradores y utilidades para proteger formularios y entrada de usuario.
"""


import logging
logger = logging.getLogger(__name__)

import html
import re
from typing import Any, Callable, Dict, Union
from functools import wraps
from PyQt6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
from PyQt6.QtCore import QObject, pyqtSignal

from rexus.utils.data_sanitizer import DataSanitizer


class XSSProtection:
    """Sistema de protección contra XSS."""

    # Patrones peligrosos comunes
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<form[^>]*>.*?</form>',
        r'<input[^>]*>',
        r'<button[^>]*>.*?</button>',
        r'javascript\s*:',
        r'vbscript\s*:',
        r'on\w+\s*=',
        r'data\s*:',
        r'eval\s*\(',
        r'expression\s*\(',
        r'alert\s*\(',
        r'confirm\s*\(',
        r'prompt\s*\(',
        r'document\.',
        r'window\.',
        r'location\.',
        r'history\.',
        r'navigator\.',
        r'cookie',
        r'innerHTML',
        r'outerHTML'
    ]

    # Atributos HTML peligrosos
    DANGEROUS_ATTRIBUTES = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onkeypress', 'onkeydown', 'onkeyup',
        'onload', 'onunload', 'onchange', 'onsubmit', 'onreset', 'onselect',
        'onblur', 'onfocus', 'onerror', 'onabort', 'style'
    ]

    @staticmethod
    def sanitize_text(text: Union[str, Any]) -> str:
        """
        Sanitiza texto eliminando contenido malicioso.

        Args:
            text: Texto a sanitizar

        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        if not text:
            return ""

        # Usar DataSanitizer como base
        sanitized = DataSanitizer.sanitize_text(text)

        # Aplicar patrones específicos de XSS con más agresividad
        for pattern in XSSProtection.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern,
'',
                sanitized,
                flags=re.IGNORECASE | re.DOTALL)

        # Segunda pasada para eliminar remanentes
        sanitized = re.sub(r'<script[^>]*>.*?</script>',
'',
            sanitized,
            flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript\s*:',
'',
            sanitized,
            flags=re.IGNORECASE)
        sanitized = re.sub(r'eval\s*\(', '', sanitized, flags=re.IGNORECASE)

        # Remover atributos peligrosos
        for attr in XSSProtection.DANGEROUS_ATTRIBUTES:
            sanitized = re.sub(f'{attr}\\s*=\\s*["\'][^"\']*["\']',
'',
                sanitized,
                flags=re.IGNORECASE)
            sanitized = re.sub(f'{attr}\\s*=\\s*[^\\s>]*',
'',
                sanitized,
                flags=re.IGNORECASE)

        return sanitized.strip()

    @staticmethod
    def validate_safe_content(content: str) -> bool:
        """
        Valida que el contenido sea seguro.

        Args:
            content: Contenido a validar

        Returns:
            bool: True si el contenido es seguro
        """
        if not content:
            return True

        # Verificar patrones peligrosos
        for pattern in XSSProtection.DANGEROUS_PATTERNS:
            if re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL):
                return False

        # Verificar atributos peligrosos
        for attr in XSSProtection.DANGEROUS_ATTRIBUTES:
            if re.search(f'{attr}\\s*=', content, flags=re.IGNORECASE):
                return False

        return True

    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """
        Sanitiza contenido HTML manteniendo tags seguros.

        Args:
            html_content: HTML a sanitizar

        Returns:
            str: HTML sanitizado
        """
        if not html_content:
            return ""

        # Tags permitidos (whitelist)
        allowed_tags = {
            'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'div', 'span', 'blockquote', 'pre', 'code'
        }

        # Escapar HTML primero
        sanitized = html.escape(html_content)

        # Permitir tags seguros
        for tag in allowed_tags:
            sanitized = re.sub(f'&lt;({tag})&gt;',
r'<\1>',
                sanitized,
                flags=re.IGNORECASE)
            sanitized = re.sub(f'&lt;/({tag})&gt;',
r'</\1>',
                sanitized,
                flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def create_content_filter(max_length: int = 1000) -> Callable:
        """
        Crea un filtro de contenido personalizado.

        Args:
            max_length: Longitud máxima permitida

        Returns:
            Callable: Función de filtro
        """
        def filter_content(text: str) -> str:
            if not text:
                return ""

            # Limitar longitud
            if len(text) > max_length:
                text = text[:max_length] + "..."

            # Sanitizar
            return XSSProtection.sanitize_text(text)

        return filter_content


class FormProtector(QObject):
    """Protector de formularios contra XSS."""

    # Señal emitida cuando se detecta contenido peligroso
    dangerous_content_detected = pyqtSignal(str, str)  # field_name, content

    def __init__(self, parent=None):
        super().__init__(parent)
        self.protected_fields = {}
        self.field_filters = {}

    def protect_field(self, field: Union[QLineEdit, QTextEdit, QPlainTextEdit],
                     field_name: str = "", max_length: int = 1000):
        """
        Protege un campo de formulario.

        Args:
            field: Campo a proteger
            field_name: Nombre del campo para logging
            max_length: Longitud máxima permitida
        """
        if not field_name:
            field_name = field.objectName() or f"{type(field).__name__}_{id(field)}"

        self.protected_fields[field_name] = field
        self.field_filters[field_name] = XSSProtection.create_content_filter(max_length)

        # Conectar eventos según el tipo de campo
        if isinstance(field, QLineEdit):
            field.textChanged.connect(lambda text: self._validate_field(field_name, text))
        elif isinstance(field, (QTextEdit, QPlainTextEdit)):
            field.textChanged.connect(lambda: self._validate_field(field_name, field.toPlainText()))

    def _validate_field(self, field_name: str, content: str):
        """Valida el contenido de un campo."""
        if not XSSProtection.validate_safe_content(content):
            self.dangerous_content_detected.emit(field_name, content)

            # Sanitizar automáticamente
            field = self.protected_fields.get(field_name)
            filter_func = self.field_filters.get(field_name)

            if field and filter_func:
                sanitized = filter_func(content)

                # Actualizar el campo con contenido sanitizado
                if isinstance(field, QLineEdit):
                    field.blockSignals(True)
                    field.setText(sanitized)
                    field.blockSignals(False)
                elif isinstance(field, (QTextEdit, QPlainTextEdit)):
                    field.blockSignals(True)
                    field.setPlainText(sanitized)
                    field.blockSignals(False)

    def get_sanitized_data(self) -> Dict[str, str]:
        """
        Obtiene datos sanitizados de todos los campos protegidos.

        Returns:
            Dict[str, str]: Datos sanitizados
        """
        data = {}

        for field_name, field in self.protected_fields.items():
            filter_func = self.field_filters.get(field_name)

            if isinstance(field, QLineEdit):
                content = field.text()
            elif isinstance(field, (QTextEdit, QPlainTextEdit)):
                content = field.toPlainText()
            else:
                continue

            if filter_func:
                data[field_name] = filter_func(content)
            else:
                data[field_name] = XSSProtection.sanitize_text(content)

        return data

    def validate_all_fields(self) -> bool:
        """
        Valida todos los campos protegidos.

        Returns:
            bool: True si todos los campos son válidos
        """
        for field_name, field in self.protected_fields.items():
            if isinstance(field, QLineEdit):
                content = field.text()
            elif isinstance(field, (QTextEdit, QPlainTextEdit)):
                content = field.toPlainText()
            else:
                continue

            if not XSSProtection.validate_safe_content(content):
                return False

        return True


def xss_protect(*field_names):
    """
    Decorador para proteger métodos que manejan datos de formulario.

    Args:
        *field_names: Nombres de los campos a proteger
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Sanitizar argumentos
            sanitized_args = []
            for arg in args:
                if isinstance(arg, str):
                    sanitized_args.append(XSSProtection.sanitize_text(arg))
                else:
                    sanitized_args.append(arg)

            # Sanitizar kwargs
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    sanitized_kwargs[key] = XSSProtection.sanitize_text(value)
                else:
                    sanitized_kwargs[key] = value

            return func(self, *sanitized_args, **sanitized_kwargs)

        wrapper._xss_protected = True
        wrapper._protected_fields = field_names
        return wrapper

    return decorator


def sanitize_form_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza datos de formulario de manera más agresiva.

    Args:
        data: Datos a sanitizar

    Returns:
        Dict[str, Any]: Datos sanitizados
    """
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Aplicar múltiples capas de sanitización
            clean_value = XSSProtection.sanitize_text(value)
            # Sanitización adicional para formularios
            clean_value = re.sub(r'<script[^>]*>.*?</script>',
'',
                clean_value,
                flags=re.IGNORECASE | re.DOTALL)
            clean_value = re.sub(r'javascript\s*:',
'',
                clean_value,
                flags=re.IGNORECASE)
            clean_value = re.sub(r'eval\s*\(',
'',
                clean_value,
                flags=re.IGNORECASE)
            sanitized[key] = clean_value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_form_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_form_data({'item': item})['item'] if isinstance(item, (str, dict))
                else XSSProtection.sanitize_text(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized
