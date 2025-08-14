"""
Sistema de logging avanzado para Rexus
Versión: 2.0.0 - Producción Ready
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

try:
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

from .config import LOGGING_CONFIG, LOGS_DIR

class RexusLogger:
    """
    Sistema de logging centralizado para Rexus con múltiples backends
    y características avanzadas como structured logging, métricas y alertas.
    """

    _instances = {}
    _configured = False

    def __init__(self, name: str = "rexus"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()

    @classmethod
    def get_logger(cls, name: str = "rexus") -> "RexusLogger":
        """Obtener instancia singleton del logger"""
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def _setup_logger(self):
        """Configurar el logger con handlers y formatters"""
        if self._configured:
            return

        # Crear directorio de logs si no existe
        LOGS_DIR.mkdir(exist_ok=True)

        # Configurar nivel de logging
        level = getattr(logging, LOGGING_CONFIG.get("level", "INFO").upper())
        self.logger.setLevel(level)

        # Limpiar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = self._get_console_formatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOGGING_CONFIG.get("file_path", LOGS_DIR / "rexus.log"),
            maxBytes=self._parse_size(LOGGING_CONFIG.get("max_size", "10MB")),
            backupCount=LOGGING_CONFIG.get("backup_count", 5),
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_formatter = self._get_file_formatter()
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Handler para errores críticos (archivo separado)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "errors.log",
            maxBytes=self._parse_size("5MB"),
            backupCount=3,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)

        # Handler para audit logs (archivo separado)
        audit_handler = logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "audit.log",
            maxBytes=self._parse_size("10MB"),
            backupCount=10,
            encoding="utf-8"
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = self._get_audit_formatter()
        audit_handler.setFormatter(audit_formatter)

        # Crear logger separado para auditoría
        audit_logger = logging.getLogger(f"{self.name}.audit")
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)

        # Configurar structured logging si está disponible
        if STRUCTLOG_AVAILABLE:
            self._setup_structlog()

        self._configured = True
        self.info("Sistema de logging inicializado", extra={
            "version": "2.0.0",
            "handlers": len(self.logger.handlers),
            "level": level
        })

    def _get_console_formatter(self) -> logging.Formatter:
        """Formatter colorizado para consola"""
        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
                'ENDC': '\033[0m',      # End color
            }

            def format(self, record):
                log_color = self.COLORS.get(record.levelname, '')
                record.levelname = f"{log_color}{record.levelname}{self.COLORS['ENDC']}"
                return super().format(record)

        return ColoredFormatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _get_file_formatter(self) -> logging.Formatter:
        """Formatter para archivos de log"""
        return logging.Formatter(
            fmt=LOGGING_CONFIG.get("format",
                "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(funcName)s | %(message)s"),
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _get_audit_formatter(self) -> logging.Formatter:
        """Formatter para logs de auditoría (JSON)"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'module': record.name,
                    'function': record.funcName,
                    'line': record.lineno,
                    'message': record.getMessage(),
                }

                # Agregar información extra si existe
                if hasattr(record, 'extra_data'):
                    log_entry.update(record.extra_data)

                return json.dumps(log_entry, ensure_ascii=False)

        return JSONFormatter()

    def _setup_structlog(self):
        """Configurar structured logging con structlog"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def _parse_size(self, size_str: str) -> int:
        """Convertir string de tamaño (ej: '10MB',
'10M',
            '10 MB',
            '10 K') a bytes"""
        if not isinstance(size_str, str):
            raise ValueError(f"Tamaño de log inválido: {size_str}")
        size_str = size_str.replace(" ", "").upper().strip()
        units = [
            ("GB", 1024**3), ("G", 1024**3),
            ("MB", 1024**2), ("M", 1024**2),
            ("KB", 1024), ("K", 1024),
            ("B", 1)
        ]
        for unit, multiplier in units:
            if size_str.endswith(unit):
                num = size_str[:-len(unit)]
                try:
                    return int(num) * multiplier
                except ValueError:
                    raise ValueError(f"Tamaño de log inválido: {size_str}")
        # Si solo es un número, asumir bytes
        try:
            return int(size_str)
        except ValueError:
            raise ValueError(f"Tamaño de log inválido: {size_str}")

    # Métodos de logging estándar
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log message de debug"""
        self.logger.debug(message, extra=extra or {})

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log message informativo"""
        self.logger.info(message, extra=extra or {})

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log message de advertencia"""
        self.logger.warning(message, extra=extra or {})

    def error(self,
message: str,
        extra: Optional[Dict[str,
        Any]] = None,
        exc_info: bool = True):
        """Log message de error"""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)

    def critical(self,
message: str,
        extra: Optional[Dict[str,
        Any]] = None,
        exc_info: bool = True):
        """Log message crítico"""
        self.logger.critical(message, extra=extra or {}, exc_info=exc_info)

    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log excepción con traceback completo"""
        self.logger.exception(message, extra=extra or {})

    # Métodos especializados
    def audit(self, action: str, user: str = None, resource: str = None,
              result: str = "success", extra: Optional[Dict[str, Any]] = None):
        """Log de auditoría para acciones importantes"""
        audit_logger = logging.getLogger(f"{self.name}.audit")
        audit_data = {
            'action': action,
            'user': user,
            'resource': resource,
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
            **(extra or {})
        }

        audit_logger.info("AUDIT", extra={'extra_data': audit_data})

    def performance(self, operation: str, duration: float,
                   extra: Optional[Dict[str, Any]] = None):
        """Log de métricas de performance"""
        perf_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.utcnow().isoformat(),
            **(extra or {})
        }

        self.info(f"PERFORMANCE: {operation}", extra=perf_data)

    def security(self, event: str, severity: str = "info",
                source_ip: str = None, user: str = None,
                extra: Optional[Dict[str, Any]] = None):
        """Log de eventos de seguridad"""
        security_data = {
            'security_event': event,
            'severity': severity,
            'source_ip': source_ip,
            'user': user,
            'timestamp': datetime.utcnow().isoformat(),
            **(extra or {})
        }

        level_method = getattr(self.logger, severity.lower(), self.logger.info)
        level_method(f"SECURITY: {event}", extra=security_data)

# Decorador para logging automático de funciones
def log_function_call(logger: Optional[RexusLogger] = None,
                     log_args: bool = False,
                     log_result: bool = False):
    """
    Decorador para logging automático de llamadas a funciones.

    Args:
        logger: Instancia del logger a usar
        log_args: Si incluir argumentos en el log
        log_result: Si incluir resultado en el log
    """
    if logger is None:
        logger = RexusLogger.get_logger()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            start_time = datetime.utcnow()

            # Log de inicio
            log_data = {'function': func_name}
            if log_args:
                log_data['args'] = str(args)
                log_data['kwargs'] = str(kwargs)

            logger.debug(f"Iniciando función: {func_name}", extra=log_data)

            try:
                result = func(*args, **kwargs)

                # Log de éxito
                duration = (datetime.utcnow() - start_time).total_seconds()
                success_data = {
                    'function': func_name,
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'success'
                }

                if log_result:
                    success_data['result'] = str(result)

                logger.debug(f"Función completada: {func_name}", extra=success_data)
                return result

            except Exception as e:
                # Log de error
                duration = (datetime.utcnow() - start_time).total_seconds()
                error_data = {
                    'function': func_name,
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }

                logger.error(f"Error en función: {func_name}", extra=error_data, exc_info=True)
                raise

        return wrapper
    return decorator

# Instancia global del logger
logger = RexusLogger.get_logger()

# Funciones de conveniencia para compatibilidad
def get_logger(name: str = "rexus") -> RexusLogger:
    """Obtener instancia del logger"""
    return RexusLogger.get_logger(name)

def setup_logger(name: str = "rexus", level: int = logging.INFO) -> RexusLogger:
    """Función de compatibilidad con el logger anterior"""
    return RexusLogger.get_logger(name)

def audit_log(action: str, user: str = None, resource: str = None,
              result: str = "success", **kwargs):
    """Función de conveniencia para audit logging"""
    logger.audit(action, user, resource, result, kwargs)

def performance_log(operation: str, duration: float, **kwargs):
    """Función de conveniencia para performance logging"""
    logger.performance(operation, duration, kwargs)

def security_log(event: str, severity: str = "info", **kwargs):
    """Función de conveniencia para security logging"""
    logger.security(event, severity, **kwargs)

# Funciones de compatibilidad con el logger anterior
def log_info(message: str):
    """Log de información"""
    logger.info(message)

def log_warning(message: str):
    """Log de advertencia"""
    logger.warning(message)

def log_error(message: str):
    """Log de error"""
    logger.error(message)

def log_debug(message: str):
    """Log de debug"""
    logger.debug(message)

# Configurar logging para librerías de terceros
def configure_third_party_logging():
    """Configurar logging para librerías externas"""
    # Reducir verbosidad de PyQt
    logging.getLogger("PyQt6").setLevel(logging.WARNING)

    # Configurar otros loggers problemáticos
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Alias para compatibilidad
default_logger = logger
Logger = logger

# Configurar automáticamente al importar
configure_third_party_logging()
