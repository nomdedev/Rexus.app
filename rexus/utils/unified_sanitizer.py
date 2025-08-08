"""
Unified Data Sanitizer - Sistema unificado de sanitización de datos
Reemplaza las implementaciones inconsistentes de DataSanitizer en diferentes módulos

Responsabilidades:
- Sanitización consistente de strings
- Validación y limpieza de datos numéricos
- Validación de emails
- Escape de HTML/XML
- Prevención de SQL Injection
- Validación de URLs y archivos
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

# Configurar logging
logger = logging.getLogger(__name__)


class UnifiedDataSanitizer:
    """Sanitizador de datos unificado para toda la aplicación."""
    
    def __init__(self):
        """Inicializa el sanitizador con configuraciones por defecto."""
        # Patrones de seguridad
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"].*['\"])",
            r"(\bUNION\s+(ALL\s+)?SELECT\b)",
            r"(\bEXEC\s*\()",
            r"(\bCHAR\s*\()",
            r"(\bCAST\s*\()",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
        ]
        
        # Configuraciones
        self.max_string_length = 1000
        self.max_numeric_value = 999999999
        self.min_numeric_value = -999999999
    
    def sanitize_string(self, value: Any, max_length: Optional[int] = None, allow_html: bool = False) -> str:
        """
        Sanitiza una cadena de texto.
        
        Args:
            value: Valor a sanitizar
            max_length: Longitud máxima permitida
            allow_html: Si permitir HTML básico
            
        Returns:
            String sanitizado
        """
        try:
            if value is None:
                return ""
            
            # Convertir a string
            text = str(value)
            
            # Aplicar longitud máxima
            if max_length is None:
                max_length = self.max_string_length
            text = text[:max_length]
            
            # Limpiar caracteres de control
            text = self._remove_control_chars(text)
            
            # Prevenir SQL Injection
            text = self._prevent_sql_injection(text)
            
            # Prevenir XSS
            if not allow_html:
                text = self._prevent_xss(text)
                text = html.escape(text)
            else:
                text = self._sanitize_html_safe(text)
            
            # Normalizar espacios
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logger.warning(f"Error sanitizando string: {e}")
            return ""
    
    def sanitize_numeric(self, value: Any, min_val: Optional[Union[int, float]] = None, 
                        max_val: Optional[Union[int, float]] = None, 
                        allow_decimal: bool = True) -> Union[int, float, None]:
        """
        Sanitiza un valor numérico.
        
        Args:
            value: Valor a sanitizar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            allow_decimal: Si permitir decimales
            
        Returns:
            Número sanitizado o None si inválido
        """
        try:
            if value is None or value == "":
                return None
            
            # Convertir string a número
            if isinstance(value, str):
                # Limpiar caracteres no numéricos excepto punto y signo
                cleaned = re.sub(r'[^\d\.\-\+]', '', value)
                if not cleaned or cleaned in ['-', '+', '.']:
                    return None
                value = cleaned
            
            # Intentar conversión
            if allow_decimal:
                try:
                    num = Decimal(str(value))
                    result = float(num)
                except (InvalidOperation, ValueError):
                    return None
            else:
                try:
                    result = int(float(value))
                except (ValueError, OverflowError):
                    return None
            
            # Aplicar rangos
            if min_val is not None:
                result = max(result, min_val)
            else:
                result = max(result, self.min_numeric_value)
                
            if max_val is not None:
                result = min(result, max_val)
            else:
                result = min(result, self.max_numeric_value)
            
            return result
            
        except Exception as e:
            logger.warning(f"Error sanitizando número: {e}")
            return None
    
    def sanitize_email(self, email: Any) -> Optional[str]:
        """
        Sanitiza y valida una dirección de email.
        
        Args:
            email: Email a sanitizar
            
        Returns:
            Email sanitizado o None si inválido
        """
        try:
            if not email:
                return None
            
            email_str = str(email).strip().lower()
            
            # Validar longitud
            if len(email_str) > 254:  # RFC 5321
                return None
            
            # Sanitizar caracteres peligrosos
            email_str = self._prevent_sql_injection(email_str)
            email_str = self._prevent_xss(email_str)
            
            # Validar formato básico
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_str):
                return None
            
            # Verificar partes del email
            local, domain = email_str.split('@')
            
            # Validar parte local
            if len(local) > 64 or not local:
                return None
            
            # Validar dominio
            if len(domain) > 253 or not domain or domain.startswith('.') or domain.endswith('.'):
                return None
            
            return email_str
            
        except Exception as e:
            logger.warning(f"Error sanitizando email: {e}")
            return None
    
    def sanitize_phone(self, phone: Any) -> Optional[str]:
        """
        Sanitiza un número de teléfono.
        
        Args:
            phone: Teléfono a sanitizar
            
        Returns:
            Teléfono sanitizado o None si inválido
        """
        try:
            if not phone:
                return None
            
            phone_str = str(phone)
            
            # Extraer solo números, +, -, (, ), espacios
            cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', phone_str)
            
            # Normalizar espacios
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            # Validar longitud (entre 7 y 20 caracteres es razonable)
            if len(cleaned) < 7 or len(cleaned) > 20:
                return None
            
            # Verificar que tiene al menos algunos dígitos
            if not re.search(r'\d{3}', cleaned):
                return None
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error sanitizando teléfono: {e}")
            return None
    
    def sanitize_url(self, url: Any) -> Optional[str]:
        """
        Sanitiza una URL.
        
        Args:
            url: URL a sanitizar
            
        Returns:
            URL sanitizada o None si inválida
        """
        try:
            if not url:
                return None
            
            url_str = str(url).strip()
            
            # Validar longitud
            if len(url_str) > 2048:
                return None
            
            # Prevenir scripts maliciosos
            url_str = self._prevent_xss(url_str)
            
            # Validar esquema
            parsed = urlparse(url_str)
            allowed_schemes = ['http', 'https', 'ftp', 'ftps']
            
            if parsed.scheme.lower() not in allowed_schemes:
                return None
            
            # Verificar que tiene dominio válido
            if not parsed.netloc:
                return None
            
            return url_str
            
        except Exception as e:
            logger.warning(f"Error sanitizando URL: {e}")
            return None
    
    def sanitize_sql_input(self, value: Any) -> str:
        """
        Sanitiza entrada para prevenir SQL Injection.
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Valor sanitizado
        """
        if not value:
            return ""
        
        text = str(value)
        
        # Aplicar patrones de SQL injection
        for pattern in self.sql_injection_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # Escapar comillas
        text = text.replace("'", "''")
        text = text.replace('"', '""')
        
        return text
    
    def sanitize_html(self, value: Any, allowed_tags: Optional[List[str]] = None) -> str:
        """
        Sanitiza HTML permitiendo solo tags específicos.
        
        Args:
            value: Valor a sanitizar
            allowed_tags: Tags HTML permitidos
            
        Returns:
            HTML sanitizado
        """
        if not value:
            return ""
        
        text = str(value)
        
        # Si no se permiten tags, escapar todo
        if not allowed_tags:
            return html.escape(text)
        
        # Sanitizar tags peligrosos
        text = self._prevent_xss(text)
        
        # Permitir solo tags específicos (implementación básica)
        # Para una implementación completa, usar librerías como bleach
        for tag in ['script', 'iframe', 'object', 'embed', 'link', 'meta', 'style']:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
            pattern = f'<{tag}[^>]*/?>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def sanitize_dict(self, data: Dict[str, Any], string_fields: Optional[List[str]] = None, 
                     numeric_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Sanitiza un diccionario completo.
        
        Args:
            data: Diccionario a sanitizar
            string_fields: Campos que deben tratarse como strings
            numeric_fields: Campos que deben tratarse como números
            
        Returns:
            Diccionario sanitizado
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitizar clave
            clean_key = self.sanitize_string(key, 100)
            
            # Sanitizar valor según tipo
            if string_fields and key in string_fields:
                sanitized[clean_key] = self.sanitize_string(value)
            elif numeric_fields and key in numeric_fields:
                sanitized[clean_key] = self.sanitize_numeric(value)
            elif isinstance(value, str):
                sanitized[clean_key] = self.sanitize_string(value)
            elif isinstance(value, (int, float)):
                sanitized[clean_key] = self.sanitize_numeric(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [self.sanitize_string(item) if isinstance(item, str) else item for item in value]
            else:
                sanitized[clean_key] = value
        
        return sanitized
    
    def _remove_control_chars(self, text: str) -> str:
        """Remueve caracteres de control peligrosos."""
        # Mantener solo caracteres imprimibles, tabs, y newlines
        return ''.join(char for char in text if ord(char) >= 32 or char in ['\t', '\n', '\r'])
    
    def _prevent_sql_injection(self, text: str) -> str:
        """Previene patrones de SQL Injection."""
        for pattern in self.sql_injection_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text
    
    def _prevent_xss(self, text: str) -> str:
        """Previene patrones de XSS."""
        for pattern in self.xss_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        return text
    
    def _sanitize_html_safe(self, text: str) -> str:
        """Sanitiza HTML manteniendo tags seguros."""
        # Lista de tags seguros
        safe_tags = ['p', 'br', 'strong', 'em', 'u', 'b', 'i']
        
        # Escapar todo primero
        text = html.escape(text)
        
        # Restaurar tags seguros
        for tag in safe_tags:
            text = text.replace(f'&lt;{tag}&gt;', f'<{tag}>')
            text = text.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
        
        return text


# Instancia global para uso en toda la aplicación
unified_sanitizer = UnifiedDataSanitizer()


def sanitize_string(value: Any, max_length: Optional[int] = None) -> str:
    """Función de conveniencia para sanitizar strings."""
    return unified_sanitizer.sanitize_string(value, max_length)


def sanitize_numeric(value: Any, min_val: Optional[Union[int, float]] = None, 
                    max_val: Optional[Union[int, float]] = None) -> Union[int, float, None]:
    """Función de conveniencia para sanitizar números."""
    return unified_sanitizer.sanitize_numeric(value, min_val, max_val)


def sanitize_email(email: Any) -> Optional[str]:
    """Función de conveniencia para sanitizar emails."""
    return unified_sanitizer.sanitize_email(email)


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Función de conveniencia para sanitizar diccionarios."""
    return unified_sanitizer.sanitize_dict(data)