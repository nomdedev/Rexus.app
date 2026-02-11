"""
Monitoring Middleware - Middleware de Monitoreo

Middleware Flask para trackear automáticamente todas las requests HTTP
y exponer métricas en tiempo real.
"""

import time
import logging
from functools import wraps
from flask import request, g
from .metrics_manager import MetricsManager

logger = logging.getLogger(__name__)


class MonitoringMiddleware:
    """
    Middleware para monitoreo automático de aplicaciones Flask.

    Registra automáticamente:
    - Todas las requests HTTP
    - Tiempos de respuesta
    - Códigos de estado
    - Errores
    """

    def __init__(self, app=None):
        """
        Inicializa el middleware.

        Args:
            app: Aplicación Flask (opcional)
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Inicializa el middleware en una app Flask.

        Args:
            app: Aplicación Flask
        """
        self.app = app

        # Registrar before_request
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown)

        # Agregar endpoint /metrics si no existe
        if not self._has_metrics_endpoint(app):
            from .prometheus_exporter import create_metrics_endpoint
            create_metrics_endpoint(app, '/metrics')

        logger.info("Monitoring middleware initialized")

    def _before_request(self):
        """Antes de cada request."""
        g.start_time = time.time()
        g.metrics_manager = MetricsManager

    def _after_request(self, response):
        """Después de cada request."""
        # Calcular duración
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time

            # Extraer información de la request
            method = request.method
            path = request.path
            status_code = response.status_code
            endpoint = request.endpoint or 'unknown'

            # Ignorar health checks y metrics
            if path in ['/health', '/metrics', '/favicon.ico']:
                return response

            # Registrar duración
            MetricsManager.histogram(
                'http_request_duration_seconds',
                duration,
                {
                    'method': method,
                    'endpoint': endpoint,
                    'status': str(status_code)
                }
            )

            # Registrar request
            MetricsManager.increment_counter(
                'http_requests_total',
                {
                    'method': method,
                    'endpoint': endpoint,
                    'status': str(status_code)
                }
            )

            # Log de requests lentas (> 1s)
            if duration > 1.0:
                logger.warning(f"Slow request detected: {method} {path} took {duration:.2f}s")

        return response

    def _teardown(self, exception):
        """Cleanup después de cada request."""
        if exception is not None:
            # Registrar excepción no manejada
            MetricsManager.increment_errors(
                error_type=type(exception).__name__,
                context='unhandled_exception'
            )
            logger.error(f"Unhandled exception: {exception}")

    def _has_metrics_endpoint(self, app) -> bool:
        """Verifica si la app ya tiene endpoint /metrics."""
        try:
            for rule in app.url_map.iter_rules():
                if rule.rule == '/metrics':
                    return True
        except:
            pass
        return False


def track_endpoint(metric_name: str = None):
    """
    Decorador para trackear un endpoint específico.

    Args:
        metric_name: Nombre de la métrica (default: endpoint_duration)

    Usage:
        @app.route('/api/productos')
        @track_endpoint('productos_list')
        def listar_productos():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with MetricsManager.measure_operation(metric_name or func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def track_module(module_name: str):
    """
    Decorador para trackear llamadas a un módulo.

    Args:
        module_name: Nombre del módulo

    Usage:
        @track_module('inventario')
        def crear_producto(data):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            MetricsManager.increment_counter(
                'module_calls_total',
                {'module': module_name, 'function': func.__name__}
            )

            with MetricsManager.measure_operation(
                f"{module_name}_{func.__name__}",
                {'module': module_name}
            ):
                return func(*args, **kwargs)
        return wrapper
    return decorator
