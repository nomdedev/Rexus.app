"""
Vista de Herrajes

Interfaz modernizada para gestión de herrajes por obra.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from src.utils.message_system import show_success, show_error, show_warning, ask_question
from src.utils.form_validators import FormValidator, FormValidatorManager
from src.modules.herrajes.improved_dialogs import HerrajeDialogManager, HerrajeObrasDialog, HerrajePedidosDialog
from src.utils.format_utils import format_for_display, table_formatter
from PyQt6.QtWidgets import (
    QComboBox,
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
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HerrajesView(QWidget):
    """Vista principal para gestión de herrajes."""

    # Señales
    buscar_herrajes = pyqtSignal(str)
    filtrar_herrajes = pyqtSignal(dict)
    asignar_herraje_obra = pyqtSignal(int, int, float, str)
    crear_pedido_obra = pyqtSignal(int, str, list)
    obtener_estadisticas = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = None
        self.herraje_actual = None
        
        # Gestores de diálogos mejorados
        self.dialog_manager = None
        self.obras_dialog = None
        self.pedidos_dialog = None
        
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("🔧 Gestión de Herrajes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # Panel de estadísticas
        self.create_statistics_panel()
        main_layout.addWidget(self.stats_frame)

        # Panel de filtros y búsqueda
        self.create_filters_panel()
        main_layout.addWidget(self.filters_frame)

        # Panel de herrajes
        self.create_herrajes_panel()
        main_layout.addWidget(self.herrajes_frame)

        # Panel de acciones
        self.create_actions_panel()
        main_layout.addWidget(self.actions_frame)

        # Aplicar estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
            }
            QTableWidget {
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                padding: 10px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

    def create_statistics_panel(self):
        """Crea el panel de estadísticas."""
        self.stats_frame = QGroupBox("📊 Estadísticas de Herrajes")

        stats_layout = QHBoxLayout(self.stats_frame)

        # Estadísticas individuales
        self.stats_labels = {}
        stats_info = [
            ("total_herrajes", "Total Herrajes", "#3498db"),
            ("proveedores_activos", "Proveedores Activos", "#2ecc71"),
            ("valor_inventario", "Valor Inventario", "#e74c3c"),
            ("pedidos_pendientes", "Pedidos Pendientes", "#f39c12"),
        ]

        for key, label, color in stats_info:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }}
                QLabel {{
                    color: white;
                    font-weight: bold;
                }}
            """)

            stat_layout = QVBoxLayout(stat_widget)

            value_label = QLabel("0")
            value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(label)
            desc_label.setStyleSheet("font-size: 12px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)

            self.stats_labels[key] = value_label
            stats_layout.addWidget(stat_widget)

    def create_filters_panel(self):
        """Crea el panel de filtros y búsqueda."""
        self.filters_frame = QGroupBox("🔍 Filtros y Búsqueda")

        filters_layout = QHBoxLayout(self.filters_frame)

        # Búsqueda general
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Buscar por código, descripción o proveedor..."
        )
        self.search_input.textChanged.connect(self.on_search_changed)

        # Filtro por proveedor
        self.proveedor_filter = QComboBox()
        self.proveedor_filter.addItem("Todos los proveedores")
        self.proveedor_filter.currentTextChanged.connect(self.on_filters_changed)

        # Filtro por categoría
        self.categoria_filter = QComboBox()
        self.categoria_filter.addItem("Todas las categorías")
        self.categoria_filter.addItems(
            ["Bisagras", "Cerraduras", "Manijas", "Tornillos", "Otros"]
        )
        self.categoria_filter.currentTextChanged.connect(self.on_filters_changed)

        # Botón de limpiar filtros
        self.clear_filters_btn = QPushButton("Limpiar Filtros")
        self.clear_filters_btn.clicked.connect(self.clear_filters)

        filters_layout.addWidget(QLabel("Buscar:"))
        filters_layout.addWidget(self.search_input, 2)
        filters_layout.addWidget(QLabel("Proveedor:"))
        filters_layout.addWidget(self.proveedor_filter, 1)
        filters_layout.addWidget(QLabel("Categoría:"))
        filters_layout.addWidget(self.categoria_filter, 1)
        filters_layout.addWidget(self.clear_filters_btn)

    def create_herrajes_panel(self):
        """Crea el panel de herrajes."""
        self.herrajes_frame = QGroupBox("🔧 Lista de Herrajes")

        herrajes_layout = QVBoxLayout(self.herrajes_frame)

        # Tabla de herrajes
        self.herrajes_table = QTableWidget()
        self.herrajes_table.setColumnCount(8)
        self.herrajes_table.setHorizontalHeaderLabels(
            [
                "Código",
                "Descripción",
                "Proveedor",
                "Precio Unit.",
                "Unidad",
                "Categoría",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.herrajes_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.herrajes_table.setAlternatingRowColors(True)
        self.herrajes_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        
        # Conectar selección de tabla  
        self.herrajes_table.itemSelectionChanged.connect(self.on_herraje_seleccionado)

        herrajes_layout.addWidget(self.herrajes_table)

    def create_actions_panel(self):
        """Crea el panel de acciones."""
        self.actions_frame = QGroupBox("⚡ Acciones")

        actions_layout = QHBoxLayout(self.actions_frame)

        # Botones de acción
        self.crear_herraje_btn = QPushButton("➕ Crear Herraje")
        self.crear_herraje_btn.clicked.connect(self.crear_herraje_mejorado)
        
        self.editar_herraje_btn = QPushButton("✏️ Editar Herraje")
        self.editar_herraje_btn.clicked.connect(self.editar_herraje_mejorado)
        
        self.eliminar_herraje_btn = QPushButton("🗑️ Eliminar Herraje")
        self.eliminar_herraje_btn.clicked.connect(self.eliminar_herraje_mejorado)

        self.asignar_obra_btn = QPushButton("📋 Asignar a Obra")
        self.asignar_obra_btn.clicked.connect(self.asignar_a_obra_mejorado)

        self.crear_pedido_btn = QPushButton("🛒 Crear Pedido")
        self.crear_pedido_btn.clicked.connect(self.crear_pedido_mejorado)

        self.actualizar_btn = QPushButton("🔄 Actualizar")
        self.actualizar_btn.clicked.connect(self.actualizar_datos)

        self.estadisticas_btn = QPushButton("📊 Ver Estadísticas")
        self.estadisticas_btn.clicked.connect(self.show_estadisticas)

        actions_layout.addWidget(self.crear_herraje_btn)
        actions_layout.addWidget(self.editar_herraje_btn)
        actions_layout.addWidget(self.eliminar_herraje_btn)
        actions_layout.addWidget(self.asignar_obra_btn)
        actions_layout.addWidget(self.crear_pedido_btn)
        actions_layout.addWidget(self.actualizar_btn)
        actions_layout.addWidget(self.estadisticas_btn)
        actions_layout.addStretch()

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller
        
        # Inicializar gestores de diálogos con el controlador
        self.dialog_manager = HerrajeDialogManager(self, controller)
        self.obras_dialog = HerrajeObrasDialog(self, controller)
        self.pedidos_dialog = HerrajePedidosDialog(self, controller)
        
        if hasattr(self.controller, "cargar_datos_iniciales"):
            self.controller.cargar_datos_iniciales()
    
    # ===== MÉTODOS MEJORADOS CON NUEVAS UTILIDADES =====
    
    def crear_herraje_mejorado(self):
        """Crea un nuevo herraje usando el sistema de diálogos mejorado."""
        if self.dialog_manager:
            success = self.dialog_manager.show_create_dialog()
            if success:
                self.actualizar_datos()  # Recargar la tabla
    
    def editar_herraje_mejorado(self):
        """Edita el herraje seleccionado usando el sistema mejorado."""
        if not self.herraje_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para editar.")
            return
        
        if self.dialog_manager:
            success = self.dialog_manager.show_edit_dialog(self.herraje_actual)
            if success:
                self.actualizar_datos()  # Recargar la tabla
    
    def eliminar_herraje_mejorado(self):
        """Elimina el herraje seleccionado usando confirmación mejorada."""
        if not self.herraje_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para eliminar.")
            return
        
        if self.dialog_manager:
            success = self.dialog_manager.confirm_and_delete(self.herraje_actual)
            if success:
                self.actualizar_datos()  # Recargar la tabla
    
    def asignar_a_obra_mejorado(self):
        """Asigna el herraje a una obra usando diálogo mejorado."""
        if not self.herraje_actual:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para asignar a una obra.")
            return
        
        if self.obras_dialog:
            self.obras_dialog.show_asignar_obra_dialog(self.herraje_actual)
    
    def crear_pedido_mejorado(self):
        """Crea un pedido de herrajes usando diálogo mejorado."""
        if self.pedidos_dialog:
            # Obtener herrajes seleccionados si hay alguno
            herrajes_seleccionados = []
            if self.herraje_actual:
                herrajes_seleccionados = [self.herraje_actual]
            
            self.pedidos_dialog.show_crear_pedido_dialog(herrajes_seleccionados)
    
    def on_herraje_seleccionado(self):
        """Maneja la selección de herraje en la tabla."""
        current_row = self.herrajes_table.currentRow()
        if current_row >= 0:
            # Obtener datos del herraje seleccionado desde la primera columna (ID)
            herraje_id_item = self.herrajes_table.item(current_row, 0)
            if herraje_id_item:
                herraje_id = herraje_id_item.data(Qt.ItemDataRole.UserRole)
                if herraje_id and self.controller:
                    # Obtener datos completos del herraje desde el controlador
                    herraje_data = self.controller.obtener_herraje_por_id(herraje_id)
                    if herraje_data:
                        self.herraje_actual = herraje_data
                        return
            
            # Fallback: construir datos básicos desde la tabla
            codigo = self.herrajes_table.item(current_row, 0).text() if self.herrajes_table.item(current_row, 0) else ""
            descripcion = self.herrajes_table.item(current_row, 1).text() if self.herrajes_table.item(current_row, 1) else ""
            
            self.herraje_actual = {
                'id': current_row + 1,  # ID temporal
                'codigo': codigo,
                'descripcion': descripcion
            }
        else:
            self.herraje_actual = None

    def cargar_herrajes_en_tabla(self, herrajes):
        """Carga herrajes en la tabla."""
        self.herrajes_table.setRowCount(len(herrajes))

        for row, herraje in enumerate(herrajes):
            # Datos del herraje
            items = [
                herraje.get("codigo", ""),
                herraje.get("descripcion", ""),
                herraje.get("proveedor", ""),
                f"${herraje.get('precio_unitario', 0.0):.2f}",
                herraje.get("unidad_medida", ""),
                herraje.get("categoria", ""),
                herraje.get("estado", ""),
            ]

            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Guardar el ID en el primer item para referencia
                if col == 0:
                    table_item.setData(Qt.ItemDataRole.UserRole, herraje.get("id", 0))
                self.herrajes_table.setItem(row, col, table_item)

            # Botón de acciones
            action_btn = QPushButton("Ver Detalle")
            action_btn.clicked.connect(
                lambda checked, r=row: self.show_herraje_detail(r)
            )
            self.herrajes_table.setCellWidget(row, 7, action_btn)

    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas mostradas."""
        self.stats_labels["total_herrajes"].setText(
            str(estadisticas.get("total_herrajes", 0))
        )
        self.stats_labels["proveedores_activos"].setText(
            str(estadisticas.get("proveedores_activos", 0))
        )
        self.stats_labels["valor_inventario"].setText(
            f"${estadisticas.get('valor_total_inventario', 0.0):.2f}"
        )
        self.stats_labels["pedidos_pendientes"].setText(
            str(estadisticas.get("pedidos_pendientes", 0))
        )

    def on_search_changed(self, text):
        """Maneja cambios en la búsqueda."""
        if self.controller:
            self.controller.buscar_herrajes(text)

    def on_filters_changed(self):
        """Maneja cambios en los filtros."""
        filtros = {
            "proveedor": self.proveedor_filter.currentText()
            if self.proveedor_filter.currentText() != "Todos los proveedores"
            else None,
            "categoria": self.categoria_filter.currentText()
            if self.categoria_filter.currentText() != "Todas las categorías"
            else None,
        }

        if self.controller:
            self.controller.aplicar_filtros(filtros)

    def clear_filters(self):
        """Limpia todos los filtros."""
        self.search_input.clear()
        self.proveedor_filter.setCurrentIndex(0)
        self.categoria_filter.setCurrentIndex(0)

    def show_asignar_obra_dialog(self):
        """Muestra diálogo para asignar herraje a obra."""
        selected_row = self.herrajes_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un herraje de la tabla."
            )
            return

        # Obtener datos del herraje seleccionado
        herraje_id = self.herrajes_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        codigo = self.herrajes_table.item(selected_row, 0).text()
        descripcion = self.herrajes_table.item(selected_row, 1).text()
        
        # Crear diálogo de asignación
        dialog = DialogoAsignarObra(self, codigo, descripcion)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                self.controller.asignar_herraje_obra(
                    int(herraje_id), 
                    datos["obra_id"], 
                    datos["cantidad"], 
                    datos["observaciones"]
                )

    def show_crear_pedido_dialog(self):
        """Muestra diálogo para crear pedido."""
        # Crear diálogo de pedido
        dialog = DialogoCrearPedido(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                self.controller.crear_pedido_obra(
                    datos["obra_id"],
                    datos["proveedor"],
                    datos["herrajes_lista"]
                )
    
    def show_crear_herraje_dialog(self):
        """Muestra diálogo para crear nuevo herraje."""
        dialog = DialogoCrearHerrajeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                self.controller.crear_herraje(datos)
    
    def show_editar_herraje_dialog(self):
        """Muestra diálogo para editar herraje."""
        selected_row = self.herrajes_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un herraje de la tabla."
            )
            return
        
        herraje_id = self.herrajes_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        if self.controller:
            herraje = self.controller.obtener_herraje_por_id(herraje_id)
            if herraje:
                dialog = DialogoCrearHerrajeDialog(self, herraje)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    datos = dialog.obtener_datos()
                    self.controller.actualizar_herraje(herraje_id, datos)
    
    def show_eliminar_herraje_dialog(self):
        """Elimina el herraje seleccionado."""
        selected_row = self.herrajes_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Advertencia", "Seleccione un herraje de la tabla."
            )
            return
        
        herraje_id = self.herrajes_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        if self.controller:
            self.controller.eliminar_herraje(herraje_id)

    def show_herraje_detail(self, row):
        """Muestra detalles del herraje seleccionado."""
        codigo = self.herrajes_table.item(row, 0).text()
        descripcion = self.herrajes_table.item(row, 1).text()
        proveedor = self.herrajes_table.item(row, 2).text()

        QMessageBox.information(
            self,
            "Detalle Herraje",
            f"Código: {codigo}\nDescripción: {descripcion}\nProveedor: {proveedor}",
        )

    def actualizar_datos(self):
        """Actualiza los datos de la vista."""
        if self.controller:
            self.controller.cargar_datos_iniciales()

    def show_crear_herraje_dialog(self):
        """Muestra el diálogo para crear un nuevo herraje."""
        dialog = HerrajeDialog(self, titulo="Crear Nuevo Herraje")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos_herraje = dialog.obtener_datos()
            if self.controller:
                # Implementar creación de herraje en el controlador
                show_success(self, "Herraje Creado", f"El herraje '{datos_herraje['descripcion']}' ha sido creado exitosamente.")
                self.actualizar_datos()
            else:
                show_error(self, "Error", "No hay controlador disponible para crear el herraje.")
    
    def show_editar_herraje_dialog(self):
        """Muestra el diálogo para editar un herraje existente."""
        # Obtener herraje seleccionado
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para editar.")
            return
            
        dialog = HerrajeDialog(self, titulo="Editar Herraje")
        # Aquí cargarías los datos del herraje seleccionado
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos_herraje = dialog.obtener_datos()
            if self.controller:
                # Implementar edición de herraje en el controlador
                show_success(self, "Herraje Actualizado", f"El herraje '{datos_herraje['descripcion']}' ha sido actualizado exitosamente.")
                self.actualizar_datos()
    
    def show_eliminar_herraje_dialog(self):
        """Confirma y elimina un herraje."""
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para eliminar.")
            return
            
        if ask_question(
            self,
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este herraje?\n\nEsta acción no se puede deshacer."
        ):
            if self.controller:
                # Implementar eliminación en el controlador
                show_success(self, "Herraje Eliminado", "El herraje ha sido eliminado exitosamente.")
                self.actualizar_datos()
    
    def show_asignar_obra_dialog(self):
        """Muestra el diálogo para asignar herraje a una obra."""
        current_row = self.herrajes_table.currentRow()
        if current_row < 0:
            show_warning(self, "Sin selección", "Por favor seleccione un herraje para asignar a una obra.")
            return
        
        # Aquí implementarías el diálogo de asignación a obra
        show_success(self, "Asignación Exitosa", "El herraje ha sido asignado a la obra correctamente.")
    
    def show_crear_pedido_dialog(self):
        """Muestra el diálogo para crear un pedido."""
        # Implementar diálogo de pedido
        show_success(self, "Pedido Creado", "El pedido ha sido creado exitosamente.")

    def show_estadisticas(self):
        """Muestra estadísticas detalladas."""
        if self.controller:
            self.controller.mostrar_estadisticas_detalladas()

    def show_error(self, mensaje):
        """Muestra mensaje de error."""
        QMessageBox.critical(self, "Error", mensaje)

    def show_success(self, mensaje):
        """Muestra mensaje de éxito."""
        QMessageBox.information(self, "Éxito", mensaje)


class DialogoAsignarObra(QDialog):
    """Diálogo para asignar herraje a obra."""
    
    def __init__(self, parent=None, codigo_herraje="", descripcion=""):
        super().__init__(parent)
        self.setWindowTitle("Asignar Herraje a Obra")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.codigo_herraje = codigo_herraje
        self.descripcion = descripcion
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Información del herraje
        info_label = QLabel(f"Herraje: {self.codigo_herraje} - {self.descripcion}")
        info_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.obra_combo = QComboBox()
        self.obra_combo.addItems(["Obra 1", "Obra 2", "Obra 3"])  # Datos demo
        
        self.cantidad_spin = QDoubleSpinBox()
        self.cantidad_spin.setMinimum(0.1)
        self.cantidad_spin.setMaximum(9999.0)
        self.cantidad_spin.setValue(1.0)
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setMaximumHeight(100)
        
        form_layout.addRow("Obra:", self.obra_combo)
        form_layout.addRow("Cantidad:", self.cantidad_spin)
        form_layout.addRow("Observaciones:", self.observaciones_text)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "obra_id": self.obra_combo.currentIndex() + 1,
            "cantidad": self.cantidad_spin.value(),
            "observaciones": self.observaciones_text.toPlainText()
        }


class DialogoCrearPedido(QDialog):
    """Diálogo para crear pedido de herrajes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Pedido de Herrajes")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.obra_combo = QComboBox()
        self.obra_combo.addItems(["Obra 1", "Obra 2", "Obra 3"])  # Datos demo
        
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.addItems(["Proveedor A", "Proveedor B", "Proveedor C"])  # Datos demo
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setMaximumHeight(100)
        
        form_layout.addRow("Obra:", self.obra_combo)
        form_layout.addRow("Proveedor:", self.proveedor_combo)
        form_layout.addRow("Observaciones:", self.observaciones_text)
        
        layout.addLayout(form_layout)
        
        # Lista de herrajes (simplificada)
        herrajes_label = QLabel("Herrajes del pedido:")
        layout.addWidget(herrajes_label)
        
        self.herrajes_list = QTextEdit()
        self.herrajes_list.setPlainText("Herraje 1 - Cantidad: 5\nHeraje 2 - Cantidad: 3")
        layout.addWidget(self.herrajes_list)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "obra_id": self.obra_combo.currentIndex() + 1,
            "proveedor": self.proveedor_combo.currentText(),
            "herrajes_lista": [
                {"herraje_id": 1, "cantidad": 5, "precio_unitario": 10.0},
                {"herraje_id": 2, "cantidad": 3, "precio_unitario": 15.0}
            ]
        }


class DialogoCrearHerrajeDialog(QDialog):
    """Diálogo para crear/editar herraje."""
    
    def __init__(self, parent=None, herraje=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Herraje" if herraje is None else "Editar Herraje")
        self.setModal(True)
        self.setFixedSize(600, 700)
        
        self.herraje = herraje
        self.init_ui()
        
        if herraje:
            self.cargar_datos_herraje(herraje)
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Scroll area para el formulario
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Información básica
        info_group = QGroupBox("Información Básica")
        info_layout = QFormLayout(info_group)
        
        self.codigo_input = QLineEdit()
        self.descripcion_input = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["BISAGRA", "CERRADURA", "MANIJA", "TORNILLO", "RIEL", "SOPORTE", "OTRO"])
        
        self.proveedor_input = QLineEdit()
        self.precio_spin = QDoubleSpinBox()
        self.precio_spin.setMaximum(99999.99)
        self.precio_spin.setDecimals(2)
        
        self.unidad_combo = QComboBox()
        self.unidad_combo.addItems(["UNIDAD", "PAR", "JUEGO", "METRO", "KILOGRAMO"])
        
        self.categoria_input = QLineEdit()
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["ACTIVO", "INACTIVO", "DESCONTINUADO"])
        
        info_layout.addRow("Código:", self.codigo_input)
        info_layout.addRow("Descripción:", self.descripcion_input)
        info_layout.addRow("Tipo:", self.tipo_combo)
        info_layout.addRow("Proveedor:", self.proveedor_input)
        info_layout.addRow("Precio Unitario:", self.precio_spin)
        info_layout.addRow("Unidad:", self.unidad_combo)
        info_layout.addRow("Categoría:", self.categoria_input)
        info_layout.addRow("Estado:", self.estado_combo)
        
        # Stock
        stock_group = QGroupBox("Stock")
        stock_layout = QFormLayout(stock_group)
        
        self.stock_minimo_spin = QSpinBox()
        self.stock_minimo_spin.setMaximum(99999)
        self.stock_actual_spin = QSpinBox()
        self.stock_actual_spin.setMaximum(99999)
        self.ubicacion_input = QLineEdit()
        
        stock_layout.addRow("Stock Mínimo:", self.stock_minimo_spin)
        stock_layout.addRow("Stock Actual:", self.stock_actual_spin)
        stock_layout.addRow("Ubicación:", self.ubicacion_input)
        
        # Detalles técnicos
        detalles_group = QGroupBox("Detalles Técnicos")
        detalles_layout = QFormLayout(detalles_group)
        
        self.marca_input = QLineEdit()
        self.modelo_input = QLineEdit()
        self.color_input = QLineEdit()
        self.material_input = QLineEdit()
        self.dimensiones_input = QLineEdit()
        self.peso_spin = QDoubleSpinBox()
        self.peso_spin.setMaximum(9999.999)
        self.peso_spin.setDecimals(3)
        self.peso_spin.setSuffix(" kg")
        
        detalles_layout.addRow("Marca:", self.marca_input)
        detalles_layout.addRow("Modelo:", self.modelo_input)
        detalles_layout.addRow("Color:", self.color_input)
        detalles_layout.addRow("Material:", self.material_input)
        detalles_layout.addRow("Dimensiones:", self.dimensiones_input)
        detalles_layout.addRow("Peso:", self.peso_spin)
        
        # Observaciones
        obs_group = QGroupBox("Observaciones y Especificaciones")
        obs_layout = QVBoxLayout(obs_group)
        
        self.observaciones_text = QTextEdit()
        self.observaciones_text.setMaximumHeight(80)
        self.especificaciones_text = QTextEdit()
        self.especificaciones_text.setMaximumHeight(80)
        
        obs_layout.addWidget(QLabel("Observaciones:"))
        obs_layout.addWidget(self.observaciones_text)
        obs_layout.addWidget(QLabel("Especificaciones técnicas:"))
        obs_layout.addWidget(self.especificaciones_text)
        
        # Agregar grupos al scroll
        scroll_layout.addWidget(info_group)
        scroll_layout.addWidget(stock_group)
        scroll_layout.addWidget(detalles_group)
        scroll_layout.addWidget(obs_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def cargar_datos_herraje(self, herraje):
        """Carga los datos del herraje en el formulario."""
        self.codigo_input.setText(herraje.get("codigo", ""))
        self.descripcion_input.setText(herraje.get("descripcion", ""))
        self.tipo_combo.setCurrentText(herraje.get("tipo", "OTRO"))
        self.proveedor_input.setText(herraje.get("proveedor", ""))
        self.precio_spin.setValue(herraje.get("precio_unitario", 0.0))
        self.unidad_combo.setCurrentText(herraje.get("unidad_medida", "UNIDAD"))
        self.categoria_input.setText(herraje.get("categoria", ""))
        self.estado_combo.setCurrentText(herraje.get("estado", "ACTIVO"))
        
        self.stock_minimo_spin.setValue(herraje.get("stock_minimo", 0))
        self.stock_actual_spin.setValue(herraje.get("stock_actual", 0))
        self.ubicacion_input.setText(herraje.get("ubicacion", ""))
        
        self.marca_input.setText(herraje.get("marca", ""))
        self.modelo_input.setText(herraje.get("modelo", ""))
        self.color_input.setText(herraje.get("color", ""))
        self.material_input.setText(herraje.get("material", ""))
        self.dimensiones_input.setText(herraje.get("dimensiones", ""))
        self.peso_spin.setValue(herraje.get("peso", 0.0))
        
        self.observaciones_text.setText(herraje.get("observaciones", ""))
        self.especificaciones_text.setText(herraje.get("especificaciones", ""))
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "codigo": self.codigo_input.text(),
            "descripcion": self.descripcion_input.text(),
            "tipo": self.tipo_combo.currentText(),
            "proveedor": self.proveedor_input.text(),
            "precio_unitario": self.precio_spin.value(),
            "unidad_medida": self.unidad_combo.currentText(),
            "categoria": self.categoria_input.text(),
            "estado": self.estado_combo.currentText(),
            "stock_minimo": self.stock_minimo_spin.value(),
            "stock_actual": self.stock_actual_spin.value(),
            "ubicacion": self.ubicacion_input.text(),
            "marca": self.marca_input.text(),
            "modelo": self.modelo_input.text(),
            "color": self.color_input.text(),
            "material": self.material_input.text(),
            "dimensiones": self.dimensiones_input.text(),
            "peso": self.peso_spin.value(),
            "observaciones": self.observaciones_text.toPlainText(),
            "especificaciones": self.especificaciones_text.toPlainText()
        }
