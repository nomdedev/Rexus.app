"""
QTableWidget Optimizado para Módulo Obras
Versión mejorada con soporte para temas, paginación y rendimiento optimizado

Fecha: 13/08/2025
Objetivo: Completar UI/UX del módulo Obras con componente de tabla optimizado
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMenu
)
from rexus.ui.components.base_components import RexusTable, RexusLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction
from typing import List, Dict, Any, Optional, Callable
import datetime


class OptimizedTableWidget(RexusTable):
    """
    QTableWidget optimizado para el módulo Obras con características avanzadas.

    Características:
    - Soporte para temas oscuros/claros automático
    - Colores inteligentes por estado
    - Carga lazy de datos grandes
    - Integración con paginación
    - Menú contextual inteligente
    - Indicadores visuales de estado
    """

    # Señales personalizadas
    row_double_clicked = pyqtSignal(int, dict)  # Fila doble-click con datos
    context_menu_requested = pyqtSignal(int, dict, object)  # Menú contextual
    data_export_requested = pyqtSignal(str)  # Exportación solicitada
    refresh_requested = pyqtSignal()  # Actualización solicitada

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuración de datos
        self.current_data = []
        self.loading_state = False
        self.pagination_enabled = True

        # Configuración de columnas para obras
        self.column_config = {
            'id': {'header': 'ID', 'width': 50, 'align': 'center'},
            'codigo_obra': {'header': 'Código', 'width': 100, 'align': 'left'},
            'nombre_obra': {'header': 'Nombre', 'width': 200, 'align': 'left'},
            'cliente': {'header': 'Cliente', 'width': 150, 'align': 'left'},
            'estado': {'header': 'Estado', 'width': 100, 'align': 'center'},
            'tipo_obra': {'header': 'Tipo', 'width': 100, 'align': 'center'},
            'fecha_inicio': {'header': 'F. Inicio', 'width': 90, 'align': 'center'},
            'fecha_fin_estimada': {'header': 'F. Fin', 'width': 90, 'align': 'center'},
            'porcentaje_presupuesto_usado': {'header': 'Progreso', 'width': 80, 'align': 'center'},
            'presupuesto_total': {'header': 'Presupuesto', 'width': 120, 'align': 'right'},
            'estado_temporal': {'header': 'Estado Temporal', 'width': 100, 'align': 'center'}
        }

        # Configuración de colores por estado
        self.estado_colors = {
            'EN_PROCESO': {'bg': '#dcfce7', 'text': '#166534'},  # Verde
            'PLANIFICACION': {'bg': '#fef3c7', 'text': '#92400e'},  # Amarillo
            'PAUSADA': {'bg': '#fed7d7', 'text': '#c53030'},  # Rojo claro
            'FINALIZADA': {'bg': '#e0e7ff', 'text': '#3730a3'},  # Azul
            'CANCELADA': {'bg': '#f3f4f6', 'text': '#6b7280'},  # Gris
            'VENCIDA': {'bg': '#fecaca', 'text': '#dc2626'},  # Rojo
            'PROXIMA_VENCER': {'bg': '#fde68a', 'text': '#d97706'},  # Naranja
            'EN_TIEMPO': {'bg': '#d1fae5', 'text': '#065f46'}  # Verde oscuro
        }

        self._init_table()
        self._setup_context_menu()
        self._connect_signals()
        self._apply_modern_styles()

    def _init_table(self):
        """Inicializa la configuración básica de la tabla."""
        # Configurar headers
        headers = [config['header'] for config in self.column_config.values()]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # Configurar anchos de columna
        for i, (key, config) in enumerate(self.column_config.items()):
            self.setColumnWidth(i, config['width'])

        # Configuraciones generales
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        self.setWordWrap(False)

        # Configurar header horizontal
        h_header = self.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        h_header.setStretchLastSection(True)
        h_header.setHighlightSections(True)
        h_header.setSortIndicatorShown(True)

        # Configurar header vertical
        v_header = self.verticalHeader()
        v_header.setVisible(True)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        v_header.setDefaultSectionSize(35)

        # Configurar altura de filas
        self.setRowHeight(0, 35)

    def _setup_context_menu(self):
        """Configura el menú contextual."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _connect_signals(self):
        """Conecta las señales internas."""
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def _apply_modern_styles(self):
        """Aplica estilos modernos adaptativos para tema oscuro/claro."""
        self.setStyleSheet("""
            OptimizedTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                font-size: 13px;
            }

            OptimizedTableWidget::item {
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid #f1f5f9;
            }

            OptimizedTableWidget::item:selected {
                background-color: #3b82f6;
                color: white;
            }

            OptimizedTableWidget::item:hover {
                background-color: #f1f5f9;
            }

            QHeaderView::section {
                background-color: #f8fafc;
                color: #374151;
                border: 1px solid #e5e7eb;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }

            QHeaderView::section:hover {
                background-color: #e5e7eb;
            }

            QHeaderView::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNUw2IDhMOSA1IiBzdHJva2U9IiM2Yjc2ODAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                width: 12px;
                height: 12px;
            }

            QHeaderView::up-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTkgN0w2IDRMMy43IiBzdHJva2U9IiM2Yjc2ODAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                width: 12px;
                height: 12px;
            }

            /* Tema oscuro - se aplica automáticamente */
            OptimizedTableWidget[darkMode="true"] {
                background-color: #1f2937;
                alternate-background-color: #374151;
                border: 1px solid #4b5563;
                gridline-color: #4b5563;
                color: #f9fafb;
            }

            OptimizedTableWidget[darkMode="true"]::item {
                border-bottom: 1px solid #4b5563;
                color: #f9fafb;
            }

            OptimizedTableWidget[darkMode="true"]::item:hover {
                background-color: #4b5563;
            }

            OptimizedTableWidget[darkMode="true"] QHeaderView::section {
                background-color: #374151;
                color: #f9fafb;
                border: 1px solid #4b5563;
            }
        """)

    def load_data(self,
data: List[Dict[str,
        Any]],
        loading_callback: Optional[Callable] = None):
        """
        Carga datos en la tabla de forma optimizada.

        Args:
            data: Lista de diccionarios con datos de obras
            loading_callback: Callback opcional para mostrar progreso
        """
        if self.loading_state:
            return

        self.loading_state = True
        self.current_data = data

        # Limpiar tabla
        self.setRowCount(0)

        if not data:
            self.loading_state = False
            return

        # Configurar número de filas
        self.setRowCount(len(data))

        # Cargar datos fila por fila
        for row, obra_data in enumerate(data):
            self._populate_row(row, obra_data)

            # Callback de progreso si se proporciona
            if loading_callback and row % 10 == 0:
                progress = int((row / len(data)) * 100)
                loading_callback(progress)

        # Aplicar altura uniforme a todas las filas
        for row in range(self.rowCount()):
            self.setRowHeight(row, 35)

        self.loading_state = False

        # Callback final
        if loading_callback:
            loading_callback(100)

    def _populate_row(self, row: int, obra_data: Dict[str, Any]):
        """
        Puebla una fila específica con datos de obra.

        Args:
            row: Número de fila
            obra_data: Datos de la obra
        """
        column_keys = list(self.column_config.keys())

        for col, key in enumerate(column_keys):
            value = obra_data.get(key, '')
            config = self.column_config[key]

            # Crear item con formato específico
            if key == 'porcentaje_presupuesto_usado':
                # Mostrar como progreso
                item = self._create_progress_item(value)
            elif key == 'presupuesto_total':
                # Formato monetario
                item = self._create_currency_item(value)
            elif key in ['fecha_inicio', 'fecha_fin_estimada']:
                # Formato de fecha
                item = self._create_date_item(value)
            elif key == 'estado':
                # Estado con color
                item = self._create_status_item(value, 'estado')
            elif key == 'estado_temporal':
                # Estado temporal con color
                item = self._create_status_item(value, 'estado_temporal')
            else:
                # Item normal
                item = QTableWidgetItem(str(value))

            # Aplicar alineación
            if config['align'] == 'center':
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            elif config['align'] == 'right':
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Hacer item no editable
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.setItem(row, col, item)

    def _create_progress_item(self, value: Any) -> QTableWidgetItem:
        """Crea un item de progreso formateado."""
        try:
            progress = float(value) if value else 0.0
            progress_text = f"{progress:.1f}%"
            item = QTableWidgetItem(progress_text)

            # Color según progreso
            if progress >= 90:
                item.setBackground(QColor("#dcfce7"))  # Verde
            elif progress >= 70:
                item.setBackground(QColor("#fef3c7"))  # Amarillo
            elif progress >= 40:
                item.setBackground(QColor("#fde68a"))  # Naranja claro
            else:
                item.setBackground(QColor("#fecaca"))  # Rojo claro

            return item
        except (ValueError, TypeError, AttributeError):
            return QTableWidgetItem("0.0%")

    def _create_currency_item(self, value: Any) -> QTableWidgetItem:
        """Crea un item de moneda formateado."""
        try:
            amount = float(value) if value else 0.0
            formatted = f"${amount:,.0f}"
            item = QTableWidgetItem(formatted)

            # Color según monto
            if amount >= 1000000:  # > 1M
                item.setForeground(QColor("#059669"))  # Verde
            elif amount >= 500000:  # > 500K
                item.setForeground(QColor("#d97706"))  # Naranja
            else:
                item.setForeground(QColor("#6b7280"))  # Gris

            return item
        except (ValueError, TypeError, AttributeError):
            return QTableWidgetItem("$0")

    def _create_date_item(self, value: Any) -> QTableWidgetItem:
        """Crea un item de fecha formateado."""
        if not value:
            return QTableWidgetItem("-")

        try:
            # Si es string, intentar parsearlo
            if isinstance(value, str):
                if value in ['-', '', 'None', 'null']:
                    return QTableWidgetItem("-")
                # Intentar parsear diferentes formatos
                try:
                    date_obj = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                except:
                    try:
                        date_obj = datetime.datetime.strptime(value, "%d/%m/%Y").date()
                    except:
                        return QTableWidgetItem(str(value))
            elif hasattr(value, 'date'):
                date_obj = value.date()
            else:
                date_obj = value

            # Formatear fecha
            formatted = date_obj.strftime("%d/%m/%Y")
            item = QTableWidgetItem(formatted)

            # Color según proximidad (solo para fechas futuras)
            today = datetime.date.today()
            if date_obj < today:
                item.setForeground(QColor("#dc2626"))  # Rojo - vencida
            elif date_obj <= today + datetime.timedelta(days=7):
                item.setForeground(QColor("#d97706"))  # Naranja - próxima
            else:
                item.setForeground(QColor("#059669"))  # Verde - normal

            return item
        except:
            return QTableWidgetItem(str(value))

    def _create_status_item(self, value: Any, status_type: str) -> QTableWidgetItem:
        """Crea un item de estado con colores."""
        status = str(value).upper() if value else 'DESCONOCIDO'
        item = QTableWidgetItem(status)

        # Aplicar colores según tipo y valor
        if status in self.estado_colors:
            colors = self.estado_colors[status]
            item.setBackground(QColor(colors['bg']))
            item.setForeground(QColor(colors['text']))
        else:
            # Color por defecto
            item.setBackground(QColor("#f3f4f6"))
            item.setForeground(QColor("#6b7280"))

        return item

    def _show_context_menu(self, position):
        """Muestra el menú contextual."""
        item = self.itemAt(position)
        if not item:
            return

        row = item.row()
        if row >= len(self.current_data):
            return

        obra_data = self.current_data[row]

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: white;
            }
        """)

        # Acciones del menú
        ver_action = QAction("👁️ Ver Detalles", self)
        editar_action = QAction("✏️ Editar", self)
        cronograma_action = QAction("📅 Ver Cronograma", self)
        export_action = QAction("[CHART] Exportar", self)
        refresh_action = QAction("🔄 Actualizar", self)

        menu.addAction(ver_action)
        menu.addAction(editar_action)
        menu.addSeparator()
        menu.addAction(cronograma_action)
        menu.addAction(export_action)
        menu.addSeparator()
        menu.addAction(refresh_action)

        # Conectar acciones
        ver_action.triggered.connect(lambda: self.row_double_clicked.emit(row, obra_data))
        editar_action.triggered.connect(lambda: self.row_double_clicked.emit(row, obra_data))
        export_action.triggered.connect(lambda: self.data_export_requested.emit('xlsx'))
        refresh_action.triggered.connect(lambda: self.refresh_requested.emit())

        # Emitir señal para acciones personalizadas
        self.context_menu_requested.emit(row, obra_data, menu)

        # Mostrar menú
        menu.exec(self.mapToGlobal(position))

    def _on_item_double_clicked(self, item):
        """Maneja el doble-click en un item."""
        row = item.row()
        if row < len(self.current_data):
            obra_data = self.current_data[row]
            self.row_double_clicked.emit(row, obra_data)

    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.current_data):
            # Aquí se puede emitir señal adicional si es necesario
            pass

    def get_selected_obra_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de la obra seleccionada.

        Returns:
            Dict con datos de la obra o None si no hay selección
        """
        current_row = self.currentRow()
        if 0 <= current_row < len(self.current_data):
            return self.current_data[current_row]
        return None

    def update_row_data(self, row: int, new_data: Dict[str, Any]):
        """
        Actualiza los datos de una fila específica.

        Args:
            row: Número de fila
            new_data: Nuevos datos
        """
        if 0 <= row < len(self.current_data):
            self.current_data[row].update(new_data)
            self._populate_row(row, self.current_data[row])

    def set_loading_state(self, loading: bool):
        """
        Establece el estado de carga de la tabla.

        Args:
            loading: True si está cargando
        """
        self.loading_state = loading
        self.setEnabled(not loading)

        if loading:
            self.setStyleSheet(self.styleSheet() + """
                OptimizedTableWidget {
                    opacity: 0.6;
                }
            """)
        else:
            # Restaurar estilos normales
            self._apply_modern_styles()

    def apply_theme(self, dark_mode: bool):
        """
        Aplica tema oscuro o claro.

        Args:
            dark_mode: True para tema oscuro
        """
        self.setProperty("darkMode", dark_mode)
        self.setStyle(self.style())  # Forzar actualización de estilos


