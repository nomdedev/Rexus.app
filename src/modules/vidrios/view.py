"""Vista de Vidrios"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
    QHeaderView, QFrame, QGridLayout, QSplitter, QTabWidget,
    QMessageBox, QProgressBar, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
import os


class VidriosView(QWidget):
    
    buscar_requested = pyqtSignal(str)
    agregar_requested = pyqtSignal(dict)
    editar_requested = pyqtSignal(int, dict)
    eliminar_requested = pyqtSignal(int)
    asignar_obra_requested = pyqtSignal(int, int, float, str)
    crear_pedido_requested = pyqtSignal(int, str, list)
    filtrar_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.vidrios_data = []
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Título con icono
        title_label = QLabel("🪟 Gestión de Vidrios")
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 10px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botones principales
        self.btn_agregar = QPushButton("➕ Agregar Vidrio")
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        header_layout.addWidget(self.btn_agregar)
        
        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        header_layout.addWidget(self.btn_actualizar)
        
        layout.addLayout(header_layout)
        
        # Crear splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Filtros y estadísticas
        left_panel = self.crear_panel_izquierdo()
        main_splitter.addWidget(left_panel)
        
        # Panel derecho - Tabla y controles
        right_panel = self.crear_panel_derecho()
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        main_splitter.setSizes([300, 700])
        
        layout.addWidget(main_splitter)

    def crear_panel_izquierdo(self):
        """Crea el panel izquierdo con filtros y estadísticas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QVBoxLayout(filtros_group)
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar vidrios...")
        self.search_input.textChanged.connect(self.filtrar_busqueda)
        filtros_layout.addWidget(QLabel("Búsqueda:"))
        filtros_layout.addWidget(self.search_input)
        
        # Filtro por tipo
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Templado", "Laminado", "Común", "Espejo"])
        self.combo_tipo.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.combo_tipo)
        
        # Filtro por proveedor
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("Todos")
        self.combo_proveedor.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Proveedor:"))
        filtros_layout.addWidget(self.combo_proveedor)
        
        # Filtro por espesor
        self.combo_espesor = QComboBox()
        self.combo_espesor.addItems(["Todos", "3mm", "4mm", "5mm", "6mm", "8mm", "10mm", "12mm"])
        self.combo_espesor.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(QLabel("Espesor:"))
        filtros_layout.addWidget(self.combo_espesor)
        
        # Botón limpiar filtros
        btn_limpiar = QPushButton("🧹 Limpiar Filtros")
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        filtros_layout.addWidget(btn_limpiar)
        
        layout.addWidget(filtros_group)
        
        # Estadísticas
        stats_group = QGroupBox("Estadísticas")
        stats_layout = QVBoxLayout(stats_group)
        
        self.label_total = QLabel("Total vidrios: 0")
        self.label_tipos = QLabel("Tipos disponibles: 0")
        self.label_proveedores = QLabel("Proveedores activos: 0")
        self.label_valor = QLabel("Valor total: $0.00")
        
        stats_layout.addWidget(self.label_total)
        stats_layout.addWidget(self.label_tipos)
        stats_layout.addWidget(self.label_proveedores)
        stats_layout.addWidget(self.label_valor)
        
        layout.addWidget(stats_group)
        
        # Acciones rápidas
        acciones_group = QGroupBox("Acciones Rápidas")
        acciones_layout = QVBoxLayout(acciones_group)
        
        self.btn_asignar_obra = QPushButton("📋 Asignar a Obra")
        self.btn_asignar_obra.clicked.connect(self.abrir_dialogo_asignar_obra)
        acciones_layout.addWidget(self.btn_asignar_obra)
        
        self.btn_crear_pedido = QPushButton("📄 Crear Pedido")
        self.btn_crear_pedido.clicked.connect(self.abrir_dialogo_crear_pedido)
        acciones_layout.addWidget(self.btn_crear_pedido)
        
        layout.addWidget(acciones_group)
        
        layout.addStretch()
        
        return widget

    def crear_panel_derecho(self):
        """Crea el panel derecho con la tabla de vidrios."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Crear tabla
        self.tabla_vidrios = QTableWidget()
        self.tabla_vidrios.setColumnCount(10)
        self.tabla_vidrios.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Tipo", "Espesor", 
            "Proveedor", "Precio/m²", "Color", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tabla_vidrios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tabla_vidrios.setColumnWidth(0, 60)
        self.tabla_vidrios.setColumnWidth(1, 100)
        
        self.tabla_vidrios.setAlternatingRowColors(True)
        self.tabla_vidrios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_vidrios.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: 1px solid #2980b9;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.tabla_vidrios)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return widget

    def setup_timer(self):
        """Configura el timer para búsqueda con retraso."""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.realizar_busqueda)

    def filtrar_busqueda(self):
        """Filtra la búsqueda con retraso."""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms de retraso

    def realizar_busqueda(self):
        """Realiza la búsqueda."""
        termino = self.search_input.text().strip()
        if termino:
            self.buscar_requested.emit(termino)
        else:
            self.aplicar_filtros()

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        filtros = {}
        
        if self.combo_tipo.currentText() != "Todos":
            filtros["tipo"] = self.combo_tipo.currentText()
            
        if self.combo_proveedor.currentText() != "Todos":
            filtros["proveedor"] = self.combo_proveedor.currentText()
            
        if self.combo_espesor.currentText() != "Todos":
            filtros["espesor"] = self.combo_espesor.currentText().replace("mm", "")
            
        self.filtrar_requested.emit(filtros)

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.search_input.clear()
        self.combo_tipo.setCurrentText("Todos")
        self.combo_proveedor.setCurrentText("Todos")
        self.combo_espesor.setCurrentText("Todos")
        self.aplicar_filtros()

    def actualizar_tabla(self, vidrios):
        """Actualiza la tabla con los datos de vidrios."""
        self.vidrios_data = vidrios
        self.tabla_vidrios.setRowCount(len(vidrios))
        
        for row, vidrio in enumerate(vidrios):
            self.tabla_vidrios.setItem(row, 0, QTableWidgetItem(str(vidrio.get("id", ""))))
            self.tabla_vidrios.setItem(row, 1, QTableWidgetItem(str(vidrio.get("codigo", ""))))
            self.tabla_vidrios.setItem(row, 2, QTableWidgetItem(str(vidrio.get("descripcion", ""))))
            self.tabla_vidrios.setItem(row, 3, QTableWidgetItem(str(vidrio.get("tipo", ""))))
            self.tabla_vidrios.setItem(row, 4, QTableWidgetItem(f"{vidrio.get('espesor', '')}mm"))
            self.tabla_vidrios.setItem(row, 5, QTableWidgetItem(str(vidrio.get("proveedor", ""))))
            self.tabla_vidrios.setItem(row, 6, QTableWidgetItem(f"${vidrio.get('precio_m2', 0):.2f}"))
            self.tabla_vidrios.setItem(row, 7, QTableWidgetItem(str(vidrio.get("color", ""))))
            self.tabla_vidrios.setItem(row, 8, QTableWidgetItem(str(vidrio.get("estado", ""))))
            
            # Botones de acción
            self.crear_botones_accion(row, vidrio.get("id"))

    def crear_botones_accion(self, row, vidrio_id):
        """Crea botones de acción para cada fila."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar")
        btn_editar.setMaximumWidth(30)
        btn_editar.clicked.connect(lambda: self.abrir_dialogo_editar(vidrio_id))
        
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar")
        btn_eliminar.setMaximumWidth(30)
        btn_eliminar.clicked.connect(lambda: self.confirmar_eliminar(vidrio_id))
        
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)
        
        self.tabla_vidrios.setCellWidget(row, 9, widget)

    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas en el panel izquierdo."""
        self.label_total.setText(f"Total vidrios: {estadisticas.get('total_vidrios', 0)}")
        self.label_tipos.setText(f"Tipos disponibles: {estadisticas.get('tipos_disponibles', 0)}")
        self.label_proveedores.setText(f"Proveedores activos: {estadisticas.get('proveedores_activos', 0)}")
        self.label_valor.setText(f"Valor total: ${estadisticas.get('valor_total_inventario', 0):.2f}")

    def abrir_dialogo_agregar(self):
        """Abre el diálogo para agregar un nuevo vidrio."""
        dialogo = VidrioDialog(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            self.agregar_requested.emit(datos)

    def abrir_dialogo_editar(self, vidrio_id):
        """Abre el diálogo para editar un vidrio existente."""
        vidrio = self.obtener_vidrio_por_id(vidrio_id)
        if vidrio:
            dialogo = VidrioDialog(self, vidrio)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos = dialogo.obtener_datos()
                self.editar_requested.emit(vidrio_id, datos)

    def abrir_dialogo_asignar_obra(self):
        """Abre el diálogo para asignar vidrio a obra."""
        if not self.vidrios_data:
            QMessageBox.warning(self, "Advertencia", "No hay vidrios disponibles")
            return
            
        dialogo = AsignarObraDialog(self, self.vidrios_data)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            self.asignar_obra_requested.emit(
                datos["vidrio_id"], datos["obra_id"], 
                datos["metros_cuadrados"], datos["medidas_especificas"]
            )

    def abrir_dialogo_crear_pedido(self):
        """Abre el diálogo para crear un pedido."""
        if not self.vidrios_data:
            QMessageBox.warning(self, "Advertencia", "No hay vidrios disponibles")
            return
            
        dialogo = CrearPedidoDialog(self, self.vidrios_data)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            self.crear_pedido_requested.emit(
                datos["obra_id"], datos["proveedor"], datos["vidrios_lista"]
            )

    def confirmar_eliminar(self, vidrio_id):
        """Confirma la eliminación de un vidrio."""
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este vidrio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.eliminar_requested.emit(vidrio_id)

    def obtener_vidrio_por_id(self, vidrio_id):
        """Obtiene un vidrio por su ID."""
        for vidrio in self.vidrios_data:
            if vidrio.get("id") == vidrio_id:
                return vidrio
        return None

    def actualizar_datos(self):
        """Solicita actualización de datos."""
        self.progress_bar.setVisible(True)
        self.aplicar_filtros()
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        QMessageBox.information(self, "Vidrios", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        QMessageBox.critical(self, "Error - Vidrios", mensaje)


class VidrioDialog(QDialog):
    """Diálogo para agregar/editar vidrios."""
    
    def __init__(self, parent=None, vidrio=None):
        super().__init__(parent)
        self.vidrio = vidrio
        self.init_ui()
        if vidrio:
            self.cargar_datos()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Agregar Vidrio" if not self.vidrio else "Editar Vidrio")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.input_codigo = QLineEdit()
        self.input_descripcion = QLineEdit()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Templado", "Laminado", "Común", "Espejo"])
        self.input_espesor = QDoubleSpinBox()
        self.input_espesor.setSuffix(" mm")
        self.input_espesor.setRange(1, 50)
        self.input_proveedor = QLineEdit()
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setPrefix("$")
        self.input_precio.setRange(0, 999999)
        self.input_color = QLineEdit()
        self.input_tratamiento = QLineEdit()
        self.input_dimensiones = QLineEdit()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["ACTIVO", "INACTIVO", "DESCONTINUADO"])
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setMaximumHeight(80)
        
        form_layout.addRow("Código:", self.input_codigo)
        form_layout.addRow("Descripción:", self.input_descripcion)
        form_layout.addRow("Tipo:", self.combo_tipo)
        form_layout.addRow("Espesor:", self.input_espesor)
        form_layout.addRow("Proveedor:", self.input_proveedor)
        form_layout.addRow("Precio/m²:", self.input_precio)
        form_layout.addRow("Color:", self.input_color)
        form_layout.addRow("Tratamiento:", self.input_tratamiento)
        form_layout.addRow("Dimensiones:", self.input_dimensiones)
        form_layout.addRow("Estado:", self.combo_estado)
        form_layout.addRow("Observaciones:", self.input_observaciones)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def cargar_datos(self):
        """Carga los datos del vidrio en el formulario."""
        if self.vidrio:
            self.input_codigo.setText(str(self.vidrio.get("codigo", "")))
            self.input_descripcion.setText(str(self.vidrio.get("descripcion", "")))
            self.combo_tipo.setCurrentText(str(self.vidrio.get("tipo", "")))
            self.input_espesor.setValue(float(self.vidrio.get("espesor", 0)))
            self.input_proveedor.setText(str(self.vidrio.get("proveedor", "")))
            self.input_precio.setValue(float(self.vidrio.get("precio_m2", 0)))
            self.input_color.setText(str(self.vidrio.get("color", "")))
            self.input_tratamiento.setText(str(self.vidrio.get("tratamiento", "")))
            self.input_dimensiones.setText(str(self.vidrio.get("dimensiones_disponibles", "")))
            self.combo_estado.setCurrentText(str(self.vidrio.get("estado", "ACTIVO")))
            self.input_observaciones.setPlainText(str(self.vidrio.get("observaciones", "")))

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "codigo": self.input_codigo.text(),
            "descripcion": self.input_descripcion.text(),
            "tipo": self.combo_tipo.currentText(),
            "espesor": self.input_espesor.value(),
            "proveedor": self.input_proveedor.text(),
            "precio_m2": self.input_precio.value(),
            "color": self.input_color.text(),
            "tratamiento": self.input_tratamiento.text(),
            "dimensiones_disponibles": self.input_dimensiones.text(),
            "estado": self.combo_estado.currentText(),
            "observaciones": self.input_observaciones.toPlainText()
        }


class AsignarObraDialog(QDialog):
    """Diálogo para asignar vidrio a obra."""
    
    def __init__(self, parent=None, vidrios_data=None):
        super().__init__(parent)
        self.vidrios_data = vidrios_data or []
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Asignar Vidrio a Obra")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.combo_vidrio = QComboBox()
        for vidrio in self.vidrios_data:
            self.combo_vidrio.addItem(
                f"{vidrio.get('codigo', '')} - {vidrio.get('descripcion', '')}", 
                vidrio.get('id')
            )
        
        self.input_obra_id = QSpinBox()
        self.input_obra_id.setRange(1, 999999)
        
        self.input_metros = QDoubleSpinBox()
        self.input_metros.setSuffix(" m²")
        self.input_metros.setRange(0.01, 999999)
        
        self.input_medidas = QTextEdit()
        self.input_medidas.setMaximumHeight(80)
        
        form_layout.addRow("Vidrio:", self.combo_vidrio)
        form_layout.addRow("ID Obra:", self.input_obra_id)
        form_layout.addRow("Metros cuadrados:", self.input_metros)
        form_layout.addRow("Medidas específicas:", self.input_medidas)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "vidrio_id": self.combo_vidrio.currentData(),
            "obra_id": self.input_obra_id.value(),
            "metros_cuadrados": self.input_metros.value(),
            "medidas_especificas": self.input_medidas.toPlainText()
        }


class CrearPedidoDialog(QDialog):
    """Diálogo para crear pedido de vidrios."""
    
    def __init__(self, parent=None, vidrios_data=None):
        super().__init__(parent)
        self.vidrios_data = vidrios_data or []
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Crear Pedido de Vidrios")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.input_obra_id = QSpinBox()
        self.input_obra_id.setRange(1, 999999)
        
        self.input_proveedor = QLineEdit()
        
        form_layout.addRow("ID Obra:", self.input_obra_id)
        form_layout.addRow("Proveedor:", self.input_proveedor)
        
        layout.addLayout(form_layout)
        
        # Tabla de vidrios
        self.tabla_vidrios = QTableWidget()
        self.tabla_vidrios.setColumnCount(4)
        self.tabla_vidrios.setHorizontalHeaderLabels(["Vidrio", "Precio/m²", "Cantidad", "Seleccionar"])
        self.actualizar_tabla_vidrios()
        
        layout.addWidget(QLabel("Seleccionar vidrios:"))
        layout.addWidget(self.tabla_vidrios)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def actualizar_tabla_vidrios(self):
        """Actualiza la tabla de vidrios disponibles."""
        self.tabla_vidrios.setRowCount(len(self.vidrios_data))
        
        for row, vidrio in enumerate(self.vidrios_data):
            self.tabla_vidrios.setItem(row, 0, QTableWidgetItem(f"{vidrio.get('codigo', '')} - {vidrio.get('descripcion', '')}"))
            self.tabla_vidrios.setItem(row, 1, QTableWidgetItem(f"${vidrio.get('precio_m2', 0):.2f}"))
            
            spinbox = QDoubleSpinBox()
            spinbox.setSuffix(" m²")
            spinbox.setRange(0, 999999)
            self.tabla_vidrios.setCellWidget(row, 2, spinbox)
            
            checkbox = QCheckBox()
            self.tabla_vidrios.setCellWidget(row, 3, checkbox)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        vidrios_lista = []
        
        for row in range(self.tabla_vidrios.rowCount()):
            checkbox = self.tabla_vidrios.cellWidget(row, 3)
            if checkbox.isChecked():
                spinbox = self.tabla_vidrios.cellWidget(row, 2)
                vidrio = self.vidrios_data[row]
                vidrios_lista.append({
                    "vidrio_id": vidrio.get("id"),
                    "metros_cuadrados": spinbox.value(),
                    "precio_m2": vidrio.get("precio_m2", 0)
                })
        
        return {
            "obra_id": self.input_obra_id.value(),
            "proveedor": self.input_proveedor.text(),
            "vidrios_lista": vidrios_lista
        }
