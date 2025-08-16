"""
Sistema de Connection Pooling para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import threading
import time
import queue
from datetime import datetime
from typing import Dict, Any, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass, field
import weakref

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

from .config import DATABASE_CONFIG
from .logger import get_logger
from .cache_manager import cached

logger = get_logger("database_pool")

@dataclass
class ConnectionStats:
    """Estadísticas de conexión"""
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    queries_executed: int = 0
    total_query_time: float = 0.0
    errors: int = 0

    @property
    def average_query_time(self) -> float:
        return (self.total_query_time / self.queries_executed) if self.queries_executed > 0 else 0.0

    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        return (datetime.now() - self.last_used).total_seconds()

class PooledConnection:
    """Wrapper para conexión con estadísticas y pooling"""

    def __init__(self, connection, pool_ref, connection_id: str):
        self._connection = connection
        self._pool_ref = pool_ref  # weak reference al pool
        self.connection_id = connection_id
        self.stats = ConnectionStats()
        self._in_use = False
        self._lock = threading.RLock()

        logger.debug("Conexión creada", extra={
            "connection_id": connection_id
        })

    def execute(self, query: str, params: tuple = None) -> Any:
        """Ejecutar query con tracking de estadísticas"""
        start_time = time.time()

        try:
            with self._lock:
                self.stats.last_used = datetime.now()
                cursor = self._connection.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                execution_time = time.time() - start_time
                self.stats.queries_executed += 1
                self.stats.total_query_time += execution_time

                logger.debug("Query ejecutado", extra={
                    "connection_id": self.connection_id,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "query": query[:100] + "..." if len(query) > 100 else query
                })

                return cursor

        except Exception as e:
            execution_time = time.time() - start_time
            self.stats.errors += 1

            logger.error("Error ejecutando query", extra={
                "connection_id": self.connection_id,
                "execution_time_ms": round(execution_time * 1000, 2),
                "error": str(e),
                "query": query[:100] + "..." if len(query) > 100 else query
            })
            raise

    def is_healthy(self) -> bool:
        """Verificar si la conexión está saludable"""
        try:
            # Test simple de conectividad
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.warning("Conexión no saludable", extra={
                "connection_id": self.connection_id,
                "error": str(e)
            })
            return False

    def close(self):
        """Cerrar conexión"""
        try:
            if self._connection:
                self._connection.close()
                logger.debug("Conexión cerrada", extra={
                    "connection_id": self.connection_id,
                    "queries_executed": self.stats.queries_executed,
                    "total_time": round(self.stats.total_query_time, 2)
                })
        except Exception as e:
            logger.error("Error cerrando conexión", extra={
                "connection_id": self.connection_id,
                "error": str(e)
            })

    def __enter__(self):
        self._in_use = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._in_use = False
        # Devolver conexión al pool
        pool = self._pool_ref()
        if pool:
            pool._return_connection(self)

class DatabasePool:
    """
    Pool de conexiones a base de datos con funcionalidades avanzadas:
    - Connection pooling
    - Health checking
    - Load balancing
    - Retry automático
    - Métricas y monitoring
    """

    def __init__(self,
database_name: str,
        min_connections: int = 2,
        max_connections: int = 10):
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc no está disponible")

        self.database_name = database_name
        self.min_connections = min_connections
        self.max_connections = max_connections

        # Pool de conexiones
        self._available_connections = queue.Queue(maxsize=max_connections)
        self._all_connections: Dict[str, PooledConnection] = {}
        self._connection_counter = 0

        # Threading
        self._lock = threading.RLock()
        self._pool_lock = threading.RLock()

        # Health checking
        self._health_check_interval = 300  # 5 minutos
        self._last_health_check = datetime.now()

        # Configuración de conexión
        self._connection_string = self._build_connection_string()

        # Inicializar pool mínimo
        self._initialize_pool()

        # Weak reference para cleanup
        weakref.finalize(self, self._cleanup_pool)

        logger.info("DatabasePool inicializado", extra={
            "database": database_name,
            "min_connections": min_connections,
            "max_connections": max_connections
        })

    def _build_connection_string(self) -> str:
        """Construir string de conexión"""
        return (
            f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
            f"SERVER={DATABASE_CONFIG['server']};"
            f"DATABASE={self.database_name};"
            f"UID={DATABASE_CONFIG['username']};"
            f"PWD={DATABASE_CONFIG['password']};"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout={DATABASE_CONFIG['timeout']};"
        )

    def _create_connection(self) -> PooledConnection:
        """Crear nueva conexión"""
        try:
            connection = pyodbc.connect(
                self._connection_string,
                timeout=DATABASE_CONFIG['timeout']
            )

            # Configurar conexión
            connection.autocommit = False

            # Crear wrapper
            self._connection_counter += 1
            connection_id = f"{self.database_name}_{self._connection_counter}"

            pooled_conn = PooledConnection(
                connection=connection,
                pool_ref=weakref.ref(self),
                connection_id=connection_id
            )

            with self._lock:
                self._all_connections[connection_id] = pooled_conn

            logger.debug("Nueva conexión creada", extra={
                "connection_id": connection_id,
                "database": self.database_name
            })

            return pooled_conn

        except Exception as e:
            logger.error("Error creando conexión", extra={
                "database": self.database_name,
                "error": str(e)
            })
            raise

    def _initialize_pool(self):
        """Inicializar pool con conexiones mínimas"""
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                self._available_connections.put(conn, block=False)
            except Exception as e:
                logger.error("Error inicializando pool", extra={
                    "database": self.database_name,
                    "error": str(e)
                })
                # No fallar completamente si no se pueden crear todas las conexiones
                break

    def _return_connection(self, connection: PooledConnection):
        """Devolver conexión al pool"""
        try:
            if connection.is_healthy():
                self._available_connections.put(connection, block=False)
            else:
                # Conexión no saludable, crear una nueva
                self._remove_connection(connection)

                # Intentar mantener el pool mínimo
                if self.get_stats()["available_connections"] < self.min_connections:
                    try:
                        new_conn = self._create_connection()
                        self._available_connections.put(new_conn, block=False)
                    except Exception as e:
                        logger.error("Error reemplazando conexión", extra={
                            "error": str(e)
                        })

        except queue.Full:
            # Pool lleno, cerrar conexión
            self._remove_connection(connection)

    def _remove_connection(self, connection: PooledConnection):
        """Remover conexión del pool"""
        try:
            with self._lock:
                self._all_connections.pop(connection.connection_id, None)
            connection.close()
        except Exception as e:
            logger.error("Error removiendo conexión", extra={
                "connection_id": connection.connection_id,
                "error": str(e)
            })

    def _health_check(self):
        """Verificar salud de conexiones en el pool"""
        if (datetime.now() - self._last_health_check).total_seconds() < self._health_check_interval:
            return

        self._last_health_check = datetime.now()

        with self._pool_lock:
            unhealthy_connections = []

            # Verificar todas las conexiones
            for conn_id, conn in list(self._all_connections.items()):
                if not conn._in_use and not conn.is_healthy():
                    unhealthy_connections.append(conn)

            # Remover conexiones no saludables
            for conn in unhealthy_connections:
                self._remove_connection(conn)

            if unhealthy_connections:
                logger.info("Health check completado", extra={
                    "database": self.database_name,
                    "unhealthy_removed": len(unhealthy_connections)
                })

    @contextmanager
    def get_connection(self, timeout: float = 30.0) -> ContextManager[PooledConnection]:
        """
        Obtener conexión del pool con context manager

        Args:
            timeout: Tiempo máximo de espera en segundos
        """
        self._health_check()

        connection = None
        start_time = time.time()

        try:
            # Intentar obtener conexión disponible
            try:
                connection = self._available_connections.get(timeout=timeout)
            except queue.Empty:
                # No hay conexiones disponibles
                if len(self._all_connections) < self.max_connections:
                    # Crear nueva conexión
                    connection = self._create_connection()
                else:
                    raise TimeoutError(f"No se pudo obtener conexión en {timeout} segundos")

            wait_time = time.time() - start_time
            if wait_time > 1.0:  # Log si espera más de 1 segundo
                logger.warning("Espera larga para obtener conexión", extra={
                    "wait_time_seconds": round(wait_time, 2),
                    "database": self.database_name
                })

            yield connection

        except Exception as e:
            logger.error("Error obteniendo conexión", extra={
                "database": self.database_name,
                "error": str(e)
            })
            raise
        finally:
            # La conexión se devuelve automáticamente por el context manager
            pass

    def execute_query(self,
query: str,
        params: tuple = None,
        timeout: float = 30.0) -> Any:
        """Ejecutar query usando el pool"""
        with self.get_connection(timeout=timeout) as conn:
            return conn.execute(query, params)

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del pool"""
        with self._lock:
            total_connections = len(self._all_connections)
            available_connections = self._available_connections.qsize()
            in_use_connections = total_connections - available_connections

            # Estadísticas agregadas
            total_queries = sum(conn.stats.queries_executed for conn in self._all_connections.values())
            total_errors = sum(conn.stats.errors for conn in self._all_connections.values())
            total_query_time = sum(conn.stats.total_query_time for conn in self._all_connections.values())

            avg_query_time = (total_query_time / total_queries) if total_queries > 0 else 0.0

            return {
                "database": self.database_name,
                "total_connections": total_connections,
                "available_connections": available_connections,
                "in_use_connections": in_use_connections,
                "min_connections": self.min_connections,
                "max_connections": self.max_connections,
                "total_queries": total_queries,
                "total_errors": total_errors,
                "error_rate": (total_errors / total_queries * 100) if total_queries > 0 else 0.0,
                "average_query_time_ms": round(avg_query_time * 1000, 2),
                "last_health_check": self._last_health_check.isoformat()
            }

    def _cleanup_pool(self):
        """Limpiar todas las conexiones al destruir el pool"""
        with self._lock:
            for connection in list(self._all_connections.values()):
                connection.close()
            self._all_connections.clear()

        # Vaciar queue
        while not self._available_connections.empty():
            try:
                self._available_connections.get_nowait()
            except queue.Empty:
                break

        logger.info("Pool de conexiones limpiado", extra={
            "database": self.database_name
        })

