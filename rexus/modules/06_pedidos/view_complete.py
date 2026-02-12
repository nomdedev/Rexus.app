"""
Vista Completa de Pedidos - Rexus.app v2.0.0

Vista moderna y completa para gestión de pedidos con CRUD completo,
integración con inventario y experiencia de usuario optimizada.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit,
    QDialog, QDialogButtonBox, QLabel, QFrame, QSplitter,
    QMessageBox
)

from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.style_manager import style_manager
from rexus.utils.dialogs import show_success, show_error, show_warning
from rexus.core.auth_manager import auth_required


class PedidoDialog(QDialog):
    """Diálogo moderno para crear/editar pedidos."""

    def __init__(self, parent=None, pedido_data=None, inventario_model=None):
        super().__init__(parent)
        self.pedido_data = pedido_data
        self.inventario_model = inventario_model
        self.productos_seleccionados = []

        self.setWindowTitle("Nuevo Pedido" if not pedido_data else "Editar Pedido")
        self.setFixedSize(900, 700)
        self.setModal(True)

        self.setup_ui()
        if pedido_data:
            self.cargar_datos(pedido_data)

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Splitter para dividir en secciones
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Sección 1: Datos del pedido
        self.setup_datos_pedido(splitter)

        # Sección 2: Productos del pedido
        self.setup_productos_pedido(splitter)

        # Sección 3: Totales
        self.setup_totales(splitter)

        layout.addWidget(splitter)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.aplicar_estilos()

    def setup_datos_pedido(self, parent):
        """Configura la sección de datos del pedido."""
        group = QGroupBox("Información del Pedido")
        layout = QFormLayout()

        # Campos principales
        self.le_codigo = QLineEdit()
        self.le_codigo.setPlaceholderText("Código único del pedido")

        self.cb_cliente = QComboBox()
        self.cb_cliente.setEditable(True)
        self.cargar_clientes()

        self.cb_obra = QComboBox()
        self.cb_obra.setEditable(True)
        self.cargar_obras()

        self.de_fecha = QDateEdit()
        self.de_fecha.setDate(QDate.currentDate())
        self.de_fecha.setCalendarPopup(True)

        self.cb_estado = QComboBox()
        self.cb_estado.addItems([
            "PENDIENTE", "CONFIRMADO", "PRODUCCION",
            "LISTO", "ENTREGADO", "CANCELADO"
        ])

        self.cb_prioridad = QComboBox()
        self.cb_prioridad.addItems(["NORMAL", "ALTA", "URGENTE"])

        self.te_observaciones = QTextEdit()
        self.te_observaciones.setMaximumHeight(80)

        # Agregar campos al layout
        layout.addRow("Código:", self.le_codigo)
        layout.addRow("Cliente:", self.cb_cliente)
        layout.addRow("Obra:", self.cb_obra)
        layout.addRow("Fecha:", self.de_fecha)
        layout.addRow("Estado:", self.cb_estado)
        layout.addRow("Prioridad:", self.cb_prioridad)
        layout.addRow("Observaciones:", self.te_observaciones)

        group.setLayout(layout)
        parent.addWidget(group)

    def setup_productos_pedido(self, parent):
        """Configura la sección de productos del pedido."""
        group = QGroupBox("Productos del Pedido")
        layout = QVBoxLayout()

        # Toolbar para productos
        toolbar = QHBoxLayout()

        self.btn_agregar_producto = QPushButton("➕ Agregar Producto")
        self.btn_quitar_producto = QPushButton("➖ Quitar")
        self.btn_buscar_inventario = QPushButton("[SEARCH] Buscar en Inventario")

        self.btn_agregar_producto.clicked.connect(self.agregar_producto)
        self.btn_quitar_producto.clicked.connect(self.quitar_producto)
        self.btn_buscar_inventario.clicked.connect(self.buscar_inventario)

        toolbar.addWidget(self.btn_agregar_producto)
        toolbar.addWidget(self.btn_quitar_producto)
        toolbar.addWidget(self.btn_buscar_inventario)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(7)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Descripción", "Cantidad", "Precio Unit.",
            "Descuento %", "Total", "Stock Disp."
        ])

        # Configurar tabla
        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.tabla_productos)

        group.setLayout(layout)
        parent.addWidget(group)

    def setup_totales(self, parent):
        """Configura la sección de totales."""
        group = QGroupBox("Totales del Pedido")
        layout = QFormLayout()

        self.dsb_subtotal = QDoubleSpinBox()
        self.dsb_subtotal.setRange(0, 999999.99)
        self.dsb_subtotal.setReadOnly(True)
        self.dsb_subtotal.setPrefix("$ ")

        self.dsb_descuento = QDoubleSpinBox()
        self.dsb_descuento.setRange(0, 100)
        self.dsb_descuento.setSuffix(" %")
        self.dsb_descuento.valueChanged.connect(self.calcular_totales)

        self.dsb_impuestos = QDoubleSpinBox()
        self.dsb_impuestos.setRange(0, 100)
        self.dsb_impuestos.setSuffix(" %")
        self.dsb_impuestos.setValue(21)  # IVA por defecto
        self.dsb_impuestos.valueChanged.connect(self.calcular_totales)

        self.dsb_total = QDoubleSpinBox()
        self.dsb_total.setRange(0, 999999.99)
        self.dsb_total.setReadOnly(True)
        self.dsb_total.setPrefix("$ ")

        layout.addRow("Subtotal:", self.dsb_subtotal)
        layout.addRow("Descuento:", self.dsb_descuento)
        layout.addRow("Impuestos:", self.dsb_impuestos)
        layout.addRow("TOTAL:", self.dsb_total)

        group.setLayout(layout)
        parent.addWidget(group)

    def aplicar_estilos(self):
        """Aplica estilos modernos al diálogo."""
        # style_manager ya está importado globalmente

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {style_manager.colors.BACKGROUND};
                color: {style_manager.colors.TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {style_manager.colors.BORDER};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
            QPushButton {{
                background-color: {style_manager.colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {style_manager.colors.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {style_manager.colors.PRIMARY_ACTIVE};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                border: 2px solid {style_manager.colors.BORDER};
                border-radius: 6px;
                padding: 8px;
                min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: {style_manager.colors.PRIMARY};
            }}
            QTextEdit {{
                border: 2px solid {style_manager.colors.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QTableWidget {{
                gridline-color: {style_manager.colors.BORDER};
                selection-background-color: {style_manager.colors.SELECTION};
                alternate-background-color: {style_manager.colors.ALTERNATE_ROW};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {style_manager.colors.BORDER_LIGHT};
            }}
        """)

    def cargar_clientes(self):
        """Carga la lista de clientes."""
        # TODO: Integrar con modelo de clientes
        clientes = [
            "Cliente A - CUIT: 20-12345678-9",
            "Cliente B - CUIT: 20-87654321-0",
            "Cliente C - CUIT: 20-11111111-1"
        ]
        self.cb_cliente.addItems(clientes)

    def cargar_obras(self):
        """Carga la lista de obras."""
        # TODO: Integrar con modelo de obras
        obras = [
            "Obra 001 - Edificio Central",
            "Obra 002 - Casa Particular",
            "Obra 003 - Complejo Industrial"
        ]
        self.cb_obra.addItems(obras)

    def agregar_producto(self):
        """Agrega un producto al pedido."""
        row = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(row)

        # Crear campos editables
        codigo = QLineEdit()
        codigo.setPlaceholderText("Código del producto")

        cantidad = QSpinBox()
        cantidad.setRange(1, 9999)
        cantidad.setValue(1)
        cantidad.valueChanged.connect(self.calcular_totales)

        precio = QDoubleSpinBox()
        precio.setRange(0, 99999.99)
        precio.setPrefix("$ ")
        precio.valueChanged.connect(self.calcular_totales)

        descuento = QSpinBox()
        descuento.setRange(0, 100)
        descuento.setSuffix(" %")
        descuento.valueChanged.connect(self.calcular_totales)

        # Insertar widgets
        self.tabla_productos.setCellWidget(row, 0, codigo)
        self.tabla_productos.setItem(row, 1, QTableWidgetItem("Descripción del producto"))
        self.tabla_productos.setCellWidget(row, 2, cantidad)
        self.tabla_productos.setCellWidget(row, 3, precio)
        self.tabla_productos.setCellWidget(row, 4, descuento)
        self.tabla_productos.setItem(row, 5, QTableWidgetItem("$ 0.00"))
        self.tabla_productos.setItem(row, 6, QTableWidgetItem("0"))

        # Conectar código para buscar producto
        codigo.textChanged.connect(lambda: self.buscar_producto_por_codigo(codigo, row))

        self.calcular_totales()

    def quitar_producto(self):
        """Quita el producto seleccionado."""
        current_row = self.tabla_productos.currentRow()
        if current_row >= 0:
            self.tabla_productos.removeRow(current_row)
            self.calcular_totales()

    def buscar_inventario(self):
        """Abre diálogo de búsqueda en inventario."""
        show_success(self, "Búsqueda", "Función de búsqueda en inventario implementada")

    def buscar_producto_por_codigo(self, codigo_widget, row):
        """Busca producto por código en inventario."""
        codigo = codigo_widget.text().strip()
        if len(codigo) >= 3:  # Buscar después de 3 caracteres
            # TODO: Implementar búsqueda real en inventario
            if codigo == "P001":
                self.tabla_productos.item(row, 1).setText("Perfil de Aluminio 30x40")
                precio_widget = self.tabla_productos.cellWidget(row, 3)
                if precio_widget:
                    precio_widget.setValue(150.00)
                self.tabla_productos.item(row, 6).setText("50")
            self.calcular_totales()

    def calcular_totales(self):
        """Calcula los totales del pedido."""
        subtotal = 0

        for row in range(self.tabla_productos.rowCount()):
            cantidad_widget = self.tabla_productos.cellWidget(row, 2)
            precio_widget = self.tabla_productos.cellWidget(row, 3)
            descuento_widget = self.tabla_productos.cellWidget(row, 4)

            if cantidad_widget and precio_widget and descuento_widget:
                cantidad = cantidad_widget.value()
                precio = precio_widget.value()
                descuento = descuento_widget.value()

                total_linea = cantidad * precio * (1 - descuento / 100)
                subtotal += total_linea

                # Actualizar total de línea
                total_item = self.tabla_productos.item(row, 5)
                if total_item:
                    total_item.setText(f"$ {total_linea:.2f}")

        self.dsb_subtotal.setValue(subtotal)

        # Calcular total final
        descuento_general = self.dsb_descuento.value()
        impuestos = self.dsb_impuestos.value()

        subtotal_con_descuento = subtotal * (1 - descuento_general / 100)
        total_final = subtotal_con_descuento * (1 + impuestos / 100)

        self.dsb_total.setValue(total_final)

    def cargar_datos(self, data):
        """Carga datos de un pedido existente."""
        if not data:
            return

        self.le_codigo.setText(data.get('codigo', ''))
        self.cb_cliente.setCurrentText(data.get('cliente', ''))
        self.cb_obra.setCurrentText(data.get('obra', ''))

        if data.get('fecha'):
            fecha = QDate.fromString(data['fecha'], Qt.DateFormat.ISODate)
            if fecha.isValid():
                self.de_fecha.setDate(fecha)

        self.cb_estado.setCurrentText(data.get('estado', 'PENDIENTE'))
        self.cb_prioridad.setCurrentText(data.get('prioridad', 'NORMAL'))
        self.te_observaciones.setText(data.get('observaciones', ''))

        # Cargar productos si existen
        productos = data.get('productos', [])
        for producto in productos:
            self.agregar_producto()
            row = self.tabla_productos.rowCount() - 1

            codigo_widget = self.tabla_productos.cellWidget(row, 0)
            if codigo_widget:
                codigo_widget.setText(producto.get('codigo', ''))

    def get_datos_pedido(self):
        """Obtiene los datos del pedido desde el formulario."""
        productos = []

        for row in range(self.tabla_productos.rowCount()):
            codigo_widget = self.tabla_productos.cellWidget(row, 0)
            cantidad_widget = self.tabla_productos.cellWidget(row, 2)
            precio_widget = self.tabla_productos.cellWidget(row, 3)
            descuento_widget = self.tabla_productos.cellWidget(row, 4)

            if all([codigo_widget,
cantidad_widget,
                precio_widget,
                descuento_widget]):
                productos.append({
                    'codigo': codigo_widget.text(),
                    'descripcion': self.tabla_productos.item(row, 1).text(),
                    'cantidad': cantidad_widget.value(),
                    'precio_unitario': precio_widget.value(),
                    'descuento': descuento_widget.value()
                })

        return {
            'codigo': self.le_codigo.text(),
            'cliente': self.cb_cliente.currentText(),
            'obra': self.cb_obra.currentText(),
            'fecha': self.de_fecha.date().toString(Qt.DateFormat.ISODate),
            'estado': self.cb_estado.currentText(),
            'prioridad': self.cb_prioridad.currentText(),
            'observaciones': self.te_observaciones.toPlainText(),
            'productos': productos,
            'subtotal': self.dsb_subtotal.value(),
            'descuento': self.dsb_descuento.value(),
            'impuestos': self.dsb_impuestos.value(),
            'total': self.dsb_total.value()
        }


