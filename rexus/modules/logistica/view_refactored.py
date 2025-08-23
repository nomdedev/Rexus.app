# -*- coding: utf-8 -*-
"""
Vista Refactorizada de Logística - Rexus.app
Refactorización del archivo original view.py de 2207 líneas

Esta versión divide la funcionalidad en componentes especializados:
- TablaTransportesWidget: Gestión de tabla de transportes
- EstadisticasWidget: Métricas y estadísticas
- ServiciosWidget: Gestión de servicios
- MapaWidget: Visualización geográfica

Mejoras implementadas:
- Separación de responsabilidades
- Componentes reutilizables
- Mejor mantenibilidad
- Código más legible y testeable
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

# Imports de componentes refactorizados
from .components.base_logistica_widget import BaseLogisticaWidget
from .components.tabla_transportes_widget import TablaTransportesWidget
from .components.estadisticas_widget import EstadisticasWidget
from .components.servicios_widget import ServiciosWidget
from .components.mapa_widget import MapaWidget

# Imports originales conservados
from rexus.ui.standard_components import StandardComponents
from rexus.utils.export_manager import ModuleExportMixin
from rexus.modules.logistica.constants import LogisticaConstants
from rexus.modules.logistica.dialogo_transporte import DialogoNuevoTransporte

logger = logging.getLogger(__name__)


class LogisticaViewRefactored(QWidget, ModuleExportMixin):
    """Vista principal de logística refactorizada con componentes especializados."""
    
    # Señales principales
    transport_created = pyqtSignal(dict)
    transport_updated = pyqtSignal(dict)
    transport_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.current_data = {}
        self.widgets = {}
        
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()
    
    def setup_ui(self):
        """Configurar interfaz principal."""
        layout = QVBoxLayout(self)
        
        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Crear pestañas especializadas
        self.create_tabs()
        
        layout.addWidget(self.tab_widget)
        self.apply_styles()
    
    def create_tabs(self):
        """Crear pestañas especializadas."""
        
        # Pestaña Transportes
        self.transportes_widget = TablaTransportesWidget(self)
        self.tab_widget.addTab(self.transportes_widget, "🚛 Transportes")
        self.widgets['transportes'] = self.transportes_widget
        
        # Pestaña Estadísticas
        self.estadisticas_widget = EstadisticasWidget(self)
        self.tab_widget.addTab(self.estadisticas_widget, "📊 Estadísticas")
        self.widgets['estadisticas'] = self.estadisticas_widget
        
        # Pestaña Servicios
        self.servicios_widget = ServiciosWidget(self)
        self.tab_widget.addTab(self.servicios_widget, "🔧 Servicios")
        self.widgets['servicios'] = self.servicios_widget
        
        # Pestaña Mapa
        self.mapa_widget = MapaWidget(self)
        self.tab_widget.addTab(self.mapa_widget, "🗺️ Mapa")
        self.widgets['mapa'] = self.mapa_widget
    
    def create_placeholder(self, text: str) -> QWidget:
        """Crear placeholder para futuras implementaciones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        from PyQt6.QtWidgets import QLabel
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet()
        
        layout.addWidget(label)
        return widget
    
    def connect_signals(self):
        """Conectar señales entre componentes."""
        
        # Señales de transportes
        if hasattr(self, 'transportes_widget'):
            self.transportes_widget.transport_selected.connect(self.on_transport_selected)
            self.transportes_widget.transport_edited.connect(self.on_transport_edited)
            self.transportes_widget.transport_deleted.connect(self.on_transport_deleted)
            self.transportes_widget.error_occurred.connect(self.handle_error)
        
        # Señales de estadísticas
        if hasattr(self, 'estadisticas_widget'):
            self.estadisticas_widget.data_updated.connect(self.on_stats_updated)
            self.estadisticas_widget.error_occurred.connect(self.handle_error)
        
        # Señales de servicios
        if hasattr(self, 'servicios_widget'):
            self.servicios_widget.service_created.connect(self.on_service_created)
            self.servicios_widget.service_updated.connect(self.on_service_updated)
            self.servicios_widget.service_completed.connect(self.on_service_completed)
            self.servicios_widget.error_occurred.connect(self.handle_error)
        
        # Señales de mapas
        if hasattr(self, 'mapa_widget'):
            self.mapa_widget.location_selected.connect(self.on_location_selected)
            self.mapa_widget.route_calculated.connect(self.on_route_calculated)
            self.mapa_widget.error_occurred.connect(self.handle_error)
    
    def apply_styles(self):
        """Aplicar estilos personalizados."""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-top: 2px solid #4CAF50;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #f0f0f0, stop: 1 #e0e0e0);
                border: 1px solid #c0c0c0;
                padding: 8px 20px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
            }
        """)
    
    def load_initial_data(self):
        """Cargar datos iniciales."""
        try:
            if hasattr(self, 'transportes_widget'):
                self.transportes_widget.refresh_data()
            
            if hasattr(self, 'estadisticas_widget'):
                self.estadisticas_widget.refresh_data()
            
            # Cargar servicios
            if hasattr(self, 'servicios_widget'):
                self.servicios_widget.refresh_data()
            
            # Cargar mapas
            if hasattr(self, 'mapa_widget'):
                self.mapa_widget.refresh_data()
                
        except Exception as e:
    
    # Event handlers
    def on_transport_selected(self, transport_data: Dict[str, Any]):
        """Manejar selección de transporte."""
        logger.info(f"Transporte seleccionado: {transport_data.get('numero', 'N/A')}")
        self.current_data['selected_transport'] = transport_data
    
    def on_transport_edited(self, transport_data: Dict[str, Any]):
        """Manejar edición de transporte."""
        try:
            self.mostrar_dialogo_editar_transporte(transport_data)
        except Exception as e:
    
    def on_transport_deleted(self, transport_id: int):
        """Manejar eliminación de transporte."""
        try:
            if self.controller:
                success = self.controller.delete_transport(transport_id)
                if success:
                    self.transport_deleted.emit(transport_id)
                    QMessageBox.information(self, "Éxito", "Transporte eliminado")
            else:
                QMessageBox.information(self, "Simulación", f"Transporte {transport_id} eliminado")
                
        except Exception as e:
    
    def on_stats_updated(self):
        """Manejar actualización de estadísticas."""
        logger.info("Estadísticas actualizadas")
    
    def on_service_created(self, service_data: Dict[str, Any]):
        """Manejar creación de servicio."""
        logger.info(f"Servicio creado: {service_data.get('tipo', 'N/A')}")
        # Actualizar estadísticas si es necesario
        if hasattr(self, 'estadisticas_widget'):
            self.estadisticas_widget.refresh_data()
    
    def on_service_updated(self, service_data: Dict[str, Any]):
        """Manejar actualización de servicio."""
        logger.info(f"Servicio actualizado: {service_data.get('id', 'N/A')}")
    
    def on_service_completed(self, service_id: int):
        """Manejar finalización de servicio."""
        logger.info(f"Servicio completado: {service_id}")
        # Actualizar estadísticas y mapa
        if hasattr(self, 'estadisticas_widget'):
            self.estadisticas_widget.refresh_data()
        if hasattr(self, 'mapa_widget'):
            self.mapa_widget.refresh_data()
    
    def on_location_selected(self, lat: float, lon: float):
        """Manejar selección de ubicación en mapa."""
        logger.info(f"Ubicación seleccionada: {lat}, {lon}")
        self.current_data['selected_location'] = {'lat': lat, 'lon': lon}
    
    def on_route_calculated(self, route_data: Dict[str, Any]):
        """Manejar cálculo de ruta."""
        logger.info(f"Ruta calculada - Distancia: {route_data.get('distancia', 0)} km")
        self.current_data['current_route'] = route_data
    
    def handle_error(self, error_message: str):
        """Manejar errores de widgets hijos."""
            
    def mostrar_dialogo_editar_transporte(self, transport_data: Dict[str, Any]):
        """Mostrar diálogo para editar transporte.""" 
        try:
            dialogo = DialogoNuevoTransporte(self, transport_data)
            dialogo.setWindowTitle("Editar Transporte")
            
            if dialogo.exec() == dialogo.DialogCode.Accepted:
                updated_data = dialogo.get_transport_data()
                
                if self.controller:
                    success = self.controller.update_transport(updated_data)
                    if success:
                        self.transport_updated.emit(updated_data)
                        self.transportes_widget.update_transport(updated_data)
                        QMessageBox.information(self, "Éxito", "Transporte actualizado")
                else:
                    QMessageBox.information(self, "Simulación", "Transporte actualizado")
                    
        except Exception as e:
    
    def export_data(self, data, formato='excel'):
        """Método de compatibilidad para exportación."""
        try:
            if formato == 'excel':
                return self.export_to_excel(
                    data=data,
                    filename="logistica_export",
                    sheet_name="Datos"
                )
            return False
        except Exception as e:


# Alias para compatibilidad
LogisticaView = LogisticaViewRefactored