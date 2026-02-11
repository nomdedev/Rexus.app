"""
Metrics Manager - Gestor Central de Métricas

Proporciona una interfaz centralizada para registrar métricas
de aplicación que serán exportadas a Prometheus.
"""

import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsManager:
    """
    Gestor central de métricas de la aplicación.

    Proporciona métodos para registrar:
    - Contadores (conteos de eventos)
    - Histogramas (distribuciones de valores)
    - Gauges (valores actuales)
    - Summaries (estadísticas)
    """

    # Almacén de métricas (para evitar dependencia de prometheus_client)
    _metrics: Dict[str, Dict[str, Any]] = {
        'counters': {},
        'histograms': {},
        'gauges': {},
        'summaries': {}
    }

    @classmethod
    def counter(cls, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """
        Incrementa un contador.

        Args:
            name: Nombre de la métrica
            value: Valor a incrementar (default: 1.0)
            labels: Labels opcionales para agrupar
        """
        key = cls._make_key(name, labels)
        if key not in cls._metrics['counters']:
            cls._metrics['counters'][key] = 0.0

        cls._metrics['counters'][key] += value
        logger.debug(f"Counter {name} incremented by {value}: {cls._metrics['counters'][key]}")

    @classmethod
    def histogram(cls, name: str, value: float, labels: Dict[str, str] = None):
        """
        Registra un valor en un histograma.

        Args:
            name: Nombre de la métrica
            value: Valor a registrar
            labels: Labels opcionales
        """
        key = cls._make_key(name, labels)
        if key not in cls._metrics['histograms']:
            cls._metrics['histograms'][key] = []

        cls._metrics['histograms'][key].append({
            'value': value,
            'timestamp': time.time()
        })

        # Mantener solo últimos 1000 valores para evitar overflow
        if len(cls._metrics['histograms'][key]) > 1000:
            cls._metrics['histograms'][key] = cls._metrics['histograms'][key][-1000:]

        logger.debug(f"Histogram {name} recorded value: {value}")

    @classmethod
    def gauge(cls, name: str, value: float, labels: Dict[str, str] = None):
        """
        Registra un valor actual (gauge).

        Args:
            name: Nombre de la métrica
            value: Valor a registrar
            labels: Labels opcionales
        """
        key = cls._make_key(name, labels)
        cls._metrics['gauges'][key] = value
        logger.debug(f"Gauge {name} set to: {value}")

    @classmethod
    def summary(cls, name: str, value: float, labels: Dict[str, str] = None):
        """
        Registra un valor en un summary.

        Args:
            name: Nombre de la métrica
            value: Valor a registrar
            labels: Labels opcionales
        """
        key = cls._make_key(name, labels)
        if key not in cls._metrics['summaries']:
            cls._metrics['summaries'][key] = []

        cls._metrics['summaries'][key].append({
            'value': value,
            'timestamp': time.time()
        })

        # Mantener solo últimos 1000 valores
        if len(cls._metrics['summaries'][key]) > 1000:
            cls._metrics['summaries'][key] = cls._metrics['summaries'][key][-1000:]

        logger.debug(f"Summary {name} recorded value: {value}")

    @classmethod
    def increment_counter(cls, name: str, labels: Dict[str, str] = None):
        """Incrementa un contador en 1."""
        cls.counter(name, 1.0, labels)

    @classmethod
    def increment_errors(cls, error_type: str, context: str = ""):
        """Registra un error."""
        labels = {'error_type': error_type, 'context': context} if context else {'error_type': error_type}
        cls.increment_counter('errors_total', labels)

    @classmethod
    def get_all_metrics(cls) -> Dict[str, Any]:
        """
        Obtiene todas las métricas registradas.

        Returns:
            Diccionario con todas las métricas
        """
        return {
            'counters': cls._metrics['counters'].copy(),
            'histograms': cls._metrics['histograms'].copy(),
            'gauges': cls._metrics['gauges'].copy(),
            'summaries': cls._metrics['summaries'].copy(),
            'timestamp': datetime.now().isoformat()
        }

    @classmethod
    def get_histogram_stats(cls, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """
        Obtiene estadísticas de un histograma.

        Args:
            name: Nombre del histograma
            labels: Labels del histograma

        Returns:
            Estadísticas (count, sum, avg, min, max)
        """
        key = cls._make_key(name, labels)
        if key not in cls._metrics['histograms']:
            return {'count': 0, 'sum': 0, 'avg': 0, 'min': 0, 'max': 0}

        values = [v['value'] for v in cls._metrics['histograms'][key]]
        if not values:
            return {'count': 0, 'sum': 0, 'avg': 0, 'min': 0, 'max': 0}

        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }

    @classmethod
    def reset(cls):
        """Resetea todas las métricas (útil para tests)."""
        cls._metrics = {
            'counters': {},
            'histograms': {},
            'gauges': {},
            'summaries': {}
        }

    @classmethod
    def _make_key(cls, name: str, labels: Dict[str, str] = None) -> str:
        """
        Crea una key única para la métrica basada en nombre y labels.

        Args:
            name: Nombre de la métrica
            labels: Labels opcionales

        Returns:
            Key única
        """
        if not labels:
            return name

        label_str = ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    # ==================== DECORADORES ====================

    @classmethod
    def count_calls(cls, metric_name: str = None, labels: Dict[str, str] = None):
        """
        Decorador para contar llamadas a una función.

        Args:
            metric_name: Nombre de la métrica (default: nombre_funcucion_calls)
            labels: Labels estáticos

        Returns:
            Decorador
        """
        def decorator(func: Callable) -> Callable:
            name = metric_name or f"{func.__name__}_calls"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    cls.increment_counter(name, labels)
                    return result
                except Exception as e:
                    cls.increment_errors(type(e).__name__, func.__name__)
                    raise

            return wrapper
        return decorator

    @classmethod
    def measure_time(cls, metric_name: str = None, labels: Dict[str, str] = None):
        """
        Decorador para medir tiempo de ejecución.

        Args:
            metric_name: Nombre de la métrica (default: nombre_funcucion_duration)
            labels: Labels estáticos

        Returns:
            Decorador
        """
        def decorator(func: Callable) -> Callable:
            name = metric_name or f"{func.__name__}_duration"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    cls.histogram(name, duration, labels)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    cls.histogram(name, duration, {**(labels or {}), 'status': 'error'})
                    cls.increment_errors(type(e).__name__, func.__name__)
                    raise

            return wrapper
        return decorator

    @classmethod
    def track_database_query(cls, query_type: str, table: str):
        """
        Decorador para trackear queries de BD.

        Args:
            query_type: Tipo de query (SELECT, INSERT, UPDATE, DELETE)
            table: Nombre de la tabla

        Returns:
            Decorador
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    # Registrar duración
                    cls.histogram(
                        'database_query_duration_seconds',
                        duration,
                        {'query_type': query_type, 'table': table}
                    )

                    # Registrar conteo
                    cls.increment_counter(
                        'database_queries_total',
                        {'query_type': query_type, 'table': table}
                    )

                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    cls.histogram(
                        'database_query_duration_seconds',
                        duration,
                        {'query_type': query_type, 'table': table, 'status': 'error'}
                    )
                    raise

            return wrapper
        return decorator

    # ==================== CONTEXT MANAGERS ====================

    @classmethod
    @contextmanager
    def measure_operation(cls, operation_name: str, labels: Dict[str, str] = None):
        """
        Context manager para medir una operación.

        Args:
            operation_name: Nombre de la operación
            labels: Labels opcionales

        Yields:
            None
        """
        start_time = time.time()
        success = True

        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            all_labels = {**(labels or {}), 'status': 'success' if success else 'error'}
            cls.histogram(f"{operation_name}_duration", duration, all_labels)
            cls.increment_counter(f"{operation_name}_total", all_labels)

    @classmethod
    @contextmanager
    def track_cache_operation(cls, operation: str, cache_type: str = 'redis'):
        """
        Context manager para trackear operaciones de caché.

        Args:
            operation: Tipo de operación (get, set, delete)
            cache_type: Tipo de caché

        Yields:
            (hit: bool) - Para operaciones GET
        """
        start_time = time.time()
        hit = False

        try:
            if operation == 'get':
                # El yield permite que el código indique si fue hit
                hit = yield True
                labels = {'operation': operation, 'cache_type': cache_type, 'result': 'hit' if hit else 'miss'}
            else:
                yield None
                labels = {'operation': operation, 'cache_type': cache_type}

            duration = time.time() - start_time
            cls.histogram(f"cache_operation_duration", duration, labels)
            cls.increment_counter(f"cache_operations_total", labels)

        except Exception:
            duration = time.time() - start_time
            error_labels = {'operation': operation, 'cache_type': cache_type, 'status': 'error'}
            cls.histogram(f"cache_operation_duration", duration, error_labels)
            cls.increment_errors('cache_error', operation)
            raise
