"""
Authentication Manager - Módulo especializado para autenticación de usuarios
Refactorizado de UsuariosModel para mejor mantenibilidad

Responsabilidades:
- Autenticación de usuarios
- Validación de contraseñas
- Manejo de intentos fallidos y bloqueos
- Hashing seguro de contraseñas
"""

import datetime
import hashlib
import logging

# Fallback para bcrypt si no está disponible
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    # Mock de bcrypt usando hashlib
    class MockBcrypt:
        @staticmethod
        def gensalt(rounds=12):
            return b"mock_salt_rexus_app"

        @staticmethod
        def hashpw(password, salt):
            if isinstance(password, str):
                password = password.encode('utf-8')
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            return hashlib.pbkdf2_hmac('sha256', password, salt, 100000)

        @staticmethod
        def checkpw(password, hashed):
            if isinstance(password, str):
                password = password.encode('utf-8')
            test_hash = MockBcrypt.hashpw(password, b"mock_salt_rexus_app")
            return test_hash == hashed

    bcrypt = MockBcrypt()
from typing import Dict, Any, Optional

# Configurar logging
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
        from rexus.utils.sql_security import SQLSecurityValidator
except ImportError:
    logger.warning("Security utilities not fully available")
    DataSanitizer = None
    SQLSecurityValidator = None

from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.unified_sanitizer import sanitize_string


