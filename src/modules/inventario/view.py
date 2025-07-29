"""
Vista de Inventario

Interfaz de usuario moderna para la gestión del inventario con sistema de reservas.
"""

import datetime
from typing import Any, Dict

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from rexus.utils.form_validators import FormValidator, FormValidatorManager, validacion_codigo_producto
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
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
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .dialogs import ReservaDialog


class InventarioView(QWidget):
    """Vista principal del módulo de inventario con sistema de reservas."""

    # Señales
    producto_agregado = pyqtSignal(dict)
    producto_editado = pyqtSignal(dict)
    producto_eliminado = pyqtSignal(int)
    movimiento_solicitado = pyqtSignal(dict)
    reserva_solicitada = pyqtSignal(dict)
    reserva_liberada = pyqtSignal(int)

    def __init__(self, db_connection=None, usuario_actual="SISTEMA"):
        super().__init__()
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual
        self.controller = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)  # Reduced spacing
        main_layout.setContentsMargins(10, 8, 10, 8)  # Reduced margins

        # Pestañas principales (sin título)
        self.create_tabs()
        main_layout.addWidget(self.tabs)

        # Aplicar estilo general optimizado para compacidad
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border: 1px solid #bdc3c7;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #d5dbdb);
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                margin: 8px 0px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
        """)

    def create_tabs(self):
        """Crea las pestañas principales del inventario."""
        self.tabs = QTabWidget()

        # Pestaña 1: Inventario General
        self.create_inventario_tab()

        # Pestaña 2: Reservas por Obra
        self.create_reservas_tab()

        # Pestaña 3: Disponibilidad
        self.create_disponibilidad_tab()

        # Pestaña 4: Estadísticas
        self.create_estadisticas_tab()

    def create_inventario_tab(self):
        """Crea la pestaña de inventario general."""
        inventario_widget = QWidget()
        layout = QVBoxLayout(inventario_widget)
        layout.setSpacing(6)  # Compact spacing

        # Panel de filtros y acciones combinado - más compacto
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(8, 6, 8, 6)

        # Búsqueda por código/descripción
        control_layout.addWidget(QLabel("Buscar:"))
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Código o descripción...")
        self.busqueda_input.setMaximumWidth(200)
        control_layout.addWidget(self.busqueda_input)

        # Filtro por categoría
        control_layout.addWidget(QLabel("Categoría:"))
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Todas")
        self.categoria_combo.setMaximumWidth(120)
        control_layout.addWidget(self.categoria_combo)

        # Botones de filtrado
        self.buscar_btn = QPushButton("🔍")
        self.buscar_btn.setMaximumWidth(35)
        self.buscar_btn.setToolTip("Buscar")
        control_layout.addWidget(self.buscar_btn)

        self.limpiar_btn = QPushButton("🧹")
        self.limpiar_btn.setMaximumWidth(35)
        self.limpiar_btn.setToolTip("Limpiar filtros")
        control_layout.addWidget(self.limpiar_btn)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator)

        # Acciones principales - más compactas
        self.nuevo_producto_btn = QPushButton("➕")
        self.nuevo_producto_btn.setMaximumWidth(35)
        self.nuevo_producto_btn.setToolTip("Nuevo Producto")
        self.nuevo_producto_btn.clicked.connect(self.mostrar_dialogo_nuevo_producto)
        control_layout.addWidget(self.nuevo_producto_btn)
        
        self.editar_producto_btn = QPushButton("✏️")
        self.editar_producto_btn.setMaximumWidth(35)
        self.editar_producto_btn.setToolTip("Editar Producto")
        control_layout.addWidget(self.editar_producto_btn)
        
        self.eliminar_producto_btn = QPushButton("🗑️")
        self.eliminar_producto_btn.setMaximumWidth(35)
        self.eliminar_producto_btn.setToolTip("Eliminar Producto")
        control_layout.addWidget(self.eliminar_producto_btn)
        
        # Segundo separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator2)
        
        self.movimiento_btn = QPushButton("📦")
        self.movimiento_btn.setMaximumWidth(35)
        self.movimiento_btn.setToolTip("Registrar Movimiento")
        control_layout.addWidget(self.movimiento_btn)
        
        self.exportar_btn = QPushButton("📄")
        self.exportar_btn.setMaximumWidth(35)
        self.exportar_btn.setToolTip("Exportar Inventario")
        control_layout.addWidget(self.exportar_btn)

        control_layout.addStretch()
        layout.addWidget(control_frame)

        # Tabla de inventario
        self.create_tabla_inventario()
        layout.addWidget(self.tabla_inventario)

        self.tabs.addTab(inventario_widget, "📦 Inventario General")

    def create_tabla_inventario(self):
        """Crea la tabla de inventario."""
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(10)
        self.tabla_inventario.setHorizontalHeaderLabels(
            [
                "Código",
                "Descripción",
                "Categoría",
                "Stock Actual",
                "Stock Mínimo",
                "Stock Reservado",
                "Precio Unit.",
                "Valor Total",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla con tamaños de columna optimizados
        header = self.tabla_inventario.horizontalHeader()
        if header is not None:
            # Configurar anchos específicos para optimizar el espacio
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Código
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descripción
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Categoría
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Stock Actual
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Stock Mínimo
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Stock Reservado
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Precio Unit.
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Valor Total
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # Estado
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)  # Acciones
            
            # Establecer anchos específicos (en píxeles)
            self.tabla_inventario.setColumnWidth(0, 80)   # Código
            self.tabla_inventario.setColumnWidth(2, 90)   # Categoría
            self.tabla_inventario.setColumnWidth(3, 70)   # Stock Actual
            self.tabla_inventario.setColumnWidth(4, 70)   # Stock Mínimo
            self.tabla_inventario.setColumnWidth(5, 80)   # Stock Reservado
            self.tabla_inventario.setColumnWidth(6, 85)   # Precio Unit.
            self.tabla_inventario.setColumnWidth(7, 90)   # Valor Total
            self.tabla_inventario.setColumnWidth(8, 70)   # Estado
            self.tabla_inventario.setColumnWidth(9, 80)   # Acciones
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Estilo de tabla optimizado para más densidad de información
        self.tabla_inventario.setStyleSheet("""
            QTableWidget {
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                padding: 6px 8px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                color: #2c3e50;
                font-size: 11px;
                min-height: 25px;
            }
        """)

    def create_reservas_tab(self):
        """Crea la pestaña de reservas por obra."""
        reservas_widget = QWidget()
        layout = QVBoxLayout(reservas_widget)

        # Panel de control de reservas
        control_frame = QGroupBox("🏗️ Control de Reservas por Obra")
        control_layout = QVBoxLayout(control_frame)

        # Selector de obra
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Obra:"))

        self.obra_selector = QComboBox()
        self.obra_selector.addItem("Seleccionar obra...")
        self.obra_selector.currentIndexChanged.connect(self.on_obra_changed)
        selector_layout.addWidget(self.obra_selector)

        # Botón para crear nueva reserva
        self.nueva_reserva_btn = QPushButton("➕ Nueva Reserva")
        self.nueva_reserva_btn.clicked.connect(self.show_nueva_reserva_dialog)
        selector_layout.addWidget(self.nueva_reserva_btn)

        # Botón para generar reporte
        self.reporte_reservas_btn = QPushButton("📊 Generar Reporte")
        self.reporte_reservas_btn.clicked.connect(self.generar_reporte_reservas)
        selector_layout.addWidget(self.reporte_reservas_btn)

        selector_layout.addStretch()
        control_layout.addLayout(selector_layout)

        layout.addWidget(control_frame)

        # Tabla de reservas
        self.create_reservas_table()
        layout.addWidget(self.reservas_table_frame)

        self.tabs.addTab(reservas_widget, "🏗️ Reservas por Obra")

    def create_reservas_table(self):
        """Crea la tabla de reservas."""
        self.reservas_table_frame = QGroupBox("📋 Reservas Activas")
        table_layout = QVBoxLayout(self.reservas_table_frame)

        # Tabla de reservas
        self.reservas_table = QTableWidget()
        self.reservas_table.setColumnCount(8)
        self.reservas_table.setHorizontalHeaderLabels(
            [
                "Código",
                "Producto",
                "Cantidad",
                "Unidad",
                "Valor Unit.",
                "Valor Total",
                "Fecha Reserva",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.reservas_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.reservas_table.setAlternatingRowColors(True)
        self.reservas_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Estilo de tabla optimizado para compacidad
        self.reservas_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                padding: 6px 8px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                color: #2c3e50;
                font-size: 11px;
                min-height: 25px;
            }
        """)

        table_layout.addWidget(self.reservas_table)

    def create_disponibilidad_tab(self):
        """Crea la pestaña de disponibilidad de materiales."""
        disponibilidad_widget = QWidget()
        layout = QVBoxLayout(disponibilidad_widget)

        # Panel de filtros
        filtros_frame = QGroupBox("🔍 Filtros de Disponibilidad")
        filtros_layout = QHBoxLayout(filtros_frame)

        # Filtro por categoría
        filtros_layout.addWidget(QLabel("Categoría:"))
        self.categoria_filter = QComboBox()
        self.categoria_filter.addItem("Todas las categorías")
        self.categoria_filter.currentTextChanged.connect(self.filtrar_disponibilidad)
        filtros_layout.addWidget(self.categoria_filter)

        # Filtro por estado de stock
        filtros_layout.addWidget(QLabel("Estado:"))
        self.estado_stock_filter = QComboBox()
        self.estado_stock_filter.addItems(["Todos", "Normal", "Bajo", "Agotado"])
        self.estado_stock_filter.currentTextChanged.connect(self.filtrar_disponibilidad)
        filtros_layout.addWidget(self.estado_stock_filter)

        # Búsqueda por código/descripción
        filtros_layout.addWidget(QLabel("Buscar:"))
        self.busqueda_disponibilidad = QLineEdit()
        self.busqueda_disponibilidad.setPlaceholderText("Código o descripción...")
        self.busqueda_disponibilidad.textChanged.connect(self.filtrar_disponibilidad)
        filtros_layout.addWidget(self.busqueda_disponibilidad)

        # Botón actualizar
        self.actualizar_disponibilidad_btn = QPushButton("🔄 Actualizar")
        self.actualizar_disponibilidad_btn.clicked.connect(
            self.actualizar_disponibilidad
        )
        filtros_layout.addWidget(self.actualizar_disponibilidad_btn)

        filtros_layout.addStretch()
        layout.addWidget(filtros_frame)

        # Tabla de disponibilidad
        self.create_disponibilidad_table()
        layout.addWidget(self.disponibilidad_table_frame)

        self.tabs.addTab(disponibilidad_widget, "📊 Disponibilidad")

    def create_disponibilidad_table(self):
        """Crea la tabla de disponibilidad."""
        self.disponibilidad_table_frame = QGroupBox("📊 Estado de Disponibilidad")
        table_layout = QVBoxLayout(self.disponibilidad_table_frame)

        # Tabla de disponibilidad
        self.disponibilidad_table = QTableWidget()
        self.disponibilidad_table.setColumnCount(9)
        self.disponibilidad_table.setHorizontalHeaderLabels(
            [
                "Código",
                "Descripción",
                "Categoría",
                "Stock Total",
                "Stock Reservado",
                "Stock Disponible",
                "Stock Mínimo",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.disponibilidad_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.disponibilidad_table.setAlternatingRowColors(True)
        self.disponibilidad_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Aplicar mismo estilo que tabla de reservas
        self.disponibilidad_table.setStyleSheet(self.reservas_table.styleSheet())

        table_layout.addWidget(self.disponibilidad_table)

    def create_estadisticas_tab(self):
        """Crea la pestaña de estadísticas separada."""
        estadisticas_widget = QWidget()
        layout = QVBoxLayout(estadisticas_widget)

        # Título
        title_label = QLabel("📊 Estadísticas del Inventario")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title_label)

        # Panel de estadísticas generales
        stats_frame = QGroupBox("📈 Estadísticas Generales")
        stats_layout = QHBoxLayout(stats_frame)

        # Crear widgets de estadísticas
        self.stats_widgets = {}
        stats_info = [
            ("total_productos", "Total Productos", "#3498db"),
            ("valor_total", "Valor Total", "#e74c3c"),
            ("stock_bajo", "Stock Bajo", "#f39c12"),
            ("productos_activos", "Productos Activos", "#2ecc71"),
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
            value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(label)
            desc_label.setStyleSheet("font-size: 11px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)

            self.stats_widgets[key] = value_label
            stats_layout.addWidget(stat_widget)

        layout.addWidget(stats_frame)

        # Panel de estadísticas de reservas
        reservas_stats_frame = QGroupBox("🏗️ Estadísticas de Reservas")
        reservas_stats_layout = QHBoxLayout(reservas_stats_frame)

        # Crear widgets de estadísticas de reservas
        self.stats_reservas = {}
        reservas_stats_info = [
            ("total_reservas", "Total Reservas", "#3498db"),
            ("valor_reservado", "Valor Reservado", "#e74c3c"),
            ("productos_reservados", "Productos Reservados", "#2ecc71"),
            ("stock_disponible", "Stock Disponible", "#f39c12"),
        ]

        for key, label, color in reservas_stats_info:
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
            value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(label)
            desc_label.setStyleSheet("font-size: 11px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)

            self.stats_reservas[key] = value_label
            reservas_stats_layout.addWidget(stat_widget)

        layout.addWidget(reservas_stats_frame)

        # Panel de gráficos o información adicional
        info_frame = QGroupBox("📋 Información Adicional")
        info_layout = QVBoxLayout(info_frame)

        info_text = QLabel("""
        📊 Resumen de Inventario:
        
        • Esta pestaña muestra estadísticas detalladas del inventario
        • Las estadísticas se actualizan automáticamente
        • Puede ver el rendimiento general del inventario
        • Monitoreo de stock bajo y productos críticos
        
        🔄 Última actualización: Al cargar el módulo
        """)
        info_text.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                color: #495057;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)
        layout.addStretch()

        self.tabs.addTab(estadisticas_widget, "📊 Estadísticas")

    def cargar_inventario_en_tabla(self, productos):
        """Carga los productos en la tabla de inventario."""
        self.tabla_inventario.setRowCount(len(productos))

        for row, producto in enumerate(productos):
            items = [
                producto.get("codigo", ""),
                producto.get("descripcion", ""),
                producto.get("categoria", ""),
                str(producto.get("stock_actual", 0)),
                str(producto.get("stock_minimo", 0)),
                str(producto.get("stock_reservado", 0)),
                f"${float(producto.get('precio_unitario', 0.0)):.2f}",
                f"${float(producto.get('stock_actual', 0)) * float(producto.get('precio_unitario', 0.0)):.2f}",
                producto.get("estado_stock", "NORMAL"),
            ]

            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Colorear según estado
                if col == 8:  # Columna de estado
                    if item == "AGOTADO":
                        table_item.setBackground(QColor("#e74c3c"))
                        table_item.setForeground(QColor("white"))
                    elif item == "BAJO":
                        table_item.setBackground(QColor("#f39c12"))
                        table_item.setForeground(QColor("white"))
                    else:
                        table_item.setBackground(QColor("#2ecc71"))
                        table_item.setForeground(QColor("white"))

                self.tabla_inventario.setItem(row, col, table_item)

            # Botón de acciones
            acciones_btn = QPushButton("⚙️ Acciones")
            self.tabla_inventario.setCellWidget(row, 9, acciones_btn)

    def cargar_obras_en_selector(self, obras):
        """Carga las obras en el selector."""
        self.obra_selector.clear()
        self.obra_selector.addItem("Seleccionar obra...")

        for obra in obras:
            self.obra_selector.addItem(
                f"{obra['codigo']} - {obra['nombre']}", obra["id"]
            )

    def cargar_reservas_en_tabla(self, reservas):
        """Carga las reservas en la tabla."""
        self.reservas_table.setRowCount(len(reservas))

        for row, reserva in enumerate(reservas):
            items = [
                reserva.get("codigo", ""),
                reserva.get("descripcion", ""),
                str(reserva.get("cantidad_reservada", 0)),
                reserva.get("unidad_medida", ""),
                f"${reserva.get('precio_unitario', 0.0):.2f}",
                f"${reserva.get('cantidad_reservada', 0) * reserva.get('precio_unitario', 0.0):.2f}",
                str(reserva.get("fecha_reserva", "")),
            ]

            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.reservas_table.setItem(row, col, table_item)

            # Botón para liberar reserva
            liberar_btn = QPushButton("🔓 Liberar")
            liberar_btn.clicked.connect(
                lambda checked, r=reserva: self.liberar_reserva(r)
            )
            self.reservas_table.setCellWidget(row, 7, liberar_btn)

    def cargar_disponibilidad_en_tabla(self, disponibilidad):
        """Carga la disponibilidad en la tabla."""
        self.disponibilidad_table.setRowCount(len(disponibilidad))

        for row, item in enumerate(disponibilidad):
            items = [
                item.get("codigo", ""),
                item.get("descripcion", ""),
                item.get("categoria", ""),
                str(item.get("stock_actual", 0)),
                str(item.get("stock_reservado", 0)),
                str(item.get("stock_disponible", 0)),
                str(item.get("stock_minimo", 0)),
                item.get("estado_stock", "NORMAL"),
            ]

            for col, item_data in enumerate(items):
                table_item = QTableWidgetItem(str(item_data))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Colorear según estado
                if col == 7:  # Columna de estado
                    if item_data == "AGOTADO":
                        table_item.setBackground(QColor("#e74c3c"))
                        table_item.setForeground(QColor("white"))
                    elif item_data == "BAJO":
                        table_item.setBackground(QColor("#f39c12"))
                        table_item.setForeground(QColor("white"))
                    else:
                        table_item.setBackground(QColor("#2ecc71"))
                        table_item.setForeground(QColor("white"))

                self.disponibilidad_table.setItem(row, col, table_item)

            # Botón para ver detalles
            detalle_btn = QPushButton("👁️ Ver Detalle")
            detalle_btn.clicked.connect(
                lambda checked, i=item: self.ver_detalle_disponibilidad(i)
            )
            self.disponibilidad_table.setCellWidget(row, 8, detalle_btn)

    def actualizar_stats(self, stats):
        """Actualiza las estadísticas generales."""
        self.stats_widgets["total_productos"].setText(
            str(stats.get("total_productos", 0))
        )
        self.stats_widgets["valor_total"].setText(
            f"${stats.get('valor_total', 0.0):.2f}"
        )
        self.stats_widgets["stock_bajo"].setText(str(stats.get("stock_bajo", 0)))
        self.stats_widgets["productos_activos"].setText(
            str(stats.get("productos_activos", 0))
        )

    def actualizar_stats_reservas(self, stats):
        """Actualiza las estadísticas de reservas."""
        self.stats_reservas["total_reservas"].setText(
            str(stats.get("total_reservas", 0))
        )
        self.stats_reservas["valor_reservado"].setText(
            f"${stats.get('valor_reservado', 0.0):.2f}"
        )
        self.stats_reservas["productos_reservados"].setText(
            str(stats.get("productos_reservados", 0))
        )
        self.stats_reservas["stock_disponible"].setText(
            str(stats.get("stock_disponible", 0))
        )

    def on_obra_changed(self):
        """Maneja el cambio de obra seleccionada."""
        if self.obra_selector.currentIndex() > 0:
            obra_id = self.obra_selector.currentData()
            if self.controller:
                self.controller.cargar_reservas_obra(obra_id)

    def show_nueva_reserva_dialog(self):
        """Muestra el diálogo para crear una nueva reserva."""
        if self.obra_selector.currentIndex() <= 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una obra primero.")
            return

        obra_id = self.obra_selector.currentData()

        dialog = ReservaDialog(self, obra_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            reserva_data = dialog.get_reserva_data()
            if self.controller:
                self.controller.crear_reserva(reserva_data)

    def liberar_reserva(self, reserva):
        """Libera una reserva específica."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Está seguro de liberar la reserva de {reserva['descripcion']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            if self.controller:
                self.controller.liberar_reserva(reserva["id"])

    def generar_reporte_reservas(self):
        """Genera un reporte de reservas para la obra seleccionada."""
        if self.obra_selector.currentIndex() <= 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una obra primero.")
            return

        obra_id = self.obra_selector.currentData()
        if self.controller:
            self.controller.generar_reporte_reservas(obra_id)

    def filtrar_disponibilidad(self):
        """Filtra la tabla de disponibilidad."""
        if self.controller:
            filtros = {
                "categoria": self.categoria_filter.currentText()
                if self.categoria_filter.currentText() != "Todas las categorías"
                else None,
                "estado": self.estado_stock_filter.currentText()
                if self.estado_stock_filter.currentText() != "Todos"
                else None,
                "busqueda": self.busqueda_disponibilidad.text()
                if self.busqueda_disponibilidad.text()
                else None,
            }
            self.controller.filtrar_disponibilidad(filtros)

    def actualizar_disponibilidad(self):
        """Actualiza la tabla de disponibilidad."""
        if self.controller:
            self.controller.cargar_disponibilidad()

    def ver_detalle_disponibilidad(self, item):
        """Muestra el detalle de disponibilidad de un producto."""
        if self.controller:
            self.controller.mostrar_detalle_disponibilidad(item)

    def show_error(self, mensaje):
        """Muestra mensaje de error."""
        QMessageBox.critical(self, "Error", mensaje)

    def show_success(self, mensaje):
        """Muestra mensaje de éxito."""
        QMessageBox.information(self, "Éxito", mensaje)

    def show_info(self, titulo, mensaje):
        """Muestra mensaje informativo."""
        QMessageBox.information(self, titulo, mensaje)

    def mostrar_dialogo_nuevo_producto(self):
        """Muestra el diálogo para agregar un nuevo producto."""
        dialogo = DialogoNuevoProducto(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos_producto = dialogo.obtener_datos()
            if self.controller:
                self.controller.agregar_producto(datos_producto)
                # Recargar la tabla después de agregar
                self.controller.cargar_datos_iniciales()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoNuevoProducto(QDialog):
    """Diálogo para agregar un nuevo producto al inventario."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator_manager = FormValidatorManager()
        self.setWindowTitle("Nuevo Producto")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("📦 Agregar Nuevo Producto")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Formulario
        form_widget = QScrollArea()
        form_content = QWidget()
        form_layout = QFormLayout(form_content)

        # Campo código
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Ej: VID-1234, HER-5678")
        form_layout.addRow("🏷️ Código:", self.codigo_input)

        # Campo descripción
        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción del producto")
        form_layout.addRow("📝 Descripción:", self.descripcion_input)

        # Campo categoría
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Marco", "Vidrio", "Herraje", "Accesorio", "Sellador"])
        form_layout.addRow("📂 Tipo:", self.tipo_combo)

        # Campo acabado
        self.acabado_combo = QComboBox()
        self.acabado_combo.addItems(["Natural", "Blanco", "Negro", "Bronce", "Cromado"])
        form_layout.addRow("🎨 Acabado:", self.acabado_combo)

        # Campo cantidad
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(0, 999999)
        self.cantidad_input.setValue(1)
        form_layout.addRow("📦 Cantidad:", self.cantidad_input)

        # Campo precio
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.0, 999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setPrefix("$")
        form_layout.addRow("💰 Precio:", self.precio_input)

        # Campo unidad de medida
        self.unidad_combo = QComboBox()
        self.unidad_combo.addItems(["UN", "MT", "M2", "KG", "LT"])
        form_layout.addRow("📏 Unidad:", self.unidad_combo)

        # Campo proveedor
        self.proveedor_input = QLineEdit()
        self.proveedor_input.setPlaceholderText("Nombre del proveedor")
        form_layout.addRow("🏢 Proveedor:", self.proveedor_input)

        # Campo ubicación
        self.ubicacion_input = QLineEdit()
        self.ubicacion_input.setPlaceholderText("Ej: Estante A-1")
        form_layout.addRow("📍 Ubicación:", self.ubicacion_input)

        # Campo observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setPlaceholderText("Observaciones adicionales (opcional)")
        form_layout.addRow("📋 Observaciones:", self.observaciones_input)

        form_widget.setWidget(form_content)
        form_widget.setWidgetResizable(True)
        layout.addWidget(form_widget)

        # Botones
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("✅ Guardar")
        self.save_btn.clicked.connect(self.validar_y_guardar)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addWidget(QWidget())  # Spacer
        layout.addLayout(button_layout)

        # Configurar validaciones
        self.configurar_validaciones()

    def configurar_validaciones(self):
        """Configura las validaciones del formulario."""
        # Validación de código obligatorio con formato específico
        self.validator_manager.agregar_validacion(
            self.codigo_input, validacion_codigo_producto
        )

        # Validación de descripción obligatoria
        self.validator_manager.agregar_validacion(
            self.descripcion_input, FormValidator.validar_campo_obligatorio, "Descripción"
        )

        # Validación de precio
        self.validator_manager.agregar_validacion(
            self.precio_input, FormValidator.validar_numero, 0.01, 999999.99
        )

        # Validación de proveedor obligatorio
        self.validator_manager.agregar_validacion(
            self.proveedor_input, FormValidator.validar_campo_obligatorio, "Proveedor"
        )

    def validar_y_guardar(self):
        """Valida el formulario y guarda si es válido."""
        es_valido, errores = self.validator_manager.validar_formulario()
        
        if not es_valido:
            # Mostrar errores
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            QMessageBox.warning(
                self, 
                "Errores de Validación", 
                "Por favor corrige los siguientes errores:\n\n" + "\n".join(mensajes_error)
            )
            return

        # Si todo es válido, aceptar el diálogo
        self.accept()

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            'codigo': self.codigo_input.text().strip().upper(),
            'descripcion': self.descripcion_input.text().strip(),
            'tipo': self.tipo_combo.currentText(),
            'acabado': self.acabado_combo.currentText(),
            'cantidad': self.cantidad_input.value(),
            'importe': self.precio_input.value(),
            'unidad': self.unidad_combo.currentText(),
            'proveedor': self.proveedor_input.text().strip(),
            'ubicacion': self.ubicacion_input.text().strip(),
            'observaciones': self.observaciones_input.toPlainText().strip()
        }
