"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Optimizador de Consultas
Sistema para prevenir problemas N+1 y mejorar el rendimiento de queries.
"""

import time
import functools
import hashlib
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import threading


@dataclass
class QueryStats:
    """Estadísticas de una consulta."""
    query_hash: str
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_executed: Optional[datetime] = None
    cache_hits: int = 0

    def update(self, execution_time: float):
        """Actualiza las estadísticas con una nueva ejecución."""
        self.execution_count += 1
        self.total_time += execution_time
        self.avg_time = self.total_time / self.execution_count
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.last_executed = datetime.now()


class BatchQueryExecutor:
    """
    Ejecutor de consultas por lotes para evitar problemas N+1.
    """

    def __init__(self):
        self._batch_queries = {}
        self._batch_timeout = 0.1  # 100ms timeout para batching
        self._batch_threads = {}
        self._lock = threading.RLock()

    def batch_query(self,
query_key: str,
        query_func: Callable,
        *args,
        **kwargs):
        """
        Agrupa consultas similares para ejecutarlas en lotes.

        Args:
            query_key: Identificador único del tipo de consulta
            query_func: Función que ejecuta la consulta
            *args, **kwargs: Parámetros de la consulta
        """
        with self._lock:
            if query_key not in self._batch_queries:
                self._batch_queries[query_key] = {
                    'queries': [],
                    'func': query_func,
                    'timer': None
                }

            # Agregar consulta al lote
            batch = self._batch_queries[query_key]
            batch['queries'].append((args, kwargs))

            # Si es la primera consulta del lote, iniciar timer
            if batch['timer'] is None:
                batch['timer'] = threading.Timer(
                    self._batch_timeout,
                    self._execute_batch,
                    args=[query_key]
                )
                batch['timer'].start()

    def _execute_batch(self, query_key: str):
        """Ejecuta un lote de consultas."""
        with self._lock:
            if query_key not in self._batch_queries:
                return

            batch = self._batch_queries[query_key]
            queries = batch['queries']
            func = batch['func']

            # Limpiar el lote
            del self._batch_queries[query_key]

        # Ejecutar el lote fuera del lock
        try:
            if len(queries) == 1:
                # Consulta individual
                args, kwargs = queries[0]
                return func(*args, **kwargs)
            else:
                # Consulta en lote - la función debe saber manejar múltiples queries
                return func(queries)
        except Exception as e:
            print(f"[QUERY_OPTIMIZER] Error ejecutando lote {query_key}: {e}")
            return None


class QueryOptimizer:
    """
    Optimizador principal de consultas con cache y prevención N+1.
    """

    def __init__(self):
        self._query_stats: Dict[str, QueryStats] = {}
        self._batch_executor = BatchQueryExecutor()
        self._lock = threading.RLock()

        # Configuración
        self.slow_query_threshold = 1.0  # 1 segundo
        self.cache_slow_queries = True
        self.enable_batching = True

    def _generate_query_hash(self,
func: Callable,
        args: tuple,
        kwargs: dict) -> str:
        """Genera un hash único para la consulta."""
        func_name = f"{func.__module__}.{func.__name__}"
        query_signature = f"{func_name}({args}, {kwargs})"
        return hashlib.md5(query_signature.encode()).hexdigest()

    def track_query_performance(self, func: Callable):
        """
        Decorador para trackear el rendimiento de consultas.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query_hash = self._generate_query_hash(func, args, kwargs)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                self._record_query_stats(query_hash, execution_time)

                # Log consultas lentas
                if execution_time > self.slow_query_threshold:
                    print(f"[SLOW_QUERY] {func.__name__} took {execution_time:.3f}s")

        return wrapper

    def _record_query_stats(self, query_hash: str, execution_time: float):
        """Registra estadísticas de una consulta."""
        with self._lock:
            if query_hash not in self._query_stats:
                self._query_stats[query_hash] = QueryStats(query_hash)

            self._query_stats[query_hash].update(execution_time)

    def cached_query(self, cache_key: str = None, ttl: int = 300):
        """
        Decorador para cachear resultados de consultas.

        Args:
            cache_key: Clave de cache personalizada
            ttl: Time to live en segundos
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generar clave de cache
                if cache_key:
                    key = cache_key
                else:
                    query_hash = self._generate_query_hash(func, args, kwargs)
                    key = f"query_cache:{query_hash}"

                # Intentar obtener del cache
                try:
                    from .cache_manager import cache_manager

                    cached_result = cache_manager.get(key)
                    if cached_result is not None:
                        # Actualizar estadísticas de cache hit
                        query_hash = self._generate_query_hash(func, args, kwargs)
                        with self._lock:
                            if query_hash in self._query_stats:
                                self._query_stats[query_hash].cache_hits += 1
                        return cached_result

                    # Ejecutar consulta y cachear resultado
                    result = func(*args, **kwargs)
                    cache_manager.set(key, result, ttl)
                    return result

                except ImportError:
                    # Cache no disponible, ejecutar normalmente
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    def prevent_n_plus_one(self, batch_key: str):
        """
        Decorador para prevenir problemas N+1 mediante batching.

        Args:
            batch_key: Identificador único para el tipo de consulta
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self.enable_batching:
                    return self._batch_executor.batch_query(batch_key,
func,
                        *args,
                        **kwargs)
                else:
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    def paginated_query(self, page_size: int = 50, max_page_size: int = 500):
        """
        Decorador para agregar paginación automática a consultas.

        Args:
            page_size: Tamaño de página por defecto
            max_page_size: Tamaño máximo de página permitido
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extraer parámetros de paginación
                page = kwargs.pop('page', 1)
                limit = min(kwargs.pop('page_size', page_size), max_page_size)
                offset = (page - 1) * limit

                # Agregar parámetros de paginación a la consulta
                kwargs['limit'] = limit
                kwargs['offset'] = offset

                # Ejecutar consulta paginada
                result = func(*args, **kwargs)

                # Si el resultado es una lista, agregar metadatos de paginación
                if isinstance(result, list):
                    return {
                        'data': result,
                        'pagination': {
                            'page': page,
                            'page_size': limit,
                            'has_more': len(result) == limit
                        }
                    }

                return result

            return wrapper
        return decorator

    def get_query_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todas las consultas."""
        with self._lock:
            total_queries = sum(stat.execution_count for stat in self._query_stats.values())
            total_time = sum(stat.total_time for stat in self._query_stats.values())
            slow_queries = [
                stat for stat in self._query_stats.values()
                if stat.avg_time > self.slow_query_threshold
            ]

            # Top consultas por tiempo promedio
            slowest_queries = sorted(
                self._query_stats.values(),
                key=lambda s: s.avg_time,
                reverse=True
            )[:10]

            # Consultas más frecuentes
            most_frequent = sorted(
                self._query_stats.values(),
                key=lambda s: s.execution_count,
                reverse=True
            )[:10]

            return {
                'total_queries_executed': total_queries,
                'total_execution_time': round(total_time, 3),
                'average_query_time': round(total_time / total_queries if total_queries > 0 else 0, 3),
                'slow_queries_count': len(slow_queries),
                'slowest_queries': [
                    {
                        'hash': q.query_hash[:8],
                        'avg_time': round(q.avg_time, 3),
                        'execution_count': q.execution_count,
                        'cache_hits': q.cache_hits
                    }
                    for q in slowest_queries
                ],
                'most_frequent_queries': [
                    {
                        'hash': q.query_hash[:8],
                        'execution_count': q.execution_count,
                        'avg_time': round(q.avg_time, 3),
                        'cache_hits': q.cache_hits
                    }
                    for q in most_frequent
                ],
                'cache_statistics': {
                    'total_cache_hits': sum(stat.cache_hits for stat in self._query_stats.values()),
                    'cache_hit_ratio': self._calculate_cache_hit_ratio()
                }
            }

    def _calculate_cache_hit_ratio(self) -> float:
        """Calcula el ratio de cache hits."""
        total_executions = sum(stat.execution_count for stat in self._query_stats.values())
        total_cache_hits = sum(stat.cache_hits for stat in self._query_stats.values())

        if total_executions > 0:
            return round((total_cache_hits / total_executions) * 100, 2)
        return 0.0

    def get_recommendations(self) -> List[str]:
        """Genera recomendaciones de optimización."""
        recommendations = []

        with self._lock:
            # Consultas lentas que deberían cachearse
            slow_queries = [
                stat for stat in self._query_stats.values()
                if stat.avg_time > self.slow_query_threshold and \
                    stat.cache_hits == 0
            ]

            if slow_queries:
                recommendations.append(
                    f"Considera cachear {len(slow_queries)} consultas lentas que no usan cache"
                )

            # Consultas muy frecuentes
            frequent_queries = [
                stat for stat in self._query_stats.values()
                if stat.execution_count > 100 and \
                    stat.cache_hits / stat.execution_count < 0.5
            ]

            if frequent_queries:
                recommendations.append(
                    f"Mejora el cache para {len(frequent_queries)} consultas frecuentes con bajo hit ratio"
                )

            # Consultas con alta variabilidad en tiempo
            inconsistent_queries = [
                stat for stat in self._query_stats.values()
                if stat.max_time > stat.min_time * 10  # 10x diferencia
            ]

            if inconsistent_queries:
                recommendations.append(
                    f"Revisa {len(inconsistent_queries)} consultas con tiempos muy variables"
                )

        if not recommendations:
            recommendations.append("El rendimiento de consultas parece óptimo")

        return recommendations


