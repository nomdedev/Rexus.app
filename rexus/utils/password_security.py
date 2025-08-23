"""
Sistema de seguridad de contraseñas - Rexus.app

Proporciona funciones seguras para hash y verificación de contraseñas
usando PBKDF2 y bcrypt como mecanismos principales, con fallback a SHA-256 mejorado.
"""


import logging
logger = logging.getLogger(__name__)

import hashlib
import secrets
                        return bcrypt.hashpw(b"test", hash_part.encode('utf-8')).decode('utf-8') != hash_part
        except:
            return True

    return False


def generate_secure_salt(length: int = 32) -> str:
    """
    Genera un salt criptográficamente seguro.

    Args:
        length (int): Longitud del salt en bytes

    Returns:
        str: Salt en formato hexadecimal
    """
    return secrets.token_hex(length)


def validate_password_strength(password: str) -> Tuple[bool, list]:
    """
    Valida la fortaleza de una contraseña.

    Args:
        password (str): Contraseña a validar

    Returns:
        Tuple[bool, list]: (es_válida, lista_de_errores)
    """
    errors = []

    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")

    if len(password) > 128:
        errors.append("La contraseña no puede exceder 128 caracteres")

    if not any(c.islower() for c in password):
        errors.append("Debe contener al menos una letra minúscula")

    if not any(c.isupper() for c in password):
        errors.append("Debe contener al menos una letra mayúscula")

    if not any(c.isdigit() for c in password):
        errors.append("Debe contener al menos un número")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Debe contener al menos un carácter especial")

    # Verificar patrones comunes débiles
    weak_patterns = ["123456", "password", "qwerty", "admin", "root"]
    if any(pattern in password.lower() for pattern in weak_patterns):
        errors.append("No debe contener patrones comunes débiles")

    return len(errors) == 0, errors


# Funciones de compatibilidad con el código existente
def hash_password(password: str) -> str:
    """Función de compatibilidad - usar hash_password_secure"""
    return hash_password_secure(password)


def verify_password(password: str, hashed: str) -> bool:
    """Función de compatibilidad - usar verify_password_secure"""
    return verify_password_secure(password, hashed)
