"""
Configuración mejorada de logging para Rexus.app
"""

import logging
from pathlib import Path

class RexusLogger:
    """Logger personalizado para Rexus.app"""

    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        """Configura el sistema de logging"""

        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configurar loggers
        self.setup_main_logger()
        self.setup_security_logger()
        self.setup_error_logger()
        self.setup_audit_logger()

    def setup_main_logger(self):
        """Logger principal de la aplicación"""
        logger = logging.getLogger('rexus.main')
        logger.setLevel(logging.INFO)

        # Handler para archivo
        file_handler = logging.FileHandler('logs/rexus_main.log')
        file_handler.setLevel(logging.INFO)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    def setup_security_logger(self):
        """Logger para eventos de seguridad"""
        logger = logging.getLogger('rexus.security')
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def setup_error_logger(self):
        """Logger para errores críticos"""
        logger = logging.getLogger('rexus.errors')
        logger.setLevel(logging.ERROR)

        handler = logging.FileHandler('logs/errors.log')
        formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(name)s - %(levelname)s\n'
            'Message: %(message)s\n'
            'File: %(pathname)s:%(lineno)d\n'
            'Function: %(funcName)s\n'
            '---'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def setup_audit_logger(self):
        """Logger para auditoría de acciones"""
        logger = logging.getLogger('rexus.audit')
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def get_logger(name):
    """Obtiene un logger configurado"""
    return logging.getLogger(f'rexus.{name}')

def log_user_action(action, user=None, details=None):
    """Registra acción de usuario"""
    logger = get_logger('audit')
    message = f"Action: {action}"
    if user:
        message += f" | User: {user}"
    if details:
        message += f" | Details: {details}"
    logger.info(message)

def log_security_event(event, severity="INFO", details=None):
    """Registra evento de seguridad"""
    logger = get_logger('security')
    message = f"Event: {event}"
    if details:
        message += f" | Details: {details}"

    if severity == "CRITICAL":
        logger.critical(message)
    elif severity == "ERROR":
        logger.error(message)
    elif severity == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

# Inicializar logging al importar
rexus_logger = RexusLogger()
