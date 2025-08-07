"""
Base Module View Template - Rexus.app v2.0.0

Template base para vistas de módulos con componentes UI unificados.
Proporciona estructura estándar y patrones de diseño consistentes.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QStackedWidget, QScrollArea
)

from rexus.ui.components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox,
    RexusTable, RexusGroupBox, RexusFrame, RexusProgressBar,
    RexusMessageBox, RexusLayoutHelper, RexusColors
)


class BaseModuleView(QWidget):
    """
    Vista base para todos los módulos de Rexus.app.
    
    Proporciona estructura estándar y componentes unificados
    para mantener consistencia en toda la aplicación.
    """
    
    # Señales estándar que todos los módulos pueden usar
    item_selected = pyqtSignal(int)  # ID del item seleccionado
    item_created = pyqtSignal(dict)  # Datos del item creado
    item_updated = pyqtSignal(int, dict)  # ID y datos actualizados
    item_deleted = pyqtSignal(int)  # ID del item eliminado
    search_requested = pyqtSignal(str)  # Término de búsqueda
    filter_changed = pyqtSignal(dict)  # Filtros aplicados
    
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.current_data = []
        self.selected_id = None
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
    
    def setup_ui(self):
        """Configura la interfaz usuario estándar"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header del módulo
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Área principal con splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Lista/Tabla
        left_panel = self.create_list_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho - Detalles/Formulario
        right_panel = self.create_detail_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 2)  # Lista ocupa 2/3
        splitter.setStretchFactor(1, 1)  # Detalles ocupa 1/3
        
        main_layout.addWidget(splitter, 1)
        
        # Footer con información/progreso
        footer_widget = self.create_footer()
        main_layout.addWidget(footer_widget)
    
    def create_header(self) -> QWidget:
        """Crea el header estándar del módulo"""
        header_frame = RexusFrame("card")
        layout = QHBoxLayout(header_frame)
        
        # Título del módulo
        title = RexusLabel(f"Gestión de {self.module_name}", "title")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Controles del header
        header_controls = self.create_header_controls()
        layout.addLayout(header_controls)
        
        return header_frame
    
    def create_header_controls(self) -> QHBoxLayout:
        """Crea los controles del header (búsqueda, filtros, acciones)"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Campo de búsqueda
        self.search_input = RexusLineEdit(f"Buscar {self.module_name.lower()}...")
        self.search_input.setMaximumWidth(250)
        controls_layout.addWidget(self.search_input)
        
        # Botón de búsqueda
        self.search_btn = RexusButton("Buscar", "secondary")
        controls_layout.addWidget(self.search_btn)
        
        # Separador
        separator = RexusFrame("separator")
        separator.setMaximumHeight(20)
        controls_layout.addWidget(separator)
        
        # Botón nuevo
        self.new_btn = RexusButton("Nuevo", "primary")
        controls_layout.addWidget(self.new_btn)
        
        # Botón actualizar
        self.refresh_btn = RexusButton("Actualizar", "secondary")
        controls_layout.addWidget(self.refresh_btn)
        
        return controls_layout
    
    def create_list_panel(self) -> QWidget:
        """Crea el panel de lista/tabla"""
        panel_frame = RexusFrame("card")
        layout = QVBoxLayout(panel_frame)
        
        # Título de la sección
        list_title = RexusLabel(f"Lista de {self.module_name}", "subtitle")
        layout.addWidget(list_title)
        
        # Área de filtros (opcional)
        filters_widget = self.create_filters_section()
        if filters_widget:
            layout.addWidget(filters_widget)
        
        # Tabla principal
        self.main_table = RexusTable(0, 4)  # Se configurará en setup_table
        self.setup_table()
        layout.addWidget(self.main_table, 1)
        
        # Controles de tabla
        table_controls = self.create_table_controls()
        layout.addLayout(table_controls)
        
        return panel_frame
    
    def create_filters_section(self) -> Optional[QWidget]:
        """
        Crea sección de filtros. 
        Override en clases hijas para personalizar.
        """
        # Por defecto, sin filtros adicionales
        # Las clases hijas pueden override este método
        return None
    
    def setup_table(self):
        """
        Configura la tabla principal.
        Debe ser implementado por las clases hijas.
        """
        # Configuración básica - override en clases hijas
        headers = ["ID", "Nombre", "Estado", "Acciones"]
        self.main_table.setColumnCount(len(headers))
        self.main_table.setHorizontalHeaderLabels(headers)
    
    def create_table_controls(self) -> QHBoxLayout:
        """Crea controles para la tabla (paginación, etc.)"""
        controls_layout = QHBoxLayout()
        
        # Información de registros
        self.record_info = RexusLabel("0 registros", "caption")
        controls_layout.addWidget(self.record_info)
        
        controls_layout.addStretch()
        
        # Controles de paginación
        self.prev_btn = RexusButton("Anterior", "secondary")
        self.prev_btn.setEnabled(False)
        controls_layout.addWidget(self.prev_btn)
        
        self.next_btn = RexusButton("Siguiente", "secondary")  
        self.next_btn.setEnabled(False)
        controls_layout.addWidget(self.next_btn)
        
        return controls_layout
    
    def create_detail_panel(self) -> QWidget:
        """Crea el panel de detalles/formulario"""
        panel_frame = RexusFrame("card")
        layout = QVBoxLayout(panel_frame)
        
        # Stack widget para alternar entre vista y edición
        self.detail_stack = QStackedWidget()
        
        # Vista de detalles (solo lectura)
        detail_view = self.create_detail_view()
        self.detail_stack.addWidget(detail_view)
        
        # Vista de edición/creación
        edit_view = self.create_edit_view()
        self.detail_stack.addWidget(edit_view)
        
        layout.addWidget(self.detail_stack, 1)
        
        # Controles del panel
        panel_controls = self.create_detail_controls()
        layout.addLayout(panel_controls)
        
        return panel_frame
    
    def create_detail_view(self) -> QWidget:
        """
        Crea la vista de detalles (solo lectura).
        Override en clases hijas para personalizar.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        self.detail_title = RexusLabel("Selecciona un elemento", "subtitle")
        layout.addWidget(self.detail_title)
        
        # Área de scroll para detalles
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget interno con detalles
        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)
        self.setup_detail_fields()
        
        scroll_area.setWidget(self.detail_content)
        layout.addWidget(scroll_area, 1)
        
        return widget
    
    def create_edit_view(self) -> QWidget:
        """
        Crea la vista de edición/creación.
        Override en clases hijas para personalizar.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        self.edit_title = RexusLabel("Editar elemento", "subtitle")
        layout.addWidget(self.edit_title)
        
        # Área de scroll para formulario
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget interno con formulario
        self.edit_content = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_content)
        self.setup_edit_form()
        
        scroll_area.setWidget(self.edit_content)
        layout.addWidget(scroll_area, 1)
        
        return widget
    
    def setup_detail_fields(self):
        """
        Configura los campos de la vista de detalles.
        Debe ser implementado por las clases hijas.
        """
        # Implementación básica
        info_label = RexusLabel("Sin elemento seleccionado", "body")
        self.detail_layout.addWidget(info_label)
    
    def setup_edit_form(self):
        """
        Configura el formulario de edición.
        Debe ser implementado por las clases hijas.
        """
        # Implementación básica
        info_label = RexusLabel("Formulario no configurado", "body")
        self.edit_layout.addWidget(info_label)
    
    def create_detail_controls(self) -> QHBoxLayout:
        """Crea controles del panel de detalles"""
        controls_layout = QHBoxLayout()
        
        # Botones de acción
        self.edit_btn = RexusButton("Editar", "secondary")
        self.edit_btn.setEnabled(False)
        controls_layout.addWidget(self.edit_btn)
        
        self.delete_btn = RexusButton("Eliminar", "error")
        self.delete_btn.setEnabled(False)
        controls_layout.addWidget(self.delete_btn)
        
        controls_layout.addStretch()
        
        # Botones de formulario (ocultos inicialmente)
        self.cancel_btn = RexusButton("Cancelar", "secondary")
        self.cancel_btn.setVisible(False)
        controls_layout.addWidget(self.cancel_btn)
        
        self.save_btn = RexusButton("Guardar", "primary")
        self.save_btn.setVisible(False)
        controls_layout.addWidget(self.save_btn)
        
        return controls_layout
    
    def create_footer(self) -> QWidget:
        """Crea el footer con información de estado"""
        footer_frame = RexusFrame("default")
        layout = QHBoxLayout(footer_frame)
        
        # Estado de la aplicación
        self.status_label = RexusLabel("Listo", "caption")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Barra de progreso (oculta por defecto)
        self.progress_bar = RexusProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)
        
        return footer_frame
    
    def setup_connections(self):
        """Configura las conexiones de señales estándar"""
        # Búsqueda
        self.search_btn.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Acciones principales
        self.new_btn.clicked.connect(self.create_new_item)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Tabla
        self.main_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Controles de detalle
        self.edit_btn.clicked.connect(self.enter_edit_mode)
        self.delete_btn.clicked.connect(self.delete_item)
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.save_btn.clicked.connect(self.save_item)
        
        # Paginación
        self.prev_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)
    
    def apply_styles(self):
        """Aplica estilos específicos del módulo"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {RexusColors.BACKGROUND};
            }}
        """)
    
    # Métodos de interfaz que pueden ser override por las clases hijas
    
    def perform_search(self):
        """Ejecuta búsqueda"""
        search_term = self.search_input.text().strip()
        if search_term:
            self.search_requested.emit(search_term)
            self.set_status(f"Buscando '{search_term}'...")
    
    def create_new_item(self):
        """Inicia creación de nuevo elemento"""
        self.selected_id = None
        self.edit_title.setText(f"Nuevo {self.module_name}")
        self.clear_edit_form()
        self.enter_edit_mode()
    
    def refresh_data(self):
        """Actualiza los datos"""
        self.set_status("Actualizando datos...")
        # Las clases hijas implementarán la lógica específica
    
    def on_selection_changed(self):
        """Maneja cambio de selección en la tabla"""
        selected_items = self.main_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            item_id = int(self.main_table.item(row, 0).text())
            self.selected_id = item_id
            self.item_selected.emit(item_id)
            self.enable_detail_controls(True)
        else:
            self.selected_id = None
            self.enable_detail_controls(False)
    
    def enter_edit_mode(self):
        """Entra en modo edición"""
        self.detail_stack.setCurrentIndex(1)  # Vista de edición
        self.toggle_edit_controls(True)
    
    def cancel_edit(self):
        """Cancela la edición"""
        self.detail_stack.setCurrentIndex(0)  # Vista de detalles
        self.toggle_edit_controls(False)
        self.clear_edit_form()
    
    def save_item(self):
        """Guarda el elemento"""
        data = self.get_form_data()
        if self.validate_form_data(data):
            if self.selected_id:
                # Actualizar existente
                self.item_updated.emit(self.selected_id, data)
            else:
                # Crear nuevo
                self.item_created.emit(data)
            self.cancel_edit()
        
    def delete_item(self):
        """Elimina el elemento seleccionado"""
        if self.selected_id:
            result = RexusMessageBox.question(
                self, 
                "Confirmar eliminación",
                f"¿Está seguro de eliminar este {self.module_name.lower()}?"
            )
            if result == RexusMessageBox.StandardButton.Yes:
                self.item_deleted.emit(self.selected_id)
    
    def previous_page(self):
        """Página anterior"""
        # Implementar paginación
        pass
    
    def next_page(self):
        """Página siguiente"""
        # Implementar paginación
        pass
    
    # Métodos utilitarios
    
    def set_status(self, message: str, show_progress: bool = False):
        """Actualiza el estado en el footer"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(show_progress)
    
    def enable_detail_controls(self, enabled: bool):
        """Habilita/deshabilita controles de detalle"""
        self.edit_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
    
    def toggle_edit_controls(self, edit_mode: bool):
        """Alterna entre modo vista y edición"""
        # Ocultar botones de vista
        self.edit_btn.setVisible(not edit_mode)
        self.delete_btn.setVisible(not edit_mode)
        
        # Mostrar botones de edición
        self.cancel_btn.setVisible(edit_mode)
        self.save_btn.setVisible(edit_mode)
    
    def update_record_info(self, total_records: int, current_page: int = 1):
        """Actualiza información de registros"""
        self.record_info.setText(f"{total_records} registros")
    
    # Métodos abstractos que deben implementar las clases hijas
    
    def get_form_data(self) -> Dict[str, Any]:
        """
        Obtiene datos del formulario de edición.
        Debe ser implementado por las clases hijas.
        """
        return {}
    
    def validate_form_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos del formulario.
        Debe ser implementado por las clases hijas.
        """
        return True
    
    def clear_edit_form(self):
        """
        Limpia el formulario de edición.
        Debe ser implementado por las clases hijas.
        """
        pass
    
    def populate_form(self, data: Dict[str, Any]):
        """
        Puebla el formulario con datos.
        Debe ser implementado por las clases hijas.
        """
        pass
    
    def populate_detail_view(self, data: Dict[str, Any]):
        """
        Puebla la vista de detalles con datos.
        Debe ser implementado por las clases hijas.
        """
        pass