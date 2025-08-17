"""
Vista de Logística Refactorizada - Rexus.app v2.0.0

Versión modular y mantenible que utiliza componentes separados
para mejorar la organización del código.

Reducido de 2196 líneas a <500 líneas mediante extracción de componentes.
"""

import logging
from typing import Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QSplitter, QLabel
)

# Importar componentes modulares
from rexus.modules.logistica.components import (
    LogisticaTableManager,
    LogisticaPanelManager,
    LogisticaTransportManager
)

# Importar componentes Rexus
from rexus.ui.components.base_components import RexusButton, RexusLineEdit
from rexus.ui.standard_components import StandardComponents
from rexus.utils.export_manager import ModuleExportMixin

# Importar constantes
from rexus.modules.logistica.constants import LogisticaConstants

logger = logging.getLogger(__name__)


class LogisticaViewRefactored(QWidget, ModuleExportMixin):
    """Vista principal de logística modularizada."""
    
    # Señales para comunicación con el controlador
    solicitud_actualizar_estadisticas = pyqtSignal()
    solicitud_actualizar_transporte = pyqtSignal(dict)
    solicitud_eliminar_transporte = pyqtSignal(str)

    def __init__(self, parent=None):
        """Inicializa la vista de logística."""
        QWidget.__init__(self, parent)
        ModuleExportMixin.__init__(self)
        
        self.controller = None
        
        # Inicializar gestores de componentes
        self.table_manager = LogisticaTableManager(self)
        self.panel_manager = LogisticaPanelManager(self)
        self.transport_manager = LogisticaTransportManager(self)
        
        # Configurar UI y datos
        self.setup_ui()
        self.setup_connections()
        self.cargar_datos_iniciales()

    def setup_ui(self) -> None:
        """Configura la interfaz principal modular."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._get_tab_style())
        
        # Crear pestañas
        self._crear_pestaña_transportes()
        self._crear_pestaña_entregas()
        self._crear_pestaña_estadisticas()
        self._crear_pestaña_servicios()
        self._crear_pestaña_mapa()
        
        layout.addWidget(self.tab_widget)

    def _crear_pestaña_transportes(self):
        """Crea la pestaña de gestión de transportes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Panel de control superior
        panel_control = self._crear_panel_control_transportes()
        layout.addWidget(panel_control)
        
        # Tabla de transportes
        self.tabla_transportes = QTableWidget()
        self.table_manager.set_tabla_transportes(self.tabla_transportes)
        self.table_manager.configurar_tabla_transportes()
        layout.addWidget(self.tabla_transportes)
        
        self.tab_widget.addTab(tab, "🚚 Transportes")

    def _crear_pestaña_entregas(self):
        """Crea la pestaña de gestión de entregas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Panel de filtros de entregas
        panel_filtros = self.panel_manager.crear_panel_filtros_servicios_optimizado()
        
        # Tabla de entregas
        self.tabla_entregas = QTableWidget()
        self.table_manager.set_tabla_entregas(self.tabla_entregas)
        self.table_manager.cargar_entregas_en_tabla()
        
        # Layout horizontal con filtros y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(panel_filtros)
        splitter.addWidget(self.tabla_entregas)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        self.tab_widget.addTab(tab, "📦 Entregas")

    def _crear_pestaña_estadisticas(self):
        """Crea la pestaña de estadísticas y métricas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Panel de métricas
        panel_metricas = self.panel_manager.crear_panel_metricas_compacto()
        layout.addWidget(panel_metricas)
        
        # Panel de gráficos
        panel_graficos = self.panel_manager.crear_panel_graficos_mejorado()
        layout.addWidget(panel_graficos)
        
        # Panel de resumen
        panel_resumen = self.panel_manager.crear_panel_resumen_optimizado()
        layout.addWidget(panel_resumen)
        
        self.tab_widget.addTab(tab, "📊 Estadísticas")

    def _crear_pestaña_servicios(self):
        """Crea la pestaña de servicios y rutas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Widget de direcciones
        widget_direcciones = self.panel_manager.crear_widget_direcciones_mejorado()
        layout.addWidget(widget_direcciones)
        
        # Placeholder para gestión de servicios
        placeholder = QLabel("🚀 Gestión de Servicios\n\nPróximamente: Generación automática de servicios")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-size: 16px; padding: 50px;")
        layout.addWidget(placeholder)
        
        self.tab_widget.addTab(tab, "🛣️ Servicios")

    def _crear_pestaña_mapa(self):
        """Crea la pestaña del mapa interactivo."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Panel de control del mapa
        panel_control = self.panel_manager.crear_panel_control_mapa_optimizado()
        
        # Área del mapa (placeholder)
        mapa_placeholder = QLabel("🗺️ Mapa Interactivo\n\nIntegración con mapas pendiente")
        mapa_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mapa_placeholder.setStyleSheet("""
            background-color: #f5f5f5;
            border: 2px dashed #ccc;
            color: #666;
            font-size: 16px;
            border-radius: 8px;
        """)
        
        layout.addWidget(panel_control)
        layout.addWidget(mapa_placeholder, 1)
        
        self.tab_widget.addTab(tab, "🗺️ Mapa")

    def _crear_panel_control_transportes(self) -> QWidget:
        """Crea el panel de control para transportes."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Campo de búsqueda
        self.busqueda_edit = RexusLineEdit()
        self.busqueda_edit.setPlaceholderText("🔍 Buscar transportes...")
        layout.addWidget(self.busqueda_edit)
        
        # Botones de acción
        self.btn_nuevo_transporte = RexusButton("➕ Nuevo")
        self.btn_editar_transporte = RexusButton("✏️ Editar")
        self.btn_eliminar_transporte = RexusButton("🗑️ Eliminar")
        self.btn_exportar = RexusButton("📊 Exportar")
        
        # Establecer estilos de botones
        self.btn_nuevo_transporte.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_editar_transporte.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_eliminar_transporte.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_exportar.setStyleSheet("background-color: #FF9800; color: white;")
        
        # Deshabilitar botones de edición inicialmente
        self.btn_editar_transporte.setEnabled(False)
        self.btn_eliminar_transporte.setEnabled(False)
        
        layout.addWidget(self.btn_nuevo_transporte)
        layout.addWidget(self.btn_editar_transporte)
        layout.addWidget(self.btn_eliminar_transporte)
        layout.addWidget(self.btn_exportar)
        
        return panel

    def setup_connections(self):
        """Configura las conexiones de señales y slots."""
        # Conexiones de búsqueda
        if hasattr(self, 'busqueda_edit'):
            self.busqueda_edit.textChanged.connect(self.transport_manager.buscar_transportes)
        
        # Conexiones de botones de transportes
        if hasattr(self, 'btn_nuevo_transporte'):
            self.btn_nuevo_transporte.clicked.connect(
                self.transport_manager.mostrar_dialogo_nuevo_transporte
            )
        
        if hasattr(self, 'btn_editar_transporte'):
            self.btn_editar_transporte.clicked.connect(
                self.transport_manager.editar_transporte_seleccionado
            )
        
        if hasattr(self, 'btn_eliminar_transporte'):
            self.btn_eliminar_transporte.clicked.connect(
                self.transport_manager.eliminar_transporte_seleccionado
            )
        
        if hasattr(self, 'btn_exportar'):
            self.btn_exportar.clicked.connect(
                self.transport_manager.exportar_transportes_excel
            )
        
        # Conexión de selección de tabla
        if hasattr(self, 'tabla_transportes'):
            self.tabla_transportes.itemSelectionChanged.connect(
                self.transport_manager.actualizar_estado_botones
            )

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en las tablas."""
        # Los datos se cargan automáticamente en los managers
        pass

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller
        self.transport_manager.set_controller(controller)

    def exportar_a_excel(self):
        """Exporta datos a Excel (implementación heredada)."""
        try:
            from rexus.utils.export_manager import export_table_to_excel
            
            if hasattr(self, 'tabla_transportes'):
                export_table_to_excel(
                    self.tabla_transportes,
                    "transportes_logistica",
                    "Exportación de Transportes"
                )
            else:
                logger.warning("No hay tabla de transportes para exportar")
                
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")

    def _get_tab_style(self) -> str:
        """Retorna el estilo CSS para las pestañas."""
        return """
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """


# Alias para compatibilidad con el sistema actual
LogisticaView = LogisticaViewRefactored