"""
Sistema de seguridad de contraseñas - Rexus.app

Proporciona funciones seguras para hash y verificación de contraseñas
usando PBKDF2 y bcrypt como mecanismos principales, con fallback a SHA-256 mejorado.
"""

import logging
from typing import Tuple, List, Optional
import hashlib
import secrets
import hmac
import re

logger = logging.getLogger(__name__)

# Intentar importar bcrypt, si no está disponible usar PBKDF2
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt no disponible, usando PBKDF2 como fallback")


class PasswordSecurity:
    """
    Sistema completo de seguridad para contraseñas
    """

    # Constantes de seguridad
    PBKDF2_ITERATIONS = 100000
    SALT_LENGTH = 32
    HASH_LENGTH = 64

    @staticmethod
    def generate_secure_salt(length: int = 32) -> str:
        """
        Genera un salt criptográficamente seguro.

        Args:
            length: Longitud del salt en bytes

        Returns:
            str: Salt en formato hexadecimal
        """
        return secrets.token_hex(length)

    @staticmethod
    def hash_password_secure(password: str) -> str:
        """
        Hashea una contraseña de forma segura usando el mejor método disponible.

        Args:
            password: Contraseña a hashear

        Returns:
            str: Hash de la contraseña con salt incluido
        """
        if not password:
            raise ValueError("La contraseña no puede estar vacía")

        try:
            if BCRYPT_AVAILABLE:
                # Usar bcrypt si está disponible
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                return f"bcrypt:{hashed.decode('utf-8')}"
            else:
                # Fallback a PBKDF2
                salt = PasswordSecurity.generate_secure_salt()
                hash_obj = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    PasswordSecurity.PBKDF2_ITERATIONS,
                    dklen=PasswordSecurity.HASH_LENGTH
                )
                hash_hex = hash_obj.hex()
                return f"pbkdf2:{salt}:{hash_hex}"

        except Exception as e:
            logger.error(f"Error al hashear contraseña: {str(e)}")
            raise

    @staticmethod
    def verify_password_secure(password: str, hashed: str) -> bool:
        """
        Verifica una contraseña contra su hash.

        Args:
            password: Contraseña a verificar
            hashed: Hash almacenado

        Returns:
            bool: True si la contraseña es correcta
        """
        if not password or not hashed:
            return False

        try:
            if hashed.startswith("bcrypt:"):
                if not BCRYPT_AVAILABLE:
                    logger.error("Hash bcrypt encontrado pero bcrypt no disponible")
                    return False

                hash_part = hashed[7:]  # Remover "bcrypt:"
                return bcrypt.checkpw(password.encode('utf-8'), hash_part.encode('utf-8'))

            elif hashed.startswith("pbkdf2:"):
                parts = hashed.split(":")
                if len(parts) != 3:
                    return False

                _, salt, stored_hash = parts

                # Recalcular hash
                hash_obj = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    PasswordSecurity.PBKDF2_ITERATIONS,
                    dklen=PasswordSecurity.HASH_LENGTH
                )
                computed_hash = hash_obj.hex()

                # Verificación segura contra timing attacks
                return hmac.compare_digest(computed_hash, stored_hash)

            else:
                # Hash legacy (SHA-256 simple) - para compatibilidad
                logger.warning("Hash legacy detectado, considere actualizar")
                return PasswordSecurity._verify_legacy_hash(password, hashed)

        except Exception as e:
            logger.error(f"Error al verificar contraseña: {str(e)}")
            return False

    @staticmethod
    def _verify_legacy_hash(password: str, hashed: str) -> bool:
        """
        Verifica hash legacy para compatibilidad hacia atrás.

        Args:
            password: Contraseña a verificar
            hashed: Hash legacy

        Returns:
            bool: True si coincide
        """
        try:
            # Simple SHA-256 con salt (método legacy)
            if ":" in hashed:
                salt, hash_part = hashed.split(":", 1)
                combined = (salt + password).encode('utf-8')
                computed = hashlib.sha256(combined).hexdigest()
                return hmac.compare_digest(computed, hash_part)
            else:
                # SHA-256 simple (muy inseguro)
                computed = hashlib.sha256(password.encode('utf-8')).hexdigest()
                return hmac.compare_digest(computed, hashed)
        except Exception:
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """
        Valida la fortaleza de una contraseña.

        Args:
            password: Contraseña a validar

        Returns:
            Tuple[bool, List[str]]: (es_válida, lista_de_errores)
        """
        errors = []

        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")

        if len(password) > 128:
            errors.append("La contraseña no puede exceder 128 caracteres")

        if not re.search(r'[a-z]', password):
            errors.append("Debe contener al menos una letra minúscula")

        if not re.search(r'[A-Z]', password):
            errors.append("Debe contener al menos una letra mayúscula")

        if not re.search(r'\d', password):
            errors.append("Debe contener al menos un número")

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            errors.append("Debe contener al menos un carácter especial")

        # Verificar patrones comunes débiles
        weak_patterns = [
            "123456", "password", "qwerty", "admin", "root",
            "123456789", "12345678", "111111", "abc123"
        ]
        if any(pattern in password.lower() for pattern in weak_patterns):
            errors.append("No debe contener patrones comunes débiles")

        # Verificar secuencias
        if re.search(r'(.)\1{2,}', password):  # Tres o más caracteres repetidos
            errors.append("No debe contener caracteres repetidos consecutivos")

        return len(errors) == 0, errors

    @staticmethod
    def generate_password_suggestions(base_password: Optional[str] = None) -> List[str]:
        """
        Genera sugerencias de contraseñas seguras.

        Args:
            base_password: Contraseña base para generar variaciones

        Returns:
            List[str]: Lista de sugerencias
        """
        suggestions = []

        if base_password:
            # Generar variaciones de la contraseña base
            base = re.sub(r'[^a-zA-Z0-9]', '', base_password)

            # Agregar números y símbolos
            suggestions.append(f"{base}2024!")
            suggestions.append(f"{base}#{secrets.randbelow(1000):03d}")
            suggestions.append(f"{base.upper()}!{secrets.randbelow(100):02d}")
        else:
            # Generar contraseñas aleatorias
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            for _ in range(5):
                pwd = ''.join(secrets.choice(chars) for _ in range(12))
                suggestions.append(pwd)

        return suggestions

    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        """
        Verifica si un hash necesita ser recalculado (para actualizar algoritmos).

        Args:
            hashed: Hash a verificar

        Returns:
            bool: True si necesita rehash
        """
        if not hashed:
            return True

        # Si no tiene prefijo, es un hash legacy
        if not hashed.startswith(("bcrypt:", "pbkdf2:")):
            return True

        # Si usa bcrypt pero bcrypt no está disponible, necesita rehash
        if hashed.startswith("bcrypt:") and not BCRYPT_AVAILABLE:
            return True

        return False

    @staticmethod
    def migrate_hash(password: str, old_hash: str) -> Optional[str]:
        """
        Migra un hash legacy a un formato más seguro.

        Args:
            password: Contraseña original
            old_hash: Hash legacy

        Returns:
            Optional[str]: Nuevo hash o None si falla
        """
        if PasswordSecurity.verify_password_secure(password, old_hash):
            try:
                return PasswordSecurity.hash_password_secure(password)
            except Exception as e:
                logger.error(f"Error al migrar hash: {str(e)}")

        return None


# Funciones de compatibilidad con el código existente
def hash_password(password: str) -> str:
    """Función de compatibilidad - usar hash_password_secure"""
    return PasswordSecurity.hash_password_secure(password)


def verify_password(password: str, hashed: str) -> bool:
    """Función de compatibilidad - usar verify_password_secure"""
    return PasswordSecurity.verify_password_secure(password, hashed)


def generate_secure_salt(length: int = 32) -> str:
    """Función de compatibilidad - usar generate_secure_salt"""
    return PasswordSecurity.generate_secure_salt(length)


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Función de compatibilidad - usar validate_password_strength"""
    return PasswordSecurity.validate_password_strength(password)
