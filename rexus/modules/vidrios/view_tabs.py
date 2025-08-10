"""
Vista de Vidrios con Pestañas - Rexus.app
Permite gestionar vidrios, estadísticas, pedidos y obras asociadas en pestañas.
"""

import logging
from typing import Dict, List, Any

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QWidget, QTextEdit, QDateEdit,
    QDoubleSpinBox, QSpinBox, QTabWidget, QGridLayout, QProgressBar,
    QScrollArea, QSplitter
)

from PyQt6.QtGui import QFont, QPalette, QColor

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox, RexusTable,
    RexusFrame, RexusGroupBox, RexusLayoutHelper
)

from rexus.ui.standard_components import StandardComponents
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector


class VidriosTabsView(QWidget):
    """Vista principal del módulo de vidrios con sistema de pestañas."""

    # Señales para compatibilidad con el sistema principal
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    buscar_requested = pyqtSignal(dict)
    agregar_requested = pyqtSignal(dict)
    editar_requested = pyqtSignal(int, dict)
    eliminar_requested = pyqtSignal(int)
    asignar_obra_requested = pyqtSignal(int, int)
    crear_pedido_requested = pyqtSignal(dict)
    filtrar_requested = pyqtSignal(dict)

    # Señales específicas del módulo
    solicitud_crear_vidrio = pyqtSignal(dict)
    solicitud_actualizar_vidrio = pyqtSignal(dict)
    solicitud_eliminar_vidrio = pyqtSignal(str)
    crear_pedido_solicitado = pyqtSignal(dict)
    asignar_obra_solicitado = pyqtSignal(dict)
    solicitud_actualizar_estadisticas = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()
        self.init_xss_protection()

    def init_ui(self):
        """Inicializa la interfaz de usuario con pestañas."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Crear título principal
        titulo_widget = self.crear_titulo_principal()
        layout.addWidget(titulo_widget)

        # Crear sistema de pestañas
        self.tab_widget = QTabWidget()
        self.configurar_tabs()
        
        # Crear cada pestaña
        self.crear_pestana_vidrios()
        self.crear_pestana_estadisticas()  
        self.crear_pestana_pedidos()
        self.crear_pestana_obras()
        
        layout.addWidget(self.tab_widget)

        # Aplicar estilos
        self.aplicar_estilos()

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()
        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def crear_titulo_principal(self) -> QWidget:
        """Crea el título principal del módulo."""
        titulo_widget = QWidget()
        titulo_widget.setFixedHeight(70)
        titulo_layout = QHBoxLayout(titulo_widget)
        titulo_layout.setContentsMargins(20, 10, 20, 10)

        # Título
        titulo_label = QLabel("🪟 Gestión de Vidrios")
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background: transparent;
            }
        """)
        titulo_layout.addWidget(titulo_label)

        titulo_layout.addStretch()

        # Botón de actualización global
        self.btn_actualizar = RexusButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos_generales)
        titulo_layout.addWidget(self.btn_actualizar)

        return titulo_widget

    def configurar_tabs(self):
        """Configura el widget de pestañas."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)

    def crear_pestana_vidrios(self):
        """Crea la pestaña de vidrios principal."""
        tab_vidrios = QWidget()
        layout = QVBoxLayout(tab_vidrios)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control para la tabla
        control_panel = self.crear_panel_control_vidrios()
        layout.addWidget(control_panel)

        # Tabla principal
        self.tabla_vidrios = StandardComponents.create_standard_table()
        self.configurar_tabla_vidrios()
        layout.addWidget(self.tabla_vidrios)

        # Panel de acciones rápidas
        acciones_panel = self.crear_panel_acciones_vidrios()
        layout.addWidget(acciones_panel)

        self.tab_widget.addTab(tab_vidrios, "🪟 Vidrios")

    def crear_pestana_estadisticas(self):
        """Crea la pestaña de estadísticas."""
        tab_stats = QWidget()
        layout = QVBoxLayout(tab_stats)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area para estadísticas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        # Crear paneles de estadísticas
        resumen_panel = self.crear_panel_resumen_estadisticas()
        stats_layout.addWidget(resumen_panel)

        graficos_panel = self.crear_panel_graficos_vidrios()
        stats_layout.addWidget(graficos_panel)

        metricas_panel = self.crear_panel_metricas_detalladas()
        stats_layout.addWidget(metricas_panel)

        stats_layout.addStretch()
        scroll.setWidget(stats_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab_stats, "📊 Estadísticas")

    def crear_pestana_pedidos(self):
        """Crea la pestaña de pedidos."""
        tab_pedidos = QWidget()
        layout = QVBoxLayout(tab_pedidos)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de filtros para pedidos
        filtros_panel = self.crear_panel_filtros_pedidos()
        layout.addWidget(filtros_panel)

        # Splitter para dividir pedidos
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de pedidos activos
        pedidos_activos_widget = self.crear_widget_pedidos_activos()
        splitter.addWidget(pedidos_activos_widget)

        # Detalles del pedido seleccionado
        detalles_widget = self.crear_widget_detalles_pedido()
        splitter.addWidget(detalles_widget)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        self.tab_widget.addTab(tab_pedidos, "📦 Pedidos")

    def crear_pestana_obras(self):
        """Crea la pestaña de obras asociadas."""
        tab_obras = QWidget()
        layout = QVBoxLayout(tab_obras)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control de obras
        control_obras_panel = self.crear_panel_control_obras()
        layout.addWidget(control_obras_panel)

        # Contenedor principal de obras
        obras_container = QSplitter(Qt.Orientation.Horizontal)

        # Panel lateral con obras disponibles
        obras_widget = self.crear_widget_obras_disponibles()
        obras_container.addWidget(obras_widget)

        # Widget de asignación de vidrios
        asignacion_widget = self.crear_widget_asignacion_vidrios()
        obras_container.addWidget(asignacion_widget)

        obras_container.setSizes([400, 600])
        layout.addWidget(obras_container)

        self.tab_widget.addTab(tab_obras, "🏗️ Obras")

    # Paneles de control
    def crear_panel_control_vidrios(self) -> QWidget:
        """Crea el panel de control para la pestaña de vidrios."""
        panel = RexusGroupBox("Control de Vidrios")
        layout = QHBoxLayout(panel)

        # Búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar vidrios...")
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input_busqueda)

        # Filtro de tipo
        self.combo_tipo = RexusComboBox()
        self.combo_tipo.addItems(["Todos", "Claro", "Esmerilado", "Templado", "Laminado", "Reflectivo"])
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.combo_tipo)

        # Filtro de estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["Todos", "Disponible", "Asignado", "En producción", "Entregado"])
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)

        # Botón de búsqueda
        btn_buscar = RexusButton("🔍 Buscar")
        btn_buscar.clicked.connect(self.buscar_vidrios)
        layout.addWidget(btn_buscar)

        layout.addStretch()

        return panel

    def crear_panel_acciones_vidrios(self) -> QWidget:
        """Crea el panel de acciones para la tabla."""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Botones de acción
        self.btn_nuevo_vidrio = RexusButton("➕ Nuevo Vidrio")
        self.btn_nuevo_vidrio.clicked.connect(self.mostrar_dialogo_nuevo_vidrio)
        layout.addWidget(self.btn_nuevo_vidrio)

        self.btn_editar_vidrio = RexusButton("✏️ Editar")
        self.btn_editar_vidrio.clicked.connect(self.editar_vidrio_seleccionado)
        layout.addWidget(self.btn_editar_vidrio)

        self.btn_eliminar_vidrio = RexusButton("🗑️ Eliminar")
        self.btn_eliminar_vidrio.clicked.connect(self.eliminar_vidrio_seleccionado)
        layout.addWidget(self.btn_eliminar_vidrio)

        layout.addStretch()

        self.btn_exportar = RexusButton("📊 Exportar Excel")
        self.btn_exportar.clicked.connect(self.exportar_a_excel)
        layout.addWidget(self.btn_exportar)

        return panel

    # Configuración de tablas
    def configurar_tabla_vidrios(self):
        """Configura la tabla de vidrios."""
        headers = ["ID", "Tipo", "Dimensiones", "Estado", "Stock", "Precio", "Obras", "Acciones"]
        self.tabla_vidrios.setColumnCount(len(headers))
        self.tabla_vidrios.setHorizontalHeaderLabels(headers)
        
        # Ajustar anchos
        self.tabla_vidrios.setColumnWidth(0, 80)
        self.tabla_vidrios.setColumnWidth(1, 120)
        self.tabla_vidrios.setColumnWidth(2, 150)
        self.tabla_vidrios.setColumnWidth(3, 100)
        self.tabla_vidrios.setColumnWidth(4, 80)
        self.tabla_vidrios.setColumnWidth(5, 100)
        self.tabla_vidrios.setColumnWidth(6, 120)

    # Métodos auxiliares (implementaciones básicas)
    def crear_panel_resumen_estadisticas(self) -> QWidget:
        panel = RexusGroupBox("Resumen de Vidrios")
        layout = QGridLayout(panel)
        
        # Métricas básicas
        metricas = [
            ("Total Vidrios", "245", "#3498db"),
            ("Disponibles", "156", "#27ae60"),
            ("Asignados", "67", "#f39c12"),
            ("En Producción", "22", "#e74c3c")
        ]

        for i, (titulo, valor, color) in enumerate(metricas):
            card = self.crear_tarjeta_metrica(titulo, valor, color)
            layout.addWidget(card, 0, i)

        return panel

    def crear_panel_graficos_vidrios(self) -> QWidget:
        panel = RexusGroupBox("Gráficos de Vidrios")
        layout = QVBoxLayout(panel)
        
        grafico_placeholder = QLabel("📊 Gráficos de estadísticas de vidrios\n(Implementación con matplotlib)")
        grafico_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grafico_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                padding: 40px;
                color: #7f8c8d;
                font-size: 14px;
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(grafico_placeholder)
        
        return panel

    def crear_panel_metricas_detalladas(self) -> QWidget:
        panel = RexusGroupBox("Métricas Detalladas")
        layout = QVBoxLayout(panel)
        
        metricas_placeholder = QLabel("📈 Métricas detalladas de vidrios")
        metricas_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metricas_placeholder)
        
        return panel

    # Métodos de eventos (stubs básicos)
    def buscar_vidrios(self):
        """Busca vidrios según los filtros."""
        pass

    def actualizar_datos_generales(self):
        """Actualiza todos los datos de las pestañas."""
        self.solicitud_actualizar_estadisticas.emit()

    def mostrar_dialogo_nuevo_vidrio(self):
        """Muestra el diálogo para crear nuevo vidrio."""
        pass

    def editar_vidrio_seleccionado(self):
        """Edita el vidrio seleccionado."""
        pass

    def eliminar_vidrio_seleccionado(self):
        """Elimina el vidrio seleccionado."""
        pass

    def exportar_a_excel(self):
        """Exporta datos a Excel."""
        pass

    # Métodos auxiliares para otros widgets (stubs básicos)
    def crear_panel_filtros_pedidos(self) -> QWidget:
        return RexusGroupBox("Filtros de Pedidos")

    def crear_widget_pedidos_activos(self) -> QWidget:
        return RexusGroupBox("Pedidos Activos")

    def crear_widget_detalles_pedido(self) -> QWidget:
        return RexusGroupBox("Detalles del Pedido")

    def crear_panel_control_obras(self) -> QWidget:
        return RexusGroupBox("Control de Obras")

    def crear_widget_obras_disponibles(self) -> QWidget:
        return RexusGroupBox("Obras Disponibles")

    def crear_widget_asignacion_vidrios(self) -> QWidget:
        return RexusGroupBox("Asignación de Vidrios")

    def crear_tarjeta_metrica(self, titulo: str, valor: str, color: str) -> QWidget:
        """Crea una tarjeta de métrica."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout(card)
        
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: bold;")
        layout.addWidget(titulo_label)

        valor_label = QLabel(valor)
        valor_label.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
        layout.addWidget(valor_label)

        return card

    def aplicar_estilos(self):
        """Aplica estilos específicos al widget."""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
