"""
Connection Pool para Base de Datos - Rexus.app
Gestiona eficientemente las conexiones a SQL Server

Implementa:
- Pool de conexiones reutilizables
- Configuración de timeout
- Manejo de conexiones caídas
- Métricas de uso del pool
- Soporte para múltiples bases de datos
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, List, Any
from contextlib import contextmanager
import pyodbc

logger = logging.getLogger(__name__)


class PoolState(Enum):
    """Estados del pool de conexiones."""
    INITIALIZING = "initializing"
    READY = "ready"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class PoolConfig:
    """Configuración del pool de conexiones."""
    # Tamaño del pool
    min_connections: int = 2
    max_connections: int = 10
    connection_timeout: int = 30  # segundos

    # Reciclaje de conexiones
    max_connection_age: int = 3600  # segundos (1 hora)
    max_idle_time: int = 600  # segundos (10 minutos)

    # Reconexión
    max_retries: int = 3
    retry_delay: float = 1.0  # segundos

    # Salud de la conexión
    health_check_interval: int = 60  # segundos
    health_check_timeout: int = 5  # segundos

    # SQLAlchemy style pool
    pool_pre_ping: bool = True  # Verificar conexión antes de usar
    pool_recycle: int = 3600  # Reciclar conexión después de N segundos


@dataclass
class ConnectionWrapper:
    """Wrapper para una conexión del pool."""
    connection: pyodbc.Connection
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    in_use: bool = False
    use_count: int = 0
    is_valid: bool = True

    @property
    def age(self) -> timedelta:
        """Edad de la conexión."""
        return datetime.now() - self.created_at

    @property
    def idle_time(self) -> timedelta:
        """Tiempo idle de la conexión."""
        return datetime.now() - self.last_used


class DatabaseConnectionPool:
    """
    Pool de conexiones para SQL Server.

    Implementa un pool eficiente con:
    - Mínimo y máximo de conexiones
    - Reciclaje automático de conexiones viejas
    - Health checks periódicos
    - Reconexión automática ante fallos

    Example:
        pool = DatabaseConnectionPool(
            connection_string="...",
            config=PoolConfig(max_connections=10)
        )

        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
    """

    def __init__(self,
                 connection_string: str,
                 database_name: str,
                 config: PoolConfig = None):
        """
        Inicializa el pool de conexiones.

        Args:
            connection_string: String de conexión ODBC
            database_name: Nombre de la base de datos
            config: Configuración del pool
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.config = config or PoolConfig()

        self._state = PoolState.INITIALIZING
        self._connections: List[ConnectionWrapper] = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._stats = {
            'created': 0,
            'reused': 0,
            'closed': 0,
            'errors': 0,
            'wait_count': 0,
            'wait_time_total': 0.0
        }

        # Inicializar conexiones mínimas
        self._initialize_min_connections()

        # Iniciar health check thread
        self._health_check_thread = None
        if self.config.health_check_interval > 0:
            self._start_health_check()

        self._state = PoolState.READY
        logger.info(f"Connection pool initialized for {database_name}")

    def _initialize_min_connections(self):
        """Inicializa las conexiones mínimas del pool."""
        for _ in range(self.config.min_connections):
            try:
                wrapper = self._create_connection()
                if wrapper:
                    self._connections.append(wrapper)
            except Exception as e:
                logger.error(f"Error initializing min connection: {e}")

    def _create_connection(self) -> Optional[ConnectionWrapper]:
        """Crea una nueva conexión a la base de datos."""
        try:
            conn = pyodbc.connect(
                self.connection_string,
                timeout=self.config.connection_timeout
            )

            # Configurar conexión
            conn.autocommit = False
            conn.setencoding(encoding='utf-8')

            wrapper = ConnectionWrapper(connection=conn)
            self._stats['created'] += 1

            logger.debug(f"Created new connection for {self.database_name}")
            return wrapper

        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Error creating connection for {self.database_name}: {e}")
            return None

    def _is_connection_valid(self, wrapper: ConnectionWrapper) -> bool:
        """Verifica si una conexión es válida."""
        if not wrapper.is_valid:
            return False

        # Verificar edad máxima
        if wrapper.age.total_seconds() > self.config.max_connection_age:
            logger.debug(f"Connection too old: {wrapper.age}")
            return False

        # Verificar si la conexión está cerrada
        try:
            if wrapper.connection.closed:
                return False
        except Exception:
            return False

        # Health check si está configurado
        if self.config.pool_pre_ping:
            try:
                cursor = wrapper.connection.cursor()
                cursor.execute("SELECT 1").fetchone()
                cursor.close()
            except Exception:
                logger.debug("Health check failed")
                return False

        return True

    def _close_connection(self, wrapper: ConnectionWrapper):
        """Cierra una conexión."""
        try:
            if not wrapper.connection.closed:
                wrapper.connection.close()
            self._stats['closed'] += 1
        except Exception as e:
            logger.debug(f"Error closing connection: {e}")

    @contextmanager
    def get_connection(self, timeout: float = None):
        """
        Obtiene una conexión del pool.

        Args:
            timeout: Tiempo máximo de espera (usa config por defecto)

        Yields:
            Conexión pyodbc

        Raises:
            TimeoutError: Si no hay conexión disponible
            ConnectionError: Si hay error de conexión
        """
        if timeout is None:
            timeout = self.config.connection_timeout

        wrapper = None
        start_time = time.time()

        try:
            # Buscar conexión disponible
            with self._lock:
                deadline = start_time + timeout

                while time.time() < deadline:
                    # Buscar conexión libre y válida
                    for w in self._connections:
                        if not w.in_use and self._is_connection_valid(w):
                            w.in_use = True
                            w.last_used = datetime.now()
                            w.use_count += 1
                            wrapper = w
                            self._stats['reused'] += 1
                            break

                    if wrapper:
                        break

                    # Si no hay conexión y no hemos alcanzado el máximo, crear una
                    if (len(self._connections) < self.config.max_connections and
                            not any(not w.in_use for w in self._connections)):
                        new_wrapper = self._create_connection()
                        if new_wrapper:
                            new_wrapper.in_use = True
                            self._connections.append(new_wrapper)
                            wrapper = new_wrapper
                            break

                    # Esperar a que se libere una conexión
                    wait_time = min(0.1, deadline - time.time())
                    if wait_time > 0:
                        self._stats['wait_count'] += 1
                        self._condition.wait(wait_time)

                # Registrar tiempo de espera
                wait_duration = time.time() - start_time
                self._stats['wait_time_total'] += wait_duration

            if wrapper is None:
                raise TimeoutError(
                    f"No connection available after {timeout}s for {self.database_name}"
                )

            logger.debug(f"Got connection for {self.database_name} (use count: {wrapper.use_count})")

            yield wrapper.connection

        except Exception as e:
            logger.error(f"Error using connection: {e}")
            self._stats['errors'] += 1
            raise

        finally:
            # Liberar la conexión
            if wrapper:
                with self._lock:
                    wrapper.in_use = False
                    self._condition.notify()

                    # Verificar si debemos reciclar la conexión
                    if wrapper.idle_time.total_seconds() > self.config.max_idle_time:
                        if len(self._connections) > self.config.min_connections:
                            self._connections.remove(wrapper)
                            self._close_connection(wrapper)
                            logger.debug("Recycled idle connection")

    def recycle_connections(self):
        """Recicla conexiones viejas o inválidas."""
        with self._lock:
            to_remove = []

            for wrapper in self._connections:
                if not wrapper.in_use:
                    if not self._is_connection_valid(wrapper):
                        to_remove.append(wrapper)
                    elif (len(self._connections) > self.config.min_connections and
                          wrapper.idle_time.total_seconds() > self.config.max_idle_time):
                        to_remove.append(wrapper)

            for wrapper in to_remove:
                self._connections.remove(wrapper)
                self._close_connection(wrapper)

            if to_remove:
                logger.info(f"Recycled {len(to_remove)} connections for {self.database_name}")

    def _start_health_check(self):
        """Inicia el thread de health check."""
        def health_check_loop():
            while self._state == PoolState.READY:
                try:
                    time.sleep(self.config.health_check_interval)
                    self.recycle_connections()
                except Exception as e:
                    logger.error(f"Error in health check: {e}")

        self._health_check_thread = threading.Thread(
            target=health_check_loop,
            name=f"HealthCheck-{self.database_name}",
            daemon=True
        )
        self._health_check_thread.start()

    def close(self):
        """Cierra todas las conexiones del pool."""
        self._state = PoolState.CLOSING

        with self._lock:
            for wrapper in self._connections:
                self._close_connection(wrapper)
            self._connections.clear()

        self._state = PoolState.CLOSED
        logger.info(f"Connection pool closed for {self.database_name}")

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del pool."""
        with self._lock:
            active = sum(1 for w in self._connections if w.in_use)
            idle = len(self._connections) - active

            return {
                'database': self.database_name,
                'state': self._state.value,
                'connections': {
                    'total': len(self._connections),
                    'active': active,
                    'idle': idle,
                    'min': self.config.min_connections,
                    'max': self.config.max_connections
                },
                'stats': self._stats.copy(),
                'avg_wait_time': (
                    self._stats['wait_time_total'] / self._stats['wait_count']
                    if self._stats['wait_count'] > 0 else 0
                )
            }

    def execute_query(self, query: str, params: tuple = None,
                      timeout: int = 30) -> List[tuple]:
        """
        Ejecuta una query usando el pool.

        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query
            timeout: Timeout de ejecución

        Returns:
            Lista de tuplas con resultados
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            if timeout:
                cursor.timeout = timeout

            results = cursor.fetchall()
            cursor.close()

            return results


