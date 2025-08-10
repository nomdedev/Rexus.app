"""
Pestaña de Entregas para el módulo de Logística

Maneja la interfaz y lógica específica de las entregas.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from .base_tab import BaseTab
from ..constants import ESTADOS_ENTREGA, TABLE_HEADERS, ICONS, UI_CONFIG
from ..widgets import (
    LogisticaButton, LogisticaTable, LogisticaGroupBox, 
    FilterPanel, FormBuilder
)


class TabEntregas(BaseTab):
    """Pestaña para gestión de entregas."""
    
    # Señales específicas de entregas
    entrega_seleccionada = pyqtSignal(dict)
    crear_entrega_solicitada = pyqtSignal(dict)
    actualizar_entrega_solicitada = pyqtSignal(dict)
    eliminar_entrega_solicitada = pyqtSignal(int)
    
    def __init__(self, parent=None):
        self.entregas_data = []
        self.selected_entrega = None
        super().__init__("Entregas", ICONS["tabs"]["entregas"], parent)
    
    def init_ui(self):
        """Inicializa la interfaz de la pestaña de entregas."""
        # Panel de filtros
        self.create_filters_panel()
        
        # Tabla de entregas
        self.create_table()
        
        # Panel de acciones
        self.create_actions_panel()
    
    def create_filters_panel(self):
        """Crea el panel de filtros."""
        filters_config = {
            "search": True,
            "estado": ESTADOS_ENTREGA
        }
        
        self.filter_panel = FilterPanel(filters_config, self)
        self.filter_panel.filter_changed.connect(self.on_filters_changed)
        
        # Envolver en GroupBox
        filters_group = LogisticaGroupBox("Filtros y Búsqueda", self)
        filters_group.add_widget(self.filter_panel)
        
        self.main_layout.addWidget(filters_group)
    
    def create_table(self):
        """Crea la tabla de entregas."""
        self.tabla_entregas = LogisticaTable(TABLE_HEADERS["entregas"], self)
        self.tabla_entregas.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.main_layout.addWidget(self.tabla_entregas)
    
    def create_actions_panel(self):
        """Crea el panel de acciones."""
        actions_layout = QHBoxLayout()
        
        # Botón nueva entrega
        self.btn_nueva_entrega = LogisticaButton(
            "Nueva Entrega", "success", ICONS["buttons"]["nueva_entrega"], self
        )
        self.btn_nueva_entrega.clicked.connect(self.on_nueva_entrega)
        actions_layout.addWidget(self.btn_nueva_entrega)
        
        # Botón editar (deshabilitado inicialmente)
        self.btn_editar_entrega = LogisticaButton(
            "Editar", "info", "✏️", self
        )
        self.btn_editar_entrega.setEnabled(False)
        self.btn_editar_entrega.clicked.connect(self.on_editar_entrega)
        actions_layout.addWidget(self.btn_editar_entrega)
        
        # Botón eliminar (deshabilitado inicialmente)
        self.btn_eliminar_entrega = LogisticaButton(
            "Eliminar", "danger", "🗑️", self
        )
        self.btn_eliminar_entrega.setEnabled(False)
        self.btn_eliminar_entrega.clicked.connect(self.on_eliminar_entrega)
        actions_layout.addWidget(self.btn_eliminar_entrega)
        
        # Separador
        actions_layout.addStretch()
        
        # Botón actualizar
        self.btn_actualizar = LogisticaButton(
            "Actualizar", "info", "🔄", self
        )
        self.btn_actualizar.clicked.connect(self.refresh)
        actions_layout.addWidget(self.btn_actualizar)
        
        # Botón exportar
        self.btn_exportar = LogisticaButton(
            "Exportar", "secondary", "📊", self
        )
        self.btn_exportar.clicked.connect(self.on_exportar)
        actions_layout.addWidget(self.btn_exportar)
        
        self.main_layout.addLayout(actions_layout)
    
    def connect_signals(self):
        """Conecta las señales específicas."""
        # Las señales ya están conectadas en create_actions_panel
        pass
    
    def on_filters_changed(self, filters: Dict[str, Any]):
        """Maneja cambios en los filtros."""
        self.apply_filters(filters)
    
    def on_selection_changed(self):
        """Maneja cambios en la selección de la tabla."""
        selected_items = self.tabla_entregas.selectedItems()
        
        if selected_items:
            # Obtener la fila seleccionada
            row = selected_items[0].row()
            if 0 <= row < len(self.entregas_data):
                self.selected_entrega = self.entregas_data[row]
                self.entrega_seleccionada.emit(self.selected_entrega)
                
                # Habilitar botones de acción
                self.btn_editar_entrega.setEnabled(True)
                self.btn_eliminar_entrega.setEnabled(True)
            else:
                self.selected_entrega = None
                self.btn_editar_entrega.setEnabled(False)
                self.btn_eliminar_entrega.setEnabled(False)
        else:
            self.selected_entrega = None
            self.btn_editar_entrega.setEnabled(False)
            self.btn_eliminar_entrega.setEnabled(False)
    
    def on_nueva_entrega(self):
        """Maneja la creación de nueva entrega."""
        self.emit_action("mostrar_dialogo_nueva_entrega")
    
    def on_editar_entrega(self):
        """Maneja la edición de entrega."""
        if self.selected_entrega:
            self.emit_action("mostrar_dialogo_editar_entrega", self.selected_entrega)
    
    def on_eliminar_entrega(self):
        """Maneja la eliminación de entrega."""
        if self.selected_entrega:
            entrega_id = self.selected_entrega.get("id")
            direccion = self.selected_entrega.get("direccion", "N/A")
            
            if self.ask_confirmation(
                f"¿Está seguro de eliminar la entrega a '{direccion}'?",
                "Confirmar eliminación"
            ):
                self.eliminar_entrega_solicitada.emit(entrega_id)
    
    def on_exportar(self):
        """Maneja la exportación de datos."""
        self.emit_action("exportar_entregas", {"data": self.entregas_data})
    
    def apply_filters(self, filters: Dict[str, Any]):
        """Aplica los filtros a los datos mostrados."""
        if not hasattr(self, 'original_entregas_data'):
            self.original_entregas_data = self.entregas_data.copy()
        
        filtered_data = self.original_entregas_data
        
        # Filtro por texto de búsqueda
        search_text = filters.get("search", "").lower()
        if search_text:
            filtered_data = [
                entrega for entrega in filtered_data
                if any(search_text in str(value).lower() 
                      for value in entrega.values())
            ]
        
        # Filtro por estado
        estado_filter = filters.get("estado", "Todos")
        if estado_filter != "Todos":
            filtered_data = [
                entrega for entrega in filtered_data
                if entrega.get("estado", "") == estado_filter
            ]
        
        # Actualizar tabla con datos filtrados
        self.update_table_data(filtered_data)
    
    def update_table_data(self, data: List[Dict[str, Any]]):
        """Actualiza los datos de la tabla."""
        self.entregas_data = data
        self.tabla_entregas.setRowCount(len(data))
        
        for row, entrega in enumerate(data):
            # Llenar las celdas de la tabla
            self.tabla_entregas.setItem(row, 0, self.create_table_item(str(entrega.get("id", ""))))
            self.tabla_entregas.setItem(row, 1, self.create_table_item(str(entrega.get("fecha_programada", ""))))
            self.tabla_entregas.setItem(row, 2, self.create_table_item(str(entrega.get("direccion", ""))))
            self.tabla_entregas.setItem(row, 3, self.create_table_item(str(entrega.get("estado", ""))))
            self.tabla_entregas.setItem(row, 4, self.create_table_item(str(entrega.get("contacto", ""))))
            self.tabla_entregas.setItem(row, 5, self.create_table_item(str(entrega.get("observaciones", ""))))
            
            # Columna de acciones (por ahora solo texto)
            self.tabla_entregas.setItem(row, 6, self.create_table_item("Acciones"))
    
    def create_table_item(self, text: str):
        """Crea un item de tabla con el texto especificado."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Solo lectura
        return item
    
    def cargar_entregas_en_tabla(self, entregas: List[Dict[str, Any]]):
        """Carga las entregas en la tabla (método público para compatibilidad)."""
        self.original_entregas_data = entregas.copy()
        self.update_table_data(entregas)
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna los datos actuales de entregas."""
        return {
            "entregas": self.entregas_data,
            "selected": self.selected_entrega,
            "filters": self.filter_panel.get_filters() if hasattr(self, 'filter_panel') else {}
        }
    
    def refresh(self):
        """Refresca los datos de entregas."""
        self.emit_action("cargar_entregas")
        self.show_success("Datos actualizados correctamente")
    
    def clear(self):
        """Limpia la selección y datos."""
        self.tabla_entregas.clearSelection()
        self.selected_entrega = None
        self.btn_editar_entrega.setEnabled(False)
        self.btn_eliminar_entrega.setEnabled(False)