"""
Vista de Contabilidad

Sistema completo de contabilidad para Stock.App v1.1.3
Interfaz moderna con tabs para diferentes funcionalidades
"""

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

from PyQt6.QtCore import QDate, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ContabilidadView(QWidget):
    """Vista principal del módulo de contabilidad."""

    # Señales para el controlador
    crear_departamento_signal = pyqtSignal(dict)
    crear_empleado_signal = pyqtSignal(dict)
    crear_asiento_signal = pyqtSignal(dict)
    crear_recibo_signal = pyqtSignal(dict)
    imprimir_recibo_signal = pyqtSignal(int)
    generar_reporte_signal = pyqtSignal(dict)
    actualizar_datos_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.datos_contables = {}
        self.current_user = "ADMIN"
        self.current_role = "ADMIN"
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header con título y controles
        header_layout = self.create_header()
        layout.addLayout(header_layout)

        # Tabs principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                min-width: 120px;
            }
            QTab:selected {
                background-color: #3498db;
                color: white;
            }
            QTab:hover {
                background-color: #5dade2;
                color: white;
            }
        """)

        # Crear tabs
        self.create_tabs()

        layout.addWidget(self.tabs)

        # Status bar
        self.status_bar = self.create_status_bar()
        layout.addWidget(self.status_bar)

        # Conectar señales
        self.connect_signals()

    def create_header(self):
        """Crea el header con título y controles."""
        header_layout = QHBoxLayout()

        # Título
        title_label = QLabel("💰 Contabilidad - Stock.App v1.1.3")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Controles de usuario
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        user_layout = QHBoxLayout(user_frame)

        user_label = QLabel(f"👤 {self.current_user} ({self.current_role})")
        user_label.setStyleSheet("color: white; font-weight: bold;")
        user_layout.addWidget(user_label)

        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        user_layout.addWidget(refresh_btn)

        header_layout.addWidget(user_frame)

        return header_layout

    def create_tabs(self):
        """Crea las pestañas principales."""
        # Dashboard
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")

        # Libro Contable
        self.libro_tab = self.create_libro_contable_tab()
        self.tabs.addTab(self.libro_tab, "📚 Libro Contable")

        # Recibos
        self.recibos_tab = self.create_recibos_tab()
        self.tabs.addTab(self.recibos_tab, "🧾 Recibos")

        # Pagos por Obra
        self.pagos_obra_tab = self.create_pagos_obra_tab()
        self.tabs.addTab(self.pagos_obra_tab, "🏗️ Pagos por Obra")

        # Materiales
        self.materiales_tab = self.create_materiales_tab()
        self.tabs.addTab(self.materiales_tab, "📦 Materiales")

        # Departamentos
        self.departamentos_tab = self.create_departamentos_tab()
        self.tabs.addTab(self.departamentos_tab, "🏢 Departamentos")

        # Empleados
        self.empleados_tab = self.create_empleados_tab()
        self.tabs.addTab(self.empleados_tab, "👥 Empleados")

        # Reportes
        self.reportes_tab = self.create_reportes_tab()
        self.tabs.addTab(self.reportes_tab, "📈 Reportes")

        # Auditoría
        self.auditoria_tab = self.create_auditoria_tab()
        self.tabs.addTab(self.auditoria_tab, "🔍 Auditoría")

    def create_dashboard_tab(self):
        """Crea la pestaña de dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Resumen general
        resumen_frame = QGroupBox("📊 Resumen General")
        resumen_frame.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        resumen_layout = QGridLayout(resumen_frame)

        # Cards de resumen
        self.cards_resumen = {}
        cards_data = [
            ("💰 Total Ingresos", "total_ingresos", "#27ae60"),
            ("💸 Total Egresos", "total_egresos", "#e74c3c"),
            ("🧾 Recibos Emitidos", "recibos_emitidos", "#3498db"),
            ("📚 Asientos Contables", "asientos_contables", "#9b59b6"),
            ("🏗️ Pagos por Obra", "pagos_obra", "#f39c12"),
            ("📦 Compras Materiales", "compras_materiales", "#1abc9c"),
        ]

        for i, (titulo, key, color) in enumerate(cards_data):
            card = self.create_info_card(titulo, "0", color)
            self.cards_resumen[key] = card
            resumen_layout.addWidget(card, i // 3, i % 3)

        layout.addWidget(resumen_frame)

        # Gráficos y estadísticas
        graficos_frame = QGroupBox("📈 Estadísticas")
        graficos_frame.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding-top: 10px;
                margin-top: 10px;
            }
        """)
        graficos_layout = QHBoxLayout(graficos_frame)

        # Placeholder para gráficos
        grafico_label = QLabel("📊 Gráficos de estadísticas se mostrarán aquí")
        grafico_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 50px;
                text-align: center;
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
            }
        """)
        grafico_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graficos_layout.addWidget(grafico_label)

        layout.addWidget(graficos_frame)

        return widget

    def create_libro_contable_tab(self):
        """Crea la pestaña del libro contable."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nuevo_asiento_btn = QPushButton("➕ Nuevo Asiento")
        nuevo_asiento_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nuevo_asiento_btn.clicked.connect(self.show_nuevo_asiento_dialog)
        toolbar.addWidget(nuevo_asiento_btn)

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("📅 Desde:"))
        self.libro_fecha_desde = QDateEdit()
        self.libro_fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.libro_fecha_desde.setCalendarPopup(True)
        filtros_layout.addWidget(self.libro_fecha_desde)

        filtros_layout.addWidget(QLabel("📅 Hasta:"))
        self.libro_fecha_hasta = QDateEdit()
        self.libro_fecha_hasta.setDate(QDate.currentDate())
        self.libro_fecha_hasta.setCalendarPopup(True)
        filtros_layout.addWidget(self.libro_fecha_hasta)

        filtros_layout.addWidget(QLabel("📂 Tipo:"))
        self.libro_tipo_combo = QComboBox()
        self.libro_tipo_combo.addItems(
            ["Todos", "INGRESO", "EGRESO", "AJUSTE", "TRANSFERENCIA"]
        )
        filtros_layout.addWidget(self.libro_tipo_combo)

        buscar_btn = QPushButton("🔍 Buscar")
        buscar_btn.clicked.connect(self.buscar_libro_contable)
        filtros_layout.addWidget(buscar_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de asientos
        self.tabla_libro = QTableWidget()
        self.tabla_libro.setColumnCount(12)
        self.tabla_libro.setHorizontalHeaderLabels(
            [
                "ID",
                "Número",
                "Fecha",
                "Tipo",
                "Concepto",
                "Referencia",
                "Debe",
                "Haber",
                "Saldo",
                "Estado",
                "Usuario",
                "Acciones",
            ]
        )

        self.tabla_libro.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_libro.setAlternatingRowColors(True)
        self.tabla_libro.horizontalHeader().setStretchLastSection(True)
        self.tabla_libro.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.tabla_libro)

        return widget

    def create_recibos_tab(self):
        """Crea la pestaña de recibos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nuevo_recibo_btn = QPushButton("➕ Nuevo Recibo")
        nuevo_recibo_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nuevo_recibo_btn.clicked.connect(self.show_nuevo_recibo_dialog)
        toolbar.addWidget(nuevo_recibo_btn)

        imprimir_recibo_btn = QPushButton("🖨️ Imprimir Seleccionado")
        imprimir_recibo_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        imprimir_recibo_btn.clicked.connect(self.imprimir_recibo_seleccionado)
        toolbar.addWidget(imprimir_recibo_btn)

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("📅 Desde:"))
        self.recibos_fecha_desde = QDateEdit()
        self.recibos_fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.recibos_fecha_desde.setCalendarPopup(True)
        filtros_layout.addWidget(self.recibos_fecha_desde)

        filtros_layout.addWidget(QLabel("📅 Hasta:"))
        self.recibos_fecha_hasta = QDateEdit()
        self.recibos_fecha_hasta.setDate(QDate.currentDate())
        self.recibos_fecha_hasta.setCalendarPopup(True)
        filtros_layout.addWidget(self.recibos_fecha_hasta)

        filtros_layout.addWidget(QLabel("📂 Tipo:"))
        self.recibos_tipo_combo = QComboBox()
        self.recibos_tipo_combo.addItems(
            ["Todos", "PAGO", "COMPRA", "GASTO", "REEMBOLSO"]
        )
        filtros_layout.addWidget(self.recibos_tipo_combo)

        buscar_recibos_btn = QPushButton("🔍 Buscar")
        buscar_recibos_btn.clicked.connect(self.buscar_recibos)
        filtros_layout.addWidget(buscar_recibos_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de recibos
        self.tabla_recibos = QTableWidget()
        self.tabla_recibos.setColumnCount(11)
        self.tabla_recibos.setHorizontalHeaderLabels(
            [
                "ID",
                "Número",
                "Fecha",
                "Tipo",
                "Concepto",
                "Beneficiario",
                "Monto",
                "Moneda",
                "Estado",
                "Impreso",
                "Acciones",
            ]
        )

        self.tabla_recibos.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_recibos.setAlternatingRowColors(True)
        self.tabla_recibos.horizontalHeader().setStretchLastSection(True)
        self.tabla_recibos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_recibos)

        return widget

    def create_pagos_obra_tab(self):
        """Crea la pestaña de pagos por obra."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nuevo_pago_btn = QPushButton("➕ Nuevo Pago")
        nuevo_pago_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nuevo_pago_btn.clicked.connect(self.show_nuevo_pago_obra_dialog)
        toolbar.addWidget(nuevo_pago_btn)

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("🏗️ Obra:"))
        self.pagos_obra_combo = QComboBox()
        self.pagos_obra_combo.addItems(["Todas las obras"])
        filtros_layout.addWidget(self.pagos_obra_combo)

        filtros_layout.addWidget(QLabel("📂 Categoría:"))
        self.pagos_categoria_combo = QComboBox()
        self.pagos_categoria_combo.addItems(
            ["Todas", "MATERIAL", "MANO_OBRA", "EQUIPOS", "SERVICIOS", "OTROS"]
        )
        filtros_layout.addWidget(self.pagos_categoria_combo)

        buscar_pagos_btn = QPushButton("🔍 Buscar")
        buscar_pagos_btn.clicked.connect(self.buscar_pagos_obra)
        filtros_layout.addWidget(buscar_pagos_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de pagos
        self.tabla_pagos_obra = QTableWidget()
        self.tabla_pagos_obra.setColumnCount(10)
        self.tabla_pagos_obra.setHorizontalHeaderLabels(
            [
                "ID",
                "Obra",
                "Concepto",
                "Categoría",
                "Monto",
                "Fecha",
                "Método Pago",
                "Estado",
                "Usuario",
                "Acciones",
            ]
        )

        self.tabla_pagos_obra.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_pagos_obra.setAlternatingRowColors(True)
        self.tabla_pagos_obra.horizontalHeader().setStretchLastSection(True)
        self.tabla_pagos_obra.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_pagos_obra)

        return widget

    def create_materiales_tab(self):
        """Crea la pestaña de materiales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nueva_compra_btn = QPushButton("➕ Nueva Compra")
        nueva_compra_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nueva_compra_btn.clicked.connect(self.show_nueva_compra_dialog)
        toolbar.addWidget(nueva_compra_btn)

        registrar_pago_btn = QPushButton("💳 Registrar Pago")
        registrar_pago_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        registrar_pago_btn.clicked.connect(self.show_pago_material_dialog)
        toolbar.addWidget(registrar_pago_btn)

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("🏪 Proveedor:"))
        self.materiales_proveedor_combo = QComboBox()
        self.materiales_proveedor_combo.addItems(["Todos los proveedores"])
        filtros_layout.addWidget(self.materiales_proveedor_combo)

        filtros_layout.addWidget(QLabel("💰 Estado:"))
        self.materiales_estado_combo = QComboBox()
        self.materiales_estado_combo.addItems(
            ["Todos", "PENDIENTE", "PARCIAL", "PAGADO"]
        )
        filtros_layout.addWidget(self.materiales_estado_combo)

        buscar_materiales_btn = QPushButton("🔍 Buscar")
        buscar_materiales_btn.clicked.connect(self.buscar_materiales)
        filtros_layout.addWidget(buscar_materiales_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de materiales
        self.tabla_materiales = QTableWidget()
        self.tabla_materiales.setColumnCount(11)
        self.tabla_materiales.setHorizontalHeaderLabels(
            [
                "ID",
                "Producto",
                "Proveedor",
                "Cantidad",
                "Precio Unit.",
                "Total",
                "Pagado",
                "Pendiente",
                "Estado",
                "Fecha",
                "Acciones",
            ]
        )

        self.tabla_materiales.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_materiales.setAlternatingRowColors(True)
        self.tabla_materiales.horizontalHeader().setStretchLastSection(True)
        self.tabla_materiales.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_materiales)

        return widget

    def create_departamentos_tab(self):
        """Crea la pestaña de departamentos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nuevo_departamento_btn = QPushButton("➕ Nuevo Departamento")
        nuevo_departamento_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nuevo_departamento_btn.clicked.connect(self.show_nuevo_departamento_dialog)
        toolbar.addWidget(nuevo_departamento_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Tabla de departamentos
        self.tabla_departamentos = QTableWidget()
        self.tabla_departamentos.setColumnCount(8)
        self.tabla_departamentos.setHorizontalHeaderLabels(
            [
                "ID",
                "Código",
                "Nombre",
                "Responsable",
                "Presupuesto",
                "Estado",
                "Fecha Creación",
                "Acciones",
            ]
        )

        self.tabla_departamentos.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_departamentos.setAlternatingRowColors(True)
        self.tabla_departamentos.horizontalHeader().setStretchLastSection(True)
        self.tabla_departamentos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_departamentos)

        return widget

    def create_empleados_tab(self):
        """Crea la pestaña de empleados."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        nuevo_empleado_btn = QPushButton("➕ Nuevo Empleado")
        nuevo_empleado_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        nuevo_empleado_btn.clicked.connect(self.show_nuevo_empleado_dialog)
        toolbar.addWidget(nuevo_empleado_btn)

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("🏢 Departamento:"))
        self.empleados_departamento_combo = QComboBox()
        self.empleados_departamento_combo.addItems(["Todos los departamentos"])
        filtros_layout.addWidget(self.empleados_departamento_combo)

        buscar_empleados_btn = QPushButton("🔍 Buscar")
        buscar_empleados_btn.clicked.connect(self.buscar_empleados)
        filtros_layout.addWidget(buscar_empleados_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de empleados
        self.tabla_empleados = QTableWidget()
        self.tabla_empleados.setColumnCount(10)
        self.tabla_empleados.setHorizontalHeaderLabels(
            [
                "ID",
                "Código",
                "Nombre",
                "Apellido",
                "Documento",
                "Departamento",
                "Cargo",
                "Salario",
                "Estado",
                "Acciones",
            ]
        )

        self.tabla_empleados.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_empleados.setAlternatingRowColors(True)
        self.tabla_empleados.horizontalHeader().setStretchLastSection(True)
        self.tabla_empleados.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_empleados)

        return widget

    def create_reportes_tab(self):
        """Crea la pestaña de reportes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Selector de tipo de reporte
        selector_frame = QGroupBox("📊 Tipo de Reporte")
        selector_layout = QGridLayout(selector_frame)

        # Botones para diferentes tipos de reportes
        reportes_btns = [
            ("📚 Libro Contable", "libro_contable"),
            ("🧾 Recibos", "recibos"),
            ("🏗️ Pagos por Obra", "pagos_obra"),
            ("📦 Materiales", "materiales"),
            ("🏢 Departamentos", "departamentos"),
            ("👥 Empleados", "empleados"),
            ("📈 Resumen Ejecutivo", "resumen_ejecutivo"),
            ("🔍 Auditoría", "auditoria"),
        ]

        for i, (texto, tipo) in enumerate(reportes_btns):
            btn = QPushButton(texto)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5dade2;
                }
            """)
            btn.clicked.connect(lambda checked, t=tipo: self.generar_reporte(t))
            selector_layout.addWidget(btn, i // 4, i % 4)

        layout.addWidget(selector_frame)

        # Parámetros del reporte
        parametros_frame = QGroupBox("⚙️ Parámetros del Reporte")
        parametros_layout = QFormLayout(parametros_frame)

        self.reporte_fecha_desde = QDateEdit()
        self.reporte_fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.reporte_fecha_desde.setCalendarPopup(True)
        parametros_layout.addRow("📅 Fecha Desde:", self.reporte_fecha_desde)

        self.reporte_fecha_hasta = QDateEdit()
        self.reporte_fecha_hasta.setDate(QDate.currentDate())
        self.reporte_fecha_hasta.setCalendarPopup(True)
        parametros_layout.addRow("📅 Fecha Hasta:", self.reporte_fecha_hasta)

        self.reporte_formato_combo = QComboBox()
        self.reporte_formato_combo.addItems(["PDF", "Excel", "CSV"])
        parametros_layout.addRow("📄 Formato:", self.reporte_formato_combo)

        layout.addWidget(parametros_frame)

        # Área de vista previa
        preview_frame = QGroupBox("👁️ Vista Previa")
        preview_layout = QVBoxLayout(preview_frame)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText(
            "Seleccione un tipo de reporte para ver la vista previa..."
        )
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_frame)

        return widget

    def create_auditoria_tab(self):
        """Crea la pestaña de auditoría."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel("🔍 Auditoría del Sistema"))

        toolbar.addStretch()

        # Filtros
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_frame)

        filtros_layout.addWidget(QLabel("📋 Tabla:"))
        self.auditoria_tabla_combo = QComboBox()
        self.auditoria_tabla_combo.addItems(
            [
                "Todas",
                "libro_contable",
                "recibos",
                "pagos_obras",
                "pagos_materiales",
                "departamentos",
                "empleados",
            ]
        )
        filtros_layout.addWidget(self.auditoria_tabla_combo)

        filtros_layout.addWidget(QLabel("👤 Usuario:"))
        self.auditoria_usuario_combo = QComboBox()
        self.auditoria_usuario_combo.addItems(["Todos"])
        filtros_layout.addWidget(self.auditoria_usuario_combo)

        buscar_auditoria_btn = QPushButton("🔍 Buscar")
        buscar_auditoria_btn.clicked.connect(self.buscar_auditoria)
        filtros_layout.addWidget(buscar_auditoria_btn)

        toolbar.addWidget(filtros_frame)

        layout.addLayout(toolbar)

        # Tabla de auditoría
        self.tabla_auditoria = QTableWidget()
        self.tabla_auditoria.setColumnCount(8)
        self.tabla_auditoria.setHorizontalHeaderLabels(
            [
                "ID",
                "Tabla",
                "Registro",
                "Acción",
                "Usuario",
                "Fecha",
                "Datos Anteriores",
                "Datos Nuevos",
            ]
        )

        self.tabla_auditoria.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        self.tabla_auditoria.setAlternatingRowColors(True)
        self.tabla_auditoria.horizontalHeader().setStretchLastSection(True)
        self.tabla_auditoria.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_auditoria)

        return widget

    def create_info_card(self, titulo, valor, color):
        """Crea una tarjeta de información."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout(card)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo_label)

        valor_label = QLabel(valor)
        valor_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(valor_label)

        return card

    def create_status_bar(self):
        """Crea la barra de estado."""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
        """)

        status_layout = QHBoxLayout(status_frame)

        self.status_label = QLabel("✅ Sistema listo")
        self.status_label.setStyleSheet("color: white; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.conexion_label = QLabel("🔗 Conectado a DB")
        self.conexion_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        status_layout.addWidget(self.conexion_label)

        return status_frame

    def connect_signals(self):
        """Conecta las señales de la interfaz."""
        # Las señales se conectarán con el controlador
        pass

    # MÉTODOS DE DIÁLOGOS
    def show_nuevo_asiento_dialog(self):
        """Muestra el diálogo para crear un nuevo asiento contable."""
        # Implementar diálogo de asiento
        pass

    def show_nuevo_recibo_dialog(self):
        """Muestra el diálogo para crear un nuevo recibo."""
        # Implementar diálogo de recibo
        pass

    def show_nuevo_pago_obra_dialog(self):
        """Muestra el diálogo para registrar un pago por obra."""
        # Implementar diálogo de pago por obra
        pass

    def show_nueva_compra_dialog(self):
        """Muestra el diálogo para registrar una nueva compra de material."""
        # Implementar diálogo de compra
        pass

    def show_pago_material_dialog(self):
        """Muestra el diálogo para registrar un pago de material."""
        # Implementar diálogo de pago material
        pass

    def show_nuevo_departamento_dialog(self):
        """Muestra el diálogo para crear un nuevo departamento."""
        # Implementar diálogo de departamento
        pass

    def show_nuevo_empleado_dialog(self):
        """Muestra el diálogo para crear un nuevo empleado."""
        # Implementar diálogo de empleado
        pass

    # MÉTODOS DE BÚSQUEDA Y ACTUALIZACIÓN
    def buscar_libro_contable(self):
        """Busca asientos en el libro contable."""
        # Implementar búsqueda
        pass

    def buscar_recibos(self):
        """Busca recibos."""
        # Implementar búsqueda
        pass

    def buscar_pagos_obra(self):
        """Busca pagos por obra."""
        # Implementar búsqueda
        pass

    def buscar_materiales(self):
        """Busca materiales."""
        # Implementar búsqueda
        pass

    def buscar_empleados(self):
        """Busca empleados."""
        # Implementar búsqueda
        pass

    def buscar_auditoria(self):
        """Busca registros de auditoría."""
        # Implementar búsqueda
        pass

    def imprimir_recibo_seleccionado(self):
        """Imprime el recibo seleccionado."""
        # Implementar impresión
        pass

    def generar_reporte(self, tipo_reporte):
        """Genera un reporte del tipo especificado."""
        # Implementar generación de reportes
        pass

    def refresh_data(self):
        """Actualiza todos los datos de la interfaz."""
        self.actualizar_datos_signal.emit()

    def actualizar_dashboard(self, datos):
        """Actualiza el dashboard con nuevos datos."""
        if "resumen" in datos:
            resumen = datos["resumen"]

            # Actualizar cards
            if "libro_contable" in resumen:
                self.cards_resumen["total_ingresos"].findChild(QLabel).setText(
                    f"${resumen['libro_contable']['total_debe']:,.2f}"
                )
                self.cards_resumen["total_egresos"].findChild(QLabel).setText(
                    f"${resumen['libro_contable']['total_haber']:,.2f}"
                )
                self.cards_resumen["asientos_contables"].findChild(QLabel).setText(
                    str(resumen["libro_contable"]["total_asientos"])
                )

            if "recibos" in resumen:
                self.cards_resumen["recibos_emitidos"].findChild(QLabel).setText(
                    str(resumen["recibos"]["total_recibos"])
                )

            if "pagos_obras" in resumen:
                self.cards_resumen["pagos_obra"].findChild(QLabel).setText(
                    str(resumen["pagos_obras"]["total_pagos"])
                )

            if "pagos_materiales" in resumen:
                self.cards_resumen["compras_materiales"].findChild(QLabel).setText(
                    str(resumen["pagos_materiales"]["total_compras"])
                )

    def actualizar_tabla_libro(self, asientos):
        """Actualiza la tabla del libro contable."""
        self.tabla_libro.setRowCount(len(asientos))

        for row, asiento in enumerate(asientos):
            self.tabla_libro.setItem(row, 0, QTableWidgetItem(str(asiento["id"])))
            self.tabla_libro.setItem(
                row, 1, QTableWidgetItem(asiento["numero_asiento"])
            )
            self.tabla_libro.setItem(
                row, 2, QTableWidgetItem(str(asiento["fecha_asiento"]))
            )
            self.tabla_libro.setItem(row, 3, QTableWidgetItem(asiento["tipo_asiento"]))
            self.tabla_libro.setItem(row, 4, QTableWidgetItem(asiento["concepto"]))
            self.tabla_libro.setItem(
                row, 5, QTableWidgetItem(asiento["referencia"] or "")
            )
            self.tabla_libro.setItem(
                row, 6, QTableWidgetItem(f"${asiento['debe']:,.2f}")
            )
            self.tabla_libro.setItem(
                row, 7, QTableWidgetItem(f"${asiento['haber']:,.2f}")
            )
            self.tabla_libro.setItem(
                row, 8, QTableWidgetItem(f"${asiento['saldo']:,.2f}")
            )
            self.tabla_libro.setItem(row, 9, QTableWidgetItem(asiento["estado"]))
            self.tabla_libro.setItem(
                row, 10, QTableWidgetItem(asiento["usuario_creacion"])
            )

            # Botón de acciones
            acciones_btn = QPushButton("⚙️")
            acciones_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            self.tabla_libro.setCellWidget(row, 11, acciones_btn)

    def actualizar_tabla_recibos(self, recibos):
        """Actualiza la tabla de recibos."""
        self.tabla_recibos.setRowCount(len(recibos))

        for row, recibo in enumerate(recibos):
            self.tabla_recibos.setItem(row, 0, QTableWidgetItem(str(recibo["id"])))
            self.tabla_recibos.setItem(
                row, 1, QTableWidgetItem(recibo["numero_recibo"])
            )
            self.tabla_recibos.setItem(
                row, 2, QTableWidgetItem(str(recibo["fecha_emision"]))
            )
            self.tabla_recibos.setItem(row, 3, QTableWidgetItem(recibo["tipo_recibo"]))
            self.tabla_recibos.setItem(row, 4, QTableWidgetItem(recibo["concepto"]))
            self.tabla_recibos.setItem(row, 5, QTableWidgetItem(recibo["beneficiario"]))
            self.tabla_recibos.setItem(
                row, 6, QTableWidgetItem(f"${recibo['monto']:,.2f}")
            )
            self.tabla_recibos.setItem(row, 7, QTableWidgetItem(recibo["moneda"]))
            self.tabla_recibos.setItem(row, 8, QTableWidgetItem(recibo["estado"]))
            self.tabla_recibos.setItem(
                row, 9, QTableWidgetItem("✅" if recibo["impreso"] else "❌")
            )

            # Botón de acciones
            acciones_btn = QPushButton("⚙️")
            acciones_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            self.tabla_recibos.setCellWidget(row, 10, acciones_btn)

    def mostrar_mensaje(self, titulo, mensaje, tipo="info"):
        """Muestra un mensaje al usuario."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)

        if tipo == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif tipo == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif tipo == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)

        msg_box.exec()

    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de estado."""
        self.status_label.setText(mensaje)

        # Auto-limpiar después de 5 segundos
        QTimer.singleShot(5000, lambda: self.status_label.setText("✅ Sistema listo"))
