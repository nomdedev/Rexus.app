"""
Rexus.app - Conexión a Base de Datos de Usuarios

Implementación de la conexión a la base de datos de usuarios usando pyodbc.
Maneja la conexión segura a SQL Server y proporciona métodos para consultas de usuarios y permisos.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import pyodbc

logger = logging.getLogger(__name__)

class UsersDatabaseConnection:
    """
    Clase para manejar la conexión a la base de datos de usuarios.
    Implementa el patrón Singleton para mantener una única conexión.
    """

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connection is None:
            self._connection_string = self._build_connection_string()
            self._connect()

    def _build_connection_string(self) -> str:
        """Construye la cadena de conexión usando variables de entorno."""
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        server = os.getenv('DB_SERVER', 'localhost')
        database = os.getenv('DB_USERS', 'users')  # Usando DB_USERS del .env
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')

        if not all([server, database, username, password]):
            raise ValueError("Faltan variables de entorno para la conexión a BD")

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

    def _connect(self):
        """Establece la conexión a la base de datos."""
        try:
            self._connection = pyodbc.connect(
                self._connection_string,
                timeout=10,
                autocommit=False
            )
            logger.info("[DB] Conexión exitosa a la base de datos de usuarios")
        except pyodbc.Error as e:
            logger.error(f"[DB] Error conectando a la base de datos: {e}")
            raise

    @contextmanager
    def get_cursor(self):
        """Context manager para obtener un cursor de la base de datos."""
        if self._connection is None:
            raise ConnectionError("No hay conexión activa a la base de datos")

        cursor = None
        try:
            cursor = self._connection.cursor()
            yield cursor
        except pyodbc.Error as e:
            logger.error(f"[DB] Error en operación de base de datos: {e}")
            if cursor:
                self._connection.rollback()
            raise
        else:
            self._connection.commit()
        finally:
            if cursor:
                cursor.close()

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Obtiene los módulos permitidos para un usuario específico.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de nombres de módulos permitidos
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT modulo FROM permisos_usuario
                    WHERE usuario_id = ?
                """, (user_id,))

                modules = [row[0] for row in cursor.fetchall()]
                logger.info(f"[DB] Permisos obtenidos para usuario {user_id}: {modules}")
                return modules

        except pyodbc.Error as e:
            logger.error(f"[DB] Error obteniendo permisos para usuario {user_id}: {e}")
            return []

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información de un usuario por su nombre de usuario.

        Args:
            username: Nombre de usuario

        Returns:
            Diccionario con información del usuario o None si no existe
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, rol, activo
                    FROM usuarios
                    WHERE username = ? AND activo = 1
                """, (username,))

                row = cursor.fetchone()
                if row:
                    user_data = {
                        'id': row[0],
                        'username': row[1],
                        'rol': row[2],
                        'activo': row[3]
                    }
                    logger.info(f"[DB] Usuario encontrado: {username}")
                    return user_data
                else:
                    logger.warning(f"[DB] Usuario no encontrado: {username}")
                    return None

        except pyodbc.Error as e:
            logger.error(f"[DB] Error obteniendo usuario {username}: {e}")
            return None

    def validate_user_credentials(self, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """
        Valida las credenciales de un usuario.

        Args:
            username: Nombre de usuario
            password_hash: Hash de la contraseña

        Returns:
            Diccionario con información del usuario si las credenciales son válidas
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, rol, activo
                    FROM usuarios
                    WHERE username = ? AND password_hash = ? AND activo = 1
                """, (username, password_hash))

                row = cursor.fetchone()
                if row:
                    user_data = {
                        'id': row[0],
                        'username': row[1],
                        'rol': row[2],
                        'activo': row[3]
                    }
                    logger.info(f"[DB] Credenciales válidas para usuario: {username}")
                    return user_data
                else:
                    logger.warning(f"[DB] Credenciales inválidas para usuario: {username}")
                    return None

        except pyodbc.Error as e:
            logger.error(f"[DB] Error validando credenciales para {username}: {e}")
            return None

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("[DB] Conexión cerrada exitosamente")
            except pyodbc.Error as e:
                logger.error(f"[DB] Error cerrando conexión: {e}")
            finally:
                self._connection = None
                UsersDatabaseConnection._instance = None
