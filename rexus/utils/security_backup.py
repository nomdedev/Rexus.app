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

"""Security Utilities"""

import hashlib
import secrets
import re
import logging

class SecurityUtils:
    """Utilidades de seguridad para la aplicación"""
    
    @staticmethod
    def hash_password(password):
        """Genera hash seguro de contraseña"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt + pwd_hash.hex()
    
    @staticmethod
    def verify_password(password, hashed):
        """Verifica contraseña contra hash"""
        try:
            salt = hashed[:32]
            stored_hash = hashed[32:]
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return stored_hash == pwd_hash.hex()
        except Exception:
            return False
    
    @staticmethod
    def sanitize_input(text, max_length=255):
        """Sanitiza entrada de texto"""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        # Remover caracteres peligrosos
        text = re.sub(r'[<>"\';\\]', '', text)
        
        # Limitar longitud
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def validate_email(email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def generate_token(length=32):
        """Genera token seguro"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def is_safe_filename(filename):
        """Verifica si el nombre de archivo es seguro"""
        if not filename or len(filename) > 255:
            return False
        
        # Caracteres no permitidos
        unsafe_chars = r'[<>:"/\\|?*]'
        if re.search(unsafe_chars, filename):
            return False
        
        # Nombres reservados en Windows
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper() in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def log_security_event(event_type, details, level=logging.WARNING):
        """Registra evento de seguridad"""
        logger = logging.getLogger('security')
        logger.log(level, f"[SECURITY] {event_type}: {details}")

# Instancia global para compatibilidad
security_utils = SecurityUtils()