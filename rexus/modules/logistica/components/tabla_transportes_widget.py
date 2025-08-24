# -*- coding: utf-8 -*-
"""
Widget especializado para la tabla de transportes
Refactorizado de LogisticaView
"""

import logging
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .base_logistica_widget import BaseLogisticaWidget
from rexus.ui.components.base_components import RexusButton, RexusLineEdit
from rexus.utils.export_manager import ModuleExportMixin

logger = logging.getLogger(__name__)


class TablaTransportesWidget(BaseLogisticaWidget, ModuleExportMixin):
    """Widget para gestionar tabla de transportes."""
    
    # Señales específicas
    transport_selected = pyqtSignal(dict)
    transport_edited = pyqtSignal(dict)
    transport_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selection = None
        
    def create_ui(self):
        """Crear interfaz de la tabla de transportes."""
        layout = QVBoxLayout(self)
        
        # Panel de búsqueda
        search_layout = QHBoxLayout()
        
        self.search_input = RexusLineEdit()
        self.search_input.setPlaceholderText("Buscar transportes...")
        
        self.btn_search = RexusButton("Buscar")
        self.btn_refresh = RexusButton("Actualizar")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(search_layout)
        
        # Tabla de transportes
        self.tabla_transportes = QTableWidget()
        self.configurar_tabla()
        layout.addWidget(self.tabla_transportes)
        
        # Panel de acciones
        actions_layout = QHBoxLayout()
        
        self.btn_new = RexusButton("Nuevo Transporte")
        self.btn_edit = RexusButton("Editar")
        self.btn_delete = RexusButton("Eliminar")
        self.btn_export = RexusButton("Exportar")
        
        # Estado inicial de botones
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        
        actions_layout.addWidget(self.btn_new)
        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_delete)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_export)
        
        layout.addLayout(actions_layout)
        
    def connect_signals(self):
        """Conectar señales del widget."""
        self.search_input.returnPressed.connect(self.buscar_transportes)
        self.btn_search.clicked.connect(self.buscar_transportes)
        self.btn_refresh.clicked.connect(self.refresh_data)
        
        self.btn_new.clicked.connect(self.nuevo_transporte)
        self.btn_edit.clicked.connect(self.editar_transporte)
        self.btn_delete.clicked.connect(self.eliminar_transporte)
        self.btn_export.clicked.connect(self.exportar_datos)
        
        self.tabla_transportes.itemSelectionChanged.connect(self.on_selection_changed)
        self.tabla_transportes.itemDoubleClicked.connect(self.editar_transporte)
    
    def configurar_tabla(self):
        """Configurar tabla de transportes."""
        columnas = [
            "ID", "Número", "Estado", "Origen", "Destino", 
            "Conductor", "Vehículo", "Fecha Salida", "Observaciones"
        ]
        
        self.tabla_transportes.setColumnCount(len(columnas))
        self.tabla_transportes.setHorizontalHeaderLabels(columnas)
        
        # Configurar encabezados
        header = self.tabla_transportes.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Alternating row colors
        self.tabla_transportes.setAlternatingRowColors(True)
        self.tabla_transportes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
    def refresh_data(self):
        """Actualizar datos de transportes."""
        try:
            # Si hay parent, solicitar datos
            if hasattr(self.parent_view, 'controller'):
                transportes = self.parent_view.controller.get_transportes()
                self.cargar_transportes(transportes)
            else:
                # Datos de ejemplo para testing
                self.cargar_datos_ejemplo()
                
        except Exception as e:
            logger.error(f"Error configurando tabla transportes: {e}")
    
    def cargar_transportes(self, transportes: List[Dict[str, Any]]):
        """Cargar transportes en la tabla."""
        self.data = transportes
        self.tabla_transportes.setRowCount(len(transportes))
        
        for row, transporte in enumerate(transportes):
            items = [
                str(transporte.get('id', '')),
                str(transporte.get('numero', '')),
                str(transporte.get('estado', '')),
                str(transporte.get('origen', '')),
                str(transporte.get('destino', '')),
                str(transporte.get('conductor', '')),
                str(transporte.get('vehiculo', '')),
                str(transporte.get('fecha_salida', '')),
                str(transporte.get('observaciones', ''))
            ]
            
            for col, item in enumerate(items):
                table_item = QTableWidgetItem(item)
                if col == 0:  # ID column
                    table_item.setData(Qt.ItemDataRole.UserRole, transporte)
                self.tabla_transportes.setItem(row, col, table_item)
        
        self.data_updated.emit()
    
    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo."""
        datos_ejemplo = [
            {
                'id': 1, 'numero': 'T-001', 'estado': 'En tránsito',
                'origen': 'Almacén Central', 'destino': 'Obra Norte',
                'conductor': 'Juan Pérez', 'vehiculo': 'Camión A-123',
                'fecha_salida': '2025-08-23', 'observaciones': 'Entrega urgente'
            },
            {
                'id': 2, 'numero': 'T-002', 'estado': 'Programado',
                'origen': 'Proveedor ABC', 'destino': 'Almacén Central',
                'conductor': 'María García', 'vehiculo': 'Camión B-456',
                'fecha_salida': '2025-08-24', 'observaciones': 'Materiales especiales'
            },
            {
                'id': 3, 'numero': 'T-003', 'estado': 'Completado',
                'origen': 'Almacén Sur', 'destino': 'Obra Este',
                'conductor': 'Carlos López', 'vehiculo': 'Van C-789',
                'fecha_salida': '2025-08-22', 'observaciones': 'Entrega exitosa'
            }
        ]
        
        self.cargar_transportes(datos_ejemplo)
    
    def buscar_transportes(self):
        """Buscar transportes por filtro."""
        filtro = self.search_input.text().strip()
        
        if not filtro:
            self.refresh_data()
            return
        
        # Filtrar datos actuales
        transportes_filtrados = []
        for transporte in self.data:
            if (filtro.lower() in str(transporte.get('numero', '')).lower() or
                filtro.lower() in str(transporte.get('conductor', '')).lower() or
                filtro.lower() in str(transporte.get('estado', '')).lower()):
                transportes_filtrados.append(transporte)
        
        self.cargar_transportes(transportes_filtrados)
    
    def on_selection_changed(self):
        """Manejar cambio de selección."""
        current_row = self.tabla_transportes.currentRow()
        
        if current_row >= 0:
            # Obtener datos del transporte seleccionado
            id_item = self.tabla_transportes.item(current_row, 0)
            if id_item:
                self.current_selection = id_item.data(Qt.ItemDataRole.UserRole)
                self.btn_edit.setEnabled(True)
                self.btn_delete.setEnabled(True)
                self.transport_selected.emit(self.current_selection)
        else:
            self.current_selection = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
    
    def nuevo_transporte(self):
        """Crear nuevo transporte."""
        if hasattr(self.parent_view, 'mostrar_dialogo_nuevo_transporte'):
            self.parent_view.mostrar_dialogo_nuevo_transporte()
        else:
            # Placeholder para desarrollo
            QMessageBox.information(self, "Nuevo Transporte", "Funcionalidad en desarrollo")
    
    def editar_transporte(self):
        """Editar transporte seleccionado."""
        if not self.current_selection:
            QMessageBox.warning(self, "Selección", "Seleccione un transporte para editar")
            return
        
        # Emitir señal para edición
        self.transport_edited.emit(self.current_selection)
    
    def eliminar_transporte(self):
        """Eliminar transporte seleccionado."""
        if not self.current_selection:
            QMessageBox.warning(self, "Selección", "Seleccione un transporte para eliminar")
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar el transporte {self.current_selection.get('numero', '')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            transporte_id = self.current_selection.get('id')
            self.transport_deleted.emit(transporte_id)
            
            # Actualizar tabla
            self.refresh_data()
    
    def exportar_datos(self):
        """Exportar datos de transportes."""
        if not self.data:
            QMessageBox.warning(self, "Exportar", "No hay datos para exportar")
            return
        
        try:
            # Preparar datos para exportación
            export_data = []
            for transporte in self.data:
                export_data.append({
                    'Número': transporte.get('numero', ''),
                    'Estado': transporte.get('estado', ''),
                    'Origen': transporte.get('origen', ''),
                    'Destino': transporte.get('destino', ''),
                    'Conductor': transporte.get('conductor', ''),
                    'Vehículo': transporte.get('vehiculo', ''),
                    'Fecha Salida': transporte.get('fecha_salida', ''),
                    'Observaciones': transporte.get('observaciones', '')
                })
            
            # Usar funcionalidad de exportación heredada
            success = self.export_to_excel(
                data=export_data,
                filename="transportes_logistica",
                sheet_name="Transportes"
            )
            
            if success:
                QMessageBox.information(self, "Exportar", "Datos exportados exitosamente")
            else:
                QMessageBox.warning(self, "Exportar", "Error al exportar datos")
                
        except Exception as e:
            logger.error(f"Error al exportar datos de transportes: {e}")
    
    def get_selected_transport(self) -> Dict[str, Any]:
        """Obtener transporte seleccionado."""
        return self.current_selection or {}
    
    def update_transport(self, transport_data: Dict[str, Any]):
        """Actualizar un transporte en la tabla."""
        transport_id = transport_data.get('id')
        
        for i, transporte in enumerate(self.data):
            if transporte.get('id') == transport_id:
                self.data[i] = transport_data
                break
        
        # Recargar tabla
        self.cargar_transportes(self.data)