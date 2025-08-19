"""
Vista de Inventario con separación por obras - Rexus.app v2.0.0

Funcionalidades principales:
- Tabla principal con todos los perfiles
- Pestañas separadas para cada obra
- Botones para separar material por obra
- Vista de material asignado a cada obra
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QGroupBox, QSplitter, QHeaderView, QComboBox, QLineEdit,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QDialogButtonBox
)

from rexus.ui.components.base_components import (
    RexusButton, RexusTable, RexusLineEdit, RexusComboBox, RexusLabel
)

class InventarioObrasView(QWidget):
    """Vista principal del inventario con separación por obras."""
    
    # Señales
    separar_material_requested = pyqtSignal(int, int, int)  # producto_id, obra_id, cantidad
    cargar_obras_requested = pyqtSignal()
    cargar_inventario_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.obras_disponibles = []
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz principal."""
        layout = QVBoxLayout(self)
        
        # Panel superior con controles
        panel_control = self.crear_panel_control()
        layout.addWidget(panel_control)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Inventario general
        panel_inventario = self.crear_panel_inventario()
        splitter.addWidget(panel_inventario)
        
        # Panel derecho: Obras y asignaciones
        self.tab_widget = QTabWidget()
        self.crear_pestañas_obras()
        splitter.addWidget(self.tab_widget)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        self.aplicar_estilos()
    
    def crear_panel_control(self):
        """Crea el panel de control superior."""
        grupo = QGroupBox("Control de Inventario")
        layout = QHBoxLayout(grupo)
        
        # Botón actualizar inventario
        self.btn_actualizar = RexusButton("🔄 Actualizar Inventario")
        self.btn_actualizar.clicked.connect(self.cargar_inventario_requested.emit)
        layout.addWidget(self.btn_actualizar)
        
        # Búsqueda
        layout.addWidget(RexusLabel("Buscar:"))
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Código, nombre o descripción...")
        layout.addWidget(self.input_busqueda)
        
        # Filtro por categoría
        layout.addWidget(RexusLabel("Categoría:"))
        self.combo_categoria = RexusComboBox()
        layout.addWidget(self.combo_categoria)
        
        # Botón cargar obras
        self.btn_cargar_obras = RexusButton("🏗️ Cargar Obras")
        self.btn_cargar_obras.clicked.connect(self.cargar_obras_requested.emit)
        layout.addWidget(self.btn_cargar_obras)
        
        layout.addStretch()
        return grupo
    
    def crear_panel_inventario(self):
        """Crea el panel de inventario general."""
        grupo = QGroupBox("Inventario General - Todos los Perfiles")
        layout = QVBoxLayout(grupo)
        
        # Tabla principal de inventario
        self.tabla_inventario = RexusTable()
        self.configurar_tabla_inventario()
        layout.addWidget(self.tabla_inventario)
        
        # Panel de botones
        panel_botones = QHBoxLayout()
        
        self.btn_separar = RexusButton("📦 Separar Material para Obra")
        self.btn_separar.clicked.connect(self.abrir_dialogo_separacion)
        panel_botones.addWidget(self.btn_separar)
        
        self.btn_ver_detalle = RexusButton("👁️ Ver Detalle")
        panel_botones.addWidget(self.btn_ver_detalle)
        
        panel_botones.addStretch()
        layout.addLayout(panel_botones)
        
        return grupo
    
    def configurar_tabla_inventario(self):
        """Configura la tabla principal de inventario."""
        headers = [
            "ID", "Código", "Nombre", "Descripción", 
            "Stock Total", "Stock Disponible", "Stock Asignado",
            "Unidad", "Precio", "Ubicación"
        ]
        
        self.tabla_inventario.setColumnCount(len(headers))
        self.tabla_inventario.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos
        header = self.tabla_inventario.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Descripción
        
        # Selección por filas
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setAlternatingRowColors(True)
    
    def crear_pestañas_obras(self):
        """Crea las pestañas para cada obra."""
        # Pestaña de resumen
        self.crear_pestaña_resumen()
        
        # Las pestañas de obras específicas se crearán dinámicamente
        
    def crear_pestaña_resumen(self):
        """Crea la pestaña de resumen general."""
        widget_resumen = QWidget()
        layout = QVBoxLayout(widget_resumen)
        
        # Estadísticas generales
        grupo_stats = QGroupBox("Resumen General")
        layout_stats = QVBoxLayout(grupo_stats)
        
        self.lbl_total_productos = RexusLabel("Total de productos: 0")
        self.lbl_stock_total = RexusLabel("Stock total: 0")
        self.lbl_stock_disponible = RexusLabel("Stock disponible: 0")
        self.lbl_stock_asignado = RexusLabel("Stock asignado: 0")
        self.lbl_obras_activas = RexusLabel("Obras activas: 0")
        
        layout_stats.addWidget(self.lbl_total_productos)
        layout_stats.addWidget(self.lbl_stock_total)
        layout_stats.addWidget(self.lbl_stock_disponible)
        layout_stats.addWidget(self.lbl_stock_asignado)
        layout_stats.addWidget(self.lbl_obras_activas)
        
        layout.addWidget(grupo_stats)
        layout.addStretch()
        
        self.tab_widget.addTab(widget_resumen, "📊 Resumen")
    
    def agregar_pestaña_obra(self, obra_id, obra_nombre):
        """Agrega una nueva pestaña para una obra específica."""
        widget_obra = QWidget()
        layout = QVBoxLayout(widget_obra)
        
        # Información de la obra
        grupo_info = QGroupBox(f"Obra: {obra_nombre}")
        layout_info = QHBoxLayout(grupo_info)
        
        lbl_info = RexusLabel(f"ID: {obra_id}")
        layout_info.addWidget(lbl_info)
        layout_info.addStretch()
        
        layout.addWidget(grupo_info)
        
        # Tabla de materiales asignados a esta obra
        tabla_obra = RexusTable()
        self.configurar_tabla_obra(tabla_obra)
        layout.addWidget(tabla_obra)
        
        # Botones específicos de la obra
        panel_botones = QHBoxLayout()
        
        btn_liberar = RexusButton("🔄 Liberar Material")
        btn_exportar = RexusButton("📋 Exportar Lista")
        
        panel_botones.addWidget(btn_liberar)
        panel_botones.addWidget(btn_exportar)
        panel_botones.addStretch()
        
        layout.addLayout(panel_botones)
        
        # Guardar referencia a la tabla
        widget_obra.tabla_materiales = tabla_obra
        
        self.tab_widget.addTab(widget_obra, f"🏗️ {obra_nombre}")
        
        return widget_obra
    
    def configurar_tabla_obra(self, tabla):
        """Configura una tabla de materiales de obra."""
        headers = [
            "Código", "Nombre", "Cantidad Asignada", 
            "Fecha Asignación", "Estado", "Observaciones"
        ]
        
        tabla.setColumnCount(len(headers))
        tabla.setHorizontalHeaderLabels(headers)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setAlternatingRowColors(True)
    
    def abrir_dialogo_separacion(self):
        """Abre el diálogo para separar material para una obra."""
        fila_actual = self.tabla_inventario.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección requerida", 
                              "Seleccione un producto del inventario")
            return
        
        # Obtener datos del producto seleccionado
        producto_id = int(self.tabla_inventario.item(fila_actual, 0).text())
        nombre_producto = self.tabla_inventario.item(fila_actual, 2).text()
        stock_disponible = int(self.tabla_inventario.item(fila_actual, 5).text())
        
        dialogo = DialogoSeparacionMaterial(self, producto_id, nombre_producto, stock_disponible)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            obra_id, cantidad = dialogo.obtener_datos()
            self.separar_material_requested.emit(producto_id, obra_id, cantidad)
    
    def cargar_datos_inventario(self, productos):
        """Carga los datos en la tabla principal de inventario."""
        self.tabla_inventario.setRowCount(len(productos))
        
        for row, producto in enumerate(productos):
            self.tabla_inventario.setItem(row, 0, QTableWidgetItem(str(producto.get('id', ''))))
            self.tabla_inventario.setItem(row, 1, QTableWidgetItem(str(producto.get('codigo', ''))))
            self.tabla_inventario.setItem(row, 2, QTableWidgetItem(str(producto.get('nombre', ''))))
            self.tabla_inventario.setItem(row, 3, QTableWidgetItem(str(producto.get('descripcion', ''))))
            self.tabla_inventario.setItem(row, 4, QTableWidgetItem(str(producto.get('stock_total', 0))))
            self.tabla_inventario.setItem(row, 5, QTableWidgetItem(str(producto.get('stock_disponible', 0))))
            self.tabla_inventario.setItem(row, 6, QTableWidgetItem(str(producto.get('stock_asignado', 0))))
            self.tabla_inventario.setItem(row, 7, QTableWidgetItem(str(producto.get('unidad', ''))))
            self.tabla_inventario.setItem(row, 8, QTableWidgetItem(f"${producto.get('precio', 0):.2f}"))
            self.tabla_inventario.setItem(row, 9, QTableWidgetItem(str(producto.get('ubicacion', ''))))
    
    def cargar_obras_disponibles(self, obras):
        """Carga las obras disponibles y crea sus pestañas."""
        self.obras_disponibles = obras
        
        # Limpiar pestañas existentes (excepto resumen)
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)
        
        # Crear pestaña para cada obra
        for obra in obras:
            self.agregar_pestaña_obra(obra['id'], obra['nombre'])
    
    def cargar_materiales_obra(self, obra_id, materiales):
        """Carga los materiales asignados a una obra específica."""
        # Encontrar la pestaña correspondiente
        for i in range(1, self.tab_widget.count()):  # Empezar en 1 para saltar resumen
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'tabla_materiales'):
                # Aquí deberías verificar que corresponde a la obra correcta
                tabla = widget.tabla_materiales
                tabla.setRowCount(len(materiales))
                
                for row, material in enumerate(materiales):
                    tabla.setItem(row, 0, QTableWidgetItem(str(material.get('codigo', ''))))
                    tabla.setItem(row, 1, QTableWidgetItem(str(material.get('nombre', ''))))
                    tabla.setItem(row, 2, QTableWidgetItem(str(material.get('cantidad_asignada', 0))))
                    tabla.setItem(row, 3, QTableWidgetItem(str(material.get('fecha_asignacion', ''))))
                    tabla.setItem(row, 4, QTableWidgetItem(str(material.get('estado', ''))))
                    tabla.setItem(row, 5, QTableWidgetItem(str(material.get('observaciones', ''))))
                break
    
    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas en la pestaña de resumen."""
        if hasattr(self, 'lbl_total_productos'):
            self.lbl_total_productos.setText(f"Total de productos: {stats.get('total_productos', 0)}")
            self.lbl_stock_total.setText(f"Stock total: {stats.get('stock_total', 0)}")
            self.lbl_stock_disponible.setText(f"Stock disponible: {stats.get('stock_disponible', 0)}")
            self.lbl_stock_asignado.setText(f"Stock asignado: {stats.get('stock_asignado', 0)}")
            self.lbl_obras_activas.setText(f"Obras activas: {stats.get('obras_activas', 0)}")
    
    def aplicar_estilos(self):
        """Aplica estilos modernos a la interfaz."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007acc;
            }
        """)


class DialogoSeparacionMaterial(QDialog):
    """Diálogo para separar material para una obra específica."""
    
    def __init__(self, parent, producto_id, nombre_producto, stock_disponible):
        super().__init__(parent)
        self.producto_id = producto_id
        self.stock_disponible = stock_disponible
        self.init_ui(nombre_producto)
    
    def init_ui(self, nombre_producto):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Separar Material para Obra")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Información del producto
        info_layout = QFormLayout()
        info_layout.addRow("Producto:", QLabel(nombre_producto))
        info_layout.addRow("Stock disponible:", QLabel(str(self.stock_disponible)))
        layout.addLayout(info_layout)
        
        # Formulario de separación
        form_layout = QFormLayout()
        
        # Selección de obra
        self.combo_obra = QComboBox()
        form_layout.addRow("Obra destino:", self.combo_obra)
        
        # Cantidad a separar
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(self.stock_disponible)
        self.spin_cantidad.setValue(1)
        form_layout.addRow("Cantidad a separar:", self.spin_cantidad)
        
        layout.addLayout(form_layout)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)
    
    def cargar_obras(self, obras):
        """Carga las obras disponibles en el combo."""
        self.combo_obra.clear()
        for obra in obras:
            self.combo_obra.addItem(obra['nombre'], obra['id'])
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        obra_id = self.combo_obra.currentData()
        cantidad = self.spin_cantidad.value()
        return obra_id, cantidad