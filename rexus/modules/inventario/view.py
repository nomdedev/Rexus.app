# 🔒 Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control

# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check

# 🔒 XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added
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

Vista de Inventario

Interfaz de usuario moderna para la gestión del inventario con sistema de reservas.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
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
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Importar validadores con manejo de errores
try:
    from rexus.utils.form_validators import (
        FormValidator,
        FormValidatorManager,
        validacion_codigo_producto,
    )
    from utils.data_sanitizer import DataSanitizer

    VALIDATORS_AVAILABLE = True
    SANITIZER_AVAILABLE = True
    data_sanitizer = DataSanitizer()
except ImportError:
    print("[INFO] Form validators not available, using basic validation")
    VALIDATORS_AVAILABLE = False
    SANITIZER_AVAILABLE = False
    data_sanitizer = None

    # Crear clases mock para evitar errores
    class FormValidator:
        @staticmethod
        def validar_campo_obligatorio(value, name):
            # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
            if SANITIZER_AVAILABLE and data_sanitizer and hasattr(value, "strip"):
                value = data_sanitizer.sanitize_string(value)
            return bool(value.strip() if hasattr(value, "strip") else value)

        @staticmethod
        def validar_numero(value, min_val=None, max_val=None):
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    return False
                if max_val is not None and num > max_val:
                    return False
                return True
            except:
                return False

    class FormValidatorManager:
        def __init__(self):
            self.validaciones = []

        def agregar_validacion(self, widget, validator, *args):
            # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
            # TODO: Implementar @auth_required o verificación manual
            # if not AuthManager.check_permission('agregar_validacion'):
            #     raise PermissionError("Acceso denegado - Permisos insuficientes")

            # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
            if SANITIZER_AVAILABLE and data_sanitizer and hasattr(widget, "text"):
                current_text = widget.text()
                if isinstance(current_text, str):
                    sanitized_text = data_sanitizer.sanitize_string(current_text)
                    if sanitized_text != current_text:
                        widget.setText(sanitized_text)

            pass

        def validar_formulario(self):
            return True, []

        def obtener_mensajes_error(self):
            return []

    def validacion_codigo_producto(value):
        return bool(value.strip() if hasattr(value, "strip") else value)


