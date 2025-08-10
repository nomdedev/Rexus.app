"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Vista Completa de Herrajes - Rexus.app v2.0.0

Interfaz completa para gestión de herrajes con asignación a obras y exportación
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QTextEdit, QFrame, QHeaderView,
    QAbstractItemView, QMenu, QApplication, QScrollArea, QGridLayout,
    QFileDialog, QProgressBar, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap

from rexus.core.database import InventarioDatabaseConnection
from rexus.modules.herrajes.model import HerrajesModel
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class ExportDialog(QDialog):
    """Diálogo para exportar herrajes a PDF o Excel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar Herrajes")
        self.setFixedSize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Exportar Herrajes por Obra")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Selección de obra
        self.obra_combo = QComboBox()
        self.obra_combo.addItems(["Obra 1 - Residencial Norte", "Obra 2 - Edificio Central", "Obra 3 - Plaza Comercial"])
        form_layout.addRow("Obra:", self.obra_combo)
        
        # Formato de exportación
        self.formato_combo = QComboBox()
        self.formato_combo.addItems(["PDF", "Excel"])
        form_layout.addRow("Formato:", self.formato_combo)
        
        # Incluir precios
        self.incluir_precios_check = QCheckBox("Incluir precios")
        self.incluir_precios_check.setChecked(True)
        form_layout.addRow("Opciones:", self.incluir_precios_check)
        
        # Incluir stock
        self.incluir_stock_check = QCheckBox("Incluir stock actual")
        self.incluir_stock_check.setChecked(True)
        form_layout.addRow("", self.incluir_stock_check)
        
        # Observaciones
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setPlaceholderText("Observaciones adicionales para el reporte...")
        self.observaciones_text.setMaximumHeight(80)
        form_layout.addRow("Observaciones:", self.observaciones_text)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_export_data(self):
        return {
            'obra': self.obra_combo.currentText(),
            'formato': self.formato_combo.currentText(),
            'incluir_precios': self.incluir_precios_check.isChecked(),
            'incluir_stock': self.incluir_stock_check.isChecked(),
            'observaciones': self.observaciones_text.toPlainText()
        }


class HerrajeDialog(QDialog):
    """Diálogo para crear/editar herrajes"""
    
    def __init__(self, parent=None, herraje_data=None):
        super().__init__(parent)
        self.herraje_data = herraje_data
        self.setWindowTitle("Nuevo Herraje" if not herraje_data else "Editar Herraje")
        self.setFixedSize(600, 700)
        self.init_ui()
        
        if herraje_data:
            self.load_herraje_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Nuevo Herraje" if not self.herraje_data else "Editar Herraje")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Datos básicos
        basic_group = QGroupBox("Datos Básicos")
        basic_layout = QFormLayout(basic_group)
        
        self.codigo_edit = QLineEdit()
        self.codigo_edit.setPlaceholderText("Código único del herraje")
        basic_layout.addRow("Código*:", self.codigo_edit)
        
        self.descripcion_edit = QLineEdit()
        self.descripcion_edit.setPlaceholderText("Descripción detallada")
        basic_layout.addRow("Descripción*:", self.descripcion_edit)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["BISAGRA", "CERRADURA", "MANIJA", "TORNILLO", "RIEL", "SOPORTE", "OTRO"])
        basic_layout.addRow("Tipo:", self.tipo_combo)
        
        self.categoria_edit = QLineEdit()
        self.categoria_edit.setPlaceholderText("Categoría del herraje")
        basic_layout.addRow("Categoría:", self.categoria_edit)
        
        scroll_layout.addWidget(basic_group)
        
        # Proveedor y precios
        price_group = QGroupBox("Proveedor y Precios")
        price_layout = QFormLayout(price_group)
        
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setEditable(True)
        self.proveedor_combo.addItems(["Herrajes SA", "Seguridad Total", "Ferretería Central", "Proveedor A", "Proveedor B"])
        price_layout.addRow("Proveedor*:", self.proveedor_combo)
        
        self.precio_spin = QDoubleSpinBox()
        self.precio_spin.setRange(0.01, 99999.99)
        self.precio_spin.setDecimals(2)
        self.precio_spin.setSuffix(" $")
        price_layout.addRow("Precio Unitario:", self.precio_spin)
        
        self.unidad_combo = QComboBox()
        self.unidad_combo.addItems(["UNIDAD", "PAR", "JUEGO", "METRO", "KILOGRAMO"])
        price_layout.addRow("Unidad de Medida:", self.unidad_combo)
        
        scroll_layout.addWidget(price_group)
        
        # Inventario
        inventory_group = QGroupBox("Inventario")
        inventory_layout = QFormLayout(inventory_group)
        
        self.stock_actual_spin = QSpinBox()
        self.stock_actual_spin.setRange(0, 99999)
        inventory_layout.addRow("Stock Actual:", self.stock_actual_spin)
        
        self.stock_minimo_spin = QSpinBox()
        self.stock_minimo_spin.setRange(0, 99999)
        inventory_layout.addRow("Stock Mínimo:", self.stock_minimo_spin)
        
        self.ubicacion_edit = QLineEdit()
        self.ubicacion_edit.setPlaceholderText("Ubicación en almacén")
        inventory_layout.addRow("Ubicación:", self.ubicacion_edit)
        
        scroll_layout.addWidget(inventory_group)
        
        # Especificaciones técnicas
        spec_group = QGroupBox("Especificaciones Técnicas")
        spec_layout = QFormLayout(spec_group)
        
        self.marca_edit = QLineEdit()
        self.marca_edit.setPlaceholderText("Marca del herraje")
        spec_layout.addRow("Marca:", self.marca_edit)
        
        self.modelo_edit = QLineEdit()
        self.modelo_edit.setPlaceholderText("Modelo del herraje")
        spec_layout.addRow("Modelo:", self.modelo_edit)
        
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("Color del herraje")
        spec_layout.addRow("Color:", self.color_edit)
        
        self.material_edit = QLineEdit()
        self.material_edit.setPlaceholderText("Material del herraje")
        spec_layout.addRow("Material:", self.material_edit)
        
        self.dimensiones_edit = QLineEdit()
        self.dimensiones_edit.setPlaceholderText("Dimensiones (ej: 10x8x2 cm)")
        spec_layout.addRow("Dimensiones:", self.dimensiones_edit)
        
        self.peso_spin = QDoubleSpinBox()
        self.peso_spin.setRange(0.001, 999.999)
        self.peso_spin.setDecimals(3)
        self.peso_spin.setSuffix(" kg")
        spec_layout.addRow("Peso:", self.peso_spin)
        
        scroll_layout.addWidget(spec_group)
        
        # Observaciones
        obs_group = QGroupBox("Observaciones y Notas")
        obs_layout = QVBoxLayout(obs_group)
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setPlaceholderText("Observaciones generales del herraje...")
        self.observaciones_text.setMaximumHeight(60)
        obs_layout.addWidget(self.observaciones_text)
        
        self.especificaciones_text = QTextEdit()
        self.especificaciones_text.setPlaceholderText("Especificaciones técnicas detalladas...")
        self.especificaciones_text.setMaximumHeight(60)
        obs_layout.addWidget(QLabel("Especificaciones:"))
        obs_layout.addWidget(self.especificaciones_text)
        
        scroll_layout.addWidget(obs_group)
        
        # Estado
        state_group = QGroupBox("Estado")
        state_layout = QFormLayout(state_group)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["ACTIVO", "INACTIVO", "DESCONTINUADO"])
        state_layout.addRow("Estado:", self.estado_combo)
        
        scroll_layout.addWidget(state_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_herraje_data(self):
        """Carga los datos del herraje en el formulario"""
        if not self.herraje_data:
            return
        
        self.codigo_edit.setText(self.herraje_data.get('codigo', ''))
        self.descripcion_edit.setText(self.herraje_data.get('descripcion', ''))
        
        tipo_index = self.tipo_combo.findText(self.herraje_data.get('tipo', 'OTRO'))
        if tipo_index >= 0:
            self.tipo_combo.setCurrentIndex(tipo_index)
        
        self.categoria_edit.setText(self.herraje_data.get('categoria', ''))
        self.proveedor_combo.setCurrentText(self.herraje_data.get('proveedor', ''))
        self.precio_spin.setValue(self.herraje_data.get('precio_unitario', 0.0))
        
        unidad_index = self.unidad_combo.findText(self.herraje_data.get('unidad_medida', 'UNIDAD'))
        if unidad_index >= 0:
            self.unidad_combo.setCurrentIndex(unidad_index)
        
        self.stock_actual_spin.setValue(self.herraje_data.get('stock_actual', 0))
        self.stock_minimo_spin.setValue(self.herraje_data.get('stock_minimo', 0))
        self.ubicacion_edit.setText(self.herraje_data.get('ubicacion', ''))
        
        self.marca_edit.setText(self.herraje_data.get('marca', ''))
        self.modelo_edit.setText(self.herraje_data.get('modelo', ''))
        self.color_edit.setText(self.herraje_data.get('color', ''))
        self.material_edit.setText(self.herraje_data.get('material', ''))
        self.dimensiones_edit.setText(self.herraje_data.get('dimensiones', ''))
        self.peso_spin.setValue(self.herraje_data.get('peso', 0.0))
        
        self.observaciones_text.setText(self.herraje_data.get('observaciones', ''))
        self.especificaciones_text.setText(self.herraje_data.get('especificaciones', ''))
        
        estado_index = self.estado_combo.findText(self.herraje_data.get('estado', 'ACTIVO'))
        if estado_index >= 0:
            self.estado_combo.setCurrentIndex(estado_index)
    
    def get_herraje_data(self):
        """Obtiene los datos del formulario"""
        return {
            'codigo': self.codigo_edit.text().strip(),
            'descripcion': self.descripcion_edit.text().strip(),
            'tipo': self.tipo_combo.currentText(),
            'categoria': self.categoria_edit.text().strip(),
            'proveedor': self.proveedor_combo.currentText().strip(),
            'precio_unitario': self.precio_spin.value(),
            'unidad_medida': self.unidad_combo.currentText(),
            'stock_actual': self.stock_actual_spin.value(),
            'stock_minimo': self.stock_minimo_spin.value(),
            'ubicacion': self.ubicacion_edit.text().strip(),
            'marca': self.marca_edit.text().strip(),
            'modelo': self.modelo_edit.text().strip(),
            'color': self.color_edit.text().strip(),
            'material': self.material_edit.text().strip(),
            'dimensiones': self.dimensiones_edit.text().strip(),
            'peso': self.peso_spin.value(),
            'observaciones': self.observaciones_text.toPlainText(),
            'especificaciones': self.especificaciones_text.toPlainText(),
            'estado': self.estado_combo.currentText()
        }
    
    def validate_form(self):
        """Valida los datos del formulario"""
        if not self.codigo_edit.text().strip():
            QMessageBox.warning(self, "Error", "El código es requerido")
            return False
        
        if not self.descripcion_edit.text().strip():
            QMessageBox.warning(self, "Error", "La descripción es requerida")
            return False
        
        if not self.proveedor_combo.currentText().strip():
            QMessageBox.warning(self, "Error", "El proveedor es requerido")
            return False
        
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class AsignarObraDialog(QDialog):
    """Diálogo para asignar herrajes a obra"""
    
    def __init__(self, parent=None, herraje_data=None):
        super().__init__(parent)
        self.herraje_data = herraje_data
        self.setWindowTitle("Asignar Herraje a Obra")
        self.setFixedSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Asignar Herraje a Obra")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Información del herraje
        if self.herraje_data:
            herraje_info = QGroupBox("Herraje Seleccionado")
            herraje_layout = QVBoxLayout(herraje_info)
            
            info_text = f"""
            <b>Código:</b> {self.herraje_data.get('codigo', 'N/A')}<br>
            <b>Descripción:</b> {self.herraje_data.get('descripcion', 'N/A')}<br>
            <b>Proveedor:</b> {self.herraje_data.get('proveedor', 'N/A')}<br>
            <b>Precio:</b> ${self.herraje_data.get('precio_unitario', 0.0):.2f}<br>
            <b>Stock Actual:</b> {self.herraje_data.get('stock_actual', 0)} {self.herraje_data.get('unidad_medida', 'UND')}
            """
            
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            herraje_layout.addWidget(info_label)
            
            layout.addWidget(herraje_info)
        
        # Formulario de asignación
        form_group = QGroupBox("Datos de Asignación")
        form_layout = QFormLayout(form_group)
        
        # Selección de obra
        self.obra_combo = QComboBox()
        self.obra_combo.addItems([
            "Obra 1 - Residencial Norte",
            "Obra 2 - Edificio Central", 
            "Obra 3 - Plaza Comercial",
            "Obra 4 - Conjunto Habitacional",
            "Obra 5 - Oficinas Corporativas"
        ])
        form_layout.addRow("Obra*:", self.obra_combo)
        
        # Cantidad requerida
        self.cantidad_spin = QDoubleSpinBox()
        self.cantidad_spin.setRange(0.01, 99999.99)
        self.cantidad_spin.setDecimals(2)
        self.cantidad_spin.setValue(1.0)
        form_layout.addRow("Cantidad*:", self.cantidad_spin)
        
        # Fecha de entrega estimada
        self.fecha_entrega = QDateEdit()
        self.fecha_entrega.setDate(QDate.currentDate().addDays(7))
        self.fecha_entrega.setCalendarPopup(True)
        form_layout.addRow("Fecha Entrega:", self.fecha_entrega)
        
        # Observaciones
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setPlaceholderText("Observaciones sobre la asignación...")
        self.observaciones_text.setMaximumHeight(100)
        form_layout.addRow("Observaciones:", self.observaciones_text)
        
        layout.addWidget(form_group)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_asignacion_data(self):
        return {
            'obra': self.obra_combo.currentText(),
            'cantidad': self.cantidad_spin.value(),
            'fecha_entrega': self.fecha_entrega.date().toPython(),
            'observaciones': self.observaciones_text.toPlainText()
        }
    
    def validate_form(self):
        if self.cantidad_spin.value() <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return False
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class HerrajesCompletaView(QWidget):
    """Vista completa de herrajes con todas las funcionalidades"""
    
    # Señales
    herraje_created = pyqtSignal(dict)
    herraje_updated = pyqtSignal(dict)
    herraje_deleted = pyqtSignal(int)
    herraje_assigned = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.init_model()
        self.init_ui()
        self.load_data()
    
    def init_model(self):
        """Inicializa el modelo de herrajes"""
        try:
            db_connection = InventarioDatabaseConnection()
            self.model = HerrajesModel(db_connection)
        except Exception as e:
            print(f"Error inicializando modelo herrajes: {e}")
            self.model = HerrajesModel()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("🔧 Gestión Completa de Herrajes")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Gestión de Herrajes
        herrajes_tab = self.create_herrajes_tab()
        tabs.addTab(herrajes_tab, "Herrajes")
        
        # Tab 2: Asignación por Obra
        asignacion_tab = self.create_asignacion_tab()
        tabs.addTab(asignacion_tab, "Asignación por Obra")
        
        # Tab 3: Reportes y Exportación
        reportes_tab = self.create_reportes_tab()
        tabs.addTab(reportes_tab, "Reportes")
        
        # Tab 4: Estadísticas
        stats_tab = self.create_stats_tab()
        tabs.addTab(stats_tab, "Estadísticas")
        
        layout.addWidget(tabs)
    
    def create_herrajes_tab(self):
        """Crea la pestaña de gestión de herrajes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        nuevo_btn = QPushButton("Nuevo Herraje")
        nuevo_btn.clicked.connect(self.crear_herraje)
        toolbar.addWidget(nuevo_btn)
        
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(self.editar_herraje)
        toolbar.addWidget(editar_btn)
        
        eliminar_btn = QPushButton("Eliminar")
        eliminar_btn.clicked.connect(self.eliminar_herraje)
        toolbar.addWidget(eliminar_btn)
        
        toolbar.addStretch()
        
        # Búsqueda
        search_label = QLabel("Buscar:")
        toolbar.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Código, descripción o proveedor...")
        self.search_edit.textChanged.connect(self.buscar_herrajes)
        toolbar.addWidget(self.search_edit)
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout(filtros_group)
        
        self.tipo_filter = QComboBox()
        self.tipo_filter.addItems(["Todos", "BISAGRA", "CERRADURA", "MANIJA", "TORNILLO", "RIEL", "SOPORTE", "OTRO"])
        self.tipo_filter.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.tipo_filter)
        
        self.proveedor_filter = QComboBox()
        self.proveedor_filter.addItems(["Todos"])
        self.proveedor_filter.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Proveedor:"))
        filtros_layout.addWidget(self.proveedor_filter)
        
        self.estado_filter = QComboBox()
        self.estado_filter.addItems(["Todos", "ACTIVO", "INACTIVO", "DESCONTINUADO"])
        self.estado_filter.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Estado:"))
        filtros_layout.addWidget(self.estado_filter)
        
        layout.addWidget(filtros_group)
        
        # Tabla de herrajes
        self.herrajes_table = QTableWidget()
        self.herrajes_table.setColumnCount(10)
        self.herrajes_table.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Tipo", "Proveedor", 
            "Precio", "Stock", "Unidad", "Estado", "Última Act."
        ])
        
        # Configurar tabla
        header = self.herrajes_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.herrajes_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.herrajes_table.setAlternatingRowColors(True)
        self.herrajes_table.setSortingEnabled(True)
        
        # Menú contextual
        self.herrajes_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.herrajes_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.herrajes_table)
        
        return tab
    
    def create_asignacion_tab(self):
        """Crea la pestaña de asignación por obra"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Asignación de Herrajes por Obra")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Selector de obra
        obra_layout = QHBoxLayout()
        obra_layout.addWidget(QLabel("Obra:"))
        
        self.obra_selector = QComboBox()
        self.obra_selector.addItems([
            "Obra 1 - Residencial Norte",
            "Obra 2 - Edificio Central", 
            "Obra 3 - Plaza Comercial",
            "Obra 4 - Conjunto Habitacional",
            "Obra 5 - Oficinas Corporativas"
        ])
        self.obra_selector.currentTextChanged.connect(self.cargar_herrajes_obra)
        obra_layout.addWidget(self.obra_selector)
        
        asignar_btn = QPushButton("Asignar Herraje")
        asignar_btn.clicked.connect(self.asignar_herraje_a_obra)
        obra_layout.addWidget(asignar_btn)
        
        obra_layout.addStretch()
        layout.addLayout(obra_layout)
        
        # Tabla de herrajes asignados
        self.asignados_table = QTableWidget()
        self.asignados_table.setColumnCount(8)
        self.asignados_table.setHorizontalHeaderLabels([
            "Código", "Descripción", "Proveedor", "Cantidad", 
            "Precio Unit.", "Total", "Estado", "Fecha Asig."
        ])
        
        # Configurar tabla
        header = self.asignados_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.asignados_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.asignados_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.asignados_table)
        
        return tab
    
    def create_reportes_tab(self):
        """Crea la pestaña de reportes y exportación"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Reportes y Exportación")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Botones de exportación
        export_group = QGroupBox("Exportar Datos")
        export_layout = QGridLayout(export_group)
        
        export_pdf_btn = QPushButton("📄 Exportar a PDF")
        export_pdf_btn.clicked.connect(self.exportar_pdf)
        export_layout.addWidget(export_pdf_btn, 0, 0)
        
        export_excel_btn = QPushButton("[CHART] Exportar a Excel")
        export_excel_btn.clicked.connect(self.exportar_excel)
        export_layout.addWidget(export_excel_btn, 0, 1)
        
        export_obra_btn = QPushButton("🏗️ Reporte por Obra")
        export_obra_btn.clicked.connect(self.exportar_por_obra)
        export_layout.addWidget(export_obra_btn, 1, 0)
        
        export_proveedor_btn = QPushButton("🏪 Reporte por Proveedor")
        export_proveedor_btn.clicked.connect(self.exportar_por_proveedor)
        export_layout.addWidget(export_proveedor_btn, 1, 1)
        
        layout.addWidget(export_group)
        
        # Área de vista previa
        preview_group = QGroupBox("Vista Previa del Reporte")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Seleccione un tipo de reporte para generar vista previa...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        return tab
    
    def create_stats_tab(self):
        """Crea la pestaña de estadísticas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Estadísticas de Herrajes")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Estadísticas básicas
        stats_layout = QHBoxLayout()
        
        # Total herrajes
        total_group = QGroupBox("Total Herrajes")
        total_layout = QVBoxLayout(total_group)
        self.total_herrajes_label = QLabel("0")
        self.total_herrajes_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_herrajes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.total_herrajes_label)
        stats_layout.addWidget(total_group)
        
        # Valor total
        valor_group = QGroupBox("Valor Total Inventario")
        valor_layout = QVBoxLayout(valor_group)
        self.valor_total_label = QLabel("$0.00")
        self.valor_total_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.valor_total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        valor_layout.addWidget(self.valor_total_label)
        stats_layout.addWidget(valor_group)
        
        # Proveedores
        proveedores_group = QGroupBox("Proveedores Activos")
        proveedores_layout = QVBoxLayout(proveedores_group)
        self.proveedores_label = QLabel("0")
        self.proveedores_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.proveedores_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        proveedores_layout.addWidget(self.proveedores_label)
        stats_layout.addWidget(proveedores_group)
        
        layout.addLayout(stats_layout)
        
        # Gráfico de herrajes por proveedor
        chart_group = QGroupBox("Herrajes por Proveedor")
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_table = QTableWidget()
        self.chart_table.setColumnCount(2)
        self.chart_table.setHorizontalHeaderLabels(["Proveedor", "Cantidad"])
        self.chart_table.setMaximumHeight(200)
        chart_layout.addWidget(self.chart_table)
        
        layout.addWidget(chart_group)
        
        return tab
    
    def load_data(self):
        """Carga todos los datos"""
        self.cargar_herrajes()
        self.cargar_estadisticas()
        self.cargar_proveedores()
    
    def cargar_herrajes(self):
        """Carga la lista de herrajes"""
        if not self.model:
            return
        
        herrajes = self.model.obtener_todos_herrajes()
        
        self.herrajes_table.setRowCount(len(herrajes))
        
        for i, herraje in enumerate(herrajes):
            self.herrajes_table.setItem(i, 0, QTableWidgetItem(str(herraje.get('id', ''))))
            self.herrajes_table.setItem(i, 1, QTableWidgetItem(herraje.get('codigo', '')))
            self.herrajes_table.setItem(i, 2, QTableWidgetItem(herraje.get('descripcion', '')))
            self.herrajes_table.setItem(i, 3, QTableWidgetItem(herraje.get('tipo', '')))
            self.herrajes_table.setItem(i, 4, QTableWidgetItem(herraje.get('proveedor', '')))
            self.herrajes_table.setItem(i, 5, QTableWidgetItem(f"${herraje.get('precio_unitario', 0.0):.2f}"))
            self.herrajes_table.setItem(i, 6, QTableWidgetItem(str(herraje.get('stock_actual', 0))))
            self.herrajes_table.setItem(i, 7, QTableWidgetItem(herraje.get('unidad_medida', '')))
            self.herrajes_table.setItem(i, 8, QTableWidgetItem(herraje.get('estado', '')))
            
            fecha_act = herraje.get('fecha_actualizacion', '')
            if fecha_act:
                fecha_str = str(fecha_act).split('.')[0]  # Remover microsegundos
            else:
                fecha_str = ''
            self.herrajes_table.setItem(i, 9, QTableWidgetItem(fecha_str))
    
    def cargar_estadisticas(self):
        """Carga las estadísticas"""
        if not self.model:
            return
        
        stats = self.model.obtener_estadisticas()
        
        self.total_herrajes_label.setText(str(stats.get('total_herrajes', 0)))
        self.valor_total_label.setText(f"${stats.get('valor_total_inventario', 0.0):,.2f}")
        self.proveedores_label.setText(str(stats.get('proveedores_activos', 0)))
        
        # Actualizar tabla de proveedores
        proveedores = stats.get('herrajes_por_proveedor', [])
        self.chart_table.setRowCount(len(proveedores))
        
        for i, proveedor in enumerate(proveedores):
            self.chart_table.setItem(i, 0, QTableWidgetItem(proveedor['proveedor']))
            self.chart_table.setItem(i, 1, QTableWidgetItem(str(proveedor['cantidad'])))
    
    def cargar_proveedores(self):
        """Carga la lista de proveedores para filtros"""
        if not self.model:
            return
        
        proveedores = self.model.obtener_proveedores()
        
        # Actualizar filtro de proveedores
        self.proveedor_filter.clear()
        self.proveedor_filter.addItem("Todos")
        self.proveedor_filter.addItems(proveedores)
    
    def crear_herraje(self):
        """Crea un nuevo herraje"""
        dialog = HerrajeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_herraje_data()
            
            if self.model:
                success, message = self.model.crear_herraje(datos)
                if success:
                    QMessageBox.information(self, "Éxito", message)
                    self.load_data()
                    self.herraje_created.emit(datos)
                else:
                    QMessageBox.warning(self, "Error", message)
    
    def editar_herraje(self):
        """Edita el herraje seleccionado"""
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un herraje para editar")
            return
        
        herraje_id = int(self.herrajes_table.item(current_row, 0).text())
        
        if self.model:
            herraje_data = self.model.obtener_herraje_por_id(herraje_id)
            if herraje_data:
                dialog = HerrajeDialog(self, herraje_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    datos = dialog.get_herraje_data()
                    
                    success, message = self.model.actualizar_herraje(herraje_id, datos)
                    if success:
                        QMessageBox.information(self, "Éxito", message)
                        self.load_data()
                        self.herraje_updated.emit(datos)
                    else:
                        QMessageBox.warning(self, "Error", message)
    
    def eliminar_herraje(self):
        """Elimina el herraje seleccionado"""
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un herraje para eliminar")
            return
        
        herraje_id = int(self.herrajes_table.item(current_row, 0).text())
        codigo = self.herrajes_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar el herraje '{codigo}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes and self.model:
            success, message = self.model.eliminar_herraje(herraje_id)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.load_data()
                self.herraje_deleted.emit(herraje_id)
            else:
                QMessageBox.warning(self, "Error", message)
    
    def buscar_herrajes(self, text):
        """Busca herrajes por texto"""
        for i in range(self.herrajes_table.rowCount()):
            show = False
            for j in range(1, self.herrajes_table.columnCount()):  # Excluir columna ID
                item = self.herrajes_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.herrajes_table.setRowHidden(i, not show)
    
    def aplicar_filtros(self):
        """Aplica los filtros seleccionados"""
        tipo_filter = self.tipo_filter.currentText()
        proveedor_filter = self.proveedor_filter.currentText()
        estado_filter = self.estado_filter.currentText()
        
        for i in range(self.herrajes_table.rowCount()):
            show = True
            
            # Filtro por tipo
            if tipo_filter != "Todos":
                tipo_item = self.herrajes_table.item(i, 3)
                if not tipo_item or tipo_item.text() != tipo_filter:
                    show = False
            
            # Filtro por proveedor
            if proveedor_filter != "Todos":
                proveedor_item = self.herrajes_table.item(i, 4)
                if not proveedor_item or proveedor_item.text() != proveedor_filter:
                    show = False
            
            # Filtro por estado
            if estado_filter != "Todos":
                estado_item = self.herrajes_table.item(i, 8)
                if not estado_item or estado_item.text() != estado_filter:
                    show = False
            
            self.herrajes_table.setRowHidden(i, not show)
    
    def asignar_herraje_a_obra(self):
        """Asigna un herraje a una obra"""
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un herraje para asignar")
            return
        
        herraje_id = int(self.herrajes_table.item(current_row, 0).text())
        
        if self.model:
            herraje_data = self.model.obtener_herraje_por_id(herraje_id)
            if herraje_data:
                dialog = AsignarObraDialog(self, herraje_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    datos = dialog.get_asignacion_data()
                    
                    # Simular asignación (aquí iría la lógica real)
                    QMessageBox.information(self, "Éxito", 
                        f"Herraje asignado a {datos['obra']} con cantidad {datos['cantidad']}")
                    
                    self.herraje_assigned.emit(datos)
                    self.cargar_herrajes_obra()
    
    def cargar_herrajes_obra(self):
        """Carga los herrajes asignados a la obra seleccionada"""
        # Simular datos de herrajes asignados
        datos_demo = [
            {
                'codigo': 'BIS-001',
                'descripcion': 'Bisagra de puerta estándar',
                'proveedor': 'Herrajes SA',
                'cantidad': 24,
                'precio_unitario': 15.50,
                'estado': 'PENDIENTE',
                'fecha_asignacion': '2024-01-15'
            },
            {
                'codigo': 'CER-001',
                'descripcion': 'Cerradura de seguridad',
                'proveedor': 'Seguridad Total',
                'cantidad': 12,
                'precio_unitario': 85.00,
                'estado': 'COMPLETADO',
                'fecha_asignacion': '2024-01-10'
            }
        ]
        
        self.asignados_table.setRowCount(len(datos_demo))
        
        for i, herraje in enumerate(datos_demo):
            self.asignados_table.setItem(i, 0, QTableWidgetItem(herraje['codigo']))
            self.asignados_table.setItem(i, 1, QTableWidgetItem(herraje['descripcion']))
            self.asignados_table.setItem(i, 2, QTableWidgetItem(herraje['proveedor']))
            self.asignados_table.setItem(i, 3, QTableWidgetItem(str(herraje['cantidad'])))
            self.asignados_table.setItem(i, 4, QTableWidgetItem(f"${herraje['precio_unitario']:.2f}"))
            total = herraje['cantidad'] * herraje['precio_unitario']
            self.asignados_table.setItem(i, 5, QTableWidgetItem(f"${total:.2f}"))
            self.asignados_table.setItem(i, 6, QTableWidgetItem(herraje['estado']))
            self.asignados_table.setItem(i, 7, QTableWidgetItem(herraje['fecha_asignacion']))
    
    def exportar_pdf(self):
        """Exporta los herrajes a PDF"""
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_export_data()
            
            # Simular exportación a PDF
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar PDF", f"herrajes_{datos['obra']}.pdf", "PDF files (*.pdf)"
            )
            
            if filename:
                # Aquí iría la lógica real de exportación a PDF
                QMessageBox.information(self, "Éxito", f"PDF exportado exitosamente a {filename}")
    
    def exportar_excel(self):
        """Exporta los herrajes a Excel"""
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_export_data()
            
            # Simular exportación a Excel
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Excel", f"herrajes_{datos['obra']}.xlsx", "Excel files (*.xlsx)"
            )
            
            if filename:
                # Aquí iría la lógica real de exportación a Excel
                QMessageBox.information(self, "Éxito", f"Excel exportado exitosamente a {filename}")
    
    def exportar_por_obra(self):
        """Genera reporte por obra"""
        obra_seleccionada = self.obra_selector.currentText()
        
        reporte = f"""
