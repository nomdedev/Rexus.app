"""
Vista Completa de Administración - Rexus.app v2.0.0

Interfaz completa para gestión administrativa con pestañas separadas
para contabilidad y recursos humanos
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QTextEdit, QFrame, QHeaderView,
    QAbstractItemView, QMenu, QApplication, QScrollArea, QGridLayout,
    QDateEdit, QProgressBar, QSplitter, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap

from src.core.database import InventarioDatabaseConnection


class EmpleadoDialog(QDialog):
    """Diálogo para crear/editar empleados"""
    
    def __init__(self, parent=None, empleado_data=None):
        super().__init__(parent)
        self.empleado_data = empleado_data
        self.setWindowTitle("Nuevo Empleado" if not empleado_data else "Editar Empleado")
        self.setFixedSize(600, 700)
        self.init_ui()
        
        if empleado_data:
            self.load_empleado_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Nuevo Empleado" if not self.empleado_data else "Editar Empleado")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Datos personales
        personal_group = QGroupBox("Datos Personales")
        personal_layout = QFormLayout(personal_group)
        
        self.nombre_edit = QLineEdit()
        personal_layout.addRow("Nombre*:", self.nombre_edit)
        
        self.apellido_edit = QLineEdit()
        personal_layout.addRow("Apellido*:", self.apellido_edit)
        
        self.cedula_edit = QLineEdit()
        personal_layout.addRow("Cédula*:", self.cedula_edit)
        
        self.email_edit = QLineEdit()
        personal_layout.addRow("Email:", self.email_edit)
        
        self.telefono_edit = QLineEdit()
        personal_layout.addRow("Teléfono:", self.telefono_edit)
        
        self.direccion_edit = QLineEdit()
        personal_layout.addRow("Dirección:", self.direccion_edit)
        
        self.fecha_nacimiento = QDateEdit()
        self.fecha_nacimiento.setDate(QDate.currentDate().addYears(-25))
        self.fecha_nacimiento.setCalendarPopup(True)
        personal_layout.addRow("Fecha Nacimiento:", self.fecha_nacimiento)
        
        scroll_layout.addWidget(personal_group)
        
        # Datos laborales
        laboral_group = QGroupBox("Datos Laborales")
        laboral_layout = QFormLayout(laboral_group)
        
        self.cargo_edit = QLineEdit()
        laboral_layout.addRow("Cargo*:", self.cargo_edit)
        
        self.departamento_combo = QComboBox()
        self.departamento_combo.addItems([
            "Administración", "Producción", "Ventas", "Contabilidad", 
            "Recursos Humanos", "Mantenimiento", "Logística"
        ])
        laboral_layout.addRow("Departamento:", self.departamento_combo)
        
        self.fecha_ingreso = QDateEdit()
        self.fecha_ingreso.setDate(QDate.currentDate())
        self.fecha_ingreso.setCalendarPopup(True)
        laboral_layout.addRow("Fecha Ingreso:", self.fecha_ingreso)
        
        self.salario_spin = QDoubleSpinBox()
        self.salario_spin.setRange(0, 99999999.99)
        self.salario_spin.setDecimals(2)
        self.salario_spin.setSuffix(" $")
        laboral_layout.addRow("Salario Base:", self.salario_spin)
        
        self.tipo_contrato_combo = QComboBox()
        self.tipo_contrato_combo.addItems([
            "Indefinido", "Fijo", "Temporal", "Prestación de Servicios"
        ])
        laboral_layout.addRow("Tipo Contrato:", self.tipo_contrato_combo)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Activo", "Inactivo", "Vacaciones", "Incapacidad"])
        laboral_layout.addRow("Estado:", self.estado_combo)
        
        scroll_layout.addWidget(laboral_group)
        
        # Observaciones
        obs_group = QGroupBox("Observaciones")
        obs_layout = QVBoxLayout(obs_group)
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setMaximumHeight(80)
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
    
    def load_empleado_data(self):
        """Carga los datos del empleado"""
        if not self.empleado_data:
            return
            
        self.nombre_edit.setText(self.empleado_data.get('nombre', ''))
        self.apellido_edit.setText(self.empleado_data.get('apellido', ''))
        self.cedula_edit.setText(self.empleado_data.get('cedula', ''))
        self.email_edit.setText(self.empleado_data.get('email', ''))
        self.telefono_edit.setText(self.empleado_data.get('telefono', ''))
        self.direccion_edit.setText(self.empleado_data.get('direccion', ''))
        self.cargo_edit.setText(self.empleado_data.get('cargo', ''))
        self.salario_spin.setValue(self.empleado_data.get('salario', 0.0))
        self.observaciones_text.setText(self.empleado_data.get('observaciones', ''))
    
    def get_empleado_data(self):
        """Obtiene los datos del formulario"""
        return {
            'nombre': self.nombre_edit.text().strip(),
            'apellido': self.apellido_edit.text().strip(),
            'cedula': self.cedula_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'telefono': self.telefono_edit.text().strip(),
            'direccion': self.direccion_edit.text().strip(),
            'fecha_nacimiento': self.fecha_nacimiento.date().toPython(),
            'cargo': self.cargo_edit.text().strip(),
            'departamento': self.departamento_combo.currentText(),
            'fecha_ingreso': self.fecha_ingreso.date().toPython(),
            'salario': self.salario_spin.value(),
            'tipo_contrato': self.tipo_contrato_combo.currentText(),
            'estado': self.estado_combo.currentText(),
            'observaciones': self.observaciones_text.toPlainText()
        }
    
    def validate_form(self):
        """Valida el formulario"""
        if not self.nombre_edit.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return False
        
        if not self.apellido_edit.text().strip():
            QMessageBox.warning(self, "Error", "El apellido es requerido")
            return False
        
        if not self.cedula_edit.text().strip():
            QMessageBox.warning(self, "Error", "La cédula es requerida")
            return False
        
        if not self.cargo_edit.text().strip():
            QMessageBox.warning(self, "Error", "El cargo es requerido")
            return False
        
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class TransaccionDialog(QDialog):
    """Diálogo para crear/editar transacciones contables"""
    
    def __init__(self, parent=None, transaccion_data=None):
        super().__init__(parent)
        self.transaccion_data = transaccion_data
        self.setWindowTitle("Nueva Transacción" if not transaccion_data else "Editar Transacción")
        self.setFixedSize(500, 400)
        self.init_ui()
        
        if transaccion_data:
            self.load_transaccion_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Nueva Transacción" if not self.transaccion_data else "Editar Transacción")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulario
        form_group = QGroupBox("Datos de la Transacción")
        form_layout = QFormLayout(form_group)
        
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        form_layout.addRow("Fecha*:", self.fecha_edit)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Ingreso", "Egreso", "Transferencia"])
        form_layout.addRow("Tipo*:", self.tipo_combo)
        
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems([
            "Ventas", "Compras", "Gastos Operativos", "Nómina", 
            "Servicios", "Impuestos", "Otros"
        ])
        form_layout.addRow("Categoría*:", self.categoria_combo)
        
        self.concepto_edit = QLineEdit()
        form_layout.addRow("Concepto*:", self.concepto_edit)
        
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setRange(0.01, 99999999.99)
        self.valor_spin.setDecimals(2)
        self.valor_spin.setSuffix(" $")
        form_layout.addRow("Valor*:", self.valor_spin)
        
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.addItems([
            "Caja", "Banco Corriente", "Banco Ahorros", "Tarjeta Crédito"
        ])
        form_layout.addRow("Cuenta:", self.cuenta_combo)
        
        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setMaximumHeight(80)
        form_layout.addRow("Descripción:", self.descripcion_edit)
        
        layout.addWidget(form_group)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_transaccion_data(self):
        """Carga los datos de la transacción"""
        if not self.transaccion_data:
            return
            
        self.concepto_edit.setText(self.transaccion_data.get('concepto', ''))
        self.valor_spin.setValue(self.transaccion_data.get('valor', 0.0))
        self.descripcion_edit.setText(self.transaccion_data.get('descripcion', ''))
    
    def get_transaccion_data(self):
        """Obtiene los datos del formulario"""
        return {
            'fecha': self.fecha_edit.date().toPython(),
            'tipo': self.tipo_combo.currentText(),
            'categoria': self.categoria_combo.currentText(),
            'concepto': self.concepto_edit.text().strip(),
            'valor': self.valor_spin.value(),
            'cuenta': self.cuenta_combo.currentText(),
            'descripcion': self.descripcion_edit.toPlainText()
        }
    
    def validate_form(self):
        """Valida el formulario"""
        if not self.concepto_edit.text().strip():
            QMessageBox.warning(self, "Error", "El concepto es requerido")
            return False
        
        if self.valor_spin.value() <= 0:
            QMessageBox.warning(self, "Error", "El valor debe ser mayor a 0")
            return False
        
        return True
    
    def accept(self):
        if self.validate_form():
            super().accept()


class AdministracionCompletaView(QWidget):
    """Vista completa de administración con pestañas separadas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        
        # Título con height reducido
        title = QLabel("💼 Administración Integral")
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
        
        # Tab 1: Recursos Humanos
        rrhh_tab = self.create_rrhh_tab()
        tabs.addTab(rrhh_tab, "👥 Recursos Humanos")
        
        # Tab 2: Contabilidad
        contabilidad_tab = self.create_contabilidad_tab()
        tabs.addTab(contabilidad_tab, "💰 Contabilidad")
        
        # Tab 3: Reportes
        reportes_tab = self.create_reportes_tab()
        tabs.addTab(reportes_tab, "📊 Reportes")
        
        layout.addWidget(tabs)
    
    def create_rrhh_tab(self):
        """Crea la pestaña de recursos humanos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Subtabs para RRHH
        rrhh_tabs = QTabWidget()
        
        # Empleados
        empleados_tab = self.create_empleados_tab()
        rrhh_tabs.addTab(empleados_tab, "Empleados")
        
        # Nómina
        nomina_tab = self.create_nomina_tab()
        rrhh_tabs.addTab(nomina_tab, "Nómina")
        
        # Asistencia
        asistencia_tab = self.create_asistencia_tab()
        rrhh_tabs.addTab(asistencia_tab, "Asistencia")
        
        # Vacaciones
        vacaciones_tab = self.create_vacaciones_tab()
        rrhh_tabs.addTab(vacaciones_tab, "Vacaciones")
        
        layout.addWidget(rrhh_tabs)
        return tab
    
    def create_empleados_tab(self):
        """Crea la pestaña de empleados"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        nuevo_btn = QPushButton("Nuevo Empleado")
        nuevo_btn.clicked.connect(self.crear_empleado)
        toolbar.addWidget(nuevo_btn)
        
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(self.editar_empleado)
        toolbar.addWidget(editar_btn)
        
        eliminar_btn = QPushButton("Eliminar")
        eliminar_btn.clicked.connect(self.eliminar_empleado)
        toolbar.addWidget(eliminar_btn)
        
        toolbar.addStretch()
        
        # Búsqueda
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Buscar empleado...")
        toolbar.addWidget(search_edit)
        
        layout.addLayout(toolbar)
        
        # Tabla de empleados
        self.empleados_table = QTableWidget()
        self.empleados_table.setColumnCount(8)
        self.empleados_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Cédula", "Cargo", 
            "Departamento", "Salario", "Estado"
        ])
        
        # Configurar tabla
        header = self.empleados_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.empleados_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.empleados_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.empleados_table)
        
        return tab
    
    def create_nomina_tab(self):
        """Crea la pestaña de nómina"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Período de nómina
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("Período:"))
        
        periodo_combo = QComboBox()
        periodo_combo.addItems([
            "Enero 2024", "Febrero 2024", "Marzo 2024", "Abril 2024"
        ])
        periodo_layout.addWidget(periodo_combo)
        
        procesar_btn = QPushButton("Procesar Nómina")
        procesar_btn.clicked.connect(self.procesar_nomina)
        periodo_layout.addWidget(procesar_btn)
        
        generar_btn = QPushButton("Generar Desprendibles")
        generar_btn.clicked.connect(self.generar_desprendibles)
        periodo_layout.addWidget(generar_btn)
        
        periodo_layout.addStretch()
        layout.addLayout(periodo_layout)
        
        # Tabla de nómina
        self.nomina_table = QTableWidget()
        self.nomina_table.setColumnCount(8)
        self.nomina_table.setHorizontalHeaderLabels([
            "Empleado", "Salario Base", "Bonificaciones", "Deducciones", 
            "Seguridad Social", "Retenciones", "Neto a Pagar", "Estado"
        ])
        
        # Configurar tabla
        header = self.nomina_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.nomina_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.nomina_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.nomina_table)
        
        return tab
    
    def create_asistencia_tab(self):
        """Crea la pestaña de asistencia"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controles de fecha
        fecha_layout = QHBoxLayout()
        fecha_layout.addWidget(QLabel("Fecha:"))
        
        fecha_edit = QDateEdit()
        fecha_edit.setDate(QDate.currentDate())
        fecha_edit.setCalendarPopup(True)
        fecha_layout.addWidget(fecha_edit)
        
        registrar_btn = QPushButton("Registrar Asistencia")
        registrar_btn.clicked.connect(self.registrar_asistencia)
        fecha_layout.addWidget(registrar_btn)
        
        fecha_layout.addStretch()
        layout.addLayout(fecha_layout)
        
        # Tabla de asistencia
        self.asistencia_table = QTableWidget()
        self.asistencia_table.setColumnCount(6)
        self.asistencia_table.setHorizontalHeaderLabels([
            "Empleado", "Fecha", "Hora Entrada", "Hora Salida", 
            "Horas Trabajadas", "Observaciones"
        ])
        
        # Configurar tabla
        header = self.asistencia_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.asistencia_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.asistencia_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.asistencia_table)
        
        return tab
    
    def create_vacaciones_tab(self):
        """Crea la pestaña de vacaciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        solicitar_btn = QPushButton("Solicitar Vacaciones")
        solicitar_btn.clicked.connect(self.solicitar_vacaciones)
        toolbar.addWidget(solicitar_btn)
        
        aprobar_btn = QPushButton("Aprobar")
        aprobar_btn.clicked.connect(self.aprobar_vacaciones)
        toolbar.addWidget(aprobar_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Tabla de vacaciones
        self.vacaciones_table = QTableWidget()
        self.vacaciones_table.setColumnCount(6)
        self.vacaciones_table.setHorizontalHeaderLabels([
            "Empleado", "Fecha Inicio", "Fecha Fin", "Días", 
            "Estado", "Observaciones"
        ])
        
        # Configurar tabla
        header = self.vacaciones_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.vacaciones_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vacaciones_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.vacaciones_table)
        
        return tab
    
    def create_contabilidad_tab(self):
        """Crea la pestaña de contabilidad"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Subtabs para contabilidad
        conta_tabs = QTabWidget()
        
        # Transacciones
        transacciones_tab = self.create_transacciones_tab()
        conta_tabs.addTab(transacciones_tab, "Transacciones")
        
        # Cuentas por cobrar
        cxc_tab = self.create_cuentas_cobrar_tab()
        conta_tabs.addTab(cxc_tab, "Cuentas por Cobrar")
        
        # Cuentas por pagar
        cxp_tab = self.create_cuentas_pagar_tab()
        conta_tabs.addTab(cxp_tab, "Cuentas por Pagar")
        
        # Balance
        balance_tab = self.create_balance_tab()
        conta_tabs.addTab(balance_tab, "Balance General")
        
        layout.addWidget(conta_tabs)
        return tab
    
    def create_transacciones_tab(self):
        """Crea la pestaña de transacciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        nueva_btn = QPushButton("Nueva Transacción")
        nueva_btn.clicked.connect(self.crear_transaccion)
        toolbar.addWidget(nueva_btn)
        
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(self.editar_transaccion)
        toolbar.addWidget(editar_btn)
        
        eliminar_btn = QPushButton("Eliminar")
        eliminar_btn.clicked.connect(self.eliminar_transaccion)
        toolbar.addWidget(eliminar_btn)
        
        toolbar.addStretch()
        
        # Filtros
        filtro_combo = QComboBox()
        filtro_combo.addItems(["Todas", "Ingresos", "Egresos"])
        toolbar.addWidget(filtro_combo)
        
        layout.addLayout(toolbar)
        
        # Tabla de transacciones
        self.transacciones_table = QTableWidget()
        self.transacciones_table.setColumnCount(7)
        self.transacciones_table.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Concepto", "Valor", "Cuenta", "Estado"
        ])
        
        # Configurar tabla
        header = self.transacciones_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.transacciones_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.transacciones_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.transacciones_table)
        
        return tab
    
    def create_cuentas_cobrar_tab(self):
        """Crea la pestaña de cuentas por cobrar"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Resumen
        resumen_layout = QHBoxLayout()
        
        # Cards de resumen
        cards = [
            ("Total por Cobrar", "$125,000", "#e74c3c"),
            ("Vencidas", "$25,000", "#f39c12"),
            ("Por Vencer", "$100,000", "#2ecc71")
        ]
        
        for titulo, valor, color in cards:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: 500;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(valor)
            value_label.setStyleSheet(f"font-size: 18px; color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            resumen_layout.addWidget(card)
        
        layout.addLayout(resumen_layout)
        
        # Tabla de cuentas por cobrar
        self.cxc_table = QTableWidget()
        self.cxc_table.setColumnCount(6)
        self.cxc_table.setHorizontalHeaderLabels([
            "Cliente", "Factura", "Fecha", "Vencimiento", "Valor", "Estado"
        ])
        
        # Configurar tabla
        header = self.cxc_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.cxc_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cxc_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.cxc_table)
        
        return tab
    
    def create_cuentas_pagar_tab(self):
        """Crea la pestaña de cuentas por pagar"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Resumen
        resumen_layout = QHBoxLayout()
        
        # Cards de resumen
        cards = [
            ("Total por Pagar", "$85,000", "#3498db"),
            ("Vencidas", "$15,000", "#e74c3c"),
            ("Por Vencer", "$70,000", "#f39c12")
        ]
        
        for titulo, valor, color in cards:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: 500;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(valor)
            value_label.setStyleSheet(f"font-size: 18px; color: {color}; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            resumen_layout.addWidget(card)
        
        layout.addLayout(resumen_layout)
        
        # Tabla de cuentas por pagar
        self.cxp_table = QTableWidget()
        self.cxp_table.setColumnCount(6)
        self.cxp_table.setHorizontalHeaderLabels([
            "Proveedor", "Factura", "Fecha", "Vencimiento", "Valor", "Estado"
        ])
        
        # Configurar tabla
        header = self.cxp_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.cxp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cxp_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.cxp_table)
        
        return tab
    
    def create_balance_tab(self):
        """Crea la pestaña de balance general"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Período
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("Período:"))
        
        periodo_combo = QComboBox()
        periodo_combo.addItems([
            "Enero 2024", "Febrero 2024", "Marzo 2024", "Abril 2024"
        ])
        periodo_layout.addWidget(periodo_combo)
        
        generar_btn = QPushButton("Generar Balance")
        generar_btn.clicked.connect(self.generar_balance)
        periodo_layout.addWidget(generar_btn)
        
        periodo_layout.addStretch()
        layout.addLayout(periodo_layout)
        
        # Splitter para activos y pasivos
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Activos
        activos_group = QGroupBox("ACTIVOS")
        activos_layout = QVBoxLayout(activos_group)
        
        self.activos_table = QTableWidget()
        self.activos_table.setColumnCount(2)
        self.activos_table.setHorizontalHeaderLabels(["Cuenta", "Valor"])
        activos_layout.addWidget(self.activos_table)
        
        splitter.addWidget(activos_group)
        
        # Pasivos y patrimonio
        pasivos_group = QGroupBox("PASIVOS Y PATRIMONIO")
        pasivos_layout = QVBoxLayout(pasivos_group)
        
        self.pasivos_table = QTableWidget()
        self.pasivos_table.setColumnCount(2)
        self.pasivos_table.setHorizontalHeaderLabels(["Cuenta", "Valor"])
        pasivos_layout.addWidget(self.pasivos_table)
        
        splitter.addWidget(pasivos_group)
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_reportes_tab(self):
        """Crea la pestaña de reportes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Reportes Administrativos")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Botones de reportes
        reports_layout = QGridLayout()
        
        reports = [
            ("📊 Reporte de Nómina", self.generar_reporte_nomina),
            ("📈 Estado de Resultados", self.generar_estado_resultados),
            ("📋 Listado de Empleados", self.generar_listado_empleados),
            ("💰 Flujo de Efectivo", self.generar_flujo_efectivo),
            ("📊 Análisis de Cuentas", self.generar_analisis_cuentas),
            ("📈 Indicadores Financieros", self.generar_indicadores)
        ]
        
        for i, (nombre, funcion) in enumerate(reports):
            btn = QPushButton(nombre)
            btn.clicked.connect(funcion)
            btn.setMinimumHeight(40)
            reports_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(reports_layout)
        
        # Área de vista previa
        preview_group = QGroupBox("Vista Previa")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Seleccione un reporte para generar vista previa...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        return tab
    
    def load_data(self):
        """Carga todos los datos"""
        self.cargar_empleados()
        self.cargar_transacciones()
        self.cargar_cuentas_cobrar()
        self.cargar_cuentas_pagar()
        self.cargar_nomina()
        self.cargar_asistencia()
        self.cargar_vacaciones()
        self.cargar_balance()
    
    def cargar_empleados(self):
        """Carga la lista de empleados"""
        # Datos demo
        empleados = [
            {"id": 1, "nombre": "Juan", "apellido": "Pérez", "cedula": "12345678", 
             "cargo": "Supervisor", "departamento": "Producción", "salario": 2500000, "estado": "Activo"},
            {"id": 2, "nombre": "María", "apellido": "García", "cedula": "87654321", 
             "cargo": "Contador", "departamento": "Contabilidad", "salario": 2200000, "estado": "Activo"},
            {"id": 3, "nombre": "Carlos", "apellido": "Rodríguez", "cedula": "11223344", 
             "cargo": "Técnico", "departamento": "Mantenimiento", "salario": 1800000, "estado": "Activo"}
        ]
        
        self.empleados_table.setRowCount(len(empleados))
        
        for i, empleado in enumerate(empleados):
            self.empleados_table.setItem(i, 0, QTableWidgetItem(str(empleado["id"])))
            self.empleados_table.setItem(i, 1, QTableWidgetItem(empleado["nombre"]))
            self.empleados_table.setItem(i, 2, QTableWidgetItem(empleado["apellido"]))
            self.empleados_table.setItem(i, 3, QTableWidgetItem(empleado["cedula"]))
            self.empleados_table.setItem(i, 4, QTableWidgetItem(empleado["cargo"]))
            self.empleados_table.setItem(i, 5, QTableWidgetItem(empleado["departamento"]))
            self.empleados_table.setItem(i, 6, QTableWidgetItem(f"${empleado['salario']:,}"))
            self.empleados_table.setItem(i, 7, QTableWidgetItem(empleado["estado"]))
    
    def cargar_transacciones(self):
        """Carga las transacciones"""
        # Datos demo
        transacciones = [
            {"id": 1, "fecha": "2024-01-15", "tipo": "Ingreso", "concepto": "Venta de productos", 
             "valor": 1500000, "cuenta": "Caja", "estado": "Completado"},
            {"id": 2, "fecha": "2024-01-16", "tipo": "Egreso", "concepto": "Pago nómina", 
             "valor": 500000, "cuenta": "Banco Corriente", "estado": "Completado"},
            {"id": 3, "fecha": "2024-01-17", "tipo": "Egreso", "concepto": "Compra materiales", 
             "valor": 300000, "cuenta": "Banco Corriente", "estado": "Pendiente"}
        ]
        
        self.transacciones_table.setRowCount(len(transacciones))
        
        for i, trans in enumerate(transacciones):
            self.transacciones_table.setItem(i, 0, QTableWidgetItem(str(trans["id"])))
            self.transacciones_table.setItem(i, 1, QTableWidgetItem(trans["fecha"]))
            self.transacciones_table.setItem(i, 2, QTableWidgetItem(trans["tipo"]))
            self.transacciones_table.setItem(i, 3, QTableWidgetItem(trans["concepto"]))
            self.transacciones_table.setItem(i, 4, QTableWidgetItem(f"${trans['valor']:,}"))
            self.transacciones_table.setItem(i, 5, QTableWidgetItem(trans["cuenta"]))
            self.transacciones_table.setItem(i, 6, QTableWidgetItem(trans["estado"]))
    
    def cargar_cuentas_cobrar(self):
        """Carga las cuentas por cobrar"""
        # Datos demo
        cuentas = [
            {"cliente": "Constructora ABC", "factura": "FAC-001", "fecha": "2024-01-10", 
             "vencimiento": "2024-02-10", "valor": 50000, "estado": "Pendiente"},
            {"cliente": "Inmobiliaria XYZ", "factura": "FAC-002", "fecha": "2024-01-15", 
             "vencimiento": "2024-02-15", "valor": 75000, "estado": "Vencida"}
        ]
        
        self.cxc_table.setRowCount(len(cuentas))
        
        for i, cuenta in enumerate(cuentas):
            self.cxc_table.setItem(i, 0, QTableWidgetItem(cuenta["cliente"]))
            self.cxc_table.setItem(i, 1, QTableWidgetItem(cuenta["factura"]))
            self.cxc_table.setItem(i, 2, QTableWidgetItem(cuenta["fecha"]))
            self.cxc_table.setItem(i, 3, QTableWidgetItem(cuenta["vencimiento"]))
            self.cxc_table.setItem(i, 4, QTableWidgetItem(f"${cuenta['valor']:,}"))
            self.cxc_table.setItem(i, 5, QTableWidgetItem(cuenta["estado"]))
    
    def cargar_cuentas_pagar(self):
        """Carga las cuentas por pagar"""
        # Datos demo
        cuentas = [
            {"proveedor": "Proveedor A", "factura": "FAC-P001", "fecha": "2024-01-12", 
             "vencimiento": "2024-02-12", "valor": 30000, "estado": "Pendiente"},
            {"proveedor": "Proveedor B", "factura": "FAC-P002", "fecha": "2024-01-18", 
             "vencimiento": "2024-02-18", "valor": 55000, "estado": "Pendiente"}
        ]
        
        self.cxp_table.setRowCount(len(cuentas))
        
        for i, cuenta in enumerate(cuentas):
            self.cxp_table.setItem(i, 0, QTableWidgetItem(cuenta["proveedor"]))
            self.cxp_table.setItem(i, 1, QTableWidgetItem(cuenta["factura"]))
            self.cxp_table.setItem(i, 2, QTableWidgetItem(cuenta["fecha"]))
            self.cxp_table.setItem(i, 3, QTableWidgetItem(cuenta["vencimiento"]))
            self.cxp_table.setItem(i, 4, QTableWidgetItem(f"${cuenta['valor']:,}"))
            self.cxp_table.setItem(i, 5, QTableWidgetItem(cuenta["estado"]))
    
    def cargar_nomina(self):
        """Carga la nómina"""
        # Datos demo
        nomina = [
            {"empleado": "Juan Pérez", "salario": 2500000, "bonif": 200000, "deduc": 150000, 
             "ss": 200000, "ret": 300000, "neto": 2050000, "estado": "Procesado"},
            {"empleado": "María García", "salario": 2200000, "bonif": 100000, "deduc": 100000, 
             "ss": 176000, "ret": 250000, "neto": 1774000, "estado": "Procesado"}
        ]
        
        self.nomina_table.setRowCount(len(nomina))
        
        for i, nom in enumerate(nomina):
            self.nomina_table.setItem(i, 0, QTableWidgetItem(nom["empleado"]))
            self.nomina_table.setItem(i, 1, QTableWidgetItem(f"${nom['salario']:,}"))
            self.nomina_table.setItem(i, 2, QTableWidgetItem(f"${nom['bonif']:,}"))
            self.nomina_table.setItem(i, 3, QTableWidgetItem(f"${nom['deduc']:,}"))
            self.nomina_table.setItem(i, 4, QTableWidgetItem(f"${nom['ss']:,}"))
            self.nomina_table.setItem(i, 5, QTableWidgetItem(f"${nom['ret']:,}"))
            self.nomina_table.setItem(i, 6, QTableWidgetItem(f"${nom['neto']:,}"))
            self.nomina_table.setItem(i, 7, QTableWidgetItem(nom["estado"]))
    
    def cargar_asistencia(self):
        """Carga la asistencia"""
        # Datos demo
        asistencia = [
            {"empleado": "Juan Pérez", "fecha": "2024-01-20", "entrada": "08:00", 
             "salida": "17:00", "horas": "8", "obs": ""},
            {"empleado": "María García", "fecha": "2024-01-20", "entrada": "08:30", 
             "salida": "17:30", "horas": "8", "obs": "Llegada tardía"}
        ]
        
        self.asistencia_table.setRowCount(len(asistencia))
        
        for i, asist in enumerate(asistencia):
            self.asistencia_table.setItem(i, 0, QTableWidgetItem(asist["empleado"]))
            self.asistencia_table.setItem(i, 1, QTableWidgetItem(asist["fecha"]))
            self.asistencia_table.setItem(i, 2, QTableWidgetItem(asist["entrada"]))
            self.asistencia_table.setItem(i, 3, QTableWidgetItem(asist["salida"]))
            self.asistencia_table.setItem(i, 4, QTableWidgetItem(asist["horas"]))
            self.asistencia_table.setItem(i, 5, QTableWidgetItem(asist["obs"]))
    
    def cargar_vacaciones(self):
        """Carga las vacaciones"""
        # Datos demo
        vacaciones = [
            {"empleado": "Juan Pérez", "inicio": "2024-03-01", "fin": "2024-03-15", 
             "dias": "15", "estado": "Aprobado", "obs": "Vacaciones anuales"},
            {"empleado": "María García", "inicio": "2024-04-01", "fin": "2024-04-10", 
             "dias": "10", "estado": "Pendiente", "obs": "Solicitud reciente"}
        ]
        
        self.vacaciones_table.setRowCount(len(vacaciones))
        
        for i, vac in enumerate(vacaciones):
            self.vacaciones_table.setItem(i, 0, QTableWidgetItem(vac["empleado"]))
            self.vacaciones_table.setItem(i, 1, QTableWidgetItem(vac["inicio"]))
            self.vacaciones_table.setItem(i, 2, QTableWidgetItem(vac["fin"]))
            self.vacaciones_table.setItem(i, 3, QTableWidgetItem(vac["dias"]))
            self.vacaciones_table.setItem(i, 4, QTableWidgetItem(vac["estado"]))
            self.vacaciones_table.setItem(i, 5, QTableWidgetItem(vac["obs"]))
    
    def cargar_balance(self):
        """Carga el balance general"""
        # Datos demo activos
        activos = [
            {"cuenta": "Caja", "valor": 500000},
            {"cuenta": "Banco Corriente", "valor": 2000000},
            {"cuenta": "Inventarios", "valor": 1500000},
            {"cuenta": "Cuentas por Cobrar", "valor": 800000}
        ]
        
        self.activos_table.setRowCount(len(activos))
        
        for i, activo in enumerate(activos):
            self.activos_table.setItem(i, 0, QTableWidgetItem(activo["cuenta"]))
            self.activos_table.setItem(i, 1, QTableWidgetItem(f"${activo['valor']:,}"))
        
        # Datos demo pasivos
        pasivos = [
            {"cuenta": "Cuentas por Pagar", "valor": 300000},
            {"cuenta": "Préstamos", "valor": 1000000},
            {"cuenta": "Capital Social", "valor": 2000000},
            {"cuenta": "Utilidades Retenidas", "valor": 1500000}
        ]
        
        self.pasivos_table.setRowCount(len(pasivos))
        
        for i, pasivo in enumerate(pasivos):
            self.pasivos_table.setItem(i, 0, QTableWidgetItem(pasivo["cuenta"]))
            self.pasivos_table.setItem(i, 1, QTableWidgetItem(f"${pasivo['valor']:,}"))
    
    # Métodos de eventos
    def crear_empleado(self):
        """Crea un nuevo empleado"""
        dialog = EmpleadoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_empleado_data()
            QMessageBox.information(self, "Éxito", f"Empleado {datos['nombre']} {datos['apellido']} creado exitosamente")
            self.cargar_empleados()
    
    def editar_empleado(self):
        """Edita un empleado"""
        current_row = self.empleados_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un empleado para editar")
            return
        
        # Obtener datos del empleado
        empleado_data = {
            'nombre': self.empleados_table.item(current_row, 1).text(),
            'apellido': self.empleados_table.item(current_row, 2).text(),
            'cedula': self.empleados_table.item(current_row, 3).text(),
            'cargo': self.empleados_table.item(current_row, 4).text(),
            'salario': float(self.empleados_table.item(current_row, 6).text().replace('$', '').replace(',', ''))
        }
        
        dialog = EmpleadoDialog(self, empleado_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_empleado_data()
            QMessageBox.information(self, "Éxito", f"Empleado {datos['nombre']} {datos['apellido']} actualizado exitosamente")
            self.cargar_empleados()
    
    def eliminar_empleado(self):
        """Elimina un empleado"""
        current_row = self.empleados_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un empleado para eliminar")
            return
        
        nombre = self.empleados_table.item(current_row, 1).text()
        apellido = self.empleados_table.item(current_row, 2).text()
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar el empleado {nombre} {apellido}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Éxito", f"Empleado {nombre} {apellido} eliminado exitosamente")
            self.cargar_empleados()
    
    def crear_transaccion(self):
        """Crea una nueva transacción"""
        dialog = TransaccionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_transaccion_data()
            QMessageBox.information(self, "Éxito", f"Transacción '{datos['concepto']}' creada exitosamente")
            self.cargar_transacciones()
    
    def editar_transaccion(self):
        """Edita una transacción"""
        current_row = self.transacciones_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una transacción para editar")
            return
        
        # Obtener datos de la transacción
        transaccion_data = {
            'concepto': self.transacciones_table.item(current_row, 3).text(),
            'valor': float(self.transacciones_table.item(current_row, 4).text().replace('$', '').replace(',', ''))
        }
        
        dialog = TransaccionDialog(self, transaccion_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_transaccion_data()
            QMessageBox.information(self, "Éxito", f"Transacción '{datos['concepto']}' actualizada exitosamente")
            self.cargar_transacciones()
    
    def eliminar_transaccion(self):
        """Elimina una transacción"""
        current_row = self.transacciones_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una transacción para eliminar")
            return
        
        concepto = self.transacciones_table.item(current_row, 3).text()
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar la transacción '{concepto}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Éxito", f"Transacción '{concepto}' eliminada exitosamente")
            self.cargar_transacciones()
    
    def procesar_nomina(self):
        """Procesa la nómina"""
        QMessageBox.information(self, "Éxito", "Nómina procesada exitosamente")
        self.cargar_nomina()
    
    def generar_desprendibles(self):
        """Genera desprendibles de nómina"""
        QMessageBox.information(self, "Éxito", "Desprendibles generados exitosamente")
    
    def registrar_asistencia(self):
        """Registra asistencia"""
        QMessageBox.information(self, "Éxito", "Asistencia registrada exitosamente")
        self.cargar_asistencia()
    
    def solicitar_vacaciones(self):
        """Solicita vacaciones"""
        QMessageBox.information(self, "Éxito", "Solicitud de vacaciones enviada")
        self.cargar_vacaciones()
    
    def aprobar_vacaciones(self):
        """Aprueba vacaciones"""
        QMessageBox.information(self, "Éxito", "Vacaciones aprobadas exitosamente")
        self.cargar_vacaciones()
    
    def generar_balance(self):
        """Genera balance general"""
        QMessageBox.information(self, "Éxito", "Balance general generado exitosamente")
        self.cargar_balance()
    
    def generar_reporte_nomina(self):
        """Genera reporte de nómina"""
        reporte = """
