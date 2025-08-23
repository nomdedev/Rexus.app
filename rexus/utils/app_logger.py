"""
Sistema de Logging Centralizado para Rexus.app
Proporciona logging consistente con niveles, formateo y rotación de archivos

Fecha: 15/08/2025
Objetivo: Reemplazar prints dispersos con logging estructurado
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class RexusLogger:
    """
    Logger centralizado para toda la aplicación Rexus.
    
    Características:
    - Múltiples niveles de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Salida tanto a consola como a archivo
    - Rotación automática de archivos de log
    - Formato consistente con timestamps e información del módulo
    - Filtrado por módulo/componente
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            RexusLogger._initialized = True
    
    def _setup_logging(self):
        """Configura el sistema de logging."""
        # Crear directorio de logs si no existe
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar logger principal
        self.logger = logging.getLogger("rexus")
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers si ya están configurados
        if self.logger.handlers:
            return
        
        # Formatter para logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola (nivel INFO y superior)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler para archivo principal (todos los niveles)
        main_log_file = self.logs_dir / f"rexus_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler separado para errores críticos
        error_log_file = self.logs_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Agregar handlers al logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Configurar loggers específicos para componentes
        self._setup_component_loggers(formatter)
        
        self.logger.info("Sistema de logging Rexus inicializado")
    
    def _setup_component_loggers(self, formatter):
        """Configura loggers específicos para componentes críticos."""
        critical_components = [
            'security', 'database', 'authentication', 'modules',
            'ui', 'cache', 'sql', 'backup', 'performance'
        ]
        
        for component in critical_components:
            component_logger = logging.getLogger(f"rexus.{component}")
            component_logger.setLevel(logging.DEBUG)
            
            # Archivo separado para componentes críticos
            component_file = self.logs_dir / f"{component}.log"
            component_handler = logging.handlers.RotatingFileHandler(
                component_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            component_handler.setLevel(logging.DEBUG)
            component_handler.setFormatter(formatter)
            component_logger.addHandler(component_handler)
    
    def get_logger(self, name: str = "rexus") -> logging.Logger:
        """
        Obtiene un logger para un módulo específico.
        
        Args:
            name: Nombre del módulo/componente
            
        Returns:
            Logger configurado
        """
        if not name.startswith("rexus"):
            name = f"rexus.{name}"
        
        return logging.getLogger(name)
    
    def log_startup_info(self):
        """Registra información de inicio de la aplicación."""
        logger = self.get_logger("startup")
        logger.info("=" * 60)
        logger.info("REXUS.APP - INICIO DE APLICACIÓN")
        logger.info(f"Versión Python: {sys.version}")
        logger.info(f"Directorio de trabajo: {os.getcwd()}")
        logger.info(f"Argumentos: {sys.argv}")
        logger.info("=" * 60)
    
    def log_security_event(self, level: str, message: str, user: Optional[str] = None):
        """
        Registra eventos de seguridad con formato especial.
        
        Args:
            level: Nivel de seguridad (INFO, WARNING, CRITICAL)
            message: Mensaje del evento
            user: Usuario relacionado (opcional)
        """
        security_logger = self.get_logger("security")
        user_info = f" | Usuario: {user}" if user else ""
        security_message = f"[SECURITY-{level}] {message}{user_info}"
        
        if level == "CRITICAL":
            security_logger.critical(security_message)
        elif level == "WARNING":
            security_logger.warning(security_message)
        else:
            security_logger.info(security_message)
    
    def log_database_operation(self, operation: str, table: str, result: str, user: Optional[str] = None):
        """
        Registra operaciones de base de datos.
        
        Args:
            operation: Tipo de operación (SELECT, INSERT, UPDATE, DELETE)
            table: Tabla afectada
            result: Resultado de la operación
            user: Usuario que ejecutó la operación
        """
        db_logger = self.get_logger("database")
        user_info = f" | Usuario: {user}" if user else ""
        db_message = f"[DB-{operation}] Tabla: {table} | Resultado: {result}{user_info}"
        db_logger.info(db_message)
    
    def log_performance_metric(self, component: str, metric: str, value: float, unit: str = "ms"):
        """
        Registra métricas de rendimiento.
        
        Args:
            component: Componente medido
            metric: Tipo de métrica
            value: Valor medido
            unit: Unidad de medida
        """
        perf_logger = self.get_logger("performance")
        perf_message = f"[PERF] {component} | {metric}: {value} {unit}"
        perf_logger.info(perf_message)
    
    def set_console_level(self, level: int):
        """
        Cambia el nivel de logging en consola.
        
        Args:
            level: Nivel de logging (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level)
                break


# Instancia global del logger
app_logger = RexusLogger()

# Funciones de conveniencia para uso directo
def get_logger(name: str = "rexus") -> logging.Logger:
    """Obtiene un logger para un módulo específico."""
    return app_logger.get_logger(name)

def log_info(message: str, component: str = "general"):
    """Log nivel INFO."""
    logger = get_logger(component)
    logger.info(message)

def log_warning(message: str, component: str = "general"):
    """Log nivel WARNING."""
    logger = get_logger(component)
    logger.warning(message)

def log_error(message: str, component: str = "general", exc_info: bool = False):
    """Log nivel ERROR."""
    logger = get_logger(component)
    logger.error(message, exc_info=exc_info)

def log_critical(message: str, component: str = "general", exc_info: bool = False):
    """Log nivel CRITICAL."""
    logger = get_logger(component)
    logger.critical(message, exc_info=exc_info)

def log_debug(message: str, component: str = "general"):
    """Log nivel DEBUG."""
    logger = get_logger(component)
    logger.debug(message)

def log_security(level: str, message: str, user: Optional[str] = None):
    """Log evento de seguridad."""
    app_logger.log_security_event(level, message, user)

def log_database(operation: str, table: str, result: str, user: Optional[str] = None):
    """Log operación de base de datos."""
    app_logger.log_database_operation(operation, table, result, user)

def log_performance(component: str, metric: str, value: float, unit: str = "ms"):
    """Log métrica de rendimiento."""
    app_logger.log_performance_metric(component, metric, value, unit)


# Funciones para migrar prints existentes
def replace_print_with_logging():
    """
    Utilidad para ayudar a migrar prints existentes a logging.
    
    Ejemplos de migración:
    
    logger.info("[INFO] Mensaje") -> log_info("Mensaje", "component")
    logger.info("[ERROR] Error") -> log_error("Error", "component")
    logger.info("[DEBUG] Debug") -> log_debug("Debug", "component")
    logger.info(f"[SECURITY] {msg}") -> log_security("INFO", msg)
    """
    pass


# Ejemplo de uso en módulos:
"""
# En cualquier archivo del proyecto:
from rexus.utils.app_logger import get_logger, log_info, log_error, log_security

# Obtener logger específico para el módulo
logger = get_logger()
logger.info("Módulo inventario inicializado")

# Usar funciones de conveniencia
log_info("Operación completada", "inventario")
log_error("Error en validación", "inventario")
log_security("CRITICAL", "Intento de acceso no autorizado", "usuario123")

# En lugar de:
logger.info("[INFO] Mensaje")
# Usar:
log_info("Mensaje", "component_name")
"""