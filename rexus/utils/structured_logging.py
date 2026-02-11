"""
Sistema de Logging Estructurado - Rexus.app
Logs con formato JSON para mejor análisis y monitorización

Características:
- Logs en formato JSON estructurado
- Contexto automático (user, request_id, module)
- Niveles de log configurables
- Output a archivo y consola
- Integración con Sentry para errores
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
import uuid


class StructuredFormatter(logging.Formatter):
    """Formatter que produce logs en formato JSON."""

    def __init__(self, service_name: str = "rexus", environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        """Formatea un registro de log como JSON."""
        # Crear diccionario base
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
        }

        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        # Agregar atributos extra
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        # Agregar información del archivo y línea
        log_entry["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestContext:
    """Contexto de solicitud para logging."""

    _instance = None
    _context = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set(cls, key: str, value: Any):
        """Establece un valor en el contexto."""
        cls._context[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtiene un valor del contexto."""
        return cls._context.get(key, default)

    @classmethod
    def clear(cls):
        """Limpia el contexto."""
        cls._context.clear()

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convierte el contexto a diccionario."""
        return cls._context.copy()

    @classmethod
    def generate_request_id(cls) -> str:
        """Genera un ID de solicitud único."""
        return str(uuid.uuid4())


class ContextualLogger(logging.LoggerAdapter):
    """Logger que agrega contexto automáticamente a cada log."""

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any] = None):
        super().__init__(logger, extra or {})

    def process(self, msg: Any, kwargs: Dict[str, Any]) -> tuple:
        """Procesa el mensaje agregando contexto."""
        # Combinar contexto del adaptador con contexto global
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        extra.update(RequestContext.to_dict())

        # Agregar request_id si no existe
        if 'request_id' not in extra:
            extra['request_id'] = RequestContext.generate_request_id()

        kwargs['extra'] = {'extra': extra}
        return msg, kwargs


def setup_logging(
    service_name: str = "rexus",
    environment: str = "production",
    log_level: str = "INFO",
    log_file: str = None,
    json_format: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging estructurado.

    Args:
        service_name: Nombre del servicio
        environment: Ambiente (development, staging, production)
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta al archivo de log
        json_format: Si usar formato JSON

    Returns:
        Logger configurado
    """
    # Obtener logger raíz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remover handlers existentes
    logger.handlers.clear()

    # Crear formatter
    if json_format:
        formatter = StructuredFormatter(service_name, environment)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler de archivo si se especifica
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> ContextualLogger:
    """
    Obtiene un logger con contexto.

    Args:
        name: Nombre del logger

    Returns:
        Logger contextual
    """
    base_logger = logging.getLogger(name)
    return ContextualLogger(base_logger)


# Decoradores para logging
def log_execution(logger_name: str = None, log_level: str = "INFO"):
    """
    Decorador para loguear ejecución de funciones.

    Args:
        logger_name: Nombre del logger
        log_level: Nivel de log

    Example:
        @log_execution("inventario", "DEBUG")
        def get_productos():
            # Esta función logueará entrada y salida
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            log_func = getattr(logger, log_level.lower())

            # Loguear entrada
            log_func(
                f"Entrando a {func.__name__}",
                extra={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                }
            )

            try:
                # Ejecutar función
                result = func(*args, **kwargs)

                # Loguear salida exitosa
                log_func(
                    f"Saliendo de {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "status": "success"
                    }
                )

                return result

            except Exception as e:
                # Loguear error
                logger.error(
                    f"Error en {func.__name__}: {str(e)}",
                    extra={
                        "function": func.__name__,
                        "status": "error",
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_errors(logger_name: str = None):
    """
    Decorador para loguear errores de funciones.

    Args:
        logger_name: Nombre del logger

    Example:
        @log_errors("inventario")
        def risky_operation():
            # Los errores se loguearán automáticamente
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = get_logger(logger_name or func.__module__)
                logger.error(
                    f"Error en {func.__name__}: {str(e)}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


@contextmanager
def log_context(**kwargs):
    """
    Context manager para agregar contexto temporal al logging.

    Args:
        **kwargs: Pares clave-valor a agregar al contexto

    Example:
        with log_context(user_id=123, action="create_pedido"):
            # Todos los logs dentro tendrán user_id y action
            create_pedido()
    """
    # Guardar contexto previo
    prev_context = RequestContext.to_dict()

    try:
        # Establecer nuevo contexto
        for key, value in kwargs.items():
            RequestContext.set(key, value)

        yield

    finally:
        # Restaurar contexto previo
        RequestContext.clear()
        RequestContext._context.update(prev_context)


def log_api_request(method: str, path: str, status_code: int,
                   duration_ms: float, **extra):
    """
    Loguea una solicitud API.

    Args:
        method: Método HTTP
        path: Ruta solicitada
        status_code: Código de estado
        duration_ms: Duración en ms
        **extra: Información adicional
    """
    logger = get_logger("api")
    logger.info(
        f"{method} {path} - {status_code}",
        extra={
            "http_method": method,
            "http_path": path,
            "http_status": status_code,
            "duration_ms": duration_ms,
            **extra
        }
    )


def log_db_query(query_type: str, table: str, duration_ms: float,
                 rows_affected: int = None, **extra):
    """
    Loguea una consulta a base de datos.

    Args:
        query_type: Tipo de consulta (SELECT, INSERT, UPDATE, DELETE)
        table: Tabla afectada
        duration_ms: Duración en ms
        rows_affected: Filas afectadas
        **extra: Información adicional
    """
    logger = get_logger("database")
    logger.debug(
        f"{query_type} on {table}",
        extra={
            "query_type": query_type,
            "table": table,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            **extra
        }
    )


def log_security_event(event_type: str, severity: str = "INFO",
                       user_id: str = None, **extra):
    """
    Loguea un evento de seguridad.

    Args:
        event_type: Tipo de evento (login, logout, permission_denied, etc.)
        severity: Severidad (INFO, WARNING, ERROR)
        user_id: ID del usuario
        **extra: Información adicional
    """
    logger = get_logger("security")
    log_func = getattr(logger, severity.lower())

    log_func(
        f"Security event: {event_type}",
        extra={
            "security_event": event_type,
            "user_id": user_id,
            "severity": severity,
            **extra
        }
    )
