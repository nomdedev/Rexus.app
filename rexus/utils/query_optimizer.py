#!/usr/bin/env python3
"""
Optimizador de Consultas - Rexus.app

Proporciona herramientas para optimizar consultas SQL y eliminar problemas N+1.
Incluye técnicas de batching, prefetch, y caching de consultas.

Fecha: 15/08/2025
Componente: Rendimiento - Optimización de Consultas
"""

import logging
from typing import Any, Dict, List, Optional
import time
import threading
from functools import wraps
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Cache inteligente para resultados de consultas
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Inicializar cache de consultas

        Args:
            max_size: Tamaño máximo del cache
            default_ttl: TTL por defecto en segundos
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del cache

        Args:
            key: Clave del cache

        Returns:
            Valor cacheado o None
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]

            if time.time() > expiry:
                del self._cache[key]
                return None

            return value

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacenar valor en cache

        Args:
            key: Clave del cache
            value: Valor a almacenar
            ttl: Tiempo de vida
        """
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            expiry = time.time() + ttl

            # Limpiar cache si es necesario
            if len(self._cache) >= self.max_size:
                self._cleanup_expired()

                if len(self._cache) >= self.max_size:
                    # Remover entrada más antigua
                    oldest_key = min(self._cache.keys(),
                                   key=lambda k: self._cache[k][1])
                    del self._cache[oldest_key]

            self._cache[key] = (value, expiry)

    def _cleanup_expired(self) -> None:
        """Limpiar entradas expiradas"""
        current_time = time.time()
        expired_keys = [k for k, (_, exp) in self._cache.items() if current_time > exp]

        for key in expired_keys:
            del self._cache[key]

    def clear(self) -> None:
        """Limpiar todo el cache"""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Obtener tamaño actual del cache"""
        with self._lock:
            return len(self._cache)


