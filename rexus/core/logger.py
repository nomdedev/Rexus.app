"""
Sistema de logging avanzado para Rexus
Versión: 2.0.0 - Producción Ready
"""

import logging
import logging.handlers
import sys
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class RexusLogger:
    """Logger avanzado para Rexus con configuraciones específicas."""
    
    def __init__(self, name: str = "rexus"):
        """Inicializa el logger de Rexus."""
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers de logging."""
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Handler para archivo
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"rexus_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s: %(name)s - %(message)s'
        )
        
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(detailed_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log mensaje informativo."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log mensaje de advertencia.""" 
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log mensaje de error."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log mensaje de debug."""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log mensaje crítico."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log excepción con stack trace."""
        self.logger.exception(message, extra=kwargs)
    
    def log_dict(self, level: str, data: Dict[str, Any]):
        """Log diccionario como JSON."""
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            getattr(self.logger, level.lower())(f"Data: {json_str}")
        except Exception as e:
            self.error(f"Error logging dict: {e}")
    
    def set_level(self, level: str):
        """Establece nivel de logging."""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # Actualizar handlers
        for handler in self.logger.handlers:
            handler.setLevel(numeric_level)


# Instancia global del logger
logger = RexusLogger("rexus")


def get_logger(name: str = None) -> RexusLogger:
    """
    Obtiene un logger para el módulo especificado.
    
    Args:
        name: Nombre del módulo/logger
        
    Returns:
        Instancia de RexusLogger
    """
    if not name:
        return logger
    
    # Crear logger específico del módulo
    module_logger = RexusLogger(name)
    return module_logger


def configure_logging(level: str = "INFO", log_to_file: bool = True):
    """
    Configura el sistema de logging global.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Si escribir logs a archivo
    """
    logger.set_level(level)
    
    if log_to_file:
        logger.info("Sistema de logging configurado para archivos")
    
    logger.info(f"Nivel de logging establecido en: {level}")


def log_system_info():
    """Log información del sistema al inicio."""
    logger.info("=== INICIO DEL SISTEMA REXUS ===")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Plataforma: {sys.platform}")
    logger.info(f"Directorio de trabajo: {os.getcwd()}")


def log_startup_message():
    """Log mensaje de inicio."""
    logger.info("Sistema de logging Rexus inicializado")


def configure_third_party_logging():
    """Configura logging de librerías de terceros."""
    # Reducir verbosidad de PyQt6
    if "PyQt6" in sys.modules:
        logging.getLogger("PyQt6").setLevel(logging.WARNING)
    
    # Configurar otros loggers problemáticos
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def create_performance_logger() -> RexusLogger:
    """Crea logger específico para métricas de performance."""
    perf_logger = RexusLogger("rexus.performance")
    return perf_logger


def create_security_logger() -> RexusLogger:
    """Crea logger específico para eventos de seguridad."""
    security_logger = RexusLogger("rexus.security")
    return security_logger


def create_audit_logger() -> RexusLogger:
    """Crea logger específico para auditoría."""
    audit_logger = RexusLogger("rexus.audit")
    return audit_logger


def log_function_call(func_name: str, args: tuple = (), kwargs: Dict = None):
    """
    Log llamada a función para debugging.
    
    Args:
        func_name: Nombre de la función
        args: Argumentos posicionales
        kwargs: Argumentos con nombre
    """
    kwargs = kwargs or {}
    logger.debug(f"Llamada a {func_name} con args={args}, kwargs={kwargs}")


def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """
    Log métrica de performance.
    
    Args:
        metric_name: Nombre de la métrica
        value: Valor de la métrica
        unit: Unidad de medida
    """
    perf_logger = create_performance_logger()
    perf_logger.info(f"METRIC: {metric_name} = {value} {unit}")


def log_error_with_context(error: Exception, context: str = ""):
    """
    Log error con contexto adicional.
    
    Args:
        error: Excepción capturada
        context: Contexto adicional
    """
    error_msg = f"Error en {context}: {str(error)}" if context else str(error)
    logger.error(error_msg)
    logger.exception("Stack trace completo:")


# Alias para compatibilidad
default_logger = logger
Logger = logger

# Configurar automáticamente al importar
configure_third_party_logging()
log_startup_message()