from .dialogs import ReservaDialog
from .dialogs.missing_dialogs import (
    DialogoEditarProducto,
    DialogoHistorialProducto,
    DialogoMovimientoInventario,
)


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
        self.logger = logging.getLogger(f"{__name__}.InventarioView")
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual
        self.controller = None
        self.logger.info(
            f"Inicializando vista de inventario para usuario: {usuario_actual}"
        )
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

        # Conectar eventos con búsqueda en tiempo real
        self.busqueda_input.textChanged.connect(self.filtrar_inventario_tiempo_real)
        self.categoria_combo.currentTextChanged.connect(self.filtrar_inventario)
        self.buscar_btn.clicked.connect(self.filtrar_inventario)
        self.limpiar_btn.clicked.connect(self.limpiar_filtros_inventario)

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
        self.editar_producto_btn.clicked.connect(self.editar_producto_seleccionado)
        control_layout.addWidget(self.editar_producto_btn)

        self.eliminar_producto_btn = QPushButton("🗑️")
        self.eliminar_producto_btn.setMaximumWidth(35)
        self.eliminar_producto_btn.setToolTip("Eliminar Producto")
        self.eliminar_producto_btn.clicked.connect(self.eliminar_producto_seleccionado)
        control_layout.addWidget(self.eliminar_producto_btn)

        # Segundo separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator2)

        self.movimiento_btn = QPushButton("📦")
        self.movimiento_btn.setMaximumWidth(35)
        self.movimiento_btn.setToolTip("Registrar Movimiento")
        self.movimiento_btn.clicked.connect(
            self.mostrar_dialogo_movimiento_seleccionado
        )
        control_layout.addWidget(self.movimiento_btn)

        self.exportar_btn = QPushButton("📄")
        self.exportar_btn.setMaximumWidth(35)
        self.exportar_btn.setToolTip("Exportar Inventario")
        self.exportar_btn.clicked.connect(self.exportar_inventario)
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
            header.setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch
            )  # Descripción
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Categoría
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Stock Actual
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Stock Mínimo
            header.setSectionResizeMode(
                5, QHeaderView.ResizeMode.Fixed
            )  # Stock Reservado
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Precio Unit.
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Valor Total
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # Estado
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)  # Acciones

            # Establecer anchos específicos (en píxeles)
            self.tabla_inventario.setColumnWidth(0, 80)  # Código
            self.tabla_inventario.setColumnWidth(2, 90)  # Categoría
            self.tabla_inventario.setColumnWidth(3, 70)  # Stock Actual
            self.tabla_inventario.setColumnWidth(4, 70)  # Stock Mínimo
            self.tabla_inventario.setColumnWidth(5, 80)  # Stock Reservado
            self.tabla_inventario.setColumnWidth(6, 85)  # Precio Unit.
            self.tabla_inventario.setColumnWidth(7, 90)  # Valor Total
            self.tabla_inventario.setColumnWidth(8, 70)  # Estado
            self.tabla_inventario.setColumnWidth(9, 80)  # Acciones
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
            acciones_btn = QPushButton("⚙️")
            acciones_btn.setMaximumWidth(35)
            acciones_btn.setToolTip("Acciones del producto")
            acciones_btn.clicked.connect(
                lambda checked, producto=producto: self.mostrar_menu_acciones_producto(
                    producto
                )
            )
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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_stats'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_stats_reservas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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

        dialog = ReservaDialog(self, obra_id=obra_id, productos=[])
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
        # 🔒 PROTECCIÓN XSS: Sanitizar búsqueda de usuario
        """Filtra la tabla de disponibilidad."""
        if self.controller:
            busqueda_text = self.busqueda_disponibilidad.text()
            if SANITIZER_AVAILABLE and data_sanitizer and busqueda_text:
                busqueda_text = data_sanitizer.sanitize_string(busqueda_text)

            filtros = {
                "categoria": self.categoria_filter.currentText()
                if self.categoria_filter.currentText() != "Todas las categorías"
                else None,
                "estado": self.estado_stock_filter.currentText()
                if self.estado_stock_filter.currentText() != "Todos"
                else None,
                "busqueda": busqueda_text if busqueda_text else None,
            }
            self.controller.filtrar_disponibilidad(filtros)

    def actualizar_disponibilidad(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_disponibilidad'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza la tabla de disponibilidad."""
        if self.controller:
            self.controller.cargar_disponibilidad()

    def ver_detalle_disponibilidad(self, item):
        """Muestra el detalle de disponibilidad de un producto."""
        if self.controller:
            self.controller.mostrar_detalle_disponibilidad(item)

    def show_error(self, mensaje):
        """Muestra mensaje de error."""
        self.logger.error(f"Error mostrado al usuario: {mensaje}")
        QMessageBox.critical(self, "Error", mensaje)

    def show_success(self, mensaje):
        """Muestra mensaje de éxito."""
        self.logger.info(f"Operación exitosa: {mensaje}")
        QMessageBox.information(self, "Éxito", mensaje)

    def show_info(self, titulo, mensaje):
        """Muestra mensaje informativo."""
        self.logger.info(f"Información mostrada - {titulo}: {mensaje}")
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

    def filtrar_inventario(self):
        """Filtra el inventario según los criterios de búsqueda."""
        if self.controller:
            filtros = {
                "busqueda": self.busqueda_input.text(),
                "categoria": self.categoria_combo.currentText()
                if self.categoria_combo.currentText() != "Todas"
                else None,
            }
            self.controller.filtrar_inventario(filtros)

    def limpiar_filtros_inventario(self):
        """Limpia todos los filtros aplicados."""
        self.busqueda_input.clear()
        self.categoria_combo.setCurrentIndex(0)
        if self.controller:
            self.controller.cargar_datos_iniciales()

    def mostrar_menu_acciones_producto(self, producto):
        """Muestra un menú con las acciones disponibles para un producto."""
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QCursor
        from PyQt6.QtWidgets import QMenu

        # Crear menú contextual
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        # Acciones disponibles
        accion_editar = menu.addAction("✏️ Editar Producto")
        if accion_editar is not None:
            accion_editar.triggered.connect(
                lambda checked, p=producto: self.editar_producto(p)
            )

        accion_movimiento = menu.addAction("📦 Registrar Movimiento")
        if accion_movimiento is not None:
            accion_movimiento.triggered.connect(
                lambda checked, p=producto: self.mostrar_dialogo_movimiento(p)
            )

        accion_reservar = menu.addAction("🔒 Crear Reserva")
        if accion_reservar is not None:
            accion_reservar.triggered.connect(
                lambda checked, p=producto: self.mostrar_dialogo_reserva(p)
            )

        menu.addSeparator()

        accion_historial = menu.addAction("📊 Ver Historial")
        if accion_historial is not None:
            accion_historial.triggered.connect(
                lambda checked, p=producto: self.ver_historial_producto(p)
            )

        accion_detalle = menu.addAction("👁️ Ver Detalles")
        if accion_detalle is not None:
            accion_detalle.triggered.connect(
                lambda checked, p=producto: self.ver_detalle_producto(p)
            )

        menu.addSeparator()

        accion_duplicar = menu.addAction("📋 Duplicar Producto")
        if accion_duplicar is not None:
            accion_duplicar.triggered.connect(
                lambda checked, p=producto: self.duplicar_producto(p)
            )

        accion_eliminar = menu.addAction("🗑️ Eliminar Producto")
        if accion_eliminar is not None:
            accion_eliminar.triggered.connect(
                lambda checked, p=producto: self.eliminar_producto(p)
            )

        # Mostrar menú en la posición del cursor
        menu.exec(QCursor.pos())

    def editar_producto(self, producto):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('editar_producto'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Abre el diálogo para editar un producto."""
        try:
            dialogo = DialogoEditarProducto(self, producto)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos_producto = dialogo.obtener_datos()
                if self.controller:
                    self.controller.actualizar_producto(
                        producto.get("id"), datos_producto
                    )
                    self.controller.cargar_datos_iniciales()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editando producto: {str(e)}")

    def mostrar_dialogo_movimiento(self, producto):
        """Muestra el diálogo para registrar un movimiento de inventario."""
        try:
            dialogo = DialogoMovimientoInventario(self, producto)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos_movimiento = dialogo.obtener_datos()
                if self.controller:
                    self.controller.registrar_movimiento(datos_movimiento)
                    self.controller.cargar_datos_iniciales()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error registrando movimiento: {str(e)}"
            )

    def mostrar_dialogo_reserva(self, producto):
        """Muestra el diálogo para crear una reserva."""
        try:
            # ReservaDialog espera una lista de productos, no un producto individual
            productos = [producto] if producto else []
            dialogo = ReservaDialog(self, obra_id=None, productos=productos)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos_reserva = dialogo.get_reserva_data()
                if self.controller:
                    self.controller.crear_reserva(datos_reserva)
                    self.controller.cargar_datos_iniciales()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creando reserva: {str(e)}")

    def ver_historial_producto(self, producto):
        """Muestra el historial de movimientos de un producto."""
        try:
            dialogo = DialogoHistorialProducto(self, producto)
            dialogo.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando historial: {str(e)}")

    def ver_detalle_producto(self, producto):
        """Muestra información detallada del producto."""
        try:
            codigo = producto.get("codigo", "N/A")
            descripcion = producto.get("descripcion", "N/A")
            categoria = producto.get("categoria", "N/A")
            stock_actual = producto.get("stock_actual", 0)
            stock_minimo = producto.get("stock_minimo", 0)
            stock_reservado = producto.get("stock_reservado", 0)
            precio = producto.get("precio_unitario", 0.0)
            proveedor = producto.get("proveedor", "N/A")
            ubicacion = producto.get("ubicacion", "N/A")

            detalle_html = f"""
            <div style='padding: 20px; font-family: Arial, sans-serif;'>
                <h2 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;'>
                    📦 Detalles del Producto
                </h2>
                
                <table style='width: 100%; border-collapse: collapse; margin-top: 15px;'>
                    <tr><td style='padding: 8px; font-weight: bold; color: #34495e;'>Código:</td>
                        <td style='padding: 8px; color: #2c3e50;'>{codigo}</td></tr>
                    <tr style='background-color: #f8f9fa;'><td style='padding: 8px; font-weight: bold; color: #34495e;'>Descripción:</td>
                        <td style='padding: 8px; color: #2c3e50;'>{descripcion}</td></tr>
                    <tr><td style='padding: 8px; font-weight: bold; color: #34495e;'>Categoría:</td>
                        <td style='padding: 8px; color: #2c3e50;'>{categoria}</td></tr>
                    <tr style='background-color: #f8f9fa;'><td style='padding: 8px; font-weight: bold; color: #34495e;'>Stock Actual:</td>
                        <td style='padding: 8px; color: #27ae60; font-weight: bold;'>{stock_actual} unidades</td></tr>
                    <tr><td style='padding: 8px; font-weight: bold; color: #34495e;'>Stock Mínimo:</td>
                        <td style='padding: 8px; color: #e67e22;'>{stock_minimo} unidades</td></tr>
                    <tr style='background-color: #f8f9fa;'><td style='padding: 8px; font-weight: bold; color: #34495e;'>Stock Reservado:</td>
                        <td style='padding: 8px; color: #e74c3c;'>{stock_reservado} unidades</td></tr>
                    <tr><td style='padding: 8px; font-weight: bold; color: #34495e;'>Precio Unitario:</td>
                        <td style='padding: 8px; color: #27ae60; font-weight: bold;'>${precio:.2f}</td></tr>
                    <tr style='background-color: #f8f9fa;'><td style='padding: 8px; font-weight: bold; color: #34495e;'>Proveedor:</td>
                        <td style='padding: 8px; color: #2c3e50;'>{proveedor}</td></tr>
                    <tr><td style='padding: 8px; font-weight: bold; color: #34495e;'>Ubicación:</td>
                        <td style='padding: 8px; color: #2c3e50;'>{ubicacion}</td></tr>
                </table>
                
                <div style='margin-top: 20px; padding: 15px; background-color: #ecf0f1; border-radius: 8px;'>
                    <h3 style='color: #2c3e50; margin-top: 0;'>📊 Estado del Stock</h3>
                    <p style='margin: 5px 0;'><strong>Stock Disponible:</strong> {stock_actual - stock_reservado} unidades</p>
                    <p style='margin: 5px 0;'><strong>Valor Total en Stock:</strong> ${stock_actual * precio:.2f}</p>
                    {'<p style="color: #e74c3c; font-weight: bold;">⚠️ Stock bajo mínimo</p>' if stock_actual <= stock_minimo else ""}
                </div>
            </div>
            """

            msg = QMessageBox(self)
            msg.setWindowTitle(f"Detalles - {codigo}")
            msg.setText(detalle_html)
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando detalles: {str(e)}")

    def duplicar_producto(self, producto):
        """Duplica un producto existente."""
        try:
            # Crear una copia del producto con nuevo código
            codigo_original = producto.get("codigo", "")
            nuevo_codigo = f"{codigo_original}_COPIA"

            respuesta = QMessageBox.question(
                self,
                "Duplicar Producto",
                f"¿Está seguro de duplicar el producto '{codigo_original}'?\n\n"
                f"Se creará un nuevo producto con código: {nuevo_codigo}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                producto_duplicado = producto.copy()
                producto_duplicado["codigo"] = nuevo_codigo
                producto_duplicado["stock_actual"] = (
                    0  # Nuevo producto empieza sin stock
                )
                producto_duplicado["stock_reservado"] = 0

                if self.controller:
                    self.controller.agregar_producto(producto_duplicado)
                    self.controller.cargar_datos_iniciales()
                    QMessageBox.information(
                        self, "Éxito", f"Producto duplicado como: {nuevo_codigo}"
                    )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error duplicando producto: {str(e)}")

    def eliminar_producto(self, producto):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('eliminar_producto'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Elimina un producto del inventario."""
        try:
            codigo = producto.get("codigo", "N/A")
            stock_actual = producto.get("stock_actual", 0)
            stock_reservado = producto.get("stock_reservado", 0)

            # Verificar si tiene stock o reservas
            if stock_actual > 0 or stock_reservado > 0:
                QMessageBox.warning(
                    self,
                    "No se puede eliminar",
                    f"No se puede eliminar el producto '{codigo}'.\n\n"
                    f"Razón: Tiene stock actual ({stock_actual}) o reservas ({stock_reservado}).\n\n"
                    "Para eliminarlo, primero debe agotar el stock y liberar las reservas.",
                )
                return

            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar el producto '{codigo}'?\n\n"
                "Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                if self.controller:
                    self.controller.eliminar_producto(producto.get("id"))
                    self.controller.cargar_datos_iniciales()
                    QMessageBox.information(
                        self, "Éxito", f"Producto '{codigo}' eliminado correctamente."
                    )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error eliminando producto: {str(e)}")

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller

    def filtrar_inventario_tiempo_real(self):
        """Filtra el inventario en tiempo real mientras el usuario escribe."""
        from PyQt6.QtCore import QTimer

        # Cancelar timer anterior si existe
        if hasattr(self, "_search_timer"):
            self._search_timer.stop()

        # Crear nuevo timer con delay de 300ms para evitar búsquedas excesivas
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._ejecutar_busqueda_tiempo_real)
        self._search_timer.start(300)

    def _ejecutar_busqueda_tiempo_real(self):
        """Ejecuta la búsqueda con un pequeño delay."""
        try:
            termino_busqueda = self.busqueda_input.text().strip()
            categoria_seleccionada = self.categoria_combo.currentText()

            # Si no hay término de búsqueda y no hay categoría específica, mostrar todos
            if not termino_busqueda and categoria_seleccionada == "Todas":
                if self.controller:
                    self.controller.cargar_datos_iniciales()
                return

            # Aplicar filtros
            self.filtrar_inventario()

        except Exception as e:
            print(f"[ERROR] Error en búsqueda tiempo real: {e}")

    def editar_producto_seleccionado(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('editar_producto_seleccionado'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Edita el producto seleccionado en la tabla."""
        current_row = self.tabla_inventario.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un producto para editar."
            )
            return

        # Obtener datos del producto de la fila seleccionada con acceso seguro
        codigo_item = self.tabla_inventario.item(current_row, 0)
        descripcion_item = self.tabla_inventario.item(current_row, 1)
        categoria_item = self.tabla_inventario.item(current_row, 2)
        stock_item = self.tabla_inventario.item(current_row, 3)

        codigo = codigo_item.text() if codigo_item is not None else ""
        descripcion = descripcion_item.text() if descripcion_item is not None else ""
        categoria = categoria_item.text() if categoria_item is not None else ""
        stock_actual = (
            int(stock_item.text())
            if stock_item is not None and stock_item.text().isdigit()
            else 0
        )

        # Crear producto mock para el diálogo
        producto = {
            "id": current_row,  # Mock ID
            "codigo": codigo,
            "descripcion": descripcion,
            "categoria": categoria,
            "stock_actual": stock_actual,
        }

        self.editar_producto(producto)

    def eliminar_producto_seleccionado(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('eliminar_producto_seleccionado'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Elimina el producto seleccionado en la tabla."""
        current_row = self.tabla_inventario.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un producto para eliminar."
            )
            return

        # Obtener datos del producto de la fila seleccionada con acceso seguro
        codigo_item = self.tabla_inventario.item(current_row, 0)
        descripcion_item = self.tabla_inventario.item(current_row, 1)
        stock_item = self.tabla_inventario.item(current_row, 3)
        stock_reservado_item = self.tabla_inventario.item(current_row, 5)

        codigo = codigo_item.text() if codigo_item is not None else ""
        descripcion = descripcion_item.text() if descripcion_item is not None else ""
        stock_actual = (
            int(stock_item.text())
            if stock_item is not None and stock_item.text().isdigit()
            else 0
        )
        stock_reservado = (
            int(stock_reservado_item.text())
            if stock_reservado_item is not None
            and stock_reservado_item.text().isdigit()
            else 0
        )

        # Crear producto mock para el diálogo
        producto = {
            "id": current_row,  # Mock ID
            "codigo": codigo,
            "descripcion": descripcion,
            "stock_actual": stock_actual,
            "stock_reservado": stock_reservado,
        }

        self.eliminar_producto(producto)

    def mostrar_dialogo_movimiento_seleccionado(self):
        """Muestra el diálogo de movimiento para el producto seleccionado."""
        current_row = self.tabla_inventario.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un producto para registrar movimiento."
            )
            return

        # Obtener datos del producto de la fila seleccionada con acceso seguro
        codigo_item = self.tabla_inventario.item(current_row, 0)
        descripcion_item = self.tabla_inventario.item(current_row, 1)
        stock_item = self.tabla_inventario.item(current_row, 3)

        codigo = codigo_item.text() if codigo_item is not None else ""
        descripcion = descripcion_item.text() if descripcion_item is not None else ""
        stock_actual = (
            int(stock_item.text())
            if stock_item is not None and stock_item.text().isdigit()
            else 0
        )

        # Crear producto mock para el diálogo
        producto = {
            "id": current_row,  # Mock ID
            "codigo": codigo,
            "descripcion": descripcion,
            "stock_actual": stock_actual,
        }

        self.mostrar_dialogo_movimiento(producto)

    def exportar_inventario(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('exportar_inventario'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Exporta el inventario actual."""
        if self.controller:
            self.controller.exportar_inventario()
        else:
            QMessageBox.information(
                self, "Información", "Función de exportación no disponible."
            )


class DialogoNuevoProducto(QDialog):
    """Diálogo para agregar un nuevo producto al inventario."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f"{__name__}.DialogoNuevoProducto")
        self.validator_manager = FormValidatorManager()
        self.setWindowTitle("Nuevo Producto")
        self.setModal(True)
        self.setFixedSize(500, 650)
        self.logger.debug("Inicializando diálogo de nuevo producto")
        self.init_ui()
        self._setup_modern_styling()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Título moderno
        title_label = QLabel("📦 Agregar Nuevo Producto")
        title_label.setProperty("labelType", "title")
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
        self.tipo_combo.addItems(
            ["Marco", "Vidrio", "Herraje", "Accesorio", "Sellador"]
        )
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
        self.observaciones_input.setPlaceholderText(
            "Observaciones adicionales (opcional)"
        )
        form_layout.addRow("📋 Observaciones:", self.observaciones_input)

        form_widget.setWidget(form_content)
        form_widget.setWidgetResizable(True)
        layout.addWidget(form_widget)

        # Botones
        button_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setProperty("buttonType", "secondary")

        self.save_btn = QPushButton("✅ Guardar Producto")
        self.save_btn.clicked.connect(self.validar_y_guardar)
        self.save_btn.setProperty("buttonType", "success")

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addWidget(QWidget())  # Spacer
        layout.addLayout(button_layout)

        # Configurar validaciones
        self.configurar_validaciones()

    def configurar_validaciones(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('configurar_validaciones'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Configura las validaciones del formulario."""
        if not VALIDATORS_AVAILABLE:
            return

        # Validación de código obligatorio con formato específico
        self.validator_manager.agregar_validacion(
            self.codigo_input, validacion_codigo_producto
        )

        # Validación de descripción obligatoria
        self.validator_manager.agregar_validacion(
            self.descripcion_input,
            FormValidator.validar_campo_obligatorio,
            "Descripción",
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
        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto antes de validar
        if SANITIZER_AVAILABLE and data_sanitizer:
            # Sanitizar campos de texto
            codigo_text = data_sanitizer.sanitize_string(self.codigo_input.text())
            descripcion_text = data_sanitizer.sanitize_string(
                self.descripcion_input.text()
            )
            proveedor_text = data_sanitizer.sanitize_string(self.proveedor_input.text())

            # Aplicar texto sanitizado a los campos
            self.codigo_input.setText(codigo_text)
            self.descripcion_input.setText(descripcion_text)
            self.proveedor_input.setText(proveedor_text)

        """Valida el formulario y guarda si es válido."""
        if VALIDATORS_AVAILABLE:
            es_valido, errores = self.validator_manager.validar_formulario()

            if not es_valido:
                # Mostrar errores
                mensajes_error = self.validator_manager.obtener_mensajes_error()
                QMessageBox.warning(
                    self,
                    "Errores de Validación",
                    "Por favor corrige los siguientes errores:\n\n"
                    + "\n".join(mensajes_error),
                )
                return
        else:
            # Validación básica sin validators
            if not self.codigo_input.text().strip():
                QMessageBox.warning(self, "Error", "El código es obligatorio")
                return
            if not self.descripcion_input.text().strip():
                QMessageBox.warning(self, "Error", "La descripción es obligatoria")
                return
            if self.precio_input.value() <= 0:
                QMessageBox.warning(self, "Error", "El precio debe ser mayor a 0")
                return
            if not self.proveedor_input.text().strip():
                QMessageBox.warning(self, "Error", "El proveedor es obligatorio")
                return

        # Si todo es válido, aceptar el diálogo
        self.logger.info(f"Producto validado correctamente: {self.codigo_input.text()}")
        self.accept()

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "codigo": self.codigo_input.text().strip().upper(),
            "descripcion": self.descripcion_input.text().strip(),
            "tipo": self.tipo_combo.currentText(),
            "acabado": self.acabado_combo.currentText(),
            "cantidad": self.cantidad_input.value(),
            "importe": self.precio_input.value(),
            "unidad": self.unidad_combo.currentText(),
            "proveedor": self.proveedor_input.text().strip(),
            "ubicacion": self.ubicacion_input.text().strip(),
            "observaciones": self.observaciones_input.toPlainText().strip(),
        }

    def _setup_modern_styling(self):
        """Configura el estilizado moderno para el diálogo."""
        try:
            from rexus.utils.form_styles import setup_form_widget

            # Aplicar estilos modernos
            setup_form_widget(self, apply_animations=True)
        except ImportError:
            # Si no existe el módulo de estilos, usar estilo básico
            print("[INFO] Form styles module not available, using basic styling")

        # Configurar propiedades específicas de botones
        self.save_btn.setProperty("buttonType", "success")
        self.cancel_btn.setProperty("buttonType", "secondary")

        # Configurar tooltips mejorados
        self.codigo_input.setToolTip("💡 Código único del producto (ej: PROD-001)")
        self.descripcion_input.setToolTip("📝 Descripción detallada del producto")
        self.precio_input.setToolTip("💰 Precio unitario en pesos")
        self.cantidad_input.setToolTip("📦 Cantidad inicial en inventario")
        self.proveedor_input.setToolTip("🏢 Nombre del proveedor principal")
        self.ubicacion_input.setToolTip("📍 Ubicación física en almacén")

        # Refrescar estilos
        style = self.style()
        if style is not None:
            style.polish(self)

        # Configurar validación visual en tiempo real
        self._setup_realtime_validation()

    def _setup_realtime_validation(self):
        """Configura validación visual en tiempo real."""
        try:
            from rexus.utils.form_styles import FormStyleManager
        except ImportError:
            # Si no existe FormStyleManager, usar validación básica
            print("[INFO] FormStyleManager not available, using basic validation")
            return

        def validate_codigo():
            text = self.codigo_input.text().strip()
            if not text:
                FormStyleManager.apply_validation_state(
                    self.codigo_input, "invalid", "El código es obligatorio"
                )
            elif len(text) < 3:
                FormStyleManager.apply_validation_state(
                    self.codigo_input,
                    "warning",
                    "El código debe tener al menos 3 caracteres",
                )
            else:
                FormStyleManager.apply_validation_state(
                    self.codigo_input, "valid", "✓ Código válido"
                )

        def validate_descripcion():
            text = self.descripcion_input.text().strip()
            if not text:
                FormStyleManager.apply_validation_state(
                    self.descripcion_input, "invalid", "La descripción es obligatoria"
                )
            elif len(text) < 5:
                FormStyleManager.apply_validation_state(
                    self.descripcion_input,
                    "warning",
                    "La descripción debe ser más descriptiva",
                )
            else:
                FormStyleManager.apply_validation_state(
                    self.descripcion_input, "valid", "✓ Descripción válida"
                )

        def validate_precio():
            value = self.precio_input.value()
            if value <= 0:
                FormStyleManager.apply_validation_state(
                    self.precio_input, "invalid", "El precio debe ser mayor a 0"
                )
            elif value > 1000000:
                FormStyleManager.apply_validation_state(
                    self.precio_input, "warning", "Precio muy alto, verifique"
                )
            else:
                FormStyleManager.apply_validation_state(
                    self.precio_input, "valid", f"✓ ${value:,.2f}"
                )

        def validate_proveedor():
            text = self.proveedor_input.text().strip()
            if not text:
                FormStyleManager.apply_validation_state(
                    self.proveedor_input, "invalid", "El proveedor es obligatorio"
                )
            else:
                FormStyleManager.apply_validation_state(
                    self.proveedor_input, "valid", "✓ Proveedor válido"
                )

        # Conectar validaciones en tiempo real
        self.codigo_input.textChanged.connect(validate_codigo)
        self.descripcion_input.textChanged.connect(validate_descripcion)
        self.precio_input.valueChanged.connect(validate_precio)
        self.proveedor_input.textChanged.connect(validate_proveedor)

        # Validar inicialmente
        validate_codigo()
        validate_descripcion()
        validate_precio()
        validate_proveedor()
