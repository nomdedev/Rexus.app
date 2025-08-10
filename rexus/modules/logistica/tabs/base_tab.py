"""
Clase base para las pestañas del módulo de Logística

Proporciona funcionalidad común a todas las pestañas.
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import QWidget, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout

from ..constants import ICONS, MESSAGES
from ..styles import MAIN_STYLE, TAB_STYLE
from ..widgets import NotificationManager


class BaseTab(QWidget):
    """Clase base para todas las pestañas de logística."""
    
    # Señales comunes
    data_changed = pyqtSignal(dict)  # Emite cuando cambian los datos
    action_requested = pyqtSignal(str, dict)  # Emite cuando se solicita una acción
    
    def __init__(self, tab_name: str, icon: str = "", parent=None):
        super().__init__(parent)
        
        self.tab_name = tab_name
        self.icon = icon
        self.controller = None
        self.notification_manager = NotificationManager()
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Aplicar estilos
        self.setStyleSheet(MAIN_STYLE + TAB_STYLE)
        
        # Inicializar UI (implementado en subclases)
        self.init_ui()
        
        # Conectar señales (implementado en subclases)
        self.connect_signals()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario. Debe ser implementado en subclases."""
        raise NotImplementedError("Subclasses must implement init_ui()")
    
    def connect_signals(self):
        """Conecta las señales de la interfaz. Puede ser sobrescrito en subclases."""
        pass
    
    def set_controller(self, controller):
        """Establece el controlador para esta pestaña."""
        self.controller = controller
        self.on_controller_set()
    
    def on_controller_set(self):
        """Llamado cuando se establece el controlador. Puede ser sobrescrito en subclases."""
        pass
    
    def get_display_name(self) -> str:
        """Retorna el nombre para mostrar en la pestaña."""
        if self.icon:
            return f"{self.icon} {self.tab_name}"
        return self.tab_name
    
    def show_success(self, message: str, title: str = "Éxito"):
        """Muestra un mensaje de éxito."""
        self.notification_manager.show_success(self, title, message)
    
    def show_error(self, message: str, title: str = "Error"):
        """Muestra un mensaje de error."""
        self.notification_manager.show_error(self, title, message)
    
    def show_warning(self, message: str, title: str = "Advertencia"):
        """Muestra un mensaje de advertencia."""
        self.notification_manager.show_warning(self, title, message)
    
    def ask_confirmation(self, message: str, title: str = "Confirmación") -> bool:
        """Muestra un diálogo de confirmación."""
        return self.notification_manager.ask_confirmation(self, title, message)
    
    def get_data(self) -> Dict[str, Any]:
        """
        Retorna los datos actuales de la pestaña.
        Debe ser implementado en subclases que manejen datos.
        """
        return {}
    
    def set_data(self, data: Dict[str, Any]):
        """
        Establece los datos de la pestaña.
        Debe ser implementado en subclases que manejen datos.
        """
        pass
    
    def refresh(self):
        """
        Refresca los datos de la pestaña.
        Debe ser implementado en subclases que necesiten refrescar datos.
        """
        pass
    
    def clear(self):
        """
        Limpia los datos de la pestaña.
        Debe ser implementado en subclases que necesiten limpiar datos.
        """
        pass
    
    def validate(self) -> tuple[bool, str]:
        """
        Valida los datos actuales de la pestaña.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        return True, ""
    
    def emit_action(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Emite una acción solicitada."""
        if data is None:
            data = {}
        self.action_requested.emit(action, data)
    
    def emit_data_changed(self, data: Optional[Dict[str, Any]] = None):
        """Emite que los datos han cambiado."""
        if data is None:
            data = self.get_data()
        self.data_changed.emit(data)