"""
BaseController - Controlador base unificado para módulos de Rexus
Proporciona funcionalidad común para todos los controladores del sistema ERP
"""

import logging
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class BaseController(QObject):
    """
    Controlador base unificado que proporciona funcionalidad común para todos los modules.
    
    Características:
    - Manejo de errores estandarizado
    - Logging centralizado
    - Validación de datos
    - Patrón de señales PyQt6
    - Gestión de modelo y vista
    """
    
    # Señales comunes para todos los controllers
    error_occurred = pyqtSignal(str)
    warning_occurred = pyqtSignal(str)
    info_message = pyqtSignal(str)
    operation_completed = pyqtSignal(str)
    
    def __init__(self, model=None, view=None, **kwargs):
        """
        Inicializa el controlador base.
        
        Args:
            model: Modelo de datos asociado
            view: Vista asociada
            **kwargs: Argumentos adicionales (db_connection, usuario_actual, etc.)
        """
        super().__init__()
        
        # Componentes MVC
        self.model = model
        self.view = view
        
        # Configuración adicional
        self.parent_widget = kwargs.get('parent_widget')
        self.db_connection = kwargs.get('db_connection')
        self.usuario_actual = kwargs.get('usuario_actual', {"id": 1, "nombre": "SISTEMA"})
        self.module_name = kwargs.get('module_name', self.__class__.__name__.replace('Controller', '').lower())
        
        # Logger específico del módulo
        self.logger = logging.getLogger(f"rexus.modules.{self.module_name}.controller")
        
        # Estado del controlador
        self.data_cache = {}
        self.is_initialized = False
        self._errors = []
        self._last_operation = None
        
        # Configuración inicial
        self._setup_base_signals()
        self.initialize()

    def _setup_base_signals(self):
        """Configura las señales base del controlador."""
        try:
            # Conectar señales de error a logging
            self.error_occurred.connect(self._handle_error_signal)
            self.warning_occurred.connect(self._handle_warning_signal)
            self.info_message.connect(self._handle_info_signal)
            
        except Exception as e:
            self.logger.error(f"Error configurando señales base: {e}")

    def _handle_error_signal(self, message: str):
        """Maneja las señales de error."""
        self.logger.error(f"[SIGNAL] {message}")
        self._errors.append(message)

    def _handle_warning_signal(self, message: str):
        """Maneja las señales de advertencia."""
        self.logger.warning(f"[SIGNAL] {message}")

    def _handle_info_signal(self, message: str):
        """Maneja las señales de información."""
        self.logger.info(f"[SIGNAL] {message}")
        
    def initialize(self) -> bool:
        """Inicializa el controlador (puede ser sobrescrito en subclases)."""
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
            self.emit_error(error_msg)
            return False

        return True
    
    def validate_model_available(self) -> bool:
        """Valida que el modelo esté disponible."""
        if not self.model:
            self.emit_error("Modelo no disponible")
            return False
        return True

    def validate_view_available(self) -> bool:
        """Valida que la vista esté disponible."""
        if not self.view:
            self.emit_warning("Vista no disponible")
            return False
        return True
    
    def emit_error(self, message: str):
        """Emite una señal de error y registra en logs."""
        self.error_occurred.emit(message)
        
        # Mostrar error en vista si está disponible
        if self.view and hasattr(self.view, 'mostrar_error'):
            self.view.mostrar_error(message)
        else:
            self.show_error_message(message)

    def emit_warning(self, message: str):
        """Emite una señal de advertencia y registra en logs."""
        self.warning_occurred.emit(message)
        
        # Mostrar advertencia en vista si está disponible
        if self.view and hasattr(self.view, 'mostrar_advertencia'):
            self.view.mostrar_advertencia(message)
        else:
            self.show_warning_message(message)

    def emit_info(self, message: str):
        """Emite una señal de información y registra en logs."""
        self.info_message.emit(message)
        
        # Mostrar información en vista si está disponible
        if self.view and hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(message, "info")
        else:
            self.show_info_message(message)

    def emit_success(self, message: str):
        """Emite una señal de éxito."""
        self.operation_completed.emit(message)
        
        # Mostrar éxito en vista si está disponible
        if self.view and hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(message, "success")
        else:
            self.show_info_message(message, "Éxito")
            
    def execute_safe_operation(self, operation_func, operation_name: str, *args, **kwargs):
        """
        Ejecuta una operación de manera segura con manejo de errores estandarizado.
        
        Args:
            operation_func: Función a ejecutar
            operation_name: Nombre descriptivo de la operación
            *args, **kwargs: Argumentos para la función
            
        Returns:
            El resultado de la operación o None si hay error
        """
        try:
            self.logger.debug(f"Iniciando operación: {operation_name}")
            self._last_operation = operation_name
            
            result = operation_func(*args, **kwargs)
            
            self.logger.debug(f"Operación {operation_name} completada exitosamente")
            return result
            
        except Exception as e:
            self.handle_error(e, operation_name)
            return None

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