class AuthenticationManager:
    """Gestor especializado de autenticación de usuarios."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.sanitizer = DataSanitizer() if DataSanitizer else None

        # Configuración de seguridad
        self.max_intentos_login = 3
        self.tiempo_bloqueo_minutos = 15
        self.password_min_length = 8

        # Salt para bcrypt (configurar según entorno)
        self.bcrypt_rounds = 12

    def autenticar_usuario_seguro(self,
username: str,
        password: str) -> Dict[str,
        Any]:
        """
        Autenticación segura de usuario con protección contra ataques.

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Dict con resultado de autenticación
        """
        try:
            # Sanitizar entrada
            if self.sanitizer:
                username_clean = sanitize_string(username, 50)
                password_clean = sanitize_string(password, 128)
            else:
                username_clean = str(username)[:50]
                password_clean = str(password)[:128]

            # Verificar si la cuenta está bloqueada
            if self.verificar_cuenta_bloqueada(username_clean):
                return {
                    'success': False,
                    'message': f'Cuenta bloqueada. Intente nuevamente en {self.tiempo_bloqueo_minutos} minutos.',
                    'user_data': None,
                    'bloqueado': True
                }

            # Obtener datos del usuario
            user_data = self._obtener_usuario_por_nombre(username_clean)
            if not user_data:
                # Registrar intento fallido (incluso para usuarios inexistentes)
                self.registrar_intento_login(username_clean, False)
                return {
                    'success': False,
                    'message': 'Credenciales inválidas',
                    'user_data': None,
                    'bloqueado': False
                }

            # Verificar contraseña
            password_valida = self._verificar_password_segura(password_clean, user_data.get('password', ''))

            if password_valida:
                # Autenticación exitosa
                self.reset_intentos_login(username_clean)
                self.registrar_intento_login(username_clean, True)

                # Limpiar datos sensibles antes de retornar
                user_data_safe = user_data.copy()
                if 'password' in user_data_safe:
                    del user_data_safe['password']

                return {
                    'success': True,
                    'message': 'Autenticación exitosa',
                    'user_data': user_data_safe,
                    'bloqueado': False
                }
            else:
                # Contraseña incorrecta
                self.registrar_intento_login(username_clean, False)
                return {
                    'success': False,
                    'message': 'Credenciales inválidas',
                    'user_data': None,
                    'bloqueado': False
                }

        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return {
                'success': False,
                'message': 'Error interno del sistema',
                'user_data': None,
                'bloqueado': False
            }

    def cambiar_password_segura(self,
usuario_id: int,
        password_actual: str,
        password_nueva: str) -> Dict[str,
        Any]:
        """
        Cambio seguro de contraseña con validaciones.

        Args:
            usuario_id: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña

        Returns:
            Dict con resultado del cambio
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Validar fortaleza de la nueva contraseña
            validacion_password = self.validar_fortaleza_password(password_nueva)
            if not validacion_password['es_valida']:
                return {
                    'success': False,
                    'message': f"Contraseña no cumple requisitos: {', '.join(validacion_password['errores'])}"
                }

            cursor = self.db_connection.cursor()

            # Obtener datos actuales del usuario
            cursor.execute("SELECT username, password FROM usuarios WHERE id = ? AND activo = 1", (usuario_id,))
            user_data = cursor.fetchone()

            if not user_data:
                return {'success': False, 'message': 'Usuario no encontrado'}

            # Verificar contraseña actual
            if not self._verificar_password_segura(password_actual, user_data[1]):
                return {'success': False, 'message': 'Contraseña actual incorrecta'}

            # Generar hash seguro de la nueva contraseña
            password_hash = self._hashear_password_segura(password_nueva)

            # Actualizar en base de datos
            cursor.execute("""
                UPDATE usuarios
                SET password = ?, updated_at = GETDATE()
                WHERE id = ? AND activo = 1
            """, (password_hash, usuario_id))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'No se pudo actualizar la contraseña'}

            self.db_connection.commit()
            logger.info(f"Contraseña cambiada para usuario ID: {usuario_id}")

            return {'success': True, 'message': 'Contraseña actualizada exitosamente'}

        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    logger.error(f"Error en operación de base de datos: {e}")
                    return None
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                if cursor:
                    cursor.close()

    def validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña según políticas de seguridad.

        Args:
            password: Contraseña a validar

        Returns:
            Dict con resultado de validación
        """
        errores = []

        # Longitud mínima
        if len(password) < self.password_min_length:
            errores.append(f"Debe tener al menos {self.password_min_length} caracteres")

        # Al menos una letra mayúscula
        if not any(c.isupper() for c in password):
            errores.append("Debe contener al menos una letra mayúscula")

        # Al menos una letra minúscula
        if not any(c.islower() for c in password):
            errores.append("Debe contener al menos una letra minúscula")

        # Al menos un número
        if not any(c.isdigit() for c in password):
            errores.append("Debe contener al menos un número")

        # Al menos un carácter especial
        caracteres_especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in caracteres_especiales for c in password):
            errores.append("Debe contener al menos un carácter especial")

        # Verificar que no sea una contraseña común
        passwords_comunes = [
            "password", "123456", "qwerty", "admin", "usuario",
            "12345678", "password123", "admin123"
        ]
        if password.lower() in passwords_comunes:
            errores.append("No puede ser una contraseña común")

        return {
            'es_valida': len(errores) == 0,
            'errores': errores,
            'puntuacion': max(0, 100 - (len(errores) * 15))
        }

    def verificar_cuenta_bloqueada(self, username: str) -> bool:
        """
        Verifica si una cuenta está bloqueada por intentos fallidos.

        Args:
            username: Nombre de usuario

        Returns:
            True si está bloqueada
        """
        try:
            if not self.db_connection:
                return False

            cursor = self.db_connection.cursor()

            # Verificar intentos fallidos recientes
            tiempo_limite = datetime.datetime.now() - datetime.timedelta(minutes=self.tiempo_bloqueo_minutos)

            cursor.execute("""
                SELECT COUNT(*) FROM intentos_login
                WHERE username = ? AND exitoso = 0 AND fecha_intento > ?
            """, (username, tiempo_limite))

            intentos_recientes = cursor.fetchone()[0]

            return intentos_recientes >= self.max_intentos_login

        except Exception as e:
            logger.error(f"Error verificando bloqueo: {e}")
            return False
        finally:
            if 'cursor' in locals():
                if cursor:
                    cursor.close()

    def registrar_intento_login(self, username: str, exitoso: bool = False) -> None:
        """
        Registra un intento de login para auditoría y control de bloqueos.

        Args:
            username: Nombre de usuario
            exitoso: Si el intento fue exitoso
        """
        try:
            if not self.db_connection:
                return

            cursor = self.db_connection.cursor()

            # Crear tabla si no existe
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='intentos_login' AND xtype='U')
                CREATE TABLE intentos_login (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(50) NOT NULL,
                    fecha_intento DATETIME DEFAULT GETDATE(),
                    exitoso BIT NOT NULL,
                    ip_address NVARCHAR(45) NULL
                )
            """)

            # Insertar registro
            cursor.execute("""
                INSERT INTO intentos_login (username, exitoso, fecha_intento)
                VALUES (?, ?, GETDATE())
            """, (username, exitoso))

            self.db_connection.commit()

        except Exception as e:
            logger.error(f"Error registrando intento de login: {e}")
        finally:
            if 'cursor' in locals():
                if cursor:
                    cursor.close()

    def reset_intentos_login(self, username: str) -> bool:
        """
        Resetea los intentos fallidos de un usuario.

        Args:
            username: Nombre de usuario

        Returns:
            True si se reseteó correctamente
        """
        try:
            if not self.db_connection:
                return False

            cursor = self.db_connection.cursor()

            # Marcar intentos previos como obsoletos
            cursor.execute("""
                UPDATE intentos_login
                SET exitoso = NULL
                WHERE username = ? AND exitoso = 0
            """, (username,))

            self.db_connection.commit()
            return True

        except Exception as e:
            logger.error(f"Error reseteando intentos: {e}")
            return False
        finally:
            if 'cursor' in locals():
                if cursor:
                    cursor.close()

    def _obtener_usuario_por_nombre(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de usuario por nombre de usuario.

        Args:
            username: Nombre de usuario

        Returns:
            Datos del usuario o None
        """
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT id, username, password, nombre_completo, email,
                       rol, activo, created_at, updated_at
                FROM usuarios
                WHERE username = ? AND activo = 1
            """, (username,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'nombre_completo': row[3],
                'email': row[4],
                'rol': row[5],
                'activo': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            }

        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
        finally:
            if 'cursor' in locals():
                if cursor:
                    cursor.close()

    def _hashear_password_segura(self, password: str) -> str:
        """
        Genera hash seguro usando bcrypt.

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash seguro
        """
        try:
            # Usar bcrypt para hashing seguro
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hasheando contraseña: {e}")
            # Fallback a SHA256 (menos seguro pero funcional)
            return hashlib.sha256(password.encode()).hexdigest()

    def _verificar_password_segura(self, password: str, hash_almacenado: str) -> bool:
        """
        Verifica contraseña contra hash almacenado.

        Args:
            password: Contraseña en texto plano
            hash_almacenado: Hash almacenado

        Returns:
            True si coincide
        """
        try:
            # Intentar verificación con bcrypt primero
            if hash_almacenado.startswith('$2b$'):
                return bcrypt.checkpw(password.encode('utf-8'), hash_almacenado.encode('utf-8'))
            else:
                # Fallback para hashes SHA256 legacy
                return hashlib.sha256(password.encode()).hexdigest() == hash_almacenado
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
