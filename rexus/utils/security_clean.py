#!/usr/bin/env python3
"""
Utilidades de seguridad para Rexus
Implementa funciones de seguridad críticas
"""

import hashlib
import logging
import re
import secrets
from typing import Optional, Dict, Any


class SecurityUtils:
    """
    Utilidades de seguridad para Rexus.app
    """

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hashea una contraseña usando PBKDF2

        Args:
            password: Contraseña a hashear
            salt: Salt opcional, se genera uno si no se proporciona

        Returns:
            str: Hash de la contraseña en formato salt:hash
        """
        if not password:
            raise ValueError("La contraseña no puede estar vacía")

        if salt is None:
            salt = secrets.token_hex(16)

        # Usar PBKDF2 con SHA-256
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Número de iteraciones
        )

        return f"{salt}:{hash_obj.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica una contraseña contra su hash

        Args:
            password: Contraseña a verificar
            hashed_password: Hash almacenado en formato salt:hash

        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            salt, stored_hash = hashed_password.split(':', 1)

            # Calcular hash de la contraseña proporcionada
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()

            # Comparación segura contra timing attacks
            return secrets.compare_digest(computed_hash, stored_hash)

        except (ValueError, TypeError, AttributeError, UnicodeDecodeError):
            # Error en verificación de contraseña
            return False

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitiza entrada de usuario para prevenir XSS"""
        if not user_input:
            return ""

        # Caracteres peligrosos comunes
        dangerous_chars = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "&": "&amp;",
            "/": "&#x2F;",
        }

        # Reemplazar caracteres peligrosos
        sanitized = user_input
        for char, replacement in dangerous_chars.items():
            sanitized = sanitized.replace(char, replacement)

        # Remover scripts obvios
        script_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"expression\s*\(",
            r"eval\s*\(",
            r"alert\s*\(",
        ]

        for pattern in script_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_sql_identifier(identifier: str) -> bool:
        """Valida que un identificador SQL sea seguro"""
        if not identifier:
            return False
        # Solo letras, números y guiones bajos, no puede empezar con número
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
        return bool(re.match(pattern, identifier)) and len(identifier) <= 64

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Genera un token seguro aleatorio"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Valida la fortaleza de una contraseña"""
        result = {"valid": False, "score": 0, "issues": []}

        if not password:
            result["issues"].append("Contraseña vacía")
            return result

        # Criterios de validación
        if len(password) < 8:
            result["issues"].append("Debe tener al menos 8 caracteres")
        else:
            result["score"] += 1

        if not re.search(r"[a-z]", password):
            result["issues"].append("Debe contener al menos una minúscula")
        else:
            result["score"] += 1

        if not re.search(r"[A-Z]", password):
            result["issues"].append("Debe contener al menos una mayúscula")
        else:
            result["score"] += 1

        if not re.search(r"\d", password):
            result["issues"].append("Debe contener al menos un número")
        else:
            result["score"] += 1

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["issues"].append("Debe contener al menos un carácter especial")
        else:
            result["score"] += 1

        result["valid"] = result["score"] >= 4
        return result

    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """
        Genera un nombre de archivo seguro

        Args:
            original_filename: Nombre original del archivo

        Returns:
            str: Nombre seguro para el archivo
        """
        if not original_filename:
            return SecurityUtils.generate_token(16)

        # Extraer extensión
        parts = original_filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            # Sanitizar nombre y extensión
            safe_name = re.sub(r'[^\w\-_\.]', '_', name)
            safe_ext = re.sub(r'[^\w]', '', ext)
            return f"{safe_name}.{safe_ext}"
        else:
            # Sin extensión
            safe_name = re.sub(r'[^\w\-_]', '_', original_filename)
            return safe_name

    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: list) -> bool:
        """
        Valida que el tipo de archivo sea permitido

        Args:
            filename: Nombre del archivo
            allowed_extensions: Lista de extensiones permitidas

        Returns:
            bool: True si el tipo es permitido
        """
        if not filename or not allowed_extensions:
            return False

        # Extraer extensión
        parts = filename.rsplit('.', 1)
        if len(parts) != 2:
            return False

        ext = parts[1].lower()
        return ext in [e.lower().lstrip('.') for e in allowed_extensions]


def get_security_logger():
    """Obtiene logger configurado para eventos de seguridad"""
    logger = logging.getLogger("rexus.security")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_security_event(event_type: str, details: str, user: Optional[str] = None):
    """Registra evento de seguridad"""
    logger = get_security_logger()
    message = f"[{event_type}] {details}"
    if user:
        message += f" | Usuario: {user}"
    logger.info(message)


# Instancia global para uso fácil
security_utils = SecurityUtils()
