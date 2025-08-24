"""
BaseController - Controlador base para módulos de Rexus
Proporciona funcionalidad común para todos los controladores
"""

import logging
from typing import Any, Dict, List, Optional
from PyQt6.QtWidgets import QMessageBox, QWidget

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class BaseController:
    """Controlador base para módulos del sistema."""
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        """Inicializa el controlador base."""
        self.parent_widget = parent_widget
        self.logger = logger
        self.data_cache = {}
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el controlador (implementar en subclases)."""
        try:
            self.is_initialized = True
            self.logger.info(f"{self.__class__.__name__} inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando {self.__class__.__name__}: {e}")
            return False
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Valida que estén presentes los campos requeridos."""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            self.logger.warning(error_msg)
            self.show_error_message(error_msg)
            return False

        return True

    def cleanup(self):
        """Limpia recursos del controlador."""
        try:
            self.data_cache.clear()
            self.is_initialized = False
            self.logger.info(f"{self.__class__.__name__} limpiado correctamente")
        except Exception as e:
            self.logger.error(f"Error limpiando {self.__class__.__name__}: {e}")
    
    def show_error_message(self, message: str, title: str = "Error"):
        """Muestra mensaje de error al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.critical(self.parent_widget, title, message)
            else:
                self.logger.error(f"Error UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def show_info_message(self, message: str, title: str = "Información"):
        """Muestra mensaje informativo al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.information(self.parent_widget, title, message)
            else:
                self.logger.info(f"Info UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def show_warning_message(self, message: str, title: str = "Advertencia"):
        """Muestra mensaje de advertencia al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.warning(self.parent_widget, title, message)
            else:
                self.logger.warning(f"Warning UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def get_cached_data(self, key: str) -> Any:
        """Obtiene datos del cache."""
        return self.data_cache.get(key)
    
    def set_cached_data(self, key: str, value: Any) -> None:
        """Almacena datos en el cache."""
        self.data_cache[key] = value
    
    def clear_cache(self) -> None:
        """Limpia el cache de datos."""
        self.data_cache.clear()
        
    def is_ready(self) -> bool:
        """Verifica si el controlador está listo para usar."""
        return self.is_initialized
    
    def handle_error(self, error: Exception, context: str = ""):
        """Maneja errores de forma centralizada."""
        error_msg = f"Error en {context}: {str(error)}" if context else str(error)
        self.logger.exception(error_msg)
        self.show_error_message(error_msg)
