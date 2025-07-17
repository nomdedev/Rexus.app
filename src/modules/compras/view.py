"""
Vista de Compras

Interfaz de usuario para el módulo de compras.
"""

from datetime import date, datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ComprasView(QWidget):
    """Vista principal del módulo de compras."""

    # Señales
    orden_creada = pyqtSignal(dict)
    orden_actualizada = pyqtSignal(int, str)
    busqueda_realizada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título removido según solicitado

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Crear tabs
        tab_widget = QTabWidget()
        
        # Pestaña de compras
        panel_compras = self.crear_panel_compras()
        tab_widget.addTab(panel_compras, "📋 Órdenes de Compra")
        
        # Pestaña de estadísticas
        panel_estadisticas = self.crear_panel_estadisticas()
        tab_widget.addTab(panel_estadisticas, "📊 Estadísticas")
        
        layout.addWidget(tab_widget)

        # Aplicar estilo general
        self.aplicar_estilo()

    def crear_panel_control(self):
        """Crea el panel de control superior."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón Nueva Orden
        self.btn_nueva_orden = QPushButton("Nueva Orden")
        self.btn_nueva_orden.setIcon(QIcon("📋"))
        self.btn_nueva_orden.clicked.connect(self.abrir_dialog_nueva_orden)

        # Búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText(
            "Buscar por proveedor o número de orden..."
        )
        self.input_busqueda.returnPressed.connect(self.buscar_compras)

        # Filtro por estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(
            ["Todos", "PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]
        )
        self.combo_estado.currentTextChanged.connect(self.buscar_compras)

        # Filtro por fechas
        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addMonths(-3))
        self.date_desde.setCalendarPopup(True)
        self.date_desde.dateChanged.connect(self.buscar_compras)

        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.dateChanged.connect(self.buscar_compras)

        # Botón buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_compras)

        # Botón actualizar
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)

        # Agregar widgets
        layout.addWidget(self.btn_nueva_orden)
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input_busqueda)
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)
        layout.addWidget(QLabel("Desde:"))
        layout.addWidget(self.date_desde)
        layout.addWidget(QLabel("Hasta:"))
        layout.addWidget(self.date_hasta)
        layout.addWidget(self.btn_buscar)
        layout.addWidget(self.btn_actualizar)

        return panel

    def crear_panel_compras(self):
        """Crea el panel de lista de compras."""
        panel = QGroupBox("Órdenes de Compra")
        layout = QVBoxLayout(panel)

        # Tabla de compras
        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(10)
        self.tabla_compras.setHorizontalHeaderLabels(
            [
                "ID",
                "Proveedor",
                "Número Orden",
                "Fecha Pedido",
                "Fecha Entrega",
                "Estado",
                "Total",
                "Usuario",
                "Fecha Creación",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_compras.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.tabla_compras.setAlternatingRowColors(True)
        self.tabla_compras.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_compras.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Estilo de la tabla
        self.tabla_compras.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e0e0;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 12px;
                font-weight: bold;
                color: #495057;
            }
        """)

        layout.addWidget(self.tabla_compras)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas."""
        panel = QGroupBox("Estadísticas")
        layout = QVBoxLayout(panel)

        # Estadísticas generales
        self.stats_frame = QFrame()
        self.stats_frame.setFrameStyle(QFrame.Shape.Box)
        self.stats_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        stats_layout = QVBoxLayout(self.stats_frame)

        # Labels de estadísticas
        self.lbl_total_ordenes = QLabel("Total Órdenes: 0")
        self.lbl_ordenes_pendientes = QLabel("Pendientes: 0")
        self.lbl_ordenes_aprobadas = QLabel("Aprobadas: 0")
        self.lbl_monto_total = QLabel("Monto Total: $0.00")

        # Estilo para labels
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                margin: 2px;
            }
        """

        for label in [
            self.lbl_total_ordenes,
            self.lbl_ordenes_pendientes,
            self.lbl_ordenes_aprobadas,
            self.lbl_monto_total,
        ]:
            label.setStyleSheet(label_style)
            stats_layout.addWidget(label)

        layout.addWidget(self.stats_frame)

        # Gráfico de estados (texto por ahora)
        self.estados_frame = QFrame()
        self.estados_frame.setFrameStyle(QFrame.Shape.Box)
        self.estados_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        estados_layout = QVBoxLayout(self.estados_frame)

        titulo_estados = QLabel("Distribución por Estado")
        titulo_estados.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        titulo_estados.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        estados_layout.addWidget(titulo_estados)

        self.texto_estados = QTextEdit()
        self.texto_estados.setMaximumHeight(150)
        self.texto_estados.setReadOnly(True)
        self.texto_estados.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        estados_layout.addWidget(self.texto_estados)

        layout.addWidget(self.estados_frame)

        return panel

    def aplicar_estilo(self):
        """Aplica el estilo general al widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                max-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
                font-size: 14px;
            }
        """)

    def abrir_dialog_nueva_orden(self):
        """Abre el diálogo para crear una nueva orden."""
        dialog = DialogNuevaOrden(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            self.orden_creada.emit(datos)

    def buscar_compras(self):
        """Ejecuta la búsqueda de compras."""
        filtros = {
            "proveedor": self.input_busqueda.text(),
            "estado": self.combo_estado.currentText()
            if self.combo_estado.currentText() != "Todos"
            else "",
            "fecha_inicio": self.date_desde.date().toPython(),
            "fecha_fin": self.date_hasta.date().toPython(),
        }
        self.busqueda_realizada.emit(filtros)

    def cargar_compras_en_tabla(self, compras):
        """Carga las compras en la tabla."""
        self.tabla_compras.setRowCount(len(compras))

        for row, compra in enumerate(compras):
            # Datos básicos
            self.tabla_compras.setItem(
                row, 0, QTableWidgetItem(str(compra.get("id", "")))
            )
            self.tabla_compras.setItem(
                row, 1, QTableWidgetItem(str(compra.get("proveedor", "")))
            )
            self.tabla_compras.setItem(
                row, 2, QTableWidgetItem(str(compra.get("numero_orden", "")))
            )
            self.tabla_compras.setItem(
                row, 3, QTableWidgetItem(str(compra.get("fecha_pedido", "")))
            )
            self.tabla_compras.setItem(
                row, 4, QTableWidgetItem(str(compra.get("fecha_entrega_estimada", "")))
            )

            # Estado con color
            estado_item = QTableWidgetItem(str(compra.get("estado", "")))
            estado = compra.get("estado", "")
            if estado == "PENDIENTE":
                estado_item.setBackground(Qt.GlobalColor.yellow)
            elif estado == "APROBADA":
                estado_item.setBackground(Qt.GlobalColor.cyan)
            elif estado == "RECIBIDA":
                estado_item.setBackground(Qt.GlobalColor.green)
            elif estado == "CANCELADA":
                estado_item.setBackground(Qt.GlobalColor.red)

            self.tabla_compras.setItem(row, 5, estado_item)

            # Total
            total = compra.get("total_final", 0)
            self.tabla_compras.setItem(row, 6, QTableWidgetItem(f"${total:,.2f}"))

            # Usuario y fecha
            self.tabla_compras.setItem(
                row, 7, QTableWidgetItem(str(compra.get("usuario_creacion", "")))
            )
            self.tabla_compras.setItem(
                row, 8, QTableWidgetItem(str(compra.get("fecha_creacion", "")))
            )

            # Botones de acción
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("background-color: #f39c12; color: white;")
            btn_editar.clicked.connect(
                lambda checked, id=compra.get("id"): self.editar_orden(id)
            )
            self.tabla_compras.setCellWidget(row, 9, btn_editar)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas mostradas."""
        self.lbl_total_ordenes.setText(
            f"Total Órdenes: {stats.get('total_ordenes', 0)}"
        )
        self.lbl_monto_total.setText(
            f"Monto Total: ${stats.get('monto_total', 0):,.2f}"
        )

        # Actualizar contadores por estado
        estados_data = stats.get("ordenes_por_estado", [])
        pendientes = next(
            (x["cantidad"] for x in estados_data if x["estado"] == "PENDIENTE"), 0
        )
        aprobadas = next(
            (x["cantidad"] for x in estados_data if x["estado"] == "APROBADA"), 0
        )

        self.lbl_ordenes_pendientes.setText(f"Pendientes: {pendientes}")
        self.lbl_ordenes_aprobadas.setText(f"Aprobadas: {aprobadas}")

        # Actualizar texto de estados
        texto_estados = "Distribución por Estado:\n\n"
        for estado_data in estados_data:
            texto_estados += f"• {estado_data['estado']}: {estado_data['cantidad']}\n"

        self.texto_estados.setPlainText(texto_estados)

    def editar_orden(self, orden_id):
        """Edita una orden existente."""
        # Por ahora solo cambiar estado
        estados = ["PENDIENTE", "APROBADA", "RECIBIDA", "CANCELADA"]

        # Crear un diálogo simple para cambiar estado
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Estado")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        combo_estado = QComboBox()
        combo_estado.addItems(estados)
        layout.addWidget(QLabel("Nuevo Estado:"))
        layout.addWidget(combo_estado)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevo_estado = combo_estado.currentText()
            self.orden_actualizada.emit(orden_id, nuevo_estado)

    def actualizar_datos(self):
        """Actualiza los datos de la vista."""
        self.buscar_compras()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogNuevaOrden(QDialog):
    """Diálogo para crear una nueva orden de compra."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Orden de Compra")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Campos
        self.input_proveedor = QLineEdit()
        self.input_numero_orden = QLineEdit()
        self.date_pedido = QDateEdit()
        self.date_pedido.setDate(QDate.currentDate())
        self.date_pedido.setCalendarPopup(True)

        self.date_entrega = QDateEdit()
        self.date_entrega.setDate(QDate.currentDate().addDays(30))
        self.date_entrega.setCalendarPopup(True)

        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["PENDIENTE", "APROBADA"])

        self.input_descuento = QDoubleSpinBox()
        self.input_descuento.setRange(0, 999999)
        self.input_descuento.setDecimals(2)
        self.input_descuento.setSuffix(" $")

        self.input_impuestos = QDoubleSpinBox()
        self.input_impuestos.setRange(0, 999999)
        self.input_impuestos.setDecimals(2)
        self.input_impuestos.setSuffix(" $")

        self.input_observaciones = QTextEdit()
        self.input_observaciones.setMaximumHeight(100)

        # Agregar campos al formulario
        form_layout.addRow("Proveedor:", self.input_proveedor)
        form_layout.addRow("Número de Orden:", self.input_numero_orden)
        form_layout.addRow("Fecha Pedido:", self.date_pedido)
        form_layout.addRow("Fecha Entrega:", self.date_entrega)
        form_layout.addRow("Estado:", self.combo_estado)
        form_layout.addRow("Descuento:", self.input_descuento)
        form_layout.addRow("Impuestos:", self.input_impuestos)
        form_layout.addRow("Observaciones:", self.input_observaciones)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Aplicar estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
                outline: none;
            }
        """)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "proveedor": self.input_proveedor.text(),
            "numero_orden": self.input_numero_orden.text(),
            "fecha_pedido": self.date_pedido.date().toPython(),
            "fecha_entrega_estimada": self.date_entrega.date().toPython(),
            "estado": self.combo_estado.currentText(),
            "descuento": self.input_descuento.value(),
            "impuestos": self.input_impuestos.value(),
            "observaciones": self.input_observaciones.toPlainText(),
            "usuario_creacion": "Usuario Actual",  # TODO: Obtener del sistema
        }
