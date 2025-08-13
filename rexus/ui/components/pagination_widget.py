"""
Sistema de Paginación Inteligente para Rexus.app
Proporciona paginación eficiente para tablas grandes con más de 1000 registros

Fecha: 13/08/2025
Objetivo: Mejorar rendimiento en tablas grandes con paginación optimizada
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
    QComboBox, QLineEdit, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIntValidator
from typing import Callable, Optional, Dict, Any


class PaginationWidget(QWidget):
    """
    Widget de paginación inteligente para tablas grandes.
    
    Características:
    - Paginación eficiente con OFFSET/LIMIT
    - Navegación rápida (primera, última, saltar a página)
    - Tamaños de página configurables
    - Búsqueda con debounce para reducir consultas
    - Información de estado y progreso
    - Integración con SmartCache
    """
    
    # Señales
    page_changed = pyqtSignal(int)  # Nueva página
    page_size_changed = pyqtSignal(int)  # Nuevo tamaño de página
    search_requested = pyqtSignal(str)  # Búsqueda solicitada
    refresh_requested = pyqtSignal()  # Solicitud de actualización
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado de paginación
        self.current_page = 1
        self.total_pages = 1
        self.page_size = 50
        self.total_records = 0
        self.available_page_sizes = [25, 50, 100, 200, 500]
        
        # Configuración de búsqueda
        self.search_debounce_timer = QTimer()
        self.search_debounce_timer.setSingleShot(True)
        self.search_debounce_timer.timeout.connect(self._emit_search)
        self.search_debounce_delay = 500  # ms
        self.current_search_term = ""
        
        # Callbacks para cargar datos
        self.data_loader: Optional[Callable] = None
        self.search_loader: Optional[Callable] = None
        
        self._init_ui()
        self._connect_signals()
        self._apply_styles()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(10)
        
        # Marco principal
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        main_frame.setObjectName("paginationFrame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(15, 10, 15, 10)
        frame_layout.setSpacing(10)
        
        # Layout superior: Búsqueda y controles de página
        top_layout = QHBoxLayout()
        
        # Sección de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        search_label.setObjectName("searchLabel")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en registros...")
        self.search_input.setObjectName("searchInput")
        self.search_input.setMaximumWidth(300)
        
        self.clear_search_btn = QPushButton("✖")
        self.clear_search_btn.setObjectName("clearSearchBtn")
        self.clear_search_btn.setMaximumWidth(30)
        self.clear_search_btn.setToolTip("Limpiar búsqueda")
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_search_btn)
        
        # Espaciador
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Sección de tamaño de página
        page_size_layout = QHBoxLayout()
        page_size_label = QLabel("Registros por página:")
        page_size_label.setObjectName("pageSizeLabel")
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.setObjectName("pageSizeCombo")
        for size in self.available_page_sizes:
            self.page_size_combo.addItem(str(size), size)
        self.page_size_combo.setCurrentText(str(self.page_size))
        
        page_size_layout.addWidget(page_size_label)
        page_size_layout.addWidget(self.page_size_combo)
        
        # Ensamblar layout superior
        top_layout.addLayout(search_layout)
        top_layout.addItem(spacer)
        top_layout.addLayout(page_size_layout)
        
        # Layout inferior: Navegación de páginas
        nav_layout = QHBoxLayout()
        
        # Botones de navegación
        self.first_btn = QPushButton("⏮️ Primera")
        self.first_btn.setObjectName("firstBtn")
        
        self.prev_btn = QPushButton("◀️ Anterior")
        self.prev_btn.setObjectName("prevBtn")
        
        # Entrada directa de página
        page_input_layout = QHBoxLayout()
        page_label = QLabel("Página:")
        
        self.page_input = QLineEdit()
        self.page_input.setObjectName("pageInput")
        self.page_input.setMaximumWidth(60)
        self.page_input.setValidator(QIntValidator(1, 9999))
        
        self.page_info_label = QLabel("de 1")
        self.page_info_label.setObjectName("pageInfoLabel")
        
        page_input_layout.addWidget(page_label)
        page_input_layout.addWidget(self.page_input)
        page_input_layout.addWidget(self.page_info_label)
        
        self.next_btn = QPushButton("Siguiente ▶️")
        self.next_btn.setObjectName("nextBtn")
        
        self.last_btn = QPushButton("Última ⏭️")
        self.last_btn.setObjectName("lastBtn")
        
        # Botón de actualización
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setToolTip("Actualizar datos")
        
        # Ensamblar navegación
        nav_layout.addWidget(self.first_btn)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addLayout(page_input_layout)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.last_btn)
        nav_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        nav_layout.addWidget(self.refresh_btn)
        
        # Información de estado
        self.status_label = QLabel("Sin datos")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ensamblar todo
        frame_layout.addLayout(top_layout)
        frame_layout.addLayout(nav_layout)
        frame_layout.addWidget(self.status_label)
        
        main_layout.addWidget(main_frame)
        
        # Estado inicial
        self._update_ui_state()
    
    def _connect_signals(self):
        """Conecta las señales de los controles."""
        # Navegación
        self.first_btn.clicked.connect(self.go_to_first_page)
        self.prev_btn.clicked.connect(self.go_to_previous_page)
        self.next_btn.clicked.connect(self.go_to_next_page)
        self.last_btn.clicked.connect(self.go_to_last_page)
        
        # Entrada directa de página
        self.page_input.returnPressed.connect(self._on_page_input_entered)
        
        # Tamaño de página
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        
        # Búsqueda con debounce
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        # Actualización
        self.refresh_btn.clicked.connect(self.refresh_data)
    
    def _apply_styles(self):
        """Aplica estilos al widget."""
        self.setStyleSheet("""
            #paginationFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            
            #searchLabel, #pageSizeLabel {
                font-weight: bold;
                color: #475569;
            }
            
            #searchInput {
                padding: 6px 12px;
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            
            #searchInput:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            #clearSearchBtn {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            
            #clearSearchBtn:hover {
                background-color: #dc2626;
            }
            
            #pageSizeCombo {
                padding: 4px 8px;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: white;
            }
            
            #firstBtn, #prevBtn, #nextBtn, #lastBtn {
                padding: 6px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background-color: white;
                font-weight: bold;
            }
            
            #firstBtn:hover, #prevBtn:hover, #nextBtn:hover, #lastBtn:hover {
                background-color: #e2e8f0;
            }
            
            #firstBtn:disabled, #prevBtn:disabled, #nextBtn:disabled, #lastBtn:disabled {
                background-color: #f1f5f9;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            
            #pageInput {
                padding: 4px 8px;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: white;
                text-align: center;
                font-weight: bold;
            }
            
            #pageInfoLabel {
                font-weight: bold;
                color: #475569;
            }
            
            #refreshBtn {
                padding: 6px 12px;
                border: 1px solid #10b981;
                border-radius: 6px;
                background-color: #10b981;
                color: white;
                font-weight: bold;
            }
            
            #refreshBtn:hover {
                background-color: #059669;
            }
            
            #statusLabel {
                color: #64748b;
                font-style: italic;
                padding: 5px;
            }
        """)
    
    def set_data_loader(self, loader: Callable[[int, int], Dict[str, Any]]):
        """
        Establece el callback para cargar datos paginados.
        
        Args:
            loader: Función que acepta (page, page_size) y retorna Dict con:
                   - 'data': Lista de registros
                   - 'total': Total de registros
                   - 'page': Página actual
                   - 'page_size': Tamaño de página
        """
        self.data_loader = loader
    
    def set_search_loader(self, loader: Callable[[str, int, int], Dict[str, Any]]):
        """
        Establece el callback para búsqueda paginada.
        
        Args:
            loader: Función que acepta (search_term, page, page_size) y retorna Dict con:
                   - 'data': Lista de registros filtrados
                   - 'total': Total de registros que coinciden
                   - 'page': Página actual
                   - 'page_size': Tamaño de página
        """
        self.search_loader = loader
    
    def update_pagination_info(self, total_records: int, current_page: int = None):
        """
        Actualiza la información de paginación.
        
        Args:
            total_records: Total de registros disponibles
            current_page: Página actual (opcional)
        """
        self.total_records = total_records
        if current_page is not None:
            self.current_page = current_page
        
        # Calcular total de páginas
        self.total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        
        # Asegurar que la página actual es válida
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Actualiza el estado de la interfaz de usuario."""
        # Actualizar entrada de página
        self.page_input.setText(str(self.current_page))
        self.page_info_label.setText(f"de {self.total_pages}")
        
        # Habilitar/deshabilitar botones
        self.first_btn.setEnabled(self.current_page > 1)
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        self.last_btn.setEnabled(self.current_page < self.total_pages)
        
        # Actualizar información de estado
        start_record = ((self.current_page - 1) * self.page_size) + 1
        end_record = min(self.current_page * self.page_size, self.total_records)
        
        if self.total_records > 0:
            status_text = f"Mostrando {start_record}-{end_record} de {self.total_records:,} registros"
            if self.current_search_term:
                status_text += f" (filtrado por: '{self.current_search_term}')"
        else:
            status_text = "No hay registros para mostrar"
            if self.current_search_term:
                status_text = f"No se encontraron resultados para: '{self.current_search_term}'"
        
        self.status_label.setText(status_text)
    
    def go_to_first_page(self):
        """Navega a la primera página."""
        if self.current_page != 1:
            self.current_page = 1
            self._emit_page_change()
    
    def go_to_previous_page(self):
        """Navega a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self._emit_page_change()
    
    def go_to_next_page(self):
        """Navega a la página siguiente."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._emit_page_change()
    
    def go_to_last_page(self):
        """Navega a la última página."""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self._emit_page_change()
    
    def go_to_page(self, page: int):
        """
        Navega a una página específica.
        
        Args:
            page: Número de página (1-based)
        """
        page = max(1, min(page, self.total_pages))
        if page != self.current_page:
            self.current_page = page
            self._emit_page_change()
    
    def _on_page_input_entered(self):
        """Maneja la entrada directa de página."""
        try:
            page = int(self.page_input.text())
            self.go_to_page(page)
        except ValueError:
            # Restaurar valor actual si la entrada es inválida
            self.page_input.setText(str(self.current_page))
    
    def _on_page_size_changed(self, text: str):
        """Maneja el cambio de tamaño de página."""
        try:
            new_size = int(text)
            if new_size != self.page_size:
                self.page_size = new_size
                # Recalcular página actual para mantener registros visibles
                first_record = ((self.current_page - 1) * self.page_size) + 1
                self.current_page = max(1, (first_record + new_size - 1) // new_size)
                self.page_size_changed.emit(new_size)
                self._emit_page_change()
        except ValueError:
            pass
    
    def _on_search_text_changed(self, text: str):
        """Maneja el cambio en el texto de búsqueda con debounce."""
        self.search_debounce_timer.stop()
        self.current_search_term = text.strip()
        
        if self.current_search_term:
            self.search_debounce_timer.start(self.search_debounce_delay)
        else:
            self._emit_search()
    
    def _emit_search(self):
        """Emite la señal de búsqueda."""
        self.current_page = 1  # Resetear a primera página en búsqueda
        self.search_requested.emit(self.current_search_term)
    
    def clear_search(self):
        """Limpia la búsqueda."""
        self.search_input.clear()
        self.current_search_term = ""
        self.current_page = 1
        self.search_requested.emit("")
    
    def refresh_data(self):
        """Solicita actualización de datos."""
        self.refresh_requested.emit()
    
    def _emit_page_change(self):
        """Emite la señal de cambio de página."""
        self._update_ui_state()
        self.page_changed.emit(self.current_page)
    
    def get_current_page(self) -> int:
        """Retorna la página actual."""
        return self.current_page
    
    def get_page_size(self) -> int:
        """Retorna el tamaño de página actual."""
        return self.page_size
    
    def get_search_term(self) -> str:
        """Retorna el término de búsqueda actual."""
        return self.current_search_term
    
    def set_loading_state(self, loading: bool):
        """
        Establece el estado de carga.
        
        Args:
            loading: True si está cargando, False si no
        """
        self.setEnabled(not loading)
        if loading:
            self.status_label.setText("Cargando datos...")
        else:
            self._update_ui_state()


# Ejemplo de uso en módulos
"""
# En el módulo/vista:
from rexus.ui.components.pagination_widget import PaginationWidget

class MiModuloView(BaseModuleView):
    def __init__(self):
        super().__init__()
        
        # Crear widget de paginación
        self.pagination = PaginationWidget()
        self.pagination.set_data_loader(self.load_paginated_data)
        self.pagination.set_search_loader(self.search_paginated_data)
        
        # Conectar señales
        self.pagination.page_changed.connect(self.on_page_changed)
        self.pagination.search_requested.connect(self.on_search_requested)
        self.pagination.refresh_requested.connect(self.refresh_table)
        
        # Agregar al layout
        layout.addWidget(self.pagination)
    
    def load_paginated_data(self, page: int, page_size: int) -> Dict:
        # Cargar datos paginados desde el modelo
        return self.model.obtener_datos_paginados(page, page_size)
    
    def search_paginated_data(self, search_term: str, page: int, page_size: int) -> Dict:
        # Buscar datos paginados
        return self.model.buscar_datos_paginados(search_term, page, page_size)
    
    def on_page_changed(self, page: int):
        # Cargar nueva página
        self.load_table_data()
    
    def on_search_requested(self, search_term: str):
        # Realizar búsqueda
        self.load_table_data()
"""