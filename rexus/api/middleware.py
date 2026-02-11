"""
Middleware API - Rexus.app
Middleware para monitorización, logging y seguridad de APIs

Características:
- Logging automático de requests
- Métricas Prometheus
- Rate limiting por IP
- CORS configuración
- Request ID tracking
"""

import time
import uuid
import logging
from typing import Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


# ===============================
# Middleware genérico (framework-agnostic)
# ===============================

class APIMiddleware:
    """Middleware base para APIs."""

    def __init__(self):
        self.request_start_times = {}

    def before_request(self, request_id: str, method: str, path: str, **kwargs):
        """Hook antes de procesar el request."""
        self.request_start_times[request_id] = time.time()

        from rexus.utils.structured_logging import log_context, RequestContext

        # Establecer contexto
        RequestContext.set("request_id", request_id)
        RequestContext.set("http_method", method)
        RequestContext.set("http_path", path)

        logger.info(f"Request started: {method} {path}")

    def after_request(self, request_id: str, method: str, path: str,
                     status_code: int, **kwargs):
        """Hook después de procesar el request."""
        duration = time.time() - self.request_start_times.get(request_id, 0)

        from rexus.utils.structured_logging import log_api_request

        log_api_request(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration * 1000
        )

        # Actualizar métricas
        from rexus.monitoring.prometheus_metrics import inc_counter, observe_histogram

        inc_counter(
            "rexus_http_requests_total",
            method=method,
            endpoint=path,
            status=str(status_code)
        )

        observe_histogram(
            "rexus_http_request_duration_seconds",
            duration,
            method=method,
            endpoint=path
        )

        # Limpiar
        if request_id in self.request_start_times:
            del self.request_start_times[request_id]

    def on_error(self, request_id: str, method: str, path: str,
                error: Exception, **kwargs):
        """Hook cuando ocurre un error."""
        duration = time.time() - self.request_start_times.get(request_id, 0)

        logger.error(
            f"Request error: {method} {path}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "duration_ms": duration * 1000
            },
            exc_info=True
        )


# ===============================
# FastAPI Middleware
# ===============================

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp

    class FastAPIMiddleware(BaseHTTPMiddleware):
        """Middleware para FastAPI."""

        def __init__(self, app: ASGIApp):
            super().__init__(app)
            self.api_middleware = APIMiddleware()

        async def dispatch(self, request: Request, call_next):
            """Procesa cada request."""
            request_id = str(uuid.uuid4())
            method = request.method
            path = request.url.path

            # Before request
            self.api_middleware.before_request(request_id, method, path)

            try:
                # Procesar request
                response = await call_next(request)

                # After request
                self.api_middleware.after_request(
                    request_id, method, path, response.status_code
                )

                # Agregar headers
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                # On error
                self.api_middleware.on_error(request_id, method, path, e)
                raise

    FASTAPI_AVAILABLE = True

except ImportError:
    FASTAPI_AVAILABLE = False


# ===============================
# Flask Middleware
# ===============================

try:
    from flask import request, g, Response

    class FlaskMiddleware:
        """Middleware para Flask."""

        def __init__(self, app=None):
            self.app = app
            self.api_middleware = APIMiddleware()
            if app:
                self.init_app(app)

        def init_app(self, app):
            """Inicializa el middleware en una app Flask."""
            app.before_request(self._before_request)
            app.after_request(self._after_request)
            app.teardown_appcontext(self._teardown)

        def _before_request(self):
            """Hook antes de cada request."""
            request_id = str(uuid.uuid4())
            g.request_id = request_id
            g.request_start_time = time.time()

            self.api_middleware.before_request(
                request_id,
                request.method,
                request.path
            )

        def _after_request(self, response: Response):
            """Hook después de cada request."""
            request_id = getattr(g, 'request_id', None)
            method = request.method
            path = request.path

            if request_id:
                self.api_middleware.after_request(
                    request_id,
                    method,
                    path,
                    response.status_code
                )

                response.headers["X-Request-ID"] = request_id

            return response

        def _teardown(self, exception):
            """Hook al finalizar el request."""
            if exception:
                request_id = getattr(g, 'request_id', None)
                method = getattr(g, 'request_method', 'UNKNOWN')
                path = getattr(g, 'request_path', 'UNKNOWN')

                if request_id:
                    self.api_middleware.on_error(
                        request_id,
                        method,
                        path,
                        exception
                    )

    FLASK_AVAILABLE = True

