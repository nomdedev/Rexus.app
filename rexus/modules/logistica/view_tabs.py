"""
MIT License

Copyright (c) 2024 Rexus.app

Módulo de Logística con Sistema de Pestañas
Vista principal con pestañas para tabla, estadísticas, servicios y mapa
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
from rexus.utils.message_system import show_error, show_warning
from rexus.utils.xss_protection import FormProtector


class LogisticaTabsView(QWidget):
    """Vista principal del módulo de logística con sistema de pestañas."""

    # Señales
    solicitud_crear_transporte = pyqtSignal(dict)
    solicitud_actualizar_transporte = pyqtSignal(dict)
    solicitud_eliminar_transporte = pyqtSignal(str)
    crear_entrega_solicitada = pyqtSignal(dict)
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
        self.crear_pestana_tabla()
        self.crear_pestana_estadisticas()  
        self.crear_pestana_servicios()
        self.crear_pestana_mapa()
        
        layout.addWidget(self.tab_widget)

        # Aplicar estilos
        self.aplicar_estilos()

    def crear_titulo_principal(self) -> QWidget:
        """Crea el título principal del módulo."""
        titulo_widget = QWidget()
        titulo_widget.setFixedHeight(70)
        titulo_layout = QHBoxLayout(titulo_widget)
        titulo_layout.setContentsMargins(20, 10, 20, 10)

        # Título
        titulo_label = QLabel("Gestión de Logística")
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
        self.btn_actualizar = RexusButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos_generales)
        titulo_layout.addWidget(self.btn_actualizar)

        return titulo_widget

    def configurar_tabs(self):
        """Configura el widget de pestañas."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)

    def crear_pestana_tabla(self):
        """Crea la pestaña de tabla principal."""
        tab_tabla = QWidget()
        layout = QVBoxLayout(tab_tabla)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control para la tabla
        control_panel = self.crear_panel_control_tabla()
        layout.addWidget(control_panel)

        # Tabla principal
        self.tabla_transportes = StandardComponents.create_standard_table()
        self.configurar_tabla_transportes()
        layout.addWidget(self.tabla_transportes)

        # Panel de acciones rápidas
        acciones_panel = self.crear_panel_acciones_tabla()
        layout.addWidget(acciones_panel)

        self.tab_widget.addTab(tab_tabla, "Transportes")

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

        graficos_panel = self.crear_panel_graficos()
        stats_layout.addWidget(graficos_panel)

        metricas_panel = self.crear_panel_metricas_detalladas()
        stats_layout.addWidget(metricas_panel)

        stats_layout.addStretch()
        scroll.setWidget(stats_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab_stats, "Estadísticas")

    def crear_pestana_servicios(self):
        """Crea la pestaña de servicios."""
        tab_servicios = QWidget()
        layout = QVBoxLayout(tab_servicios)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de filtros para servicios
        filtros_panel = self.crear_panel_filtros_servicios()
        layout.addWidget(filtros_panel)

        # Splitter para dividir servicios
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de servicios activos
        servicios_activos_widget = self.crear_widget_servicios_activos()
        splitter.addWidget(servicios_activos_widget)

        # Detalles del servicio seleccionado
        detalles_widget = self.crear_widget_detalles_servicio()
        splitter.addWidget(detalles_widget)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        self.tab_widget.addTab(tab_servicios, "Servicios")

    def crear_pestana_mapa(self):
        """Crea la pestaña del mapa con direcciones."""
        tab_mapa = QWidget()
        layout = QVBoxLayout(tab_mapa)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control del mapa
        control_mapa_panel = self.crear_panel_control_mapa()
        layout.addWidget(control_mapa_panel)

        # Contenedor principal del mapa
        mapa_container = QSplitter(Qt.Orientation.Horizontal)

        # Panel lateral con direcciones
        direcciones_widget = self.crear_widget_direcciones()
        mapa_container.addWidget(direcciones_widget)

        # Widget del mapa (placeholder por ahora)
        mapa_widget = self.crear_widget_mapa()
        mapa_container.addWidget(mapa_widget)

        mapa_container.setSizes([300, 700])
        layout.addWidget(mapa_container)

        self.tab_widget.addTab(tab_mapa, "Mapa")

    # Panel de control para tabla
    def crear_panel_control_tabla(self) -> QWidget:
        """Crea el panel de control para la pestaña de tabla."""
        panel = RexusGroupBox("Control de Transportes")
        layout = QHBoxLayout(panel)

        # Búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar transportes...")
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input_busqueda)

        # Filtro de estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["Todos", "Pendiente", "En tránsito", "Entregado", "Cancelado"])
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)

        # Botón de búsqueda
        btn_buscar = RexusButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_transportes)
        layout.addWidget(btn_buscar)

        layout.addStretch()

        return panel

    def crear_panel_acciones_tabla(self) -> QWidget:
        """Crea el panel de acciones para la tabla."""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Botones de acción
        self.btn_nuevo_transporte = RexusButton("Nuevo Transporte")
        self.btn_nuevo_transporte.clicked.connect(self.mostrar_dialogo_nuevo_transporte)
        layout.addWidget(self.btn_nuevo_transporte)

        self.btn_editar_transporte = RexusButton("Editar")
        self.btn_editar_transporte.clicked.connect(self.editar_transporte_seleccionado)
        layout.addWidget(self.btn_editar_transporte)

        self.btn_eliminar_transporte = RexusButton("Eliminar")
        self.btn_eliminar_transporte.clicked.connect(self.eliminar_transporte_seleccionado)
        layout.addWidget(self.btn_eliminar_transporte)

        layout.addStretch()

        self.btn_exportar = RexusButton("Exportar Excel")
        self.btn_exportar.clicked.connect(self.exportar_a_excel)
        layout.addWidget(self.btn_exportar)

        return panel

    # Panel de estadísticas
    def crear_panel_resumen_estadisticas(self) -> QWidget:
        """Crea el panel de resumen de estadísticas."""
        panel = RexusGroupBox("Resumen General")
        layout = QGridLayout(panel)

        # Métricas principales
        metricas = [
            ("Total Transportes", "156", "#3498db"),
            ("En Tránsito", "23", "#f39c12"),
            ("Entregados Hoy", "8", "#27ae60"),
            ("Pendientes", "12", "#e74c3c")
        ]

        for i, (titulo, valor, color) in enumerate(metricas):
            card = self.crear_tarjeta_metrica(titulo, valor, color)
            layout.addWidget(card, 0, i)

        return panel

    def crear_panel_graficos(self) -> QWidget:
        """Crea el panel de gráficos."""
        panel = RexusGroupBox("Gráficos y Tendencias")
        layout = QVBoxLayout(panel)

        # Placeholder para gráficos
        grafico_placeholder = QLabel("Gráficos de estadísticas\n(Implementación futura con matplotlib)")
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
        grafico_placeholder.setMinimumHeight(200)
        layout.addWidget(grafico_placeholder)

        return panel

    def crear_panel_metricas_detalladas(self) -> QWidget:
        """Crea el panel de métricas detalladas."""
        panel = RexusGroupBox("Métricas Detalladas")
        layout = QVBoxLayout(panel)

        # Barras de progreso para diferentes métricas
        metricas_detalle = [
            ("Eficiencia de entregas", 85, "#27ae60"),
            ("Tiempo promedio de entrega", 72, "#3498db"),
            ("Satisfacción del cliente", 92, "#9b59b6"),
            ("Utilización de flota", 68, "#f39c12")
        ]

        for nombre, porcentaje, color in metricas_detalle:
            metrica_widget = self.crear_widget_metrica(nombre, porcentaje, color)
            layout.addWidget(metrica_widget)

        return panel

    # Panel de servicios
    def crear_panel_filtros_servicios(self) -> QWidget:
        """Crea el panel de filtros para servicios."""
        panel = RexusGroupBox("Filtros de Servicios")
        layout = QHBoxLayout(panel)

        # Filtros
        self.combo_tipo_servicio = RexusComboBox()
        self.combo_tipo_servicio.addItems(["Todos", "Express", "Estándar", "Económico"])
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.combo_tipo_servicio)

        self.combo_estado_servicio = RexusComboBox()
        self.combo_estado_servicio.addItems(["Todos", "Activo", "Pausado", "Finalizado"])
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado_servicio)

        btn_filtrar = RexusButton("Aplicar Filtros")
        btn_filtrar.clicked.connect(self.aplicar_filtros_servicios)
        layout.addWidget(btn_filtrar)

        layout.addStretch()

        return panel

    def crear_widget_servicios_activos(self) -> QWidget:
        """Crea el widget de servicios activos."""
        widget = RexusGroupBox("Servicios Activos")
        layout = QVBoxLayout(widget)

        # Tabla de servicios
        self.tabla_servicios = StandardComponents.create_standard_table()
        self.configurar_tabla_servicios()
        layout.addWidget(self.tabla_servicios)

        return widget

    def crear_widget_detalles_servicio(self) -> QWidget:
        """Crea el widget de detalles del servicio."""
        widget = RexusGroupBox("Detalles del Servicio")
        layout = QVBoxLayout(widget)

        # Información del servicio seleccionado
        self.label_servicio_info = QLabel("Seleccione un servicio para ver detalles")
        self.label_servicio_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_servicio_info.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.label_servicio_info)

        return widget

    # Panel de mapa
    def crear_panel_control_mapa(self) -> QWidget:
        """Crea el panel de control del mapa."""
        panel = RexusGroupBox("Control del Mapa")
        layout = QHBoxLayout(panel)

        # Opciones del mapa
        self.combo_vista_mapa = RexusComboBox()
        self.combo_vista_mapa.addItems(["Satélite", "Carretera", "Híbrido"])
        layout.addWidget(QLabel("Vista:"))
        layout.addWidget(self.combo_vista_mapa)

        self.checkbox_mostrar_rutas = RexusButton("Mostrar Rutas")
        self.checkbox_mostrar_rutas.setCheckable(True)
        layout.addWidget(self.checkbox_mostrar_rutas)

        btn_centrar = RexusButton("Centrar Mapa")
        btn_centrar.clicked.connect(self.centrar_mapa)
        layout.addWidget(btn_centrar)

        layout.addStretch()

        return panel

    def crear_widget_direcciones(self) -> QWidget:
        """Crea el widget de direcciones."""
        widget = RexusGroupBox("Direcciones")
        layout = QVBoxLayout(widget)

        # Lista de direcciones
        self.tabla_direcciones = StandardComponents.create_standard_table()
        self.configurar_tabla_direcciones()
        layout.addWidget(self.tabla_direcciones)

        return widget

    def crear_widget_mapa(self) -> QWidget:
        """Crea el widget del mapa (placeholder)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Placeholder del mapa
        mapa_placeholder = QLabel("Mapa Interactivo\n(Implementación futura con API de mapas)")
        mapa_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mapa_placeholder.setStyleSheet("""
            QLabel {
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 50px;
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
                background-color: #ecf0f1;
            }
        """)
        mapa_placeholder.setMinimumHeight(400)
        layout.addWidget(mapa_placeholder)

        return widget

    # Métodos auxiliares
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

    def crear_widget_metrica(self, nombre: str, porcentaje: int, color: str) -> QWidget:
        """Crea un widget de métrica con barra de progreso."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)

        # Etiqueta
        label = QLabel(f"{nombre}: {porcentaje}%")
        label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)

        # Barra de progreso
        progress = QProgressBar()
        progress.setValue(porcentaje)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)

        return widget

    # Configuración de tablas
    def configurar_tabla_transportes(self):
        """Configura la tabla de transportes."""
        headers = ["ID", "Origen", "Destino", "Estado", "Conductor", "Fecha", "Acciones"]
        self.tabla_transportes.setColumnCount(len(headers))
        self.tabla_transportes.setHorizontalHeaderLabels(headers)
        
        # Ajustar anchos
        self.tabla_transportes.setColumnWidth(0, 80)
        self.tabla_transportes.setColumnWidth(1, 150)
        self.tabla_transportes.setColumnWidth(2, 150)
        self.tabla_transportes.setColumnWidth(3, 100)
        self.tabla_transportes.setColumnWidth(4, 120)
        self.tabla_transportes.setColumnWidth(5, 100)

    def configurar_tabla_servicios(self):
        """Configura la tabla de servicios."""
        headers = ["ID", "Tipo", "Estado", "Cliente", "Prioridad"]
        self.tabla_servicios.setColumnCount(len(headers))
        self.tabla_servicios.setHorizontalHeaderLabels(headers)

    def configurar_tabla_direcciones(self):
        """Configura la tabla de direcciones."""
        headers = ["Dirección", "Ciudad", "Estado", "Tipo"]
        self.tabla_direcciones.setColumnCount(len(headers))
        self.tabla_direcciones.setHorizontalHeaderLabels(headers)

    # Métodos de evento
    def buscar_transportes(self):
        """Busca transportes según los filtros."""
        termino = self.input_busqueda.text()
        estado = self.combo_estado.currentText()
        
        if self.controller:
            self.controller.buscar_transportes(termino, estado)

    def actualizar_datos_generales(self):
        """Actualiza todos los datos de las pestañas."""
        self.solicitud_actualizar_estadisticas.emit()
        if self.controller:
            self.controller.cargar_datos_generales()

    def aplicar_filtros_servicios(self):
        """Aplica filtros a los servicios."""
        tipo = self.combo_tipo_servicio.currentText()
        estado = self.combo_estado_servicio.currentText()
        # Lógica de filtrado

    def centrar_mapa(self):
        """Centra el mapa en la ubicación principal."""
        # Lógica para centrar mapa
        pass

    def mostrar_dialogo_nuevo_transporte(self):
        """Muestra el diálogo para crear un nuevo transporte."""
        # Implementar diálogo
        pass

    def editar_transporte_seleccionado(self):
        """Edita el transporte seleccionado."""
        # Implementar edición
        pass

    def eliminar_transporte_seleccionado(self):
        """Elimina el transporte seleccionado."""
        # Implementar eliminación
        pass

    def exportar_a_excel(self):
        """Exporta los datos a Excel."""
        # Implementar exportación
        pass

    # XSS Protection
    def init_xss_protection(self):
        """Inicializa la protección XSS."""
        try:
            self.form_protector = FormProtector()
            
            # Proteger campos de entrada
            if hasattr(self, 'input_busqueda'):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")
                
        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def aplicar_estilos(self):
        """Aplica estilos modernos a la vista."""
        # Estilo para las pestañas
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                top: -1px;
                background-color: white;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #2c3e50;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e6e6e6;
            }
        """)

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller