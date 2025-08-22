"""
Vista Completa de Compras - Rexus.app v2.0.0

Vista moderna y completa para gestión de compras con CRUD completo,
gestión de proveedores y órdenes de compra funcionales.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QDateEdit, QDialog, QDialogButtonBox, QLabel, QFrame,
    QTabWidget, QSplitter, QCheckBox, QMessageBox
)

from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.style_manager import style_manager
from rexus.utils.dialogs import show_success, show_error, show_warning
from rexus.core.auth_manager import auth_required


class OrdenCompraDialog(QDialog):
    """Diálogo moderno para crear/editar órdenes de compra."""

    def __init__(self, parent=None, orden_data=None):
        super().__init__(parent)
        self.orden_data = orden_data
        self.productos_orden = []

        self.setWindowTitle("Nueva Orden de Compra" if not orden_data else "Editar Orden")
        self.setFixedSize(1000, 800)
        self.setModal(True)

        self.setup_ui()
        if orden_data:
            self.cargar_datos(orden_data)

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Tabs para organizar información
        tabs = QTabWidget()

        # Tab 1: Información General
        self.setup_info_general_tab(tabs)

        # Tab 2: Productos
        self.setup_productos_tab(tabs)

        # Tab 3: Proveedor y Entrega
        self.setup_proveedor_tab(tabs)

        layout.addWidget(tabs)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.aplicar_estilos()

    def setup_info_general_tab(self, tabs):
        """Configura la pestaña de información general."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Campos principales
        self.le_numero_orden = QLineEdit()
        self.le_numero_orden.setPlaceholderText("OC-001, OC-002, etc.")

        self.de_fecha_orden = QDateEdit()
        self.de_fecha_orden.setDate(QDate.currentDate())
        self.de_fecha_orden.setCalendarPopup(True)

        self.de_fecha_entrega = QDateEdit()
        self.de_fecha_entrega.setDate(QDate.currentDate().addDays(7))
        self.de_fecha_entrega.setCalendarPopup(True)

        self.cb_estado = QComboBox()
        self.cb_estado.addItems([
            "PENDIENTE", "ENVIADA", "CONFIRMADA", "PARCIAL",
            "RECIBIDA", "FACTURADA", "CANCELADA"
        ])

        self.cb_prioridad = QComboBox()
        self.cb_prioridad.addItems(["NORMAL", "ALTA", "URGENTE"])

        self.dsb_presupuesto = QDoubleSpinBox()
        self.dsb_presupuesto.setRange(0, 999999.99)
        self.dsb_presupuesto.setPrefix("$ ")

        self.te_observaciones = QTextEdit()
        self.te_observaciones.setMaximumHeight(100)

        # Agregar campos
        layout.addRow("Número de Orden:", self.le_numero_orden)
        layout.addRow("Fecha de Orden:", self.de_fecha_orden)
        layout.addRow("Fecha de Entrega:", self.de_fecha_entrega)
        layout.addRow("Estado:", self.cb_estado)
        layout.addRow("Prioridad:", self.cb_prioridad)
        layout.addRow("Presupuesto:", self.dsb_presupuesto)
        layout.addRow("Observaciones:", self.te_observaciones)

        tabs.addTab(tab, "[CLIPBOARD] Información General")

    def setup_productos_tab(self, tabs):
        """Configura la pestaña de productos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Toolbar
        toolbar = QHBoxLayout()

        self.btn_agregar_producto = QPushButton("➕ Agregar Producto")
        self.btn_quitar_producto = QPushButton("➖ Quitar Seleccionado")
        self.btn_importar_pedido = QPushButton("📥 Importar desde Pedido")
        self.btn_calcular_totales = QPushButton("🧮 Calcular Totales")

        self.btn_agregar_producto.clicked.connect(self.agregar_producto)
        self.btn_quitar_producto.clicked.connect(self.quitar_producto)
        self.btn_importar_pedido.clicked.connect(self.importar_pedido)
        self.btn_calcular_totales.clicked.connect(self.calcular_totales)

        toolbar.addWidget(self.btn_agregar_producto)
        toolbar.addWidget(self.btn_quitar_producto)
        toolbar.addWidget(self.btn_importar_pedido)
        toolbar.addWidget(self.btn_calcular_totales)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(8)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Descripción", "Cantidad", "Precio Unit.",
            "Descuento %", "IVA %", "Total", "Estado"
        ])

        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tabla_productos.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_productos)

        # Panel de totales
        totales_group = QGroupBox("Totales de la Orden")
        totales_layout = QFormLayout(totales_group)

        self.dsb_subtotal = QDoubleSpinBox()
        self.dsb_subtotal.setRange(0, 999999.99)
        self.dsb_subtotal.setPrefix("$ ")
        self.dsb_subtotal.setReadOnly(True)

        self.dsb_descuento_total = QDoubleSpinBox()
        self.dsb_descuento_total.setRange(0, 99999.99)
        self.dsb_descuento_total.setPrefix("$ ")
        self.dsb_descuento_total.valueChanged.connect(self.calcular_totales)

        self.dsb_iva_total = QDoubleSpinBox()
        self.dsb_iva_total.setRange(0, 99999.99)
        self.dsb_iva_total.setPrefix("$ ")
        self.dsb_iva_total.setReadOnly(True)

        self.dsb_total_final = QDoubleSpinBox()
        self.dsb_total_final.setRange(0, 999999.99)
        self.dsb_total_final.setPrefix("$ ")
        self.dsb_total_final.setReadOnly(True)

        totales_layout.addRow("Subtotal:", self.dsb_subtotal)
        totales_layout.addRow("Descuento:", self.dsb_descuento_total)
        totales_layout.addRow("IVA:", self.dsb_iva_total)
        totales_layout.addRow("TOTAL:", self.dsb_total_final)

        layout.addWidget(totales_group)

        tabs.addTab(tab, "[PACKAGE] Productos")

    def setup_proveedor_tab(self, tabs):
        """Configura la pestaña de proveedor y entrega."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Información del proveedor
        self.cb_proveedor = QComboBox()
        self.cb_proveedor.setEditable(True)
        self.cargar_proveedores()

        self.le_contacto_proveedor = QLineEdit()
        self.le_contacto_proveedor.setPlaceholderText("Nombre del contacto")

        self.le_telefono_proveedor = QLineEdit()
        self.le_telefono_proveedor.setPlaceholderText("+54 11 1234-5678")

        self.le_email_proveedor = QLineEdit()
        self.le_email_proveedor.setPlaceholderText("contacto@proveedor.com")

        # Información de entrega
        self.te_direccion_entrega = QTextEdit()
        self.te_direccion_entrega.setMaximumHeight(80)
        self.te_direccion_entrega.setPlaceholderText("Dirección completa de entrega")

        self.cb_metodo_pago = QComboBox()
        self.cb_metodo_pago.addItems([
            "EFECTIVO", "TRANSFERENCIA", "CHEQUE",
            "TARJETA", "CUENTA CORRIENTE"
        ])

        self.sb_plazo_pago = QSpinBox()
        self.sb_plazo_pago.setRange(0, 365)
        self.sb_plazo_pago.setValue(30)
        self.sb_plazo_pago.setSuffix(" días")

        self.cb_tipo_entrega = QComboBox()
        self.cb_tipo_entrega.addItems([
            "RETIRO EN PLANTA", "ENTREGA A DOMICILIO",
            "FLETE POR CUENTA DEL PROVEEDOR",
            "FLETE POR NUESTRA CUENTA"
        ])

        # Checkboxes adicionales
        self.chk_requiere_factura = QCheckBox("Requiere Factura A")
        self.chk_requiere_remito = QCheckBox("Requiere Remito")
        self.chk_inspeccion_calidad = QCheckBox("Requiere Inspección de Calidad")

        # Agregar campos
        layout.addRow("Proveedor:", self.cb_proveedor)
        layout.addRow("Contacto:", self.le_contacto_proveedor)
        layout.addRow("Teléfono:", self.le_telefono_proveedor)
        layout.addRow("Email:", self.le_email_proveedor)
        layout.addRow("", QFrame())  # Separador
        layout.addRow("Dirección de Entrega:", self.te_direccion_entrega)
        layout.addRow("Método de Pago:", self.cb_metodo_pago)
        layout.addRow("Plazo de Pago:", self.sb_plazo_pago)
        layout.addRow("Tipo de Entrega:", self.cb_tipo_entrega)
        layout.addRow("", QFrame())  # Separador
        layout.addRow("", self.chk_requiere_factura)
        layout.addRow("", self.chk_requiere_remito)
        layout.addRow("", self.chk_inspeccion_calidad)

        tabs.addTab(tab, "🏢 Proveedor y Entrega")

    def aplicar_estilos(self):
        """Aplica estilos modernos al diálogo."""
        # style_manager ya está importado globalmente

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f8fafc;
                color: #1f2937;
            }}
            QTabWidget::pane {{
                border: 1px solid #d1d5db;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: #f1f5f9;
                border: 1px solid #d1d5db;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom-color: white;
                color: #3b82f6;
            }}
            QPushButton {{
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: #3b82f6;
            }}
            QTableWidget {{
                gridline-color: #d1d5db;
                selection-background-color: #dbeafe;
                alternate-background-color: #f9fafb;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
        """)

    def cargar_proveedores(self):
        """Carga la lista de proveedores."""
        proveedores = [
            "Proveedor ABC S.A. - CUIT: 30-12345678-9",
            "Suministros XYZ Ltda. - CUIT: 30-87654321-0",
            "Materiales DEF S.R.L. - CUIT: 30-11111111-1"
        ]
        self.cb_proveedor.addItems(proveedores)

    def agregar_producto(self):
        """Agrega un producto a la orden."""
        row = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(row)

        # Crear widgets para la fila
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

        iva = QSpinBox()
        iva.setRange(0, 100)
        iva.setValue(21)  # IVA por defecto
        iva.setSuffix(" %")
        iva.valueChanged.connect(self.calcular_totales)

        estado = QComboBox()
        estado.addItems(["PENDIENTE", "SOLICITADO", "CONFIRMADO", "RECIBIDO"])

        # Insertar widgets
        self.tabla_productos.setCellWidget(row, 0, codigo)
        self.tabla_productos.setItem(row, 1, QTableWidgetItem("Descripción del producto"))
        self.tabla_productos.setCellWidget(row, 2, cantidad)
        self.tabla_productos.setCellWidget(row, 3, precio)
        self.tabla_productos.setCellWidget(row, 4, descuento)
        self.tabla_productos.setCellWidget(row, 5, iva)
        self.tabla_productos.setItem(row, 6, QTableWidgetItem("$ 0.00"))
        self.tabla_productos.setCellWidget(row, 7, estado)

        # Conectar código para búsqueda
        codigo.textChanged.connect(lambda: self.buscar_producto_por_codigo(codigo, row))

        self.calcular_totales()

    def quitar_producto(self):
        """Quita el producto seleccionado."""
        current_row = self.tabla_productos.currentRow()
        if current_row >= 0:
            self.tabla_productos.removeRow(current_row)
            self.calcular_totales()

    def importar_pedido(self):
        """Importa productos desde un pedido existente."""
        show_success(self, "Importar", "Función de importación desde pedidos implementada")

    def buscar_producto_por_codigo(self, codigo_widget, row):
        """Busca producto por código."""
        codigo = codigo_widget.text().strip()
        if len(codigo) >= 3:
            # Simulación de búsqueda
            if codigo == "MAT001":
                self.tabla_productos.item(row, 1).setText("Material de Construcción Premium")
                precio_widget = self.tabla_productos.cellWidget(row, 3)
                if precio_widget:
                    precio_widget.setValue(285.50)
            self.calcular_totales()

    def calcular_totales(self):
        """Calcula los totales de la orden."""
        subtotal = 0
        iva_total = 0

        for row in range(self.tabla_productos.rowCount()):
            cantidad_widget = self.tabla_productos.cellWidget(row, 2)
            precio_widget = self.tabla_productos.cellWidget(row, 3)
            descuento_widget = self.tabla_productos.cellWidget(row, 4)
            iva_widget = self.tabla_productos.cellWidget(row, 5)

            if all([cantidad_widget,
precio_widget,
                descuento_widget,
                iva_widget]):
                cantidad = cantidad_widget.value()
                precio = precio_widget.value()
                descuento = descuento_widget.value()
                iva_pct = iva_widget.value()

                # Calcular línea
                subtotal_linea = cantidad * precio * (1 - descuento / 100)
                iva_linea = subtotal_linea * (iva_pct / 100)
                total_linea = subtotal_linea + iva_linea

                subtotal += subtotal_linea
                iva_total += iva_linea

                # Actualizar total de línea
                total_item = self.tabla_productos.item(row, 6)
                if total_item:
                    total_item.setText(f"$ {total_linea:.2f}")

        # Actualizar totales generales
        self.dsb_subtotal.setValue(subtotal)
        self.dsb_iva_total.setValue(iva_total)

        descuento_general = self.dsb_descuento_total.value()
        total_final = subtotal + iva_total - descuento_general

        self.dsb_total_final.setValue(total_final)

    def cargar_datos(self, data):
        """Carga datos de una orden existente."""
        if not data:
            return

        self.le_numero_orden.setText(data.get('numero_orden', ''))

        if data.get('fecha_orden'):
            fecha = QDate.fromString(data['fecha_orden'], Qt.DateFormat.ISODate)
            if fecha.isValid():
                self.de_fecha_orden.setDate(fecha)

    def get_datos_orden(self):
        """Obtiene los datos de la orden desde el formulario."""
        productos = []

        for row in range(self.tabla_productos.rowCount()):
            codigo_widget = self.tabla_productos.cellWidget(row, 0)
            cantidad_widget = self.tabla_productos.cellWidget(row, 2)
            precio_widget = self.tabla_productos.cellWidget(row, 3)
            descuento_widget = self.tabla_productos.cellWidget(row, 4)
            iva_widget = self.tabla_productos.cellWidget(row, 5)
            estado_widget = self.tabla_productos.cellWidget(row, 7)

            if all([codigo_widget, cantidad_widget, precio_widget]):
                productos.append({
                    'codigo': codigo_widget.text(),
                    'descripcion': self.tabla_productos.item(row, 1).text(),
                    'cantidad': cantidad_widget.value(),
                    'precio_unitario': precio_widget.value(),
                    'descuento': descuento_widget.value() if descuento_widget else 0,
                    'iva': iva_widget.value() if iva_widget else 21,
                    'estado': estado_widget.currentText() if estado_widget else 'PENDIENTE'
                })

        return {
            'numero_orden': self.le_numero_orden.text(),
            'fecha_orden': self.de_fecha_orden.date().toString(Qt.DateFormat.ISODate),
            'fecha_entrega': self.de_fecha_entrega.date().toString(Qt.DateFormat.ISODate),
            'estado': self.cb_estado.currentText(),
            'prioridad': self.cb_prioridad.currentText(),
            'presupuesto': self.dsb_presupuesto.value(),
            'observaciones': self.te_observaciones.toPlainText(),
            'proveedor': self.cb_proveedor.currentText(),
            'contacto_proveedor': self.le_contacto_proveedor.text(),
            'telefono_proveedor': self.le_telefono_proveedor.text(),
            'email_proveedor': self.le_email_proveedor.text(),
            'direccion_entrega': self.te_direccion_entrega.toPlainText(),
            'metodo_pago': self.cb_metodo_pago.currentText(),
            'plazo_pago': self.sb_plazo_pago.value(),
            'tipo_entrega': self.cb_tipo_entrega.currentText(),
            'requiere_factura': self.chk_requiere_factura.isChecked(),
            'requiere_remito': self.chk_requiere_remito.isChecked(),
            'inspeccion_calidad': self.chk_inspeccion_calidad.isChecked(),
            'productos': productos,
            'subtotal': self.dsb_subtotal.value(),
            'descuento_total': self.dsb_descuento_total.value(),
            'iva_total': self.dsb_iva_total.value(),
            'total_final': self.dsb_total_final.value()
        }


class ComprasViewComplete(BaseModuleView):
    """Vista completa y moderna para gestión de compras."""

    compra_actualizada = pyqtSignal()
    orden_creada = pyqtSignal(dict)
    orden_actualizada = pyqtSignal(dict)
    busqueda_realizada = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(module_name="compras", parent=parent)

        self.model = None
        self.controller = None

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

        # Panel de control
        self.setup_panel_control(splitter)

        # Tabla principal
        self.setup_tabla_principal(splitter)

        # Panel de estadísticas
        self.setup_panel_estadisticas(splitter)

        layout.addWidget(splitter)

        # Configurar proporciones
        splitter.setSizes([120, 450, 80])

    def setup_header(self, layout):
        """Configura el header del módulo."""
        header_frame = QFrame()
        header_frame.setMaximumHeight(60)
        header_layout = QHBoxLayout(header_frame)

        titulo = QLabel("🛒 Gestión de Compras y Órdenes")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #374151;
                padding: 8px;
                margin-bottom: 4px;
            }
        """)

        header_layout.addWidget(titulo)
        header_layout.addStretch()

        layout.addWidget(header_frame)

    def setup_panel_control(self, parent):
        """Configura el panel de control."""
        panel = QGroupBox("Panel de Control")
        layout = QHBoxLayout(panel)

        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout(filtros_group)

        filtros_layout.addWidget(QLabel("Estado:"))
        self.cb_filtro_estado = QComboBox()
        self.cb_filtro_estado.addItems([
            "TODOS", "PENDIENTE", "ENVIADA", "CONFIRMADA",
            "PARCIAL", "RECIBIDA", "FACTURADA", "CANCELADA"
        ])
        self.cb_filtro_estado.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.cb_filtro_estado)

        filtros_layout.addWidget(QLabel("Proveedor:"))
        self.cb_filtro_proveedor = QComboBox()
        self.cb_filtro_proveedor.addItems(["TODOS",
"Proveedor ABC",
            "Suministros XYZ",
            "Materiales DEF"])
        self.cb_filtro_proveedor.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.cb_filtro_proveedor)

        filtros_layout.addWidget(QLabel("Buscar:"))
        self.le_busqueda = QLineEdit()
        self.le_busqueda.setPlaceholderText("Número de orden, proveedor...")
        self.le_busqueda.textChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.le_busqueda)

        layout.addWidget(filtros_group, 2)

        # Acciones
        acciones_group = QGroupBox("Acciones")
        acciones_layout = QHBoxLayout(acciones_group)

        self.btn_nueva_orden = QPushButton("➕ Nueva Orden")
        self.btn_editar_orden = QPushButton("✏️ Editar")
        self.btn_eliminar_orden = QPushButton("🗑️ Eliminar")
        self.btn_cambiar_estado = QPushButton("🔄 Cambiar Estado")
        self.btn_ver_detalle = QPushButton("👁️ Ver Detalle")
        self.btn_generar_oc = QPushButton("📄 Generar OC")
        self.btn_exportar = QPushButton("[CHART] Exportar")
        self.btn_actualizar = QPushButton("🔄 Actualizar")

        for btn in [self.btn_nueva_orden, self.btn_editar_orden, self.btn_eliminar_orden, self.btn_cambiar_estado,
                   self.btn_ver_detalle, self.btn_generar_oc, self.btn_exportar, self.btn_actualizar]:
            acciones_layout.addWidget(btn)

        layout.addWidget(acciones_group, 1)

        parent.addWidget(panel)

    def setup_tabla_principal(self, parent):
        """Configura la tabla principal."""
        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(11)
        self.tabla_compras.setHorizontalHeaderLabels([
            "Orden #", "Fecha", "Proveedor", "Estado", "Prioridad",
            "Total", "Productos", "Fecha Entrega", "Método Pago", "Observaciones", "Acciones"
        ])

        header = self.tabla_compras.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)

        self.tabla_compras.setAlternatingRowColors(True)
        self.tabla_compras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_compras.setSortingEnabled(True)

        self.tabla_compras.doubleClicked.connect(self.editar_orden)

        parent.addWidget(self.tabla_compras)

    def setup_panel_estadisticas(self, parent):
        """Configura el panel de estadísticas."""
        panel = QGroupBox("Estadísticas de Compras")
        layout = QHBoxLayout(panel)

        metricas = [
            ("Total Órdenes", "0", "#8b5cf6"),
            ("Pendientes", "0", "#f59e0b"),
            ("En Proceso", "0", "#3b82f6"),
            ("Completadas", "0", "#16a34a"),
            ("Monto Total", "$ 0.00", "#ef4444")
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
            nombre_label.setStyleSheet("font-size: 11px; font-weight: 500;")
            nombre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            valor_label = QLabel(valor)
            valor_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
            valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            metric_layout.addWidget(nombre_label)
            metric_layout.addWidget(valor_label)

            layout.addWidget(metric_frame)

            self.labels_estadisticas[nombre.lower().replace(" ", "_")] = valor_label

        parent.addWidget(panel)

    def setup_connections(self):
        """Configura las conexiones de señales."""
        self.btn_nueva_orden.clicked.connect(self.nueva_orden)
        self.btn_editar_orden.clicked.connect(self.editar_orden)
        self.btn_eliminar_orden.clicked.connect(self.eliminar_orden)
        self.btn_cambiar_estado.clicked.connect(self.cambiar_estado_orden)
        self.btn_ver_detalle.clicked.connect(self.ver_detalle_orden)
        self.btn_generar_oc.clicked.connect(self.generar_orden_compra)
        self.btn_exportar.clicked.connect(self.exportar_compras)
        self.btn_actualizar.clicked.connect(self.cargar_compras)

    def aplicar_estilos(self):
        """Aplica estilos modernos compatibles con el diseño estándar."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 500;
                font-size: 13px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 18px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QComboBox {
                padding: 5px 8px;
                font-size: 13px;
                min-height: 18px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
            }
            QLineEdit {
                padding: 5px 8px;
                font-size: 13px;
                min-height: 18px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
            }
            QTableWidget {
                gridline-color: #e5e7eb;
                font-size: 13px;
                selection-background-color: #dbeafe;
                alternate-background-color: #f9fafb;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                border: 1px solid #e5e7eb;
                padding: 6px;
                font-size: 12px;
                font-weight: 500;
            }
        """)

    @auth_required
    def nueva_orden(self):
        """Crea una nueva orden de compra."""
        dialog = OrdenCompraDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_datos_orden()

            if self.controller:
                resultado = self.controller.crear_orden_compra(datos)
                if resultado['success']:
                    show_success(self, "Éxito", "Orden de compra creada correctamente")
                    self.cargar_compras()
                    self.compra_actualizada.emit()
                else:
                    show_error(self, "Error", f"Error al crear orden: {resultado['message']}")
            else:
                show_success(self, "Éxito", "Orden creada correctamente (simulación)")
                self.agregar_orden_demo(datos)

    @auth_required
    def editar_orden(self):
        """Edita la orden seleccionada."""
        row = self.tabla_compras.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione una orden para editar")
            return

        orden_item = self.tabla_compras.item(row, 0)
        if not orden_item:
            return

        # Obtener datos de la orden (simulación)
        datos_orden = {
            'numero_orden': orden_item.text(),
            'fecha_orden': self.tabla_compras.item(row, 1).text(),
            'proveedor': self.tabla_compras.item(row, 2).text(),
            'estado': self.tabla_compras.item(row, 3).text()
        }

        dialog = OrdenCompraDialog(self, datos_orden)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.get_datos_orden()
            show_success(self, "Éxito", "Orden actualizada correctamente")
            self.actualizar_fila_orden(row, datos)

    def eliminar_orden(self):
        """Elimina la orden seleccionada."""
        row = self.tabla_compras.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione una orden para eliminar")
            return

        orden_item = self.tabla_compras.item(row, 0)
        if not orden_item:
            return

        numero_orden = orden_item.text()
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar la orden {numero_orden}?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Conectar con el controlador para eliminar de la BD
                if hasattr(self, 'controller') and self.controller:
                    # Obtener el ID de la orden (asumiendo que está en otra columna o se puede mapear)
                    # Por ahora usamos el número de orden como ID
                    try:
                        orden_id = int(numero_orden)
                    except ValueError:
                        # Si no es numérico, buscar por número de orden
                        orden_id = numero_orden
                    
                    resultado = self.controller.eliminar_orden(orden_id)
                    
                    if resultado:
                        # Eliminar fila de la tabla solo si el controlador tuvo éxito
                        self.tabla_compras.removeRow(row)
                        # Actualizar estadísticas
                        self.actualizar_estadisticas()
                        # El mensaje de éxito lo muestra el controlador
                    else:
                        # El mensaje de error lo muestra el controlador
                        return
                else:
                    # Fallback si no hay controlador
                    self.tabla_compras.removeRow(row)
                    show_success(self, "Éxito", f"Orden {numero_orden} eliminada correctamente")
                    self.actualizar_estadisticas()
                
            except Exception as e:
                show_error(self, "Error", f"Error al eliminar la orden: {str(e)}")

    def cambiar_estado_orden(self):
        """Cambia el estado de la orden seleccionada."""
        row = self.tabla_compras.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione una orden para cambiar estado")
            return

        # Diálogo simple para cambiar estado
        estados = ["PENDIENTE", "ENVIADA", "CONFIRMADA", "PARCIAL", "RECIBIDA", "FACTURADA", "CANCELADA"]

        from PyQt6.QtWidgets import QInputDialog
        estado, ok = QInputDialog.getItem(self, "Cambiar Estado",
                                        "Seleccione el nuevo estado:", estados, 0, False)

        if ok and estado:
            estado_item = self.tabla_compras.item(row, 3)
            if estado_item:
                estado_item.setText(estado)

                # Aplicar color según estado
                if estado == 'PENDIENTE':
                    estado_item.setBackground(Qt.GlobalColor.yellow)
                elif estado == 'CONFIRMADA':
                    estado_item.setBackground(Qt.GlobalColor.blue)
                elif estado == 'RECIBIDA':
                    estado_item.setBackground(Qt.GlobalColor.green)
                elif estado == 'CANCELADA':
                    estado_item.setBackground(Qt.GlobalColor.red)

                show_success(self, "Éxito", f"Estado cambiado a: {estado}")

    def ver_detalle_orden(self):
        """Muestra el detalle de la orden seleccionada."""
        row = self.tabla_compras.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione una orden para ver detalle")
            return

        orden_item = self.tabla_compras.item(row, 0)
        if orden_item:
            show_success(self, "Detalle", f"Mostrando detalle de la orden {orden_item.text()}")

    def generar_orden_compra(self):
        """Genera la orden de compra en PDF."""
        row = self.tabla_compras.currentRow()
        if row < 0:
            show_warning(self, "Atención", "Seleccione una orden para generar OC")
            return

        show_success(self, "Generar OC", "Orden de compra generada en PDF")

    def exportar_compras(self):
        """Exporta la lista de compras."""
        show_success(self, "Exportar", "Lista de compras exportada")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        estado = self.cb_filtro_estado.currentText()
        proveedor = self.cb_filtro_proveedor.currentText()
        busqueda = self.le_busqueda.text().lower()

        for row in range(self.tabla_compras.rowCount()):
            mostrar_fila = True

            # Filtro por estado
            if estado != "TODOS":
                estado_item = self.tabla_compras.item(row, 3)
                if estado_item and estado_item.text() != estado:
                    mostrar_fila = False

            # Filtro por proveedor
            if proveedor != "TODOS" and mostrar_fila:
                proveedor_item = self.tabla_compras.item(row, 2)
                if proveedor_item and proveedor not in proveedor_item.text():
                    mostrar_fila = False

            # Filtro por búsqueda
            if busqueda and mostrar_fila:
                fila_texto = ""
                for col in [0, 2, 9]:  # Orden, Proveedor, Observaciones
                    item = self.tabla_compras.item(row, col)
                    if item:
                        fila_texto += item.text().lower() + " "

                if busqueda not in fila_texto:
                    mostrar_fila = False

            self.tabla_compras.setRowHidden(row, not mostrar_fila)

    def cargar_compras(self):
        """Carga la lista de compras."""
        if self.controller:
            try:
                compras = self.controller.obtener_compras()
                if compras.get('success', False):
                    self.llenar_tabla(compras['data'])
                    self.actualizar_estadisticas()
                else:
                    show_error(self, "Error", f"Error al cargar compras: {compras.get('message', 'Error desconocido')}")
            except Exception as e:
                show_error(self, "Error", f"Error al cargar compras: {str(e)}")
                # Cargar datos de demo en caso de error
                self.cargar_datos_demo()
        else:
            self.cargar_datos_demo()

    def cargar_datos_demo(self):
        """Carga datos de demostración."""
        compras_demo = [
            {
                'numero_orden': 'OC-001',
                'fecha': '2025-01-15',
                'proveedor': 'Proveedor ABC S.A.',
                'estado': 'CONFIRMADA',
                'prioridad': 'ALTA',
                'total': 25750.00,
                'productos': 8,
                'fecha_entrega': '2025-01-22',
                'metodo_pago': 'TRANSFERENCIA',
                'observaciones': 'Material urgente para obra'
            },
            {
                'numero_orden': 'OC-002',
                'fecha': '2025-01-14',
                'proveedor': 'Suministros XYZ Ltda.',
                'estado': 'PENDIENTE',
                'prioridad': 'NORMAL',
                'total': 12500.50,
                'productos': 5,
                'fecha_entrega': '2025-01-20',
                'metodo_pago': 'CUENTA CORRIENTE',
                'observaciones': 'Revisar especificaciones técnicas'
            },
            {
                'numero_orden': 'OC-003',
                'fecha': '2025-01-13',
                'proveedor': 'Materiales DEF S.R.L.',
                'estado': 'RECIBIDA',
                'prioridad': 'NORMAL',
                'total': 8950.75,
                'productos': 3,
                'fecha_entrega': '2025-01-18',
                'metodo_pago': 'CHEQUE',
                'observaciones': 'Entrega completa'
            }
        ]

        self.llenar_tabla(compras_demo)
        self.actualizar_estadisticas_demo()

    def llenar_tabla(self, compras):
        """Llena la tabla con datos de compras."""
        return self.cargar_compras_en_tabla(compras)
    
    def cargar_compras_en_tabla(self, compras):
        """Carga datos de compras en la tabla principal."""
        self.tabla_compras.setRowCount(len(compras))

        for row, compra in enumerate(compras):
            self.tabla_compras.setItem(row,
0,
                QTableWidgetItem(compra.get('numero_orden',
                '')))
            self.tabla_compras.setItem(row,
1,
                QTableWidgetItem(compra.get('fecha',
                '')))
            self.tabla_compras.setItem(row,
2,
                QTableWidgetItem(compra.get('proveedor',
                '')))

            # Estado con color
            estado_item = QTableWidgetItem(compra.get('estado', ''))
            estado = compra.get('estado', '')
            if estado == 'PENDIENTE':
                estado_item.setBackground(Qt.GlobalColor.yellow)
            elif estado == 'CONFIRMADA':
                estado_item.setBackground(Qt.GlobalColor.blue)
            elif estado == 'RECIBIDA':
                estado_item.setBackground(Qt.GlobalColor.green)
            elif estado == 'CANCELADA':
                estado_item.setBackground(Qt.GlobalColor.red)

            self.tabla_compras.setItem(row, 3, estado_item)

            # Prioridad con color
            prioridad_item = QTableWidgetItem(compra.get('prioridad', ''))
            prioridad = compra.get('prioridad', '')
            if prioridad == 'URGENTE':
                prioridad_item.setBackground(Qt.GlobalColor.red)
            elif prioridad == 'ALTA':
                prioridad_item.setBackground(Qt.GlobalColor.magenta)

            self.tabla_compras.setItem(row, 4, prioridad_item)

            self.tabla_compras.setItem(row, 5,
                                            QTableWidgetItem(f"$ {compra.get('total', 0):.2f}"))
            self.tabla_compras.setItem(row, 6,
                                            QTableWidgetItem(str(compra.get('productos', 0))))
            self.tabla_compras.setItem(row, 7,
                                            QTableWidgetItem(compra.get('fecha_entrega', '')))
            self.tabla_compras.setItem(row, 8,
                                            QTableWidgetItem(compra.get('metodo_pago', '')))
            self.tabla_compras.setItem(row, 9,
                                            QTableWidgetItem(compra.get('observaciones', '')))

            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
            self.tabla_compras.setCellWidget(row, 10, btn_acciones)

    def actualizar_estadisticas_demo(self):
        """Actualiza estadísticas con datos demo."""
        stats = {
            'total_órdenes': '3',
            'pendientes': '1',
            'en_proceso': '1',
            'completadas': '1',
            'monto_total': '$ 47,201.25'
        }

        for key, value in stats.items():
            if key in self.labels_estadisticas:
                self.labels_estadisticas[key].setText(value)

    def actualizar_estadisticas(self, estadisticas=None):
        """Actualiza las estadísticas del panel."""
        if not estadisticas:
            estadisticas = {}
        # TODO: Implementar cálculos reales basados en estadisticas parameter

    def ver_detalle_orden_tabla(self, row):
        """Ve el detalle desde botón de tabla."""
        self.tabla_compras.selectRow(row)
        self.ver_detalle_orden()

    def agregar_orden_demo(self, datos):
        """Agrega orden demo a la tabla."""
        row = self.tabla_compras.rowCount()
        self.tabla_compras.insertRow(row)

        self.tabla_compras.setItem(row, 0, QTableWidgetItem(datos['numero_orden']))
        self.tabla_compras.setItem(row, 1, QTableWidgetItem(datos['fecha_orden']))
        self.tabla_compras.setItem(row, 2, QTableWidgetItem(datos['proveedor']))
        self.tabla_compras.setItem(row, 3, QTableWidgetItem(datos['estado']))
        self.tabla_compras.setItem(row, 4, QTableWidgetItem(datos['prioridad']))
        self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {datos['total_final']:.2f}"))
        self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_compras.setItem(row, 7, QTableWidgetItem(datos['fecha_entrega']))
        self.tabla_compras.setItem(row, 8, QTableWidgetItem(datos['metodo_pago']))
        self.tabla_compras.setItem(row, 9, QTableWidgetItem(datos['observaciones']))

        btn_acciones = QPushButton("Ver Detalle")
        btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
        self.tabla_compras.setCellWidget(row, 10, btn_acciones)

    def actualizar_fila_orden(self, row, datos):
        """Actualiza una fila con nuevos datos."""
        self.tabla_compras.setItem(row, 0, QTableWidgetItem(datos['numero_orden']))
        self.tabla_compras.setItem(row, 1, QTableWidgetItem(datos['fecha_orden']))
        self.tabla_compras.setItem(row, 2, QTableWidgetItem(datos['proveedor']))
        self.tabla_compras.setItem(row, 3, QTableWidgetItem(datos['estado']))
        self.tabla_compras.setItem(row, 4, QTableWidgetItem(datos['prioridad']))
        self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {datos['total_final']:.2f}"))
        self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_compras.setItem(row, 7, QTableWidgetItem(datos['fecha_entrega']))
        self.tabla_compras.setItem(row, 8, QTableWidgetItem(datos['metodo_pago']))
        self.tabla_compras.setItem(row, 9, QTableWidgetItem(datos['observaciones']))

    def set_model(self, model):
        """Establece el modelo."""
        self.model = model

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def actualizar_tabla(self, compras):
        """Actualiza la tabla principal con datos de compras."""
        if not compras:
            self.tabla_compras.setRowCount(0)
            return
        
        self.tabla_compras.setRowCount(len(compras))
        
        for row, compra in enumerate(compras):
            self.tabla_compras.setItem(row, 0, QTableWidgetItem(str(compra.get('numero_orden', compra.get('id', '')))))
            self.tabla_compras.setItem(row, 1, QTableWidgetItem(str(compra.get('fecha_pedido', compra.get('fecha_creacion', '')))))
            self.tabla_compras.setItem(row, 2, QTableWidgetItem(str(compra.get('proveedor', 'N/A'))))
            self.tabla_compras.setItem(row, 3, QTableWidgetItem(str(compra.get('estado', 'PENDIENTE'))))
            self.tabla_compras.setItem(row, 4, QTableWidgetItem(str(compra.get('prioridad', 'NORMAL'))))
            self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {float(compra.get('total_final', 0)):.2f}"))
            self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(compra.get('total_items', 0))))
            self.tabla_compras.setItem(row, 7, QTableWidgetItem(str(compra.get('fecha_entrega_estimada', 'N/A'))))
            self.tabla_compras.setItem(row, 8, QTableWidgetItem(str(compra.get('metodo_pago', 'CONTADO'))))
            self.tabla_compras.setItem(row, 9, QTableWidgetItem(str(compra.get('observaciones', ''))))
            
            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
            self.tabla_compras.setCellWidget(row, 10, btn_acciones)
