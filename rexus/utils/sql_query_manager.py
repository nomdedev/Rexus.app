"""
Rexus.app - SQL Query Manager

Gestor de consultas SQL que proporciona una interfaz segura para ejecutar
consultas parametrizadas contra la base de datos de usuarios.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import pyodbc

logger = logging.getLogger(__name__)

class SQLQueryManager:
    """
    Gestor de consultas SQL que maneja la ejecución segura de queries
    contra la base de datos de usuarios.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el SQLQueryManager.

        Args:
            db_connection: Conexión opcional a la base de datos
        """
        self.db_connection = db_connection
        self._connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """Construye la cadena de conexión usando variables de entorno."""
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        server = os.getenv('DB_SERVER', 'localhost')
        database = os.getenv('DB_USERS', 'users')  # Usar DB_USERS del .env
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')

        if not all([server, database, username, password]):
            raise ValueError("Faltan variables de entorno para la conexión a BD. Requeridas: DB_SERVER, DB_USERS, DB_USERNAME, DB_PASSWORD")

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

    @contextmanager
    def _get_connection(self):
        """Context manager para obtener una conexión a la base de datos."""
        connection = None
        try:
            if self.db_connection and hasattr(self.db_connection, '_connection') and self.db_connection._connection:
                # Usar conexión existente si está disponible
                connection = self.db_connection._connection
                cursor = connection.cursor()
                yield cursor
            else:
                # Crear nueva conexión
                connection = pyodbc.connect(self._connection_string, timeout=10, autocommit=False)
                cursor = connection.cursor()
                try:
                    yield cursor
                finally:
                    if connection:
                        connection.commit()
        except pyodbc.Error as e:
            logger.error(f"[SQL] Error en operación de base de datos: {e}")
            if connection and connection != (self.db_connection._connection if self.db_connection else None):
                connection.rollback()
            raise
        finally:
            if connection and connection != (self.db_connection._connection if self.db_connection else None):
                connection.close()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta

        Returns:
            Lista de tuplas con los resultados
        """
        try:
            with self._get_connection() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results = cursor.fetchall()
                logger.debug(f"[SQL] Query ejecutada exitosamente: {query[:50]}...")
                return results

        except pyodbc.Error as e:
            logger.error(f"[SQL] Error ejecutando query: {e}")
            raise

    def execute_non_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta que no retorna resultados (INSERT, UPDATE, DELETE).

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta

        Returns:
            Número de filas afectadas
        """
        try:
            with self._get_connection() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                rows_affected = cursor.rowcount
                logger.debug(f"[SQL] Non-query ejecutada exitosamente: {query[:50]}... ({rows_affected} filas)")
                return rows_affected

        except pyodbc.Error as e:
            logger.error(f"[SQL] Error ejecutando non-query: {e}")
            raise

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Obtiene los módulos permitidos para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de módulos permitidos
        """
        query = "SELECT modulo FROM permisos_usuario WHERE usuario_id = ?"
        results = self.execute_query(query, (user_id,))
        return [row[0] for row in results]

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un usuario por nombre de usuario.

        Args:
            username: Nombre de usuario

        Returns:
            Diccionario con información del usuario o None
        """
        query = """
            SELECT id, username, rol, activo
            FROM usuarios
            WHERE username = ? AND activo = 1
        """
        results = self.execute_query(query, (username,))

        if results:
            row = results[0]
            return {
                'id': row[0],
                'username': row[1],
                'rol': row[2],
                'activo': row[3]
            }
        return None

    def validate_credentials(self, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """
        Valida las credenciales de un usuario.

        Args:
            username: Nombre de usuario
            password_hash: Hash de la contraseña

        Returns:
            Diccionario con información del usuario si válido
        """
        query = """
            SELECT id, username, rol, activo
            FROM usuarios
            WHERE username = ? AND password_hash = ? AND activo = 1
        """
        results = self.execute_query(query, (username, password_hash))

        if results:
            row = results[0]
            return {
                'id': row[0],
                'username': row[1],
                'rol': row[2],
                'activo': row[3]
            }
        return None
