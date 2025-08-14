"""
Mejoras en la gestión de base de datos para Rexus.app
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Optional
from queue import Queue, Empty
from rexus.utils.logging_config import get_logger
from rexus.utils.error_handler import DatabaseConnectionError

class DatabasePool:
    """Pool de conexiones de base de datos mejorado"""

    def __init__(self, database_path: str, max_connections: int = 10):
        self.database_path = database_path
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.logger = get_logger('database')

        # Crear conexiones iniciales
        self._initialize_pool()

    def _initialize_pool(self):
        """Inicializa el pool de conexiones"""
        try:
            for _ in range(min(3, self.max_connections)):  # Iniciar con 3 conexiones
                conn = self._create_connection()
                if conn:
                    self.connections.put(conn)
                    self.active_connections += 1

            self.logger.info(f"Database pool initialized with {self.active_connections} connections")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise DatabaseConnectionError(f"No se pudo inicializar el pool de BD: {e}")

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Crea una nueva conexión a la base de datos"""
        try:
            conn = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )

            # Configuraciones de rendimiento
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA foreign_keys=ON")

            return conn
        except Exception as e:
            self.logger.error(f"Failed to create database connection: {e}")
            return None

    @contextmanager
    def get_connection(self, timeout: float = 10.0):
        """Obtiene una conexión del pool"""
        connection = None
        time.time()

        try:
            # Intentar obtener conexión existente
            try:
                connection = self.connections.get(timeout=timeout)
            except Empty:
                # Si no hay conexiones disponibles, crear una nueva
                with self.lock:
                    if self.active_connections < self.max_connections:
                        connection = self._create_connection()
                        if connection:
                            self.active_connections += 1
                        else:
                            raise DatabaseConnectionError("No se pudo crear nueva conexión")
                    else:
                        raise DatabaseConnectionError("Pool de conexiones agotado")

            # Verificar que la conexión esté activa
            if connection:
                try:
                    connection.execute("SELECT 1")
                except sqlite3.Error:
                    # Conexión inválida, crear una nueva
                    connection.close()
                    connection = self._create_connection()
                    if not connection:
                        raise DatabaseConnectionError("No se pudo restablecer la conexión")

            yield connection

        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Error de conexión a BD: {e}")
        finally:
            # Devolver conexión al pool
            if connection:
                try:
                    # Verificar que la conexión siga siendo válida
                    connection.execute("SELECT 1")
                    self.connections.put(connection)
                except:
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
                except:
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
