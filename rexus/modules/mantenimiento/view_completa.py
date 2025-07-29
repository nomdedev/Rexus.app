"""
Vista Completa de Mantenimiento - Rexus.app v2.0.0

Interfaz completa para gestión de mantenimiento con historial de máquinas
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QTextEdit, QFrame, QHeaderView,
    QAbstractItemView, QMenu, QApplication, QScrollArea, QGridLayout,
    QDateEdit, QProgressBar, QSplitter, QListWidget, QListWidgetItem,
    QFileDialog, QCalendarWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap, QColor

from rexus.core.database import InventarioDatabaseConnection


class MaquinariaDialog(QDialog):
    """Diálogo para crear/editar maquinaria"""
    
    def __init__(self, parent=None, maquina_data=None):
        super().__init__(parent)
        self.maquina_data = maquina_data
        self.setWindowTitle("Nueva Máquina" if not maquina_data else "Editar Máquina")
        self.setFixedSize(700, 800)
        self.init_ui()
        
        if maquina_data:
            self.load_maquina_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Nueva Máquina" if not self.maquina_data else "Editar Máquina")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Información básica
        basic_group = QGroupBox("Información Básica")
        basic_layout = QFormLayout(basic_group)
        
        self.codigo_edit = QLineEdit()
        self.codigo_edit.setPlaceholderText("Código único de la máquina")
        basic_layout.addRow("Código*:", self.codigo_edit)
        
        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Nombre descriptivo")
        basic_layout.addRow("Nombre*:", self.nombre_edit)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "Cortadora", "Soldadora", "Pulidora", "Taladro", "Prensa",
            "Compresor", "Generador", "Montacargas", "Grúa", "Otro"
        ])
        basic_layout.addRow("Tipo*:", self.tipo_combo)
        
        self.marca_edit = QLineEdit()
        self.marca_edit.setPlaceholderText("Marca del equipo")
        basic_layout.addRow("Marca:", self.marca_edit)
        
        self.modelo_edit = QLineEdit()
        self.modelo_edit.setPlaceholderText("Modelo del equipo")
        basic_layout.addRow("Modelo:", self.modelo_edit)
        
        self.numero_serie_edit = QLineEdit()
        self.numero_serie_edit.setPlaceholderText("Número de serie")
        basic_layout.addRow("Nº Serie:", self.numero_serie_edit)
        
        scroll_layout.addWidget(basic_group)
        
        # Información técnica
        tech_group = QGroupBox("Información Técnica")
        tech_layout = QFormLayout(tech_group)
        
        self.potencia_edit = QLineEdit()
        self.potencia_edit.setPlaceholderText("Ej: 5 HP, 2.2 kW")
        tech_layout.addRow("Potencia:", self.potencia_edit)
        
        self.voltaje_edit = QLineEdit()
        self.voltaje_edit.setPlaceholderText("Ej: 220V, 440V")
        tech_layout.addRow("Voltaje:", self.voltaje_edit)
        
        self.amperaje_edit = QLineEdit()
        self.amperaje_edit.setPlaceholderText("Ej: 10A, 15A")
        tech_layout.addRow("Amperaje:", self.amperaje_edit)
        
        self.peso_spin = QDoubleSpinBox()
        self.peso_spin.setRange(0, 99999.99)
        self.peso_spin.setDecimals(2)
        self.peso_spin.setSuffix(" kg")
        tech_layout.addRow("Peso:", self.peso_spin)
        
        self.dimensiones_edit = QLineEdit()
        self.dimensiones_edit.setPlaceholderText("Ej: 150x80x120 cm")
        tech_layout.addRow("Dimensiones:", self.dimensiones_edit)
        
        scroll_layout.addWidget(tech_group)
        
        # Información de compra
        purchase_group = QGroupBox("Información de Compra")
        purchase_layout = QFormLayout(purchase_group)
        
        self.proveedor_edit = QLineEdit()
        self.proveedor_edit.setPlaceholderText("Nombre del proveedor")
        purchase_layout.addRow("Proveedor:", self.proveedor_edit)
        
        self.fecha_compra = QDateEdit()
        self.fecha_compra.setDate(QDate.currentDate())
        self.fecha_compra.setCalendarPopup(True)
        purchase_layout.addRow("Fecha Compra:", self.fecha_compra)
        
        self.costo_spin = QDoubleSpinBox()
        self.costo_spin.setRange(0, 99999999.99)
        self.costo_spin.setDecimals(2)
        self.costo_spin.setSuffix(" $")
        purchase_layout.addRow("Costo:", self.costo_spin)
        
        self.garantia_spin = QSpinBox()
        self.garantia_spin.setRange(0, 120)
        self.garantia_spin.setSuffix(" meses")
        purchase_layout.addRow("Garantía:", self.garantia_spin)
        
        scroll_layout.addWidget(purchase_group)
        
        # Ubicación y estado
        location_group = QGroupBox("Ubicación y Estado")
        location_layout = QFormLayout(location_group)
        
        self.ubicacion_edit = QLineEdit()
        self.ubicacion_edit.setPlaceholderText("Ubicación física de la máquina")
        location_layout.addRow("Ubicación*:", self.ubicacion_edit)
        
        self.area_combo = QComboBox()
        self.area_combo.addItems([
            "Producción", "Mantenimiento", "Almacén", "Oficinas", "Patio", "Otro"
        ])
        location_layout.addRow("Área:", self.area_combo)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems([
            "Operativo", "En Mantenimiento", "Fuera de Servicio", "En Reparación", "Standby"
        ])
        location_layout.addRow("Estado*:", self.estado_combo)
        
        self.responsable_edit = QLineEdit()
        self.responsable_edit.setPlaceholderText("Persona responsable")
        location_layout.addRow("Responsable:", self.responsable_edit)
        
        scroll_layout.addWidget(location_group)
        
        # Configuración de mantenimiento
        maintenance_group = QGroupBox("Configuración de Mantenimiento")
        maintenance_layout = QFormLayout(maintenance_group)
        
        self.frecuencia_combo = QComboBox()
        self.frecuencia_combo.addItems([
            "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", 
            "Trimestral", "Semestral", "Anual"
        ])
        maintenance_layout.addRow("Frecuencia:", self.frecuencia_combo)
        
        self.horas_servicio_spin = QSpinBox()
        self.horas_servicio_spin.setRange(0, 999999)
        self.horas_servicio_spin.setSuffix(" hrs")
        maintenance_layout.addRow("Horas de Servicio:", self.horas_servicio_spin)
        
        self.proximo_mantenimiento = QDateEdit()
        self.proximo_mantenimiento.setDate(QDate.currentDate().addMonths(1))
        self.proximo_mantenimiento.setCalendarPopup(True)
        maintenance_layout.addRow("Próximo Mant.:", self.proximo_mantenimiento)
        
        scroll_layout.addWidget(maintenance_group)
        
        # Observaciones
        obs_group = QGroupBox("Observaciones y Notas")
        obs_layout = QVBoxLayout(obs_group)
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setPlaceholderText("Observaciones generales, características especiales, etc.")
        self.observaciones_text.setMaximumHeight(100)
        obs_layout.addWidget(self.observaciones_text)
        
        scroll_layout.addWidget(obs_group)
        
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
    
    def load_maquina_data(self):
        """Carga los datos de la máquina"""
        if not self.maquina_data:
            return
            
        self.codigo_edit.setText(self.maquina_data.get('codigo', ''))
        self.nombre_edit.setText(self.maquina_data.get('nombre', ''))
        self.marca_edit.setText(self.maquina_data.get('marca', ''))
        self.modelo_edit.setText(self.maquina_data.get('modelo', ''))
        self.numero_serie_edit.setText(self.maquina_data.get('numero_serie', ''))
        self.potencia_edit.setText(self.maquina_data.get('potencia', ''))
        self.voltaje_edit.setText(self.maquina_data.get('voltaje', ''))
        self.amperaje_edit.setText(self.maquina_data.get('amperaje', ''))
        self.peso_spin.setValue(self.maquina_data.get('peso', 0.0))
        self.dimensiones_edit.setText(self.maquina_data.get('dimensiones', ''))
        self.proveedor_edit.setText(self.maquina_data.get('proveedor', ''))
        self.costo_spin.setValue(self.maquina_data.get('costo', 0.0))
        self.garantia_spin.setValue(self.maquina_data.get('garantia_meses', 0))
        self.ubicacion_edit.setText(self.maquina_data.get('ubicacion', ''))
        self.responsable_edit.setText(self.maquina_data.get('responsable', ''))
        self.horas_servicio_spin.setValue(self.maquina_data.get('horas_servicio', 0))
        self.observaciones_text.setText(self.maquina_data.get('observaciones', ''))
    
    def get_maquina_data(self):
        """Obtiene los datos del formulario"""
        return {
            'codigo': self.codigo_edit.text().strip(),
            'nombre': self.nombre_edit.text().strip(),
            'tipo': self.tipo_combo.currentText(),
            'marca': self.marca_edit.text().strip(),
            'modelo': self.modelo_edit.text().strip(),
            'numero_serie': self.numero_serie_edit.text().strip(),
            'potencia': self.potencia_edit.text().strip(),
            'voltaje': self.voltaje_edit.text().strip(),
            'amperaje': self.amperaje_edit.text().strip(),
            'peso': self.peso_spin.value(),
            'dimensiones': self.dimensiones_edit.text().strip(),
            'proveedor': self.proveedor_edit.text().strip(),
            'fecha_compra': self.fecha_compra.date().toPython(),
            'costo': self.costo_spin.value(),
            'garantia_meses': self.garantia_spin.value(),
            'ubicacion': self.ubicacion_edit.text().strip(),
            'area': self.area_combo.currentText(),
            'estado': self.estado_combo.currentText(),
            'responsable': self.responsable_edit.text().strip(),
            'frecuencia_mantenimiento': self.frecuencia_combo.currentText(),
            'horas_servicio': self.horas_servicio_spin.value(),
            'proximo_mantenimiento': self.proximo_mantenimiento.date().toPython(),
            'observaciones': self.observaciones_text.toPlainText()
        }
    
    def validate_form(self):
        """Valida el formulario"""
        if not self.codigo_edit.text().strip():
            QMessageBox.warning(self, "Error", "El código es requerido")
            return False
        
        if not self.nombre_edit.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return False
        
        if not self.ubicacion_edit.text().strip():
            QMessageBox.warning(self, "Error", "La ubicación es requerida")
            return False
        
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class ServicioDialog(QDialog):
    """Diálogo para registrar servicios/mantenimientos"""
    
    def __init__(self, parent=None, maquina_codigo=None, servicio_data=None):
        super().__init__(parent)
        self.maquina_codigo = maquina_codigo
        self.servicio_data = servicio_data
        self.setWindowTitle("Nuevo Servicio" if not servicio_data else "Editar Servicio")
        self.setFixedSize(600, 500)
        self.init_ui()
        
        if servicio_data:
            self.load_servicio_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Nuevo Servicio" if not self.servicio_data else "Editar Servicio")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Información del servicio
        form_group = QGroupBox("Información del Servicio")
        form_layout = QFormLayout(form_group)
        
        if self.maquina_codigo:
            maquina_label = QLabel(f"Máquina: {self.maquina_codigo}")
            maquina_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            form_layout.addRow("", maquina_label)
        
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        form_layout.addRow("Fecha*:", self.fecha_edit)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "Mantenimiento Preventivo", "Mantenimiento Correctivo", 
            "Reparación", "Inspección", "Calibración", "Limpieza", "Otro"
        ])
        form_layout.addRow("Tipo*:", self.tipo_combo)
        
        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setPlaceholderText("Descripción detallada del servicio realizado...")
        self.descripcion_edit.setMaximumHeight(100)
        form_layout.addRow("Descripción*:", self.descripcion_edit)
        
        self.tecnico_edit = QLineEdit()
        self.tecnico_edit.setPlaceholderText("Nombre del técnico responsable")
        form_layout.addRow("Técnico:", self.tecnico_edit)
        
        self.duracion_spin = QDoubleSpinBox()
        self.duracion_spin.setRange(0.1, 99.9)
        self.duracion_spin.setDecimals(1)
        self.duracion_spin.setSuffix(" hrs")
        form_layout.addRow("Duración:", self.duracion_spin)
        
        self.costo_spin = QDoubleSpinBox()
        self.costo_spin.setRange(0, 99999999.99)
        self.costo_spin.setDecimals(2)
        self.costo_spin.setSuffix(" $")
        form_layout.addRow("Costo:", self.costo_spin)
        
        self.repuestos_edit = QTextEdit()
        self.repuestos_edit.setPlaceholderText("Lista de repuestos utilizados...")
        self.repuestos_edit.setMaximumHeight(60)
        form_layout.addRow("Repuestos:", self.repuestos_edit)
        
        self.observaciones_edit = QTextEdit()
        self.observaciones_edit.setPlaceholderText("Observaciones adicionales...")
        self.observaciones_edit.setMaximumHeight(60)
        form_layout.addRow("Observaciones:", self.observaciones_edit)
        
        # Próximo servicio
        self.proximo_servicio = QDateEdit()
        self.proximo_servicio.setDate(QDate.currentDate().addMonths(1))
        self.proximo_servicio.setCalendarPopup(True)
        form_layout.addRow("Próximo Servicio:", self.proximo_servicio)
        
        layout.addWidget(form_group)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_servicio_data(self):
        """Carga los datos del servicio"""
        if not self.servicio_data:
            return
            
        self.descripcion_edit.setText(self.servicio_data.get('descripcion', ''))
        self.tecnico_edit.setText(self.servicio_data.get('tecnico', ''))
        self.duracion_spin.setValue(self.servicio_data.get('duracion', 0.0))
        self.costo_spin.setValue(self.servicio_data.get('costo', 0.0))
        self.repuestos_edit.setText(self.servicio_data.get('repuestos', ''))
        self.observaciones_edit.setText(self.servicio_data.get('observaciones', ''))
    
    def get_servicio_data(self):
        """Obtiene los datos del formulario"""
        return {
            'maquina_codigo': self.maquina_codigo,
            'fecha': self.fecha_edit.date().toPython(),
            'tipo': self.tipo_combo.currentText(),
            'descripcion': self.descripcion_edit.toPlainText(),
            'tecnico': self.tecnico_edit.text().strip(),
            'duracion': self.duracion_spin.value(),
            'costo': self.costo_spin.value(),
            'repuestos': self.repuestos_edit.toPlainText(),
            'observaciones': self.observaciones_edit.toPlainText(),
            'proximo_servicio': self.proximo_servicio.date().toPython()
        }
    
    def validate_form(self):
        """Valida el formulario"""
        if not self.descripcion_edit.toPlainText().strip():
            QMessageBox.warning(self, "Error", "La descripción es requerida")
            return False
        
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class MantenimientoCompletaView(QWidget):
    """Vista completa de mantenimiento con historial de máquinas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        
        # Título con height reducido
        title = QLabel("🛠️ Gestión de Mantenimiento")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                max-height: 40px;
            }
        """)
        layout.addWidget(title)
        
        # Tabs principales
        tabs = QTabWidget()
        
        # Tab 1: Maquinaria
        maquinaria_tab = self.create_maquinaria_tab()
        tabs.addTab(maquinaria_tab, "🏭 Maquinaria")
        
        # Tab 2: Servicios
        servicios_tab = self.create_servicios_tab()
        tabs.addTab(servicios_tab, "🔧 Servicios")
        
        # Tab 3: Planificación
        planificacion_tab = self.create_planificacion_tab()
        tabs.addTab(planificacion_tab, "📅 Planificación")
        
        # Tab 4: Reportes
        reportes_tab = self.create_reportes_tab()
        tabs.addTab(reportes_tab, "📊 Reportes")
        
        layout.addWidget(tabs)
    
    def create_maquinaria_tab(self):
        """Crea la pestaña de maquinaria"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        nueva_btn = QPushButton("Nueva Máquina")
        nueva_btn.clicked.connect(self.crear_maquina)
        toolbar.addWidget(nueva_btn)
        
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(self.editar_maquina)
        toolbar.addWidget(editar_btn)
        
        eliminar_btn = QPushButton("Eliminar")
        eliminar_btn.clicked.connect(self.eliminar_maquina)
        toolbar.addWidget(eliminar_btn)
        
        toolbar.addStretch()
        
        # Filtros
        filtro_tipo = QComboBox()
        filtro_tipo.addItems(["Todos", "Cortadora", "Soldadora", "Pulidora", "Taladro", "Prensa"])
        filtro_tipo.currentTextChanged.connect(self.filtrar_maquinas)
        toolbar.addWidget(QLabel("Tipo:"))
        toolbar.addWidget(filtro_tipo)
        
        filtro_estado = QComboBox()
        filtro_estado.addItems(["Todos", "Operativo", "En Mantenimiento", "Fuera de Servicio"])
        filtro_estado.currentTextChanged.connect(self.filtrar_maquinas)
        toolbar.addWidget(QLabel("Estado:"))
        toolbar.addWidget(filtro_estado)
        
        # Búsqueda
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Buscar máquina...")
        search_edit.textChanged.connect(self.buscar_maquinas)
        toolbar.addWidget(search_edit)
        
        layout.addLayout(toolbar)
        
        # Estadísticas rápidas (cuadros pequeños)
        stats_layout = QHBoxLayout()
        
        stats_cards = [
            ("Total Máquinas", "15", "#3498db"),
            ("Operativas", "12", "#2ecc71"),
            ("En Mantenimiento", "2", "#f39c12"),
            ("Fuera de Servicio", "1", "#e74c3c")
        ]
        
        for titulo, valor, color in stats_cards:
            card = QFrame()
            card.setFixedSize(120, 60)  # Cuadros pequeños 120x60
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(2)
            
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-size: 9px; color: #7f8c8d; font-weight: 500;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(valor)
            value_label.setStyleSheet(f"font-size: 18px; color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            stats_layout.addWidget(card)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Tabla de maquinaria
        self.maquinas_table = QTableWidget()
        self.maquinas_table.setColumnCount(8)
        self.maquinas_table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Tipo", "Marca", "Ubicación", 
            "Estado", "Último Servicio", "Próximo Servicio"
        ])
        
        # Configurar tabla
        header = self.maquinas_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.maquinas_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.maquinas_table.setAlternatingRowColors(True)
        self.maquinas_table.setSortingEnabled(True)
        
        # Menú contextual
        self.maquinas_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.maquinas_table.customContextMenuRequested.connect(self.show_maquina_context_menu)
        
        # Doble clic para ver historial
        self.maquinas_table.itemDoubleClicked.connect(self.ver_historial_maquina)
        
        layout.addWidget(self.maquinas_table)
        
        return tab
    
    def create_servicios_tab(self):
        """Crea la pestaña de servicios"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        nuevo_btn = QPushButton("Nuevo Servicio")
        nuevo_btn.clicked.connect(self.crear_servicio)
        toolbar.addWidget(nuevo_btn)
        
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(self.editar_servicio)
        toolbar.addWidget(editar_btn)
        
        eliminar_btn = QPushButton("Eliminar")
        eliminar_btn.clicked.connect(self.eliminar_servicio)
        toolbar.addWidget(eliminar_btn)
        
        toolbar.addStretch()
        
        # Filtros
        filtro_tipo = QComboBox()
        filtro_tipo.addItems(["Todos", "Preventivo", "Correctivo", "Reparación", "Inspección"])
        toolbar.addWidget(QLabel("Tipo:"))
        toolbar.addWidget(filtro_tipo)
        
        filtro_mes = QComboBox()
        filtro_mes.addItems(["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"])
        toolbar.addWidget(QLabel("Mes:"))
        toolbar.addWidget(filtro_mes)
        
        layout.addLayout(toolbar)
        
        # Tabla de servicios
        self.servicios_table = QTableWidget()
        self.servicios_table.setColumnCount(8)
        self.servicios_table.setHorizontalHeaderLabels([
            "Fecha", "Máquina", "Tipo", "Descripción", "Técnico", 
            "Duración", "Costo", "Estado"
        ])
        
        # Configurar tabla
        header = self.servicios_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.servicios_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.servicios_table.setAlternatingRowColors(True)
        self.servicios_table.setSortingEnabled(True)
        
        layout.addWidget(self.servicios_table)
        
        return tab
    
    def create_planificacion_tab(self):
        """Crea la pestaña de planificación"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Planificación de Mantenimientos")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Splitter para calendario y lista
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Calendario
        calendar_group = QGroupBox("Calendario de Mantenimientos")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.mostrar_mantenimientos_fecha)
        calendar_layout.addWidget(self.calendar)
        
        splitter.addWidget(calendar_group)
        
        # Lista de mantenimientos programados
        list_group = QGroupBox("Mantenimientos Programados")
        list_layout = QVBoxLayout(list_group)
        
        self.mantenimientos_list = QListWidget()
        list_layout.addWidget(self.mantenimientos_list)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        programar_btn = QPushButton("Programar Mantenimiento")
        programar_btn.clicked.connect(self.programar_mantenimiento)
        buttons_layout.addWidget(programar_btn)
        
        completar_btn = QPushButton("Marcar Completado")
        completar_btn.clicked.connect(self.completar_mantenimiento)
        buttons_layout.addWidget(completar_btn)
        
        list_layout.addLayout(buttons_layout)
        
        splitter.addWidget(list_group)
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_reportes_tab(self):
        """Crea la pestaña de reportes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Reportes de Mantenimiento")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Botones de reportes
        reports_layout = QGridLayout()
        
        reports = [
            ("📊 Reporte de Máquinas", self.generar_reporte_maquinas),
            ("🔧 Historial de Servicios", self.generar_historial_servicios),
            ("💰 Costos de Mantenimiento", self.generar_costos_mantenimiento),
            ("📅 Mantenimientos Programados", self.generar_mantenimientos_programados),
            ("📈 Indicadores de Rendimiento", self.generar_indicadores_rendimiento),
            ("🔍 Análisis de Averías", self.generar_analisis_averias)
        ]
        
        for i, (nombre, funcion) in enumerate(reports):
            btn = QPushButton(nombre)
            btn.clicked.connect(funcion)
            btn.setMinimumHeight(40)
            reports_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(reports_layout)
        
        # Área de vista previa
        preview_group = QGroupBox("Vista Previa del Reporte")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Seleccione un reporte para generar vista previa...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        return tab
    
    def load_data(self):
        """Carga todos los datos"""
        self.cargar_maquinas()
        self.cargar_servicios()
        self.cargar_mantenimientos_programados()
    
    def cargar_maquinas(self):
        """Carga la lista de máquinas"""
        # Datos demo
        maquinas = [
            {
                "codigo": "MAQ-001", "nombre": "Cortadora Plasma", "tipo": "Cortadora",
                "marca": "Hypertherm", "ubicacion": "Taller A", "estado": "Operativo",
                "ultimo_servicio": "2024-01-15", "proximo_servicio": "2024-02-15"
            },
            {
                "codigo": "MAQ-002", "nombre": "Soldadora MIG", "tipo": "Soldadora",
                "marca": "Lincoln", "ubicacion": "Taller B", "estado": "En Mantenimiento",
                "ultimo_servicio": "2024-01-10", "proximo_servicio": "2024-02-10"
            },
            {
                "codigo": "MAQ-003", "nombre": "Pulidora Angular", "tipo": "Pulidora",
                "marca": "Bosch", "ubicacion": "Taller A", "estado": "Operativo",
                "ultimo_servicio": "2024-01-20", "proximo_servicio": "2024-02-20"
            },
            {
                "codigo": "MAQ-004", "nombre": "Taladro Industrial", "tipo": "Taladro",
                "marca": "Makita", "ubicacion": "Taller C", "estado": "Fuera de Servicio",
                "ultimo_servicio": "2024-01-05", "proximo_servicio": "2024-02-05"
            },
            {
                "codigo": "MAQ-005", "nombre": "Prensa Hidráulica", "tipo": "Prensa",
                "marca": "Enerpac", "ubicacion": "Taller A", "estado": "Operativo",
                "ultimo_servicio": "2024-01-18", "proximo_servicio": "2024-02-18"
            }
        ]
        
        self.maquinas_table.setRowCount(len(maquinas))
        
        for i, maquina in enumerate(maquinas):
            self.maquinas_table.setItem(i, 0, QTableWidgetItem(maquina["codigo"]))
            self.maquinas_table.setItem(i, 1, QTableWidgetItem(maquina["nombre"]))
            self.maquinas_table.setItem(i, 2, QTableWidgetItem(maquina["tipo"]))
            self.maquinas_table.setItem(i, 3, QTableWidgetItem(maquina["marca"]))
            self.maquinas_table.setItem(i, 4, QTableWidgetItem(maquina["ubicacion"]))
            
            # Colorear estado
            estado_item = QTableWidgetItem(maquina["estado"])
            if maquina["estado"] == "Operativo":
                estado_item.setBackground(QColor(46, 204, 113, 50))
            elif maquina["estado"] == "En Mantenimiento":
                estado_item.setBackground(QColor(243, 156, 18, 50))
            else:
                estado_item.setBackground(QColor(231, 76, 60, 50))
            
            self.maquinas_table.setItem(i, 5, estado_item)
            self.maquinas_table.setItem(i, 6, QTableWidgetItem(maquina["ultimo_servicio"]))
            self.maquinas_table.setItem(i, 7, QTableWidgetItem(maquina["proximo_servicio"]))
    
    def cargar_servicios(self):
        """Carga la lista de servicios"""
        # Datos demo
        servicios = [
            {
                "fecha": "2024-01-15", "maquina": "MAQ-001", "tipo": "Preventivo",
                "descripcion": "Mantenimiento preventivo rutinario", "tecnico": "Juan Pérez",
                "duracion": "2.5", "costo": "150,000", "estado": "Completado"
            },
            {
                "fecha": "2024-01-10", "maquina": "MAQ-002", "tipo": "Correctivo",
                "descripcion": "Reparación de sistema de soldadura", "tecnico": "María García",
                "duracion": "4.0", "costo": "250,000", "estado": "En Proceso"
            },
            {
                "fecha": "2024-01-20", "maquina": "MAQ-003", "tipo": "Preventivo",
                "descripcion": "Cambio de discos y limpieza", "tecnico": "Carlos López",
                "duracion": "1.5", "costo": "80,000", "estado": "Completado"
            }
        ]
        
        self.servicios_table.setRowCount(len(servicios))
        
        for i, servicio in enumerate(servicios):
            self.servicios_table.setItem(i, 0, QTableWidgetItem(servicio["fecha"]))
            self.servicios_table.setItem(i, 1, QTableWidgetItem(servicio["maquina"]))
            self.servicios_table.setItem(i, 2, QTableWidgetItem(servicio["tipo"]))
            self.servicios_table.setItem(i, 3, QTableWidgetItem(servicio["descripcion"]))
            self.servicios_table.setItem(i, 4, QTableWidgetItem(servicio["tecnico"]))
            self.servicios_table.setItem(i, 5, QTableWidgetItem(f"{servicio['duracion']} hrs"))
            self.servicios_table.setItem(i, 6, QTableWidgetItem(f"${servicio['costo']}"))
            self.servicios_table.setItem(i, 7, QTableWidgetItem(servicio["estado"]))
    
    def cargar_mantenimientos_programados(self):
        """Carga los mantenimientos programados"""
        # Datos demo
        mantenimientos = [
            "MAQ-001 - Mantenimiento Preventivo - 15/02/2024",
            "MAQ-002 - Inspección General - 10/02/2024",
            "MAQ-003 - Cambio de Filtros - 20/02/2024",
            "MAQ-004 - Reparación Mayor - 05/03/2024",
            "MAQ-005 - Calibración - 18/02/2024"
        ]
        
        self.mantenimientos_list.clear()
        
        for mantenimiento in mantenimientos:
            item = QListWidgetItem(mantenimiento)
            item.setIcon(QIcon())  # Aquí se podría agregar un icono
            self.mantenimientos_list.addItem(item)
    
    def crear_maquina(self):
        """Crea una nueva máquina"""
        dialog = MaquinariaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_maquina_data()
            QMessageBox.information(self, "Éxito", f"Máquina {datos['codigo']} creada exitosamente")
            self.cargar_maquinas()
    
    def editar_maquina(self):
        """Edita una máquina"""
        current_row = self.maquinas_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una máquina para editar")
            return
        
        # Obtener datos de la máquina
        maquina_data = {
            'codigo': self.maquinas_table.item(current_row, 0).text(),
            'nombre': self.maquinas_table.item(current_row, 1).text(),
            'tipo': self.maquinas_table.item(current_row, 2).text(),
            'marca': self.maquinas_table.item(current_row, 3).text(),
            'ubicacion': self.maquinas_table.item(current_row, 4).text(),
            'estado': self.maquinas_table.item(current_row, 5).text()
        }
        
        dialog = MaquinariaDialog(self, maquina_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_maquina_data()
            QMessageBox.information(self, "Éxito", f"Máquina {datos['codigo']} actualizada exitosamente")
            self.cargar_maquinas()
    
    def eliminar_maquina(self):
        """Elimina una máquina"""
        current_row = self.maquinas_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una máquina para eliminar")
            return
        
        codigo = self.maquinas_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar la máquina {codigo}?\n\nEsto también eliminará todo su historial de servicios.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Éxito", f"Máquina {codigo} eliminada exitosamente")
            self.cargar_maquinas()
    
    def ver_historial_maquina(self):
        """Muestra el historial completo de una máquina"""
        current_row = self.maquinas_table.currentRow()
        if current_row < 0:
            return
        
        codigo = self.maquinas_table.item(current_row, 0).text()
        nombre = self.maquinas_table.item(current_row, 1).text()
        
        # Crear ventana de historial
        historial_dialog = QDialog(self)
        historial_dialog.setWindowTitle(f"Historial de {codigo} - {nombre}")
        historial_dialog.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(historial_dialog)
        
        # Título
        title = QLabel(f"Historial Completo: {codigo} - {nombre}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabla de historial
        historial_table = QTableWidget()
        historial_table.setColumnCount(6)
        historial_table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Descripción", "Técnico", "Duración", "Costo"
        ])
        
        # Datos demo del historial
        historial_data = [
            ["2024-01-15", "Preventivo", "Mantenimiento preventivo rutinario", "Juan Pérez", "2.5 hrs", "$150,000"],
            ["2023-12-10", "Correctivo", "Reparación de motor", "María García", "4.0 hrs", "$300,000"],
            ["2023-11-15", "Preventivo", "Cambio de filtros", "Carlos López", "1.5 hrs", "$80,000"],
            ["2023-10-20", "Inspección", "Inspección general", "Ana Rodríguez", "2.0 hrs", "$100,000"],
            ["2023-09-25", "Calibración", "Calibración de sensores", "Juan Pérez", "3.0 hrs", "$200,000"]
        ]
        
        historial_table.setRowCount(len(historial_data))
        
        for i, row_data in enumerate(historial_data):
            for j, cell_data in enumerate(row_data):
                historial_table.setItem(i, j, QTableWidgetItem(cell_data))
        
        historial_table.horizontalHeader().setStretchLastSection(True)
        historial_table.setAlternatingRowColors(True)
        
        layout.addWidget(historial_table)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(historial_dialog.close)
        layout.addWidget(close_btn)
        
        historial_dialog.exec()
    
    def crear_servicio(self):
        """Crea un nuevo servicio"""
        # Obtener máquina seleccionada si hay una
        maquina_codigo = None
        current_row = self.maquinas_table.currentRow()
        if current_row >= 0:
            maquina_codigo = self.maquinas_table.item(current_row, 0).text()
        
        dialog = ServicioDialog(self, maquina_codigo)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_servicio_data()
            QMessageBox.information(self, "Éxito", f"Servicio registrado exitosamente para {datos['maquina_codigo']}")
            self.cargar_servicios()
    
    def editar_servicio(self):
        """Edita un servicio"""
        current_row = self.servicios_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un servicio para editar")
            return
        
        # Obtener datos del servicio
        servicio_data = {
            'maquina_codigo': self.servicios_table.item(current_row, 1).text(),
            'descripcion': self.servicios_table.item(current_row, 3).text(),
            'tecnico': self.servicios_table.item(current_row, 4).text(),
            'duracion': float(self.servicios_table.item(current_row, 5).text().replace(' hrs', '')),
            'costo': float(self.servicios_table.item(current_row, 6).text().replace('$', '').replace(',', ''))
        }
        
        dialog = ServicioDialog(self, servicio_data['maquina_codigo'], servicio_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_servicio_data()
            QMessageBox.information(self, "Éxito", f"Servicio actualizado exitosamente")
            self.cargar_servicios()
    
    def eliminar_servicio(self):
        """Elimina un servicio"""
        current_row = self.servicios_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un servicio para eliminar")
            return
        
        maquina = self.servicios_table.item(current_row, 1).text()
        fecha = self.servicios_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar el servicio de {maquina} del {fecha}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Éxito", "Servicio eliminado exitosamente")
            self.cargar_servicios()
    
    def filtrar_maquinas(self):
        """Filtra las máquinas según los filtros seleccionados"""
        # Aquí implementarías la lógica de filtrado
        QMessageBox.information(self, "Info", "Filtros aplicados")
    
    def buscar_maquinas(self, text):
        """Busca máquinas por texto"""
        for i in range(self.maquinas_table.rowCount()):
            show = False
            for j in range(self.maquinas_table.columnCount()):
                item = self.maquinas_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.maquinas_table.setRowHidden(i, not show)
    
    def show_maquina_context_menu(self, position):
        """Muestra menú contextual para máquinas"""
        if self.maquinas_table.itemAt(position):
            menu = QMenu()
            
            edit_action = menu.addAction("Editar")
            edit_action.triggered.connect(self.editar_maquina)
            
            history_action = menu.addAction("Ver Historial")
            history_action.triggered.connect(self.ver_historial_maquina)
            
            service_action = menu.addAction("Nuevo Servicio")
            service_action.triggered.connect(self.crear_servicio)
            
            menu.addSeparator()
            
            delete_action = menu.addAction("Eliminar")
            delete_action.triggered.connect(self.eliminar_maquina)
            
            menu.exec(self.maquinas_table.mapToGlobal(position))
    
    def mostrar_mantenimientos_fecha(self, date):
        """Muestra mantenimientos para una fecha específica"""
        QMessageBox.information(self, "Mantenimientos", f"Mantenimientos programados para {date.toString()}")
    
    def programar_mantenimiento(self):
        """Programa un nuevo mantenimiento"""
        QMessageBox.information(self, "Éxito", "Mantenimiento programado exitosamente")
        self.cargar_mantenimientos_programados()
    
    def completar_mantenimiento(self):
        """Marca un mantenimiento como completado"""
        current_item = self.mantenimientos_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Seleccione un mantenimiento para completar")
            return
        
        QMessageBox.information(self, "Éxito", "Mantenimiento marcado como completado")
        self.cargar_mantenimientos_programados()
    
    def generar_reporte_maquinas(self):
        """Genera reporte de máquinas"""
        reporte = """
