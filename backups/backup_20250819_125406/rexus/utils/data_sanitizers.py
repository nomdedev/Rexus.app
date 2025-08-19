#!/usr/bin/env python3
"""
Sanitizadores de Datos Especializados - Rexus.app

Proporciona sanitizadores específicos para diferentes tipos de datos
con enfoque en seguridad y prevención de ataques.

Fecha: 15/08/2025
Componente: Seguridad - Sanitización de Datos
"""

import re
import html
import json
import hashlib
import secrets
import unicodedata
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from pathlib import Path

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("data_sanitizers")
except ImportError:
    import logging
    logger = logging.getLogger("data_sanitizers")


class TextSanitizer:
    """Sanitizador especializado para texto y strings."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """
        Sanitiza texto general removiendo contenido peligroso.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida
            allow_html: Si permite tags HTML básicos
        
        Returns:
            str: Texto sanitizado
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Normalizar unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remover caracteres de control
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Escapar HTML si no se permite
        if not allow_html:
            text = html.escape(text)
        else:
            # Permitir solo tags seguros
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
            text = TextSanitizer._sanitize_html(text, allowed_tags)
        
        # Truncar si excede longitud máxima
        if len(text) > max_length:
            text = text[:max_length].rstrip()
            logger.warning(f"Texto truncado a {max_length} caracteres")
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitiza nombres de personas."""
        if not isinstance(name, str):
            name = str(name)
        
        # Solo letras, espacios, guiones, puntos y acentos
        name = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\.]', '', name)
        
        # Normalizar espacios y capitalizar
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Limitar longitud
        if len(name) > 100:
            name = name[:100].rstrip()
        
        return name.strip()
    
    @staticmethod
    def sanitize_code(code: str) -> str:
        """Sanitiza códigos alfanuméricos."""
        if not isinstance(code, str):
            code = str(code)
        
        # Solo letras mayúsculas, números y guiones
        code = re.sub(r'[^A-Z0-9\-_]', '', code.upper())
        
        # Limitar longitud
        if len(code) > 20:
            code = code[:20]
        
        return code.strip()
    
    @staticmethod
    def sanitize_description(description: str) -> str:
        """Sanitiza descripciones permitiendo más flexibilidad."""
        if not isinstance(description, str):
            description = str(description)
        
        # Remover scripts y contenido peligroso
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
        ]
        
        for pattern in dangerous_patterns:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE | re.DOTALL)
        
        # Escapar HTML
        description = html.escape(description)
        
        # Limitar longitud
        if len(description) > 2000:
            description = description[:2000].rstrip()
        
        return description.strip()
    
    @staticmethod
    def _sanitize_html(text: str, allowed_tags: List[str]) -> str:
        """Sanitiza HTML permitiendo solo tags específicos."""
        # Remover todos los tags excepto los permitidos
        allowed_pattern = '|'.join(allowed_tags)
        tag_pattern = r'<(?!/?(?:' + allowed_pattern + r')\b)[^>]*>'
        text = re.sub(tag_pattern, '', text, flags=re.IGNORECASE)
        
        # Remover atributos de eventos
        event_pattern = r'\s+on\w+\s*=\s*["\'][^"\']*["\']'
        text = re.sub(event_pattern, '', text, flags=re.IGNORECASE)
        
        return text


class NumericSanitizer:
    """Sanitizador especializado para datos numéricos."""
    
    @staticmethod
    def sanitize_integer(value: Any, min_value: Optional[int] = None, 
                        max_value: Optional[int] = None) -> Optional[int]:
        """
        Sanitiza y valida enteros.
        
        Args:
            value: Valor a sanitizar
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
        
        Returns:
            Optional[int]: Entero sanitizado o None si es inválido
        """
        try:
            if isinstance(value, str):
                # Remover caracteres no numéricos
                value = re.sub(r'[^\d\-]', '', value)
            
            int_value = int(value)
            
            # Verificar rango
            if min_value is not None and int_value < min_value:
                logger.warning(f"Valor entero {int_value} menor que mínimo {min_value}")
                return min_value
            
            if max_value is not None and int_value > max_value:
                logger.warning(f"Valor entero {int_value} mayor que máximo {max_value}")
                return max_value
            
            return int_value
        
        except (ValueError, TypeError):
            logger.error(f"No se pudo convertir '{value}' a entero")
            return None
    
    @staticmethod
    def sanitize_decimal(value: Any, max_digits: int = 10, 
                        decimal_places: int = 2) -> Optional[Decimal]:
        """
        Sanitiza decimales con precisión específica.
        
        Args:
            value: Valor a sanitizar
            max_digits: Máximo número de dígitos
            decimal_places: Lugares decimales
        
        Returns:
            Optional[Decimal]: Decimal sanitizado o None si es inválido
        """
        try:
            if isinstance(value, str):
                # Limpiar caracteres no numéricos excepto punto y coma
                value = re.sub(r'[^\d\.\-,]', '', value)
                # Convertir coma a punto para decimales
                value = value.replace(',', '.')
            
            decimal_value = Decimal(str(value))
            
            # Redondear a lugares decimales especificados
            decimal_value = decimal_value.quantize(
                Decimal('0.' + '0' * decimal_places)
            )
            
            # Verificar número máximo de dígitos
            if len(str(decimal_value).replace('.', '').replace('-', '')) > max_digits:
                logger.warning(f"Decimal {decimal_value} excede máximo de dígitos {max_digits}")
                return None
            
            return decimal_value
        
        except (InvalidOperation, ValueError, TypeError):
            logger.error(f"No se pudo convertir '{value}' a decimal")
            return None
    
    @staticmethod
    def sanitize_currency(value: Any) -> Optional[Decimal]:
        """Sanitiza valores monetarios."""
        return NumericSanitizer.sanitize_decimal(value, max_digits=12, decimal_places=2)
    
    @staticmethod
    def sanitize_percentage(value: Any) -> Optional[float]:
        """Sanitiza porcentajes (0-100)."""
        try:
            float_value = float(value)
            # Asegurar rango 0-100
            float_value = max(0.0, min(100.0, float_value))
            return round(float_value, 2)
        except (ValueError, TypeError):
            logger.error(f"No se pudo convertir '{value}' a porcentaje")
            return None


class DateTimeSanitizer:
    """Sanitizador especializado para fechas y horas."""
    
    @staticmethod
    def sanitize_date(value: Any, date_format: str = '%Y-%m-%d') -> Optional[date]:
        """
        Sanitiza fechas.
        
        Args:
            value: Valor a sanitizar
            date_format: Formato esperado de fecha
        
        Returns:
            Optional[date]: Fecha sanitizada o None si es inválida
        """
        try:
            if isinstance(value, date):
                return value
            
            if isinstance(value, datetime):
                return value.date()
            
            if isinstance(value, str):
                # Limpiar caracteres no válidos para fechas
                value = re.sub(r'[^\d\-/:]', '', value)
                parsed_date = datetime.strptime(value, date_format).date()
                
                # Verificar rango razonable
                min_date = date(1900, 1, 1)
                max_date = date(2100, 12, 31)
                
                if min_date <= parsed_date <= max_date:
                    return parsed_date
                else:
                    logger.warning(f"Fecha {parsed_date} fuera de rango válido")
                    return None
            
        except (ValueError, TypeError):
            logger.error(f"No se pudo convertir '{value}' a fecha")
            return None
    
    @staticmethod
    def sanitize_datetime(value: Any, datetime_format: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
        """Sanitiza fechas y horas."""
        try:
            if isinstance(value, datetime):
                return value
            
            if isinstance(value, str):
                parsed_datetime = datetime.strptime(value, datetime_format)
                
                # Verificar rango razonable
                min_datetime = datetime(1900, 1, 1)
                max_datetime = datetime(2100, 12, 31)
                
                if min_datetime <= parsed_datetime <= max_datetime:
                    return parsed_datetime
                else:
                    logger.warning(f"DateTime {parsed_datetime} fuera de rango válido")
                    return None
            
        except (ValueError, TypeError):
            logger.error(f"No se pudo convertir '{value}' a datetime")
            return None


class ContactSanitizer:
    """Sanitizador especializado para datos de contacto."""
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """
        Sanitiza emails.
        
        Args:
            email: Email a sanitizar
        
        Returns:
            Optional[str]: Email sanitizado o None si es inválido
        """
        if not isinstance(email, str):
            return None
        
        # Convertir a minúsculas y limpiar espacios
        email = email.lower().strip()
        
        # Verificar formato básico
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            logger.warning(f"Email inválido: {email}")
            return None
        
        # Verificar longitud de partes
        try:
            local, domain = email.rsplit('@', 1)
            if len(local) > 64 or len(domain) > 253:
                logger.warning(f"Email con partes demasiado largas: {email}")
                return None
        except ValueError:
            return None
        
        # Escapar para HTML
        return html.escape(email)
    
    @staticmethod
    def sanitize_phone(phone: str) -> Optional[str]:
        """
        Sanitiza números telefónicos.
        
        Args:
            phone: Teléfono a sanitizar
        
        Returns:
            Optional[str]: Teléfono sanitizado o None si es inválido
        """
        if not isinstance(phone, str):
            return None
        
        # Remover todos los caracteres excepto dígitos, +, -, (, ), espacios
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone.strip())
        
        # Verificar longitud razonable
        digits_only = re.sub(r'[^\d]', '', phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            logger.warning(f"Teléfono con longitud inválida: {phone}")
            return None
        
        return phone
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """
        Sanitiza URLs.
        
        Args:
            url: URL a sanitizar
        
        Returns:
            Optional[str]: URL sanitizada o None si es inválida
        """
        if not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Verificar esquema permitido
        if not (url.startswith('http://') or url.startswith('https://')):
            # Agregar https por defecto si no tiene esquema
            if not url.startswith('//'):
                url = 'https://' + url
            else:
                url = 'https:' + url
        
        # Verificar longitud máxima
        if len(url) > 2083:
            logger.warning(f"URL demasiado larga: {len(url)} caracteres")
            return None
        
        # Verificar caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", ';', '|']
        for char in dangerous_chars:
            if char in url:
                logger.warning(f"URL contiene caracteres peligrosos: {url}")
                return None
        
        return html.escape(url)


class SecuritySanitizer:
    """Sanitizador especializado para datos de seguridad."""
    
    @staticmethod
    def sanitize_password(password: str) -> Optional[str]:
        """
        Sanitiza contraseñas (no las modifica, solo valida).
        
        Args:
            password: Contraseña a validar
        
        Returns:
            Optional[str]: Contraseña si es válida o None
        """
        if not isinstance(password, str):
            return None
        
        # Verificar longitud mínima
        if len(password) < 8:
            logger.warning("Contraseña demasiado corta")
            return None
        
        # Verificar longitud máxima (por seguridad)
        if len(password) > 128:
            logger.warning("Contraseña demasiado larga")
            return None
        
        # Verificar complejidad básica
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit):
            logger.warning("Contraseña no cumple requisitos de complejidad")
            return None
        
        return password  # Retornar sin modificar
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera hash seguro de contraseña.
        
        Args:
            password: Contraseña a hashear
        
        Returns:
            str: Hash de la contraseña
        """
        # Generar salt aleatorio
        salt = secrets.token_hex(32)
        
        # Crear hash con salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Iteraciones
        )
        
        # Combinar salt y hash
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica contraseña contra hash.
        
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
        
        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            salt, hash_hex = hashed.split(':')
            
            # Recrear hash con la misma salt
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return password_hash.hex() == hash_hex
        
        except (ValueError, AttributeError):
            return False


