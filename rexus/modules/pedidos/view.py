"""
Vista de Pedidos Modernizada

Interfaz moderna para la gestión de pedidos del sistema.
"""

import json
from datetime import date, datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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

from rexus.utils.message_system import show_success, show_error, show_warning, ask_question
from rexus.modules.pedidos.improved_dialogs import PedidoDialogManager, PedidoDetalleDialog, PedidoEstadoDialog
from rexus.utils.format_utils import format_for_display, table_formatter, currency_formatter


class PedidosView(QWidget):
    """Vista modernizada para gestión de pedidos."""

    # Señales
    pedido_seleccionado = pyqtSignal(dict)
    solicitud_crear_pedido = pyqtSignal(dict)
    solicitud_actualizar_pedido = pyqtSignal(dict)
    solicitud_eliminar_pedido = pyqtSignal(str)
    solicitud_cambiar_estado = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.pedidos_data = []
        self.pedido_actual = None
        
        # Gestores de diálogos mejorados
        self.dialog_manager = None
        self.detalle_dialog = None
        self.estado_dialog = None

        self.init_ui()
        self.aplicar_estilos()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_widget = self.crear_header()
        layout.addWidget(header_widget)

        # Pestañas principales
        self.tab_widget = QTabWidget()

        # Pestaña de lista de pedidos
        tab_lista = self.crear_tab_lista()
        self.tab_widget.addTab(tab_lista, "📋 Lista de Pedidos")

        # Pestaña de creación/edición
        tab_edicion = self.crear_tab_edicion()
        self.tab_widget.addTab(tab_edicion, "📝 Editar Pedido")

        # Pestaña de estadísticas
        tab_estadisticas = self.crear_tab_estadisticas()
        self.tab_widget.addTab(tab_estadisticas, "📊 Estadísticas")

        layout.addWidget(self.tab_widget)

    def crear_header(self):
        """Crea el header con título y estadísticas."""
        header = QFrame()
        header.setFixedHeight(120)
        layout = QHBoxLayout(header)

        # Título
        titulo_container = QVBoxLayout()
        titulo = QLabel("📋 Gestión de Pedidos")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        subtitulo = QLabel("Administración de pedidos y órdenes de compra")
        subtitulo.setFont(QFont("Segoe UI", 12))

        titulo_container.addWidget(titulo)
        titulo_container.addWidget(subtitulo)
        titulo_container.addStretch()

        layout.addLayout(titulo_container)
        layout.addStretch()

        # Estadísticas
        stats_container = QHBoxLayout()

        self.stat_total = self.crear_stat_card("Total Pedidos", "0", "#3498db")
        self.stat_pendientes = self.crear_stat_card("Pendientes", "0", "#f39c12")
        self.stat_proceso = self.crear_stat_card("En Proceso", "0", "#9b59b6")
        self.stat_completados = self.crear_stat_card("Completados", "0", "#27ae60")

        stats_container.addWidget(self.stat_total)
        stats_container.addWidget(self.stat_pendientes)
        stats_container.addWidget(self.stat_proceso)
        stats_container.addWidget(self.stat_completados)

        layout.addLayout(stats_container)

        return header

    def crear_stat_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        card = QFrame()
        card.setFixedSize(120, 80)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)

        valor_label = QLabel(valor)
        valor_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        valor_label.setStyleSheet(f"color: {color};")

        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Segoe UI", 10))
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(valor_label)
        layout.addWidget(titulo_label)

        # Guardar referencias
        setattr(card, "valor_label", valor_label)
        setattr(card, "titulo_label", titulo_label)
        setattr(card, "color", color)

        return card

    def crear_tab_lista(self):
        """Crea la pestaña de lista de pedidos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Barra de herramientas
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar pedidos...")
        self.search_input.textChanged.connect(self.filtrar_pedidos)

        # Filtros
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(
            ["Todos", "Pendiente", "En Proceso", "Completado", "Cancelado"]
        )
        self.filtro_estado.currentTextChanged.connect(self.filtrar_pedidos)

        self.filtro_prioridad = QComboBox()
        self.filtro_prioridad.addItems(["Todas", "Baja", "Media", "Alta", "Urgente"])
        self.filtro_prioridad.currentTextChanged.connect(self.filtrar_pedidos)

        # Botones
        self.btn_nuevo_pedido = QPushButton("➕ Nuevo Pedido")
        self.btn_nuevo_pedido.clicked.connect(self.nuevo_pedido)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_pedidos)

        self.btn_exportar = QPushButton("📊 Exportar")
        self.btn_exportar.clicked.connect(self.exportar_pedidos)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.filtro_estado)
        toolbar_layout.addWidget(self.filtro_prioridad)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_nuevo_pedido)
        toolbar_layout.addWidget(self.btn_actualizar)
        toolbar_layout.addWidget(self.btn_exportar)

        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(8)
        self.tabla_pedidos.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "Cliente",
                "Estado",
                "Prioridad",
                "Total",
                "Responsable",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_pedidos.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.tabla_pedidos.setColumnWidth(0, 80)
        self.tabla_pedidos.setColumnWidth(1, 100)
        self.tabla_pedidos.setColumnWidth(3, 100)
        self.tabla_pedidos.setColumnWidth(4, 80)
        self.tabla_pedidos.setColumnWidth(5, 100)
        self.tabla_pedidos.setColumnWidth(7, 120)

        self.tabla_pedidos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.itemSelectionChanged.connect(self.on_pedido_seleccionado)

        layout.addWidget(toolbar)
        layout.addWidget(self.tabla_pedidos)

        return widget

    def crear_tab_edicion(self):
        """Crea la pestaña de edición de pedidos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Información del pedido
        info_group = QGroupBox("Información del Pedido")
        info_layout = QFormLayout(info_group)

        self.input_numero = QLineEdit()
        self.input_numero.setEnabled(False)
        self.date_pedido = QDateEdit()
        self.date_pedido.setDate(QDate.currentDate())
        self.input_cliente = QLineEdit()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(
            ["Pendiente", "En Proceso", "Completado", "Cancelado"]
        )
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItems(["Baja", "Media", "Alta", "Urgente"])
        self.input_responsable = QLineEdit()

        info_layout.addRow("Número:", self.input_numero)
        info_layout.addRow("Fecha:", self.date_pedido)
        info_layout.addRow("Cliente:", self.input_cliente)
        info_layout.addRow("Estado:", self.combo_estado)
        info_layout.addRow("Prioridad:", self.combo_prioridad)
        info_layout.addRow("Responsable:", self.input_responsable)

        # Detalles del pedido
        detalles_group = QGroupBox("Detalles del Pedido")
        detalles_layout = QVBoxLayout(detalles_group)

        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio Unit.", "Subtotal", "Acciones"]
        )
        self.tabla_productos.setMaximumHeight(200)

        # Botones para productos
        productos_botones = QHBoxLayout()
        self.btn_agregar_producto = QPushButton("➕ Agregar Producto")
        self.btn_agregar_producto.clicked.connect(self.agregar_producto)
        productos_botones.addWidget(self.btn_agregar_producto)
        productos_botones.addStretch()

        detalles_layout.addWidget(self.tabla_productos)
        detalles_layout.addLayout(productos_botones)

        # Resumen financiero
        resumen_group = QGroupBox("Resumen Financiero")
        resumen_layout = QFormLayout(resumen_group)

        self.input_subtotal = QDoubleSpinBox()
        self.input_subtotal.setEnabled(False)
        self.input_subtotal.setMaximum(999999.99)
        self.input_descuento = QDoubleSpinBox()
        self.input_descuento.setMaximum(999999.99)
        self.input_impuestos = QDoubleSpinBox()
        self.input_impuestos.setEnabled(False)
        self.input_impuestos.setMaximum(999999.99)
        self.input_total = QDoubleSpinBox()
        self.input_total.setEnabled(False)
        self.input_total.setMaximum(999999.99)

        resumen_layout.addRow("Subtotal:", self.input_subtotal)
        resumen_layout.addRow("Descuento:", self.input_descuento)
        resumen_layout.addRow("Impuestos:", self.input_impuestos)
        resumen_layout.addRow("Total:", self.input_total)

        # Notas
        notas_group = QGroupBox("Notas y Observaciones")
        notas_layout = QVBoxLayout(notas_group)

        self.text_notas = QTextEdit()
        self.text_notas.setMaximumHeight(100)
        notas_layout.addWidget(self.text_notas)

        # Botones de acción
        botones_layout = QHBoxLayout()

        self.btn_guardar_pedido = QPushButton("💾 Guardar Pedido")
        self.btn_guardar_pedido.clicked.connect(self.guardar_pedido)

        self.btn_cancelar_edicion = QPushButton("❌ Cancelar")
        self.btn_cancelar_edicion.clicked.connect(self.cancelar_edicion)

        self.btn_imprimir = QPushButton("🖨️ Imprimir")
        self.btn_imprimir.clicked.connect(self.imprimir_pedido)

        botones_layout.addWidget(self.btn_guardar_pedido)
        botones_layout.addWidget(self.btn_cancelar_edicion)
        botones_layout.addWidget(self.btn_imprimir)
        botones_layout.addStretch()

        # Agregar grupos al scroll
        scroll_layout.addWidget(info_group)
        scroll_layout.addWidget(detalles_group)
        scroll_layout.addWidget(resumen_group)
        scroll_layout.addWidget(notas_group)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        layout.addLayout(botones_layout)

        return widget

    def crear_tab_estadisticas(self):
        """Crea la pestaña de estadísticas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Filtros de período
        filtros_layout = QHBoxLayout()

        filtros_layout.addWidget(QLabel("Período:"))
        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())

        filtros_layout.addWidget(self.date_desde)
        filtros_layout.addWidget(QLabel("hasta"))
        filtros_layout.addWidget(self.date_hasta)

        btn_actualizar_stats = QPushButton("🔄 Actualizar")
        btn_actualizar_stats.clicked.connect(self.actualizar_estadisticas)
        filtros_layout.addWidget(btn_actualizar_stats)
        filtros_layout.addStretch()

        layout.addLayout(filtros_layout)

        # Métricas principales
        metricas_layout = QHBoxLayout()

        self.stat_ventas_mes = self.crear_stat_card(
            "Ventas del Mes", "$0.00", "#3498db"
        )
        self.stat_pedidos_mes = self.crear_stat_card("Pedidos del Mes", "0", "#27ae60")
        self.stat_promedio_pedido = self.crear_stat_card(
            "Promedio por Pedido", "$0.00", "#f39c12"
        )
        self.stat_tiempo_promedio = self.crear_stat_card(
            "Tiempo Promedio", "0 días", "#9b59b6"
        )

        metricas_layout.addWidget(self.stat_ventas_mes)
        metricas_layout.addWidget(self.stat_pedidos_mes)
        metricas_layout.addWidget(self.stat_promedio_pedido)
        metricas_layout.addWidget(self.stat_tiempo_promedio)

        layout.addLayout(metricas_layout)

        # Gráficos placeholder
        graficos_group = QGroupBox("Análisis de Tendencias")
        graficos_layout = QVBoxLayout(graficos_group)

        placeholder_label = QLabel("📊 Gráficos de análisis (próximamente)")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(
            "color: #7f8c8d; font-size: 18px; padding: 50px;"
        )

        graficos_layout.addWidget(placeholder_label)

        layout.addWidget(graficos_group)
        layout.addStretch()

        return widget

    def aplicar_estilos(self):
        """Aplica estilos modernos al widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }

            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }

            QTabBar::tab {
                background: linear-gradient(135deg, #ecf0f1, #d5dbdb);
                border: 1px solid #bdc3c7;
                border-bottom: none;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #2c3e50;
            }

            QTabBar::tab:selected {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border-bottom: 2px solid #3498db;
            }

            QTabBar::tab:hover {
                background: linear-gradient(135deg, #d5dbdb, #bdc3c7);
            }

            QLabel {
                color: #2c3e50;
                font-weight: 500;
            }

            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }

            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }

            QPushButton {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }

            QPushButton:hover {
                background: linear-gradient(135deg, #2980b9, #1f618d);
            }

            QPushButton:pressed {
                background: linear-gradient(135deg, #1f618d, #154360);
            }

            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }

            QHeaderView::section {
                background: linear-gradient(135deg, #34495e, #2c3e50);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                min-width: 100px;
            }

            QComboBox:focus {
                border-color: #3498db;
            }

            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }

            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }

            QTextEdit:focus {
                border-color: #3498db;
            }

            QDateEdit, QDoubleSpinBox, QSpinBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }

            QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border-color: #3498db;
            }
        """)

    def cargar_pedidos_en_tabla(self, pedidos):
        """Carga la lista de pedidos en la tabla."""
        self.pedidos_data = pedidos
        self.tabla_pedidos.setRowCount(len(pedidos))

        for row, pedido in enumerate(pedidos):
            # ID
            item_id = QTableWidgetItem(str(pedido.get("id", "")))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_pedidos.setItem(row, 0, item_id)

            # Fecha
            fecha = pedido.get("fecha", "")
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    pass
            self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(fecha))

            # Cliente
            self.tabla_pedidos.setItem(
                row, 2, QTableWidgetItem(pedido.get("cliente", ""))
            )

            # Estado
            estado = pedido.get("estado", "")
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Colorear según estado
            if estado == "Completado":
                item_estado.setBackground(QColor("#d4edda"))
                item_estado.setForeground(QColor("#155724"))
            elif estado == "En Proceso":
                item_estado.setBackground(QColor("#d1ecf1"))
                item_estado.setForeground(QColor("#0c5460"))
            elif estado == "Pendiente":
                item_estado.setBackground(QColor("#fff3cd"))
                item_estado.setForeground(QColor("#856404"))
            elif estado == "Cancelado":
                item_estado.setBackground(QColor("#f8d7da"))
                item_estado.setForeground(QColor("#721c24"))

            self.tabla_pedidos.setItem(row, 3, item_estado)

            # Prioridad
            prioridad = pedido.get("prioridad", "")
            item_prioridad = QTableWidgetItem(prioridad)
            item_prioridad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Colorear según prioridad
            if prioridad == "Urgente":
                item_prioridad.setBackground(QColor("#f8d7da"))
                item_prioridad.setForeground(QColor("#721c24"))
            elif prioridad == "Alta":
                item_prioridad.setBackground(QColor("#fff3cd"))
                item_prioridad.setForeground(QColor("#856404"))
            elif prioridad == "Media":
                item_prioridad.setBackground(QColor("#d1ecf1"))
                item_prioridad.setForeground(QColor("#0c5460"))
            else:  # Baja
                item_prioridad.setBackground(QColor("#d4edda"))
                item_prioridad.setForeground(QColor("#155724"))

            self.tabla_pedidos.setItem(row, 4, item_prioridad)

            # Total
            total = pedido.get("total", 0)
            item_total = QTableWidgetItem(f"${total:,.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_pedidos.setItem(row, 5, item_total)

            # Responsable
            self.tabla_pedidos.setItem(
                row, 6, QTableWidgetItem(pedido.get("responsable", ""))
            )

            # Botón de acciones
            btn_acciones = QPushButton("⚙️ Acciones")
            btn_acciones.clicked.connect(lambda: self.mostrar_acciones(pedido))
            self.tabla_pedidos.setCellWidget(row, 7, btn_acciones)

        # Actualizar estadísticas
        self.actualizar_estadisticas_header()

    def actualizar_estadisticas_header(self):
        """Actualiza las estadísticas del header."""
        if not self.pedidos_data:
            return

        total = len(self.pedidos_data)
        pendientes = len(
            [p for p in self.pedidos_data if p.get("estado") == "Pendiente"]
        )
        proceso = len([p for p in self.pedidos_data if p.get("estado") == "En Proceso"])
        completados = len(
            [p for p in self.pedidos_data if p.get("estado") == "Completado"]
        )

        self.stat_total.valor_label.setText(str(total))
        self.stat_pendientes.valor_label.setText(str(pendientes))
        self.stat_proceso.valor_label.setText(str(proceso))
        self.stat_completados.valor_label.setText(str(completados))

    def filtrar_pedidos(self):
        """Filtra pedidos según los criterios seleccionados."""
        texto_busqueda = self.search_input.text().lower()
        estado_filtro = self.filtro_estado.currentText()
        prioridad_filtro = self.filtro_prioridad.currentText()

        for row in range(self.tabla_pedidos.rowCount()):
            mostrar_fila = True

            # Filtro por texto
            if texto_busqueda:
                cliente = self.tabla_pedidos.item(row, 2).text().lower()
                pedido_id = self.tabla_pedidos.item(row, 0).text().lower()
                responsable = self.tabla_pedidos.item(row, 6).text().lower()

                if not (
                    texto_busqueda in cliente
                    or texto_busqueda in pedido_id
                    or texto_busqueda in responsable
                ):
                    mostrar_fila = False

            # Filtro por estado
            if estado_filtro != "Todos":
                estado_actual = self.tabla_pedidos.item(row, 3).text()
                if estado_actual != estado_filtro:
                    mostrar_fila = False

            # Filtro por prioridad
            if prioridad_filtro != "Todas":
                prioridad_actual = self.tabla_pedidos.item(row, 4).text()
                if prioridad_actual != prioridad_filtro:
                    mostrar_fila = False

            self.tabla_pedidos.setRowHidden(row, not mostrar_fila)

    def on_pedido_seleccionado(self):
        """Maneja la selección de un pedido."""
        fila_actual = self.tabla_pedidos.currentRow()
        if fila_actual >= 0:
            pedido_id = self.tabla_pedidos.item(fila_actual, 0).text()
            pedido = next(
                (p for p in self.pedidos_data if str(p.get("id")) == pedido_id), None
            )

            if pedido:
                self.pedido_actual = pedido
                self.cargar_pedido_en_formulario(pedido)

    def cargar_pedido_en_formulario(self, pedido):
        """Carga los datos del pedido en el formulario de edición."""
        self.input_numero.setText(str(pedido.get("id", "")))
        self.input_cliente.setText(pedido.get("cliente", ""))
        self.combo_estado.setCurrentText(pedido.get("estado", "Pendiente"))
        self.combo_prioridad.setCurrentText(pedido.get("prioridad", "Media"))
        self.input_responsable.setText(pedido.get("responsable", ""))

        # Fecha
        fecha = pedido.get("fecha", "")
        if fecha:
            try:
                if isinstance(fecha, str):
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                    self.date_pedido.setDate(QDate(fecha_obj))
            except:
                pass

        # Totales
        self.input_subtotal.setValue(pedido.get("subtotal", 0))
        self.input_descuento.setValue(pedido.get("descuento", 0))
        self.input_impuestos.setValue(pedido.get("impuestos", 0))
        self.input_total.setValue(pedido.get("total", 0))

        # Notas
        self.text_notas.setText(pedido.get("notas", ""))

        # Cambiar a pestaña de edición
        self.tab_widget.setCurrentIndex(1)

    def nuevo_pedido(self):
        """Crea un nuevo pedido."""
        self.pedido_actual = None
        self.limpiar_formulario()
        self.tab_widget.setCurrentIndex(1)

    def limpiar_formulario(self):
        """Limpia el formulario de edición."""
        self.input_numero.clear()
        self.input_cliente.clear()
        self.combo_estado.setCurrentText("Pendiente")
        self.combo_prioridad.setCurrentText("Media")
        self.input_responsable.clear()
        self.date_pedido.setDate(QDate.currentDate())
        self.input_subtotal.setValue(0)
        self.input_descuento.setValue(0)
        self.input_impuestos.setValue(0)
        self.input_total.setValue(0)
        self.text_notas.clear()
        self.tabla_productos.setRowCount(0)

    def guardar_pedido(self):
        """Guarda el pedido actual."""
        datos_pedido = {
            "cliente": self.input_cliente.text(),
            "estado": self.combo_estado.currentText(),
            "prioridad": self.combo_prioridad.currentText(),
            "responsable": self.input_responsable.text(),
            "fecha": self.date_pedido.date().toString("yyyy-MM-dd"),
            "subtotal": self.input_subtotal.value(),
            "descuento": self.input_descuento.value(),
            "impuestos": self.input_impuestos.value(),
            "total": self.input_total.value(),
            "notas": self.text_notas.toPlainText(),
        }

        if self.pedido_actual:
            datos_pedido["id"] = self.pedido_actual["id"]
            self.solicitud_actualizar_pedido.emit(datos_pedido)
        else:
            self.solicitud_crear_pedido.emit(datos_pedido)

    def cancelar_edicion(self):
        """Cancela la edición actual."""
        self.tab_widget.setCurrentIndex(0)

    def agregar_producto(self):
        """Agrega un producto al pedido."""
        # Aquí implementarías un diálogo para agregar productos
        pass

    def mostrar_acciones(self, pedido):
        """Muestra el menú de acciones para un pedido."""
        # Aquí implementarías un menú contextual
        pass

    def exportar_pedidos(self):
        """Exporta los pedidos a un archivo."""
        # Aquí implementarías la funcionalidad de exportación
        pass

    def imprimir_pedido(self):
        """Imprime el pedido actual."""
        # Aquí implementarías la funcionalidad de impresión
        pass

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas de la pestaña correspondiente."""
        # Aquí implementarías la actualización de estadísticas
        pass

    def cargar_pedidos(self):
        """Solicita la carga de pedidos al controlador."""
        if self.controller:
            self.controller.cargar_pedidos()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
        
        # Inicializar gestores de diálogos con el controlador
        self.dialog_manager = PedidoDialogManager(self, controller)
        self.detalle_dialog = PedidoDetalleDialog(self, controller)
        self.estado_dialog = PedidoEstadoDialog(self, controller)
        
        if hasattr(self.controller, "cargar_pedidos"):
            self.controller.cargar_pedidos()
    
    # ===== MÉTODOS MEJORADOS CON NUEVAS UTILIDADES =====
    
    def crear_pedido_mejorado(self):
        """Crea un nuevo pedido usando el sistema de diálogos mejorado."""
        if self.dialog_manager:
            success = self.dialog_manager.show_create_dialog()
            if success:
                self.cargar_pedidos()  # Recargar la tabla
    
    def editar_pedido_mejorado(self):
        """Edita el pedido seleccionado usando el sistema mejorado."""
        if not self.pedido_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un pedido para editar.")
            return
        
        if self.dialog_manager:
            success = self.dialog_manager.show_edit_dialog(self.pedido_actual)
            if success:
                self.cargar_pedidos()  # Recargar la tabla
    
    def eliminar_pedido_mejorado(self):
        """Elimina el pedido seleccionado usando confirmación mejorada."""
        if not self.pedido_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un pedido para eliminar.")
            return
        
        if self.dialog_manager:
            success = self.dialog_manager.confirm_and_delete(self.pedido_actual)
            if success:
                self.cargar_pedidos()  # Recargar la tabla
    
    def gestionar_detalle_mejorado(self):
        """Gestiona el detalle del pedido seleccionado."""
        if not self.pedido_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un pedido para gestionar su detalle.")
            return
        
        if self.detalle_dialog:
            self.detalle_dialog.show_detalle_dialog(self.pedido_actual)
    
    def cambiar_estado_mejorado(self):
        """Cambia el estado del pedido seleccionado."""
        if not self.pedido_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un pedido para cambiar su estado.")
            return
        
        if self.estado_dialog:
            success = self.estado_dialog.show_cambiar_estado_dialog(self.pedido_actual)
            if success:
                self.cargar_pedidos()  # Recargar la tabla
    
    def on_pedido_seleccionado(self):
        """Maneja la selección de pedido en la tabla."""
        current_row = self.tabla_pedidos.currentRow()
        if current_row >= 0:
            # Obtener datos del pedido seleccionado
            pedido_id = self.tabla_pedidos.item(current_row, 0).text()
            pedido_data = next(
                (p for p in self.pedidos_data if str(p.get('id', '')) == pedido_id), 
                None
            )
            
            if pedido_data:
                self.pedido_actual = pedido_data
                
                # Habilitar botones de acción si existen
                self._habilitar_botones_accion(True)
                
                # Emitir señal
                self.pedido_seleccionado.emit(pedido_data)
        else:
            self.pedido_actual = None
            self._habilitar_botones_accion(False)
    
    def _habilitar_botones_accion(self, habilitar: bool):
        """Habilita o deshabilita los botones de acción según la selección."""
        if hasattr(self, 'btn_editar'):
            self.btn_editar.setEnabled(habilitar)
        if hasattr(self, 'btn_eliminar'):
            self.btn_eliminar.setEnabled(habilitar)
        if hasattr(self, 'btn_detalle'):
            self.btn_detalle.setEnabled(habilitar)
        if hasattr(self, 'btn_cambiar_estado'):
            self.btn_cambiar_estado.setEnabled(habilitar)
    
    def cargar_pedidos_con_formato(self, pedidos):
        """Carga pedidos en la tabla con formateo consistente."""
        if not pedidos:
            return
        
        self.pedidos_data = pedidos
        
        # Usar formatters de utilidades para consistencia
        formatters = table_formatter.create_default_formatters()
        formatted_data = table_formatter.format_table_data(pedidos, formatters)
        
        # Cargar en tabla existente
        if hasattr(self, 'tabla_pedidos'):
            self.cargar_en_tabla_pedidos(formatted_data)