REPORTE DE NÓMINA - ENERO 2024
=============================

RESUMEN GENERAL:
- Total empleados: 3
- Total salarios base: $6,500,000
- Total bonificaciones: $300,000
- Total deducciones: $250,000
- Total seguridad social: $520,000
- Total retenciones: $850,000
- NETO A PAGAR: $5,180,000

DETALLE POR EMPLEADO:
1. Juan Pérez - Supervisor
   - Salario: $2,500,000
   - Neto: $2,050,000

2. María García - Contador
   - Salario: $2,200,000
   - Neto: $1,774,000

3. Carlos Rodríguez - Técnico
   - Salario: $1,800,000
   - Neto: $1,356,000
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_estado_resultados(self):
        """Genera estado de resultados"""
        reporte = """
ESTADO DE RESULTADOS - ENERO 2024
=================================

INGRESOS:
- Ventas de productos: $1,500,000
- Servicios: $300,000
- Otros ingresos: $50,000
TOTAL INGRESOS: $1,850,000

EGRESOS:
- Costo de ventas: $600,000
- Gastos de personal: $500,000
- Gastos operativos: $200,000
- Otros gastos: $100,000
TOTAL EGRESOS: $1,400,000

UTILIDAD BRUTA: $450,000
UTILIDAD NETA: $450,000
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_listado_empleados(self):
        """Genera listado de empleados"""
        reporte = """
