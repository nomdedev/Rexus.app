#!/usr/bin/env python3
"""
Configuración centralizada de logging para el sistema.
Proporciona una configuración consistente para todos los módulos.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

# Configuración de niveles de logging
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Configuración por defecto
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class LoggingConfig:
    """
    Clase para configurar el logging del sistema.
    """
    
    def __init__(self):
        """Inicializa la configuración de logging."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar el logger raíz
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Configura el logger raíz del sistema."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Evitar duplicación de handlers
        if root_logger.handlers:
            return
        
        # Crear formatter
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler para logs generales
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "rexus.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # File handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "rexus_errors.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str, level: str = None, log_file: str = None) -> logging.Logger:
        """
        Obtiene un logger configurado.
        
        Args:
            name: Nombre del logger
            level: Nivel de logging (opcional)
            log_file: Archivo de log específico (opcional)
            
        Returns:
            logging.Logger: Logger configurado
        """
        logger = logging.getLogger(name)
        
        # Establecer nivel si se proporciona
        if level and level.upper() in LOG_LEVELS:
            logger.setLevel(LOG_LEVELS[level.upper()])
        
        # Agregar file handler específico si se proporciona
        if log_file:
            self._add_file_handler(logger, log_file)
        
        return logger
    
    def _add_file_handler(self, logger: logging.Logger, log_file: str):
        """
        Agrega un file handler específico a un logger.
        
        Args:
            logger: Logger al que agregar el handler
            log_file: Nombre del archivo de log
        """
        # Evitar duplicación
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith(log_file):
                return
        
        file_path = self.log_dir / log_file
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def set_module_log_level(self, module_name: str, level: str):
        """
        Establece el nivel de logging para un módulo específico.
        
        Args:
            module_name: Nombre del módulo
            level: Nivel de logging
        """
        if level.upper() in LOG_LEVELS:
            logger = logging.getLogger(module_name)
            logger.setLevel(LOG_LEVELS[level.upper()])

# Instancia global de configuración
_logging_config = LoggingConfig()

# Funciones de conveniencia para uso directo
def get_logger(name: str, level: str = None, log_file: str = None) -> logging.Logger:
    """
    Función de conveniencia para obtener un logger configurado.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (opcional)
        log_file: Archivo de log específico (opcional)
        
    Returns:
        logging.Logger: Logger configurado
    """
    return _logging_config.get_logger(name, level, log_file)

def set_log_level(level: str):
    """
    Establece el nivel de logging global.
    
    Args:
        level: Nivel de logging
    """
    if level.upper() in LOG_LEVELS:
        logging.getLogger().setLevel(LOG_LEVELS[level.upper()])

def set_module_log_level(module_name: str, level: str):
    """
    Establece el nivel de logging para un módulo específico.
    
    Args:
        module_name: Nombre del módulo
        level: Nivel de logging
    """
    _logging_config.set_module_log_level(module_name, level)

def configure_logging_from_env():
    """Configura el logging basado en variables de entorno."""
    # Nivel global
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    set_log_level(log_level)
    
    # Niveles por módulo
    module_levels = os.getenv('MODULE_LOG_LEVELS', '')
    if module_levels:
        for module_level in module_levels.split(','):
            if ':' in module_level:
                module, level = module_level.split(':', 1)
                set_module_log_level(module.strip(), level.strip())
