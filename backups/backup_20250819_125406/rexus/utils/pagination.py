"""
Sistema de paginación para Rexus.app

Proporciona componentes de paginación para tablas grandes
mejorando el rendimiento y la experiencia de usuario.
"""

from typing import Dict, List, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSpinBox,
    QComboBox, QFrame, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import pyqtSignal
import math


class PaginationInfo:
    """Información de paginación."""

    def __init__(self,
page: int = 1,
        page_size: int = 50,
        total_items: int = 0):
        self.page = max(1, page)
        self.page_size = max(1, page_size)
        self.total_items = max(0, total_items)

    @property
    def total_pages(self) -> int:
        """Calcula el número total de páginas."""
        if self.total_items == 0:
            return 1
        return math.ceil(self.total_items / self.page_size)

    @property
    def offset(self) -> int:
        """Calcula el offset para la consulta SQL (OFFSET)."""
        return (self.page - 1) * self.page_size

    @property
    def has_previous(self) -> bool:
        """Verifica si hay página anterior."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """Verifica si hay página siguiente."""
        return self.page < self.total_pages

    @property
    def start_item(self) -> int:
        """Número del primer elemento en la página actual."""
        if self.total_items == 0:
            return 0
        return self.offset + 1

    @property
    def end_item(self) -> int:
        """Número del último elemento en la página actual."""
        end = self.offset + self.page_size
        return min(end, self.total_items)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la información a diccionario."""
        return {
            'page': self.page,
            'page_size': self.page_size,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'offset': self.offset,
            'has_previous': self.has_previous,
            'has_next': self.has_next,
            'start_item': self.start_item,
            'end_item': self.end_item
        }


