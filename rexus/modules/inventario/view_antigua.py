"""
MIT License

Copyright (c) 2024 Rexus.app

Vista de Inventario Mejorada - Soluciona limitaciones de paginación y funcionalidades faltantes
"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QTableWidgetItem,
    QWidget,
    QSplitter,
    QTabWidget,
)

# Importar componentes del framework de estandarización UI
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusGroupBox,
    RexusFrame,
    RexusSpinBox,
    RexusCheckBox,
    RexusTextEdit,
    RexusProgressBar,
    RexusLayoutHelper
)
from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.style_manager import style_manager
from rexus.utils.message_system import show_error, show_warning
from rexus.utils.xss_protection import FormProtector

# Importar diálogo de obras asociadas
try:
    from .obras_asociadas_dialog import ObrasAsociadasDialog
except ImportError:
    ObrasAsociadasDialog = None


class InventarioView(BaseModuleView):
    """Vista mejorada del módulo de inventario con todas las funcionalidades."""

    # Señales para comunicación MVC
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    solicitar_producto_detalles = pyqtSignal(int)
    solicitar_busqueda = pyqtSignal(dict)
    solicitar_crear_producto = pyqtSignal()
    solicitar_editar_producto = pyqtSignal(int)
    solicitar_eliminar_producto = pyqtSignal(int)
    solicitar_cargar_pagina = pyqtSignal(int, int)  # página, registros_por_página
    solicitar_exportar = pyqtSignal()
    solicitar_importar = pyqtSignal()
    presupuesto_cargado = pyqtSignal(dict)  # datos del presupuesto cargado

    def __init__(self, parent=None):
        super().__init__("[PACKAGE] Gestión de Inventario", parent=parent)
        self.controller = None
        self.productos_actuales = []
        self.filtros_activos = {}

        # Configuración de paginación mejorada
        self.pagina_actual = 1
        self.registros_por_pagina = 100  # Incrementado de 50 a 100
        self.total_registros = 0
        self.total_paginas = 1

        # Timer para búsqueda en tiempo real
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.ejecutar_busqueda_retrasada)
        self.search_timer.setSingleShot(True)

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        self.setup_inventario_ui()

        # Aplicar estilo unificado
        if style_manager:
            style_manager.apply_unified_module_style(self)

    def setup_inventario_ui(self):
        """Configura la UI específica del módulo de inventario."""
        # Configurar controles específicos
        self.setup_inventario_controls()

        # Panel de filtros avanzados (colapsable)
        self.panel_filtros = self.crear_panel_filtros_avanzados()
        self.add_to_main_content(self.panel_filtros)

        # Crear pestañas principales: Inventario General y Obras
        self.tab_widget = QTabWidget()
        
        # Pestaña 1: Inventario General (tabla principal)
        self.tab_inventario_general = self.crear_tab_inventario_general()
        self.tab_widget.addTab(self.tab_inventario_general, "Inventario General")
        
        # Pestaña 2: Separación por Obras
        self.tab_obras = self.crear_tab_obras()
        self.tab_widget.addTab(self.tab_obras, "Obras y Asignaciones")
        
        self.add_to_main_content(self.tab_widget)
        
        # Splitter principal para dividir tabla y panel lateral (en pestaña general)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Widget principal de la tabla
        tabla_widget = self.crear_widget_tabla_principal()
        splitter.addWidget(tabla_widget)

        # Panel lateral con funcionalidades
        panel_lateral = self.crear_panel_lateral()
        splitter.addWidget(panel_lateral)

        # Configurar proporciones del splitter
        splitter.setSizes([700, 300])  # 70% tabla, 30% panel lateral

        self.add_to_main_content(splitter)

        # Panel de información y paginación en la parte inferior
        footer_widget = self.crear_footer()
        self.add_to_main_content(footer_widget)

        # Aplicar tema del módulo
        self.apply_theme()

    def setup_inventario_controls(self):
        """Configura los controles específicos del módulo de inventario."""
        # Añadir controles al panel principal
        controls_layout = RexusLayoutHelper.create_horizontal_layout()

        # Botones principales de acción con componentes Rexus
        self.btn_nuevo_producto = RexusButton("➕ Nuevo Producto", "primary")
        controls_layout.addWidget(self.btn_nuevo_producto)

        self.btn_importar = RexusButton("📥 Importar", "secondary")
        controls_layout.addWidget(self.btn_importar)

        self.btn_exportar = RexusButton("📤 Exportar", "secondary")
        controls_layout.addWidget(self.btn_exportar)

        # Añadir controles al área principal
        self.add_to_main_content(controls_layout)

    def crear_panel_filtros_avanzados(self):
        """Crea panel de filtros avanzados y búsqueda."""
        panel = RexusGroupBox("[SEARCH] Búsqueda y Filtros Avanzados")
        panel.setCheckable(True)
        panel.setChecked(True)  # Expandido por defecto

        layout = RexusLayoutHelper.create_vertical_layout()

        # Primera fila - Búsqueda principal
        fila1 = RexusLayoutHelper.create_horizontal_layout()

        # Campo de búsqueda principal con búsqueda en tiempo real
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("[SEARCH] Buscar por código, descripción, categoría...")
        self.input_busqueda.textChanged.connect(self.on_texto_busqueda_cambiado)
        self.input_busqueda.setMinimumWidth(300)
        fila1.addWidget(RexusLabel("Búsqueda:", "body"))
        fila1.addWidget(self.input_busqueda)

        # Botón buscar y limpiar
        self.btn_buscar = RexusButton("[SEARCH] Buscar", "secondary")
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda)
        fila1.addWidget(self.btn_buscar)

        self.btn_limpiar_busqueda = RexusButton("🧹 Limpiar", "secondary")
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)
        fila1.addWidget(self.btn_limpiar_busqueda)

        fila1.addStretch()
        layout.addLayout(fila1)

        # Segunda fila - Filtros específicos
        fila2 = RexusLayoutHelper.create_horizontal_layout()

        # Filtro por categoría
        fila2.addWidget(RexusLabel("Categoría:", "body"))
        self.combo_categoria = RexusComboBox()
        self.combo_categoria.addItems([
            "Todas", "Herrajes", "Vidrios", "Herramientas",
            "Materiales", "Eléctricos", "Plomería", "Accesorios"
        ])
        self.combo_categoria.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_categoria)

        # Filtro por stock
        fila2.addWidget(RexusLabel("Stock:", "body"))
        self.combo_stock = RexusComboBox()
        self.combo_stock.addItems([
            "Todos", "Con stock", "Stock bajo", "Sin stock", "Stock crítico"
        ])
        self.combo_stock.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_stock)

        # Filtro por estado
        fila2.addWidget(RexusLabel("Estado:", "body"))
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["Todos",
"Activo",
            "Inactivo",
            "Descontinuado"])
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_estado)

        fila2.addStretch()
        layout.addLayout(fila2)

        # Tercera fila - Configuración de vista
        fila3 = RexusLayoutHelper.create_horizontal_layout()

        fila3.addWidget(RexusLabel("Registros por página:", "body"))
        self.combo_registros = RexusComboBox()
        self.combo_registros.addItems(["25",
"50",
            "100",
            "200",
            "500",
            "1000"])
        self.combo_registros.setCurrentText("100")
        self.combo_registros.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        fila3.addWidget(self.combo_registros)

        # Mostrar/ocultar columnas
        self.check_mostrar_codigo = RexusCheckBox("Código")
        self.check_mostrar_codigo.setChecked(True)
        self.check_mostrar_descripcion = RexusCheckBox("Descripción")
        self.check_mostrar_descripcion.setChecked(True)
        self.check_mostrar_stock = RexusCheckBox("Stock")
        self.check_mostrar_stock.setChecked(True)
        self.check_mostrar_precio = RexusCheckBox("Precio")
        self.check_mostrar_precio.setChecked(True)

        fila3.addWidget(RexusLabel("Mostrar:", "body"))
        fila3.addWidget(self.check_mostrar_codigo)
        fila3.addWidget(self.check_mostrar_descripcion)
        fila3.addWidget(self.check_mostrar_stock)
        fila3.addWidget(self.check_mostrar_precio)

        # Conectar cambios de visibilidad
        for checkbox in [self.check_mostrar_codigo, self.check_mostrar_descripcion,
                        self.check_mostrar_stock, self.check_mostrar_precio]:
            checkbox.stateChanged.connect(self.actualizar_visibilidad_columnas)

        fila3.addStretch()
        layout.addLayout(fila3)

        panel.setLayout(layout)
        return panel

    def crear_widget_tabla_principal(self):
        """Crea el widget principal con la tabla de inventario."""
        widget = QWidget()
        layout = RexusLayoutHelper.create_vertical_layout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Barra de herramientas de la tabla
        toolbar = RexusLayoutHelper.create_horizontal_layout()

        # Información de registros
        self.lbl_info_registros = RexusLabel("Cargando...", "body")
        toolbar.addWidget(self.lbl_info_registros)

        toolbar.addStretch()

        # Botones de acción de tabla
        self.btn_actualizar = RexusButton("🔄 Actualizar", "secondary")
        self.btn_actualizar.clicked.connect(self.cargar_inventario)
        toolbar.addWidget(self.btn_actualizar)

        self.btn_editar = RexusButton("✏️ Editar", "secondary")
        self.btn_editar.setEnabled(False)
        toolbar.addWidget(self.btn_editar)

        self.btn_eliminar = RexusButton("🗑️ Eliminar", "danger")
        self.btn_eliminar.setEnabled(False)
        toolbar.addWidget(self.btn_eliminar)

        # Agregar separador visual
        toolbar.addStretch()

        # Botón para cargar presupuestos PDF
        self.btn_cargar_presupuesto = RexusButton("📄 Cargar Presupuesto", "info")
        self.btn_cargar_presupuesto.setToolTip("Subir presupuesto PDF y asociarlo a una obra")
        toolbar.addWidget(self.btn_cargar_presupuesto)

        layout.addLayout(toolbar)

        # Crear tabla mejorada
        self.tabla_inventario = RexusTable()
        self.configurar_tabla_mejorada()

        # Usar el método de BaseModuleView para configurar la tabla principal
        self.set_main_table(self.tabla_inventario)

        layout.addWidget(self.tabla_inventario)

        widget.setLayout(layout)
        return widget

    def crear_panel_lateral(self):
        """Crea panel lateral con funcionalidades adicionales."""
        panel = QWidget()
        layout = RexusLayoutHelper.create_vertical_layout()

        # Panel de estadísticas rápidas
        stats_group = RexusGroupBox("[CHART] Estadísticas")
        stats_layout = RexusLayoutHelper.create_vertical_layout()

        self.lbl_total_productos = RexusLabel("Total: 0", "body")
        self.lbl_stock_critico = RexusLabel("Stock crítico: 0", "body")
        self.lbl_valor_total = RexusLabel("Valor total: $0", "body")

        for lbl in [self.lbl_total_productos, self.lbl_stock_critico, self.lbl_valor_total]:
            stats_layout.addWidget(lbl)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Panel de acciones rápidas
        acciones_group = RexusGroupBox("⚡ Acciones Rápidas")
        acciones_layout = RexusLayoutHelper.create_vertical_layout()

        self.btn_reporte_stock_bajo = RexusButton("[CLIPBOARD] Reporte Stock Bajo", "secondary")
        self.btn_movimiento = RexusButton("[PACKAGE] Registrar Movimiento", "secondary")
        self.btn_asociar_obra = RexusButton("[CONSTRUCTION] Asociar a Obra", "secondary")
        self.btn_generar_qr = RexusButton("📱 Generar QR", "secondary")

        # Establecer nombres de objeto para que el controlador los encuentre
        self.btn_movimiento.setObjectName("btn_movimiento")
        self.btn_limpiar = self.btn_limpiar_busqueda  # Alias para compatibilidad

        for btn in [self.btn_reporte_stock_bajo, self.btn_movimiento,
                   self.btn_asociar_obra, self.btn_generar_qr]:
            btn.setMinimumHeight(35)
            acciones_layout.addWidget(btn)

        acciones_group.setLayout(acciones_layout)
        layout.addWidget(acciones_group)

        # Panel de información del producto seleccionado
        info_group = RexusGroupBox("ℹ️ Producto Seleccionado")
        info_layout = RexusLayoutHelper.create_vertical_layout()

        self.info_producto = RexusTextEdit()
        self.info_producto.setMaximumHeight(150)
        self.info_producto.setReadOnly(True)
        self.info_producto.setText("Seleccione un producto para ver detalles")
        info_layout.addWidget(self.info_producto)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def crear_footer(self):
        """Crea footer con paginación y controles."""
        footer = RexusFrame()
        footer.setMaximumHeight(50)

        layout = RexusLayoutHelper.create_horizontal_layout()

        # Progreso de carga
        self.progress_bar = RexusProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Información de paginación
        self.lbl_paginacion = RexusLabel("Página 1 de 1", "body")
        layout.addWidget(self.lbl_paginacion)

        layout.addStretch()

        # Controles de paginación
        self.btn_primera_pagina = RexusButton("⏮️", "secondary")
        self.btn_pagina_anterior = RexusButton("◀️", "secondary")
        self.spin_pagina = RexusSpinBox()
        self.spin_pagina.setMinimum(1)
        self.btn_pagina_siguiente = RexusButton("▶️", "secondary")
        self.btn_ultima_pagina = RexusButton("⏭️", "secondary")

        # Conectar señales de paginación
        self.btn_primera_pagina.clicked.connect(lambda: self.ir_a_pagina(1))
        self.btn_pagina_anterior.clicked.connect(self.pagina_anterior)
        self.spin_pagina.valueChanged.connect(self.ir_a_pagina)
        self.btn_pagina_siguiente.clicked.connect(self.pagina_siguiente)
        self.btn_ultima_pagina.clicked.connect(self.ir_a_ultima_pagina)

        for btn in [self.btn_primera_pagina, self.btn_pagina_anterior,
                   self.btn_pagina_siguiente, self.btn_ultima_pagina]:
            btn.setMaximumWidth(40)
            layout.addWidget(btn)

        layout.addWidget(self.spin_pagina)

        footer.setLayout(layout)
        return footer

    def configurar_tabla_mejorada(self):
        """Configura la tabla con todas las funcionalidades mejoradas."""
        # Configurar columnas con información completa de stock
        columnas = [
            "[CLIPBOARD] Código", "[NOTE] Descripción", "📂 Categoría", 
            "[PACKAGE] Stock Total", "📦 Stock Disponible", "🔒 Stock Separado",
            "[MONEY] Precio", "[CHART] Estado", "📍 Ubicación", "📅 Actualización"
        ]

        self.tabla_inventario.setColumnCount(len(columnas))
        self.tabla_inventario.setHorizontalHeaderLabels(columnas)

        # Configurar header
        header = self.tabla_inventario.horizontalHeader()
        header.setStretchLastSection(True)

        # Tamaños de columnas optimizados para las nuevas columnas
        anchos = [80, 180, 90, 70, 80, 80, 80, 80, 100, 120]
        for i, ancho in enumerate(anchos):
            if i < len(anchos):
                header.resizeSection(i, ancho)

        # Configuraciones de tabla
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_inventario.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_inventario.setSortingEnabled(True)

        # Conectar señales
        self.tabla_inventario.itemSelectionChanged.connect(self.on_producto_seleccionado)
        self.tabla_inventario.itemDoubleClicked.connect(self.on_item_doble_click)

        # Los estilos se aplicarán por el tema unificado

    def aplicar_estilos_tabla(self):
        """Aplica estilos de alto contraste a la tabla."""
        # Los estilos de tabla ahora los maneja el sistema unificado de temas

    def apply_theme(self):
        """Aplica estilos limpios y legibles - SIMPLIFICADO."""
        # NO sobrescribir estilos - usar el sistema unificado
        # Los estilos se manejan automáticamente por StyleManager

        # Configuraciones específicas para el módulo de inventario si es necesario
        self._apply_inventario_specific_styling()

    def _apply_inventario_specific_styling(self):
        """Aplica estilos específicos del módulo de inventario."""
        # Aplicar estilos de alto contraste a la tabla si existe
        if hasattr(self, 'tabla_inventario'):
            self.aplicar_estilos_tabla()

    def crear_controles_paginacion(self):
        """Crea los controles de paginación compatibles con BaseModuleView."""
        paginacion_layout = RexusLayoutHelper.create_horizontal_layout()

        # Etiqueta de información con componente Rexus
        self.info_label = RexusLabel("Mostrando 1-100 de 0 registros", "body")
        paginacion_layout.addWidget(self.info_label)

        paginacion_layout.addStretch()

        # Controles de navegación con componentes Rexus
        self.btn_primera = RexusButton("<<", "secondary")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)

        self.btn_anterior = RexusButton("<", "secondary")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)

        # Control de página actual con componentes Rexus
        self.pagina_actual_spin = RexusSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(RexusLabel("Página:", "body"))
        paginacion_layout.addWidget(self.pagina_actual_spin)

        self.total_paginas_label = RexusLabel("de 1", "body")
        paginacion_layout.addWidget(self.total_paginas_label)

        self.btn_siguiente = RexusButton(">", "secondary")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)

        self.btn_ultima = RexusButton(">>", "secondary")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ir_a_ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)

        # Selector de registros por página con componentes Rexus
        paginacion_layout.addWidget(RexusLabel("Registros por página:", "body"))
        self.registros_por_pagina_combo = RexusComboBox()
        self.registros_por_pagina_combo.addItems(["25",
"50",
            "100",
            "200",
            "500",
            "1000"])
        self.registros_por_pagina_combo.setCurrentText("100")
        self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina_combo)
        paginacion_layout.addWidget(self.registros_por_pagina_combo)

        return paginacion_layout

    def cambiar_registros_por_pagina_combo(self, registros):
        """Cambia la cantidad de registros por página desde el combo de paginación."""
        try:
            nuevo_valor = int(registros)
            if nuevo_valor != self.registros_por_pagina:
                self.registros_por_pagina = nuevo_valor
                self.pagina_actual = 1  # Resetear a primera página
                self.cargar_datos_con_filtros()
        except ValueError:
            pass

    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada desde el spinner."""
        self.ir_a_pagina(pagina)

    def actualizar_controles_paginacion_base(self, pagina_actual, total_paginas, total_registros, registros_mostrados):
        """Actualiza los controles de paginación del BaseModuleView."""
        if hasattr(self, 'info_label'):
            inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} registros")

        if hasattr(self, 'pagina_actual_spin'):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)

        if hasattr(self, 'total_paginas_label'):
            self.total_paginas_label.setText(f"de {total_paginas}")

        # Habilitar/deshabilitar botones
        if hasattr(self, 'btn_primera'):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)

    # === MÉTODOS DE FUNCIONALIDAD ===

    def on_texto_busqueda_cambiado(self):
        """Maneja cambios en el texto de búsqueda (búsqueda en tiempo real)."""
        self.search_timer.stop()
        self.search_timer.start(500)  # Esperar 500ms antes de buscar

    def ejecutar_busqueda_retrasada(self):
        """Ejecuta búsqueda después del delay."""
        self.ejecutar_busqueda()

    def ejecutar_busqueda(self):
        """Ejecuta búsqueda con filtros actuales."""
        self.progress_bar.setVisible(True)

        filtros = {
            'search': self.input_busqueda.text().strip(),
            'categoria': self.combo_categoria.currentText() if self.combo_categoria.currentText() != "Todas" else None,
            'stock_filter': self.combo_stock.currentText() if self.combo_stock.currentText() != "Todos" else None,
            'estado': self.combo_estado.currentText() if self.combo_estado.currentText() != "Todos" else None,
        }

        self.filtros_activos = {k: v for k, v in filtros.items() if v}

        # Resetear a primera página
        self.pagina_actual = 1
        self.cargar_datos_con_filtros()

    def aplicar_filtros(self):
        """Aplica filtros cuando cambian los combos."""
        self.ejecutar_busqueda()

    def limpiar_busqueda(self):
        """Limpia todos los filtros de búsqueda."""
        self.input_busqueda.clear()
        self.combo_categoria.setCurrentText("Todas")
        self.combo_stock.setCurrentText("Todos")
        self.combo_estado.setCurrentText("Todos")

        self.filtros_activos = {}
        self.pagina_actual = 1
        self.cargar_inventario()

    def cambiar_registros_por_pagina(self):
        """Cambia la cantidad de registros por página."""
        nuevo_valor = int(self.combo_registros.currentText())
        if nuevo_valor != self.registros_por_pagina:
            self.registros_por_pagina = nuevo_valor
            self.pagina_actual = 1  # Resetear a primera página
            self.cargar_datos_con_filtros()

    def actualizar_visibilidad_columnas(self):
        """Actualiza la visibilidad de las columnas según checkboxes."""
        columnas_visibilidad = {
            0: self.check_mostrar_codigo.isChecked(),      # Código
            1: self.check_mostrar_descripcion.isChecked(), # Descripción
            3: self.check_mostrar_stock.isChecked(),       # Stock
            4: self.check_mostrar_precio.isChecked(),      # Precio
        }

        for col, visible in columnas_visibilidad.items():
            self.tabla_inventario.setColumnHidden(col, not visible)

    def on_producto_seleccionado(self):
        """Maneja selección de producto."""
        fila = self.tabla_inventario.currentRow()
        hay_seleccion = fila >= 0

        # Habilitar/deshabilitar botones
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)

        if hay_seleccion and fila < len(self.productos_actuales):
            producto = self.productos_actuales[fila]
            self.mostrar_info_producto(producto)
        else:
            self.info_producto.setText("Seleccione un producto para ver detalles")

    def mostrar_info_producto(self, producto):
        """Muestra información detallada del producto seleccionado."""
        info = f"""
[CLIPBOARD] <b>Código:</b> {producto.get('codigo', 'N/A')}
[NOTE] <b>Descripción:</b> {producto.get('descripcion', 'N/A')}
📂 <b>Categoría:</b> {producto.get('categoria', 'N/A')}
[PACKAGE] <b>Stock actual:</b> {producto.get('stock_actual', 0)}
[MONEY] <b>Precio:</b> ${producto.get('precio_unitario', 0):,.2f}
[CHART] <b>Estado:</b> {producto.get('estado', 'N/A')}
📍 <b>Ubicación:</b> {producto.get('ubicacion', 'No especificada')}
📅 <b>Última actualización:</b> {producto.get('fecha_actualizacion', 'N/A')}
        """
        self.info_producto.setHtml(info)

    def on_item_doble_click(self, item):
        """Maneja doble clic para mostrar obras asociadas."""
        try:
            if not item or ObrasAsociadasDialog is None:
                return

            fila = item.row()
            if 0 <= fila < len(self.productos_actuales):
                producto = self.productos_actuales[fila]

                # Crear y mostrar diálogo
                dialog = ObrasAsociadasDialog(producto, self)
                dialog.exec()

        except Exception as e:
            show_error(self, "Error", f"Error al mostrar obras asociadas: {str(e)}")

    # === MÉTODOS DE PAGINACIÓN ===

    def ir_a_pagina(self, pagina):
        """Va a una página específica."""
        if 1 <= pagina <= self.total_paginas:
            self.pagina_actual = pagina
            self.cargar_datos_con_filtros()

    def pagina_anterior(self):
        """Va a la página anterior."""
        if self.pagina_actual > 1:
            self.ir_a_pagina(self.pagina_actual - 1)

    def pagina_siguiente(self):
        """Va a la página siguiente."""
        if self.pagina_actual < self.total_paginas:
            self.ir_a_pagina(self.pagina_actual + 1)

    def ir_a_ultima_pagina(self):
        """Va a la última página."""
        self.ir_a_pagina(self.total_paginas)

    def actualizar_controles_paginacion(self):
        """Actualiza los controles de paginación."""
        # Actualizar labels existentes del footer
        if hasattr(self, 'lbl_paginacion'):
            self.lbl_paginacion.setText(f"Página {self.pagina_actual} de {self.total_paginas}")

        if hasattr(self, 'lbl_info_registros'):
            inicio = (self.pagina_actual - 1) * self.registros_por_pagina + 1
            fin = min(inicio + len(self.productos_actuales) - 1, self.total_registros)
            self.lbl_info_registros.setText(f"Mostrando {inicio}-{fin} de {self.total_registros} registros")

        # Actualizar spinner del footer
        if hasattr(self, 'spin_pagina'):
            self.spin_pagina.blockSignals(True)
            self.spin_pagina.setMaximum(max(1, self.total_paginas))
            self.spin_pagina.setValue(self.pagina_actual)
            self.spin_pagina.blockSignals(False)

        # Habilitar/deshabilitar botones del footer
        if hasattr(self, 'btn_primera_pagina'):
            self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
            self.btn_pagina_anterior.setEnabled(self.pagina_actual > 1)
            self.btn_pagina_siguiente.setEnabled(self.pagina_actual < self.total_paginas)
            self.btn_ultima_pagina.setEnabled(self.pagina_actual < self.total_paginas)

        # También actualizar controles de BaseModuleView si existen
        if hasattr(self, 'actualizar_controles_paginacion_base'):
            self.actualizar_controles_paginacion_base(
                self.pagina_actual,
                self.total_paginas,
                self.total_registros,
                len(self.productos_actuales)
            )

    # === MÉTODOS DE DATOS ===

    def cargar_inventario(self):
        """Carga inventario completo sin filtros."""
        self.filtros_activos = {}
        self.pagina_actual = 1
        self.cargar_datos_con_filtros()

    def cargar_datos_con_filtros(self):
        """Carga datos aplicando filtros y paginación actuales."""
        if self.controller and \
            hasattr(self.controller, 'cargar_inventario_paginado'):
            # Emitir señal para que el controlador cargue los datos
            self.solicitar_cargar_pagina.emit(self.pagina_actual, self.registros_por_pagina)
        elif self.controller and \
            hasattr(self.controller, 'cargar_inventario'):
            # Fallback para controladores que no soportan paginación
            self.controller.cargar_inventario()
        else:
            # Fallback con datos de ejemplo
            self.mostrar_datos_ejemplo()

    def mostrar_datos_ejemplo(self):
        """Muestra datos de ejemplo cuando no hay controlador."""
        productos_ejemplo = []

        # Generar más productos de ejemplo para probar paginación
        for i in range(1, 251):  # 250 productos de ejemplo
            productos_ejemplo.append({
                'id': i,
                'codigo': f'PROD{i:03d}',
                'descripcion': f'Producto de ejemplo {i}',
                'categoria': ['Herrajes', 'Vidrios', 'Herramientas', 'Materiales'][i % 4],
                'stock_actual': (i * 7) % 100,  # Variación en stock
                'precio_unitario': round(25.50 + (i * 0.5), 2),
                'estado': 'Activo' if i % 10 != 0 else 'Inactivo',
                'ubicacion': f'{chr(65 + (i % 5))}-{(i % 20):02d}',
                'fecha_actualizacion': '2025-08-07'
            })

        # Aplicar paginación a los datos de ejemplo
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        productos_pagina = productos_ejemplo[inicio:fin]

        self.actualizar_tabla_inventario(productos_pagina, len(productos_ejemplo))

    def actualizar_tabla_inventario(self, productos, total_registros=None):
        """Actualiza la tabla con los productos recibidos."""
        try:
            self.productos_actuales = productos

            if total_registros is not None:
                self.total_registros = total_registros
                self.total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)

            # Limpiar tabla
            self.tabla_inventario.setRowCount(len(productos))

            # Llenar tabla
            for fila, producto in enumerate(productos):
                # Código
                self.tabla_inventario.setItem(fila,
0,
                    QTableWidgetItem(str(producto.get('codigo',
                    ''))))

                # Descripción
                self.tabla_inventario.setItem(fila,
1,
                    QTableWidgetItem(str(producto.get('descripcion',
                    ''))))

                # Categoría
                self.tabla_inventario.setItem(fila, 2,
                    QTableWidgetItem(str(producto.get('categoria', ''))))

                # Stock Total
                stock_total = producto.get('stock_actual', 0)
                stock_total_item = QTableWidgetItem(str(stock_total))
                if stock_total == 0:
                    stock_total_item.setBackground(QColor("#ffebee"))
                    stock_total_item.setForeground(QColor("#c62828"))
                elif stock_total <= 10:
                    stock_total_item.setBackground(QColor("#fff3e0"))
                    stock_total_item.setForeground(QColor("#ef6c00"))
                else:
                    stock_total_item.setBackground(QColor("#e8f5e8"))
                    stock_total_item.setForeground(QColor("#2e7d32"))
                self.tabla_inventario.setItem(fila, 3, stock_total_item)

                # Stock Disponible (Stock Total - Stock Separado)
                stock_separado = producto.get('stock_separado', 0)
                stock_disponible = stock_total - stock_separado
                disponible_item = QTableWidgetItem(str(max(0, stock_disponible)))
                if stock_disponible <= 0:
                    disponible_item.setBackground(QColor("#ffebee"))
                    disponible_item.setForeground(QColor("#c62828"))
                elif stock_disponible <= 5:
                    disponible_item.setBackground(QColor("#fff3e0"))
                    disponible_item.setForeground(QColor("#ef6c00"))
                else:
                    disponible_item.setBackground(QColor("#e8f5e8"))
                    disponible_item.setForeground(QColor("#2e7d32"))
                self.tabla_inventario.setItem(fila, 4, disponible_item)

                # Stock Separado
                separado_item = QTableWidgetItem(str(stock_separado))
                if stock_separado > 0:
                    separado_item.setBackground(QColor("#e3f2fd"))
                    separado_item.setForeground(QColor("#1565c0"))
                self.tabla_inventario.setItem(fila, 5, separado_item)

                # Precio
                precio = producto.get('precio_unitario', 0.0)
                self.tabla_inventario.setItem(fila, 6, QTableWidgetItem(f"${precio:.2f}"))

                # Estado
                estado = producto.get('estado', 'Activo')
                estado_item = QTableWidgetItem(estado)
                if estado == 'Activo':
                    estado_item.setForeground(QColor("#2e7d32"))
                else:
                    estado_item.setForeground(QColor("#c62828"))
                self.tabla_inventario.setItem(fila, 7, estado_item)

                # Ubicación
                self.tabla_inventario.setItem(fila, 8,
                    QTableWidgetItem(str(producto.get('ubicacion', ''))))

                # Fecha actualización
                self.tabla_inventario.setItem(fila, 9,
                    QTableWidgetItem(str(producto.get('fecha_actualizacion', ''))))

            # Actualizar controles
            self.actualizar_controles_paginacion()
            self.actualizar_estadisticas()
            self.actualizar_visibilidad_columnas()

            self.progress_bar.setVisible(False)

        except Exception as e:
            show_error(self, "Error", f"Error actualizando tabla: {str(e)}")
            self.progress_bar.setVisible(False)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del panel lateral."""
        try:
            total = self.total_registros
            stock_critico = sum(1 for p in self.productos_actuales if p.get('stock_actual', 0) <= 10)
            valor_total = sum(p.get('precio_unitario', 0) * p.get('stock_actual', 0) for p in self.productos_actuales)

            self.lbl_total_productos.setText(f"Total: {total}")
            self.lbl_stock_critico.setText(f"Stock crítico: {stock_critico}")
            self.lbl_valor_total.setText(f"Valor total: ${valor_total:,.2f}")

        except Exception as e:
            logger.info(f"Error actualizando estadísticas: {e}")

    def _on_dangerous_content(self, campo, contenido):
        """Maneja detección de contenido peligroso XSS."""
        show_warning(self, "Contenido Peligroso",
                    f"[WARN] Contenido potencialmente peligroso detectado en {campo}")

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

        # Conectar señales específicas si el controlador las soporta
        if hasattr(controller, 'cargar_inventario_paginado'):
            self.solicitar_cargar_pagina.connect(controller.cargar_inventario_paginado)

        if hasattr(controller, 'buscar_productos'):
            self.solicitar_busqueda.connect(controller.buscar_productos)

        # Conectar botones principales con verificación de existencia
        buttons_to_connect = [
            ('btn_nuevo_producto', 'nuevo_producto', lambda: controller.nuevo_producto()),
            ('btn_editar', 'editar_producto', lambda: controller.editar_producto(self.obtener_producto_seleccionado_id())),
            ('btn_eliminar', 'eliminar_producto', lambda: controller.eliminar_producto(self.obtener_producto_seleccionado_id())),
            ('btn_exportar', 'exportar_inventario', lambda: controller.exportar_inventario()),
            ('btn_importar', 'importar_inventario', lambda: controller.importar_inventario()),
            ('btn_movimiento', 'registrar_movimiento', lambda: controller.registrar_movimiento()),
            ('btn_reporte_stock_bajo', 'generar_reporte_stock_bajo', lambda: controller.generar_reporte_stock_bajo()),
            ('btn_asociar_obra', 'asociar_a_obra', lambda: controller.asociar_a_obra(self.obtener_producto_seleccionado_id())),
            ('btn_generar_qr', 'generar_codigo_qr', lambda: controller.generar_codigo_qr(self.obtener_producto_seleccionado_id()))
        ]

        for button_name, controller_method, callback in buttons_to_connect:
            try:
                # Verificar que el botón existe y el controlador tiene el método
                if hasattr(self, button_name) and \
                    hasattr(controller, controller_method):
                    button = getattr(self, button_name)
                    if button and hasattr(button, 'clicked'):
                        button.clicked.connect(callback)
                        logger.info(f"[INVENTARIO] Conectado {button_name} -> {controller_method}")
                    else:
                        logger.info(f"[INVENTARIO] Botón {button_name} no válido o ya destruido")
                else:
                    logger.info(f"[INVENTARIO] Saltando {button_name} - no disponible")
            except Exception as e:
                logger.info(f"[INVENTARIO] Error conectando {button_name}: {e}")

    def obtener_producto_seleccionado_id(self):
        """Obtiene el ID del producto seleccionado."""
        fila = self.tabla_inventario.currentRow()
        if 0 <= fila < len(self.productos_actuales):
            return self.productos_actuales[fila].get('id')
        return None

    # === MÉTODOS DE COMPATIBILIDAD CON VISTA ANTERIOR ===

    def actualizar_tabla(self, productos):
        """Método de compatibilidad para actualizar_tabla_inventario."""
        self.actualizar_tabla_inventario(productos)

    def mostrar_productos(self, productos):
        """Método de compatibilidad para mostrar productos."""
        self.actualizar_tabla_inventario(productos)

    def cargar_datos(self, datos):
        """Método de compatibilidad para cargar datos."""
        self.actualizar_tabla_inventario(datos)

    def cargar_inventario_inicial(self):
        """Carga inicial del inventario."""
        self.cargar_inventario()

    def show_error(self, mensaje, titulo="Error"):
        """
        Muestra un mensaje de error al usuario.
        
        Args:
            mensaje (str): Mensaje de error a mostrar
            titulo (str): Título del diálogo de error
        """
        try:
            from rexus.utils.message_system import show_error
            show_error(mensaje, titulo)
        except ImportError:
            # Fallback usando QMessageBox
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle(titulo)
            msg.setText(mensaje)
            msg.exec()

    # === MÉTODOS PARA PESTAÑAS DE OBRAS ===

    def crear_tab_inventario_general(self):
        """Crea la pestaña de inventario general con todos los perfiles."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mover el splitter existente a esta pestaña
        # (El código existente del splitter debería ir aquí)
        
        # Por ahora, agregar un placeholder
        from rexus.ui.components.base_components import RexusLabel
        placeholder = RexusLabel()
        layout.addWidget(placeholder)
        
        return widget

    def crear_tab_obras(self):
        """Crea la pestaña de obras con separación de materiales."""
        from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                   QSplitter, QGroupBox, QTabWidget as QTabWidgetObras)
        from PyQt6.QtCore import Qt
        from rexus.ui.components.base_components import (RexusButton, RexusLabel, 
                                                       RexusTable, RexusComboBox)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Panel de control para obras
        panel_control = QGroupBox()
        control_layout = QHBoxLayout(panel_control)
        
        # Botón para cargar obras
        self.btn_cargar_obras = RexusButton("Cargar Obras")
        control_layout.addWidget(self.btn_cargar_obras)
        
        # Combo para seleccionar obra
        control_layout.addWidget(RexusLabel("Obra:"))
        self.combo_obras = RexusComboBox()
        control_layout.addWidget(self.combo_obras)
        
        # Botón para separar material
        self.btn_separar_material = RexusButton("Separar Material Seleccionado")
        control_layout.addWidget(self.btn_separar_material)
        
        control_layout.addStretch()
        layout.addWidget(panel_control)
        
        # Splitter horizontal: Lista de productos | Pestañas de obras
        splitter_obras = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Lista de productos disponibles
        panel_productos = QGroupBox("Productos Disponibles")
        productos_layout = QVBoxLayout(panel_productos)
        
        self.tabla_productos_disponibles = RexusTable()
        self.configurar_tabla_productos_disponibles()
        productos_layout.addWidget(self.tabla_productos_disponibles)
        
        splitter_obras.addWidget(panel_productos)
        
        # Panel derecho: Pestañas de obras
        self.tab_widget_obras = QTabWidgetObras()
        
        # Pestaña de resumen
        tab_resumen = self.crear_tab_resumen_obras()
        self.tab_widget_obras.addTab(tab_resumen, "Resumen")
        
        splitter_obras.addWidget(self.tab_widget_obras)
        
        # Configurar proporciones del splitter
        splitter_obras.setSizes([400, 600])
        layout.addWidget(splitter_obras)
        
        return widget

    def configurar_tabla_productos_disponibles(self):
        """Configura la tabla de productos disponibles para separar."""
        headers = ["ID", "Código", "Nombre", "Stock Disponible", "Stock Asignado", "Ubicación"]
        self.tabla_productos_disponibles.setColumnCount(len(headers))
        self.tabla_productos_disponibles.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos
        from PyQt6.QtWidgets import QHeaderView
        header = self.tabla_productos_disponibles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Selección por filas
        from PyQt6.QtWidgets import QTableWidget
        self.tabla_productos_disponibles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos_disponibles.setAlternatingRowColors(True)

    def crear_tab_resumen_obras(self):
        """Crea la pestaña de resumen de obras."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
        from rexus.ui.components.base_components import RexusLabel
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estadísticas generales
        grupo_stats = QGroupBox()
        stats_layout = QVBoxLayout(grupo_stats)
        
        self.lbl_total_obras = RexusLabel("Obras activas: 0")
        self.lbl_material_asignado = RexusLabel("Material total asignado: 0")
        self.lbl_material_disponible = RexusLabel("Material disponible: 0")
        
        stats_layout.addWidget(self.lbl_total_obras)
        stats_layout.addWidget(self.lbl_material_asignado)
        stats_layout.addWidget(self.lbl_material_disponible)
        
        layout.addWidget(grupo_stats)
        layout.addStretch()
        
        return widget

    def agregar_obra_tab(self, obra_id, obra_nombre):
        """Agrega una nueva pestaña para una obra específica."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout
        from rexus.ui.components.base_components import RexusButton, RexusLabel, RexusTable
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información de la obra
        grupo_info = QGroupBox(f)
        info_layout = QHBoxLayout(grupo_info)
        
        info_layout.addWidget(RexusLabel(f"ID: {obra_id}"))
        info_layout.addStretch()
        
        # Botones de acción
        btn_liberar = RexusButton("Liberar Material")
        btn_exportar = RexusButton("Exportar Lista")
        info_layout.addWidget(btn_liberar)
        info_layout.addWidget(btn_exportar)
        
        layout.addWidget(grupo_info)
        
        # Tabla de materiales asignados
        tabla_materiales = RexusTable()
        self.configurar_tabla_materiales_obra(tabla_materiales)
        layout.addWidget(tabla_materiales)
        
        # Guardar referencia a la tabla en el widget
        widget.tabla_materiales = tabla_materiales
        widget.obra_id = obra_id
        
        self.tab_widget_obras.addTab(widget, f"Obra: {obra_nombre}")
        
        return widget

    def configurar_tabla_materiales_obra(self, tabla):
        """Configura una tabla de materiales asignados a una obra."""
        headers = ["Código", "Nombre", "Cantidad Asignada", "Fecha Asignación", "Estado"]
        tabla.setColumnCount(len(headers))
        tabla.setHorizontalHeaderLabels(headers)
        
        from PyQt6.QtWidgets import QTableWidget
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setAlternatingRowColors(True)

    def cargar_obras_disponibles(self, obras):
        """Carga las obras disponibles en el combo y crea pestañas."""
        # Cargar en combo
        self.combo_obras.clear()
        for obra in obras:
            self.combo_obras.addItem(obra['nombre'], obra['id'])
        
        # Limpiar pestañas existentes (excepto resumen)
        while self.tab_widget_obras.count() > 1:
            self.tab_widget_obras.removeTab(1)
        
        # Crear pestaña para cada obra
        for obra in obras:
            self.agregar_obra_tab(obra['id'], obra['nombre'])

    def cargar_materiales_obra(self, obra_id, materiales):
        """Carga los materiales asignados a una obra específica."""
        from PyQt6.QtWidgets import QTableWidgetItem
        
        # Encontrar la pestaña correspondiente
        for i in range(1, self.tab_widget_obras.count()):
            widget = self.tab_widget_obras.widget(i)
            if hasattr(widget, 'obra_id') and widget.obra_id == obra_id:
                tabla = widget.tabla_materiales
                tabla.setRowCount(len(materiales))
                
                for row, material in enumerate(materiales):
                    tabla.setItem(row, 0, QTableWidgetItem(str(material.get('codigo', ''))))
                    tabla.setItem(row, 1, QTableWidgetItem(str(material.get('nombre', ''))))
                    tabla.setItem(row, 2, QTableWidgetItem(str(material.get('cantidad_asignada', 0))))
                    tabla.setItem(row, 3, QTableWidgetItem(str(material.get('fecha_asignacion', ''))))
                    tabla.setItem(row, 4, QTableWidgetItem(str(material.get('estado', ''))))
                break

    # === MÉTODOS PARA CARGA DE PRESUPUESTOS PDF ===

    def cargar_presupuesto_pdf(self):
        """Abre un diálogo para cargar un presupuesto PDF y asociarlo a una obra."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        try:
            # Abrir diálogo para seleccionar archivo PDF
            archivo_pdf, _ = QFileDialog.getOpenFileName(
                self,
                ,
                "",
                "Archivos PDF (*.pdf);;Todos los archivos (*)"
            )
            
            if archivo_pdf:
                # Abrir diálogo para seleccionar obra
                from .dialogs.seleccionar_obra_dialog import SeleccionarObraDialog
                dialogo_obra = SeleccionarObraDialog(self)
                
                if dialogo_obra.exec() == QFileDialog.DialogCode.Accepted:
                    obra_seleccionada = dialogo_obra.get_obra_seleccionada()
                    
                    if obra_seleccionada:
                        # Emitir señal para que el controlador maneje la carga
                        self.presupuesto_cargado.emit({
                            'archivo_pdf': archivo_pdf,
                            'obra_id': obra_seleccionada['id'],
                            'obra_nombre': obra_seleccionada['nombre']
                        })
                    else:
                        QMessageBox.warning(self, , "Debe seleccionar una obra")
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar presupuesto: {str(e)}")
