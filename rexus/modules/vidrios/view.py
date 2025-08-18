"""
MIT License

Copyright (c) 2024 Rexus.app

Vista de Vidrios Modernizada - Interfaz con pestañas y diseño mejorado
Migración desde BaseModuleView a sistema de pestañas
"""

from typing import Dict, List, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QFormLayout, QDoubleSpinBox, QSpinBox, QDialog, QDialogButtonBox,
    QGridLayout, QScrollArea, QSplitter, QHeaderView
)
from PyQt6.QtGui import QColor

from rexus.ui.standard_components import StandardComponents
from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin


class VidriosModernView(QWidget, ModuleExportMixin):
    """Vista modernizada del módulo de vidrios con pestañas."""

    # Señales para comunicación con controlador
    solicitud_actualizar_datos = pyqtSignal()
    solicitud_buscar = pyqtSignal(dict)
    solicitud_agregar = pyqtSignal(dict)
    solicitud_editar = pyqtSignal(int, dict)
    solicitud_eliminar = pyqtSignal(int)
    solicitud_exportar = pyqtSignal(str)  # formato: 'excel' o 'pdf'

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.form_protector = FormProtector()
        self.setup_ui()
        self.cargar_datos_ejemplo()

    def aplicar_estilos_minimalistas(self):
        """Aplica estilos ultra minimalistas y compactos al módulo de vidrios."""
        self.setStyleSheet("""
            /* Estilo general ultra compacto */
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10px;
            }

            /* Pestañas ultra minimalistas */
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 3px;
                background-color: white;
                margin-top: 1px;
            }

            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                padding: 8px 12px;
                margin-right: 1px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                font-size: 12px;
                color: #6b7280;
                min-width: 80px;
                min-height: 24px;
                max-height: 24px;
            }

            QTabBar::tab:selected {
                background-color: white;
                color: #1f2937;
                font-weight: 600;
                border-bottom: 2px solid #3b82f6;
            }

            /* Tablas ultra compactas */
            QTableWidget {
                gridline-color: #e5e7eb;
                selection-background-color: #3b82f6;
                selection-color: white;
                alternate-background-color: transparent;
                font-size: 9px;
                border: 1px solid #e5e7eb;
                border-radius: 2px;
                background: transparent;
            }

            QTableWidget::item {
                padding: 1px 4px;
                border: none;
                font-size: 9px;
            }

            QHeaderView::section {
                background-color: transparent;
                color: #374151;
                font-weight: 500;
                font-size: 8px;
                border: none;
                border-right: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
                padding: 2px 4px;
            }

            /* Botones ultra compactos */
            QPushButton {
                padding: 2px 6px;
                font-size: 9px;
                font-weight: normal;
                min-height: 16px;
                max-height: 20px;
                border-radius: 2px;
            }

            /* GroupBox minimalista */
            QGroupBox {
                font-weight: 500;
                font-size: 9px;
                color: #374151;
                border: 1px solid #e5e7eb;
                border-radius: 3px;
                margin-top: 4px;
                padding-top: 4px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 2px 6px;
                background: #3b82f6;
                color: white;
                border-radius: 2px;
                font-size: 8px;
            }
        """)

    def setup_ui(self):
        """Configura la interfaz principal con pestañas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        # Aplicar estilos minimalistas
        self.aplicar_estilos_minimalistas()

        # Header del módulo
        header = self.crear_header_modulo()
        layout.addWidget(header)

        # Widget de pestañas principal
        self.tab_widget = QTabWidget()
        self.configurar_pestanas()

        # Crear pestañas
        self.crear_pestana_inventario()
        self.crear_pestana_especificaciones()
        self.crear_pestana_pedidos()
        self.crear_pestana_estadisticas()

        layout.addWidget(self.tab_widget)

    def crear_header_modulo(self) -> QFrame:
        """Crea el header principal del módulo."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e40af, stop:1 #3b82f6);
                border: none;
                border-radius: 8px;
                min-height: 50px;
                max-height: 50px;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)

        # Título
        titulo = QLabel("[WINDOW] Gestión de Vidrios")
        titulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)

        # Botones de acción rápida
        btn_actualizar = QPushButton("🔄")
        btn_exportar = QPushButton("[CHART]")

        for btn in [btn_actualizar, btn_exportar]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
            """)

        btn_actualizar.clicked.connect(self.actualizar_datos)
        btn_exportar.clicked.connect(self.exportar_datos)

        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(btn_actualizar)
        layout.addWidget(btn_exportar)

        return header

    def configurar_pestanas(self):
        """Configura el estilo y comportamiento de las pestañas."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)

        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #374151;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                margin-right: 2px;
                font-weight: 500;
                min-width: 80px;
                min-height: 24px;
                max-height: 24px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1e40af;
                border-color: #3b82f6;
                border-bottom: 2px solid white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
                color: #1e40af;
            }
        """)

    def crear_pestana_inventario(self):
        """Crea la pestaña principal de inventario de vidrios."""
        tab_inventario = QWidget()
        layout = QVBoxLayout(tab_inventario)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Panel de control compacto
        control_panel = self.crear_panel_control_inventario()
        layout.addWidget(control_panel)

        # Tabla de vidrios
        self.tabla_vidrios = StandardComponents.create_standard_table()
        self.configurar_tabla_vidrios()
        layout.addWidget(self.tabla_vidrios)

        # Asignar referencia para exportación
        self.tabla_principal = self.tabla_vidrios

        # Controles de paginación
        paginacion_panel = self.crear_controles_paginacion()
        layout.addWidget(paginacion_panel)

        # Panel de acciones
        acciones_panel = self.crear_panel_acciones_inventario()
        layout.addWidget(acciones_panel)

        self.tab_widget.addTab(tab_inventario, "[PACKAGE] Inventario")

    def crear_panel_control_inventario(self) -> QFrame:
        """Crea el panel de control para la pestaña de inventario."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 8, 12, 8)

        # Fila de búsqueda y filtros
        busqueda_layout = QHBoxLayout()
        busqueda_layout.setSpacing(8)

        # Búsqueda
        busqueda_layout.addWidget(QLabel("[SEARCH] Buscar:"))
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por código, tipo, dimensiones...")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        busqueda_layout.addWidget(self.input_busqueda)

        # Filtro por tipo
        busqueda_layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Todos", "Templado", "Laminado", "Común", "Bajo Emisivo", "Espejado"
        ])
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
                min-width: 120px;
            }
        """)
        busqueda_layout.addWidget(self.combo_tipo)

        # Filtro por stock
        busqueda_layout.addWidget(QLabel("Stock:"))
        self.combo_stock = QComboBox()
        self.combo_stock.addItems(["Todos",
"En Stock",
            "Stock Bajo",
            "Sin Stock"])
        self.combo_stock.setStyleSheet(self.combo_tipo.styleSheet())
        busqueda_layout.addWidget(self.combo_stock)

        # Botón buscar
        btn_buscar = StandardComponents.create_primary_button("[SEARCH] Buscar")
        btn_buscar.clicked.connect(self.buscar_vidrios)
        busqueda_layout.addWidget(btn_buscar)

        busqueda_layout.addStretch()

        layout.addLayout(busqueda_layout)

        return panel

    def configurar_tabla_vidrios(self):
        """Configura la tabla principal de vidrios."""
        headers = [
            "ID", "Código", "Tipo", "Espesor", "Ancho", "Alto",
            "M²", "Stock", "Precio/M²", "Estado", "Ubicación"
        ]

        self.tabla_vidrios.setColumnCount(len(headers))
        self.tabla_vidrios.setHorizontalHeaderLabels(headers)

        # Configurar anchos compactos
        anchos = [50, 80, 90, 60, 60, 60, 60, 50, 80, 70, 100]
        for i, ancho in enumerate(anchos):
            self.tabla_vidrios.setColumnWidth(i, ancho)

        # Configuraciones adicionales
        self.tabla_vidrios.setAlternatingRowColors(False)
        self.tabla_vidrios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_vidrios.setSortingEnabled(True)

        # Header compacto
        header = self.tabla_vidrios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(40)
        header.setDefaultSectionSize(60)

    def crear_panel_acciones_inventario(self) -> QFrame:
        """Crea el panel de acciones para inventario."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                max-height: 60px;
            }
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)

        # Botones de acción
        self.btn_nuevo_vidrio = StandardComponents.create_primary_button("➕ Nuevo Vidrio")
        self.btn_editar_vidrio = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_eliminar_vidrio = StandardComponents.create_danger_button("🗑️ Eliminar")
        self.btn_duplicar_vidrio = StandardComponents.create_info_button("[CLIPBOARD] Duplicar")

        # Conectar eventos
        self.btn_nuevo_vidrio.clicked.connect(self.mostrar_dialogo_nuevo_vidrio)
        self.btn_editar_vidrio.clicked.connect(self.editar_vidrio_seleccionado)
        self.btn_eliminar_vidrio.clicked.connect(self.eliminar_vidrio_seleccionado)

        layout.addWidget(self.btn_nuevo_vidrio)
        layout.addWidget(self.btn_editar_vidrio)
        layout.addWidget(self.btn_eliminar_vidrio)
        layout.addWidget(self.btn_duplicar_vidrio)

        # Agregar botón de exportación
        self.add_export_button(layout, "📄 Exportar Vidrios")

        layout.addStretch()

        # Botones de exportación
        btn_export_excel = StandardComponents.create_success_button("[CHART] Excel")
        btn_export_pdf = StandardComponents.create_info_button("📄 PDF")

        btn_export_excel.clicked.connect(lambda: self.exportar_datos('excel'))
        btn_export_pdf.clicked.connect(lambda: self.exportar_datos('pdf'))

        layout.addWidget(btn_export_excel)
        layout.addWidget(btn_export_pdf)

        return panel

    def crear_pestana_especificaciones(self):
        """Crea la pestaña de especificaciones técnicas."""
        tab_specs = QWidget()
        layout = QVBoxLayout(tab_specs)
        layout.setContentsMargins(12, 12, 12, 12)

        # Splitter para dividir la vista
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo - Lista de vidrios
        lista_widget = self.crear_widget_lista_vidrios()
        splitter.addWidget(lista_widget)

        # Panel derecho - Detalles y especificaciones
        detalles_widget = self.crear_widget_detalles_vidrio()
        splitter.addWidget(detalles_widget)

        # Proporción 40-60
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)
        self.tab_widget.addTab(tab_specs, "[CLIPBOARD] Especificaciones")

    def crear_widget_lista_vidrios(self) -> QWidget:
        """Crea el widget de lista de vidrios para especificaciones."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header_label = QLabel("[WINDOW] Catálogo de Vidrios")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1e293b;
                padding: 8px 0px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(header_label)

        # Lista simplificada
        self.lista_specs = StandardComponents.create_standard_table()
        self.configurar_lista_especificaciones()
        layout.addWidget(self.lista_specs)

        return widget

    def configurar_lista_especificaciones(self):
        """Configura la lista para especificaciones."""
        headers = ["Código", "Tipo", "Dimensiones"]
        self.lista_specs.setColumnCount(len(headers))
        self.lista_specs.setHorizontalHeaderLabels(headers)

        # Ocultar números de fila
        self.lista_specs.verticalHeader().setVisible(False)

        # Anchos ajustados
        self.lista_specs.setColumnWidth(0, 100)
        self.lista_specs.setColumnWidth(1, 120)
        self.lista_specs.setColumnWidth(2, 150)

        # Eventos de selección
        self.lista_specs.itemSelectionChanged.connect(self.actualizar_detalles_vidrio)

    def crear_widget_detalles_vidrio(self) -> QWidget:
        """Crea el widget de detalles del vidrio seleccionado."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        self.detalles_header = QLabel("[CLIPBOARD] Seleccionar un vidrio para ver detalles")
        self.detalles_header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #374151;
                padding: 8px 0px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(self.detalles_header)

        # Área de detalles scrolleable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # Contenido de detalles
        self.contenido_detalles = QWidget()
        self.layout_detalles = QVBoxLayout(self.contenido_detalles)

        # Placeholder inicial
        placeholder = QLabel("Seleccione un vidrio de la lista para ver sus especificaciones técnicas completas.")
        placeholder.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-style: italic;
                text-align: center;
                padding: 40px 20px;
            }
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setWordWrap(True)

        self.layout_detalles.addWidget(placeholder)
        self.layout_detalles.addStretch()

        scroll_area.setWidget(self.contenido_detalles)
        layout.addWidget(scroll_area)

        return widget

    def crear_pestana_pedidos(self):
        """Crea la pestaña de gestión de pedidos."""
        tab_pedidos = QWidget()
        layout = QVBoxLayout(tab_pedidos)
        layout.setContentsMargins(12, 12, 12, 12)

        # Panel de control de pedidos
        control_pedidos = self.crear_panel_control_pedidos()
        layout.addWidget(control_pedidos)

        # Tabla de pedidos
        self.tabla_pedidos = StandardComponents.create_standard_table()
        self.configurar_tabla_pedidos()
        layout.addWidget(self.tabla_pedidos)

        # Panel de acciones de pedidos
        acciones_pedidos = self.crear_panel_acciones_pedidos()
        layout.addWidget(acciones_pedidos)

        self.tab_widget.addTab(tab_pedidos, "[CLIPBOARD] Pedidos")

    def crear_panel_control_pedidos(self) -> QFrame:
        """Panel de control para pedidos."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)

        # Filtros de pedidos
        layout.addWidget(QLabel("Estado:"))
        self.combo_estado_pedido = QComboBox()
        self.combo_estado_pedido.addItems([
            "Todos", "Pendiente", "Procesando", "Listo", "Entregado", "Cancelado"
        ])
        layout.addWidget(self.combo_estado_pedido)

        layout.addWidget(QLabel("Prioridad:"))
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItems(["Todas", "Alta", "Media", "Baja"])
        layout.addWidget(self.combo_prioridad)

        btn_filtrar_pedidos = StandardComponents.create_primary_button("[SEARCH] Filtrar")
        layout.addWidget(btn_filtrar_pedidos)

        layout.addStretch()

        return panel

    def configurar_tabla_pedidos(self):
        """Configura la tabla de pedidos."""
        headers = [
            "ID", "Cliente", "Fecha", "Vidrios", "M² Total",
            "Valor", "Estado", "Prioridad", "Entrega"
        ]

        self.tabla_pedidos.setColumnCount(len(headers))
        self.tabla_pedidos.setHorizontalHeaderLabels(headers)

        # Configurar anchos
        anchos = [50, 120, 80, 100, 70, 90, 80, 70, 80]
        for i, ancho in enumerate(anchos):
            self.tabla_pedidos.setColumnWidth(i, ancho)

    def crear_panel_acciones_pedidos(self) -> QFrame:
        """Panel de acciones para pedidos."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                max-height: 60px;
            }
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)

        # Botones de gestión de pedidos
        self.btn_nuevo_pedido = StandardComponents.create_primary_button("➕ Nuevo Pedido")
        self.btn_editar_pedido = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_cancelar_pedido = StandardComponents.create_danger_button("[ERROR] Cancelar")
        self.btn_procesar_pedido = StandardComponents.create_success_button("⚡ Procesar")

        layout.addWidget(self.btn_nuevo_pedido)
        layout.addWidget(self.btn_editar_pedido)
        layout.addWidget(self.btn_cancelar_pedido)
        layout.addWidget(self.btn_procesar_pedido)
        layout.addStretch()

        # Exportación de pedidos
        btn_export_pedidos = StandardComponents.create_info_button("[CHART] Exportar")
        layout.addWidget(btn_export_pedidos)

        return panel

    def crear_pestana_estadisticas(self):
        """Crea la pestaña de estadísticas y reportes."""
        tab_stats = QWidget()
        layout = QVBoxLayout(tab_stats)
        layout.setContentsMargins(12, 12, 12, 12)

        # Grid de widgets de estadísticas
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)

        # Widgets de estadísticas
        widgets_stats = [
            self.crear_widget_resumen_inventario(),
            self.crear_widget_top_vidrios(),
            self.crear_widget_pedidos_mes(),
            self.crear_widget_valoracion_stock()
        ]

        # Distribuir en grid 2x2
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for widget, pos in zip(widgets_stats, positions):
            stats_layout.addWidget(widget, pos[0], pos[1])

        layout.addLayout(stats_layout)
        self.tab_widget.addTab(tab_stats, "[CHART] Estadísticas")

    def crear_widget_resumen_inventario(self) -> QWidget:
        """Widget de resumen del inventario."""
        return self._crear_widget_estadistica(
            "[PACKAGE] Resumen Inventario",
            [
                ("Total Tipos", "47", "#3b82f6"),
                ("En Stock", "42", "#10b981"),
                ("Stock Bajo", "3", "#f59e0b"),
                ("Sin Stock", "2", "#ef4444")
            ]
        )

    def crear_widget_top_vidrios(self) -> QWidget:
        """Widget de vidrios más vendidos."""
        return self._crear_widget_estadistica(
            "[TROPHY] Más Vendidos",
            [
                ("Templado 6mm", "324 m²", "#3b82f6"),
                ("Laminado 8mm", "289 m²", "#10b981"),
                ("DVH 4+4", "176 m²", "#f59e0b"),
                ("Espejado 4mm", "142 m²", "#8b5cf6")
            ]
        )

    def crear_widget_pedidos_mes(self) -> QWidget:
        """Widget de pedidos del mes."""
        return self._crear_widget_estadistica(
            "[CLIPBOARD] Pedidos Mes",
            [
                ("Procesados", "156", "#10b981"),
                ("Pendientes", "23", "#f59e0b"),
                ("Entregados", "142", "#3b82f6"),
                ("Cancelados", "8", "#ef4444")
            ]
        )

    def crear_widget_valoracion_stock(self) -> QWidget:
        """Widget de valoración del stock."""
        return self._crear_widget_estadistica(
            "[MONEY] Valoración Stock",
            [
                ("Total General", "$2.847.500", "#10b981"),
                ("Templados", "$1.234.800", "#3b82f6"),
                ("Laminados", "$892.400", "#8b5cf6"),
                ("Otros", "$720.300", "#6b7280")
            ]
        )

    def _crear_widget_estadistica(self, titulo: str, datos: List[tuple]) -> QWidget:
        """Crea un widget de estadística con título y datos."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #374151;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 4px;
            }
        """)
        layout.addWidget(titulo_label)

        # Datos
        for label, value, color in datos:
            item_layout = QHBoxLayout()

            # Indicador de color
            indicator = QLabel("●")
            indicator.setStyleSheet(f"QLabel {{ color: {color}; font-size: 16px; }}")

            # Etiqueta
            label_widget = QLabel(label)
            label_widget.setStyleSheet("QLabel { color: #6b7280; font-size: 11px; }")

            # Valor
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)

            item_layout.addWidget(indicator)
            item_layout.addWidget(label_widget)
            item_layout.addStretch()
            item_layout.addWidget(value_widget)

            layout.addLayout(item_layout)

        return widget

    # === MÉTODOS DE EVENTOS ===

    def buscar_vidrios(self):
        """Ejecuta búsqueda de vidrios."""
        filtros = {
            'busqueda': self.input_busqueda.text(),
            'tipo': self.combo_tipo.currentText(),
            'stock': self.combo_stock.currentText()
        }
        self.solicitud_buscar.emit(filtros)

    def mostrar_dialogo_nuevo_vidrio(self):
        """Muestra el diálogo para crear nuevo vidrio."""
        dialogo = DialogoVidrioModerno(self, modo='nuevo')
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            self.solicitud_agregar.emit(datos)

    def editar_vidrio_seleccionado(self):
        """Edita el vidrio seleccionado."""
        row = self.tabla_vidrios.currentRow()
        if row >= 0:
            # Obtener ID del vidrio
            id_item = self.tabla_vidrios.item(row, 0)
            if id_item:
                vidrio_id = int(id_item.text())
                # Aquí deberías obtener los datos completos del vidrio
                dialogo = DialogoVidrioModerno(self, modo='editar')
                if dialogo.exec() == QDialog.DialogCode.Accepted:
                    datos = dialogo.obtener_datos()
                    self.solicitud_editar.emit(vidrio_id, datos)

    def eliminar_vidrio_seleccionado(self):
        """Elimina el vidrio seleccionado."""
        row = self.tabla_vidrios.currentRow()
        if row >= 0:
            id_item = self.tabla_vidrios.item(row, 0)
            if id_item:
                vidrio_id = int(id_item.text())
                # Confirmar eliminación
                from PyQt6.QtWidgets import QMessageBox
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    f"¿Está seguro de eliminar el vidrio ID {vidrio_id}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if respuesta == QMessageBox.StandardButton.Yes:
                    self.solicitud_eliminar.emit(vidrio_id)

    def actualizar_detalles_vidrio(self):
        """Actualiza los detalles del vidrio seleccionado."""
        row = self.lista_specs.currentRow()
        if row >= 0:
            # Actualizar header
            codigo_item = self.lista_specs.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                self.detalles_header.setText(f"[CLIPBOARD] Detalles: {codigo}")

                # Aquí deberías cargar los detalles reales del vidrio
                self._mostrar_detalles_ejemplo(codigo)

    def _mostrar_detalles_ejemplo(self, codigo: str):
        """Muestra detalles de ejemplo para el vidrio."""
        # Limpiar layout anterior
        while self.layout_detalles.count():
            child = self.layout_detalles.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Crear nuevos detalles
        detalles = {
            "Código": codigo,
            "Tipo": "Templado",
            "Espesor": "6 mm",
            "Dimensiones": "2.00 x 1.50 m",
            "Área": "3.00 m²",
            "Stock": "25 unidades",
            "Ubicación": "Sector A, Estante 3",
            "Precio": "$45.000 / m²",
            "Proveedor": "Cristales SA",
            "Fecha Ingreso": "2024-08-05",
            "Estado": "Disponible"
        }

        for label, value in detalles.items():
            row_widget = QFrame()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 4, 0, 4)

            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #374151;
                    min-width: 120px;
                }
            """)

            value_widget = QLabel(value)
            value_widget.setStyleSheet("QLabel { color: #6b7280; }")

            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()

            self.layout_detalles.addWidget(row_widget)

        self.layout_detalles.addStretch()

    def actualizar_datos(self):
        """Actualiza todos los datos del módulo."""
        self.solicitud_actualizar_datos.emit()

    def exportar_datos(self, formato='excel'):
        """Exporta datos en el formato especificado."""
        self.solicitud_exportar.emit(formato)

    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para desarrollo."""
        # Datos de ejemplo para la tabla de vidrios
        datos_vidrios = [
            ["1", "VT-001", "Templado", "6mm", "2000", "1500", "3.00", "25", "$45.000", "Disponible", "Sector A"],
            ["2", "VL-002", "Laminado", "8mm", "1800", "1200", "2.16", "15", "$52.000", "Disponible", "Sector B"],
            ["3", "VC-003", "Común", "4mm", "1500", "1000", "1.50", "0", "$28.000", "Sin Stock", "Sector C"],
            ["4", "VE-004", "Espejado", "5mm", "2200", "1600", "3.52", "8", "$38.000", "Stock Bajo", "Sector A"],
        ]

        self.tabla_vidrios.setRowCount(len(datos_vidrios))
        for row, data in enumerate(datos_vidrios):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))

                # Colorear según stock
                if col == 9:  # Columna Estado
                    if value == "Sin Stock":
                        item.setBackground(QColor("#fee2e2"))
                    elif "Stock Bajo" in value:
                        item.setBackground(QColor("#fef3c7"))
                    else:
                        item.setBackground(QColor("#dcfce7"))

                self.tabla_vidrios.setItem(row, col, item)

        # Datos para lista de especificaciones
        self.lista_specs.setRowCount(4)
        for row, data in enumerate(datos_vidrios):
            self.lista_specs.setItem(row, 0, QTableWidgetItem(data[1]))  # Código
            self.lista_specs.setItem(row, 1, QTableWidgetItem(data[2]))  # Tipo
            self.lista_specs.setItem(row, 2, QTableWidgetItem(f"{data[4]}x{data[5]}mm"))  # Dimensiones

    def crear_controles_paginacion(self) -> QFrame:
        """Crea los controles de paginación."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                max-height: 40px;
            }
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        # Información de registros
        self.info_label = QLabel("Mostrando 1-50 de 0 vidrios")
        self.info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Botones de navegación
        self.btn_primera = QPushButton("⟪")
        self.btn_anterior = QPushButton("‹")
        self.btn_siguiente = QPushButton("›")
        self.btn_ultima = QPushButton("⟫")

        for btn in [self.btn_primera, self.btn_anterior, self.btn_siguiente, self.btn_ultima]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #475569;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                    border-color: #3b82f6;
                }
                QPushButton:disabled {
                    background: #f8fafc;
                    color: #cbd5e1;
                    border-color: #e2e8f0;
                }
            """)

        layout.addWidget(self.btn_primera)
        layout.addWidget(self.btn_anterior)
        
        # Campo de página actual
        self.page_input = QLineEdit("1")
        self.page_input.setFixedSize(50, 32)
        self.page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 4px;
                text-align: center;
            }
        """)
        layout.addWidget(self.page_input)
        
        # Label "de X"
        self.total_pages_label = QLabel("de 1")
        self.total_pages_label.setStyleSheet("color: #64748b; margin: 0 8px;")
        layout.addWidget(self.total_pages_label)

        layout.addWidget(self.btn_siguiente)
        layout.addWidget(self.btn_ultima)

        return panel


class DialogoVidrioModerno(QDialog):
    """Diálogo moderno para crear/editar vidrios."""

    def __init__(self, parent=None, modo='nuevo'):
        super().__init__(parent)
        self.modo = modo
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        titulo = "Nuevo Vidrio" if self.modo == 'nuevo' else "Editar Vidrio"
        self.setWindowTitle(titulo)
        self.setFixedSize(400, 500)

        layout = QVBoxLayout(self)

        # Formulario principal
        form_layout = QFormLayout()

        # Campos del formulario
        self.codigo_edit = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Templado",
"Laminado",
            "Común",
            "Bajo Emisivo",
            "Espejado"])

        self.espesor_spin = QDoubleSpinBox()
        self.espesor_spin.setRange(3.0, 25.0)
        self.espesor_spin.setValue(6.0)
        self.espesor_spin.setSuffix(" mm")

        self.ancho_spin = QSpinBox()
        self.ancho_spin.setRange(100, 3000)
        self.ancho_spin.setValue(2000)
        self.ancho_spin.setSuffix(" mm")

        self.alto_spin = QSpinBox()
        self.alto_spin.setRange(100, 3000)
        self.alto_spin.setValue(1500)
        self.alto_spin.setSuffix(" mm")

        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 999)

        self.precio_spin = QDoubleSpinBox()
        self.precio_spin.setRange(0.0, 999999.99)
        self.precio_spin.setPrefix("$ ")

        self.ubicacion_edit = QLineEdit()

        # Agregar campos al formulario
        form_layout.addRow("Código:", self.codigo_edit)
        form_layout.addRow("Tipo:", self.tipo_combo)
        form_layout.addRow("Espesor:", self.espesor_spin)
        form_layout.addRow("Ancho:", self.ancho_spin)
        form_layout.addRow("Alto:", self.alto_spin)
        form_layout.addRow("Stock:", self.stock_spin)
        form_layout.addRow("Precio/M²:", self.precio_spin)
        form_layout.addRow("Ubicación:", self.ubicacion_edit)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def obtener_datos(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        return {
            'codigo': sanitize_string(self.codigo_edit.text()),
            'tipo': self.tipo_combo.currentText(),
            'espesor': self.espesor_spin.value(),
            'ancho': self.ancho_spin.value(),
            'alto': self.alto_spin.value(),
            'stock': self.stock_spin.value(),
            'precio': self.precio_spin.value(),
            'ubicacion': sanitize_string(self.ubicacion_edit.text())
        }

    # Alias para compatibilidad con importaciones existentes
VidriosView = VidriosModernView
