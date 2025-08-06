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
SOFTWARE. """Security Utilities"""

import hashlib
import secrets
import re
import logging
from typing import Optional

class SecurityUtils:
    """Utilidades de seguridad para la aplicación"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash seguro de contraseña usando PBKDF2"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt + pwd_hash.hex()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica contraseña contra hash"""
        try:
            salt = hashed[:32]
            stored_hash = hashed[32:]
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return stored_hash == pwd_hash.hex()
        except Exception:
            return False
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitiza entrada de usuario para prevenir XSS"""
        if not user_input:
            return ""
        
        # Caracteres peligrosos para XSS
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
            '/': '&#x2F;'
        }
        
        sanitized = user_input
        for char, replacement in dangerous_chars.items():
            sanitized = sanitized.replace(char, replacement)
        
        # Remover scripts y contenido peligroso
        script_pattern = re.compile(r'<script.*?</script>', re.IGNORECASE | re.DOTALL)
        sanitized = script_pattern.sub('', sanitized)
        
        # Remover eventos javascript
        event_pattern = re.compile(r'on\w+\s*=', re.IGNORECASE)
        sanitized = event_pattern.sub('', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_sql_identifier(identifier: str) -> bool:
        """Valida que un identificador SQL sea seguro"""
        if not identifier:
            return False
        
        # Solo letras, números y guiones bajos
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(pattern, identifier) is not None
    
    @staticmethod
    def generate_secure_token() -> str:
        """Genera un token seguro aleatorio"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Valida la fortaleza de una contraseña"""
        result = {
            'valid': False,
            'score': 0,
            'issues': []
        }
        
        if len(password) < 8:
            result['issues'].append('Debe tener al menos 8 caracteres')
        else:
            result['score'] += 1
        
        if not re.search(r'[A-Z]', password):
            result['issues'].append('Debe contener al menos una mayúscula')
        else:
            result['score'] += 1
        
        if not re.search(r'[a-z]', password):
            result['issues'].append('Debe contener al menos una minúscula')
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
    logger = logging.getLogger('security')
    if not logger.handlers:
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