class FileSanitizer:
    """Sanitizador especializado para archivos y rutas."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> Optional[str]:
        """
        Sanitiza nombres de archivo.
        
        Args:
            filename: Nombre de archivo a sanitizar
        
        Returns:
            Optional[str]: Nombre sanitizado o None si es inválido
        """
        if not isinstance(filename, str):
            return None
        
        # Remover path (solo el nombre)
        filename = Path(filename).name
        
        # Verificar longitud
        if len(filename) > 255:
            logger.warning(f"Nombre de archivo demasiado largo: {len(filename)}")
            return None
        
        # Remover caracteres peligrosos del sistema
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        
        # Verificar extensiones peligrosas
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
            '.vbs', '.js', '.jar', '.msi', '.dll'
        ]
        
        file_ext = Path(filename).suffix.lower()
        if file_ext in dangerous_extensions:
            logger.warning(f"Extensión de archivo peligrosa: {file_ext}")
            return None
        
        # Asegurar que no esté vacío después de sanitización
        if not filename or filename in ['.', '..']:
            return None
        
        return filename.strip()
    
    @staticmethod
    def sanitize_file_path(file_path: str, base_directory: str) -> Optional[str]:
        """
        Sanitiza rutas de archivo previniendo path traversal.
        
        Args:
            file_path: Ruta a sanitizar
            base_directory: Directorio base permitido
        
        Returns:
            Optional[str]: Ruta sanitizada o None si es inválida
        """
        if not isinstance(file_path, str) or not isinstance(base_directory, str):
            return None
        
        try:
            # Resolver rutas absolutas
            base_path = Path(base_directory).resolve()
            target_path = (base_path / file_path).resolve()
            
            # Verificar que la ruta esté dentro del directorio base
            if not str(target_path).startswith(str(base_path)):
                logger.warning(f"Intento de path traversal detectado: {file_path}")
                return None
            
            return str(target_path)
        
        except (OSError, ValueError):
            logger.error(f"Ruta inválida: {file_path}")
            return None


class SQLSanitizer:
    """Sanitizador especializado para prevenir SQL injection."""
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> Optional[str]:
        """
        Sanitiza identificadores SQL (nombres de tablas, columnas).
        
        Args:
            identifier: Identificador a sanitizar
        
        Returns:
            Optional[str]: Identificador sanitizado o None si es inválido
        """
        if not isinstance(identifier, str):
            return None
        
        # Solo permitir letras, números y guiones bajos
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            logger.warning(f"Identificador SQL inválido: {identifier}")
            return None
        
        # Verificar longitud
        if len(identifier) > 64:
            logger.warning(f"Identificador SQL demasiado largo: {identifier}")
            return None
        
        # Verificar que no sea una palabra reservada
        reserved_words = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'TRIGGER', 'PROCEDURE',
            'FUNCTION', 'DATABASE', 'SCHEMA', 'USER', 'GRANT', 'REVOKE'
        }
        
        if identifier.upper() in reserved_words:
            logger.warning(f"Identificador SQL es palabra reservada: {identifier}")
            return None
        
        return identifier
    
    @staticmethod
    def escape_sql_string(value: str) -> str:
        """
        Escapa strings para SQL (aunque se recomienda usar parámetros).
        
        Args:
            value: String a escapar
        
        Returns:
            str: String escapado
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Escapar comillas simples duplicándolas
        escaped = value.replace("'", "''")
        
        # Escapar caracteres de control
        escaped = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', escaped)
        
        return escaped


