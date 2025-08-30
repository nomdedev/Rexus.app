"""
Rexus.app - Utilidades de Seguridad

Utilidades para manejo seguro de contraseñas y validaciones de seguridad.
"""

import hashlib
import hmac
import secrets
from typing import Optional, Tuple


class SecurityUtils:
    """
    Utilidades de seguridad para el manejo de contraseñas y validaciones.
    """

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hashea una contraseña usando PBKDF2 con salt.

        Args:
            password: Contraseña a hashear
            salt: Salt opcional, se genera uno si no se proporciona

        Returns:
            Hash de la contraseña en formato salt:hash
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Usar PBKDF2 con SHA-256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Número de iteraciones
        )

        return f"{salt}:{key.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.

        Args:
            password: Contraseña a verificar
            hashed: Hash almacenado en formato salt:hash

        Returns:
            True si la contraseña es correcta
        """
        try:
            salt, stored_hash = hashed.split(':', 1)
            computed_hash = SecurityUtils.hash_password(password, salt)
            return hmac.compare_digest(computed_hash, hashed)
        except ValueError:
            # Hash malformado
            return False

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Genera un token seguro aleatorio.

        Args:
            length: Longitud del token en bytes

        Returns:
            Token hexadecimal
        """
        return secrets.token_hex(length)

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña.

        Args:
            password: Contraseña a validar

        Returns:
            Tupla (es_valida, mensaje)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula"

        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula"

        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"

        # Verificar contraseñas comunes (lista básica)
        common_passwords = ['password', '123456', 'admin', 'user', 'login']
        if password.lower() in common_passwords:
            return False, "La contraseña es demasiado común"

        return True, "Contraseña válida"

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitiza entrada de usuario para prevenir inyección.

        Args:
            input_str: Cadena a sanitizar

        Returns:
            Cadena sanitizada
        """
        # Remover caracteres potencialmente peligrosos
        dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        sanitized = input_str

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()
