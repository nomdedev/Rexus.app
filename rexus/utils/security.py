#!/usr/bin/env python3
"""
Utilidades de seguridad para Rexus
Implementa funciones de seguridad críticas
"""

import hashlib
import secrets
import re
import html
from typing import Any, Optional


class SecurityUtils:
    """Utilidades de seguridad para el sistema Rexus"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hashea una contraseña con salt
        
        Args:
            password: Contraseña a hashear
            salt: Salt opcional (se genera uno si no se proporciona)
            
        Returns:
            tuple: (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
        
        return hash_bytes.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hash_stored: str, salt: str) -> bool:
        """
        Verifica una contraseña contra su hash almacenado
        
        Args:
            password: Contraseña a verificar
            hash_stored: Hash almacenado
            salt: Salt usado en el hash
            
        Returns:
            bool: True si la contraseña es válida
        """
        try:
            hash_computed, _ = SecurityUtils.hash_password(password, salt)
            return secrets.compare_digest(hash_computed, hash_stored)
        except (ValueError, TypeError, UnicodeDecodeError, IndexError):
            return False
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitiza entrada de usuario para prevenir XSS"""
        if not isinstance(user_input, str):
            user_input = str(user_input)
        
        # Escapar HTML
        sanitized = html.escape(user_input, quote=True)
        
        # Eliminar caracteres de control peligrosos
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def sanitize_sql_input(user_input: Any) -> str:
        """
        Sanitiza entrada para SQL (nota: usar parámetros preparados es mejor)
        
        Args:
            user_input: Entrada del usuario
            
        Returns:
            str: Entrada sanitizada
        """
        if user_input is None:
            return ""
        
        if not isinstance(user_input, str):
            user_input = str(user_input)
        
        # Escapar comillas simples duplicándolas
        return user_input.replace("'", "''")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            bool: True si el formato es válido
        """
        if not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Genera un token seguro aleatorio
        
        Args:
            length: Longitud del token en bytes
            
        Returns:
            str: Token hexadecimal
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """
        Verifica si un nombre de archivo es seguro
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si es seguro
        """
        if not isinstance(filename, str) or not filename:
            return False
        
        # Caracteres prohibidos
        forbidden_chars = '<>:"/\\|?*'
        if any(char in filename for char in forbidden_chars):
            return False
        
        # Nombres reservados en Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True


# Alias para compatibilidad
def sanitize_string(text: Any) -> str:
    """Alias para SecurityUtils.sanitize_input"""
    return SecurityUtils.sanitize_input(str(text) if text is not None else "")


def sanitize_sql_input(text: Any) -> str:
    """Alias para SecurityUtils.sanitize_sql_input"""
    return SecurityUtils.sanitize_sql_input(text)