# Instancia global del optimizador
query_optimizer = QueryOptimizer()


# Decoradores de conveniencia
def track_performance(func):
    """Decorador de conveniencia para trackear rendimiento."""
    return query_optimizer.track_query_performance(func)


def cached_query(cache_key: str = None, ttl: int = 300):
    """Decorador de conveniencia para cache de consultas."""
    return query_optimizer.cached_query(cache_key, ttl)


def prevent_n_plus_one(batch_key: str):
    """Decorador de conveniencia para prevenir N+1."""
    return query_optimizer.prevent_n_plus_one(batch_key)


def paginated(page_size: int = 50):
    """Decorador de conveniencia para paginación."""
    return query_optimizer.paginated_query(page_size)


# Función para aplicar múltiples optimizaciones
def optimized_query(cache_key: str = None, ttl: int = 300,
                   batch_key: str = None, page_size: int = 50):
    """
    Decorador que combina múltiples optimizaciones.

    Args:
        cache_key: Clave de cache personalizada
        ttl: Time to live para cache
        batch_key: Clave para batching (previene N+1)
        page_size: Tamaño de página por defecto
    """
    def decorator(func):
        # Aplicar decoradores en orden
        optimized_func = track_performance(func)

        if cache_key or ttl != 300:
            optimized_func = cached_query(cache_key, ttl)(optimized_func)

        if batch_key:
            optimized_func = prevent_n_plus_one(batch_key)(optimized_func)

        if page_size != 50:
            optimized_func = paginated(page_size)(optimized_func)

        return optimized_func

    return decorator
