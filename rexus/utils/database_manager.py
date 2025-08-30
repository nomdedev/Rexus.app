"""
Mejoras en la gestión de base de datos para Rexus.app
"""

import logging
import sqlite3
import threading
from queue import Queue
from typing import Optional, List, Tuple, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Error personalizado para problemas de conexión a base de datos"""
    pass


class DatabasePool:
    """Pool de conexiones para SQLite"""

    def __init__(self, database_path: str, max_connections: int = 10):
        self.database_path = database_path
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_connection(self):
        """Obtiene una conexión del pool de forma segura"""
        connection = None
        try:
            # Intentar obtener conexión del pool
            if not self.connections.empty():
                connection = self.connections.get(timeout=1)
            else:
                # Crear nueva conexión si el pool está vacío
                with self.lock:
                    if self.active_connections < self.max_connections:
                        connection = sqlite3.connect(self.database_path)
                        self.active_connections += 1
                        self.logger.debug("Nueva conexión creada")

            if connection is None:
                raise DatabaseConnectionError("No se pudo obtener conexión del pool")

            yield connection

        except Exception as e:
            self.logger.error(f"Error obteniendo conexión: {e}")
            raise DatabaseConnectionError(f"Error de conexión: {e}")
        finally:
            # Devolver conexión al pool
            if connection:
                try:
                    # Verificar que la conexión siga siendo válida
                    connection.execute("SELECT 1")
                    self.connections.put(connection)
                except (sqlite3.Error, OSError):
                    # Conexión dañada, cerrarla y decrementar contador
                    connection.close()
                    with self.lock:
                        self.active_connections -= 1

    def close_all(self):
        """Cierra todas las conexiones del pool"""
        with self.lock:
            while not self.connections.empty():
                try:
                    conn = self.connections.get_nowait()
                    conn.close()
                except (sqlite3.Error, OSError, AttributeError):
                    pass
            self.active_connections = 0

        self.logger.info("All database connections closed")


class DatabaseManager:
    """Gestor mejorado de base de datos"""

    def __init__(self, database_path: str):
        self.pool = DatabasePool(database_path)
        self.logger = logging.getLogger('database')

    def execute_query(self, query: str, params: tuple = (), fetch: Optional[str] = None) -> Union[List, int, None]:
        """Ejecuta una consulta de forma segura"""
        with self.pool.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)

                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount

                conn.commit()
                return result

            except sqlite3.Error as e:
                conn.rollback()
                self.logger.error(f"Database query failed: {query[:100]}... Error: {e}")
                raise DatabaseConnectionError(f"Error en consulta: {e}")

    def execute_transaction(self, queries: List[Tuple[str, Tuple]]):
        """Ejecuta múltiples consultas en una transacción"""
        with self.pool.get_connection() as conn:
            try:
                cursor = conn.cursor()

                for query, params in queries:
                    cursor.execute(query, params or ())

                conn.commit()
                self.logger.info(f"Transaction completed with {len(queries)} queries")

            except sqlite3.Error as e:
                conn.rollback()
                self.logger.error(f"Transaction failed: {e}")
                raise DatabaseConnectionError(f"Error en transacción: {e}")


# Instancia global del manager
db_manager: Optional[DatabaseManager] = None


def initialize_database_manager(database_path: str):
    """Inicializa el gestor global de base de datos"""
    global db_manager
    db_manager = DatabaseManager(database_path)


def get_database_manager() -> DatabaseManager:
    """Obtiene el gestor de base de datos"""
    if not db_manager:
        raise RuntimeError("Database manager not initialized")
    return db_manager
