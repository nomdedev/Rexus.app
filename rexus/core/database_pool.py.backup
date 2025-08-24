"""
Sistema de Connection Pooling para Rexus
Versión: 2.0.0 - Enterprise Ready
"""


import logging
logger = logging.getLogger(__name__)

import threading
import time
import queue
            
            wait_time = time.time() - start_time
            if wait_time > 1.0:  # Log si espera más de 1 segundo
                logger.warning("Espera larga para obtener conexión", extra={
                    "wait_time_seconds": round(wait_time, 2),
                    "database": self.database_name
                })

            yield connection

        except Exception as e:
            logger.exception("Error obteniendo conexión", extra={
                "database": self.database_name,
                "error": str(e)
            # FIXME: Specify concrete exception types instead of generic Exception})
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
