"""
Sistema de seguridad de contraseñas - Rexus.app

Proporciona funciones seguras para hash y verificación de contraseñas
usando PBKDF2 y bcrypt como mecanismos principales, con fallback a SHA-256 mejorado.
"""

import hashlib
import secrets
import os
from typing import Optional, Tuple

# Importaciones condicionales para soporte múltiple
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, HashingError
    ARGON2_AVAILABLE = True
    ph = PasswordHasher()
except ImportError:
    ARGON2_AVAILABLE = False


class PasswordSecurityError(Exception):
    """Excepción para errores de seguridad de contraseñas"""
    pass


def hash_password_secure(password: str, method: str = "auto") -> str:
    """
    Genera un hash seguro de contraseña usando el mejor método disponible.
    
    Args:
        password (str): Contraseña en texto plano
        method (str): Método preferido ("bcrypt", "argon2", "pbkdf2", "auto")
        
    Returns:
        str: Hash seguro con prefijo del método usado
        
    Raises:
        PasswordSecurityError: Si no se puede generar el hash
    """
    if not password:
        raise PasswordSecurityError("La contraseña no puede estar vacía")
    
    if len(password) < 4:
        raise PasswordSecurityError("La contraseña debe tener al menos 4 caracteres")
    
    # Selección automática del mejor método disponible
    if method == "auto":
        if ARGON2_AVAILABLE:
            method = "argon2"
        elif BCRYPT_AVAILABLE:
            method = "bcrypt"
        else:
            method = "pbkdf2"
    
    try:
        # Argon2 - El más moderno y seguro
        if method == "argon2" and ARGON2_AVAILABLE:
            hash_result = ph.hash(password)
            return f"argon2${hash_result}"
        
        # bcrypt - Muy seguro y ampliamente usado
        elif method == "bcrypt" and BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt(rounds=12)  # 12 rounds = buen balance seguridad/rendimiento
            hash_result = bcrypt.hashpw(password.encode('utf-8'), salt)
            return f"bcrypt${hash_result.decode('utf-8')}"
        
        # PBKDF2 - Fallback seguro sin dependencias externas
        elif method == "pbkdf2" or method == "auto":
            salt = secrets.token_hex(32)  # 256-bit salt
            iterations = 100000  # Recomendación OWASP 2023
            hash_result = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                             salt.encode('utf-8'), iterations)
            return f"pbkdf2$sha256${iterations}${salt}${hash_result.hex()}"
        
        else:
            raise PasswordSecurityError(f"Método '{method}' no disponible o no soportado")
            
    except Exception as e:
        raise PasswordSecurityError(f"Error generando hash: {str(e)}")


def verify_password_secure(password: str, stored_hash: str) -> bool:
    """
    Verifica una contraseña contra un hash almacenado.
    
    Args:
        password (str): Contraseña en texto plano
        stored_hash (str): Hash almacenado con prefijo del método
        
    Returns:
        bool: True si la contraseña es correcta
        
    Raises:
        PasswordSecurityError: Si hay error en la verificación
    """
    if not password or not stored_hash:
        return False
    
    try:
        # Detectar el método por el prefijo
        if stored_hash.startswith("argon2$"):
            if not ARGON2_AVAILABLE:
                raise PasswordSecurityError("Argon2 no disponible para verificación")
            hash_part = stored_hash[7:]  # Remover prefijo "argon2$"
            try:
                ph.verify(hash_part, password)
                return True
            except VerifyMismatchError:
                return False
        
        elif stored_hash.startswith("bcrypt$"):
            if not BCRYPT_AVAILABLE:
                raise PasswordSecurityError("bcrypt no disponible para verificación")
            hash_part = stored_hash[7:]  # Remover prefijo "bcrypt$"
            return bcrypt.checkpw(password.encode('utf-8'), hash_part.encode('utf-8'))
        
        elif stored_hash.startswith("pbkdf2$"):
            parts = stored_hash.split('$')
            if len(parts) != 5:
                raise PasswordSecurityError("Formato PBKDF2 inválido")
            
            _, algorithm, iterations_str, salt, stored_hash_hex = parts
            iterations = int(iterations_str)
            
            # Verificar con PBKDF2
            computed_hash = hashlib.pbkdf2_hmac(
                algorithm, password.encode('utf-8'), 
                salt.encode('utf-8'), iterations
            )
            return secrets.compare_digest(computed_hash.hex(), stored_hash_hex)
        
        # Fallback para hashes SHA-256 existentes (modo compatibilidad)
        elif len(stored_hash) == 64 and all(c in '0123456789abcdef' for c in stored_hash.lower()):
            # Posible hash SHA-256 legacy
            legacy_hash = hashlib.sha256(password.encode()).hexdigest()
            return secrets.compare_digest(legacy_hash, stored_hash.lower())
        
        else:
            raise PasswordSecurityError("Formato de hash no reconocido")
            
    except Exception as e:
        if isinstance(e, PasswordSecurityError):
            raise
        raise PasswordSecurityError(f"Error verificando contraseña: {str(e)}")


def check_password_needs_rehash(stored_hash: str) -> bool:
    """
    Verifica si un hash de contraseña necesita ser actualizado.
    
    Args:
        stored_hash (str): Hash almacenado
        
    Returns:
        bool: True si necesita rehash
    """
    # Los hashes SHA-256 legacy necesitan migración
    if len(stored_hash) == 64 and all(c in '0123456789abcdef' for c in stored_hash.lower()):
        return True
    
    # PBKDF2 con menos de 100,000 iteraciones necesita actualización
    if stored_hash.startswith("pbkdf2$"):
        try:
            parts = stored_hash.split('$')
            iterations = int(parts[2])
            return iterations < 100000
        except (IndexError, ValueError):
            return True
    
    # bcrypt con menos de 12 rounds necesita actualización
    if stored_hash.startswith("bcrypt$") and BCRYPT_AVAILABLE:
        try:
            hash_part = stored_hash[7:]
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