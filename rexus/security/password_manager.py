"""
MIT License

Copyright (c) 2024 Rexus.app

Password Manager - Sistema seguro de gestión de contraseñas con bcrypt
"""

import secrets
import hashlib
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


class PasswordManager:
    """Gestor seguro de contraseñas con bcrypt y políticas de seguridad."""

    def __init__(self):
        """Inicializar gestor de contraseñas."""
        self.bcrypt_available = False
        self.salt_rounds = 12

        # Intentar importar bcrypt
        try:
            import bcrypt
            self.bcrypt = bcrypt
            self.bcrypt_available = True
        except ImportError:
            # Fallback a hashlib con salt para desarrollo
            self.bcrypt_available = False
            print("WARNING: bcrypt no disponible, usando hashlib como fallback")

    def hash_password(self, password: str) -> str:
        """
        Genera hash seguro de una contraseña.

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña
        """
        if self.bcrypt_available:
            # Usar bcrypt (recomendado para producción)
            password_bytes = password.encode('utf-8')
            salt = self.bcrypt.gensalt(rounds=self.salt_rounds)
            hashed = self.bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        else:
            # Fallback con múltiples rounds de hash
            salt = secrets.token_hex(16)
            return self._fallback_hash(password, salt)

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.

        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado

        Returns:
            True si la contraseña es correcta
        """
        if self.bcrypt_available and hashed.startswith('$2b$'):
            # Hash de bcrypt
            try:
                password_bytes = password.encode('utf-8')
                hashed_bytes = hashed.encode('utf-8')
                return self.bcrypt.checkpw(password_bytes, hashed_bytes)
            except Exception:
                return False
        else:
            # Fallback hash
            if ':' not in hashed:
                return False

            try:
                salt, stored_hash = hashed.split(':', 1)
                computed_hash = self._fallback_hash(password, salt)
                return computed_hash == hashed
            except Exception:
                return False

    def _fallback_hash(self, password: str, salt: str) -> str:
        """
        Fallback de hashing cuando bcrypt no está disponible.

        Args:
            password: Contraseña
            salt: Salt

        Returns:
            Hash en formato salt:hash
        """
        # Múltiples rounds de hashing para aumentar la seguridad
        result = password + salt

        for _ in range(10000):  # 10,000 iterations
            result = hashlib.sha256(result.encode()).hexdigest()

        return f"{salt}:{result}"

    def generate_secure_password(self, length: int = 16) -> str:
        """
        Genera una contraseña segura aleatoria.

        Args:
            length: Longitud de la contraseña

        Returns:
            Contraseña segura
        """
        # Caracteres seguros (excluyendo caracteres ambiguos)
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña.

        Args:
            password: Contraseña a validar

        Returns:
            Tupla (es_válida, mensaje_error)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if len(password) > 128:
            return False, "La contraseña no puede exceder 128 caracteres"

        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        complexity_score = sum([has_upper, has_lower, has_digit, has_special])

        if complexity_score < 3:
            return False, "La contraseña debe contener al menos 3 de: mayúsculas, minúsculas, números, símbolos"

        # Verificar patrones comunes
        common_patterns = [
            "123456", "password", "admin", "qwerty", "letmein",
            "welcome", "monkey", "dragon", "master", "shadow"
        ]

        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                return False, f"La contraseña contiene un patrón común: {pattern}"

        return True, "Contraseña válida"

    def is_password_compromised(self, password: str) -> bool:
        """
        Verifica si una contraseña está en listas de contraseñas comprometidas.

        Args:
            password: Contraseña a verificar

        Returns:
            True si la contraseña está comprometida

        Note:
            Esta implementación es básica. En producción se recomendaría
            usar APIs como HaveIBeenPwned de forma segura.
        """
        # Lista básica de contraseñas más comunes
        compromised_passwords = {
            "123456", "password", "123456789", "12345678", "12345",
            "1234567", "1234567890", "qwerty", "abc123", "password123",
            "admin", "letmein", "welcome", "monkey", "login",
            "master", "hello", "dragon", "shadow", "jesus"
        }

        return password.lower() in compromised_passwords

    def get_password_entropy(self, password: str) -> float:
        """
        Calcula la entropía de una contraseña.

        Args:
            password: Contraseña a analizar

        Returns:
            Entropía en bits
        """
        import math

        # Calcular espacio de caracteres
        charset_size = 0

        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            charset_size += 32

        if charset_size == 0:
            return 0.0

        # Entropía = log2(charset_size^length)
        entropy = len(password) * math.log2(charset_size)
        return entropy

    def create_password_hash_with_metadata(self,
password: str,
        user_id: str) -> Dict[str,
        Any]:
        """
        Crea hash de contraseña con metadatos de seguridad.

        Args:
            password: Contraseña en texto plano
            user_id: ID del usuario

        Returns:
            Diccionario con hash y metadatos
        """
        # Validar fortaleza
        is_strong, message = self.validate_password_strength(password)
        if not is_strong:
            raise ValueError(f"Contraseña débil: {message}")

        # Verificar si está comprometida
        if self.is_password_compromised(password):
            raise ValueError("La contraseña está en listas de contraseñas comprometidas")

        # Generar hash
        password_hash = self.hash_password(password)

        # Metadatos
        metadata = {
            'hash': password_hash,
            'created_at': datetime.now().isoformat(),
            'algorithm': 'bcrypt' if self.bcrypt_available else 'fallback_pbkdf2',
            'strength_score': self.get_password_entropy(password),
            'user_id': user_id,
            'version': '1.0'
        }

        return metadata


# Instancia global del gestor de contraseñas
password_manager: Optional[PasswordManager] = None


def init_password_manager():
    """Inicializa el gestor de contraseñas."""
    global password_manager
    password_manager = PasswordManager()


def get_password_manager() -> PasswordManager:
    """
    Obtiene la instancia del gestor de contraseñas.

    Returns:
        Instancia de PasswordManager
    """
    if password_manager is None:
        init_password_manager()

    return password_manager


def hash_password(password: str) -> str:
    """Función de conveniencia para hacer hash de contraseña."""
    return get_password_manager().hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Función de conveniencia para verificar contraseña."""
    return get_password_manager().verify_password(password, hashed)


def generate_secure_password(length: int = 16) -> str:
    """Función de conveniencia para generar contraseña segura."""
    return get_password_manager().generate_secure_password(length)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar fortaleza de contraseña."""
    return get_password_manager().validate_password_strength(password)
