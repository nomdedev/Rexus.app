"""
Vista de Logística Modernizada

Interfaz moderna para la gestión de logística y transporte.
"""

from datetime import datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogisticaView(QWidget):
    """Vista modernizada para gestión de logística."""

    # Señales
    envio_seleccionado = pyqtSignal(dict)
    solicitud_crear_envio = pyqtSignal(dict)
    solicitud_actualizar_envio = pyqtSignal(dict)
    solicitud_cancelar_envio = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.envios_data = []
        self.envio_actual = None

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

        # Pestaña de envíos
        tab_envios = self.crear_tab_envios()
        self.tab_widget.addTab(tab_envios, "📦 Envíos")

        # Pestaña de rutas
        tab_rutas = self.crear_tab_rutas()
        self.tab_widget.addTab(tab_rutas, "🗺️ Rutas")

        # Pestaña de vehículos
        tab_vehiculos = self.crear_tab_vehiculos()
        self.tab_widget.addTab(tab_vehiculos, "🚚 Vehículos")

        # Pestaña de tracking
        tab_tracking = self.crear_tab_tracking()
        self.tab_widget.addTab(tab_tracking, "📍 Tracking")

        layout.addWidget(self.tab_widget)

    def crear_header(self):
        """Crea el header con título y estadísticas."""
        header = QFrame()
        header.setFixedHeight(120)
        layout = QHBoxLayout(header)

        # Título
        titulo_container = QVBoxLayout()
        titulo = QLabel("🚚 Gestión de Logística")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        subtitulo = QLabel("Control de envíos, rutas y transporte")
        subtitulo.setFont(QFont("Segoe UI", 12))

        titulo_container.addWidget(titulo)
        titulo_container.addWidget(subtitulo)
        titulo_container.addStretch()

        layout.addLayout(titulo_container)
        layout.addStretch()

        # Estadísticas
        stats_container = QHBoxLayout()

        self.stat_envios_activos = self.crear_stat_card(
            "Envíos Activos", "0", "#3498db"
        )
        self.stat_en_ruta = self.crear_stat_card("En Ruta", "0", "#f39c12")
        self.stat_entregados = self.crear_stat_card("Entregados Hoy", "0", "#27ae60")
        self.stat_vehiculos = self.crear_stat_card("Vehículos", "0", "#9b59b6")

        stats_container.addWidget(self.stat_envios_activos)
        stats_container.addWidget(self.stat_en_ruta)
        stats_container.addWidget(self.stat_entregados)
        stats_container.addWidget(self.stat_vehiculos)

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

    def crear_tab_envios(self):
        """Crea la pestaña de envíos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Barra de herramientas
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)

        # Búsqueda
        self.search_envios = QLineEdit()
        self.search_envios.setPlaceholderText("🔍 Buscar envíos...")
        self.search_envios.textChanged.connect(self.filtrar_envios)

        # Filtros
        self.filtro_estado_envio = QComboBox()
        self.filtro_estado_envio.addItems(
            ["Todos", "Preparando", "En Ruta", "Entregado", "Cancelado"]
        )
        self.filtro_estado_envio.currentTextChanged.connect(self.filtrar_envios)

        self.filtro_transportista = QComboBox()
        self.filtro_transportista.addItems(["Todos", "Interno", "Externo"])
        self.filtro_transportista.currentTextChanged.connect(self.filtrar_envios)

        # Botones
        self.btn_nuevo_envio = QPushButton("➕ Nuevo Envío")
        self.btn_nuevo_envio.clicked.connect(self.nuevo_envio)

        self.btn_actualizar_envios = QPushButton("🔄 Actualizar")
        self.btn_actualizar_envios.clicked.connect(self.cargar_envios)

        toolbar_layout.addWidget(self.search_envios)
        toolbar_layout.addWidget(self.filtro_estado_envio)
        toolbar_layout.addWidget(self.filtro_transportista)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_nuevo_envio)
        toolbar_layout.addWidget(self.btn_actualizar_envios)

        # Tabla de envíos
        self.tabla_envios = QTableWidget()
        self.tabla_envios.setColumnCount(8)
        self.tabla_envios.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "Destino",
                "Estado",
                "Transportista",
                "Progreso",
                "Estimado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_envios.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.tabla_envios.setColumnWidth(0, 80)
        self.tabla_envios.setColumnWidth(1, 100)
        self.tabla_envios.setColumnWidth(3, 100)
        self.tabla_envios.setColumnWidth(5, 120)
        self.tabla_envios.setColumnWidth(6, 100)
        self.tabla_envios.setColumnWidth(7, 120)

        self.tabla_envios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_envios.setAlternatingRowColors(True)
        self.tabla_envios.itemSelectionChanged.connect(self.on_envio_seleccionado)

        layout.addWidget(toolbar)
        layout.addWidget(self.tabla_envios)

        return widget

    def crear_tab_rutas(self):
        """Crea la pestaña de rutas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Herramientas de rutas
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)

        self.btn_planificar_ruta = QPushButton("🗺️ Planificar Ruta")
        self.btn_optimizar_rutas = QPushButton("⚡ Optimizar Rutas")
        self.btn_ver_mapa = QPushButton("🌍 Ver Mapa")

        toolbar_layout.addWidget(self.btn_planificar_ruta)
        toolbar_layout.addWidget(self.btn_optimizar_rutas)
        toolbar_layout.addWidget(self.btn_ver_mapa)
        toolbar_layout.addStretch()

        # Tabla de rutas
        self.tabla_rutas = QTableWidget()
        self.tabla_rutas.setColumnCount(6)
        self.tabla_rutas.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Distancia", "Tiempo Est.", "Envíos", "Estado"]
        )

        # Configurar tabla de rutas
        header_rutas = self.tabla_rutas.horizontalHeader()
        if header_rutas:
            header_rutas.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header_rutas.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header_rutas.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header_rutas.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header_rutas.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            header_rutas.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        self.tabla_rutas.setAlternatingRowColors(True)

        layout.addWidget(toolbar)
        layout.addWidget(self.tabla_rutas)

        return widget

    def crear_tab_vehiculos(self):
        """Crea la pestaña de vehículos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Herramientas de vehículos
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)

        self.btn_nuevo_vehiculo = QPushButton("🚚 Nuevo Vehículo")
        self.btn_mantenimiento = QPushButton("🔧 Mantenimiento")
        self.btn_disponibilidad = QPushButton("📊 Disponibilidad")

        toolbar_layout.addWidget(self.btn_nuevo_vehiculo)
        toolbar_layout.addWidget(self.btn_mantenimiento)
        toolbar_layout.addWidget(self.btn_disponibilidad)
        toolbar_layout.addStretch()

        # Tabla de vehículos
        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(7)
        self.tabla_vehiculos.setHorizontalHeaderLabels(
            ["ID", "Placa", "Tipo", "Conductor", "Estado", "Capacidad", "Ubicación"]
        )

        # Configurar tabla de vehículos
        header_vehiculos = self.tabla_vehiculos.horizontalHeader()
        if header_vehiculos:
            header_vehiculos.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header_vehiculos.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header_vehiculos.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header_vehiculos.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header_vehiculos.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            header_vehiculos.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
            header_vehiculos.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.tabla_vehiculos.setAlternatingRowColors(True)

        layout.addWidget(toolbar)
        layout.addWidget(self.tabla_vehiculos)

        return widget

    def crear_tab_tracking(self):
        """Crea la pestaña de tracking."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Panel de seguimiento
        tracking_panel = QFrame()
        tracking_layout = QVBoxLayout(tracking_panel)

        # Búsqueda de tracking
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Código de Seguimiento:"))

        self.input_tracking = QLineEdit()
        self.input_tracking.setPlaceholderText("Ingrese código de seguimiento...")

        self.btn_buscar_tracking = QPushButton("🔍 Buscar")
        self.btn_buscar_tracking.clicked.connect(self.buscar_tracking)

        search_layout.addWidget(self.input_tracking)
        search_layout.addWidget(self.btn_buscar_tracking)
        search_layout.addStretch()

        tracking_layout.addLayout(search_layout)

        # Información del envío
        info_group = QGroupBox("Información del Envío")
        info_layout = QFormLayout(info_group)

        self.lbl_tracking_id = QLabel("---")
        self.lbl_tracking_origen = QLabel("---")
        self.lbl_tracking_destino = QLabel("---")
        self.lbl_tracking_estado = QLabel("---")
        self.lbl_tracking_fecha = QLabel("---")

        info_layout.addRow("ID:", self.lbl_tracking_id)
        info_layout.addRow("Origen:", self.lbl_tracking_origen)
        info_layout.addRow("Destino:", self.lbl_tracking_destino)
        info_layout.addRow("Estado:", self.lbl_tracking_estado)
        info_layout.addRow("Fecha:", self.lbl_tracking_fecha)

        tracking_layout.addWidget(info_group)

        # Historial de tracking
        historial_group = QGroupBox("Historial de Seguimiento")
        historial_layout = QVBoxLayout(historial_group)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(4)
        self.tabla_historial.setHorizontalHeaderLabels(
            ["Fecha/Hora", "Ubicación", "Estado", "Observaciones"]
        )

        historial_layout.addWidget(self.tabla_historial)

        tracking_layout.addWidget(historial_group)

        layout.addWidget(tracking_panel)

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

            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: #ecf0f1;
                text-align: center;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background: linear-gradient(135deg, #3498db, #2980b9);
                border-radius: 4px;
            }
        """)

    def cargar_envios_en_tabla(self, envios):
        """Carga la lista de envíos en la tabla."""
        self.envios_data = envios
        self.tabla_envios.setRowCount(len(envios))

        for row, envio in enumerate(envios):
            # ID
            item_id = QTableWidgetItem(str(envio.get("id", "")))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_envios.setItem(row, 0, item_id)

            # Fecha
            fecha = envio.get("fecha", "")
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    pass
            self.tabla_envios.setItem(row, 1, QTableWidgetItem(fecha))

            # Destino
            self.tabla_envios.setItem(
                row, 2, QTableWidgetItem(envio.get("destino", ""))
            )

            # Estado
            estado = envio.get("estado", "")
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Colorear según estado
            if estado == "Entregado":
                item_estado.setBackground(QColor("#d4edda"))
                item_estado.setForeground(QColor("#155724"))
            elif estado == "En Ruta":
                item_estado.setBackground(QColor("#d1ecf1"))
                item_estado.setForeground(QColor("#0c5460"))
            elif estado == "Preparando":
                item_estado.setBackground(QColor("#fff3cd"))
                item_estado.setForeground(QColor("#856404"))
            elif estado == "Cancelado":
                item_estado.setBackground(QColor("#f8d7da"))
                item_estado.setForeground(QColor("#721c24"))

            self.tabla_envios.setItem(row, 3, item_estado)

            # Transportista
            self.tabla_envios.setItem(
                row, 4, QTableWidgetItem(envio.get("transportista", ""))
            )

            # Progreso
            progreso = envio.get("progreso", 0)
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setValue(progreso)
            progress_bar.setFormat(f"{progreso}%")
            self.tabla_envios.setCellWidget(row, 5, progress_bar)

            # Estimado
            estimado = envio.get("fecha_estimada", "")
            if isinstance(estimado, str):
                try:
                    estimado = datetime.strptime(estimado, "%Y-%m-%d").strftime("%d/%m")
                except Exception:
                    pass
            self.tabla_envios.setItem(row, 6, QTableWidgetItem(estimado))

            # Botón de acciones
            btn_acciones = QPushButton("⚙️ Acciones")
            btn_acciones.clicked.connect(lambda: self.mostrar_acciones_envio(envio))
            self.tabla_envios.setCellWidget(row, 7, btn_acciones)

        # Actualizar estadísticas
        self.actualizar_estadisticas_header()

    def actualizar_estadisticas_header(self):
        """Actualiza las estadísticas del header."""
        if not self.envios_data:
            return

        activos = len([e for e in self.envios_data if e.get("estado") != "Entregado"])
        en_ruta = len([e for e in self.envios_data if e.get("estado") == "En Ruta"])

        # Entregados hoy (simulado)
        entregados_hoy = len(
            [e for e in self.envios_data if e.get("estado") == "Entregado"]
        )

        # Total vehículos (simulado)
        vehiculos = 5

        self.stat_envios_activos.valor_label.setText(str(activos))
        self.stat_en_ruta.valor_label.setText(str(en_ruta))
        self.stat_entregados.valor_label.setText(str(entregados_hoy))
        self.stat_vehiculos.valor_label.setText(str(vehiculos))

    def filtrar_envios(self):
        """Filtra envíos según los criterios seleccionados."""
        texto_busqueda = self.search_envios.text().lower()
        estado_filtro = self.filtro_estado_envio.currentText()
        transportista_filtro = self.filtro_transportista.currentText()

        for row in range(self.tabla_envios.rowCount()):
            mostrar_fila = True

            # Filtro por texto
            if texto_busqueda:
                item_id = self.tabla_envios.item(row, 0)
                item_destino = self.tabla_envios.item(row, 2)
                item_transportista = self.tabla_envios.item(row, 4)

                if item_id and item_destino and item_transportista:
                    envio_id = item_id.text().lower()
                    destino = item_destino.text().lower()
                    transportista = item_transportista.text().lower()

                    if not (
                        texto_busqueda in envio_id
                        or texto_busqueda in destino
                        or texto_busqueda in transportista
                    ):
                        mostrar_fila = False

            # Filtro por estado
            if estado_filtro != "Todos":
                item_estado = self.tabla_envios.item(row, 3)
                if item_estado and item_estado.text() != estado_filtro:
                    mostrar_fila = False

            # Filtro por transportista
            if transportista_filtro != "Todos":
                item_transportista = self.tabla_envios.item(row, 4)
                if item_transportista:
                    # Simplificado: Interno si contiene la empresa, Externo si no
                    es_interno = "empresa" in item_transportista.text().lower()
                    if (transportista_filtro == "Interno" and not es_interno) or (
                        transportista_filtro == "Externo" and es_interno
                    ):
                        mostrar_fila = False

            self.tabla_envios.setRowHidden(row, not mostrar_fila)

    def on_envio_seleccionado(self):
        """Maneja la selección de un envío."""
        fila_actual = self.tabla_envios.currentRow()
        if fila_actual >= 0:
            item_id = self.tabla_envios.item(fila_actual, 0)
            if item_id:
                envio_id = item_id.text()
                envio = next(
                    (e for e in self.envios_data if str(e.get("id")) == envio_id), None
                )

                if envio:
                    self.envio_actual = envio
                    self.envio_seleccionado.emit(envio)

    def nuevo_envio(self):
        """Crea un nuevo envío."""
        # Aquí implementarías un diálogo para crear envío
        pass

    def mostrar_acciones_envio(self, envio):
        """Muestra las acciones disponibles para un envío."""
        # Aquí implementarías un menú contextual
        pass

    def buscar_tracking(self):
        """Busca información de tracking."""
        codigo = self.input_tracking.text()
        if codigo:
            # Aquí implementarías la búsqueda de tracking
            pass

    def cargar_envios(self):
        """Solicita la carga de envíos al controlador."""
        if self.controller:
            self.controller.cargar_envios()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