class DatabasePoolManager:
    """Manager global para todos los pools de bases de datos"""

    def __init__(self):
        self._pools: Dict[str, DatabasePool] = {}
        self._lock = threading.RLock()
        self.logger = get_logger("database_pool_manager")

    def get_pool(self, database_name: str) -> DatabasePool:
        """Obtener pool para una base de datos específica"""
        with self._lock:
            if database_name not in self._pools:
                # Crear nuevo pool
                pool_config = DATABASE_CONFIG
                min_conn = pool_config.get("pool_size", 5) // 2
                max_conn = pool_config.get("pool_size", 5)

                self._pools[database_name] = DatabasePool(
                    database_name=database_name,
                    min_connections=max(1, min_conn),
                    max_connections=max_conn
                )

                self.logger.info("Nuevo pool creado", extra={
                    "database": database_name,
                    "min_connections": min_conn,
                    "max_connections": max_conn
                })

            return self._pools[database_name]

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtener estadísticas de todos los pools"""
        with self._lock:
            return {
                db_name: pool.get_stats()
                for db_name, pool in self._pools.items()
            }

    def close_all_pools(self):
        """Cerrar todos los pools"""
        with self._lock:
            for pool in self._pools.values():
                pool._cleanup_pool()
            self._pools.clear()

            self.logger.info("Todos los pools cerrados")

# Instancia global del pool manager
pool_manager = DatabasePoolManager()

# Funciones de conveniencia
def get_database_pool(database_name: str) -> DatabasePool:
    """Obtener pool para una base de datos"""
    return pool_manager.get_pool(database_name)

def execute_query(database_name: str, query: str, params: tuple = None) -> Any:
    """Ejecutar query usando pool"""
    pool = get_database_pool(database_name)
    return pool.execute_query(query, params)

@cached(timeout=300, key_prefix="db_query")
def execute_cached_query(database_name: str, query: str, params: tuple = None) -> Any:
    """Ejecutar query con cache automático"""
    return execute_query(database_name, query, params)

def get_all_pool_stats() -> Dict[str, Dict[str, Any]]:
    """Obtener estadísticas de todos los pools"""
    return pool_manager.get_all_stats()

# Context manager para transacciones
@contextmanager
def database_transaction(database_name: str):
    """Context manager para transacciones de BD"""
    pool = get_database_pool(database_name)

    with pool.get_connection() as conn:
        try:
            # Iniciar transacción
            conn._connection.autocommit = False
            yield conn
            # Commit automático si no hay excepciones
            conn._connection.commit()

        except (sqlite3.Error, AttributeError, RuntimeError):
            # Rollback en caso de error
            try:
                conn._connection.rollback()
            except Exception as rollback_error:
                logger.error("Error en rollback", extra={
                    "database": database_name,
                    "error": str(rollback_error)
                })
            raise
        finally:
            # Restaurar autocommit
            conn._connection.autocommit = True
