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
import decimal
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("input_validator")
except ImportError:
    import logging
    logger = logging.getLogger("input_validator")


class InputValidator:
    """
    Validador de entrada robusto con patrones de seguridad.
    
    Características:
    - Prevención de SQL injection
    - Filtrado XSS
    - Validación de tipos de datos
    - Sanitización automática
    - Logging de intentos de ataque
    """

    def __init__(self):
        """Inicializa el validador con patrones de seguridad."""
        self._init_security_patterns()
        self._init_validation_rules()
        self.max_input_length = 10000  # Límite general
        self.strict_mode = True  # Modo estricto por defecto

    def _init_security_patterns(self):
        """Inicializa patrones para detectar ataques."""
        # Patrones SQL injection
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",  # Comentarios SQL
            r"(\bOR\b.*\b=\b.*\bOR\b)",  # OR injection
            r"(\bunion\b.*\bselect\b)",  # UNION attacks
            r"(\bAND\b.*\b1\b.*=.*\b1\b)",  # Boolean injection
            r"([\'\"][\s]*[\;])",  # Quote + semicolon
            r"(\bexec\b|\bsp_\b|\bxp_\b)",  # Stored procedures
            r"(\bINFORMATION_SCHEMA\b|\bSYSOBJECTS\b)",  # Schema discovery
        ]

        # Patrones XSS
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<applet[^>]*>",
            r"<meta[^>]*>",
            r"<link[^>]*>",
            r"<style[^>]*>.*?</style>",
        ]

        # Patrones de path traversal
        self.path_traversal_patterns = [
            r"\.\.[\\/]",
            r"[\\/]\.\.[\\/]",
            r"%2e%2e[\\/]",
            r"\.\.%2f",
            r"%2e%2e%2f",
        ]

        # Patrones de command injection
        self.command_injection_patterns = [
            r"[\;\|\&\$\`]",
            r"(cmd|command|sh|bash|powershell)",
            r"(wget|curl|nc|netcat)",
            r"(\|\s*(cat|type|dir|ls))",
        ]

    def _init_validation_rules(self):
        """Inicializa reglas de validación por tipo de campo."""
        self.validation_rules = {
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'max_length': 254,
                'required_chars': ['@', '.'],
                'forbidden_chars': ['<', '>', '"', "'"],
            },
            'phone': {
                'pattern': r'^\+?[\d\s\-\(\)]{7,15}$',
                'max_length': 20,
                'allowed_chars': '+0123456789()-. ',
            },
            'name': {
                'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\.]{1,100}$',
                'max_length': 100,
                'min_length': 1,
                'forbidden_chars': ['<', '>', '"', "'", ';', '&'],
            },
            'code': {
                'pattern': r'^[A-Z0-9\-_]{1,20}$',
                'max_length': 20,
                'min_length': 1,
                'allowed_chars': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_',
            },
            'description': {
                'max_length': 1000,
                'forbidden_chars': ['<script', '</script>', 'javascript:', 'vbscript:'],
            },
            'numeric': {
                'pattern': r'^\d+(\.\d{1,2})?$',
                'max_length': 15,
                'allowed_chars': '0123456789.',
            },
            'currency': {
                'pattern': r'^\d+(\.\d{1,2})?$',
                'max_length': 12,
                'min_value': 0,
                'max_value': 999999999.99,
            },
            'date': {
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'format': '%Y-%m-%d',
            },
            'url': {
                'pattern': r'^https?://[^\s/$.?#].[^\s]*$',
                'max_length': 2083,
                'allowed_schemes': ['http', 'https'],
            },
            'filename': {
                'pattern': r'^[a-zA-Z0-9._\-]{1,255}$',
                'max_length': 255,
                'forbidden_chars': ['<', '>', ':', '"', '|', '?', '*', '/', '\\'],
                'forbidden_extensions': ['.exe', '.bat', '.cmd', '.scr', '.com', '.pif'],
            }
        }

    def validate_input(self, value: Any, field_type: str, field_name: str = "campo", 
                      additional_rules: Optional[Dict] = None) -> Tuple[bool, str, Any]:
        """
        Valida una entrada del usuario según el tipo especificado.

        Args:
            value: Valor a validar
            field_type: Tipo de campo ('email', 'name', 'numeric', etc.)
            field_name: Nombre del campo para mensajes de error
            additional_rules: Reglas adicionales específicas

        Returns:
            Tuple[bool, str, Any]: (es_válido, mensaje_error, valor_sanitizado)
        """
        try:
            # Verificar si es None/vacío
            if value is None or value == "":
                if additional_rules and additional_rules.get('required', False):
                    return False, f"{field_name} es requerido", None
                return True, "", ""

            # Convertir a string para validación
            str_value = str(value).strip()

            # Verificar longitud máxima general
            if len(str_value) > self.max_input_length:
                logger.warning(f"Entrada demasiado larga detectada en {field_name}: {len(str_value)} caracteres")
                return False, f"{field_name} excede la longitud máxima permitida", None

            # Detectar ataques de seguridad
            is_attack, attack_type = self._detect_security_threats(str_value, field_name)
            if is_attack:
                logger.error(f"Intento de ataque detectado en {field_name}: {attack_type}")
                return False, f"Entrada no válida detectada en {field_name}", None

            # Aplicar validación específica por tipo
            if field_type in self.validation_rules:
                is_valid, error_msg, sanitized_value = self._validate_field_type(
                    str_value, field_type, field_name, additional_rules
                )
                if not is_valid:
                    return False, error_msg, None
                return True, "", sanitized_value
            else:
                # Tipo no reconocido - aplicar sanitización básica
                sanitized = self._basic_sanitize(str_value)
                logger.debug(f"Tipo de campo no reconocido: {field_type}, aplicando sanitización básica")
                return True, "", sanitized

        except Exception as e:
            logger.error(f"Error validando entrada {field_name}: {e}")
            return False, f"Error interno validando {field_name}", None

    def _detect_security_threats(self, value: str, field_name: str) -> Tuple[bool, str]:
        """Detecta amenazas de seguridad comunes."""
        value_lower = value.lower()

        # Verificar SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Patrón SQL injection detectado en {field_name}: {pattern}")
                return True, "SQL Injection"

        # Verificar XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Patrón XSS detectado en {field_name}: {pattern}")
                return True, "XSS Attack"

        # Verificar path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Patrón path traversal detectado en {field_name}: {pattern}")
                return True, "Path Traversal"

        # Verificar command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Patrón command injection detectado en {field_name}: {pattern}")
                return True, "Command Injection"

        return False, ""

    def _validate_field_type(self, value: str, field_type: str, field_name: str, 
                           additional_rules: Optional[Dict]) -> Tuple[bool, str, Any]:
        """Valida un campo según su tipo específico."""
        rules = self.validation_rules[field_type].copy()
        
        # Merge additional rules
        if additional_rules:
            rules.update(additional_rules)

        # Verificar longitud mínima
        if 'min_length' in rules and len(value) < rules['min_length']:
            return False, f"{field_name} debe tener al menos {rules['min_length']} caracteres", None

        # Verificar longitud máxima
        if 'max_length' in rules and len(value) > rules['max_length']:
            return False, f"{field_name} excede la longitud máxima de {rules['max_length']} caracteres", None

        # Verificar patrón regex
        if 'pattern' in rules and not re.match(rules['pattern'], value):
            return False, f"{field_name} no tiene el formato correcto", None

        # Verificar caracteres permitidos
        if 'allowed_chars' in rules:
            for char in value:
                if char not in rules['allowed_chars']:
                    return False, f"{field_name} contiene caracteres no permitidos", None

        # Verificar caracteres prohibidos
        if 'forbidden_chars' in rules:
            for forbidden in rules['forbidden_chars']:
                if forbidden in value:
                    return False, f"{field_name} contiene caracteres no permitidos", None

        # Validaciones específicas por tipo
        if field_type == 'email':
            return self._validate_email(value, field_name)
        elif field_type == 'numeric' or field_type == 'currency':
            return self._validate_numeric(value, field_name, rules)
        elif field_type == 'date':
            return self._validate_date(value, field_name, rules)
        elif field_type == 'url':
            return self._validate_url(value, field_name)
        elif field_type == 'filename':
            return self._validate_filename(value, field_name, rules)
        else:
            # Sanitización básica para otros tipos
            sanitized = self._basic_sanitize(value)
            return True, "", sanitized

    def _validate_email(self, value: str, field_name: str) -> Tuple[bool, str, str]:
        """Validación específica para emails."""
        # Verificar formato básico
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, f"{field_name} no es un email válido", None

        # Verificar longitud de partes
        local, domain = value.rsplit('@', 1)
        if len(local) > 64:
            return False, f"La parte local del {field_name} es demasiado larga", None
        if len(domain) > 253:
            return False, f"El dominio del {field_name} es demasiado largo", None

        # Sanitizar
        sanitized = html.escape(value.lower().strip())
        return True, "", sanitized

    def _validate_numeric(self, value: str, field_name: str, rules: Dict) -> Tuple[bool, str, float]:
        """Validación específica para números."""
        try:
            numeric_value = float(value)
            
            # Verificar rango si está especificado
            if 'min_value' in rules and numeric_value < rules['min_value']:
                return False, f"{field_name} debe ser mayor o igual a {rules['min_value']}", None
            if 'max_value' in rules and numeric_value > rules['max_value']:
                return False, f"{field_name} debe ser menor o igual a {rules['max_value']}", None

            # Para currency, redondear a 2 decimales
            if 'currency' in rules or rules.get('round_decimals'):
                numeric_value = round(numeric_value, 2)

            return True, "", numeric_value
        except ValueError:
            return False, f"{field_name} debe ser un número válido", None

    def _validate_date(self, value: str, field_name: str, rules: Dict) -> Tuple[bool, str, date]:
        """Validación específica para fechas."""
        try:
            date_format = rules.get('format', '%Y-%m-%d')
            parsed_date = datetime.strptime(value, date_format).date()
            
            # Verificar rango de fechas razonable
            min_date = date(1900, 1, 1)
            max_date = date(2100, 12, 31)
            
            if parsed_date < min_date or parsed_date > max_date:
                return False, f"{field_name} debe estar entre {min_date} y {max_date}", None

            return True, "", parsed_date
        except ValueError:
            return False, f"{field_name} no es una fecha válida", None

    def _validate_url(self, value: str, field_name: str) -> Tuple[bool, str, str]:
        """Validación específica para URLs."""
        # Verificar esquema permitido
        if not (value.startswith('http://') or value.startswith('https://')):
            return False, f"{field_name} debe comenzar con http:// o https://", None

        # Verificar caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
        for char in dangerous_chars:
            if char in value:
                return False, f"{field_name} contiene caracteres no permitidos", None

        # Sanitizar
        sanitized = html.escape(value.strip())
        return True, "", sanitized

    def _validate_filename(self, value: str, field_name: str, rules: Dict) -> Tuple[bool, str, str]:
        """Validación específica para nombres de archivo."""
        # Verificar extensiones prohibidas
        if 'forbidden_extensions' in rules:
            file_ext = Path(value).suffix.lower()
            if file_ext in rules['forbidden_extensions']:
                return False, f"Tipo de archivo no permitido para {field_name}", None

        # Verificar caracteres de sistema
        system_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in system_chars:
            if char in value:
                return False, f"{field_name} contiene caracteres no válidos para archivos", None

        # Sanitizar
        sanitized = re.sub(r'[^\w\-_\.]', '_', value)
        return True, "", sanitized

    def _basic_sanitize(self, value: str) -> str:
        """Sanitización básica para campos genéricos."""
        # Escape HTML
        sanitized = html.escape(value)
        
        # Remover caracteres de control
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Normalizar espacios
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized

    def validate_form_data(self, form_data: Dict[str, Any], 
                          validation_schema: Dict[str, Dict]) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
        """
        Valida un formulario completo según un esquema de validación.

        Args:
            form_data: Datos del formulario
            validation_schema: Esquema de validación por campo

        Returns:
            Tuple[bool, Dict[str, str], Dict[str, Any]]: (es_válido, errores, datos_sanitizados)
        """
        errors = {}
        sanitized_data = {}
        is_valid = True

        for field_name, field_value in form_data.items():
            if field_name in validation_schema:
                field_rules = validation_schema[field_name]
                field_type = field_rules.get('type', 'text')
                
                valid, error_msg, sanitized_value = self.validate_input(
                    field_value, field_type, field_name, field_rules
                )
                
                if not valid:
                    errors[field_name] = error_msg
                    is_valid = False
                else:
                    sanitized_data[field_name] = sanitized_value
            else:
                # Campo no especificado en esquema - sanitización básica
                sanitized_data[field_name] = self._basic_sanitize(str(field_value))

        return is_valid, errors, sanitized_data

    def create_validation_schema(self, **field_definitions) -> Dict[str, Dict]:
        """
        Crea un esquema de validación de forma simplificada.

        Example:
            schema = validator.create_validation_schema(
                nombre={'type': 'name', 'required': True},
                email={'type': 'email', 'required': True},
                precio={'type': 'currency', 'min_value': 0, 'max_value': 999999}
            )
        """
        return field_definitions

    def set_strict_mode(self, strict: bool):
        """Activa/desactiva modo estricto de validación."""
        self.strict_mode = strict
        logger.info(f"Modo estricto de validación: {'activado' if strict else 'desactivado'}")

    def get_validation_rules(self, field_type: str) -> Optional[Dict]:
        """Obtiene las reglas de validación para un tipo de campo."""
        return self.validation_rules.get(field_type)

    def add_custom_rule(self, field_type: str, rules: Dict):
        """Agrega reglas personalizadas de validación."""
        self.validation_rules[field_type] = rules
        logger.debug(f"Reglas personalizadas agregadas para tipo: {field_type}")