except ImportError:
    FLASK_AVAILABLE = False


# ===============================
# Decoradores de API
# ===============================

def log_api_call(func: Callable = None, log_level: str = "INFO"):
    """
    Decorador para loguear llamadas a funciones de API.

    Args:
        func: Función a decorar
        log_level: Nivel de log

    Example:
        @log_api_call(log_level="DEBUG")
        def get_productos():
            return db.query("SELECT * FROM productos")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = str(uuid.uuid4())

            from rexus.utils.structured_logging import log_context

            with log_context(request_id=request_id, function=f.__name__):
                logger = logging.getLogger(f.__module__)

                try:
                    result = f(*args, **kwargs)

                    duration = (time.time() - start_time) * 1000

                    log_func = getattr(logger, log_level.lower())
                    log_func(
                        f"{f.__name__} completed",
                        extra={
                            "function": f.__name__,
                            "duration_ms": duration,
                            "status": "success"
                        }
                    )

                    return result

                except Exception as e:
                    duration = (time.time() - start_time) * 1000

                    logger.error(
                        f"{f.__name__} failed: {str(e)}",
                        extra={
                            "function": f.__name__,
                            "duration_ms": duration,
                            "status": "error",
                            "error_type": type(e).__name__
                        }
                    )
                    raise

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def validate_json(*required_fields):
    """
    Decorador para validar JSON de request.

    Args:
        *required_fields: Campos requeridos

    Example:
        @validate_json("nombre", "precio", "categoria")
        def create_producto(data):
            return db.insert("productos", data)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Asumir que el primer argumento es el request/data
            if args and isinstance(args[0], dict):
                data = args[0]
                missing = [f for f in required_fields if f not in data]

                if missing:
                    raise ValueError(f"Missing required fields: {missing}")

            return func(*args, **kwargs)

        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorador para rate limiting.

    Args:
        max_requests: Máximo de solicitudes permitidas
        window_seconds: Ventana de tiempo en segundos

    Note:
        Este es un rate limiting simple. Para producción
        se recomienda usar Redis para almacenamiento distribuido.

    Example:
        @rate_limit(max_requests=10, window_seconds=60)
        def expensive_operation():
            return do_expensive_work()
    """
    from collections import defaultdict
    from time import time

    request_counts = defaultdict(list)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Identificar el cliente (puede ser IP, user_id, etc.)
            # Aquí usamos un identificador genérico
            client_id = kwargs.get('client_id', 'default')

            now = time()
            window_start = now - window_seconds

            # Limpiar requests viejos
            request_counts[client_id] = [
                ts for ts in request_counts[client_id]
                if ts > window_start
            ]

            # Verificar límite
            if len(request_counts[client_id]) >= max_requests:
                raise Exception(f"Rate limit exceeded: {max_requests} requests per {window_seconds}s")

            # Registrar request
            request_counts[client_id].append(now)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def handle_exceptions(default_response: Any = None, log_error: bool = True):
    """
    Decorador para manejar excepciones.

    Args:
        default_response: Respuesta por defecto si ocurre error
        log_error: Si loguear el error

    Example:
        @handle_exceptions(default_response={"error": True}, log_error=True)
        def risky_operation():
            return do_something_risky()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        extra={"function": func.__name__},
                        exc_info=True
                    )

                if default_response is not None:
                    if callable(default_response):
                        return default_response(e)
                    return default_response

                raise

        return wrapper
    return decorator
