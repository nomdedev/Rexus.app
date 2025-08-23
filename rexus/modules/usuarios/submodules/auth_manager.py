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
                                'user_data': None,
                    'bloqueado': False
                }

        except Exception as e:
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
            query = self.sql_manager.get_query('usuarios', 'obtener_usuario_por_id')
            cursor.execute(query, (usuario_id,))
            user_data = cursor.fetchone()

            if not user_data:
                return {'success': False, 'message': 'Usuario no encontrado'}

            # Verificar contraseña actual
            if not self._verificar_password_segura(password_actual, user_data[1]):
                return {'success': False, 'message': 'Contraseña actual incorrecta'}

            # Generar hash seguro de la nueva contraseña
            password_hash = self._hashear_password_segura(password_nueva)

            # Actualizar en base de datos
            query = self.sql_manager.get_query('usuarios', 'actualizar_password')
            cursor.execute(query, (password_hash, usuario_id))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'No se pudo actualizar la contraseña'}

            self.db_connection.commit()
            logger.info(f"Contraseña cambiada para usuario ID: {usuario_id}")

            return {'success': True, 'message': 'Contraseña actualizada exitosamente'}

        except Exception as e:
                try:
                    self.db_connection.rollback()
                except Exception:
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
            query_create = self.sql_manager.get_query('usuarios', 'crear_tabla_intentos')
            cursor.execute(query_create)

            # Insertar registro
            query_insert = self.sql_manager.get_query('usuarios', 'insertar_intento_login')
            cursor.execute(query_insert, (username, exitoso))

            self.db_connection.commit()

        except Exception as e:
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
            query = self.sql_manager.get_query('usuarios', 'resetear_intentos_fallidos')
            cursor.execute(query, (username,))

            self.db_connection.commit()
            return True

        except Exception as e:
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

            query = self.sql_manager.get_query('usuarios', 'obtener_usuario_login')
            cursor.execute(query, (username,))

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
