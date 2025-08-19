"""
Two-Factor Authentication Module - Rexus.app

Módulo para autenticación de dos factores con TOTP (Time-based One-Time Password).
Implementación básica para sistemas que no tengan dependencias externas complejas.
"""

import base64
import hashlib
import hmac
import struct
import time
import secrets
import qrcode
from typing import Optional, Dict, Any
import io


class TwoFactorAuth:
    """Clase para manejar autenticación de dos factores."""

    def __init__(self):
        self.window = 1  # Ventana de tiempo para validación
        self.interval = 30  # Intervalo en segundos

    def generate_secret_key(self) -> str:
        """Genera una clave secreta para 2FA."""
        return base64.b32encode(secrets.token_bytes(20)).decode('utf-8').rstrip('=')

    def generate_totp_token(self, secret_key: str, timestamp: Optional[int] = None) -> str:
        """Genera un token TOTP de 6 dígitos."""
        if timestamp is None:
            timestamp = int(time.time())

        # Calcular el contador basado en tiempo
        counter = timestamp // self.interval

        # Convertir el secreto de base32 a bytes
        try:
            # Agregar padding si es necesario
            padding_needed = 8 - (len(secret_key) % 8)
            if padding_needed != 8:
                secret_key += '=' * padding_needed

            secret_bytes = base64.b32decode(secret_key, casefold=True)
        except (ValueError, TypeError, base64.binascii.Error):
            # Fallback: usar el secreto como está
            secret_bytes = secret_key.encode('utf-8')

        # Crear el mensaje para HMAC
        message = struct.pack('>Q', counter)

        # Calcular HMAC-SHA1
        hmac_digest = hmac.new(secret_bytes, message, hashlib.sha1).digest()

        # Extraer 4 bytes dinámicamente
        offset = hmac_digest[-1] & 0x0f
        truncated = hmac_digest[offset:offset + 4]

        # Convertir a entero de 32 bits
        code = struct.unpack('>I', truncated)[0]
        code &= 0x7fffffff

        # Convertir a 6 dígitos
        return f"{code % 1000000:06d}"

    def verify_totp_token(self,
secret_key: str,
        token: str,
        timestamp: Optional[int] = None) -> bool:
        """Verifica un token TOTP."""
        if not token or len(token) != 6 or not token.isdigit():
            return False

        if timestamp is None:
            timestamp = int(time.time())

        # Verificar con ventana de tiempo para compensar desfases
        for i in range(-self.window, self.window + 1):
            test_timestamp = timestamp + (i * self.interval)
            expected_token = self.generate_totp_token(secret_key, test_timestamp)

            if expected_token == token:
                return True

        return False

    def generate_qr_code_url(self,
secret_key: str,
        user_email: str,
        issuer: str = "Rexus.app") -> str:
        """Genera URL para código QR de configuración."""
        return f"otpauth://totp/{issuer}:{user_email}?secret={secret_key}&issuer={issuer}"

    def generate_qr_code_image(self,
secret_key: str,
        user_email: str,
        issuer: str = "Rexus.app") -> bytes:
        """Genera imagen QR como bytes."""
        try:
            url = self.generate_qr_code_url(secret_key, user_email, issuer)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')

            return img_buffer.getvalue()
        except ImportError:
            # Si qrcode no está disponible, retornar bytes vacíos
            return b""

    def get_backup_codes(self, count: int = 8) -> list:
        """Genera códigos de respaldo."""
        codes = []
        for _ in range(count):
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            # Formatear como XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)

        return codes

    def hash_backup_code(self, code: str) -> str:
        """Hashea un código de respaldo para almacenamiento seguro."""
        # Remover guiones y convertir a minúsculas
        clean_code = code.replace('-', '').lower()

        # Hash con salt
        salt = b"rexus_2fa_backup"
        return hashlib.pbkdf2_hmac('sha256',
clean_code.encode(),
            salt,
            100000).hex()

    def verify_backup_code(self, code: str, hashed_code: str) -> bool:
        """Verifica un código de respaldo."""
        return self.hash_backup_code(code) == hashed_code


class TwoFactorManager:
    """Manager para gestión completa de 2FA por usuario."""

    def __init__(self):
        self.totp = TwoFactorAuth()
        self.user_secrets: Dict[str, Dict[str, Any]] = {}

    def enable_2fa_for_user(self,
user_id: str,
        user_email: str) -> Dict[str,
        Any]:
        """Habilita 2FA para un usuario."""
        secret_key = self.totp.generate_secret_key()
        backup_codes = self.totp.get_backup_codes()

        # Hashear códigos de respaldo
        hashed_backup_codes = [self.totp.hash_backup_code(code) for code in backup_codes]

        user_2fa_data = {
            'secret_key': secret_key,
            'backup_codes': hashed_backup_codes,
            'enabled': False,  # Se habilita después de verificar setup
            'verified': False
        }

        self.user_secrets[user_id] = user_2fa_data

        return {
            'secret_key': secret_key,
            'backup_codes': backup_codes,  # Mostrar códigos originales al usuario
            'qr_url': self.totp.generate_qr_code_url(secret_key, user_email)
        }

    def verify_and_enable_2fa(self, user_id: str, token: str) -> bool:
        """Verifica el setup inicial y habilita 2FA."""
        if user_id not in self.user_secrets:
            return False

        user_data = self.user_secrets[user_id]
        secret_key = user_data['secret_key']

        if self.totp.verify_totp_token(secret_key, token):
            user_data['enabled'] = True
            user_data['verified'] = True
            return True

        return False

    def authenticate_user(self, user_id: str, token: str) -> bool:
        """Autentica un usuario con 2FA."""
        if user_id not in self.user_secrets:
            return False

        user_data = self.user_secrets[user_id]

        if not user_data['enabled']:
            return False

        secret_key = user_data['secret_key']

        # Verificar token TOTP primero
        if self.totp.verify_totp_token(secret_key, token):
            return True

        # Verificar códigos de respaldo
        for i, hashed_backup in enumerate(user_data['backup_codes']):
            if self.totp.verify_backup_code(token, hashed_backup):
                # Remover código usado
                user_data['backup_codes'].pop(i)
                return True

        return False

    def disable_2fa_for_user(self, user_id: str) -> bool:
        """Deshabilita 2FA para un usuario."""
        if user_id in self.user_secrets:
            del self.user_secrets[user_id]
            return True
        return False

    def is_2fa_enabled(self, user_id: str) -> bool:
        """Verifica si 2FA está habilitado para un usuario."""
        return (user_id in self.user_secrets and
                self.user_secrets[user_id].get('enabled', False))


# Instancia global del manager
two_factor_manager = TwoFactorManager()
