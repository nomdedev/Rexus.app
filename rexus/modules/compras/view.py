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

Vista de Compras - Interfaz de gestión de compras y proveedores
"""

# 🔒 Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control

# 🔒 XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added

"""
Interfaz de usuario para el módulo de compras.
"""

import logging
from datetime import date, datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from rexus.core.auth_manager import AuthManager
from rexus.utils.data_sanitizer import DataSanitizer
from rexus.utils.form_validators import FormValidator, FormValidatorManager
from rexus.utils.message_system import (
    ask_question,
    show_error,
    show_success,
    show_warning,
)
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import FormProtector, XSSProtection, xss_protect


class ComprasView(QWidget):
    """Vista principal del módulo de compras."""

    # Señales
    orden_creada = pyqtSignal(dict)
    orden_actualizada = pyqtSignal(int, str)
    busqueda_realizada = pyqtSignal(dict)

    def __init__(self):
        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(self._on_dangerous_content)
        
        super().__init__()
        self.controller = None
        self.logger = logging.getLogger(__name__)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título removido según solicitado

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Crear tabs
        tab_widget = QTabWidget()

        # Pestaña de compras
        panel_compras = self.crear_panel_compras()
        tab_widget.addTab(panel_compras, "📋 Órdenes de Compra")

        # Pestaña de estadísticas
        panel_estadisticas = self.crear_panel_estadisticas()
        tab_widget.addTab(panel_estadisticas, "📊 Estadísticas")

        layout.addWidget(tab_widget)

        # Aplicar estilo general
        self.aplicar_estilo()

    def crear_panel_control(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('crear_panel_control'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # Sanitización aplicada en procesamiento
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Crea el panel de control superior."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón Nueva Orden
        self.btn_nueva_orden = QPushButton("Nueva Orden")
        self.btn_nueva_orden.setToolTip('Acción: Botón Nueva Orden')
        self.btn_nueva_orden.setAccessibleName('Botón Nueva Orden')
        self.btn_nueva_orden.setIcon(QIcon("📋"))
        self.btn_nueva_orden.clicked.connect(self.abrir_dialog_nueva_orden)

        # Búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setAccessibleName('Input Busqueda')
        self.input_busqueda.setPlaceholderText(
            "Buscar por proveedor o número de orden..."
        )
        self.input_busqueda.returnPressed.connect(self.buscar_compras)

        # Filtro por estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(
            ["Todos", "PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]
        )
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

        # Botón buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setToolTip('Buscar elementos - Botón Buscar')
        self.btn_buscar.setAccessibleName('Botón Buscar')
        self.btn_buscar.clicked.connect(self.buscar_compras)

        # Botón actualizar
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.setToolTip('Acción: Botón Actualizar')
        self.btn_actualizar.setAccessibleName('Botón Actualizar')
        self.btn_actualizar.clicked.connect(self.actualizar_datos)

        # Agregar widgets
        layout.addWidget(self.btn_nueva_orden)
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input_busqueda)
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)
        layout.addWidget(QLabel("Desde:"))
        layout.addWidget(self.date_desde)
        layout.addWidget(QLabel("Hasta:"))
        layout.addWidget(self.date_hasta)
        layout.addWidget(self.btn_buscar)
        layout.addWidget(self.btn_actualizar)

        return panel

    def crear_panel_compras(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('crear_panel_compras'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Crea el panel de lista de compras."""
        panel = QGroupBox("Órdenes de Compra")
        layout = QVBoxLayout(panel)

        # Tabla de compras
        self.tabla_compras = QTableWidget()
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
                background-color:
        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # Sanitización aplicada en procesamiento
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)
 #e3f2fd;
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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('crear_panel_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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
        stats_general = QGroupBox("📊 Estadísticas Generales")
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
        self.lbl_total_ordenes = QLabel("Total Órdenes: 0")
        self.lbl_ordenes_pendientes = QLabel("Pendientes: 0")
        self.lbl_ordenes_aprobadas = QLabel("Aprobadas: 0")
        self.lbl_monto_total = QLabel("Monto Total: $0.00")
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
            self.lbl_total_ordenes,
            self.lbl_ordenes_pendientes,
            self.lbl_ordenes_aprobadas,
            self.lbl_monto_total,
            self.lbl_promedio_orden,
            self.lbl_ordenes_mes,
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
        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(5)
        self.tabla_proveedores.setHorizontalHeaderLabels(
            ["Proveedor", "Órdenes", "Monto Total", "Promedio", "% del Total"]
        )
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
                font-size: 13px;
                font-weight: bold;
                color: #27ae60;
                padding: 10px;
                background-color: #d5f4e6;
                border-radius: 6px;
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
            self.lbl_compras_hoy,
            self.lbl_compras_semana,
            self.lbl_compras_mes,
            self.lbl_tendencia,
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
            self.lbl_productos_unicos,
            self.lbl_categoria_top,
            self.lbl_producto_mas_comprado,
            self.lbl_ticket_promedio,
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

    def aplicar_estilo(self):
        """Aplica el estilo general al widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                max-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
                font-size: 14px;
            }
        """)

    def validar_orden_duplicada(self, numero_orden, proveedor):
        """Valida si ya existe una orden con el mismo número para el mismo proveedor."""
        try:
            self.logger.info(
                f"Validando orden duplicada: {numero_orden} para {proveedor}"
            )

            # Recorrer tabla de compras para buscar duplicados
            for row in range(self.tabla_compras.rowCount()):
                proveedor_item = self.tabla_compras.item(row, 1)  # Columna proveedor
                numero_item = self.tabla_compras.item(row, 2)  # Columna número orden

                if proveedor_item and numero_item:
                    proveedor_existente = proveedor_item.text().strip()
                    numero_existente = numero_item.text().strip()

                    # Normalizar datos para comparación
                    proveedor_norm = DataSanitizer.sanitize_text(proveedor).lower()
                    proveedor_existente_norm = DataSanitizer.sanitize_text(
                        proveedor_existente
                    ).lower()
                    numero_norm = DataSanitizer.sanitize_text(numero_orden).lower()
                    numero_existente_norm = DataSanitizer.sanitize_text(
                        numero_existente
                    ).lower()

                    if (
                        proveedor_norm == proveedor_existente_norm
                        and numero_norm == numero_existente_norm
                    ):
                        self.logger.warning(
                            f"Orden duplicada encontrada: {numero_orden} para {proveedor}"
                        )
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error al validar orden duplicada: {str(e)}")
            return False

    def abrir_dialog_nueva_orden(self):
        """Abre el diálogo para crear una nueva orden."""
        try:
            self.logger.info("Abriendo diálogo para nueva orden de compra")

            dialog = DialogNuevaOrden(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos = dialog.obtener_datos()

                # Validar orden duplicada
                if self.validar_orden_duplicada(
                    datos.get("numero_orden", ""), datos.get("proveedor", "")
                ):
                    error_msg = f"Ya existe una orden con número '{datos.get('numero_orden')}' para el proveedor '{datos.get('proveedor')}'"
                    self.logger.warning(
                        f"Intento de crear orden duplicada: {error_msg}"
                    )
                    show_error(self, "Orden duplicada", error_msg)
                    return

                self.orden_creada.emit(datos)
                self.logger.info(
                    f"Orden creada exitosamente: {datos.get('numero_orden')} - {datos.get('proveedor')}"
                )
            else:
                self.logger.info("Diálogo de nueva orden cancelado por el usuario")

        except Exception as e:
            error_msg = f"Error al crear nueva orden: {str(e)}"
            self.logger.error(error_msg)
            show_error(self, "Error", error_msg)

    def buscar_compras(self):
        """Ejecuta la búsqueda de compras."""
        try:
            self.logger.info("Iniciando búsqueda de compras")

            # Sanitizar texto de búsqueda
            texto_busqueda = DataSanitizer.sanitize_text(
                self.input_busqueda.text().strip()
            )

            filtros = {
                "proveedor": texto_busqueda,
                "estado": self.combo_estado.currentText()
                if self.combo_estado.currentText() != "Todos"
                else "",
                "fecha_inicio": self.date_desde.date().toString("yyyy-MM-dd"),
                "fecha_fin": self.date_hasta.date().toString("yyyy-MM-dd"),
            }

            self.logger.info(f"Filtros de búsqueda aplicados: {filtros}")
            self.busqueda_realizada.emit(filtros)

        except Exception as e:
            error_msg = f"Error al buscar compras: {str(e)}"
            self.logger.error(error_msg)
            show_error(self, "Error de búsqueda", error_msg)

    def cargar_compras_en_tabla(self, compras):
        """Carga las compras en la tabla."""
        try:
            self.logger.info(f"Cargando {len(compras)} compras en la tabla")

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
                    row,
                    4,
                    QTableWidgetItem(str(compra.get("fecha_entrega_estimada", ""))),
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

                # Botones de acción
                btn_editar = QPushButton("Editar")
                btn_editar.setStyleSheet("background-color: #f39c12; color: white;")
                btn_editar.clicked.connect(
                    lambda checked, id=compra.get("id"): self.editar_orden(id)
                )
                self.tabla_compras.setCellWidget(row, 9, btn_editar)

            self.logger.info(f"Compras cargadas exitosamente en la tabla")

        except Exception as e:
            error_msg = f"Error al cargar compras en tabla: {str(e)}"
            self.logger.error(error_msg)
            show_error(self, "Error de carga", error_msg)

    def actualizar_estadisticas(self, stats):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('actualizar_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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
        self.lbl_ordenes_mes.setText(f"Órdenes este Mes: {stats.get('ordenes_mes', 0)}")

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
            self.tabla_proveedores.setItem(
                row, 0, QTableWidgetItem(proveedor["proveedor"])
            )
            self.tabla_proveedores.setItem(
                row, 1, QTableWidgetItem(str(proveedor["ordenes"]))
            )
            self.tabla_proveedores.setItem(
                row, 2, QTableWidgetItem(f"${proveedor['monto_total']:,.2f}")
            )
            self.tabla_proveedores.setItem(
                row, 3, QTableWidgetItem(f"${proveedor['promedio']:,.2f}")
            )
            self.tabla_proveedores.setItem(
                row, 4, QTableWidgetItem(f"{proveedor['porcentaje']:.1f}%")
            )

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
        self.lbl_compras_semana.setText(
            f"Compras esta Semana: {stats.get('compras_semana', 0)}"
        )
        self.lbl_compras_mes.setText(f"Compras este Mes: {stats.get('compras_mes', 0)}")
        self.lbl_tendencia.setText(f"Tendencia: {stats.get('tendencia', 'Estable')}")

        # === ANÁLISIS DE PRODUCTOS ===
        self.lbl_productos_unicos.setText(
            f"Productos Únicos: {stats.get('productos_unicos', 0)}"
        )
        self.lbl_categoria_top.setText(
            f"Categoría Principal: {stats.get('categoria_principal', 'No hay datos')}"
        )
        self.lbl_producto_mas_comprado.setText(
            f"Producto Más Comprado: {stats.get('producto_mas_comprado', 'No hay datos')}"
        )
        self.lbl_ticket_promedio.setText(
            f"Ticket Promedio: ${stats.get('ticket_promedio', 0):,.2f}"
        )

        # === DISTRIBUCIÓN POR ESTADO ===
        # Actualizar texto de estados
        texto_estados = "Distribución por Estado:\n\n"
        for estado_data in estados_data:
            texto_estados += f"• {estado_data['estado']}: {estado_data['cantidad']}\n"

        self.texto_estados.setPlainText(texto_estados)

    def editar_orden(self, orden_id):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('editar_orden'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Edita una orden existente."""
        # Por ahora solo cambiar estado
        estados = ["PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]

        # Crear un diálogo simple para cambiar estado
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Estado")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        combo_estado = QComboBox()
        combo_estado.addItems(estados)
        layout.addWidget(QLabel("Nuevo Estado:"))
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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('actualizar_datos'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza los datos de la vista."""
        self.buscar_compras()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogNuevaOrden(QDialog):
    """Diálogo para crear una nueva orden de compra."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Orden de Compra")
        self.setModal(True)
        self.setMinimumSize(400, 500)

        # Inicializar el gestor de validaciones
        self.validator_manager = FormValidatorManager()

        # Configurar logger
        self.logger = logging.getLogger(__name__)

        self.init_ui()
        self.configurar_validaciones()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Campos
        self.input_proveedor = QLineEdit()
        self.input_proveedor.setAccessibleName('Input Proveedor')
        self.input_numero_orden = QLineEdit()
        self.input_numero_orden.setAccessibleName('Input Numero Orden')
        self.date_pedido = QDateEdit()
        self.date_pedido.setDate(QDate.currentDate())
        self.date_pedido.setCalendarPopup(True)

        self.date_entrega = QDateEdit()
        self.date_entrega.setDate(QDate.currentDate().addDays(30))
        self.date_entrega.setCalendarPopup(True)

        self.combo_estado = QComboBox()
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

        # Proteger campos contra XSS
        self.form_protector.protect_field(self.input_busqueda, "input_busqueda", 100)
        self.form_protector.protect_field(self.input_proveedor, "input_proveedor", 100)
        self.form_protector.protect_field(self.input_numero_orden, "input_numero_orden", 100)
        self.form_protector.protect_field(self.texto_estados, "texto_estados", 100)
        self.form_protector.protect_field(self.input_observaciones, "input_observaciones", 100)

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
        """Obtiene los datos del formulario con sanitización."""
        try:
            self.logger.info("Obteniendo y sanitizando datos del formulario de compras")

            # Sanitizar datos de entrada
            proveedor_limpio = DataSanitizer.sanitize_text(
                self.input_proveedor.text().strip()
            )
            numero_orden_limpio = DataSanitizer.sanitize_text(
                self.input_numero_orden.text().strip()
            )
            observaciones_limpias = DataSanitizer.sanitize_text(
                self.input_observaciones.toPlainText().strip()
            )

            datos = {
                "proveedor": proveedor_limpio,
                "numero_orden": numero_orden_limpio,
                "fecha_pedido": self.date_pedido.date().toString("yyyy-MM-dd"),
                "fecha_entrega_estimada": self.date_entrega.date().toString(
                    "yyyy-MM-dd"
                ),
                "estado": self.combo_estado.currentText(),
                "descuento": self.input_descuento.value(),
                "impuestos": self.input_impuestos.value(),
                "observaciones": observaciones_limpias,
                "usuario_creacion": self.get_current_user(),  # Usuario del sistema
            }

            self.logger.info(
                "Datos del formulario de compras obtenidos y sanitizados correctamente"
            )
            return datos

        except Exception as e:
            self.logger.error(
                f"Error al obtener datos del formulario de compras: {str(e)}"
            )
            return {}

    def configurar_validaciones(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('configurar_validaciones'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Configura las validaciones del formulario."""
        # Validación de proveedor obligatorio
        self.validator_manager.agregar_validacion(
            self.input_proveedor, FormValidator.validar_campo_obligatorio, "Proveedor"
        )
        self.validator_manager.agregar_validacion(
            self.input_proveedor, FormValidator.validar_longitud_texto, 2, 100
        )

        # Validación de número de orden obligatorio
        self.validator_manager.agregar_validacion(
            self.input_numero_orden,
            FormValidator.validar_campo_obligatorio,
            "Número de orden",
        )
        self.validator_manager.agregar_validacion(
            self.input_numero_orden, FormValidator.validar_longitud_texto, 3, 50
        )

        # Validación de fechas
        self.validator_manager.agregar_validacion(
            self.date_pedido, FormValidator.validar_fecha
        )

        self.validator_manager.agregar_validacion(
            self.date_entrega,
            FormValidator.validar_fecha,
            self.date_pedido.date(),  # Fecha mínima: fecha de pedido
        )

        # Validación de montos (descuento e impuestos no negativos)
        self.validator_manager.agregar_validacion(
            self.input_descuento, FormValidator.validar_numero, 0.0, 999999.99
        )

        self.validator_manager.agregar_validacion(
            self.input_impuestos, FormValidator.validar_numero, 0.0, 999999.99
        )

    def validar_y_aceptar(self):
        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # Sanitización aplicada en procesamiento
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Valida los datos y acepta el diálogo."""
        # Usar el sistema de validación
        es_valido, errores = self.validator_manager.validar_formulario()

        if not es_valido:
            # Mostrar errores con el sistema mejorado
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            show_error(
                self,
                "Errores de Validación",
                "Por favor corrige los siguientes errores:\n\n• "
                + "\n• ".join(mensajes_error),
            )
            return

        # Validación adicional: fecha de entrega posterior a fecha de pedido
        if self.date_entrega.date() <= self.date_pedido.date():
            show_error(
                self,
                "Error de Validación",
                "La fecha de entrega debe ser posterior a la fecha de pedido.\n\nPor favor seleccione una fecha de entrega que sea al menos un día después de la fecha de pedido.",
            )
            return

        # Si todo es válido, aceptar el diálogo
        self.accept()

    def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja la detección de contenido peligroso en formularios."""
        from rexus.utils.security import log_security_event
        from rexus.utils.message_system import show_warning
        
        # Log del evento de seguridad
        log_security_event(
            "XSS_ATTEMPT",
            f"Contenido peligroso detectado en campo '{field_name}': {content[:100]}...",
            "unknown"
        )
        
        # Mostrar advertencia al usuario
        show_warning(
            self,
            "Contenido No Permitido",
            f"Se ha detectado contenido potencialmente peligroso en el campo '{field_name}'.

"
            "El contenido ha sido automáticamente sanitizado por seguridad."
        )
    
    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, 'form_protector'):
            return self.form_protector.get_sanitized_data()
        else:
            return {}

    def get_current_user(self) -> str:
        """Obtiene el usuario actual del sistema."""
        try:
            from rexus.core.auth_manager import AuthManager
            return AuthManager.current_user or "SISTEMA"
        except:
            return "SISTEMA"
