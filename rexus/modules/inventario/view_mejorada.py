"""
MIT License

Copyright (c) 2024 Rexus.app

Vista de Inventario Mejorada - Soluciona limitaciones de paginación y funcionalidades faltantes
"""

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QTextEdit,
    QSplitter,
    QHeaderView,
    QMessageBox,
    QProgressBar,
)

# Importar componentes del framework UI estandarizado
from rexus.ui.standard_components import StandardComponents
from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.xss_protection import FormProtector
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Importar diálogo de obras asociadas
try:
    from .obras_asociadas_dialog import ObrasAsociadasDialog
except ImportError:
    ObrasAsociadasDialog = None


class InventarioView(QWidget):
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

    def __init__(self):
        super().__init__()
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

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario mejorada."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header con información y controles principales
        header_widget = self.crear_header()
        layout.addWidget(header_widget)

        # Panel de filtros avanzados (colapsable)
        self.panel_filtros = self.crear_panel_filtros_avanzados()
        layout.addWidget(self.panel_filtros)

        # Splitter principal para dividir tabla y panel lateral
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Widget principal de la tabla
        tabla_widget = self.crear_widget_tabla_principal()
        splitter.addWidget(tabla_widget)

        # Panel lateral con funcionalidades
        panel_lateral = self.crear_panel_lateral()
        splitter.addWidget(panel_lateral)

        # Configurar proporciones del splitter
        splitter.setSizes([700, 300])  # 70% tabla, 30% panel lateral

        # Panel de información y paginación en la parte inferior
        footer_widget = self.crear_footer()
        layout.addWidget(footer_widget)

        # Aplicar estilos
        self.aplicar_estilos_mejorados()
        
    def crear_header(self):
        """Crea el header con título y controles principales."""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.Box)
        header.setMaximumHeight(80)
        
        layout = QHBoxLayout(header)
        
        # Título del módulo
        titulo = QLabel("📦 GESTIÓN DE INVENTARIO")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(titulo)
        
        layout.addStretch()
        
        # Botones principales de acción
        self.btn_nuevo_producto = QPushButton("➕ Nuevo Producto")
        self.btn_nuevo_producto.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout.addWidget(self.btn_nuevo_producto)
        
        self.btn_importar = QPushButton("📥 Importar")
        self.btn_importar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5dade2; }
        """)
        layout.addWidget(self.btn_importar)
        
        self.btn_exportar = QPushButton("📤 Exportar")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a569bd; }
        """)
        layout.addWidget(self.btn_exportar)
        
        return header
        
    def crear_panel_filtros_avanzados(self):
        """Crea panel de filtros avanzados y búsqueda."""
        panel = QGroupBox("🔍 Búsqueda y Filtros Avanzados")
        panel.setCheckable(True)
        panel.setChecked(True)  # Expandido por defecto
        
        layout = QVBoxLayout(panel)
        
        # Primera fila - Búsqueda principal
        fila1 = QHBoxLayout()
        
        # Campo de búsqueda principal con búsqueda en tiempo real
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar por código, descripción, categoría...")
        self.input_busqueda.textChanged.connect(self.on_texto_busqueda_cambiado)
        self.input_busqueda.setMinimumWidth(300)
        fila1.addWidget(QLabel("Búsqueda:"))
        fila1.addWidget(self.input_busqueda)
        
        # Botón buscar y limpiar
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda)
        fila1.addWidget(self.btn_buscar)
        
        self.btn_limpiar_busqueda = QPushButton("🧹 Limpiar")
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)
        fila1.addWidget(self.btn_limpiar_busqueda)
        
        fila1.addStretch()
        layout.addLayout(fila1)
        
        # Segunda fila - Filtros específicos
        fila2 = QHBoxLayout()
        
        # Filtro por categoría
        fila2.addWidget(QLabel("Categoría:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "Todas", "Herrajes", "Vidrios", "Herramientas", 
            "Materiales", "Eléctricos", "Plomería", "Accesorios"
        ])
        self.combo_categoria.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_categoria)
        
        # Filtro por stock
        fila2.addWidget(QLabel("Stock:"))
        self.combo_stock = QComboBox()
        self.combo_stock.addItems([
            "Todos", "Con stock", "Stock bajo", "Sin stock", "Stock crítico"
        ])
        self.combo_stock.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_stock)
        
        # Filtro por estado
        fila2.addWidget(QLabel("Estado:"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Activo", "Inactivo", "Descontinuado"])
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        fila2.addWidget(self.combo_estado)
        
        fila2.addStretch()
        layout.addLayout(fila2)
        
        # Tercera fila - Configuración de vista
        fila3 = QHBoxLayout()
        
        fila3.addWidget(QLabel("Registros por página:"))
        self.combo_registros = QComboBox()
        self.combo_registros.addItems(["25", "50", "100", "200", "500", "1000"])
        self.combo_registros.setCurrentText("100")
        self.combo_registros.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        fila3.addWidget(self.combo_registros)
        
        # Mostrar/ocultar columnas
        self.check_mostrar_codigo = QCheckBox("Código")
        self.check_mostrar_codigo.setChecked(True)
        self.check_mostrar_descripcion = QCheckBox("Descripción")
        self.check_mostrar_descripcion.setChecked(True)
        self.check_mostrar_stock = QCheckBox("Stock")
        self.check_mostrar_stock.setChecked(True)
        self.check_mostrar_precio = QCheckBox("Precio")
        self.check_mostrar_precio.setChecked(True)
        
        fila3.addWidget(QLabel("Mostrar:"))
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
        
        return panel
        
    def crear_widget_tabla_principal(self):
        """Crea el widget principal con la tabla de inventario."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de herramientas de la tabla
        toolbar = QHBoxLayout()
        
        # Información de registros
        self.lbl_info_registros = QLabel("Cargando...")
        toolbar.addWidget(self.lbl_info_registros)
        
        toolbar.addStretch()
        
        # Botones de acción de tabla
        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_inventario)
        toolbar.addWidget(self.btn_actualizar)
        
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setEnabled(False)
        toolbar.addWidget(self.btn_editar)
        
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setEnabled(False)
        toolbar.addWidget(self.btn_eliminar)
        
        layout.addLayout(toolbar)
        
        # Crear tabla mejorada
        self.tabla_inventario = StandardComponents.create_standard_table()
        self.configurar_tabla_mejorada()
        layout.addWidget(self.tabla_inventario)
        
        return widget
        
    def crear_panel_lateral(self):
        """Crea panel lateral con funcionalidades adicionales."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel de estadísticas rápidas
        stats_group = QGroupBox("[CHART] Estadísticas")
        stats_layout = QVBoxLayout(stats_group)
        
        self.lbl_total_productos = QLabel("Total: 0")
        self.lbl_stock_critico = QLabel("Stock crítico: 0")
        self.lbl_valor_total = QLabel("Valor total: $0")
        
        for lbl in [self.lbl_total_productos, self.lbl_stock_critico, self.lbl_valor_total]:
            lbl.setStyleSheet("padding: 5px; border: 1px solid #ddd; margin: 2px;")
            stats_layout.addWidget(lbl)
            
        layout.addWidget(stats_group)
        
        # Panel de acciones rápidas
        acciones_group = QGroupBox("⚡ Acciones Rápidas")
        acciones_layout = QVBoxLayout(acciones_group)
        
        self.btn_reporte_stock_bajo = QPushButton("📋 Reporte Stock Bajo")
        self.btn_movimiento = QPushButton("📦 Registrar Movimiento")
        self.btn_asociar_obra = QPushButton("🏗️ Asociar a Obra")
        self.btn_generar_qr = QPushButton("📱 Generar QR")
        
        # Establecer nombres de objeto para que el controlador los encuentre
        self.btn_movimiento.setObjectName("btn_movimiento")
        self.btn_limpiar = self.btn_limpiar_busqueda  # Alias para compatibilidad
        
        for btn in [self.btn_reporte_stock_bajo, self.btn_movimiento, 
                   self.btn_asociar_obra, self.btn_generar_qr]:
            btn.setMinimumHeight(35)
            acciones_layout.addWidget(btn)
            
        layout.addWidget(acciones_group)
        
        # Panel de información del producto seleccionado
        info_group = QGroupBox("ℹ️ Producto Seleccionado")
        info_layout = QVBoxLayout(info_group)
        
        self.info_producto = QTextEdit()
        self.info_producto.setMaximumHeight(150)
        self.info_producto.setReadOnly(True)
        self.info_producto.setText("Seleccione un producto para ver detalles")
        info_layout.addWidget(self.info_producto)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return panel
        
    def crear_footer(self):
        """Crea footer con paginación y controles."""
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.Box)
        footer.setMaximumHeight(50)
        
        layout = QHBoxLayout(footer)
        
        # Progreso de carga
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Información de paginación
        self.lbl_paginacion = QLabel("Página 1 de 1")
        layout.addWidget(self.lbl_paginacion)
        
        layout.addStretch()
        
        # Controles de paginación
        self.btn_primera_pagina = QPushButton("⏮️")
        self.btn_pagina_anterior = QPushButton("◀️")
        self.spin_pagina = QSpinBox()
        self.spin_pagina.setMinimum(1)
        self.btn_pagina_siguiente = QPushButton("▶️")
        self.btn_ultima_pagina = QPushButton("⏭️")
        
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
        
        return footer
        
    def configurar_tabla_mejorada(self):
        """Configura la tabla con todas las funcionalidades mejoradas."""
        # Configurar columnas con más información
        columnas = [
            "📋 Código", "📝 Descripción", "📂 Categoría", "📦 Stock", 
            "💰 Precio", "[CHART] Estado", "📍 Ubicación", "📅 Actualización"
        ]
        
        self.tabla_inventario.setColumnCount(len(columnas))
        self.tabla_inventario.setHorizontalHeaderLabels(columnas)
        
        # Configurar header
        header = self.tabla_inventario.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Tamaños de columnas optimizados
        anchos = [80, 200, 100, 70, 80, 80, 100, 120]
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
        
        # Aplicar estilos de alto contraste
        self.aplicar_estilos_tabla()
        
    def aplicar_estilos_tabla(self):
        """Aplica estilos de alto contraste a la tabla."""
        estilo_tabla = """
        QTableWidget {
            gridline-color: #dddddd !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            border-radius: 4px !important;
            font-size: 13px !important;
        }
        QTableWidget::item {
            padding: 8px !important;
            border: 1px solid #dddddd !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            font-size: 13px !important;
        }
        QTableWidget::item:selected {
            background-color: #0078d4 !important;
            color: #ffffff !important;
        }
        QTableWidget::item:hover {
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }
        QHeaderView::section {
            background-color: #f8f9fa !important;
            padding: 8px !important;
            border: 1px solid #cccccc !important;
            font-weight: bold !important;
            color: #000000 !important;
            font-size: 13px !important;
        }
        """
        self.tabla_inventario.setStyleSheet(estilo_tabla)
        
    def aplicar_estilos_mejorados(self):
        """Aplica estilos mejorados y consistentes."""
        estilo = """
        /* ESTILOS MEJORADOS PARA INVENTARIO */
        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 12px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #d5dbdb;
            border-color: #95a5a6;
        }
        
        QPushButton:pressed {
            background-color: #bdc3c7;
        }
        
        QLineEdit, QComboBox {
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border-color: #3498db;
        }
        """
        
        self.setStyleSheet(estilo)
        
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
📋 <b>Código:</b> {producto.get('codigo', 'N/A')}
📝 <b>Descripción:</b> {producto.get('descripcion', 'N/A')}
📂 <b>Categoría:</b> {producto.get('categoria', 'N/A')}
📦 <b>Stock actual:</b> {producto.get('stock_actual', 0)}
💰 <b>Precio:</b> ${producto.get('precio_unitario', 0):,.2f}
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
        # Actualizar labels
        self.lbl_paginacion.setText(f"Página {self.pagina_actual} de {self.total_paginas}")
        
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina + 1
        fin = min(inicio + len(self.productos_actuales) - 1, self.total_registros)
        self.lbl_info_registros.setText(f"Mostrando {inicio}-{fin} de {self.total_registros} registros")
        
        # Actualizar spinner
        self.spin_pagina.blockSignals(True)
        self.spin_pagina.setMaximum(max(1, self.total_paginas))
        self.spin_pagina.setValue(self.pagina_actual)
        self.spin_pagina.blockSignals(False)
        
        # Habilitar/deshabilitar botones
        self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_siguiente.setEnabled(self.pagina_actual < self.total_paginas)
        self.btn_ultima_pagina.setEnabled(self.pagina_actual < self.total_paginas)
        
    # === MÉTODOS DE DATOS ===
    
    def cargar_inventario(self):
        """Carga inventario completo sin filtros."""
        self.filtros_activos = {}
        self.pagina_actual = 1
        self.cargar_datos_con_filtros()
        
    def cargar_datos_con_filtros(self):
        """Carga datos aplicando filtros y paginación actuales."""
        if self.controller and hasattr(self.controller, 'cargar_inventario_paginado'):
            # Emitir señal para que el controlador cargue los datos
            self.solicitar_cargar_pagina.emit(self.pagina_actual, self.registros_por_pagina)
        elif self.controller and hasattr(self.controller, 'cargar_inventario'):
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
                self.tabla_inventario.setItem(fila, 0, QTableWidgetItem(str(producto.get('codigo', ''))))
                
                # Descripción
                self.tabla_inventario.setItem(fila, 1, QTableWidgetItem(str(producto.get('descripcion', ''))))
                
                # Categoría
                self.tabla_inventario.setItem(fila, 2, QTableWidgetItem(str(producto.get('categoria', ''))))
                
                # Stock con colores
                stock = producto.get('stock_actual', 0)
                stock_item = QTableWidgetItem(str(stock))
                if stock == 0:
                    stock_item.setBackground(QColor("#ffebee"))
                    stock_item.setForeground(QColor("#c62828"))
                elif stock <= 10:
                    stock_item.setBackground(QColor("#fff3e0"))
                    stock_item.setForeground(QColor("#ef6c00"))
                else:
                    stock_item.setBackground(QColor("#e8f5e8"))
                    stock_item.setForeground(QColor("#2e7d32"))
                self.tabla_inventario.setItem(fila, 3, stock_item)
                
                # Precio
                precio = producto.get('precio_unitario', 0.0)
                self.tabla_inventario.setItem(fila, 4, QTableWidgetItem(f"${precio:.2f}"))
                
                # Estado
                estado = producto.get('estado', 'Activo')
                estado_item = QTableWidgetItem(estado)
                if estado == 'Activo':
                    estado_item.setForeground(QColor("#2e7d32"))
                else:
                    estado_item.setForeground(QColor("#c62828"))
                self.tabla_inventario.setItem(fila, 5, estado_item)
                
                # Ubicación
                self.tabla_inventario.setItem(fila, 6, QTableWidgetItem(str(producto.get('ubicacion', ''))))
                
                # Fecha actualización
                self.tabla_inventario.setItem(fila, 7, QTableWidgetItem(str(producto.get('fecha_actualizacion', ''))))
            
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
            print(f"Error actualizando estadísticas: {e}")
            
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
            
        # Conectar botones principales
        if hasattr(controller, 'nuevo_producto'):
            self.btn_nuevo_producto.clicked.connect(controller.nuevo_producto)
            
        if hasattr(controller, 'editar_producto'):
            self.btn_editar.clicked.connect(lambda: controller.editar_producto(self.obtener_producto_seleccionado_id()))
            
        if hasattr(controller, 'eliminar_producto'):
            self.btn_eliminar.clicked.connect(lambda: controller.eliminar_producto(self.obtener_producto_seleccionado_id()))
            
        if hasattr(controller, 'exportar_inventario'):
            self.btn_exportar.clicked.connect(controller.exportar_inventario)
            
        if hasattr(controller, 'importar_inventario'):
            self.btn_importar.clicked.connect(controller.importar_inventario)
            
        if hasattr(controller, 'registrar_movimiento'):
            self.btn_movimiento.clicked.connect(controller.registrar_movimiento)
            
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
