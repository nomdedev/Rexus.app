"""
QTableWidget Optimizado para Módulo Obras
Versión mejorada con soporte para temas, paginación y rendimiento optimizado

Fecha: 13/08/2025
Objetivo: Completar UI/UX del módulo Obras con componente de tabla optimizado
"""


import logging
logger = logging.getLogger(__name__)

            
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
