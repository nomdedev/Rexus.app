"""
Sistema mejorado de manejo de errores para Rexus.app
"""

import sys
from typing import Callable, Any
from rexus.utils.logging_config import get_logger

class RexusErrorHandler:
    """Manejador centralizado de errores"""

    def __init__(self):
        self.logger = get_logger('errors')

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Maneja excepciones no capturadas"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
        self.logger.error(error_msg,
exc_info=(exc_type,
            exc_value,
            exc_traceback))

        # Mostrar error amigable al usuario
        self.show_user_friendly_error(str(exc_value))

    def show_user_friendly_error(self, error_message):
        """Muestra error amigable al usuario"""
        try:
            from PyQt6.QtWidgets import QMessageBox

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error - Rexus.app")
            msg_box.setText("Ha ocurrido un error inesperado")
            msg_box.setDetailedText(f"Detalles técnicos:\n{error_message}")
            msg_box.setInformativeText(
                "El error ha sido registrado. "
                "Si el problema persiste, contacte con soporte técnico."
            )
            msg_box.exec()
        except (ImportError, AttributeError, RuntimeError):
            # Fallback si PyQt no está disponible
            print(f"ERROR: {error_message}")

def error_boundary(func: Callable) -> Callable:
    """Decorador para capturar errores en funciones"""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = get_logger('errors')
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)

            # Re-raise para que el llamador pueda manejar el error
            raise
    return wrapper

def safe_execute(func: Callable, default_return=None, log_errors=True) -> Any:
    """Ejecuta función de forma segura con valor por defecto"""
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger = get_logger('errors')
            logger.error(f"Safe execution failed: {str(e)}", exc_info=True)
        return default_return

def validate_database_connection(func: Callable) -> Callable:
    """Decorador para validar conexión de base de datos"""
    def wrapper(*args, **kwargs):
        try:
            # Aquí iría la validación de conexión específica
            return func(*args, **kwargs)
        except Exception as e:
            logger = get_logger('errors')
            logger.error(f"Database operation failed: {str(e)}")
            raise DatabaseConnectionError(f"Error de base de datos: {str(e)}")
    return wrapper

class DatabaseConnectionError(Exception):
    """Excepción para errores de conexión de base de datos"""

class ValidationError(Exception):
    """Excepción para errores de validación"""

class SecurityError(Exception):
    """Excepción para errores de seguridad"""

# Instalar el manejador global de errores
error_handler = RexusErrorHandler()
sys.excepthook = error_handler.handle_exception
