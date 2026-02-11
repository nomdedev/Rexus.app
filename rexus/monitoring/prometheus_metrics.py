"""
Sistema de Métricas Prometheus - Rexus.app
Exporta métricas de la aplicación para ser consumidas por Prometheus

Características:
- Contadores para eventos
- Gauges para valores actuales
- Histogramas para distribuciones
- Summaries para cálculos agregados
- Middleware para HTTP
"""

import os
import time
import logging
import functools
from typing import Dict, List, Optional, Callable
from datetime import datetime
from threading import Lock
from collections import defaultdict

# Verificar disponibilidad de prometheus_client
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
        start_http_server,
        Enum
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client no disponible. Instala con: pip install prometheus_client")

logger = logging.getLogger(__name__)


class MetricType:
    """Tipos de métricas soportadas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    ENUM = "enum"


class PrometheusMetrics:
    """
    Gestor centralizado de métricas Prometheus.

    Provee métodos para registrar y exponer métricas de la aplicación.
    """

    def __init__(self, port: int = None, enabled: bool = None):
        """
        Inicializa el gestor de métricas.

        Args:
            port: Puerto para el servidor HTTP de métricas
            enabled: Si el sistema está habilitado
        """
        self.enabled = enabled if enabled is not None else os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
        self.port = port or int(os.getenv("PROMETHEUS_PORT", "8000"))
        self._server_started = False
        self._lock = Lock()

        # Registry personalizado para Rexus
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None

        # Métricas predefinidas
        self._metrics = {}
        self._init_default_metrics()

        if self.enabled and PROMETHEUS_AVAILABLE:
            self._start_server()

    def _start_server(self):
        """Inicia el servidor HTTP de métricas."""
        if self._server_started:
            return

        try:
            start_http_server(self.port, registry=self.registry)
            self._server_started = True
            logger.info(f"Prometheus metrics server iniciado en puerto {self.port}")
        except Exception as e:
            logger.error(f"Error iniciando servidor de métricas: {e}")

    def _init_default_metrics(self):
        """Inicializa las métricas por defecto."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return

        # Contadores
        self._create_counter(
            "rexus_http_requests_total",
            "Total de solicitudes HTTP",
            ["method", "endpoint", "status"]
        )

        self._create_counter(
            "rexus_db_queries_total",
            "Total de consultas a base de datos",
            ["database", "operation", "table"]
        )

        self._create_counter(
            "rexus_logins_total",
            "Total de intentos de login",
            ["status"]
        )

        self._create_counter(
            "rexus_errors_total",
            "Total de errores",
            ["module", "error_type"]
        )

        # Gauges
        self._create_gauge(
            "rexus_active_users",
            "Número de usuarios activos"
        )

        self._create_gauge(
            "rexus_db_connections",
            "Conexiones activas a base de datos",
            ["database"]
        )

        self._create_gauge(
            "rexus_inventory_items",
            "Total de items en inventario",
            ["category"]
        )

        self._create_gauge(
            "rexus_pending_orders",
            "Pedidos pendientes",
            ["status"]
        )

        # Histograms
        self._create_histogram(
            "rexus_http_request_duration_seconds",
            "Duración de solicitudes HTTP",
            ["method", "endpoint"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        )

        self._create_histogram(
            "rexus_db_query_duration_seconds",
            "Duración de consultas a base de datos",
            ["database", "operation"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        # Summaries
        self._create_summary(
            "rexus_response_time_seconds",
            "Tiempo de respuesta",
            ["operation"]
        )

        # Enums
        self._create_enum(
            "rexus_system_status",
            "Estado del sistema",
            ["starting", "running", "degraded", "down"]
        )

    def _create_counter(self, name: str, description: str, labels: List[str] = None) -> Optional[Counter]:
        """Crea un contador."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return None

        with self._lock:
            if name in self._metrics:
                return self._metrics[name]

            metric = Counter(
                name,
                description,
                labelnames=labels or [],
                registry=self.registry
            )
            self._metrics[name] = metric
            return metric

    def _create_gauge(self, name: str, description: str, labels: List[str] = None) -> Optional[Gauge]:
        """Crea un gauge."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return None

        with self._lock:
            if name in self._metrics:
                return self._metrics[name]

            metric = Gauge(
                name,
                description,
                labelnames=labels or [],
                registry=self.registry
            )
            self._metrics[name] = metric
            return metric

    def _create_histogram(self, name: str, description: str, labels: List[str] = None,
                         buckets: List[float] = None) -> Optional[Histogram]:
        """Crea un histograma."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return None

        with self._lock:
            if name in self._metrics:
                return self._metrics[name]

            metric = Histogram(
                name,
                description,
                labelnames=labels or [],
                buckets=buckets,
                registry=self.registry
            )
            self._metrics[name] = metric
            return metric

    def _create_summary(self, name: str, description: str, labels: List[str] = None) -> Optional[Summary]:
        """Crea un summary."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return None

        with self._lock:
            if name in self._metrics:
                return self._metrics[name]

            metric = Summary(
                name,
                description,
                labelnames=labels or [],
                registry=self.registry
            )
            self._metrics[name] = metric
            return metric

    def _create_enum(self, name: str, description: str, states: List[str]) -> Optional[Enum]:
        """Crea un enum."""
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return None

        with self._lock:
            if name in self._metrics:
                return self._metrics[name]

            metric = Enum(
                name,
                description,
                states=states,
                registry=self.registry
            )
            self._metrics[name] = metric
            return metric

    # ==========================================
    # Métodos públicos para registrar métricas
    # ==========================================

    def inc_counter(self, name: str, value: float = 1, **labels) -> bool:
        """
        Incrementa un contador.

        Args:
            name: Nombre del contador
            value: Valor a incrementar (default: 1)
            **labels: Labels para la métrica

        Returns:
            True si se incrementó exitosamente
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return False

        metric = self._metrics.get(name)
        if not metric or not isinstance(metric, Counter):
            return False

        if labels:
            metric.labels(**labels).inc(value)
        else:
            metric.inc(value)

        return True

    def set_gauge(self, name: str, value: float, **labels) -> bool:
        """
        Establece el valor de un gauge.

        Args:
            name: Nombre del gauge
            value: Valor a establecer
            **labels: Labels para la métrica

        Returns:
            True si se estableció exitosamente
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return False

        metric = self._metrics.get(name)
        if not metric or not isinstance(metric, Gauge):
            return False

        if labels:
            metric.labels(**labels).set(value)
        else:
            metric.set(value)

        return True

    def observe_histogram(self, name: str, value: float, **labels) -> bool:
        """
        Observa un valor en un histograma.

        Args:
            name: Nombre del histograma
            value: Valor a observar
            **labels: Labels para la métrica

        Returns:
            True si se observó exitosamente
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return False

        metric = self._metrics.get(name)
        if not metric or not isinstance(metric, Histogram):
            return False

        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)

        return True

    def observe_summary(self, name: str, value: float, **labels) -> bool:
        """
        Observa un valor en un summary.

        Args:
            name: Nombre del summary
            value: Valor a observar
            **labels: Labels para la métrica

        Returns:
            True si se observó exitosamente
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return False

        metric = self._metrics.get(name)
        if not metric or not isinstance(metric, Summary):
            return False

        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)

        return True

    def set_enum(self, name: str, state: str) -> bool:
        """
        Establece el estado de un enum.

        Args:
            name: Nombre del enum
            state: Estado a establecer

        Returns:
            True si se estableció exitosamente
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return False

        metric = self._metrics.get(name)
        if not metric or not isinstance(metric, Enum):
            return False

        metric.state(state)
        return True

    def get_metrics_text(self) -> bytes:
        """
        Obtiene todas las métricas en formato Prometheus.

        Returns:
            Bytes con las métricas en formato de texto
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return b""

        return generate_latest(self.registry)

    # ==========================================
    # Decoradores para instrumentación automática
    # ==========================================

    def track_http_request(self, func: Callable = None, method: str = "GET") -> Callable:
        """
        Decorador para trackear solicitudes HTTP.

        Args:
            func: Función a decorar
            method: Método HTTP

        Returns:
            Función decorada
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "200"

                try:
                    result = f(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "500"
                    self.inc_counter(
                        "rexus_http_requests_total",
                        method=method,
                        endpoint=f.__name__,
                        status=status
                    )
                    self.inc_counter(
                        "rexus_errors_total",
                        module="http",
                        error_type=type(e).__name__
                    )
                    raise
                else:
                    self.inc_counter(
                        "rexus_http_requests_total",
                        method=method,
                        endpoint=f.__name__,
                        status=status
                    )
                    duration = time.time() - start_time
                    self.observe_histogram(
                        "rexus_http_request_duration_seconds",
                        duration,
                        method=method,
                        endpoint=f.__name__
                    )
                    return result

            return wrapper

        if func is not None:
            return decorator(func)
        return decorator

    def track_db_query(self, func: Callable = None, database: str = "inventario",
                      operation: str = "select") -> Callable:
        """
        Decorador para trackear consultas a base de datos.

        Args:
            func: Función a decorar
            database: Nombre de la base de datos
            operation: Tipo de operación

        Returns:
            Función decorada
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    result = f(*args, **kwargs)
                    self.inc_counter(
                        "rexus_db_queries_total",
                        database=database,
                        operation=operation,
                        table=getattr(f, '__tablename__', 'unknown')
                    )
                    duration = time.time() - start_time
                    self.observe_histogram(
                        "rexus_db_query_duration_seconds",
                        duration,
                        database=database,
                        operation=operation
                    )
                    return result
                except Exception as e:
                    self.inc_counter(
                        "rexus_db_queries_total",
                        database=database,
                        operation=operation,
                        table="error"
                    )
                    raise

            return wrapper

        if func is not None:
            return decorator(func)
        return decorator


# Instancia global
_prometheus_metrics_instance = None


def get_metrics() -> PrometheusMetrics:
    """Obtiene la instancia singleton de PrometheusMetrics."""
    global _prometheus_metrics_instance
    if _prometheus_metrics_instance is None:
        _prometheus_metrics_instance = PrometheusMetrics()
    return _prometheus_metrics_instance


# Funciones de conveniencia
def inc_counter(name: str, value: float = 1, **labels) -> bool:
    """Incrementa un contador."""
    return get_metrics().inc_counter(name, value, **labels)


def set_gauge(name: str, value: float, **labels) -> bool:
    """Establece un gauge."""
    return get_metrics().set_gauge(name, value, **labels)


def observe_histogram(name: str, value: float, **labels) -> bool:
    """Observa un valor en histograma."""
    return get_metrics().observe_histogram(name, value, **labels)


def track_http_request(func: Callable = None, method: str = "GET") -> Callable:
    """Decorador para trackear solicitudes HTTP."""
    return get_metrics().track_http_request(func, method)


def track_db_query(func: Callable = None, database: str = "inventario",
                   operation: str = "select") -> Callable:
    """Decorador para trackear consultas a DB."""
    return get_metrics().track_db_query(func, database, operation)
