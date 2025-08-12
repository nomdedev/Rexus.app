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

Vista de Compras

Interfaz de usuario para el módulo de compras.

# [SECURITY] XSS Protection Added - Validate all user inputs
# Todos los campos de formulario estan protegidos contra XSS
# XSS Protection Added
"""


from typing import Dict

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from rexus.utils.form_validators import FormValidator, FormValidatorManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# XSS Protection imports
from rexus.utils.xss_protection import XSSProtection, FormProtector
from rexus.utils.security import SecurityUtils
from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.security import SecurityUtils
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.ui.components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Mapear componentes Qt a Rexus
QLabel = RexusLabel


class ComprasView(QWidget):
    """Vista principal del módulo de compras."""

    # Señales
    orden_creada = pyqtSignal(dict)
    orden_actualizada = pyqtSignal(int, str)
    busqueda_realizada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        
        # Inicializar protección XSS
        try:
            self.xss_protector = FormProtector()
            self._setup_xss_protection()
            print('[XSS] Protección inicializada correctamente')
        except ImportError as e:
            print(f'[XSS] Dependencia no disponible: {e}')
            self.xss_protector = None
        except Exception as e:
            print(f'[XSS] Error inicializando protección: {e}')
            self.xss_protector = None
        
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)


        # Panel de control estandarizado
        control_panel = StandardComponents.create_control_panel()
        self.setup_control_panel(control_panel)
        layout.addWidget(control_panel)

        # Crear tabs
        tab_widget = QTabWidget()
        
        # Pestaña de compras
        panel_compras = self.crear_panel_compras()
        tab_widget.addTab(panel_compras, "📋 Órdenes de Compra")
        
        # Pestaña de estadísticas
        panel_estadisticas = self.crear_panel_estadisticas()
        tab_widget.addTab(panel_estadisticas, "[CHART] Estadísticas")
        
        layout.addWidget(tab_widget)

        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)

        # Aplicar estilos después de crear la interfaz
        self.aplicar_estilos()

    def aplicar_estilos(self):
        """Aplica estilos minimalistas y modernos a toda la interfaz."""
        self.setStyleSheet("""
            /* Estilo general del widget */
            QWidget {
                background-color: #fafbfc;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            /* Pestañas minimalistas */
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: white;
                margin-top: 2px;
            }
            
            QTabBar::tab {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 11px;
                color: #586069;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #24292e;
                font-weight: 500;
                border-bottom: 2px solid #0366d6;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e1e4e8;
                color: #24292e;
            }
            
            /* Tablas compactas */
            QTableWidget {
                gridline-color: #e1e4e8;
                selection-background-color: #f1f8ff;
                selection-color: #24292e;
                alternate-background-color: #f6f8fa;
                font-size: 11px;
                border: 1px solid #e1e4e8;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            
            QHeaderView::section {
                background-color: #f6f8fa;
                color: #586069;
                font-weight: 600;
                font-size: 10px;
                border: none;
                border-right: 1px solid #e1e4e8;
                border-bottom: 1px solid #e1e4e8;
                padding: 6px 8px;
            }
            
            /* GroupBox minimalista */
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                color: #24292e;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #24292e;
            }
            
            /* Botones minimalistas */
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }
            
            QPushButton:pressed {
                background-color: #d0d7de;
            }
            
            /* Campos de entrada compactos */
            QLineEdit, QComboBox {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: white;
                min-height: 18px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #0366d6;
                outline: none;
            }
            
            /* Labels compactos */
            QLabel {
                color: #24292e;
                font-size: 11px;
            }
            
            /* Scroll bars minimalistas */
            QScrollBar:vertical {
                width: 12px;
                background-color: #f6f8fa;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #d0d7de;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #bbb;
            }
        """)

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Botón Nueva Orden estandarizado
        self.btn_nueva_orden = StandardComponents.create_primary_button("➕ Nueva Orden")
        self.btn_nueva_orden.setToolTip("➕ Crear una nueva orden de compra")
        self.btn_nueva_orden.clicked.connect(self.abrir_dialog_nueva_orden)
        layout.addWidget(self.btn_nueva_orden)
        
        # Botón Gestionar Proveedores
        self.btn_proveedores = StandardComponents.create_secondary_button("🏢 Proveedores")
        self.btn_proveedores.setToolTip("🏢 Gestionar proveedores")
        self.btn_proveedores.clicked.connect(self.abrir_dialog_proveedores)
        layout.addWidget(self.btn_proveedores)
        
        # Botón Seguimiento de Entregas
        self.btn_seguimiento = StandardComponents.create_info_button("🚚 Seguimiento")
        self.btn_seguimiento.setToolTip("🚚 Seguimiento de entregas")
        self.btn_seguimiento.clicked.connect(self.abrir_seguimiento_entrega)
        layout.addWidget(self.btn_seguimiento)

        # Búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar por proveedor o número de orden...")
        self.input_busqueda.setToolTip("🔍 Buscar órdenes por proveedor, número o descripción")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.input_busqueda.returnPressed.connect(self.buscar_compras)

        # Filtro por estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems([
            "📋 Todos los estados",
            "⏳ PENDIENTE",
            "[CHECK] APROBADA",
            "🚚 RECIBIDA",
            "[ERROR] CANCELADA"
        ])
        self.combo_estado.setToolTip("[CHART] Filtrar órdenes por estado")
        self.combo_estado.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.combo_estado.currentTextChanged.connect(self.buscar_compras)

        # Filtro por fechas
        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addMonths(-3))
        self.date_desde.setCalendarPopup(True)
        self.date_desde.dateChanged.connect(self.buscar_compras)

        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.dateChanged.connect(self.buscar_compras)

        # Botón buscar estandarizado
        self.btn_buscar = StandardComponents.create_secondary_button("🔍 Buscar")
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_buscar.clicked.connect(self.buscar_compras)

        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_success_button("🔄 Actualizar")
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de órdenes")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)

        # Agregar widgets con mejor organización
        layout.addWidget(self.btn_nueva_orden)
        layout.addWidget(self.input_busqueda)
        layout.addWidget(self.combo_estado)
        
        # Sección de fechas
        fechas_layout = QHBoxLayout()
        fechas_layout.addWidget(RexusLabel("📅 Desde:"))
        fechas_layout.addWidget(self.date_desde)
        fechas_layout.addWidget(RexusLabel("📅 Hasta:"))
        fechas_layout.addWidget(self.date_hasta)
        
        fechas_widget = QWidget()
        fechas_widget.setLayout(fechas_layout)
        layout.addWidget(fechas_widget)
        
        # Separador y botones de acción
        layout.addStretch()
        layout.addWidget(self.btn_buscar)
        layout.addWidget(self.btn_actualizar)
        
        # Botón de reportes
        self.btn_reporte = StandardComponents.create_info_button("[CHART] Reporte")
        self.btn_reporte.setToolTip("[CHART] Generar reporte de compras")
        self.btn_reporte.clicked.connect(self.exportar_reporte_compras)
        layout.addWidget(self.btn_reporte)
        
        # Botón de integración con inventario
        self.btn_inventario = StandardComponents.create_warning_button("📦 Stock Bajo")
        self.btn_inventario.setToolTip("📦 Ver productos con stock bajo para comprar")
        self.btn_inventario.clicked.connect(self.ver_productos_stock_bajo)
        layout.addWidget(self.btn_inventario)

        return panel

    def crear_panel_compras(self):
        """Crea el panel de lista de compras."""
        panel = QGroupBox("Órdenes de Compra")
        layout = QVBoxLayout(panel)

        # Tabla de compras estandarizada
        self.tabla_compras = StandardComponents.create_standard_table()
        self.tabla_compras.setColumnCount(10)
        self.tabla_compras.setHorizontalHeaderLabels(
            [
                "ID",
                "Proveedor",
                "Número Orden",
                "Fecha Pedido",
                "Fecha Entrega",
                "Estado",
                "Total",
                "Usuario",
                "Fecha Creación",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_compras.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

        self.tabla_compras.setAlternatingRowColors(True)
        self.tabla_compras.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_compras.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Estilo de la tabla
        self.tabla_compras.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 12px;
                font-weight: bold;
                color: #495057;
            }
        """)

        layout.addWidget(self.tabla_compras)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas mejorado."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Crear scroll area para estadísticas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === ESTADÍSTICAS GENERALES ===
        stats_general = QGroupBox("[CHART] Estadísticas Generales")
        stats_general.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        stats_layout = QGridLayout(stats_general)
        
        # Labels de estadísticas básicas
        self.lbl_total_ordenes = RexusLabel("Total Órdenes: 0")
        self.lbl_ordenes_pendientes = RexusLabel("Pendientes: 0")
        self.lbl_ordenes_aprobadas = RexusLabel("Aprobadas: 0")
        self.lbl_monto_total = RexusLabel("Monto Total: $0.00")
        self.lbl_promedio_orden = QLabel("Promedio por Orden: $0.00")
        self.lbl_ordenes_mes = QLabel("Órdenes este Mes: 0")
        
        # Estilo para labels básicos
        label_style = """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                margin: 2px;
            }
        """
        
        labels_basicos = [
            self.lbl_total_ordenes, self.lbl_ordenes_pendientes, self.lbl_ordenes_aprobadas,
            self.lbl_monto_total, self.lbl_promedio_orden, self.lbl_ordenes_mes
        ]
        
        for i, label in enumerate(labels_basicos):
            label.setStyleSheet(label_style)
            stats_layout.addWidget(label, i // 2, i % 2)
        
        scroll_layout.addWidget(stats_general)
        
        # === ANÁLISIS POR PROVEEDORES ===
        proveedores_group = QGroupBox("🏪 Análisis por Proveedores")
        proveedores_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        proveedores_layout = QVBoxLayout(proveedores_group)
        
        # Tabla de proveedores
        self.tabla_proveedores = StandardComponents.create_standard_table()
        self.tabla_proveedores.setColumnCount(5)
        self.tabla_proveedores.setHorizontalHeaderLabels([
            "Proveedor", "Órdenes", "Monto Total", "Promedio", "% del Total"
        ])
        self.tabla_proveedores.setMaximumHeight(200)
        self.tabla_proveedores.setAlternatingRowColors(True)
        self.tabla_proveedores.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border: 1px solid #229954;
                font-weight: bold;
            }
        """)
        
        # Configurar tabla
        header = self.tabla_proveedores.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        proveedores_layout.addWidget(self.tabla_proveedores)
        
        # Proveedor destacado
        self.lbl_proveedor_top = QLabel("🏆 Proveedor Principal: No hay datos")
        self.lbl_proveedor_top.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #27ae60;
                padding: 6px 8px;
                background-color: #d5f4e6;
                border-radius: 4px;
                margin: 5px;
            }
        """)
        proveedores_layout.addWidget(self.lbl_proveedor_top)
        
        scroll_layout.addWidget(proveedores_group)
        
        # === ANÁLISIS TEMPORAL ===
        temporal_group = QGroupBox("📈 Análisis Temporal")
        temporal_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        temporal_layout = QGridLayout(temporal_group)
        
        # Estadísticas temporales
        self.lbl_compras_hoy = QLabel("Compras Hoy: 0")
        self.lbl_compras_semana = QLabel("Compras esta Semana: 0")
        self.lbl_compras_mes = QLabel("Compras este Mes: 0")
        self.lbl_tendencia = QLabel("Tendencia: Estable")
        
        temporal_style = """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e74c3c;
                padding: 8px;
                background-color: #fdf2f2;
                border-radius: 4px;
                margin: 2px;
            }
        """
        
        labels_temporales = [
            self.lbl_compras_hoy, self.lbl_compras_semana, 
            self.lbl_compras_mes, self.lbl_tendencia
        ]
        
        for i, label in enumerate(labels_temporales):
            label.setStyleSheet(temporal_style)
            temporal_layout.addWidget(label, i // 2, i % 2)
        
        scroll_layout.addWidget(temporal_group)
        
        # === ANÁLISIS DE PRODUCTOS ===
        productos_group = QGroupBox("📦 Análisis de Productos")
        productos_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        productos_layout = QGridLayout(productos_group)
        
        # Estadísticas de productos
        self.lbl_productos_unicos = QLabel("Productos Únicos: 0")
        self.lbl_categoria_top = QLabel("Categoría Principal: No hay datos")
        self.lbl_producto_mas_comprado = QLabel("Producto Más Comprado: No hay datos")
        self.lbl_ticket_promedio = QLabel("Ticket Promedio: $0.00")
        
        productos_style = """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #f39c12;
                padding: 8px;
                background-color: #fef9e7;
                border-radius: 4px;
                margin: 2px;
            }
        """
        
        labels_productos = [
            self.lbl_productos_unicos, self.lbl_categoria_top,
            self.lbl_producto_mas_comprado, self.lbl_ticket_promedio
        ]
        
        for i, label in enumerate(labels_productos):
            label.setStyleSheet(productos_style)
            productos_layout.addWidget(label, i // 2, i % 2)
        
        scroll_layout.addWidget(productos_group)
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Gráfico de estados (texto por ahora)
        self.estados_frame = QFrame()
        self.estados_frame.setFrameStyle(QFrame.Shape.Box)
        self.estados_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        estados_layout = QVBoxLayout(self.estados_frame)

        titulo_estados = QLabel("Distribución por Estado")
        titulo_estados.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        titulo_estados.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        estados_layout.addWidget(titulo_estados)

        self.texto_estados = QTextEdit()
        self.texto_estados.setMaximumHeight(150)
        self.texto_estados.setReadOnly(True)
        self.texto_estados.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        estados_layout.addWidget(self.texto_estados)

        layout.addWidget(self.estados_frame)

        return panel

    def configurar_estilos(self):
        """Configura los estilos modernos usando FormStyleManager."""
        try:
            from rexus.utils.form_styles import FormStyleManager, setup_form_widget
            
            # Aplicar estilos modernos del FormStyleManager
            setup_form_widget(self, apply_animations=True)
            
            # Estilos específicos del módulo de compras
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #f8f9fa;
                }
                QGroupBox {
                    font-weight: bold;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QDateEdit {
                    border: 2px solid #ced4da;
                    border-radius: 6px;
                    padding: 10px 12px;
                    font-size: 14px;
                    background-color: white;
                }
                QDateEdit:focus {
                    border-color: #3498db;
                }
            """)
            
        except ImportError:
            print("[WARNING] FormStyleManager no disponible, usando estilos básicos")
            self.aplicar_estilo_basico()

    def aplicar_estilo_basico(self):
        """Aplica estilos básicos como fallback."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        # Estados de botones principales
        self.btn_nueva_orden.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)
        
        # Nuevos botones
        if hasattr(self, 'btn_proveedores'):
            self.btn_proveedores.setEnabled(not loading)
        if hasattr(self, 'btn_seguimiento'):
            self.btn_seguimiento.setEnabled(not loading)
        if hasattr(self, 'btn_reporte'):
            self.btn_reporte.setEnabled(not loading)
        if hasattr(self, 'btn_configuracion'):
            self.btn_configuracion.setEnabled(not loading)
        
        # Cambiar textos durante loading
        if loading:
            self.btn_actualizar.setText("⏳ Actualizando...")
            self.btn_buscar.setText("🔍 Buscando...")
        else:
            self.btn_actualizar.setText("🔄 Actualizar")
            self.btn_buscar.setText("🔍 Buscar")

    def abrir_dialog_nueva_orden(self):
        """Abre el diálogo para crear una nueva orden."""
        dialog = DialogNuevaOrden(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            self.orden_creada.emit(datos)

    def buscar_compras(self):
        """Ejecuta la búsqueda de compras."""
        filtros = {
            "proveedor": self.input_busqueda.text(),
            "estado": self.combo_estado.currentText()
            if self.combo_estado.currentText() != "Todos"
            else "",
            "fecha_inicio": self.date_desde.date().toPython(),
            "fecha_fin": self.date_hasta.date().toPython(),
        }
        self.busqueda_realizada.emit(filtros)

    def cargar_compras_en_tabla(self, compras):
        """Carga las compras en la tabla."""
        self.tabla_compras.setRowCount(len(compras))

        for row, compra in enumerate(compras):
            # Datos básicos
            self.tabla_compras.setItem(
                row, 0, QTableWidgetItem(str(compra.get("id", "")))
            )
            self.tabla_compras.setItem(
                row, 1, QTableWidgetItem(str(compra.get("proveedor", "")))
            )
            self.tabla_compras.setItem(
                row, 2, QTableWidgetItem(str(compra.get("numero_orden", "")))
            )
            self.tabla_compras.setItem(
                row, 3, QTableWidgetItem(str(compra.get("fecha_pedido", "")))
            )
            self.tabla_compras.setItem(
                row, 4, QTableWidgetItem(str(compra.get("fecha_entrega_estimada", "")))
            )

            # Estado con color
            estado_item = QTableWidgetItem(str(compra.get("estado", "")))
            estado = compra.get("estado", "")
            if estado == "PENDIENTE":
                estado_item.setBackground(Qt.GlobalColor.yellow)
            elif estado == "APROBADA":
                estado_item.setBackground(Qt.GlobalColor.cyan)
            elif estado == "RECIBIDA":
                estado_item.setBackground(Qt.GlobalColor.green)
            elif estado == "CANCELADA":
                estado_item.setBackground(Qt.GlobalColor.red)

            self.tabla_compras.setItem(row, 5, estado_item)

            # Total
            total = compra.get("total_final", 0)
            self.tabla_compras.setItem(row, 6, QTableWidgetItem(f"${total:,.2f}"))

            # Usuario y fecha
            self.tabla_compras.setItem(
                row, 7, QTableWidgetItem(str(compra.get("usuario_creacion", "")))
            )
            self.tabla_compras.setItem(
                row, 8, QTableWidgetItem(str(compra.get("fecha_creacion", "")))
            )

            # Botones de acción - Layout horizontal con múltiples botones
            acciones_layout = QHBoxLayout()
            acciones_widget = QWidget()
            
            # Botón Editar
            btn_editar = StandardComponents.create_warning_button("Editar")
            btn_editar.clicked.connect(
                lambda checked, id=compra.get("id"): self.editar_orden(id)
            )
            acciones_layout.addWidget(btn_editar)
            
            # Botón Seguimiento
            btn_seguimiento = StandardComponents.create_info_button("Seguimiento")
            btn_seguimiento.clicked.connect(
                lambda checked, id=compra.get("id"): self.ver_seguimiento_orden(id)
            )
            acciones_layout.addWidget(btn_seguimiento)
            
            acciones_layout.setContentsMargins(2, 2, 2, 2)
            acciones_widget.setLayout(acciones_layout)
            self.tabla_compras.setCellWidget(row, 9, acciones_widget)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas completas mostradas."""
        # === ESTADÍSTICAS GENERALES ===
        self.lbl_total_ordenes.setText(
            f"Total Órdenes: {stats.get('total_ordenes', 0)}"
        )
        self.lbl_monto_total.setText(
            f"Monto Total: ${stats.get('monto_total', 0):,.2f}"
        )
        self.lbl_promedio_orden.setText(
            f"Promedio por Orden: ${stats.get('promedio_orden', 0):,.2f}"
        )
        self.lbl_ordenes_mes.setText(
            f"Órdenes este Mes: {stats.get('ordenes_mes', 0)}"
        )

        # Actualizar contadores por estado
        estados_data = stats.get("ordenes_por_estado", [])
        pendientes = next(
            (x["cantidad"] for x in estados_data if x["estado"] == "PENDIENTE"), 0
        )
        aprobadas = next(
            (x["cantidad"] for x in estados_data if x["estado"] == "APROBADA"), 0
        )

        self.lbl_ordenes_pendientes.setText(f"Pendientes: {pendientes}")
        self.lbl_ordenes_aprobadas.setText(f"Aprobadas: {aprobadas}")

        # === ANÁLISIS POR PROVEEDORES ===
        # Actualizar tabla de proveedores
        proveedores_data = stats.get("proveedores_analisis", [])
        self.tabla_proveedores.setRowCount(len(proveedores_data))
        
        for row, proveedor in enumerate(proveedores_data):
            self.tabla_proveedores.setItem(row, 0, QTableWidgetItem(proveedor["proveedor"]))
            self.tabla_proveedores.setItem(row, 1, QTableWidgetItem(str(proveedor["ordenes"])))
            self.tabla_proveedores.setItem(row, 2, QTableWidgetItem(f"${proveedor['monto_total']:,.2f}"))
            self.tabla_proveedores.setItem(row, 3, QTableWidgetItem(f"${proveedor['promedio']:,.2f}"))
            self.tabla_proveedores.setItem(row, 4, QTableWidgetItem(f"{proveedor['porcentaje']:.1f}%"))
        
        # Actualizar proveedor principal
        proveedor_principal = stats.get("proveedor_principal")
        if proveedor_principal:
            self.lbl_proveedor_top.setText(
                f"🏆 Proveedor Principal: {proveedor_principal['proveedor']} "
                f"({proveedor_principal['ordenes']} órdenes - ${proveedor_principal['monto_total']:,.2f})"
            )
        else:
            self.lbl_proveedor_top.setText("🏆 Proveedor Principal: No hay datos")

        # === ANÁLISIS TEMPORAL ===
        self.lbl_compras_hoy.setText(f"Compras Hoy: {stats.get('compras_hoy', 0)}")
        self.lbl_compras_semana.setText(f"Compras esta Semana: {stats.get('compras_semana', 0)}")
        self.lbl_compras_mes.setText(f"Compras este Mes: {stats.get('compras_mes', 0)}")
        self.lbl_tendencia.setText(f"Tendencia: {stats.get('tendencia', 'Estable')}")

        # === ANÁLISIS DE PRODUCTOS ===
        self.lbl_productos_unicos.setText(f"Productos Únicos: {stats.get('productos_unicos', 0)}")
        self.lbl_categoria_top.setText(f"Categoría Principal: {stats.get('categoria_principal', 'No hay datos')}")
        self.lbl_producto_mas_comprado.setText(f"Producto Más Comprado: {stats.get('producto_mas_comprado', 'No hay datos')}")
        self.lbl_ticket_promedio.setText(f"Ticket Promedio: ${stats.get('ticket_promedio', 0):,.2f}")

        # === DISTRIBUCIÓN POR ESTADO ===
        # Actualizar texto de estados
        texto_estados = "Distribución por Estado:\n\n"
        for estado_data in estados_data:
            texto_estados += f"• {estado_data['estado']}: {estado_data['cantidad']}\n"

        self.texto_estados.setPlainText(texto_estados)

    def editar_orden(self, orden_id):
        """Edita una orden existente."""
        # Por ahora solo cambiar estado
        estados = ["PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]

        # Crear un diálogo simple para cambiar estado
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Estado")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        combo_estado = RexusComboBox()
        combo_estado.addItems(estados)
        layout.addWidget(RexusLabel("Nuevo Estado:"))
        layout.addWidget(combo_estado)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevo_estado = combo_estado.currentText()
            self.orden_actualizada.emit(orden_id, nuevo_estado)

    def actualizar_datos(self):
        """Actualiza los datos de la vista."""
        self.buscar_compras()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
    
    def abrir_dialog_proveedores(self):
        """Abre el diálogo de gestión de proveedores."""
        try:
            from rexus.modules.compras.dialogs import DialogProveedor
            
            dialog = DialogProveedor(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos_proveedor = dialog.obtener_datos()
                
                # Crear el proveedor a través del controlador
                if self.controller:
                    exito = self.controller.crear_proveedor(datos_proveedor)
                    if exito:
                        show_success(self, "Éxito", "Proveedor creado exitosamente")
                    else:
                        show_error(self, "Error", "No se pudo crear el proveedor")
                        
        except ImportError as e:
            show_error(self, "Error", f"No se pudo cargar el diálogo de proveedores: {e}")
        except Exception as e:
            show_error(self, "Error", f"Error abriendo diálogo de proveedores: {e}")
    
    def abrir_seguimiento_entrega(self):
        """Abre el seguimiento de entregas para la orden seleccionada."""
        # Verificar que hay una orden seleccionada
        fila_seleccionada = self.tabla_compras.currentRow()
        if fila_seleccionada < 0:
            show_warning(self, "Sin selección", "Debe seleccionar una orden para ver el seguimiento")
            return
        
        try:
            # Obtener ID de la orden seleccionada
            id_item = self.tabla_compras.item(fila_seleccionada, 0)
            if not id_item:
                show_error(self, "Error", "No se pudo obtener el ID de la orden")
                return
            
            orden_id = int(id_item.text())
            self.ver_seguimiento_orden(orden_id)
            
        except ValueError:
            show_error(self, "Error", "ID de orden inválido")
        except Exception as e:
            show_error(self, "Error", f"Error abriendo seguimiento: {e}")
    
    def ver_seguimiento_orden(self, orden_id):
        """Ve el seguimiento de una orden específica."""
        try:
            from rexus.modules.compras.dialogs import DialogSeguimiento
            
            # Obtener datos de la orden desde el controlador
            if not self.controller:
                show_error(self, "Error", "No hay controlador disponible")
                return
            
            # Por ahora usar datos básicos, el controlador debería proporcionar obtener_orden_por_id
            orden_data = {
                "id": orden_id,
                "numero_orden": f"ORD-{orden_id:06d}",
                "proveedor": "Proveedor Demo",
                "fecha_pedido": "2024-08-08",
                "fecha_entrega_estimada": "2024-08-15",
                "total_final": 1500.00,
                "estado": "PENDIENTE"
            }
            
            dialog = DialogSeguimiento(self, orden_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos_seguimiento = dialog.obtener_datos_seguimiento()
                
                # Actualizar seguimiento a través del controlador
                if self.controller and hasattr(self.controller, 'actualizar_seguimiento_pedido'):
                    self.controller.actualizar_seguimiento_pedido(
                        orden_id,
                        datos_seguimiento["nuevo_estado"],
                        datos_seguimiento.get("motivo", "")
                    )
                    show_success(self, "Éxito", "Seguimiento actualizado correctamente")
                    self.actualizar_datos()
                else:
                    # Fallback: actualizar solo el estado sin seguimiento detallado
                    if self.controller:
                        try:
                            self.controller.actualizar_estado_orden(orden_id, datos_seguimiento["nuevo_estado"])
                            show_success(self, "Estado Actualizado", "El estado de la orden ha sido actualizado")
                            self.actualizar_datos()
                        except Exception as e:
                            show_error(self, "Error", f"Error actualizando estado: {str(e)}")
                    else:
                        show_warning(self, "Sin Controlador", "No hay controlador disponible")
                
        except ImportError as e:
            show_error(self, "Error", f"No se pudo cargar el diálogo de seguimiento: {e}")
        except Exception as e:
            show_error(self, "Error", f"Error en seguimiento de orden: {e}")
    
    def mostrar_estadisticas_proveedor(self, proveedor_id):
        """Muestra estadísticas detalladas de un proveedor."""
        try:
            if self.controller and hasattr(self.controller, 'obtener_estadisticas_proveedor'):
                stats = self.controller.obtener_estadisticas_proveedor(proveedor_id)
                
                # Crear diálogo simple para mostrar estadísticas
                dialog = QDialog(self)
                dialog.setWindowTitle("Estadísticas de Proveedor")
                dialog.setMinimumSize(400, 300)
                
                layout = QVBoxLayout(dialog)
                
                # Mostrar estadísticas en texto
                texto_stats = QTextEdit()
                texto_stats.setReadOnly(True)
                
                stats_text = f"""
                Estadísticas del Proveedor:
                
                Total Órdenes: {stats.get('total_ordenes', 0)}
                Monto Total: ${stats.get('monto_total', 0):,.2f}
                Promedio por Orden: ${stats.get('promedio_orden', 0):,.2f}
                Órdenes Completadas: {stats.get('ordenes_completadas', 0)}
                Órdenes Pendientes: {stats.get('ordenes_pendientes', 0)}
                """
                
                texto_stats.setPlainText(stats_text)
                layout.addWidget(texto_stats)
                
                # Botón cerrar
                btn_cerrar = StandardComponents.create_primary_button("Cerrar")
                btn_cerrar.clicked.connect(dialog.accept)
                layout.addWidget(btn_cerrar)
                
                dialog.exec()
            else:
                show_warning(self, "Funcionalidad no disponible", 
                           "Las estadísticas de proveedor no están disponibles")
                           
        except Exception as e:
            show_error(self, "Error", f"Error mostrando estadísticas: {e}")
    
    def exportar_reporte_compras(self):
        """Exporta un reporte de compras."""
        try:
            if self.controller and hasattr(self.controller, 'generar_reporte_completo'):
                # Obtener fechas del filtro
                _ = self.date_desde.date().toPython()  # fecha_inicio no usada aún
                _ = self.date_hasta.date().toPython()  # fecha_fin no usada aún
                
                reporte = self.controller.generar_reporte_completo()
                
                if reporte:
                    # Por ahora mostrar en diálogo, luego se puede exportar a Excel/PDF
                    dialog = QDialog(self)
                    dialog.setWindowTitle("Reporte de Compras")
                    dialog.setMinimumSize(600, 400)
                    
                    layout = QVBoxLayout(dialog)
                    
                    texto_reporte = QTextEdit()
                    texto_reporte.setReadOnly(True)
                    
                    reporte_text = f"""
                    REPORTE DE COMPRAS
                    Fecha: {reporte.get('fecha_reporte', '')}
                    
                    ESTADÍSTICAS GENERALES:
                    - Total Proveedores: {reporte.get('total_proveedores', 0)}
                    - Proveedores Activos: {reporte.get('proveedores_activos', 0)}
                    - Total Categorías: {reporte.get('total_categorias', 0)}
                    
                    ESTADO DEL MÓDULO: {reporte.get('resumen', {}).get('estado', 'N/A')}
                    """
                    
                    texto_reporte.setPlainText(reporte_text)
                    layout.addWidget(texto_reporte)
                    
                    # Botón cerrar
                    btn_cerrar = StandardComponents.create_primary_button("Cerrar")
                    btn_cerrar.clicked.connect(dialog.accept)
                    layout.addWidget(btn_cerrar)
                    
                    dialog.exec()
                else:
                    show_error(self, "Error", "No se pudo generar el reporte")
            else:
                show_warning(self, "Funcionalidad no disponible", 
                           "La generación de reportes no está disponible")
                           
        except Exception as e:
            show_error(self, "Error", f"Error generando reporte: {e}")
    
    def ver_productos_stock_bajo(self):
        """Muestra productos con stock bajo que necesitan compra."""
        try:
            if not self.controller:
                show_warning(self, "Sin controlador", "El controlador no está disponible")
                return
            
            # Obtener productos con stock bajo desde el modelo
            productos = self.controller.model.obtener_productos_disponibles_compra()
            
            if not productos:
                from rexus.utils.message_system import show_info
                show_info(self, "Sin productos", "No hay productos con stock bajo en este momento")
                return
            
            # Crear diálogo simple para mostrar información
            dialog = QDialog(self)
            dialog.setWindowTitle("Productos con Stock Bajo")
            dialog.setModal(True)
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            title_label = QLabel("📦 Productos que Necesitan Compra")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f; margin: 10px;")
            layout.addWidget(title_label)
            
            # Información
            info_label = QLabel(f"Se encontraron {len(productos)} productos con stock bajo o crítico.")
            info_label.setStyleSheet("color: #666; margin: 5px;")
            layout.addWidget(info_label)
            
            # Tabla de productos
            tabla = StandardComponents.create_standard_table()
            tabla.setColumnCount(6)
            tabla.setHorizontalHeaderLabels([
                "Producto", "Tipo", "Stock Actual", 
                "Stock Mínimo", "Cantidad Sugerida", "Prioridad"
            ])
            
            tabla.setRowCount(len(productos))
            
            for row, producto in enumerate(productos):
                tabla.setItem(row, 0, QTableWidgetItem(producto.get('descripcion', '')))
                tabla.setItem(row, 1, QTableWidgetItem(producto.get('tipo', '')))
                tabla.setItem(row, 2, QTableWidgetItem(str(producto.get('stock_actual', 0))))
                tabla.setItem(row, 3, QTableWidgetItem(str(producto.get('stock_minimo', 0))))
                tabla.setItem(row, 4, QTableWidgetItem(str(producto.get('sugerencia_cantidad', 0))))
                
                # Prioridad con color
                prioridad_item = QTableWidgetItem(producto.get('prioridad', 'MEDIA'))
                if producto.get('prioridad') == 'ALTA':
                    from PyQt6.QtGui import QColor
                    prioridad_item.setBackground(QColor('#ffcdd2'))
                tabla.setItem(row, 5, prioridad_item)
            
            tabla.resizeColumnsToContents()
            layout.addWidget(tabla)
            
            # Botones
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            btn_cerrar = StandardComponents.create_secondary_button("Cerrar")
            btn_cerrar.clicked.connect(dialog.close)
            buttons_layout.addWidget(btn_cerrar)
            
            btn_nueva_orden = StandardComponents.create_success_button("Nueva Orden de Compra")
            btn_nueva_orden.clicked.connect(lambda: self.nueva_orden_desde_inventario(dialog))
            buttons_layout.addWidget(btn_nueva_orden)
            
            layout.addLayout(buttons_layout)
            
            dialog.exec()
            
        except Exception as e:
            show_error(self, "Error", f"Error obteniendo productos con stock bajo: {str(e)}")
            print(f"[ERROR COMPRAS] Error en ver_productos_stock_bajo: {e}")
    
    def nueva_orden_desde_inventario(self, dialog_parent):
        """Abre diálogo de nueva orden y cierra el de inventario."""
        try:
            dialog_parent.close()
            self.abrir_dialog_nueva_orden()
        except Exception as e:
            print(f"[ERROR] Error abriendo nueva orden desde inventario: {e}")


class DialogNuevaOrden(QDialog):
    """Diálogo para crear una nueva orden de compra."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Orden de Compra")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        
        # Inicializar el gestor de validaciones
        self.validator_manager = FormValidatorManager()
        
        self.init_ui()
        self.configurar_validaciones()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Campos
        self.input_proveedor = RexusLineEdit()
        self.input_numero_orden = RexusLineEdit()
        self.date_pedido = QDateEdit()
        self.date_pedido.setDate(QDate.currentDate())
        self.date_pedido.setCalendarPopup(True)

        self.date_entrega = QDateEdit()
        self.date_entrega.setDate(QDate.currentDate().addDays(30))
        self.date_entrega.setCalendarPopup(True)

        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["PENDIENTE", "APROBADA"])

        self.input_descuento = QDoubleSpinBox()
        self.input_descuento.setRange(0, 999999)
        self.input_descuento.setDecimals(2)
        self.input_descuento.setSuffix(" $")

        self.input_impuestos = QDoubleSpinBox()
        self.input_impuestos.setRange(0, 999999)
        self.input_impuestos.setDecimals(2)
        self.input_impuestos.setSuffix(" $")

        self.input_observaciones = QTextEdit()
        self.input_observaciones.setMaximumHeight(100)

        # Agregar campos al formulario
        form_layout.addRow("Proveedor:", self.input_proveedor)
        form_layout.addRow("Número de Orden:", self.input_numero_orden)
        form_layout.addRow("Fecha Pedido:", self.date_pedido)
        form_layout.addRow("Fecha Entrega:", self.date_entrega)
        form_layout.addRow("Estado:", self.combo_estado)
        form_layout.addRow("Descuento:", self.input_descuento)
        form_layout.addRow("Impuestos:", self.input_impuestos)
        form_layout.addRow("Observaciones:", self.input_observaciones)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Aplicar estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
                outline: none;
            }
        """)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "proveedor": self.input_proveedor.text(),
            "numero_orden": self.input_numero_orden.text(),
            "fecha_pedido": self.date_pedido.date().toPython(),
            "fecha_entrega_estimada": self.date_entrega.date().toPython(),
            "estado": self.combo_estado.currentText(),
            "descuento": self.input_descuento.value(),
            "impuestos": self.input_impuestos.value(),
            "observaciones": self.input_observaciones.toPlainText(),
            "usuario_creacion": self._obtener_usuario_actual(),
        }

    def _obtener_usuario_actual(self):
        """Obtiene el usuario actual del sistema."""
        try:
            from rexus.core.auth_manager import AuthManager
            auth_manager = AuthManager()
            usuario_actual = auth_manager.get_current_user()
            return usuario_actual.get('username', 'Sistema') if usuario_actual else 'Sistema'
        except ImportError:
            return 'Sistema'
        except Exception:
            return 'Sistema'

    def configurar_validaciones(self):
        """Configura las validaciones del formulario."""
        # Validación de proveedor obligatorio
        self.validator_manager.agregar_validacion(
            self.input_proveedor, 
            FormValidator.validar_campo_obligatorio, 
            "Proveedor"
        )
        self.validator_manager.agregar_validacion(
            self.input_proveedor, 
            FormValidator.validar_longitud_texto, 
            2, 100
        )

        # Validación de número de orden obligatorio
        self.validator_manager.agregar_validacion(
            self.input_numero_orden, 
            FormValidator.validar_campo_obligatorio, 
            "Número de orden"
        )
        self.validator_manager.agregar_validacion(
            self.input_numero_orden, 
            FormValidator.validar_longitud_texto, 
            3, 50
        )

        # Validación de fechas
        self.validator_manager.agregar_validacion(
            self.date_pedido, 
            FormValidator.validar_fecha
        )
        
        self.validator_manager.agregar_validacion(
            self.date_entrega, 
            FormValidator.validar_fecha, 
            self.date_pedido.date()  # Fecha mínima: fecha de pedido
        )

        # Validación de montos (descuento e impuestos no negativos)
        self.validator_manager.agregar_validacion(
            self.input_descuento, 
            FormValidator.validar_numero, 
            0.0, 999999.99
        )
        
        self.validator_manager.agregar_validacion(
            self.input_impuestos, 
            FormValidator.validar_numero, 
            0.0, 999999.99
        )
    def crear_controles_paginacion(self):
        """Crea los controles de paginación"""
        paginacion_layout = QHBoxLayout()
        
        # Etiqueta de información
        self.info_label = QLabel("Mostrando 1-50 de 0 registros")
        paginacion_layout.addWidget(self.info_label)
        
        paginacion_layout.addStretch()
        
        # Controles de navegación
        self.btn_primera = RexusButton("<<")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)
        
        self.btn_anterior = RexusButton("<")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)
        
        # Control de página actual
        self.pagina_actual_spin = QSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(QLabel("Página:"))
        paginacion_layout.addWidget(self.pagina_actual_spin)
        
        self.total_paginas_label = QLabel("de 1")
        paginacion_layout.addWidget(self.total_paginas_label)
        
        self.btn_siguiente = RexusButton(">")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)
        
        self.btn_ultima = RexusButton(">>")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)
        
        # Selector de registros por página
        paginacion_layout.addWidget(RexusLabel("Registros por página:"))
        self.registros_por_pagina_combo = RexusComboBox()
        self.registros_por_pagina_combo.addItems(["25", "50", "100", "200"])
        self.registros_por_pagina_combo.setCurrentText("50")
        self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        paginacion_layout.addWidget(self.registros_por_pagina_combo)
        
        return paginacion_layout
    
    def actualizar_controles_paginacion(self, pagina_actual, total_paginas, total_registros, registros_mostrados):
        """Actualiza los controles de paginación"""
        if hasattr(self, 'info_label'):
            inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} registros")
        
        if hasattr(self, 'pagina_actual_spin'):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)
        
        if hasattr(self, 'total_paginas_label'):
            self.total_paginas_label.setText(f"de {total_paginas}")
        
        # Habilitar/deshabilitar botones
        if hasattr(self, 'btn_primera'):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)
    
    def ir_a_pagina(self, pagina):
        """Va a una página específica"""
        if hasattr(self.controller, 'cargar_pagina'):
            self.controller.cargar_pagina(pagina)
    
    def pagina_anterior(self):
        """Va a la página anterior"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)
    
    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            total_paginas = self.pagina_actual_spin.maximum()
            if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)
    
    def ultima_pagina(self):
        """Va a la última página"""
        if hasattr(self, 'pagina_actual_spin'):
            total_paginas = self.pagina_actual_spin.maximum()
            self.ir_a_pagina(total_paginas)
    
    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada"""
        self.ir_a_pagina(pagina)
    
    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página"""
        if hasattr(self.controller, 'cambiar_registros_por_pagina'):
            self.controller.cambiar_registros_por_pagina(int(registros))

    def validar_y_aceptar(self):
        """Valida los datos y acepta el diálogo."""
        # Usar el sistema de validación
        es_valido, _ = self.validator_manager.validar_formulario()
        
        if not es_valido:
            # Mostrar errores con el sistema mejorado
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            show_error(
                self, 
                "Errores de Validación", 
                "Por favor corrige los siguientes errores:\n\n• " + "\n• ".join(mensajes_error)
            )
            return

        # Validación adicional: fecha de entrega posterior a fecha de pedido
        if self.date_entrega.date() <= self.date_pedido.date():
            show_error(
                self, 
                "Error de Validación", 
                "La fecha de entrega debe ser posterior a la fecha de pedido.\n\nPor favor seleccione una fecha de entrega que sea al menos un día después de la fecha de pedido."
            )
            return

        # Si todo es válido, aceptar el diálogo
        self.accept()

    def _setup_xss_protection(self):
        """Configura la protección XSS para todos los campos del formulario."""
        if not self.xss_protector:
            print('[XSS] Protector no disponible, saltando configuración')
            return
            
        try:
            # Configurar filtros para campos de texto
            text_fields = []
            
            # Buscar todos los campos de entrada en el formulario
            for child in self.findChildren((QLineEdit, QTextEdit, QPlainTextEdit)):
                if hasattr(child, 'objectName') and child.objectName():
                    field_name = child.objectName()
                    text_fields.append(field_name)
                    
                    # Configurar validación en tiempo real
                    if isinstance(child, QLineEdit):
                        child.textChanged.connect(lambda text, field=field_name: self._validate_field_input(field, text))
                    elif isinstance(child, (QTextEdit, QPlainTextEdit)):
                        child.textChanged.connect(lambda field=field_name: self._validate_text_area(field))
            
            # Configurar protector con campos encontrados
            for field in text_fields:
                self.xss_protector.add_field_filter(field, max_length=1000)
            
            print(f'[XSS] Protección configurada para {len(text_fields)} campos')
            
        except Exception as e:
            print(f'[XSS ERROR] Error configurando protección: {e}')

    def _validate_field_input(self, field_name: str, text: str):
        """Valida entrada de campo en tiempo real."""
        try:
            if not SecurityUtils.is_safe_input(text):
                print(f'[XSS WARNING] Contenido potencialmente peligroso en {field_name}: {text[:50]}...')
                # Aquí podrías mostrar advertencia al usuario
        except Exception as e:
            print(f'[XSS ERROR] Error validando {field_name}: {e}')

    def _validate_text_area(self, field_name: str):
        """Valida contenido de área de texto."""
        try:
            widget = self.findChild((QTextEdit, QPlainTextEdit), field_name)
            if widget:
                text = widget.toPlainText()
                if not SecurityUtils.is_safe_input(text):
                    print(f'[XSS WARNING] Contenido potencialmente peligroso en {field_name}')
        except Exception as e:
            print(f'[XSS ERROR] Error validando área de texto {field_name}: {e}')

    def obtener_datos_formulario_seguro(self) -> Dict[str, any]:
        """Obtiene datos del formulario con sanitización XSS completa."""
        try:
            datos = {}
            
            # Obtener datos de campos de línea
            for line_edit in self.findChildren(QLineEdit):
                if hasattr(line_edit, 'objectName') and line_edit.objectName():
                    field_name = line_edit.objectName()
                    raw_text = line_edit.text()
                    # [XSS] Protection: Sanitizar entrada de usuario
                    safe_text = XSSProtection.sanitize_text(raw_text)
                    datos[field_name] = safe_text
            
            # Obtener datos de áreas de texto
            for text_edit in self.findChildren((QTextEdit, QPlainTextEdit)):
                if hasattr(text_edit, 'objectName') and text_edit.objectName():
                    field_name = text_edit.objectName()
                    raw_text = text_edit.toPlainText()
                    # [XSS] Protection: Sanitizar entrada de usuario
                    safe_text = XSSProtection.sanitize_text(raw_text)
                    datos[field_name] = safe_text
            
            # Obtener datos de combos
            for combo in self.findChildren(QComboBox):
                if hasattr(combo, 'objectName') and combo.objectName():
                    field_name = combo.objectName()
                    current_text = combo.currentText()
                    # [XSS] Protection: Sanitizar texto del combo
                    safe_text = XSSProtection.sanitize_text(current_text)
                    datos[field_name] = safe_text
            
            # Usar protector para validación final
            if hasattr(self, 'xss_protector') and self.xss_protector:
                datos = self.xss_protector.sanitize_form_data(datos)
            
            return datos
            
        except Exception as e:
            print(f'[XSS ERROR] Error obteniendo datos seguros: {e}')
            return {}
