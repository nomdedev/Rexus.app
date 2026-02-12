#!/usr/bin/env python3
"""
Módulo de sanitización unificada para todos los módulos del sistema.
Proporciona métodos seguros para limpiar y validar datos de entrada.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class UnifiedSanitizer:
    """
    Clase unificada para sanitización de datos en todo el sistema.
    """
    
    def __init__(self):
        """Inicializa el sanitizador unificado."""
        self.logger = logging.getLogger(__name__)
        
        # Patrones comunes para validación
        self.patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'username': r'^[a-zA-Z0-9_]{3,50}$',
            'phone': r'^[\d\s\-\+\(\)]{7,20}$',
            'numeric': r'^\d+$',
            'decimal': r'^\d+\.?\d*$',
            'alpha': r'^[a-zA-Z\s]+$',
            'alphanumeric': r'^[a-zA-Z0-9\s]+$',
            'safe_string': r'^[a-zA-Z0-9\s\-_.,;:()]+$'
        }
    
    def sanitize_string(self, value: str, max_length: int = 255) -> str:
        """
        Sanitiza una cadena de texto básica.
        
        Args:
            value: Valor a sanitizar
            max_length: Longitud máxima permitida
            
        Returns:
            str: Cadena sanitizada
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Eliminar espacios en blanco al inicio y final
        value = value.strip()
        
        # Escapar caracteres HTML
        value = html.escape(value)
        
        # Limitar longitud
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def sanitize_email(self, email: str) -> str:
        """
        Sanitiza y valida una dirección de email.
        
        Args:
            email: Email a sanitizar
            
        Returns:
            str: Email sanitizado
        """
        if not isinstance(email, str):
            return ""
        
        email = email.strip().lower()
        
        # Validar formato
        if not re.match(self.patterns['email'], email):
            return ""
        
        return email
    
    def sanitize_username(self, username: str) -> str:
        """
        Sanitiza y valida un nombre de usuario.
        
        Args:
            username: Nombre de usuario a sanitizar
            
        Returns:
            str: Nombre de usuario sanitizado
        """
        if not isinstance(username, str):
            return ""
        
        username = username.strip()
        
        # Validar formato
        if not re.match(self.patterns['username'], username):
            return ""
        
        return username
    
    def sanitize_numeric(self, value: Any) -> Optional[int]:
        """
        Sanitiza y valida un valor numérico entero.
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Optional[int]: Valor numérico sanitizado o None
        """
        if isinstance(value, int):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            if re.match(self.patterns['numeric'], value):
                return int(value)
        
        return None
    
    def sanitize_decimal(self, value: Any) -> Optional[float]:
        """
        Sanitiza y valida un valor decimal.
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Optional[float]: Valor decimal sanitizado o None
        """
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            value = value.strip()
            if re.match(self.patterns['decimal'], value):
                return float(value)
        
        return None
    
    def sanitize_phone(self, phone: str) -> str:
        """
        Sanitiza un número de teléfono.
        
        Args:
            phone: Teléfono a sanitizar
            
        Returns:
            str: Teléfono sanitizado
        """
        if not isinstance(phone, str):
            return ""
        
        phone = phone.strip()
        
        # Validar formato
        if not re.match(self.patterns['phone'], phone):
            return ""
        
        return phone
    
    def sanitize_sql_identifier(self, identifier: str) -> str:
        """
        Sanitiza un identificador SQL (nombre de tabla, columna, etc.).
        
        Args:
            identifier: Identificador a sanitizar
            
        Returns:
            str: Identificador sanitizado
        """
        if not isinstance(identifier, str):
            return ""
        
        identifier = identifier.strip()
        
        # Solo permitir caracteres alfanuméricos y guiones bajos
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            return ""
        
        return identifier
    
    def sanitize_html(self, html_content: str) -> str:
        """
        Sanitiza contenido HTML permitiendo solo etiquetas seguras.
        
        Args:
            html_content: Contenido HTML a sanitizar
            
        Returns:
            str: HTML sanitizado
        """
        if not isinstance(html_content, str):
            return ""
        
        # Por ahora, solo escapar todo el HTML
        # En el futuro se podría implementar una librería como bleach
        return html.escape(html_content)
    
    def sanitize_list(self, values: List[Any], item_type: str = 'string') -> List[Any]:
        """
        Sanitiza una lista de valores.
        
        Args:
            values: Lista a sanitizar
            item_type: Tipo de elementos ('string', 'numeric', 'email')
            
        Returns:
            List[Any]: Lista sanitizada
        """
        if not isinstance(values, list):
            return []
        
        sanitized = []
        
        for item in values:
            if item_type == 'string':
                sanitized.append(self.sanitize_string(item))
            elif item_type == 'numeric':
                sanitized.append(self.sanitize_numeric(item))
            elif item_type == 'email':
                sanitized.append(self.sanitize_email(item))
            else:
                sanitized.append(self.sanitize_string(item))
        
        return [item for item in sanitized if item is not None and item != ""]
    
    def sanitize_dict(self, data: Dict[str, Any], schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Sanitiza un diccionario según un esquema definido.
        
        Args:
            data: Diccionario a sanitizar
            schema: Esquema de sanitización {campo: tipo}
            
        Returns:
            Dict[str, Any]: Diccionario sanitizado
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            if key in schema:
                field_type = schema[key]
                
                if field_type == 'string':
                    sanitized[key] = self.sanitize_string(value)
                elif field_type == 'email':
                    sanitized[key] = self.sanitize_email(value)
                elif field_type == 'username':
                    sanitized[key] = self.sanitize_username(value)
                elif field_type == 'numeric':
                    sanitized[key] = self.sanitize_numeric(value)
                elif field_type == 'decimal':
                    sanitized[key] = self.sanitize_decimal(value)
                elif field_type == 'phone':
                    sanitized[key] = self.sanitize_phone(value)
                elif field_type == 'sql_identifier':
                    sanitized[key] = self.sanitize_sql_identifier(value)
                else:
                    sanitized[key] = self.sanitize_string(value)
        
        return sanitized
    
    def validate_pattern(self, value: str, pattern_name: str) -> bool:
        """
        Valida un valor contra un patrón predefinido.
        
        Args:
            value: Valor a validar
            pattern_name: Nombre del patrón
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not isinstance(value, str) or pattern_name not in self.patterns:
            return False
        
        return bool(re.match(self.patterns[pattern_name], value))
    
    def is_safe_string(self, value: str) -> bool:
        """
        Verifica si una cadena es segura (no contiene caracteres peligrosos).
        
        Args:
            value: Valor a verificar
            
        Returns:
            bool: True si es seguro, False en caso contrario
        """
        if not isinstance(value, str):
            return False
        
        # Verificar que no contenga caracteres peligrosos
        dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/', ';', '(', ')', '{', '}']
        
        for char in dangerous_chars:
            if char in value:
                return False
        
        return True

# Instancia global del sanitizador
unified_sanitizer = UnifiedSanitizer()

# Funciones de conveniencia para uso directo
def sanitize_string(value: str, max_length: int = 255) -> str:
    """Función de conveniencia para sanitizar strings."""
    return unified_sanitizer.sanitize_string(value, max_length)

def sanitize_email(email: str) -> str:
    """Función de conveniencia para sanitizar emails."""
    return unified_sanitizer.sanitize_email(email)

def sanitize_username(username: str) -> str:
    """Función de conveniencia para sanitizar nombres de usuario."""
    return unified_sanitizer.sanitize_username(username)

def sanitize_numeric(value: Any) -> Optional[int]:
    """Función de conveniencia para sanitizar valores numéricos."""
    return unified_sanitizer.sanitize_numeric(value)

def sanitize_decimal(value: Any) -> Optional[float]:
    """Función de conveniencia para sanitizar valores decimales."""
    return unified_sanitizer.sanitize_decimal(value)

def sanitize_sql_identifier(identifier: str) -> str:
    """Función de conveniencia para sanitizar identificadores SQL."""
    return unified_sanitizer.sanitize_sql_identifier(identifier)