class PaginationWidget(QWidget):
    """Widget de controles de paginación."""

    # Señales
    page_changed = pyqtSignal(int)  # Nueva página
    page_size_changed = pyqtSignal(int)  # Nuevo tamaño de página

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pagination_info = PaginationInfo()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Frame contenedor con estilo
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QLabel {
                color: #495057;
                font-weight: normal;
            }
        """)

        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(10, 5, 10, 5)

        # Botón Primera página
        self.first_btn = QPushButton("⏮")
        self.first_btn.setToolTip("Primera página")
        self.first_btn.clicked.connect(self.go_first_page)
        frame_layout.addWidget(self.first_btn)

        # Botón Página anterior
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setToolTip("Página anterior")
        self.prev_btn.clicked.connect(self.go_previous_page)
        frame_layout.addWidget(self.prev_btn)

        # Control de página actual
        frame_layout.addWidget(QLabel("Página:"))
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.on_page_changed)
        frame_layout.addWidget(self.page_spin)

        # Label total de páginas
        self.total_pages_label = QLabel("de 1")
        frame_layout.addWidget(self.total_pages_label)

        # Botón Página siguiente
        self.next_btn = QPushButton("▶")
        self.next_btn.setToolTip("Página siguiente")
        self.next_btn.clicked.connect(self.go_next_page)
        frame_layout.addWidget(self.next_btn)

        # Botón Última página
        self.last_btn = QPushButton("⏭")
        self.last_btn.setToolTip("Última página")
        self.last_btn.clicked.connect(self.go_last_page)
        frame_layout.addWidget(self.last_btn)

        # Separador
        frame_layout.addWidget(QLabel(" | "))

        # Control de elementos por página
        frame_layout.addWidget(QLabel("Mostrar:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "25", "50", "100", "200"])
        self.page_size_combo.setCurrentText("50")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        frame_layout.addWidget(self.page_size_combo)
        frame_layout.addWidget(QLabel("por página"))

        # Separador
        frame_layout.addWidget(QLabel(" | "))

        # Información de elementos
        self.info_label = QLabel("0 - 0 de 0 elementos")
        frame_layout.addWidget(self.info_label)

        # Espacio flexible
        frame_layout.addStretch()

        layout.addWidget(frame)

    def update_pagination(self, pagination_info: PaginationInfo):
        """Actualiza la información de paginación."""
        self.pagination_info = pagination_info

        # Actualizar controles
        self.page_spin.setMaximum(max(1, pagination_info.total_pages))
        self.page_spin.setValue(pagination_info.page)

        self.total_pages_label.setText(f"de {pagination_info.total_pages}")

        # Actualizar estados de botones
        self.first_btn.setEnabled(pagination_info.has_previous)
        self.prev_btn.setEnabled(pagination_info.has_previous)
        self.next_btn.setEnabled(pagination_info.has_next)
        self.last_btn.setEnabled(pagination_info.has_next)

        # Actualizar información
        if pagination_info.total_items > 0:
            info_text = f"{pagination_info.start_item} - {pagination_info.end_item} de {pagination_info.total_items} elementos"
        else:
            info_text = "0 elementos"
        self.info_label.setText(info_text)

    def go_first_page(self):
        """Va a la primera página."""
        if self.pagination_info.has_previous:
            self.page_changed.emit(1)

    def go_previous_page(self):
        """Va a la página anterior."""
        if self.pagination_info.has_previous:
            self.page_changed.emit(self.pagination_info.page - 1)

    def go_next_page(self):
        """Va a la página siguiente."""
        if self.pagination_info.has_next:
            self.page_changed.emit(self.pagination_info.page + 1)

    def go_last_page(self):
        """Va a la última página."""
        if self.pagination_info.has_next:
            self.page_changed.emit(self.pagination_info.total_pages)

    def on_page_changed(self, page: int):
        """Maneja el cambio de página desde el spinbox."""
        if page != self.pagination_info.page:
            self.page_changed.emit(page)

    def on_page_size_changed(self, page_size_text: str):
        """Maneja el cambio de tamaño de página."""
        try:
            page_size = int(page_size_text)
            if page_size != self.pagination_info.page_size:
                self.page_size_changed.emit(page_size)
        except ValueError:
            pass


class PaginatedTableMixin:
    """
    Mixin para agregar paginación a modelos de datos.

    Las clases que hereden este mixin deben implementar:
    - get_paginated_data(offset,
limit,
        filters=None) -> Tuple[List[Dict],
        int]
    """

    def __init__(self):
        self.pagination_info = PaginationInfo()
        self.current_filters = {}

    def get_paginated_results(self, page: int = 1, page_size: int = 50,
                            filters: Optional[Dict] = None) -> Tuple[List[Dict], PaginationInfo]:
        """
        Obtiene resultados paginados.

        Args:
            page: Número de página (empezando desde 1)
            page_size: Elementos por página
            filters: Filtros adicionales

        Returns:
            Tupla (datos, información_paginación)
        """
        # Actualizar filtros si se proporcionan
        if filters is not None:
            self.current_filters = filters

        # Calcular offset
        offset = (page - 1) * page_size

        try:
            # Obtener datos y total (debe implementarse en la clase hija)
            data, total_items = self.get_paginated_data(offset,
                                                       page_size,
                                                       self.current_filters)

            # Crear información de paginación
            pagination_info = PaginationInfo(page, page_size, total_items)

            self.pagination_info = pagination_info
            return data, pagination_info

        except Exception as e:
            print(f"Error obteniendo datos paginados: {e}")
            return [], PaginationInfo(page, page_size, 0)

    def get_paginated_data(self, offset: int, limit: int,
                          filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
        """
        Método que debe implementarse en las clases hijas.

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filters: Diccionario con filtros adicionales

        Returns:
            Tupla (lista_datos, total_elementos)

        Raises:
            NotImplementedError: Si no se implementa en la clase hija
        """
        raise NotImplementedError("Las clases hijas deben implementar get_paginated_data()")


def create_pagination_query(base_query: str, count_query: str = None) -> Tuple[str, str]:
    """
    Crea consultas SQL con paginación.

    Args:
        base_query: Consulta SQL base (SELECT ... FROM ... WHERE ...)
        count_query: Consulta de conteo opcional

    Returns:
        Tupla (consulta_paginada, consulta_conteo)
    """
    # Consulta paginada con OFFSET y FETCH
    paginated_query = f"""
        {base_query}
        ORDER BY id DESC
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY
    """

    # Consulta de conteo
    if count_query is None:
        # Extraer la parte SELECT y reemplazar por COUNT
        if "SELECT" in base_query.upper() and "FROM" in base_query.upper():
            from_index = base_query.upper().find("FROM")
            from_part = base_query[from_index:]
            count_query = f"SELECT COUNT(*) {from_part}"
        else:
            count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_subquery"

    return paginated_query.strip(), count_query.strip()


# Ejemplos de uso y funciones de utilidad

def apply_pagination_to_table(table_widget: QTableWidget, data: List[Dict],
                             columns: List[str]):
    """
    Aplica datos paginados a un QTableWidget.

    Args:
        table_widget: Widget de tabla
        data: Lista de datos a mostrar
        columns: Lista de nombres de columnas
    """
    table_widget.setRowCount(len(data))
    table_widget.setColumnCount(len(columns))
    table_widget.setHorizontalHeaderLabels(columns)

    for row, item in enumerate(data):
        for col, column_name in enumerate(columns):
            value = item.get(column_name, "")
            table_widget.setItem(row, col, QTableWidgetItem(str(value)))


def get_optimized_page_size(total_items: int) -> int:
    """
    Calcula un tamaño de página optimizado basado en el total de elementos.

    Args:
        total_items: Número total de elementos

    Returns:
        Tamaño de página optimizado
    """
    if total_items <= 100:
        return 25
    elif total_items <= 1000:
        return 50
    elif total_items <= 10000:
        return 100
    else:
        return 200