REPORTE DE HERRAJES POR OBRA
============================

Obra: {obra_seleccionada}
Fecha: {QDate.currentDate().toString('dd/MM/yyyy')}

HERRAJES ASIGNADOS:
------------------
• Bisagra de puerta estándar (BIS-001)
  - Cantidad: 24 unidades
  - Precio unitario: $15.50
  - Total: $372.00
  - Estado: PENDIENTE

• Cerradura de seguridad (CER-001)
  - Cantidad: 12 unidades
  - Precio unitario: $85.00
  - Total: $1,020.00
  - Estado: COMPLETADO

RESUMEN:
--------
Total herrajes: 2 tipos
Total cantidad: 36 unidades
Valor total: $1,392.00

Estado general: 50% completado
        """
        
        self.preview_text.setPlainText(reporte)
    
    def exportar_por_proveedor(self):
        """Genera reporte por proveedor"""
        reporte = f"""
REPORTE DE HERRAJES POR PROVEEDOR
===============================

Fecha: {QDate.currentDate().toString('dd/MM/yyyy')}

HERRAJES SA:
-----------
• Bisagra de puerta estándar (BIS-001): 50 unidades - $15.50 c/u
• Manija de aluminio (MAN-001): 30 unidades - $25.00 c/u
Total: $1,525.00

SEGURIDAD TOTAL:
---------------
• Cerradura de seguridad (CER-001): 25 unidades - $85.00 c/u
• Cerradura multipunto (CER-002): 15 unidades - $120.00 c/u
Total: $3,925.00

RESUMEN GENERAL:
--------------
Total proveedores: 2
Total herrajes: 4 tipos
Valor total inventario: $5,450.00
        """
        
        self.preview_text.setPlainText(reporte)
    
    def show_context_menu(self, position):
        """Muestra menú contextual en la tabla"""
        if self.herrajes_table.itemAt(position):
            menu = QMenu()
            
            edit_action = menu.addAction("Editar")
            edit_action.triggered.connect(self.editar_herraje)
            
            delete_action = menu.addAction("Eliminar")
            delete_action.triggered.connect(self.eliminar_herraje)
            
            menu.addSeparator()
            
            assign_action = menu.addAction("Asignar a Obra")
            assign_action.triggered.connect(self.asignar_herraje_a_obra)
            
            menu.exec(self.herrajes_table.mapToGlobal(position))


# Ejemplo de uso
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear vista completa de herrajes
    herrajes_view = HerrajesCompletaView()
    herrajes_view.show()
    
    sys.exit(app.exec())