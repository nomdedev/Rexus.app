# -*- coding: utf-8 -*-
"""
Vista Moderna de Pedidos - Rexus.app v2.0.0

Vista modernizada del módulo de pedidos con interfaz avanzada,
sistema de pestañas, filtros mejorados y dashboard integrado.
Sigue el patrón de diseño de los módulos más exitosos.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QFormLayout, QDoubleSpinBox, QSpinBox, QDialog, QDialogButtonBox,
    QGridLayout, QScrollArea, QSplitter, QHeaderView, QGroupBox,
    QDateEdit, QTextEdit, QCheckBox, QProgressBar
)
from PyQt6.QtGui import QColor, QFont

from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.components.base_components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox,
    RexusTable, RexusGroupBox, RexusFrame, RexusLayoutHelper
)
from rexus.ui.style_manager import style_manager
from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin


class PedidosModernView(BaseModuleView, ModuleExportMixin):
    """Vista modernizada del módulo de pedidos con interfaz avanzada."""

    # Señales para comunicación MVC
    pedido_creado = pyqtSignal(dict)
    pedido_actualizado = pyqtSignal(dict)
    pedido_eliminado = pyqtSignal(int)
    estado_cambiado = pyqtSignal(int, str)
    busqueda_realizada = pyqtSignal(dict)
    filtros_aplicados = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__("[ORDERS] Gestión de Pedidos", parent=parent)
        ModuleExportMixin.__init__(self)
        
        self.controller = None
        self.pedidos_actuales = []
        self.filtros_activos = {}
        
        # Configuración de paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 50
        self.total_registros = 0
        self.total_paginas = 1
        
        # Timer para búsqueda en tiempo real
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.ejecutar_busqueda_retrasada)
        self.search_timer.setSingleShot(True)
        
        # Protección XSS
        self.form_protector = FormProtector(self)
        
        self.setup_pedidos_ui()
        
        # Aplicar estilo unificado
        if style_manager:
            style_manager.apply_unified_module_style(self)

    def setup_pedidos_ui(self):
        """Configura la UI específica del módulo de pedidos."""
        # Configurar controles específicos
        self.setup_pedidos_controls()
        
        # Panel de filtros avanzados
        self.panel_filtros = self.crear_panel_filtros_avanzados()
        self.add_to_main_content(self.panel_filtros)
        
        # Sistema de pestañas principal
        self.tab_widget = QTabWidget()
        
        # Pestaña 1: Lista de Pedidos
        self.tab_lista_pedidos = self.crear_tab_lista_pedidos()
        self.tab_widget.addTab(self.tab_lista_pedidos, "📋 Lista de Pedidos")
        
        # Pestaña 2: Dashboard de Estados
        self.tab_dashboard = self.crear_tab_dashboard()
        self.tab_widget.addTab(self.tab_dashboard, "📊 Dashboard")
        
        # Pestaña 3: Seguimiento
        self.tab_seguimiento = self.crear_tab_seguimiento()
        self.tab_widget.addTab(self.tab_seguimiento, "🚚 Seguimiento")
        
        self.add_to_main_content(self.tab_widget)
        
        # Footer con información y paginación
        footer_widget = self.crear_footer()
        self.add_to_main_content(footer_widget)
        
        # Aplicar tema del módulo
        self.apply_theme()

    def setup_pedidos_controls(self):
        """Configura los controles específicos del módulo de pedidos."""
        controls_layout = RexusLayoutHelper.create_horizontal_layout()
        
        # Botones principales
        self.btn_nuevo_pedido = RexusButton("➕ Nuevo Pedido", "primary")
        self.btn_nuevo_pedido.clicked.connect(self.nuevo_pedido)
        controls_layout.addWidget(self.btn_nuevo_pedido)
        
        self.btn_editar_pedido = RexusButton("✏️ Editar", "secondary")
        self.btn_editar_pedido.clicked.connect(self.editar_pedido)
        controls_layout.addWidget(self.btn_editar_pedido)
        
        self.btn_eliminar_pedido = RexusButton("🗑️ Eliminar", "danger")
        self.btn_eliminar_pedido.clicked.connect(self.eliminar_pedido)
        controls_layout.addWidget(self.btn_eliminar_pedido)
        
        # Botones de estado
        self.btn_cambiar_estado = RexusButton("🔄 Cambiar Estado", "info")
        self.btn_cambiar_estado.clicked.connect(self.cambiar_estado_pedido)
        controls_layout.addWidget(self.btn_cambiar_estado)
        
        # Botones de exportación
        self.btn_exportar = RexusButton("📤 Exportar", "secondary")
        self.btn_exportar.clicked.connect(self.exportar_pedidos)
        controls_layout.addWidget(self.btn_exportar)
        
        self.btn_imprimir = RexusButton("🖨️ Imprimir", "secondary")
        self.btn_imprimir.clicked.connect(self.imprimir_pedido)
        controls_layout.addWidget(self.btn_imprimir)
        
        self.add_to_main_content(controls_layout)

    def crear_panel_filtros_avanzados(self):
        """Crea panel de filtros avanzados."""
        panel = RexusGroupBox("[FILTER] Filtros Avanzados")
        panel.setCheckable(True)
        panel.setChecked(True)
        
        layout = QVBoxLayout(panel)
        
        # Primera fila de filtros
        fila1 = QHBoxLayout()
        
        # Búsqueda general
        fila1.addWidget(RexusLabel("Buscar:"))
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Número, cliente, producto...")
        self.input_busqueda.textChanged.connect(self.iniciar_busqueda_retrasada)
        fila1.addWidget(self.input_busqueda)
        
        # Filtro por estado
        fila1.addWidget(RexusLabel("Estado:"))
        self.filtro_estado = RexusComboBox()
        self.filtro_estado.addItems([
            "Todos", "Borrador", "Pendiente", "Aprobado", 
            "En Preparación", "Listo", "En Tránsito", 
            "Entregado", "Facturado", "Cancelado"
        ])
        self.filtro_estado.currentTextChanged.connect(self.aplicar_filtros)
        fila1.addWidget(self.filtro_estado)
        
        # Filtro por prioridad
        fila1.addWidget(RexusLabel("Prioridad:"))
        self.filtro_prioridad = RexusComboBox()
        self.filtro_prioridad.addItems(["Todas", "Baja", "Media", "Alta", "Urgente"])
        self.filtro_prioridad.currentTextChanged.connect(self.aplicar_filtros)
        fila1.addWidget(self.filtro_prioridad)
        
        layout.addLayout(fila1)
        
        # Segunda fila de filtros
        fila2 = QHBoxLayout()
        
        # Filtro por cliente
        fila2.addWidget(RexusLabel("Cliente:"))
        self.filtro_cliente = RexusComboBox()
        self.filtro_cliente.addItem("Todos los clientes")
        self.filtro_cliente.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.filtro_cliente)
        
        # Rango de fechas
        fila2.addWidget(RexusLabel("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.dateChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.fecha_desde)
        
        fila2.addWidget(RexusLabel("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.dateChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.fecha_hasta)
        
        # Botón limpiar filtros
        self.btn_limpiar_filtros = RexusButton("🧹 Limpiar", "secondary")
        self.btn_limpiar_filtros.clicked.connect(self.limpiar_filtros)
        fila2.addWidget(self.btn_limpiar_filtros)
        
        layout.addLayout(fila2)
        
        return panel

    def crear_tab_lista_pedidos(self):
        """Crea la pestaña de lista de pedidos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tabla principal de pedidos
        self.tabla_pedidos = RexusTable()
        self.tabla_pedidos.setColumnCount(8)
        self.tabla_pedidos.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Estado", "Prioridad", 
            "Total", "Vendedor", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tabla_pedidos.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos.itemSelectionChanged.connect(self.pedido_seleccionado)
        
        splitter.addWidget(self.tabla_pedidos)
        
        # Panel lateral con detalles
        panel_detalles = self.crear_panel_detalles()
        splitter.addWidget(panel_detalles)
        
        # Configurar proporciones
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        return tab

    def crear_panel_detalles(self):
        """Crea el panel lateral de detalles del pedido."""
        panel = RexusGroupBox("📋 Detalles del Pedido")
        layout = QVBoxLayout(panel)
        
        # Información básica
        info_group = QGroupBox("Información General")
        info_layout = QFormLayout(info_group)
        
        self.lbl_pedido_id = QLabel("-")
        self.lbl_cliente_nombre = QLabel("-")
        self.lbl_fecha_pedido = QLabel("-")
        self.lbl_estado_actual = QLabel("-")
        self.lbl_total_pedido = QLabel("-")
        
        info_layout.addRow("ID:", self.lbl_pedido_id)
        info_layout.addRow("Cliente:", self.lbl_cliente_nombre)
        info_layout.addRow("Fecha:", self.lbl_fecha_pedido)
        info_layout.addRow("Estado:", self.lbl_estado_actual)
        info_layout.addRow("Total:", self.lbl_total_pedido)
        
        layout.addWidget(info_group)
        
        # Productos del pedido
        productos_group = QGroupBox("Productos")
        productos_layout = QVBoxLayout(productos_group)
        
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio", "Subtotal"
        ])
        self.tabla_productos.setMaximumHeight(200)
        
        productos_layout.addWidget(self.tabla_productos)
        layout.addWidget(productos_group)
        
        # Acciones rápidas
        acciones_group = QGroupBox("Acciones Rápidas")
        acciones_layout = QVBoxLayout(acciones_group)
        
        self.btn_ver_completo = QPushButton("👁️ Ver Completo")
        self.btn_duplicar = QPushButton("📋 Duplicar")
        self.btn_enviar_email = QPushButton("📧 Enviar Email")
        
        acciones_layout.addWidget(self.btn_ver_completo)
        acciones_layout.addWidget(self.btn_duplicar)
        acciones_layout.addWidget(self.btn_enviar_email)
        
        layout.addWidget(acciones_group)
        layout.addStretch()
        
        return panel

    def crear_tab_dashboard(self):
        """Crea la pestaña de dashboard."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grid de métricas
        metrics_layout = QGridLayout()
        
        # KPIs principales
        self.kpi_total_pedidos = self.crear_kpi_widget("Total Pedidos", "0", "📋")
        self.kpi_pendientes = self.crear_kpi_widget("Pendientes", "0", "⏳")
        self.kpi_entregados = self.crear_kpi_widget("Entregados", "0", "✅")
        self.kpi_facturacion = self.crear_kpi_widget("Facturación", "$0", "💰")
        
        metrics_layout.addWidget(self.kpi_total_pedidos, 0, 0)
        metrics_layout.addWidget(self.kpi_pendientes, 0, 1)
        metrics_layout.addWidget(self.kpi_entregados, 0, 2)
        metrics_layout.addWidget(self.kpi_facturacion, 0, 3)
        
        layout.addLayout(metrics_layout)
        
        # Gráficos (placeholder)
        graficos_frame = QFrame()
        graficos_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        graficos_layout = QHBoxLayout(graficos_frame)
        
        # Gráfico de estados
        estados_widget = QWidget()
        estados_layout = QVBoxLayout(estados_widget)
        estados_layout.addWidget(QLabel("📊 Estados de Pedidos"))
        
        # Lista de estados con contadores
        self.lista_estados = QWidget()
        self.lista_estados_layout = QVBoxLayout(self.lista_estados)
        estados_layout.addWidget(self.lista_estados)
        
        # Gráfico de tendencias
        tendencias_widget = QWidget()
        tendencias_layout = QVBoxLayout(tendencias_widget)
        tendencias_layout.addWidget(QLabel("📈 Tendencias Mensuales"))
        
        # Placeholder para gráfico
        grafico_placeholder = QLabel("Gráfico de tendencias\n(Implementar con Chart.js)")
        grafico_placeholder.setStyleSheet("border: 2px dashed #ccc; padding: 20px; text-align: center;")
        grafico_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tendencias_layout.addWidget(grafico_placeholder)
        
        graficos_layout.addWidget(estados_widget)
        graficos_layout.addWidget(tendencias_widget)
        
        layout.addWidget(graficos_frame)
        
        return tab

    def crear_kpi_widget(self, titulo, valor, icono):
        """Crea un widget de KPI."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        icono_label = QLabel(icono)
        icono_label.setStyleSheet("font-size: 24px;")
        
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("font-weight: bold; color: #666;")
        
        header_layout.addWidget(icono_label)
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        
        # Valor principal
        valor_label = QLabel(valor)
        valor_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; margin: 10px 0;")
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(valor_label)
        
        # Guardar referencia para actualizar
        setattr(widget, 'valor_label', valor_label)
        
        return widget

    def crear_tab_seguimiento(self):
        """Crea la pestaña de seguimiento."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Selector de pedido
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Pedido:"))
        
        self.combo_pedido_seguimiento = QComboBox()
        self.combo_pedido_seguimiento.currentTextChanged.connect(self.cargar_seguimiento)
        selector_layout.addWidget(self.combo_pedido_seguimiento)
        
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Timeline de seguimiento
        timeline_frame = QFrame()
        timeline_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        timeline_layout = QVBoxLayout(timeline_frame)
        
        timeline_layout.addWidget(QLabel("🚚 Timeline de Seguimiento"))
        
        # Área de scroll para el timeline
        scroll_area = QScrollArea()
        self.timeline_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        
        scroll_area.setWidget(self.timeline_widget)
        scroll_area.setWidgetResizable(True)
        
        timeline_layout.addWidget(scroll_area)
        layout.addWidget(timeline_frame)
        
        return tab

    def crear_footer(self):
        """Crea el footer con información y paginación."""
        footer = QFrame()
        footer.setMaximumHeight(60)
        footer.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QHBoxLayout(footer)
        
        # Información de registros
        self.lbl_info_registros = QLabel("0 pedidos")
        layout.addWidget(self.lbl_info_registros)
        
        layout.addStretch()
        
        # Controles de paginación
        self.btn_primera_pagina = QPushButton("⏮️")
        self.btn_pagina_anterior = QPushButton("◀️")
        self.lbl_pagina_actual = QLabel("Página 1 de 1")
        self.btn_pagina_siguiente = QPushButton("▶️")
        self.btn_ultima_pagina = QPushButton("⏭️")
        
        # Conectar eventos de paginación
        self.btn_primera_pagina.clicked.connect(lambda: self.ir_a_pagina(1))
        self.btn_pagina_anterior.clicked.connect(self.pagina_anterior)
        self.btn_pagina_siguiente.clicked.connect(self.pagina_siguiente)
        self.btn_ultima_pagina.clicked.connect(lambda: self.ir_a_pagina(self.total_paginas))
        
        layout.addWidget(self.btn_primera_pagina)
        layout.addWidget(self.btn_pagina_anterior)
        layout.addWidget(self.lbl_pagina_actual)
        layout.addWidget(self.btn_pagina_siguiente)
        layout.addWidget(self.btn_ultima_pagina)
        
        return footer

    # =================================================================
    # MÉTODOS DE FUNCIONALIDAD
    # =================================================================

    def iniciar_busqueda_retrasada(self):
        """Inicia búsqueda con retraso para evitar múltiples consultas."""
        self.search_timer.stop()
        self.search_timer.start(500)  # 500ms delay

    def ejecutar_busqueda_retrasada(self):
        """Ejecuta la búsqueda después del retraso."""
        self.aplicar_filtros()

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        filtros = {
            'busqueda': self.input_busqueda.text(),
            'estado': self.filtro_estado.currentText(),
            'prioridad': self.filtro_prioridad.currentText(),
            'cliente': self.filtro_cliente.currentText(),
            'fecha_desde': self.fecha_desde.date().toString('yyyy-MM-dd'),
            'fecha_hasta': self.fecha_hasta.date().toString('yyyy-MM-dd')
        }
        
        self.filtros_activos = filtros
        self.pagina_actual = 1  # Resetear a primera página
        self.filtros_aplicados.emit(filtros)

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.input_busqueda.clear()
        self.filtro_estado.setCurrentIndex(0)
        self.filtro_prioridad.setCurrentIndex(0)
        self.filtro_cliente.setCurrentIndex(0)
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_hasta.setDate(QDate.currentDate())
        self.aplicar_filtros()

    def nuevo_pedido(self):
        """Abre diálogo para crear nuevo pedido."""
        # TODO: Implementar diálogo moderno de pedidos
        pass

    def editar_pedido(self):
        """Edita el pedido seleccionado."""
        # TODO: Implementar edición de pedidos
        pass

    def eliminar_pedido(self):
        """Elimina el pedido seleccionado."""
        # TODO: Implementar eliminación con confirmación
        pass

    def cambiar_estado_pedido(self):
        """Cambia el estado del pedido seleccionado."""
        # TODO: Implementar cambio de estado
        pass

    def exportar_pedidos(self):
        """Exporta los pedidos filtrados."""
        # TODO: Implementar exportación
        pass

    def imprimir_pedido(self):
        """Imprime el pedido seleccionado."""
        # TODO: Implementar impresión
        pass

    def pedido_seleccionado(self):
        """Se ejecuta cuando se selecciona un pedido en la tabla."""
        # TODO: Cargar detalles en panel lateral
        pass

    def cargar_seguimiento(self):
        """Carga el seguimiento del pedido seleccionado."""
        # TODO: Implementar timeline de seguimiento
        pass

    # =================================================================
    # MÉTODOS DE NAVEGACIÓN
    # =================================================================

    def ir_a_pagina(self, pagina):
        """Va a una página específica."""
        if 1 <= pagina <= self.total_paginas:
            self.pagina_actual = pagina
            self.actualizar_pagina()

    def pagina_anterior(self):
        """Va a la página anterior."""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_pagina()

    def pagina_siguiente(self):
        """Va a la página siguiente."""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.actualizar_pagina()

    def actualizar_pagina(self):
        """Actualiza la información de paginación."""
        self.lbl_pagina_actual.setText(f"Página {self.pagina_actual} de {self.total_paginas}")
        
        # Habilitar/deshabilitar botones
        self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_siguiente.setEnabled(self.pagina_actual < self.total_paginas)
        self.btn_ultima_pagina.setEnabled(self.pagina_actual < self.total_paginas)
        
        # Solicitar datos de la página actual
        if self.controller:
            self.controller.cargar_pagina(self.pagina_actual, self.filtros_activos)

    # =================================================================
    # MÉTODOS PÚBLICOS PARA EL CONTROLADOR
    # =================================================================

    def cargar_pedidos_en_tabla(self, pedidos):
        """Carga los pedidos en la tabla principal."""
        self.pedidos_actuales = pedidos
        self.tabla_pedidos.setRowCount(len(pedidos))
        
        for row, pedido in enumerate(pedidos):
            # TODO: Poblar tabla con datos reales
            self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(str(pedido.get('id', ''))))
            self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(pedido.get('cliente', '')))
            self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(pedido.get('fecha', '')))
            self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(pedido.get('estado', '')))
            self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(pedido.get('prioridad', '')))
            self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(pedido.get('total', '')))
            self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(pedido.get('vendedor', '')))

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas del dashboard."""
        if hasattr(self, 'kpi_total_pedidos'):
            self.kpi_total_pedidos.valor_label.setText(str(stats.get('total', 0)))
            self.kpi_pendientes.valor_label.setText(str(stats.get('pendientes', 0)))
            self.kpi_entregados.valor_label.setText(str(stats.get('entregados', 0)))
            self.kpi_facturacion.valor_label.setText(f"${stats.get('facturacion', 0):,.2f}")

    def actualizar_info_registros(self, total, inicio, fin):
        """Actualiza la información de registros."""
        self.total_registros = total
        self.total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        
        if total > 0:
            self.lbl_info_registros.setText(f"Mostrando {inicio}-{fin} de {total} pedidos")
        else:
            self.lbl_info_registros.setText("No hay pedidos para mostrar")
        
        self.actualizar_pagina()

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        show_error(mensaje, parent=self)

    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito."""
        show_success(mensaje, parent=self)