# Manager global de pools
class ConnectionPoolManager:
    """Gestor centralizado de pools de conexión."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._pools: Dict[str, DatabaseConnectionPool] = {}
        return cls._instance

    def register_pool(self, database_name: str,
                      connection_string: str,
                      config: PoolConfig = None) -> DatabaseConnectionPool:
        """Registra un pool para una base de datos."""
        if database_name in self._pools:
            return self._pools[database_name]

        pool = DatabaseConnectionPool(
            connection_string=connection_string,
            database_name=database_name,
            config=config
        )

        self._pools[database_name] = pool
        return pool

    def get_pool(self, database_name: str) -> Optional[DatabaseConnectionPool]:
        """Obtiene un pool por nombre de base de datos."""
        return self._pools.get(database_name)

    def close_all(self):
        """Cierra todos los pools."""
        for pool in self._pools.values():
            pool.close()
        self._pools.clear()

    def get_all_stats(self) -> Dict[str, Dict]:
        """Obtiene estadísticas de todos los pools."""
        return {
            name: pool.get_stats()
            for name, pool in self._pools.items()
        }


# Instancia global
_pool_manager: Optional[ConnectionPoolManager] = None


def get_pool_manager() -> ConnectionPoolManager:
    """Obtiene la instancia singleton del PoolManager."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
    return _pool_manager