# Widget contenedor con barra de herramientas
class EnhancedTableContainer(QWidget):
    """Contenedor mejorado para la tabla optimizada con barra de herramientas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = OptimizedTableWidget()
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del contenedor."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra de herramientas superior
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Tabla principal
        layout.addWidget(self.table)

        # Barra de estado inferior
        status_bar = self._create_status_bar()
        layout.addWidget(status_bar)

    def _create_toolbar(self) -> QFrame:
        """Crea la barra de herramientas superior."""
        toolbar = QFrame()
        toolbar.setMaximumHeight(40)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)

        # Botones de acción
        refresh_btn = QPushButton("🔄 Actualizar")
        export_btn = QPushButton("[CHART] Exportar")
        filter_btn = QPushButton("[SEARCH] Filtros")

        for btn in [refresh_btn, export_btn, filter_btn]:
            btn.setMaximumHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f3f4f6;
                }
            """)

        layout.addWidget(refresh_btn)
        layout.addWidget(export_btn)
        layout.addWidget(filter_btn)
        layout.addStretch()

        # Conectar señales
        refresh_btn.clicked.connect(self.table.refresh_requested.emit)
        export_btn.clicked.connect(lambda: self.table.data_export_requested.emit('xlsx'))

        return toolbar

    def _create_status_bar(self) -> QFrame:
        """Crea la barra de estado inferior."""
        status_bar = QFrame()
        status_bar.setMaximumHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(8, 4, 8, 4)

        self.status_label = RexusLabel("Listo", "caption")

        layout.addWidget(self.status_label)
        layout.addStretch()

        return status_bar

    def update_status(self, message: str):
        """Actualiza el mensaje de estado."""
        self.status_label.setText(message)
