"""
Vista de Herrajes

Interfaz modernizada para gestión de herrajes por obra.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HerrajesView(QWidget):
    """Vista principal para gestión de herrajes."""

    # Señales
    buscar_herrajes = pyqtSignal(str)
    filtrar_herrajes = pyqtSignal(dict)
    asignar_herraje_obra = pyqtSignal(int, int, float, str)
    crear_pedido_obra = pyqtSignal(int, str, list)
    obtener_estadisticas = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("🔧 Gestión de Herrajes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # Panel de estadísticas
        self.create_statistics_panel()
        main_layout.addWidget(self.stats_frame)

        # Panel de filtros y búsqueda
        self.create_filters_panel()
        main_layout.addWidget(self.filters_frame)

        # Panel de herrajes
        self.create_herrajes_panel()
        main_layout.addWidget(self.herrajes_frame)

        # Panel de acciones
        self.create_actions_panel()
        main_layout.addWidget(self.actions_frame)

        # Aplicar estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
            }
            QTableWidget {
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                padding: 10px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

    def create_statistics_panel(self):
        """Crea el panel de estadísticas."""
        self.stats_frame = QGroupBox("📊 Estadísticas de Herrajes")

        stats_layout = QHBoxLayout(self.stats_frame)

        # Estadísticas individuales
        self.stats_labels = {}
        stats_info = [
            ("total_herrajes", "Total Herrajes", "#3498db"),
            ("proveedores_activos", "Proveedores Activos", "#2ecc71"),
            ("valor_inventario", "Valor Inventario", "#e74c3c"),
            ("pedidos_pendientes", "Pedidos Pendientes", "#f39c12"),
        ]

        for key, label, color in stats_info:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }}
                QLabel {{
                    color: white;
                    font-weight: bold;
                }}
            """)

            stat_layout = QVBoxLayout(stat_widget)

            value_label = QLabel("0")
            value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(label)
            desc_label.setStyleSheet("font-size: 12px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)

            self.stats_labels[key] = value_label
            stats_layout.addWidget(stat_widget)

    def create_filters_panel(self):
        """Crea el panel de filtros y búsqueda."""
        self.filters_frame = QGroupBox("🔍 Filtros y Búsqueda")

        filters_layout = QHBoxLayout(self.filters_frame)

        # Búsqueda general
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Buscar por código, descripción o proveedor..."
        )
        self.search_input.textChanged.connect(self.on_search_changed)

        # Filtro por proveedor
        self.proveedor_filter = QComboBox()
        self.proveedor_filter.addItem("Todos los proveedores")
        self.proveedor_filter.currentTextChanged.connect(self.on_filters_changed)

        # Filtro por categoría
        self.categoria_filter = QComboBox()
        self.categoria_filter.addItem("Todas las categorías")
        self.categoria_filter.addItems(
            ["Bisagras", "Cerraduras", "Manijas", "Tornillos", "Otros"]
        )
        self.categoria_filter.currentTextChanged.connect(self.on_filters_changed)

        # Botón de limpiar filtros
        self.clear_filters_btn = QPushButton("Limpiar Filtros")
        self.clear_filters_btn.clicked.connect(self.clear_filters)

        filters_layout.addWidget(QLabel("Buscar:"))
        filters_layout.addWidget(self.search_input, 2)
        filters_layout.addWidget(QLabel("Proveedor:"))
        filters_layout.addWidget(self.proveedor_filter, 1)
        filters_layout.addWidget(QLabel("Categoría:"))
        filters_layout.addWidget(self.categoria_filter, 1)
        filters_layout.addWidget(self.clear_filters_btn)

    def create_herrajes_panel(self):
        """Crea el panel de herrajes."""
        self.herrajes_frame = QGroupBox("🔧 Lista de Herrajes")

        herrajes_layout = QVBoxLayout(self.herrajes_frame)

        # Tabla de herrajes
        self.herrajes_table = QTableWidget()
        self.herrajes_table.setColumnCount(8)
        self.herrajes_table.setHorizontalHeaderLabels(
            [
                "Código",
                "Descripción",
                "Proveedor",
                "Precio Unit.",
                "Unidad",
                "Categoría",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.herrajes_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.herrajes_table.setAlternatingRowColors(True)
        self.herrajes_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        herrajes_layout.addWidget(self.herrajes_table)

    def create_actions_panel(self):
        """Crea el panel de acciones."""
        self.actions_frame = QGroupBox("⚡ Acciones")

        actions_layout = QHBoxLayout(self.actions_frame)

        # Botones de acción
        self.asignar_obra_btn = QPushButton("📋 Asignar a Obra")
        self.asignar_obra_btn.clicked.connect(self.show_asignar_obra_dialog)

        self.crear_pedido_btn = QPushButton("🛒 Crear Pedido")
        self.crear_pedido_btn.clicked.connect(self.show_crear_pedido_dialog)

        self.actualizar_btn = QPushButton("🔄 Actualizar")
        self.actualizar_btn.clicked.connect(self.actualizar_datos)

        self.estadisticas_btn = QPushButton("📊 Ver Estadísticas")
        self.estadisticas_btn.clicked.connect(self.show_estadisticas)

        actions_layout.addWidget(self.asignar_obra_btn)
        actions_layout.addWidget(self.crear_pedido_btn)
        actions_layout.addWidget(self.actualizar_btn)
        actions_layout.addWidget(self.estadisticas_btn)
        actions_layout.addStretch()

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def cargar_herrajes_en_tabla(self, herrajes):
        """Carga herrajes en la tabla."""
        self.herrajes_table.setRowCount(len(herrajes))

        for row, herraje in enumerate(herrajes):
            # Datos del herraje
            items = [
                herraje.get("codigo", ""),
                herraje.get("descripcion", ""),
                herraje.get("proveedor", ""),
                f"${herraje.get('precio_unitario', 0.0):.2f}",
                herraje.get("unidad_medida", ""),
                herraje.get("categoria", ""),
                herraje.get("estado", ""),
            ]

            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.herrajes_table.setItem(row, col, table_item)

            # Botón de acciones
            action_btn = QPushButton("Ver Detalle")
            action_btn.clicked.connect(
                lambda checked, r=row: self.show_herraje_detail(r)
            )
            self.herrajes_table.setCellWidget(row, 7, action_btn)

    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas mostradas."""
        self.stats_labels["total_herrajes"].setText(
            str(estadisticas.get("total_herrajes", 0))
        )
        self.stats_labels["proveedores_activos"].setText(
            str(estadisticas.get("proveedores_activos", 0))
        )
        self.stats_labels["valor_inventario"].setText(
            f"${estadisticas.get('valor_total_inventario', 0.0):.2f}"
        )
        self.stats_labels["pedidos_pendientes"].setText(
            str(estadisticas.get("pedidos_pendientes", 0))
        )

    def on_search_changed(self, text):
        """Maneja cambios en la búsqueda."""
        if self.controller:
            self.controller.buscar_herrajes(text)

    def on_filters_changed(self):
        """Maneja cambios en los filtros."""
        filtros = {
            "proveedor": self.proveedor_filter.currentText()
            if self.proveedor_filter.currentText() != "Todos los proveedores"
            else None,
            "categoria": self.categoria_filter.currentText()
            if self.categoria_filter.currentText() != "Todas las categorías"
            else None,
        }

        if self.controller:
            self.controller.aplicar_filtros(filtros)

    def clear_filters(self):
        """Limpia todos los filtros."""
        self.search_input.clear()
        self.proveedor_filter.setCurrentIndex(0)
        self.categoria_filter.setCurrentIndex(0)

    def show_asignar_obra_dialog(self):
        """Muestra diálogo para asignar herraje a obra."""
        selected_row = self.herrajes_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un herraje de la tabla."
            )
            return

        # Aquí se abriría un diálogo para asignar a obra
        # Por simplicidad, mostraremos un mensaje
        QMessageBox.information(
            self, "Asignar a Obra", "Función de asignación a obra en desarrollo."
        )

    def show_crear_pedido_dialog(self):
        """Muestra diálogo para crear pedido."""
        # Aquí se abriría un diálogo para crear pedido
        QMessageBox.information(
            self, "Crear Pedido", "Función de creación de pedido en desarrollo."
        )

    def show_herraje_detail(self, row):
        """Muestra detalles del herraje seleccionado."""
        codigo = self.herrajes_table.item(row, 0).text()
        descripcion = self.herrajes_table.item(row, 1).text()
        proveedor = self.herrajes_table.item(row, 2).text()

        QMessageBox.information(
            self,
            "Detalle Herraje",
            f"Código: {codigo}\nDescripción: {descripcion}\nProveedor: {proveedor}",
        )

    def actualizar_datos(self):
        """Actualiza los datos de la vista."""
        if self.controller:
            self.controller.cargar_datos_iniciales()

    def show_estadisticas(self):
        """Muestra estadísticas detalladas."""
        if self.controller:
            self.controller.mostrar_estadisticas_detalladas()

    def show_error(self, mensaje):
        """Muestra mensaje de error."""
        QMessageBox.critical(self, "Error", mensaje)

    def show_success(self, mensaje):
        """Muestra mensaje de éxito."""
        QMessageBox.information(self, "Éxito", mensaje)
