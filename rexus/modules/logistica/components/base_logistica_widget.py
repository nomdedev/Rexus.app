# -*- coding: utf-8 -*-
"""
Componente base para widgets de logística
Refactorización de view.py para mejor mantenibilidad
"""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from rexus.ui.components.base_components import RexusGroupBox

logger = logging.getLogger(__name__)


class BaseLogisticaWidget(QWidget):
    """Widget base para componentes de logística."""
    
    # Señales comunes
    data_updated = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.data = []
        self.setup_widget()
    
    def setup_widget(self):
        """Configuración inicial del widget."""
        self.setLayout(QVBoxLayout())
        self.create_ui()
        self.connect_signals()
    
    def create_ui(self):
        """Crear interfaz de usuario. Override en subclases."""
        pass
    
    def connect_signals(self):
        """Conectar señales. Override en subclases."""
        pass
    
    def refresh_data(self):
        """Actualizar datos. Override en subclases."""
        pass
    
    def export_data(self, formato='excel'):
        """Exportar datos del widget."""
        try:
            if not self.data:
                self.error_occurred.emit("No hay datos para exportar")
                return False
            
            # Delegar exportación al parent si está disponible
            if hasattr(self.parent_view, 'export_data'):
                return self.parent_view.export_data(self.data, formato)
            
            return True
            
        except Exception as e:
            return False
    
    def create_group_box(self, title: str, widget: QWidget) -> RexusGroupBox:
        """Crear un group box estándar."""
        group = RexusGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        group.setLayout(layout)
        return group