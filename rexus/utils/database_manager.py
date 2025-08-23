"""
Mejoras en la gestión de base de datos para Rexus.app
"""


import logging
logger = logging.getLogger(__name__)

import sqlite3
import threading
import time
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
        self.logger = get_logger('database')

    def execute_query(self,
query: str,
        params: tuple = (),
        fetch: str = None):
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

    def execute_transaction(self, queries: list):
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
