#!/usr/bin/env python3
"""
Módulo de autenticación de dos factores (2FA) para el sistema.
Proporciona funcionalidades de verificación en dos pasos.
"""

import secrets
import time
import hashlib
import base64
import logging
from typing import Dict, Optional, Tuple
import pyotp

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    """
    Clase para manejar autenticación de dos factores.
    """
    
    def __init__(self):
        """Inicializa el sistema de 2FA."""
        self.logger = logging.getLogger(__name__)
        self.totp_window = 1  # Ventana de tiempo para TOTP (±30 segundos)
        self.backup_codes_count = 10  # Número de códigos de respaldo
    
    def generate_secret(self) -> str:
        """
        Genera un secreto TOTP para un usuario.
        
        Returns:
            str: Secreto TOTP en formato base32
        """
        return base64.b32encode(secrets.token_bytes(16)).decode('utf-8')
    
    def generate_qr_code_url(self, secret: str, username: str, issuer: str = "RexusApp") -> str:
        """
        Genera la URL para el código QR de Google Authenticator.
        
        Args:
            secret: Secreto TOTP del usuario
            username: Nombre de usuario
            issuer: Nombre de la aplicación
            
        Returns:
            str: URL para generar código QR
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Verifica un token TOTP.
        
        Args:
            secret: Secreto TOTP del usuario
            token: Token proporcionado por el usuario
            
        Returns:
            bool: True si el token es válido
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=self.totp_window)
        except Exception as e:
            self.logger.error(f"Error verificando TOTP: {e}")
            return False
    
    def generate_backup_codes(self) -> list:
        """
        Genera códigos de respaldo para 2FA.
        
        Returns:
            list: Lista de códigos de respaldo
        """
        codes = []
        for _ in range(self.backup_codes_count):
            code = f"{secrets.randbelow(1000000):06d}"
            codes.append(code)
        return codes
    
    def verify_backup_code(self, stored_codes: list, provided_code: str) -> bool:
        """
        Verifica un código de respaldo.
        
        Args:
            stored_codes: Códigos almacenados para el usuario
            provided_code: Código proporcionado por el usuario
            
        Returns:
            bool: True si el código es válido
        """
        return provided_code in stored_codes
    
    def hash_backup_codes(self, codes: list) -> list:
        """
        Hashea los códigos de respaldo para almacenamiento seguro.
        
        Args:
            codes: Lista de códigos de respaldo en texto plano
            
        Returns:
            list: Lista de códigos hasheados
        """
        hashed_codes = []
        for code in codes:
            hashed = hashlib.sha256(code.encode('utf-8')).hexdigest()
            hashed_codes.append(hashed)
        return hashed_codes
    
    def generate_temp_code(self, length: int = 6) -> str:
        """
        Genera un código temporal para verificación por email/SMS.
        
        Args:
            length: Longitud del código
            
        Returns:
            str: Código temporal
        """
        return f"{secrets.randbelow(10**length):0{length}d}"
    
    def verify_temp_code(self, stored_code: str, provided_code: str, max_age_minutes: int = 10) -> bool:
        """
        Verifica un código temporal con tiempo de expiración.
        
        Args:
            stored_code: Código almacenado con timestamp
            provided_code: Código proporcionado por el usuario
            max_age_minutes: Tiempo máximo de validez en minutos
            
        Returns:
            bool: True si el código es válido y no ha expirado
        """
        try:
            # El código almacenado debería tener el formato: codigo:timestamp
            if ':' not in stored_code:
                return False
            
            code_part, timestamp_part = stored_code.split(':', 1)
            stored_timestamp = int(timestamp_part)
            
            # Verificar que el código coincida
            if code_part != provided_code:
                return False
            
            # Verificar que no haya expirado
            current_time = int(time.time())
            max_age_seconds = max_age_minutes * 60
            
            return (current_time - stored_timestamp) <= max_age_seconds
            
        except Exception as e:
            self.logger.error(f"Error verificando código temporal: {e}")
            return False
    
    def store_temp_code(self, code: str) -> str:
        """
        Almacena un código temporal con timestamp.
        
        Args:
            code: Código a almacenar
            
        Returns:
            str: Código con timestamp para almacenamiento
        """
        timestamp = int(time.time())
        return f"{code}:{timestamp}"
    
    def is_2fa_enabled(self, user_data: dict) -> bool:
        """
        Verifica si un usuario tiene 2FA habilitado.
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            bool: True si 2FA está habilitado
        """
        return bool(user_data.get('totp_secret') or user_data.get('backup_codes'))
    
    def get_2fa_status(self, user_data: dict) -> dict:
        """
        Obtiene el estado completo de 2FA de un usuario.
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            dict: Estado de 2FA
        """
        return {
            'enabled': self.is_2fa_enabled(user_data),
            'totp_enabled': bool(user_data.get('totp_secret')),
            'backup_codes_enabled': bool(user_data.get('backup_codes')),
            'temp_code_enabled': bool(user_data.get('temp_code'))
        }

# Instancia global del sistema 2FA
two_factor_auth = TwoFactorAuth()

# Funciones de conveniencia para uso directo
def generate_totp_secret() -> str:
    """Función de conveniencia para generar secreto TOTP."""
    return two_factor_auth.generate_secret()

def verify_totp_token(secret: str, token: str) -> bool:
    """Función de conveniencia para verificar token TOTP."""
    return two_factor_auth.verify_totp(secret, token)

def generate_backup_codes() -> list:
    """Función de conveniencia para generar códigos de respaldo."""
    return two_factor_auth.generate_backup_codes()

def generate_temp_verification_code(length: int = 6) -> str:
    """Función de conveniencia para generar código temporal."""
    return two_factor_auth.generate_temp_code(length)