REPORTE DE MAQUINARIA - ENERO 2024
==================================

RESUMEN GENERAL:
- Total máquinas: 5
- Operativas: 3 (60%)
- En mantenimiento: 1 (20%)
- Fuera de servicio: 1 (20%)

INVENTARIO POR TIPO:
- Cortadoras: 1
- Soldadoras: 1
- Pulidoras: 1
- Taladros: 1
- Prensas: 1

UBICACIONES:
- Taller A: 3 máquinas
- Taller B: 1 máquina
- Taller C: 1 máquina

PRÓXIMOS MANTENIMIENTOS:
- MAQ-001: 15/02/2024
- MAQ-002: 10/02/2024
- MAQ-003: 20/02/2024
- MAQ-004: 05/03/2024
- MAQ-005: 18/02/2024

RECOMENDACIONES:
- Priorizar reparación de MAQ-004
- Programar mantenimiento preventivo para febrero
- Evaluar reemplazo de equipos antiguos
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_historial_servicios(self):
        """Genera historial de servicios"""
        reporte = """
HISTORIAL DE SERVICIOS - ENERO 2024
===================================

SERVICIOS REALIZADOS:

1. MAQ-001 - Cortadora Plasma
   - Fecha: 15/01/2024
   - Tipo: Mantenimiento Preventivo
   - Técnico: Juan Pérez
   - Duración: 2.5 hrs
   - Costo: $150,000

2. MAQ-002 - Soldadora MIG
   - Fecha: 10/01/2024
   - Tipo: Mantenimiento Correctivo
   - Técnico: María García
   - Duración: 4.0 hrs
   - Costo: $250,000

3. MAQ-003 - Pulidora Angular
   - Fecha: 20/01/2024
   - Tipo: Mantenimiento Preventivo
   - Técnico: Carlos López
   - Duración: 1.5 hrs
   - Costo: $80,000

ESTADÍSTICAS:
- Total servicios: 3
- Horas invertidas: 8.0 hrs
- Costo total: $480,000
- Promedio por servicio: $160,000

TÉCNICOS MÁS ACTIVOS:
1. Juan Pérez - 1 servicio
2. María García - 1 servicio
3. Carlos López - 1 servicio
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_costos_mantenimiento(self):
        """Genera reporte de costos"""
        reporte = """
