#!/usr/bin/env python3
"""
Utilidades de seguridad para Rexus
Implementa funciones de seguridad críticas con estándares OWASP
"""

import hashlib
import secrets
import re
from typing import Optional
import logging

# Intentar importar bcrypt (estándar OWASP para contraseñas)
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt no disponible, usando PBKDF2 como fallback")

# Configuración de logging para seguridad
logging.basicConfig(level=logging.INFO)

class SecurityUtils:
    """Utilidades de seguridad para la aplicacion"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera hash seguro de contraseña usando bcrypt (estándar OWASP).

        Si bcrypt no está disponible, usa PBKDF2 como fallback seguro.

        Args:
            password: Contraseña en texto plano

        Returns:
            str: Hash de contraseña (bcrypt o PBKDF2)
        """
        if BCRYPT_AVAILABLE:
            # ✅ bcrypt - Estándar OWASP (más lento, más seguro contra GPU)
            salt = bcrypt.gensalt(rounds=12)  # 12 rounds es el recomendado
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        else:
            # ⚠️ Fallback a PBKDF2 si bcrypt no está disponible
            logging.warning("Usando PBKDF2 como fallback (bcrypt no disponible)")
            salt = secrets.token_hex(32)
            pwdhash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # 100,000 iteraciones
            )
            # Prefijo para identificar que es PBKDF2
            return f"pbkdf2${salt}${pwdhash.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica contraseña contra hash.

        Soporta hashes bcrypt y PBKDF2 (para compatibilidad con migración).

        Args:
            password: Contraseña en texto plano a verificar
            hashed: Hash almacenado

        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            # Verificar si es hash bcrypt
            if not hashed.startswith("pbkdf2$"):
                if BCRYPT_AVAILABLE:
                    # ✅ Verificar bcrypt
                    return bcrypt.checkpw(
                        password.encode('utf-8'),
                        hashed.encode('utf-8')
                    )
                else:
                    # bcrypt no disponible pero el hash es bcrypt - no podemos verificar
                    logging.error("Hash bcrypt detectado pero bcrypt no está instalado")
                    return False

            # ⚠️ Verificar PBKDF2 (legacy o fallback)
            if hashed.startswith("pbkdf2$"):
                # Formato: pbkdf2$salt$hash
                parts = hashed.split('$')
                if len(parts) != 3:
                    return False

                _, salt, stored_hash = parts
                pwdhash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                )
                return pwdhash.hex() == stored_hash

            # Intento de verificación para formato antiguo (sin prefijo)
            # TODO: Eliminar después de migración completa
            if len(hashed) >= 128:  # Formato antiguo: 64 chars salt + 64+ chars hash
                salt = hashed[:64]
                stored_hash = hashed[64:]
                pwdhash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                )
                return pwdhash.hex() == stored_hash

            return False

        except (ValueError, TypeError, UnicodeDecodeError, IndexError) as e:
            logging.error(f"Error verificando contraseña: {e}")
            return False

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitiza entrada de usuario para prevenir XSS"""
        if not user_input:
            return ""

        # Caracteres peligrosos comunes
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
            '/': '&#x2F;'
        }

        # Reemplazar caracteres peligrosos
        sanitized = user_input
        for char, replacement in dangerous_chars.items():
            sanitized = sanitized.replace(char, replacement)

        # Remover scripts obvios
        script_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'eval\s*\(',
            r'alert\s*\('
        ]

        for pattern in script_patterns:
            sanitized = re.sub(pattern,
'',
                sanitized,
                flags=re.IGNORECASE | re.DOTALL)

        return sanitized.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_sql_identifier(identifier: str) -> bool:
        """Valida que un identificador SQL sea seguro"""
        if not identifier:
            return False
        # Solo letras, números y guiones bajos, no puede empezar con número
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, identifier)) and len(identifier) <= 64

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Genera un token seguro aleatorio"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Valida la fortaleza de una contraseña"""
        result = {
            'valid': False,
            'score': 0,
            'issues': []
        }

        if not password:
            result['issues'].append('Contraseña vacía')
            return result

        # Criterios de validación
        if len(password) < 8:
            result['issues'].append('Debe tener al menos 8 caracteres')
        else:
            result['score'] += 1

        if not re.search(r'[a-z]', password):
            result['issues'].append('Debe contener al menos una minúscula')
        else:
            result['score'] += 1

        if not re.search(r'[A-Z]', password):
            result['issues'].append('Debe contener al menos una mayúscula')
        else:
            result['score'] += 1

        if not re.search(r'\d', password):
            result['issues'].append('Debe contener al menos un número')
        else:
            result['score'] += 1

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['issues'].append('Debe contener al menos un carácter especial')
        else:
            result['score'] += 1

        result['valid'] = result['score'] >= 4
        return result

def get_security_logger():
    """Obtiene logger configurado para eventos de seguridad"""
    logger = logging.getLogger('rexus.security')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