# Instancia global del validador
input_validator = InputValidator()


def validate_user_input(value: Any, field_type: str, field_name: str = "campo", 
                       **kwargs) -> Tuple[bool, str, Any]:
    """
    Función de conveniencia para validación rápida.
    
    Args:
        value: Valor a validar
        field_type: Tipo de campo
        field_name: Nombre del campo
        **kwargs: Reglas adicionales
    
    Returns:
        Tuple[bool, str, Any]: (es_válido, mensaje_error, valor_sanitizado)
    """
    return input_validator.validate_input(value, field_type, field_name, kwargs)


def validate_form(form_data: Dict[str, Any], schema: Dict[str, Dict]) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
    """
    Función de conveniencia para validación de formularios.
    
    Args:
        form_data: Datos del formulario
        schema: Esquema de validación
    
    Returns:
        Tuple[bool, Dict[str, str], Dict[str, Any]]: (es_válido, errores, datos_sanitizados)
    """
    return input_validator.validate_form_data(form_data, schema)


# Decorador para validación automática de métodos
def validate_inputs(validation_schema: Dict[str, Dict]):
    """
    Decorador para validación automática de entradas en métodos.
    
    Example:
        @validate_inputs({
            'nombre': {'type': 'name', 'required': True},
            'email': {'type': 'email', 'required': True}
        })
        def crear_usuario(self, nombre, email):
            # Los argumentos ya están validados y sanitizados
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obtener argumentos del método (excluyendo 'self')
            func_args = func.__code__.co_varnames[1:func.__code__.co_argcount]
            arg_values = dict(zip(func_args, args[1:]))  # Excluir 'self'
            arg_values.update(kwargs)
            
            # Validar argumentos
            is_valid, errors, sanitized_data = input_validator.validate_form_data(arg_values, validation_schema)
            
            if not is_valid:
                error_msg = "; ".join(errors.values())
                raise ValueError(f"Datos de entrada no válidos: {error_msg}")
            
            # Llamar función original con datos sanitizados
            new_kwargs = {k: v for k, v in sanitized_data.items() if k not in func_args[:len(args)-1]}
            new_args = args[:1] + tuple(sanitized_data.get(arg, args[i+1]) for i, arg in enumerate(func_args[:len(args)-1]))
            
            return func(*new_args, **new_kwargs)
        return wrapper
    return decorator