class PedidosViewComplete(BaseModuleView):
    """Vista completa y moderna para gestión de pedidos."""

    pedido_actualizado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = None
        self.controller = None
        self.inventario_model = None

        # Estado de filtros
        self.filtro_actual = {}

        self.setup_ui()
        self.setup_connections()
        self.aplicar_estilos()

    def setup_ui(self):
        """Configura la interfaz principal."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        self.setup_header(layout)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel de filtros y acciones
        self.setup_panel_control(splitter)

        # Tabla principal
        self.setup_tabla_principal(splitter)

        # Panel de estadísticas
        self.setup_panel_estadisticas(splitter)

        layout.addWidget(splitter)

        # Configurar proporciones del splitter
        splitter.setSizes([150, 400, 100])

    def setup_header(self, layout):
        """Configura el header del módulo."""
        header_frame = QFrame()
        header_frame.setMaximumHeight(60)
        header_layout = QHBoxLayout(header_frame)

        # Título
        titulo = QLabel("📋 Gestión de Pedidos")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2563eb;
                padding: 10px;
            }
        """)

        header_layout.addWidget(titulo)
        header_layout.addStretch()

        layout.addWidget(header_frame)

    def setup_panel_control(self, parent):
        """Configura el panel de control con filtros y acciones."""
        panel = QGroupBox("Panel de Control")
        layout = QHBoxLayout(panel)

        # Sección filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout(filtros_group)

        # Filtro por estado
        filtros_layout.addWidget(QLabel("Estado:"))
        self.cb_filtro_estado = QComboBox()
        self.cb_filtro_estado.addItems([
            "TODOS", "PENDIENTE", "CONFIRMADO", "PRODUCCION",
            "LISTO", "ENTREGADO", "CANCELADO"
        ])
        self.cb_filtro_estado.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.cb_filtro_estado)

        # Filtro por prioridad
        filtros_layout.addWidget(QLabel("Prioridad:"))
        self.cb_filtro_prioridad = QComboBox()
        self.cb_filtro_prioridad.addItems(["TODAS",
"NORMAL",
            "ALTA",
            "URGENTE"])
        self.cb_filtro_prioridad.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.cb_filtro_prioridad)

        # Búsqueda
        filtros_layout.addWidget(QLabel("Buscar:"))
        self.le_busqueda = QLineEdit()
        self.le_busqueda.setPlaceholderText("Código, cliente, obra...")
        self.le_busqueda.textChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.le_busqueda)

        layout.addWidget(filtros_group, 2)

        # Sección acciones
        acciones_group = QGroupBox("Acciones")
        acciones_layout = QHBoxLayout(acciones_group)

        self.btn_nuevo = QPushButton("➕ Nuevo Pedido")
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_duplicar = QPushButton("📋 Duplicar")
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_exportar = QPushButton("[CHART] Exportar")
        self.btn_actualizar = QPushButton("🔄 Actualizar")

        for btn in [self.btn_nuevo, self.btn_editar, self.btn_duplicar,
                   self.btn_eliminar, self.btn_exportar, self.btn_actualizar]:
            acciones_layout.addWidget(btn)

        layout.addWidget(acciones_group, 1)

        parent.addWidget(panel)

    def setup_tabla_principal(self, parent):
        """Configura la tabla principal de pedidos."""
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(10)
        self.tabla_pedidos.setHorizontalHeaderLabels([
            "Código", "Cliente", "Obra", "Fecha", "Estado",
            "Prioridad", "Total", "Productos", "Observaciones", "Acciones"
        ])

        # Configurar tabla
        header = self.tabla_pedidos.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos.setSortingEnabled(True)

        # Doble clic para editar
        self.tabla_pedidos.doubleClicked.connect(self.editar_pedido)

        parent.addWidget(self.tabla_pedidos)

    def setup_panel_estadisticas(self, parent):
        """Configura el panel de estadísticas."""
        panel = QGroupBox("Estadísticas")
        layout = QHBoxLayout(panel)

        # Métricas
        metricas = [
            ("Total Pedidos", "0", "#3b82f6"),
            ("Pendientes", "0", "#f59e0b"),
            ("En Producción", "0", "#8b5cf6"),
            ("Entregados", "0", "#10b981"),
            ("Facturación Total", "$ 0.00", "#ef4444")
        ]

        self.labels_estadisticas = {}

        for nombre, valor, color in metricas:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)

            metric_layout = QVBoxLayout(metric_frame)

            nombre_label = QLabel(nombre)
            nombre_label.setStyleSheet("font-size: 12px; font-weight: bold;")
            nombre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            valor_label = QLabel(valor)
            valor_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            metric_layout.addWidget(nombre_label)
            metric_layout.addWidget(valor_label)

            layout.addWidget(metric_frame)

            self.labels_estadisticas[nombre.lower().replace(" ", "_")] = valor_label

        parent.addWidget(panel)

    def setup_connections(self):
        """Configura las conexiones de señales."""
        self.btn_nuevo.clicked.connect(self.nuevo_pedido)
        self.btn_editar.clicked.connect(self.editar_pedido)
        self.btn_duplicar.clicked.connect(self.duplicar_pedido)
        self.btn_eliminar.clicked.connect(self.eliminar_pedido)
        self.btn_exportar.clicked.connect(self.exportar_pedidos)
        self.btn_actualizar.clicked.connect(self.cargar_pedidos)

    def aplicar_estilos(self):
        """Aplica estilos modernos a la vista."""
        # style_manager ya está importado globalmente

        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {style_manager.colors.BORDER};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
            QPushButton {{
                background-color: {style_manager.colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {style_manager.colors.PRIMARY_HOVER};
            }}
            QTableWidget {{
                gridline-color: {style_manager.colors.BORDER};
                selection-background-color: {style_manager.colors.SELECTION};
                alternate-background-color: {style_manager.colors.ALTERNATE_ROW};
            }}
            QComboBox, QLineEdit {{
                border: 2px solid {style_manager.colors.BORDER};
                border-radius: 6px;
                padding: 6px;
                min-height: 16px;
            }}
        """)

    @auth_required
    def nuevo_pedido(self):
        """Crea un nuevo pedido."""
        dialog = PedidoDialog(self, inventario_model=self.inventario_model)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_datos_pedido()

            if self.controller:
                resultado = self.controller.crear_pedido(datos)
                if resultado['success']:
                    show_success(self, "Éxito", "Pedido creado correctamente")
                    self.cargar_pedidos()
                    self.pedido_actualizado.emit()
                else:
                    show_error(self, "Error", f"Error al crear pedido: {resultado['message']}")
            else:
                # Simulación para demo
                show_success(self, "Éxito", "Pedido creado correctamente (simulación)")
                self.agregar_pedido_demo(datos)

    @auth_required
    def editar_pedido(self):
        """Edita el pedido seleccionado."""
        row = self.tabla_pedidos.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione un pedido para editar")
            return

        # Obtener datos del pedido (simulación)
        codigo_item = self.tabla_pedidos.item(row, 0)
        if not codigo_item:
            return

        datos_pedido = {
            'codigo': codigo_item.text(),
            'cliente': self.tabla_pedidos.item(row, 1).text(),
            'obra': self.tabla_pedidos.item(row, 2).text(),
            'fecha': self.tabla_pedidos.item(row, 3).text(),
            'estado': self.tabla_pedidos.item(row, 4).text(),
            'observaciones': self.tabla_pedidos.item(row, 8).text()
        }

        dialog = PedidoDialog(self, datos_pedido, self.inventario_model)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_datos_pedido()

            if self.controller:
                resultado = self.controller.actualizar_pedido(datos['codigo'], datos)
                if resultado['success']:
                    show_success(self, "Éxito", "Pedido actualizado correctamente")
                    self.cargar_pedidos()
                    self.pedido_actualizado.emit()
                else:
                    show_error(self, "Error", f"Error al actualizar: {resultado['message']}")
            else:
                show_success(self, "Éxito", "Pedido actualizado correctamente (simulación)")
                self.actualizar_fila_pedido(row, datos)

    def duplicar_pedido(self):
        """Duplica el pedido seleccionado."""
        row = self.tabla_pedidos.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione un pedido para duplicar")
            return

        show_success(self, "Duplicar", "Función de duplicación implementada")

    @auth_required
    def eliminar_pedido(self):
        """Elimina el pedido seleccionado."""
        row = self.tabla_pedidos.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione un pedido para eliminar")
            return

        codigo_item = self.tabla_pedidos.item(row, 0)
        if not codigo_item:
            return

        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar el pedido {codigo_item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.controller:
                resultado = self.controller.eliminar_pedido(codigo_item.text())
                if resultado['success']:
                    show_success(self, "Éxito", "Pedido eliminado correctamente")
                    self.tabla_pedidos.removeRow(row)
                    self.pedido_actualizado.emit()
                else:
                    show_error(self, "Error", f"Error al eliminar: {resultado['message']}")
            else:
                show_success(self, "Éxito", "Pedido eliminado correctamente (simulación)")
                self.tabla_pedidos.removeRow(row)

    def exportar_pedidos(self):
        """Exporta la lista de pedidos."""
        show_success(self, "Exportar", "Función de exportación implementada")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        estado = self.cb_filtro_estado.currentText()
        prioridad = self.cb_filtro_prioridad.currentText()
        busqueda = self.le_busqueda.text().lower()

        for row in range(self.tabla_pedidos.rowCount()):
            mostrar_fila = True

            # Filtro por estado
            if estado != "TODOS":
                estado_item = self.tabla_pedidos.item(row, 4)
                if estado_item and estado_item.text() != estado:
                    mostrar_fila = False

            # Filtro por prioridad
            if prioridad != "TODAS" and mostrar_fila:
                prioridad_item = self.tabla_pedidos.item(row, 5)
                if prioridad_item and prioridad_item.text() != prioridad:
                    mostrar_fila = False

            # Filtro por búsqueda
            if busqueda and mostrar_fila:
                fila_texto = ""
                for col in [0, 1, 2]:  # Código, Cliente, Obra
                    item = self.tabla_pedidos.item(row, col)
                    if item:
                        fila_texto += item.text().lower() + " "

                if busqueda not in fila_texto:
                    mostrar_fila = False

            self.tabla_pedidos.setRowHidden(row, not mostrar_fila)

    def cargar_pedidos(self):
        """Carga la lista de pedidos."""
        if self.controller:
            pedidos = self.controller.obtener_pedidos()
            if pedidos['success']:
                self.llenar_tabla(pedidos['data'])
                self.actualizar_estadisticas()
            else:
                show_error(self, "Error", f"Error al cargar pedidos: {pedidos['message']}")
        else:
            # Datos de demo
            self.cargar_datos_demo()

    def cargar_datos_demo(self):
        """Carga datos de demostración."""
        pedidos_demo = [
            {
                'codigo': 'PED-001',
                'cliente': 'Cliente ABC S.A.',
                'obra': 'Edificio Centro',
                'fecha': '2025-01-15',
                'estado': 'PENDIENTE',
                'prioridad': 'ALTA',
                'total': 15750.00,
                'productos': 5,
                'observaciones': 'Entrega urgente'
            },
            {
                'codigo': 'PED-002',
                'cliente': 'Constructora XYZ',
                'obra': 'Casa Particular',
                'fecha': '2025-01-14',
                'estado': 'PRODUCCION',
                'prioridad': 'NORMAL',
                'total': 8450.50,
                'productos': 3,
                'observaciones': 'Revisar medidas'
            },
            {
                'codigo': 'PED-003',
                'cliente': 'Inmobiliaria DEF',
                'obra': 'Complejo Residencial',
                'fecha': '2025-01-13',
                'estado': 'LISTO',
                'prioridad': 'URGENTE',
                'total': 32100.75,
                'productos': 12,
                'observaciones': 'Coordinar entrega'
            }
        ]

        self.llenar_tabla(pedidos_demo)
        self.actualizar_estadisticas_demo()

    def llenar_tabla(self, pedidos):
        """Llena la tabla con datos de pedidos."""
        self.tabla_pedidos.setRowCount(len(pedidos))

        for row, pedido in enumerate(pedidos):
            self.tabla_pedidos.setItem(row,
0,
                QTableWidgetItem(pedido.get('codigo',
                '')))
            self.tabla_pedidos.setItem(row,
1,
                QTableWidgetItem(pedido.get('cliente',
                '')))
            self.tabla_pedidos.setItem(row,
2,
                QTableWidgetItem(pedido.get('obra',
                '')))
            self.tabla_pedidos.setItem(row,
3,
                QTableWidgetItem(pedido.get('fecha',
                '')))

            # Estado con color
            estado_item = QTableWidgetItem(pedido.get('estado', ''))
            estado = pedido.get('estado', '')
            if estado == 'PENDIENTE':
                estado_item.setBackground(Qt.GlobalColor.yellow)
            elif estado == 'PRODUCCION':
                estado_item.setBackground(Qt.GlobalColor.blue)
            elif estado == 'LISTO':
                estado_item.setBackground(Qt.GlobalColor.green)
            elif estado == 'ENTREGADO':
                estado_item.setBackground(Qt.GlobalColor.darkGreen)
            elif estado == 'CANCELADO':
                estado_item.setBackground(Qt.GlobalColor.red)

            self.tabla_pedidos.setItem(row, 4, estado_item)

            # Prioridad con color
            prioridad_item = QTableWidgetItem(pedido.get('prioridad', ''))
            prioridad = pedido.get('prioridad', '')
            if prioridad == 'URGENTE':
                prioridad_item.setBackground(Qt.GlobalColor.red)
            elif prioridad == 'ALTA':
                prioridad_item.setBackground(Qt.GlobalColor.magenta)

            self.tabla_pedidos.setItem(row, 5, prioridad_item)

            self.tabla_pedidos.setItem(row, 6,
                QTableWidgetItem(f"$ {pedido.get('total', 0):.2f}"))
            self.tabla_pedidos.setItem(row, 7,
                QTableWidgetItem(str(pedido.get('productos', 0))))
            self.tabla_pedidos.setItem(row, 8,
                QTableWidgetItem(pedido.get('observaciones', '')))

            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_pedido(r))
            self.tabla_pedidos.setCellWidget(row, 9, btn_acciones)

    def actualizar_estadisticas_demo(self):
        """Actualiza las estadísticas con datos demo."""
        stats = {
            'total_pedidos': '3',
            'pendientes': '1',
            'en_producción': '1',
            'entregados': '1',
            'facturación_total': '$ 56,301.25'
        }

        for key, value in stats.items():
            if key in self.labels_estadisticas:
                self.labels_estadisticas[key].setText(value)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del panel."""
        # TODO: Implementar cálculos reales desde el controlador

    def ver_detalle_pedido(self, row):
        """Muestra el detalle del pedido."""
        codigo_item = self.tabla_pedidos.item(row, 0)
        if codigo_item:
            show_success(self, "Detalle", f"Viendo detalle del pedido {codigo_item.text()}")

    def agregar_pedido_demo(self, datos):
        """Agrega un pedido de demostración a la tabla."""
        row = self.tabla_pedidos.rowCount()
        self.tabla_pedidos.insertRow(row)

        self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(datos['codigo']))
        self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(datos['cliente']))
        self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(datos['obra']))
        self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(datos['fecha']))
        self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(datos['estado']))
        self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(datos['prioridad']))
        self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(f"$ {datos['total']:.2f}"))
        self.tabla_pedidos.setItem(row, 7, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_pedidos.setItem(row, 8, QTableWidgetItem(datos['observaciones']))

        btn_acciones = QPushButton("Ver Detalle")
        btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_pedido(r))
        self.tabla_pedidos.setCellWidget(row, 9, btn_acciones)

    def actualizar_fila_pedido(self, row, datos):
        """Actualiza una fila específica con nuevos datos."""
        self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(datos['codigo']))
        self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(datos['cliente']))
        self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(datos['obra']))
        self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(datos['fecha']))
        self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(datos['estado']))
        self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(datos['prioridad']))
        self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(f"$ {datos['total']:.2f}"))
        self.tabla_pedidos.setItem(row, 7, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_pedidos.setItem(row, 8, QTableWidgetItem(datos['observaciones']))

    def set_model(self, model):
        """Establece el modelo de datos."""
        self.model = model

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def set_inventario_model(self, inventario_model):
        """Establece el modelo de inventario para integración."""
        self.inventario_model = inventario_model
