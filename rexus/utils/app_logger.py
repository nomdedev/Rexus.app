"""
Rexus.app - Sistema de Logging

Módulo centralizado para el manejo de logs de la aplicación.
Proporciona logging estructurado con diferentes niveles y componentes.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

class AppLogger:
    """
    Logger centralizado para la aplicación Rexus.
    Maneja logs a archivos y consola con rotación automática.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            self._initialized = True

    def _setup_logger(self):
        """Configura el sistema de logging."""
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configurar logger principal
        self.logger = logging.getLogger('rexus')
        self.logger.setLevel(logging.DEBUG)

        # Evitar duplicación de handlers
        if self.logger.handlers:
            return

        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Handler para archivo (con rotación)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'rexus.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'error.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Agregar handlers al logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self, name: str = 'rexus') -> logging.Logger:
        """Obtiene un logger con el nombre especificado."""
        return logging.getLogger(f'rexus.{name}')

    def log_info(self, message: str, component: str = 'general'):
        """Registra un mensaje informativo."""
        logger = self.get_logger(component)
        logger.info(message)

    def log_error(self, message: str, component: str = 'general'):
        """Registra un mensaje de error."""
        logger = self.get_logger(component)
        logger.error(message)

    def log_warning(self, message: str, component: str = 'general'):
        """Registra un mensaje de advertencia."""
        logger = self.get_logger(component)
        logger.warning(message)

    def log_critical(self, message: str, component: str = 'general'):
        """Registra un mensaje crítico."""
        logger = self.get_logger(component)
        logger.critical(message)

    def log_security(self, level: str, message: str, user: Optional[str] = None):
        """Registra un evento de seguridad."""
        security_logger = self.get_logger('security')
        if user:
            message = f"[USER:{user}] {message}"
        security_logger.info(f"[{level}] {message}")

# Instancia global del logger
app_logger = AppLogger()

# Funciones de conveniencia para uso directo
def log_info(msg: str, comp: str = "general"):
    """Función de conveniencia para logging informativo."""
    app_logger.log_info(msg, comp)

def log_error(msg: str, comp: str = "general"):
    """Función de conveniencia para logging de errores."""
    app_logger.log_error(msg, comp)

def log_warning(msg: str, comp: str = "general"):
    """Función de conveniencia para logging de advertencias."""
    app_logger.log_warning(msg, comp)

def log_critical(msg: str, comp: str = "general"):
    """Función de conveniencia para logging crítico."""
    app_logger.log_critical(msg, comp)

def log_security(level: str, msg: str, user: Optional[str] = None):
    """Función de conveniencia para logging de seguridad."""
    app_logger.log_security(level, msg, user)