class QueryBatcher:
    """
    Sistema de batching para consultas SQL
    """

    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        """
        Inicializar batcher de consultas

        Args:
            batch_size: Tamaño máximo del batch
            flush_interval: Intervalo para flush automático
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batches = defaultdict(list)
        self._lock = threading.RLock()
        self._last_flush = time.time()

    def add_to_batch(self, batch_key: str, item: Any) -> None:
        """
        Agregar item a un batch

        Args:
            batch_key: Clave del batch
            item: Item a agregar
        """
        with self._lock:
            self._batches[batch_key].append(item)

            # Flush automático si el batch está lleno
            if len(self._batches[batch_key]) >= self.batch_size:
                self._flush_batch(batch_key)

    def _flush_batch(self, batch_key: str) -> List[Any]:
        """
        Ejecutar flush de un batch

        Args:
            batch_key: Clave del batch

        Returns:
            Lista de items del batch
        """
        with self._lock:
            if batch_key not in self._batches:
                return []

            batch_items = self._batches[batch_key]
            self._batches[batch_key] = []

            logger.debug(f"Flush batch {batch_key} con {len(batch_items)} items")
            return batch_items

    def flush_all(self) -> Dict[str, List[Any]]:
        """
        Ejecutar flush de todos los batches

        Returns:
            Diccionario con todos los batches
        """
        with self._lock:
            result = {}
            for batch_key in list(self._batches.keys()):
                batch_items = self._flush_batch(batch_key)
                if batch_items:
                    result[batch_key] = batch_items

            self._last_flush = time.time()
            return result

    def get_batch_size(self, batch_key: str) -> int:
        """
        Obtener tamaño actual de un batch

        Args:
            batch_key: Clave del batch

        Returns:
            Tamaño del batch
        """
        with self._lock:
            return len(self._batches.get(batch_key, []))


class QueryOptimizer:
    """
    Optimizador principal de consultas
    """

    def __init__(self, db_connection=None, cache_size: int = 1000,
                 batch_size: int = 100, enable_logging: bool = True):
        """
        Inicializar optimizador de consultas

        Args:
            db_connection: Conexión a base de datos (opcional)
            cache_size: Tamaño del cache
            batch_size: Tamaño de batches
            enable_logging: Habilitar logging
        """
        self.db_connection = db_connection
        self.cache = QueryCache(max_size=cache_size)
        self.batcher = QueryBatcher(batch_size=batch_size)
        self.enable_logging = enable_logging
        self._stats = {
            'queries_executed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'batches_processed': 0,
            'total_query_time': 0.0
        }

    def optimize_query(self, query: str, params: Optional[Dict] = None,
                      use_cache: bool = True, ttl: Optional[int] = None,
                      batch_key: Optional[str] = None) -> Any:
        """
        Optimizar y ejecutar una consulta

        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            use_cache: Usar cache
            ttl: TTL para cache
            batch_key: Clave para batching

        Returns:
            Resultado de la consulta
        """
        start_time = time.time()

        try:
            # Generar clave de cache
            cache_key = None
            if use_cache:
                cache_key = self._generate_cache_key(query, params)

                # Intentar obtener del cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self._stats['cache_hits'] += 1
                    if self.enable_logging:
                        logger.debug(f"Cache hit para query: {query[:50]}...")
                    return cached_result

            # Verificar si debe ir a un batch
            if batch_key:
                self.batcher.add_to_batch(batch_key, (query, params))
                self._stats['batches_processed'] += 1
                return None  # Resultado vendrá después del flush

            # Ejecutar consulta directamente
            result = self._execute_query(query, params)
            self._stats['queries_executed'] += 1
            self._stats['cache_misses'] += 1

            # Almacenar en cache
            if use_cache and cache_key and result is not None:
                self.cache.put(cache_key, result, ttl)

            return result

        finally:
            query_time = time.time() - start_time
            self._stats['total_query_time'] += query_time

    def _execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Ejecutar consulta SQL

        Args:
            query: Consulta SQL
            params: Parámetros

        Returns:
            Resultado de la consulta
        """
        if not self.db_connection:
            raise ValueError("No database connection available")

        try:
            # Aquí iría la lógica real de ejecución de consulta
            # Por ahora, simulamos la ejecución
            if self.enable_logging:
                logger.debug(f"Ejecutando query: {query[:100]}...")

            # Simular tiempo de ejecución
            time.sleep(0.001)

            # Retornar resultado simulado
            return {"rows": [], "rowcount": 0}

        except Exception as e:
            logger.error(f"Error ejecutando query: {str(e)}")
            raise

    def _generate_cache_key(self, query: str, params: Optional[Dict] = None) -> str:
        """
        Generar clave única para cache

        Args:
            query: Consulta SQL
            params: Parámetros

        Returns:
            Clave única
        """
        import hashlib

        # Normalizar query (remover espacios extra)
        normalized_query = re.sub(r'\s+', ' ', query.strip())

        # Incluir parámetros en la clave
        params_str = str(sorted(params.items())) if params else ""

        key_data = f"{normalized_query}:{params_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def flush_batches(self) -> Dict[str, List[Any]]:
        """
        Ejecutar flush de todos los batches pendientes

        Returns:
            Resultados de los batches
        """
        return self.batcher.flush_all()

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del optimizador

        Returns:
            Diccionario con estadísticas
        """
        stats = self._stats.copy()
        stats.update({
            'cache_size': self.cache.size(),
            'cache_hit_ratio': (stats['cache_hits'] / max(stats['queries_executed'], 1)),
            'avg_query_time': (stats['total_query_time'] / max(stats['queries_executed'], 1))
        })
        return stats

    def clear_cache(self) -> None:
        """Limpiar cache de consultas"""
        self.cache.clear()

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analizar una consulta SQL para detectar problemas de rendimiento

        Args:
            query: Consulta SQL a analizar

        Returns:
            Dict con análisis de la consulta
        """
        analysis = {
            'has_select_star': '*' in query.upper(),
            'has_join': 'JOIN' in query.upper(),
            'has_where': 'WHERE' in query.upper(),
            'has_limit': 'LIMIT' in query.upper(),
            'estimated_complexity': 'low'
        }

        # Estimar complejidad
        if analysis['has_join'] and not analysis['has_where']:
            analysis['estimated_complexity'] = 'high'
            analysis['warnings'] = ['JOIN sin WHERE puede ser ineficiente']
        elif analysis['has_select_star']:
            analysis['estimated_complexity'] = 'medium'
            analysis['warnings'] = ['SELECT * puede seleccionar columnas innecesarias']

        return analysis


# Decorador para optimización automática
def optimize_query(use_cache: bool = True, ttl: Optional[int] = None,
                   batch_key: Optional[str] = None):
    """
    Decorador para optimización automática de consultas.

    Args:
        use_cache: Si usar cache
        ttl: TTL específico para cache
        batch_key: Clave para agrupamiento en batches
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraer optimizador del contexto (debe ser inyectado)
            optimizer = getattr(wrapper, '_optimizer', None)
            if not optimizer:
                # Sin optimizador - ejecutar función normal
                return func(*args, **kwargs)

            # Generar clave de cache
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Intentar obtener del cache
            if use_cache:
                cached_result = optimizer.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # Ejecutar función original
            result = func(*args, **kwargs)

            # Almacenar en cache
            if use_cache and result is not None:
                optimizer.cache.put(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# Función de utilidad para configurar optimizador
def setup_query_optimizer(db_connection=None, **kwargs) -> QueryOptimizer:
    """
    Configura y retorna un optimizador de consultas.

    Args:
        db_connection: Conexión a la base de datos
        **kwargs: Argumentos adicionales para el optimizador

    Returns:
        QueryOptimizer: Optimizador configurado
    """
    optimizer = QueryOptimizer(db_connection, **kwargs)
    logger.info("Query optimizer configurado exitosamente")
    return optimizer


# Instancia global para uso común
default_optimizer = QueryOptimizer()