# Clase principal que unifica todos los sanitizadores
class UnifiedSanitizer:
    """Sanitizador unificado que proporciona acceso a todos los sanitizadores especializados."""
    
    def __init__(self):
        self.text = TextSanitizer()
        self.numeric = NumericSanitizer()
        self.datetime = DateTimeSanitizer()
        self.contact = ContactSanitizer()
        self.security = SecuritySanitizer()
        self.file = FileSanitizer()
        self.sql = SQLSanitizer()
    
    def sanitize_by_type(self, value: Any, data_type: str, **kwargs) -> Any:
        """
        Sanitiza un valor según su tipo.
        
        Args:
            value: Valor a sanitizar
            data_type: Tipo de dato
            **kwargs: Argumentos adicionales para el sanitizador
        
        Returns:
            Any: Valor sanitizado
        """
        if value is None or value == '':
            return value
        
        sanitizers = {
            'text': self.text.sanitize_text,
            'name': self.text.sanitize_name,
            'code': self.text.sanitize_code,
            'description': self.text.sanitize_description,
            'integer': self.numeric.sanitize_integer,
            'decimal': self.numeric.sanitize_decimal,
            'currency': self.numeric.sanitize_currency,
            'percentage': self.numeric.sanitize_percentage,
            'date': self.datetime.sanitize_date,
            'datetime': self.datetime.sanitize_datetime,
            'email': self.contact.sanitize_email,
            'phone': self.contact.sanitize_phone,
            'url': self.contact.sanitize_url,
            'password': self.security.sanitize_password,
            'filename': self.file.sanitize_filename,
            'sql_identifier': self.sql.sanitize_sql_identifier,
        }
        
        sanitizer = sanitizers.get(data_type)
        if sanitizer:
            try:
                return sanitizer(value, **kwargs)
            except Exception as e:
                logger.error(f"Error sanitizando {data_type}: {e}")
                return None
        else:
            logger.warning(f"Tipo de sanitizador no reconocido: {data_type}")
            return self.text.sanitize_text(str(value))


# Instancia global del sanitizador unificado
unified_sanitizer = UnifiedSanitizer()

# Alias para compatibilidad
DataSanitizer = UnifiedSanitizer