def init_pools_from_env():
    """
    Inicializa pools desde variables de entorno.

    Variables requeridas:
    - DB_SERVER, DB_DRIVER, DB_USERNAME, DB_PASSWORD
    - DB_USERS, DB_INVENTARIO, DB_AUDITORIA
    """
    import os

    server = os.getenv("DB_SERVER")
    driver = os.getenv("DB_DRIVER")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    if not all([server, driver, username, password]):
        raise ValueError("Faltan variables de entorno de base de datos")

    manager = get_pool_manager()
    config = PoolConfig()

    # Base template de connection string
    def build_conn_string(database: str) -> str:
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )

    # Registrar pools
    databases = {
        'users': os.getenv("DB_USERS"),
        'inventario': os.getenv("DB_INVENTARIO"),
        'auditoria': os.getenv("DB_AUDITORIA")
    }

    for name, db_name in databases.items():
        if db_name:
            manager.register_pool(
                database_name=name,
                connection_string=build_conn_string(db_name),
                config=config
            )

    return manager


# Decorador para ejecutar queries con pool
def with_db_pool(database: str):
    """
    Decorador para ejecutar funciones con pool de conexiones.

    Example:
        @with_db_pool('inventario')
        def get_productos(pool):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                return cursor.execute("SELECT * FROM productos").fetchall()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_pool_manager()
            pool = manager.get_pool(database)

            if pool is None:
                raise ValueError(f"No pool registered for database: {database}")

            # Inyectar pool como primer argumento si no se pasó
            if args and isinstance(args[0], DatabaseConnectionPool):
                return func(*args, **kwargs)

            return func(pool, *args, **kwargs)

        return wrapper
    return decorator
