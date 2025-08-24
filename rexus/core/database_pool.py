"""
DatabasePool - Pool de conexiones de base de datos para Rexus
Manejo eficiente de múltiples conexiones de BD
"""

import logging
import sqlite3
import threading
import time
import queue
from contextlib import contextmanager
from typing import Optional, Dict, Any

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class DatabasePool:
    """Pool de conexiones de base de datos."""
    
    def __init__(self, database_path: str, max_connections: int = 10):
        """Inicializa el pool de conexiones."""
        self.database_path = database_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.RLock()
        
        # Crear conexiones iniciales
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool con conexiones."""
        try:
            for _ in range(self.max_connections):
                connection = self._create_connection()
                if connection:
                    self.pool.put(connection)
                    self.active_connections += 1
            
            logger.info(f"Pool de BD inicializado con {self.active_connections} conexiones")
            
        except Exception as e:
            logger.error(f"Error inicializando pool: {e}")
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Crea una nueva conexión a la base de datos."""
        try:
            connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            connection.row_factory = sqlite3.Row
            return connection
            
        except Exception as e:
            logger.error(f"Error creando conexión: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Obtiene una conexión del pool (context manager)."""
        connection = None
        start_time = time.time()
        
        try:
            # Intentar obtener conexión del pool
            try:
                connection = self.pool.get(timeout=10.0)  # Esperar máximo 10 segundos
                
                wait_time = time.time() - start_time
                if wait_time > 1.0:  # Log si espera más de 1 segundo
                    logger.warning("Espera larga para obtener conexión", extra={
                        "wait_time_seconds": round(wait_time, 2),
                        "database": self.database_path
                    })
                
            except queue.Empty:
                # Si no hay conexiones disponibles, crear una nueva
                logger.warning("Pool agotado, creando conexión temporal")
                connection = self._create_connection()
                if not connection:
                    raise Exception("No se pudo obtener conexión de BD")
            
            yield connection
            
        except Exception as e:
            logger.error(f"Error en conexión de BD: {e}")
            # Si hay error, cerrar la conexión problemática
            if connection:
                try:
                    connection.close()
                except:
                    pass
                connection = None
            raise
            
        finally:
            # Devolver conexión al pool si es válida
            if connection:
                try:
                    # Verificar que la conexión sigue siendo válida
                    connection.execute("SELECT 1").fetchone()
                    self.pool.put(connection)
                except:
                    # Si la conexión está corrupta, crear una nueva
                    try:
                        connection.close()
                    except:
                        pass
                    
                    new_connection = self._create_connection()
                    if new_connection:
                        self.pool.put(new_connection)
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Ejecuta una consulta usando el pool."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return [{"affected_rows": cursor.rowcount}]
    
    def close_all_connections(self):
        """Cierra todas las conexiones del pool."""
        with self.lock:
            while not self.pool.empty():
                try:
                    connection = self.pool.get_nowait()
                    connection.close()
                    self.active_connections -= 1
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error cerrando conexión: {e}")
            
            logger.info("Pool de conexiones cerrado")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del pool."""
        return {
            "database_path": self.database_path,
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.pool.qsize(),
            "pool_utilization": round((self.max_connections - self.pool.qsize()) / self.max_connections * 100, 2)
        }

# Instancia global
_database_pool: Optional[DatabasePool] = None

def get_database_pool() -> DatabasePool:
    """Obtiene la instancia global del pool de BD."""
    global _database_pool
    if _database_pool is None:
        _database_pool = DatabasePool("rexus.db")
    return _database_pool

def init_database_pool(database_path: str, max_connections: int = 10) -> DatabasePool:
    """Inicializa el pool global de BD."""
    global _database_pool
    _database_pool = DatabasePool(database_path, max_connections)
    return _database_pool