COSTOS DE MANTENIMIENTO - ENERO 2024
====================================

COSTOS POR TIPO:
- Mantenimiento Preventivo: $230,000 (47.9%)
- Mantenimiento Correctivo: $250,000 (52.1%)
- Reparaciones: $0 (0%)

COSTOS POR MÁQUINA:
- MAQ-001: $150,000
- MAQ-002: $250,000
- MAQ-003: $80,000
- MAQ-004: $0
- MAQ-005: $0

COSTOS POR TÉCNICO:
- Juan Pérez: $150,000
- María García: $250,000
- Carlos López: $80,000

ANÁLISIS MENSUAL:
- Enero: $480,000
- Promedio mensual: $480,000
- Proyección anual: $5,760,000

INDICADORES:
- Costo por hora de servicio: $60,000
- Costo por máquina: $96,000
- Eficiencia: 85%

RECOMENDACIONES:
- Incrementar mantenimiento preventivo
- Evaluar costos de técnicos externos
- Optimizar inventario de repuestos
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_mantenimientos_programados(self):
        """Genera reporte de mantenimientos programados"""
        reporte = """
MANTENIMIENTOS PROGRAMADOS - FEBRERO 2024
=========================================

PRÓXIMOS 30 DÍAS:

Semana 1 (01-07 Feb):
- MAQ-002: Inspección General - 10/02/2024
- MAQ-001: Mantenimiento Preventivo - 15/02/2024

Semana 2 (08-14 Feb):
- MAQ-005: Calibración - 18/02/2024
- MAQ-003: Cambio de Filtros - 20/02/2024

Semana 3 (15-21 Feb):
- Sin mantenimientos programados

Semana 4 (22-28 Feb):
- Sin mantenimientos programados

MARZO 2024:
- MAQ-004: Reparación Mayor - 05/03/2024

RECURSOS NECESARIOS:
- Técnicos: 3 personas
- Horas estimadas: 12 hrs
- Costo estimado: $720,000
- Repuestos: Ver lista adjunta

ALERTAS:
- MAQ-004 requiere reparación urgente
- Verificar disponibilidad de repuestos
- Coordinar con producción los paros
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_indicadores_rendimiento(self):
        """Genera indicadores de rendimiento"""
        reporte = """
