"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Vista de Vidrios - Interfaz de gestión de vidrios y cristales
"""

# [LOCK] Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control

# [LOCK] XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added

import logging
import os

# Importar DataSanitizer con manejo de errores
try:
    from utils.data_sanitizer import DataSanitizer

    SANITIZER_AVAILABLE = True
    data_sanitizer = DataSanitizer()
except ImportError:
    print("[INFO] DataSanitizer not available, using basic validation")
    SANITIZER_AVAILABLE = False
    data_sanitizer = None

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


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
        self.logger = logging.getLogger(f"{__name__}.VidriosView")
        self.vidrios_data = []
        self.logger.info("Inicializando vista de vidrios")
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        # Título con icono (emoji diamante)
        title_label = QLabel("🔷 Gestión de Vidrios")
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            padding: 0;
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
        main_splitter.setSizes([200, 800])

        layout.addWidget(main_splitter)

    def crear_panel_izquierdo(self):
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_panel_izquierdo'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Crea el panel izquierdo con filtros y estadísticas."""
        widget = QWidget()
        widget.setMaximumWidth(200)
        layout = QVBoxLayout(widget)

        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QVBoxLayout(filtros_group)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar vidrios...")
        self.search_input.textChanged.connect(self.filtrar_busqueda)
        self.search_input.setMaximumWidth(180)
        filtros_layout.addWidget(QLabel("Búsqueda:"))
        filtros_layout.addWidget(self.search_input)

        # Filtro por tipo
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos",
"Templado",
            "Laminado",
            "Común",
            "Espejo"])
        self.combo_tipo.currentTextChanged.connect(self.aplicar_filtros)
        self.combo_tipo.setMaximumWidth(180)
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.combo_tipo)

        # Filtro por proveedor
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("Todos")
        self.combo_proveedor.currentTextChanged.connect(self.aplicar_filtros)
        self.combo_proveedor.setMaximumWidth(180)
        filtros_layout.addWidget(QLabel("Proveedor:"))
        filtros_layout.addWidget(self.combo_proveedor)

        # Filtro por espesor
        self.combo_espesor = QComboBox()
        self.combo_espesor.addItems(
            ["Todos", "3mm", "4mm", "5mm", "6mm", "8mm", "10mm", "12mm"]
        )
        self.combo_espesor.currentTextChanged.connect(self.aplicar_filtros)
        self.combo_espesor.setMaximumWidth(180)
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
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_panel_derecho'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Crea el panel derecho con la tabla de vidrios."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Crear tabla
        self.tabla_vidrios = QTableWidget()
        self.tabla_vidrios.setColumnCount(10)
        self.tabla_vidrios.setHorizontalHeaderLabels(
            [
                "ID",
                "Código",
                "Descripción",
                "Tipo",
                "Espesor",
                "Proveedor",
                "Precio/m²",
                "Color",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_vidrios.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tabla_vidrios.setColumnWidth(0, 60)
        self.tabla_vidrios.setColumnWidth(1, 100)

        self.tabla_vidrios.setAlternatingRowColors(True)
        self.tabla_vidrios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
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

        # [LOCK] PROTECCIÓN XSS: Sanitizar entrada de búsqueda
        if SANITIZER_AVAILABLE and data_sanitizer and termino:
            termino = data_sanitizer.sanitize_string(termino)
            self.logger.debug(f"Término de búsqueda sanitizado: {termino}")

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
            # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
            # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
            # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

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
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_tabla'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza la tabla con los datos de vidrios."""
        self.vidrios_data = vidrios
        self.tabla_vidrios.setRowCount(len(vidrios))

        for row, vidrio in enumerate(vidrios):
            self.tabla_vidrios.setItem(
                row, 0, QTableWidgetItem(str(vidrio.get("id", "")))
            )
            self.tabla_vidrios.setItem(
                row, 1, QTableWidgetItem(str(vidrio.get("codigo", "")))
            )
            self.tabla_vidrios.setItem(
                row, 2, QTableWidgetItem(str(vidrio.get("descripcion", "")))
            )
            self.tabla_vidrios.setItem(
                row, 3, QTableWidgetItem(str(vidrio.get("tipo", "")))
            )
            self.tabla_vidrios.setItem(
                row, 4, QTableWidgetItem(f"{vidrio.get('espesor', '')}mm")
            )
            self.tabla_vidrios.setItem(
                row, 5, QTableWidgetItem(str(vidrio.get("proveedor", "")))
            )
            self.tabla_vidrios.setItem(
                row, 6, QTableWidgetItem(f"${vidrio.get('precio_m2', 0):.2f}")
            )
            self.tabla_vidrios.setItem(
                row, 7, QTableWidgetItem(str(vidrio.get("color", "")))
            )
            self.tabla_vidrios.setItem(
                row, 8, QTableWidgetItem(str(vidrio.get("estado", "")))
            )

            # Botones de acción
            self.crear_botones_accion(row, vidrio.get("id"))

    def crear_botones_accion(self, row, vidrio_id):
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_botones_accion'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

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
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza las estadísticas en el panel izquierdo."""
        self.label_total.setText(
            f"Total vidrios: {estadisticas.get('total_vidrios', 0)}"
        )
        self.label_tipos.setText(
            f"Tipos disponibles: {estadisticas.get('tipos_disponibles', 0)}"
        )
        self.label_proveedores.setText(
            f"Proveedores activos: {estadisticas.get('proveedores_activos', 0)}"
        )
        self.label_valor.setText(
            f"Valor total: ${estadisticas.get('valor_total_inventario', 0):.2f}"
        )

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
                datos["vidrio_id"],
                datos["obra_id"],
                datos["metros_cuadrados"],
                datos["medidas_especificas"],
            )

    def abrir_dialogo_crear_pedido(self):
        """Abre el diálogo para crear un pedido."""
        if not self.vidrios_data:
            # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
            # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
            # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

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
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este vidrio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_datos'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Solicita actualización de datos."""
        self.progress_bar.setVisible(True)
        self.aplicar_filtros()
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        self.logger.info(f"Mensaje mostrado: {mensaje}")
        QMessageBox.information(self, "Vidrios", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        self.logger.error(f"Error mostrado al usuario: {mensaje}")
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
            self.input_dimensiones.setText(
                str(self.vidrio.get("dimensiones_disponibles", ""))
            )
            self.combo_estado.setCurrentText(str(self.vidrio.get("estado", "ACTIVO")))
            self.input_observaciones.setPlainText(
                str(self.vidrio.get("observaciones", ""))
            )

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        codigo = self.input_codigo.text()
        descripcion = self.input_descripcion.text()
        proveedor = self.input_proveedor.text()
        color = self.input_color.text()
        tratamiento = self.input_tratamiento.text()
        dimensiones = self.input_dimensiones.text()
        observaciones = self.input_observaciones.toPlainText()

        if SANITIZER_AVAILABLE and data_sanitizer:
            codigo = data_sanitizer.sanitize_string(codigo)
            descripcion = data_sanitizer.sanitize_string(descripcion)
            proveedor = data_sanitizer.sanitize_string(proveedor)
            color = data_sanitizer.sanitize_string(color)
            tratamiento = data_sanitizer.sanitize_string(tratamiento)
            dimensiones = data_sanitizer.sanitize_string(dimensiones)
            observaciones = data_sanitizer.sanitize_string(observaciones)

        return {
            "codigo": codigo,
            "descripcion": descripcion,
            "tipo": self.combo_tipo.currentText(),
            "espesor": self.input_espesor.value(),
            "proveedor": proveedor,
            "precio_m2": self.input_precio.value(),
            "color": color,
            "tratamiento": tratamiento,
            "dimensiones_disponibles": dimensiones,
            "estado": self.combo_estado.currentText(),
            "observaciones": observaciones,
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
                vidrio.get("id"),
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
            "medidas_especificas": self.input_medidas.toPlainText(),
        }


class CrearPedidoDialog(QDialog):
    """Diálogo para crear pedido de vidrios."""

    def __init__(self, parent=None, vidrios_data=None):
        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

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
        self.tabla_vidrios.setHorizontalHeaderLabels(
            ["Vidrio", "Precio/m²", "Cantidad", "Seleccionar"]
        )
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
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_tabla_vidrios'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza la tabla de vidrios disponibles."""
        self.tabla_vidrios.setRowCount(len(self.vidrios_data))

        for row, vidrio in enumerate(self.vidrios_data):
            self.tabla_vidrios.setItem(
                row,
                0,
                QTableWidgetItem(
                    f"{vidrio.get('codigo', '')} - {vidrio.get('descripcion', '')}"
                ),
            )
            self.tabla_vidrios.setItem(
                row, 1, QTableWidgetItem(f"${vidrio.get('precio_m2', 0):.2f}")
            )

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
                vidrios_lista.append(
                    {
                        "vidrio_id": vidrio.get("id"),
                        "metros_cuadrados": spinbox.value(),
                        "precio_m2": vidrio.get("precio_m2", 0),
                    }
                )

        return {
            "obra_id": self.input_obra_id.value(),
            "proveedor": self.input_proveedor.text(),
            "vidrios_lista": vidrios_lista,
        }
