"""
Sistema de Two-Factor Authentication (2FA) para Rexus.app
Genera y valida códigos TOTP (Time-based One-Time Password)
"""

import base64
import hashlib
import hmac
import json
import secrets
import struct
import time
from io import BytesIO
from typing import Any, Dict, Optional

import qrcode


class TwoFactorAuth:
    """
    Implementación de Two-Factor Authentication usando TOTP (RFC 6238)
    """

    def __init__(self, issuer: str = "Rexus.app"):
        self.issuer = issuer
        self.window = 1  # Ventana de tolerancia para códigos (±30 segundos)
        self.digits = 6  # Número de dígitos del código
        self.period = 30  # Período en segundos

    def generar_secret_key(self) -> str:
        """
        Genera una clave secreta aleatoria para 2FA.

        Returns:
            str: Clave secreta en base32
        """
        # Generar 20 bytes aleatorios (160 bits)
        secret_bytes = secrets.token_bytes(20)
        # Codificar en base32 (estándar para TOTP)
        secret_base32 = base64.b32encode(secret_bytes).decode("utf-8")
        return secret_base32

    def generar_qr_code(self, username: str, secret_key: str) -> bytes:
        """
        Genera un código QR para configurar 2FA en una app móvil.

        Args:
            username: Nombre de usuario
            secret_key: Clave secreta en base32

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Crear URI para TOTP según RFC 6238
        totp_uri = (
            f"otpauth://totp/{self.issuer}:{username}"
            f"?secret={secret_key}"
            f"&issuer={self.issuer}"
            f"&digits={self.digits}"
            f"&period={self.period}"
        )

        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir a bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        return img_buffer.getvalue()

    def generar_codigo_totp(
        self, secret_key: str, timestamp: Optional[int] = None
    ) -> str:
        """
        Genera un código TOTP para un momento específico.

        Args:
            secret_key: Clave secreta en base32
            timestamp: Timestamp unix (None para tiempo actual)

        Returns:
            str: Código TOTP de 6 dígitos
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Calcular contador basado en tiempo
        counter = timestamp // self.period

        # Decodificar secret key
        try:
            secret_bytes = base64.b32decode(secret_key.upper())
        except Exception:
            raise ValueError("Clave secreta inválida")

        # Generar HMAC-SHA1
        counter_bytes = struct.pack(">Q", counter)
        hmac_hash = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()

        # Extraer código de 6 dígitos (Dynamic Truncation)
        offset = hmac_hash[-1] & 0x0F
        code = struct.unpack(">I", hmac_hash[offset : offset + 4])[0]
        code &= 0x7FFFFFFF
        code %= 10**self.digits

        return str(code).zfill(self.digits)

    def validar_codigo_totp(
        self, secret_key: str, codigo_usuario: str, timestamp: Optional[int] = None
    ) -> bool:
        """
        Valida un código TOTP proporcionado por el usuario.

        Args:
            secret_key: Clave secreta en base32
            codigo_usuario: Código proporcionado por el usuario
            timestamp: Timestamp unix (None para tiempo actual)

        Returns:
            bool: True si el código es válido
        """
        if not codigo_usuario or len(codigo_usuario) != self.digits:
            return False

        if timestamp is None:
            timestamp = int(time.time())

        # Validar con ventana de tolerancia
        for i in range(-self.window, self.window + 1):
            test_timestamp = timestamp + (i * self.period)
            expected_code = self.generar_codigo_totp(secret_key, test_timestamp)

            if secrets.compare_digest(expected_code, codigo_usuario):
                return True

        return False

    def habilitar_2fa_usuario(self, usuarios_model, username: str) -> Dict[str, Any]:
        """
        Habilita 2FA para un usuario específico.

        Args:
            usuarios_model: Instancia del modelo de usuarios
            username: Nombre de usuario

        Returns:
            Dict con secret_key y QR code
        """
        try:
            # Generar nueva clave secreta
            secret_key = self.generar_secret_key()

            # Generar código QR
            qr_code_bytes = self.generar_qr_code(username, secret_key)

            # Guardar en base de datos (en configuración_personal como JSON)
            usuario_data = usuarios_model.obtener_usuario_por_nombre(username)
            if not usuario_data:
                raise ValueError("Usuario no encontrado")

            # Actualizar configuración personal
            config_personal = usuario_data.get("configuracion_personal", "{}")
            try:
                config_dict = json.loads(config_personal) if config_personal else {}
            except json.JSONDecodeError:
                config_dict = {}

            config_dict["2fa_enabled"] = False  # Pendiente de verificación
            config_dict["2fa_secret"] = secret_key
            config_dict["2fa_setup_date"] = int(time.time())

            # Actualizar en base de datos
            usuarios_model.actualizar_configuracion_personal(
                usuario_data["id"], json.dumps(config_dict)
            )

            return {
                "success": True,
                "secret_key": secret_key,
                "qr_code": base64.b64encode(qr_code_bytes).decode("utf-8"),
                "manual_entry_key": secret_key,
                "instructions": (
                    "1. Instale una app de autenticación (Google Authenticator, Authy, etc.)\n"
                    "2. Escanee el código QR o ingrese manualmente la clave\n"
                    "3. Ingrese el código de 6 dígitos para verificar la configuración"
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def verificar_setup_2fa(
        self, usuarios_model, username: str, codigo_verificacion: str
    ) -> bool:
        """
        Verifica y confirma la configuración de 2FA.

        Args:
            usuarios_model: Instancia del modelo de usuarios
            username: Nombre de usuario
            codigo_verificacion: Código de verificación del usuario

        Returns:
            bool: True si la verificación es exitosa
        """
        try:
            usuario_data = usuarios_model.obtener_usuario_por_nombre(username)
            if not usuario_data:
                return False

            config_personal = usuario_data.get("configuracion_personal", "{}")
            try:
                config_dict = json.loads(config_personal) if config_personal else {}
            except json.JSONDecodeError:
                return False

            secret_key = config_dict.get("2fa_secret")
            if not secret_key:
                return False

            # Validar código
            if self.validar_codigo_totp(secret_key, codigo_verificacion):
                # Habilitar 2FA permanentemente
                config_dict["2fa_enabled"] = True
                config_dict["2fa_verified_date"] = int(time.time())

                usuarios_model.actualizar_configuracion_personal(
                    usuario_data["id"], json.dumps(config_dict)
                )

                return True

            return False

        except Exception as e:
            print(f"[ERROR 2FA] Error verificando setup: {e}")
            return False

    def validar_2fa_login(self, usuarios_model, username: str, codigo_2fa: str) -> bool:
        """
        Valida el código 2FA durante el login.

        Args:
            usuarios_model: Instancia del modelo de usuarios
            username: Nombre de usuario
            codigo_2fa: Código 2FA del usuario

        Returns:
            bool: True si el código es válido
        """
        try:
            usuario_data = usuarios_model.obtener_usuario_por_nombre(username)
            if not usuario_data:
                return False

            config_personal = usuario_data.get("configuracion_personal", "{}")
            try:
                config_dict = json.loads(config_personal) if config_personal else {}
            except json.JSONDecodeError:
                return False

            # Verificar si 2FA está habilitado
            if not config_dict.get("2fa_enabled", False):
                return True  # 2FA no habilitado, permitir acceso

            secret_key = config_dict.get("2fa_secret")
            if not secret_key:
                return False

            # Validar código TOTP
            return self.validar_codigo_totp(secret_key, codigo_2fa)

        except Exception as e:
            print(f"[ERROR 2FA] Error validando login: {e}")
            return False

    def deshabilitar_2fa(self, usuarios_model, username: str) -> bool:
        """
        Deshabilita 2FA para un usuario.

        Args:
            usuarios_model: Instancia del modelo de usuarios
            username: Nombre de usuario

        Returns:
            bool: True si se deshabilitó correctamente
        """
        try:
            usuario_data = usuarios_model.obtener_usuario_por_nombre(username)
            if not usuario_data:
                return False

            config_personal = usuario_data.get("configuracion_personal", "{}")
            try:
                config_dict = json.loads(config_personal) if config_personal else {}
            except json.JSONDecodeError:
                config_dict = {}

            # Limpiar configuración 2FA
            config_dict.pop("2fa_enabled", None)
            config_dict.pop("2fa_secret", None)
            config_dict.pop("2fa_setup_date", None)
            config_dict.pop("2fa_verified_date", None)
            config_dict["2fa_disabled_date"] = int(time.time())

            usuarios_model.actualizar_configuracion_personal(
                usuario_data["id"], json.dumps(config_dict)
            )

            return True

        except Exception as e:
            print(f"[ERROR 2FA] Error deshabilitando 2FA: {e}")
            return False


# Función helper para agregar método al modelo de usuarios
def agregar_metodo_configuracion_personal(usuarios_model):
    """
    Agrega el método actualizar_configuracion_personal al modelo si no existe.
    """
    if not hasattr(usuarios_model, "actualizar_configuracion_personal"):

        def actualizar_configuracion_personal(
            self, usuario_id: int, config_json: str
        ) -> bool:
            """Actualiza la configuración personal de un usuario."""
            if not self.db_connection:
                return False

            try:
                cursor = self.db_connection.cursor()
                tabla_validada = self._validate_table_name(self.tabla_usuarios)

                query = f"UPDATE [{tabla_validada}] SET configuracion_personal = ? WHERE id = ?"
                cursor.execute(query, (config_json, usuario_id))
                self.db_connection.commit()

                return cursor.rowcount > 0

            except Exception as e:
                print(
                    f"[ERROR USUARIOS] Error actualizando configuración personal: {e}"
                )
                return False

        # Agregar método dinámicamente
        import types

        usuarios_model.actualizar_configuracion_personal = types.MethodType(
            actualizar_configuracion_personal, usuarios_model
        )


# Instancia global para uso en la aplicación
two_factor_auth = TwoFactorAuth()


if __name__ == "__main__":
    # Test básico del sistema 2FA
    tfa = TwoFactorAuth()

    # Generar clave secreta
    secret = tfa.generar_secret_key()
    print(f"Secret Key: {secret}")

    # Generar código actual
    codigo = tfa.generar_codigo_totp(secret)
    print(f"Código actual: {codigo}")

    # Validar código
    valido = tfa.validar_codigo_totp(secret, codigo)
    print(f"Código válido: {valido}")

    # Generar QR code
    qr_bytes = tfa.generar_qr_code("admin", secret)
    with open("test_qr.png", "wb") as f:
        f.write(qr_bytes)
    print("QR code guardado como test_qr.png")