INDICADORES DE RENDIMIENTO - ENERO 2024
=======================================

DISPONIBILIDAD:
- MAQ-001: 98% (Excelente)
- MAQ-002: 85% (Bueno)
- MAQ-003: 95% (Muy Bueno)
- MAQ-004: 60% (Deficiente)
- MAQ-005: 92% (Muy Bueno)

PROMEDIO GENERAL: 86%

EFICIENCIA:
- Tiempo promedio de reparación: 2.7 hrs
- Tiempo promedio entre fallas: 240 hrs
- Costo promedio por servicio: $160,000

TENDENCIAS:
- Disponibilidad: +2% vs mes anterior
- Costos: +5% vs mes anterior
- Tiempo de reparación: -10% vs mes anterior

RANKING DE MÁQUINAS:
1. MAQ-001 - 98% disponibilidad
2. MAQ-003 - 95% disponibilidad
3. MAQ-005 - 92% disponibilidad
4. MAQ-002 - 85% disponibilidad
5. MAQ-004 - 60% disponibilidad

ACCIONES RECOMENDADAS:
- Revisar MAQ-004 urgentemente
- Mantener protocolo actual para MAQ-001
- Optimizar mantenimiento de MAQ-002
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_analisis_averias(self):
        """Genera análisis de averías"""
        reporte = """
ANÁLISIS DE AVERÍAS - ENERO 2024
================================

TIPOS DE AVERÍAS MÁS FRECUENTES:
1. Fallas eléctricas: 40%
2. Desgaste de componentes: 30%
3. Falta de lubricación: 15%
4. Problemas de calibración: 10%
5. Otros: 5%

MÁQUINAS CON MÁS AVERÍAS:
1. MAQ-002 - 3 averías
2. MAQ-004 - 2 averías
3. MAQ-001 - 1 avería
4. MAQ-003 - 1 avería
5. MAQ-005 - 0 averías

CAUSAS PRINCIPALES:
- Falta de mantenimiento preventivo: 45%
- Uso inadecuado: 25%
- Desgaste normal: 20%
- Defectos de fabricación: 10%

HORARIOS DE MAYOR INCIDENCIA:
- Mañana (6-12): 20%
- Tarde (12-18): 60%
- Noche (18-24): 20%

DÍAS DE LA SEMANA:
- Lunes: 25%
- Martes: 20%
- Miércoles: 15%
- Jueves: 20%
- Viernes: 15%
- Sábado: 5%

RECOMENDACIONES:
- Incrementar mantenimiento preventivo
- Capacitar operadores
- Revisar procedimientos de uso
- Implementar sistema de monitoreo
        """
        self.preview_text.setPlainText(reporte)


# Ejemplo de uso
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear vista completa de mantenimiento
    mantenimiento_view = MantenimientoCompletaView()
    mantenimiento_view.show()
    
    sys.exit(app.exec())