LISTADO DE EMPLEADOS - ENERO 2024
=================================

EMPLEADOS ACTIVOS:

1. Juan Pérez
   - Cédula: 12345678
   - Cargo: Supervisor
   - Departamento: Producción
   - Salario: $2,500,000
   - Fecha ingreso: 2023-01-15

2. María García
   - Cédula: 87654321
   - Cargo: Contador
   - Departamento: Contabilidad
   - Salario: $2,200,000
   - Fecha ingreso: 2023-03-01

3. Carlos Rodríguez
   - Cédula: 11223344
   - Cargo: Técnico
   - Departamento: Mantenimiento
   - Salario: $1,800,000
   - Fecha ingreso: 2023-06-01

TOTAL EMPLEADOS: 3
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_flujo_efectivo(self):
        """Genera flujo de efectivo"""
        reporte = """
FLUJO DE EFECTIVO - ENERO 2024
==============================

ACTIVIDADES OPERATIVAS:
+ Ingresos por ventas: $1,500,000
- Pago a proveedores: $600,000
- Pago nómina: $500,000
- Gastos operativos: $200,000
Flujo neto operativo: $200,000

ACTIVIDADES DE INVERSIÓN:
- Compra de equipos: $100,000
Flujo neto inversión: ($100,000)

ACTIVIDADES DE FINANCIACIÓN:
+ Préstamos recibidos: $0
- Pago de préstamos: $50,000
Flujo neto financiación: ($50,000)

FLUJO NETO TOTAL: $50,000
Saldo inicial: $2,000,000
Saldo final: $2,050,000
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_analisis_cuentas(self):
        """Genera análisis de cuentas"""
        reporte = """
