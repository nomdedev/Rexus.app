"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Secure Logger - Logger con anonimización automática de datos sensibles
"""

import logging
import re
import hashlib
import os
from typing import Dict, Any, Optional, Union


class SensitiveDataMasker:
    """
    Clase para enmascarar datos sensibles en mensajes de log
    """

    def __init__(self):
        """Inicializar el enmascarador con patrones de datos sensibles"""
        self.hash_salt = "rexus_secure_logging_salt_2024"

        # Patrones de datos sensibles
        self.sensitive_patterns = [
            # Números de tarjeta de crédito
            {
                'name': 'credit_card',
                'pattern': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
                'replacement': '****-****-****-****'
            },
            # Emails (parcial)
            {
                'name': 'email',
                'pattern': re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'),
                'replacement': self._mask_email_lambda
            },
            # Números de teléfono
            {
                'name': 'phone',
                'pattern': re.compile(r'(\+?[\d\s\-\(\)]{10,15})'),
                'replacement': '***-***-****'
            },
            # Direcciones IP (mantener primeros 2 octetos)
            {
                'name': 'ip_address',
                'pattern': re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'),
                'replacement': self._mask_ip_lambda
            },
            # URLs con parámetros sensibles
            {
                'name': 'url_params',
                'pattern': re.compile(r'([?&](?:password|token|key|secret)[=])([^&\s]+)', re.IGNORECASE),
                'replacement': r'\1***MASKED***'
            },
            # JSON con datos sensibles
            {
                'name': 'json_password',
                'pattern': re.compile(r'("password"\s*:\s*")([^"]+)(")', re.IGNORECASE),
                'replacement': r'\1***MASKED***\3'
            },
            {
                'name': 'json_token',
                'pattern': re.compile(r'("(?:token|key|secret)"\s*:\s*")([^"]+)(")', re.IGNORECASE),
                'replacement': r'\1***MASKED***\3'
            },
            # Números de documento/identificación
            {
                'name': 'id_document',
                'pattern': re.compile(r'\b(\d{7,12})\b'),  # DNI, CI, etc.
                'replacement': self._hash_preserve_length_lambda
            }
        ]

    def _mask_email_lambda(self, match):
        """Lambda function para enmascarar emails"""
        username = match.group(1)
        domain = match.group(2)
        return f"{self._mask_email(username)}@{domain}"

    def _mask_ip_lambda(self, match):
        """Lambda function para enmascarar IPs"""
        return f"{match.group(1)}.{match.group(2)}.xxx.xxx"

    def _hash_preserve_length_lambda(self, match):
        """Lambda function para hash de documentos"""
        return self._hash_preserve_length(match.group(1))

    def _mask_email(self, username: str) -> str:
        """Enmascara parcialmente un username de email."""
        if len(username) <= 2:
            return "*" * len(username)
        elif len(username) <= 4:
            return username[0] + "*" * (len(username) - 2) + username[-1]
        else:
            return username[:2] + "*" * (len(username) - 4) + username[-2:]

    def _hash_preserve_length(self, value: str) -> str:
        """Hash que preserva la longitud original."""
        hash_full = hashlib.sha256((value + self.hash_salt).encode()).hexdigest()
        return hash_full[:len(value)]

    def mask_sensitive_data(self, message: str) -> str:
        """
        Enmascara datos sensibles en un mensaje de log.

        Args:
            message: Mensaje original

        Returns:
            Mensaje con datos sensibles enmascarados
        """
        if not message:
            return message

        masked_message = message

        for pattern_info in self.sensitive_patterns:
            pattern = pattern_info['pattern']
            replacement = pattern_info['replacement']

            if callable(replacement):
                # Replacement es una función
                masked_message = pattern.sub(replacement, masked_message)
            else:
                # Replacement es una string
                masked_message = pattern.sub(replacement, masked_message)

        return masked_message


class SecureLogRecord(logging.LogRecord):
    """LogRecord que enmascara automáticamente datos sensibles."""

    _masker = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicializar enmascarador si no existe
        if SecureLogRecord._masker is None:
            SecureLogRecord._masker = SensitiveDataMasker()

        # Aplicar enmascarado a mensaje
        if self.msg:
            self.msg = SecureLogRecord._masker.mask_sensitive_data(str(self.msg))

        # Aplicar enmascarado a argumentos
        if self.args:
            masked_args = []
            for arg in self.args:
                if isinstance(arg, str):
                    masked_args.append(SecureLogRecord._masker.mask_sensitive_data(arg))
                else:
                    masked_args.append(arg)
            self.args = tuple(masked_args)


class SecureFormatter(logging.Formatter):
    """Formatter que aplica enmascarado adicional."""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        # Asegurar que style sea válido para logging.Formatter
        valid_styles = ['%', '{', '$']
        if style not in valid_styles:
            style = '%'
        super().__init__(fmt, datefmt, style, validate)
        self.masker = SensitiveDataMasker()

    def format(self, record):
        """Formatea el record aplicando enmascarado adicional."""
        # Formatear normalmente
        formatted = super().format(record)

        # Aplicar enmascarado final por si acaso
        return self.masker.mask_sensitive_data(formatted)


class SecureFileHandler(logging.FileHandler):
    """FileHandler que asegura permisos seguros en archivos de log."""

    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        super().__init__(filename, mode, encoding, delay)

        # Establecer permisos restrictivos
        try:
            os.chmod(filename, 0o600)
        except OSError:
            # En Windows puede no funcionar, ignorar silenciosamente
            pass


class SecureLogger:
    """Logger principal con seguridad integrada."""

    def __init__(self, name: str, level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Usar nuestro LogRecord personalizado
        logging.setLogRecordFactory(SecureLogRecord)

        # Configurar handler si no existe
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Configura handlers seguros."""
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = SecureFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Handler de archivo (opcional - solo si existe configuración)
        try:
            # Intentar importar configuración de logging
            log_file = self._get_log_file_path()
            if log_file:
                file_handler = SecureFileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = SecureFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
        except (ImportError, AttributeError, OSError):
            # Fallback silencioso si no se puede configurar archivo
            pass

    def _get_log_file_path(self) -> Optional[str]:
        """Obtiene la ruta del archivo de log desde configuración"""
        try:
            # Intentar importar configuración del proyecto
            import ..core.config as config
            LOGGING_CONFIG = getattr(config, 'LOGGING_CONFIG', None)
            if LOGGING_CONFIG and isinstance(LOGGING_CONFIG, dict):
                return LOGGING_CONFIG.get('file_path')
        except ImportError:
            pass
        # Si no hay configuración, usar ruta por defecto
        return os.path.join(os.getcwd(), 'logs', 'secure.log')

    def debug(self, msg, *args, **kwargs):
        """Log debug con enmascarado."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log info con enmascarado."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log warning con enmascarado."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log error con enmascarado."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log critical con enmascarado."""
        self.logger.critical(msg, *args, **kwargs)

    def log_user_action(self, user: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Log específico para acciones de usuario."""
        details_str = ""
        if details:
            # Enmascarar detalles sensibles
            safe_details = {}
            for key, value in details.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret']):
                    safe_details[key] = "***MASKED***"
                else:
                    safe_details[key] = value
            details_str = f" | Details: {safe_details}"

        self.info(f"User: {user} | Action: {action}{details_str}")

    def log_security_event(self, event_type: str, severity: str, details: str):
        """Log específico para eventos de seguridad."""
        self.warning(f"SECURITY [{severity}] {event_type}: {details}")

    def log_data_access(self, user: str, table: str, operation: str, record_count: Optional[int] = None):
        """Log específico para acceso a datos."""
        count_str = f" | Records: {record_count}" if record_count else ""
        self.info(f"DATA_ACCESS | User: {user} | Table: {table} | Op: {operation}{count_str}")


# Factory function para obtener logger seguro
def get_secure_logger(name: str, level: str = 'INFO') -> SecureLogger:
    """
    Factory para obtener un logger seguro.

    Args:
        name: Nombre del logger
        level: Nivel de logging

    Returns:
        SecureLogger configurado
    """
    return SecureLogger(name, level)


# Instancia global para uso rápido
secure_logger = get_secure_logger('rexus')


# Funciones de conveniencia
def log_info(msg: str, *args, **kwargs):
    """Log info global."""
    secure_logger.info(msg, *args, **kwargs)


def log_error(msg: str, *args, **kwargs):
    """Log error global."""
    secure_logger.error(msg, *args, **kwargs)


def log_warning(msg: str, *args, **kwargs):
    """Log warning global."""
    secure_logger.warning(msg, *args, **kwargs)


def log_user_action(user: str, action: str, details: Optional[Dict[str, Any]] = None):
    """Log acción de usuario global."""
    secure_logger.log_user_action(user, action, details)


def log_security_event(event_type: str, severity: str, details: str):
    """Log evento de seguridad global."""
    secure_logger.log_security_event(event_type, severity, details)
