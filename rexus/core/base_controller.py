"""
Base Controller - Clase base para todos los controladores de Rexus.app
Proporciona funcionalidad común, defensas y patrones estandarizados.

Fecha: 15/08/2025
Objetivo: Resolver problemas críticos de estabilidad y consistencia
"""

from PyQt6.QtCore import QObject
from typing import Any, Dict, Optional

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
except ImportError:
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    
    def get_logger(name):
        return DummyLogger()

# Importar sistema de mensajería centralizado
try:
    from rexus.utils.message_system import show_success, show_error, show_warning, show_info
    MESSAGING_AVAILABLE = True
except ImportError:
    from PyQt6.QtWidgets import QMessageBox
    def show_success(parent, title, message): QMessageBox.information(parent, title, message)
    def show_error(parent, title, message): QMessageBox.critical(parent, title, message)
    def show_warning(parent, title, message): QMessageBox.warning(parent, title, message)
    def show_info(parent, title, message): QMessageBox.information(parent, title, message)
    MESSAGING_AVAILABLE = False


class BaseController(QObject):
    """
    Clase base para todos los controladores de Rexus.app.
    
    Proporciona:
    - Defensas contra componentes ausentes
    - Logging centralizado
    - Mensajería estandarizada
    - Validaciones comunes
    - Patrones de error handling
    """
    
    def __init__(self, module_name: str, model=None, view=None, db_connection=None):
        """
        Inicializa el controlador base.
        
        Args:
            module_name: Nombre del módulo para logging
            model: Modelo del módulo
            view: Vista del módulo
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        
        self.module_name = module_name
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        
        # Configurar logger específico del módulo
        self.logger = get_logger(f"{module_name}.controller")
        
        # Validar componentes críticos al inicializar
        self._validate_components()
        
        # Establecer referencia bidireccional con la vista si existe
        if self.view:
            self.view.controller = self
    
    def _validate_components(self):
        """
        Valida que los componentes críticos estén disponibles.
        Registra advertencias pero no falla la inicialización.
        """
        self.logger.debug(f"Validando componentes del controlador {self.module_name}")
        
        if not self.model:
            self.logger.error(f"CRITICO: Modelo de {self.module_name} no disponible")
            
        if not self.view:
            self.logger.warning(f"Vista de {self.module_name} no disponible")
            
        if not self.db_connection:
            self.logger.warning(f"Conexión de BD no disponible para {self.module_name}")
            
        self.logger.info(f"Validación de componentes {self.module_name} completada")
    
    def _ensure_model_available(self, operation_name: str = "operación") -> bool:
        """
        Asegura que el modelo esté disponible para una operación.
        
        Args:
            operation_name: Nombre de la operación para logging
            
        Returns:
            bool: True si el modelo está disponible
        """
        if not self.model:
            error_msg = f"Modelo no disponible para {operation_name} en {self.module_name}"
            self.logger.error(error_msg)
            self.show_error_message(error_msg)
            return False
        return True
    
    def _ensure_view_available(self, operation_name: str = "operación") -> bool:
        """
        Asegura que la vista esté disponible para una operación.
        
        Args:
            operation_name: Nombre de la operación para logging
            
        Returns:
            bool: True si la vista está disponible
        """
        if not self.view:
            error_msg = f"Vista no disponible para {operation_name} en {self.module_name}"
            self.logger.error(error_msg)
            return False
        return True
    
    def _ensure_db_available(self, operation_name: str = "operación") -> bool:
        """
        Asegura que la conexión de BD esté disponible para una operación.
        
        Args:
            operation_name: Nombre de la operación para logging
            
        Returns:
            bool: True si la conexión está disponible
        """
        if not self.db_connection:
            error_msg = f"Conexión BD no disponible para {operation_name} en {self.module_name}"
            self.logger.error(error_msg)
            self.show_error_message(error_msg)
            return False
        return True
    
    def show_message(self, mensaje: str, tipo: str = "info"):
        """
        Muestra un mensaje usando el sistema centralizado.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')
        """
        self.logger.info(f"Mensaje mostrado en {self.module_name}: {mensaje}")
        
        if not self.view:
            self.logger.warning(f"Vista no disponible para mostrar mensaje: {mensaje}")
            return
        
        title = f"{self.module_name.title()}"
        if tipo == "success":
            show_success(self.view, title, mensaje)
        elif tipo == "warning":
            show_warning(self.view, title, mensaje)
        elif tipo == "error":
            show_error(self.view, f"Error - {title}", mensaje)
        else:
            show_info(self.view, title, mensaje)
    
    def show_error_message(self, mensaje: str):
        """Muestra un mensaje de error con logging."""
        self.logger.error(f"Error en {self.module_name}: {mensaje}")
        
        if self.view:
            show_error(self.view, f"Error - {self.module_name.title()}", mensaje)
        else:
            self.logger.error(f"[NO VIEW] Error: {mensaje}")
    
    def show_success_message(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        self.logger.info(f"Éxito en {self.module_name}: {mensaje}")
        self.show_message(mensaje, "success")
    
    def show_warning_message(self, mensaje: str):
        """Muestra un mensaje de advertencia."""
        self.logger.warning(f"Advertencia en {self.module_name}: {mensaje}")
        self.show_message(mensaje, "warning")
    
    def show_info_message(self, mensaje: str):
        """Muestra un mensaje informativo."""
        self.logger.info(f"Info en {self.module_name}: {mensaje}")
        self.show_message(mensaje, "info")
    
    def safe_model_operation(self, operation_func, operation_name: str, *args, **kwargs):
        """
        Ejecuta una operación del modelo de forma segura.
        
        Args:
            operation_func: Función del modelo a ejecutar
            operation_name: Nombre de la operación para logging
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la operación o None si falla
        """
        try:
            if not self._ensure_model_available(operation_name):
                return None
            
            self.logger.debug(f"Ejecutando operación segura: {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.debug(f"Operación {operation_name} completada exitosamente")
            return result
            
        except Exception as e:
            error_msg = f"Error en {operation_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_message(error_msg)
            return None
    
    def safe_view_operation(self, operation_func, operation_name: str, *args, **kwargs):
        """
        Ejecuta una operación de la vista de forma segura.
        
        Args:
            operation_func: Función de la vista a ejecutar
            operation_name: Nombre de la operación para logging
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la operación o None si falla
        """
        try:
            if not self._ensure_view_available(operation_name):
                return None
            
            self.logger.debug(f"Ejecutando operación de vista: {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.debug(f"Operación de vista {operation_name} completada")
            return result
            
        except Exception as e:
            error_msg = f"Error en operación de vista {operation_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_message(error_msg)
            return None
    
    def validate_data(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        Valida que los datos contengan los campos requeridos.
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
            
        Returns:
            bool: True si todos los campos están presentes
        """
        if not isinstance(data, dict):
            self.logger.error("Datos para validar deben ser un diccionario")
            self.show_error_message("Datos inválidos")
            return False
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            self.logger.warning(error_msg)
            self.show_error_message(error_msg)
            return False
        
        return True
    
    def cleanup(self):
        """
        Limpia recursos cuando se cierra el controlador.
        Debe ser sobrescrito por las subclases si necesitan limpieza específica.
        """
        self.logger.info(f"Limpiando recursos del controlador {self.module_name}")
        
        # Limpiar referencias
        if self.view and hasattr(self.view, 'controller'):
            self.view.controller = None
            
        self.model = None
        self.view = None
        self.db_connection = None