ANÁLISIS DE CUENTAS - ENERO 2024
================================

CUENTAS POR COBRAR:
- Total por cobrar: $125,000
- Vencidas: $25,000 (20%)
- Por vencer: $100,000 (80%)
- Rotación: 45 días promedio

CUENTAS POR PAGAR:
- Total por pagar: $85,000
- Vencidas: $15,000 (17.6%)
- Por vencer: $70,000 (82.4%)
- Rotación: 30 días promedio

ANÁLISIS DE LIQUIDEZ:
- Ratio corriente: 1.8
- Prueba ácida: 1.2
- Capital de trabajo: $800,000

RECOMENDACIONES:
- Mejorar cobranza de cartera vencida
- Aprovechar descuentos por pronto pago
- Optimizar flujo de caja
        """
        self.preview_text.setPlainText(reporte)
    
    def generar_indicadores(self):
        """Genera indicadores financieros"""
        reporte = """
INDICADORES FINANCIEROS - ENERO 2024
====================================

INDICADORES DE LIQUIDEZ:
- Ratio corriente: 1.8
- Prueba ácida: 1.2
- Capital de trabajo: $800,000

INDICADORES DE RENTABILIDAD:
- Margen bruto: 60%
- Margen neto: 24%
- ROA: 18%
- ROE: 22%

INDICADORES DE EFICIENCIA:
- Rotación de inventarios: 6 veces/año
- Rotación de CxC: 8 veces/año
- Rotación de CxP: 12 veces/año

INDICADORES DE ENDEUDAMIENTO:
- Nivel de endeudamiento: 25%
- Cobertura de intereses: 5.2 veces
- Autonomía financiera: 75%

TENDENCIAS:
- Liquidez: Estable
- Rentabilidad: En crecimiento
- Endeudamiento: Bajo control
        """
        self.preview_text.setPlainText(reporte)


# Ejemplo de uso
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear vista completa de administración
    admin_view = AdministracionCompletaView()
    admin_view.show()
    
    sys.exit(app.exec())