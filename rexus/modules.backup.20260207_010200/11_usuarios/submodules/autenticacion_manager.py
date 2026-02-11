"""
Submódulo de Autenticación de Usuarios - Rexus.app

Gestiona autenticación, validación de contraseñas y seguridad de acceso.
Responsabilidades:
- Autenticación segura de usuarios
- Validación de fortaleza de contraseñas
- Control de intentos fallidos y bloqueos
- Gestión de sesiones y tokens
"""

import datetime
import hashlib
from typing import Any, Dict

# Imports de seguridad unificados
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback al script loader
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            # Construir nombre del script sin extensión
            script_name = f"{path.replace('scripts/sql/', '')}/{filename}"
            return self.sql_loader.load_script(script_name)


# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}

        def sanitize_string(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0

        def sanitize_integer(self, value, min_val=None, max_val=None):
            return int(value) if value else 0


class AutenticacionManager:
    """Gestor especializado para autenticación y seguridad de usuarios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de autenticación."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/usuarios/autenticacion"

        # Configuración de seguridad
        self.max_intentos_fallidos = 5
        self.tiempo_bloqueo_minutos = 30

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {
            "usuarios",
            "intentos_login",
            "sesiones_usuario",
            "bloqueos_usuario",
            "permisos_usuario",
            "roles_usuario",
        }
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    def autenticar_usuario_seguro(self,
username: str,
        password: str) -> Dict[str,
        Any]:
        """
        Autentica un usuario de forma segura con validaciones completas.

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Dict con resultado de autenticación
        """
        if not self.db_connection:
            return {"success": False, "error": "Sin conexión a base de datos"}

        try:
            # Sanitizar datos de entrada
            username_safe = sanitize_string(username, max_length=50)

            if not username_safe or not password:
                return {"success": False, "error": "Credenciales incompletas"}

            # Verificar si la cuenta está bloqueada
            if self.verificar_cuenta_bloqueada(username_safe):
                return {
                    "success": False,
                    "error": "Cuenta bloqueada por múltiples intentos fallidos",
                }

            cursor = self.db_connection.cursor()

            # Obtener datos del usuario
            query = self.sql_manager.get_query(
                self.sql_path, "obtener_usuario_autenticacion"
            )
            cursor.execute(query, (username_safe,))

            usuario = cursor.fetchone()
            if not usuario:
                self.registrar_intento_login(username_safe, exitoso=False)
                return {"success": False, "error": "Usuario no encontrado"}

            # Verificar contraseña
            password_hash = self._hash_password(password, usuario[2])  # salt
            if password_hash != usuario[1]:  # password_hash
                self.registrar_intento_login(username_safe, exitoso=False)
                return {"success": False, "error": "Contraseña incorrecta"}

            # Autenticación exitosa
            self.reset_intentos_login(username_safe)
            self.registrar_intento_login(username_safe, exitoso=True)

            # Construir datos del usuario autenticado
            columns = [desc[0] for desc in cursor.description]
            usuario_data = dict(zip(columns, usuario))

            return {
                "success": True,
                "usuario": {
                    "id": usuario_data.get("id"),
                    "username": usuario_data.get("username"),
                    "email": usuario_data.get("email"),
                    "rol": usuario_data.get("rol", "usuario"),
                    "activo": usuario_data.get("activo", True),
                    "ultimo_acceso": datetime.datetime.now(),
                },
            }

        except Exception as e:
            print(f"Error en autenticación: {str(e)}")
            return {"success": False, "error": "Error interno del sistema"}

    def verificar_cuenta_bloqueada(self, username: str) -> bool:
        """Verifica si una cuenta de usuario está bloqueada."""
        if not self.db_connection:
            return False

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "verificar_bloqueo_usuario"
            )
            cursor.execute(query, (username_safe, self.tiempo_bloqueo_minutos))

            result = cursor.fetchone()
            return (result[0] if result else 0) > 0

        except Exception as e:
            print(f"Error verificando bloqueo: {str(e)}")
            return True  # Por seguridad, asumir bloqueado

    def registrar_intento_login(self, username: str, exitoso: bool = False) -> None:
        """Registra un intento de login en el sistema."""
        if not self.db_connection:
            return

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "registrar_intento_login")
            cursor.execute(
                query,
                (
                    username_safe,
                    exitoso,
                    datetime.datetime.now(),
                    self._obtener_ip_cliente(),
                ),
            )

            self.db_connection.commit()

            # Si falló, incrementar contador
            if not exitoso:
                self._incrementar_intentos_fallidos(username_safe)

        except Exception as e:
            print(f"Error registrando intento: {str(e)}")

    def reset_intentos_login(self, username: str) -> bool:
        """Resetea los intentos fallidos de un usuario."""
        if not self.db_connection:
            return False

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "reset_intentos_fallidos")
            cursor.execute(query, (username_safe,))

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error reseteando intentos: {str(e)}")
            return False

    def validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña según criterios de seguridad.

        Args:
            password: Contraseña a validar

        Returns:
            Dict con resultado de validación y criterios evaluados
        """
        if not password:
            return {
                "valida": False,
                "puntuacion": 0,
                "criterios": {},
                "mensaje": "Contraseña requerida",
            }

        criterios = {
            "longitud_minima": len(password) >= 8,
            "tiene_mayuscula": any(c.isupper() for c in password),
            "tiene_minuscula": any(c.islower() for c in password),
            "tiene_numero": any(c.isdigit() for c in password),
            "tiene_simbolo": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "no_muy_corta": len(password) >= 6,
            "no_muy_larga": len(password) <= 128,
        }

        criterios_cumplidos = sum(criterios.values())
        total_criterios = len(criterios)

        puntuacion = (criterios_cumplidos / total_criterios) * 100

        # Determinar nivel de fortaleza
        if puntuacion >= 85:
            nivel = "Muy fuerte"
        elif puntuacion >= 70:
            nivel = "Fuerte"
        elif puntuacion >= 50:
            nivel = "Moderada"
        else:
            nivel = "Débil"

        valida = criterios_cumplidos >= 5  # Al menos 5 criterios

        return {
            "valida": valida,
            "puntuacion": round(puntuacion, 1),
            "nivel": nivel,
            "criterios": criterios,
            "criterios_cumplidos": criterios_cumplidos,
            "total_criterios": total_criterios,
            "mensaje": self._generar_mensaje_password(criterios, valida),
        }

    def cambiar_password_usuario(
        self, usuario_id: int, password_actual: str, password_nueva: str
    ) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario con validaciones."""
        if not self.db_connection:
            return {"success": False, "error": "Sin conexión a base de datos"}

        try:
            # Validar fortaleza de nueva contraseña
            validacion = self.validar_fortaleza_password(password_nueva)
            if not validacion["valida"]:
                return {
                    "success": False,
                    "error": f"Contraseña no cumple criterios: {validacion['mensaje']}",
                }

            cursor = self.db_connection.cursor()

            # Verificar contraseña actual
            query_verificar = self.sql_manager.get_query(
                self.sql_path, "verificar_password_actual"
            )
            cursor.execute(query_verificar, (usuario_id,))

            usuario = cursor.fetchone()
            if not usuario:
                return {"success": False, "error": "Usuario no encontrado"}

            password_hash_actual = self._hash_password(
                password_actual, usuario[1]
            )  # salt
            if password_hash_actual != usuario[0]:  # password_hash
                return {"success": False, "error": "Contraseña actual incorrecta"}

            # Generar nuevo hash y salt
            nuevo_salt = self._generar_salt()
            nuevo_hash = self._hash_password(password_nueva, nuevo_salt)

            # Actualizar contraseña
            query_actualizar = self.sql_manager.get_query(
                self.sql_path, "actualizar_password"
            )
            cursor.execute(query_actualizar,
(nuevo_hash,
                nuevo_salt,
                usuario_id))

            self.db_connection.commit()

            return {"success": True, "mensaje": "Contraseña actualizada exitosamente"}

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error cambiando contraseña: {str(e)}")
            return {"success": False, "error": "Error interno del sistema"}

    def _incrementar_intentos_fallidos(self, username: str) -> None:
        """Incrementa el contador de intentos fallidos."""
        try:
            cursor = self.db_connection.cursor()

            # Obtener intentos actuales
            query_obtener = self.sql_manager.get_query(
                self.sql_path, "obtener_intentos_fallidos"
            )
            cursor.execute(query_obtener, (username,))

            result = cursor.fetchone()
            intentos_actuales = (result[0] if result else 0) + 1

            # Actualizar contador
            query_actualizar = self.sql_manager.get_query(
                self.sql_path, "actualizar_intentos_fallidos"
            )
            cursor.execute(
                query_actualizar,
(intentos_actuales,
                    datetime.datetime.now(),
                    username)
            )

            # Si supera el límite, bloquear usuario
            if intentos_actuales >= self.max_intentos_fallidos:
                self._bloquear_usuario(username)

            self.db_connection.commit()

        except Exception as e:
            print(f"Error incrementando intentos: {str(e)}")

    def _bloquear_usuario(self, username: str) -> None:
        """Bloquea temporalmente un usuario."""
        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "bloquear_usuario")
            cursor.execute(
                query,
                (
                    username,
                    datetime.datetime.now(),
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=self.tiempo_bloqueo_minutos),
                ),
            )

        except Exception as e:
            print(f"Error bloqueando usuario: {str(e)}")

    def _hash_password(self, password: str, salt: str) -> str:
        """Genera hash de contraseña con salt."""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

    def _generar_salt(self) -> str:
        """Genera un salt aleatorio."""
        import secrets

        return secrets.token_hex(32)

    def _obtener_ip_cliente(self) -> str:
        """Obtiene la IP del cliente (simplificado)."""
        return "127.0.0.1"  # Placeholder

    def _generar_mensaje_password(
        self, criterios: Dict[str, bool], valida: bool
    ) -> str:
        """Genera mensaje descriptivo sobre validación de contraseña."""
        if valida:
            return "Contraseña cumple los criterios de seguridad"

        faltantes = []
        if not criterios.get("longitud_minima"):
            faltantes.append("mínimo 8 caracteres")
        if not criterios.get("tiene_mayuscula"):
            faltantes.append("al menos una mayúscula")
        if not criterios.get("tiene_minuscula"):
            faltantes.append("al menos una minúscula")
        if not criterios.get("tiene_numero"):
            faltantes.append("al menos un número")
        if not criterios.get("tiene_simbolo"):
            faltantes.append("al menos un símbolo")

        return f"Faltan: {', '.join(faltantes)}"
