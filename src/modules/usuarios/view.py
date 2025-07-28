"""
Vista de Usuarios Modernizada

Interfaz moderna para la gestión de usuarios del sistema.
"""

import json
from datetime import date, datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class UsuariosView(QWidget):
    """Vista modernizada para gestión de usuarios."""

    # Señales
    usuario_seleccionado = pyqtSignal(dict)
    solicitud_crear_usuario = pyqtSignal(dict)
    solicitud_actualizar_usuario = pyqtSignal(dict)
    solicitud_eliminar_usuario = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.usuarios_data = []
        self.usuario_actual = None

        self.init_ui()
        self.aplicar_estilos()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header con título y estadísticas
        header_widget = self.crear_header()
        layout.addWidget(header_widget)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo - Lista de usuarios
        panel_izquierdo = self.crear_panel_usuarios()
        splitter.addWidget(panel_izquierdo)

        # Panel derecho - Detalles y formulario
        panel_derecho = self.crear_panel_detalles()
        splitter.addWidget(panel_derecho)

        # Configurar proporción del splitter
        splitter.setSizes([700, 400])
        layout.addWidget(splitter)

    def crear_header(self):
        """Crea el header con título y estadísticas."""
        header = QFrame()
        header.setFixedHeight(120)
        layout = QHBoxLayout(header)

        # Título
        titulo_container = QVBoxLayout()
        titulo = QLabel("👥 Gestión de Usuarios")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        subtitulo = QLabel("Administración de usuarios y permisos del sistema")
        subtitulo.setFont(QFont("Segoe UI", 12))

        titulo_container.addWidget(titulo)
        titulo_container.addWidget(subtitulo)
        titulo_container.addStretch()

        layout.addLayout(titulo_container)
        layout.addStretch()

        # Estadísticas
        stats_container = QHBoxLayout()

        # Total usuarios
        self.stat_total = self.crear_stat_card("Total Usuarios", "0", "#3498db")
        stats_container.addWidget(self.stat_total)

        # Usuarios activos
        self.stat_activos = self.crear_stat_card("Activos", "0", "#27ae60")
        stats_container.addWidget(self.stat_activos)

        # Usuarios inactivos
        self.stat_inactivos = self.crear_stat_card("Inactivos", "0", "#e74c3c")
        stats_container.addWidget(self.stat_inactivos)

        # Administradores
        self.stat_admins = self.crear_stat_card("Admins", "0", "#f39c12")
        stats_container.addWidget(self.stat_admins)

        layout.addLayout(stats_container)

        return header

    def crear_stat_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        card = QFrame()
        card.setFixedSize(120, 80)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)

        # Valor
        valor_label = QLabel(valor)
        valor_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Segoe UI", 10))
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(valor_label)
        layout.addWidget(titulo_label)

        # Guardar referencia para actualizar
        card.valor_label = valor_label
        card.titulo_label = titulo_label
        card.color = color

        return card

    def crear_panel_usuarios(self):
        """Crea el panel izquierdo con la lista de usuarios."""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Barra de herramientas
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar usuarios...")
        self.search_input.textChanged.connect(self.filtrar_usuarios)

        # Filtros
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(["Todos", "Activos", "Inactivos"])
        self.filtro_estado.currentTextChanged.connect(self.filtrar_usuarios)

        self.filtro_rol = QComboBox()
        self.filtro_rol.addItems(
            ["Todos", "Administrador", "Usuario", "Operador", "Invitado"]
        )
        self.filtro_rol.currentTextChanged.connect(self.filtrar_usuarios)

        # Botones de acción
        self.btn_nuevo = QPushButton("➕ Nuevo Usuario")
        self.btn_nuevo.clicked.connect(self.mostrar_dialogo_nuevo_usuario)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_usuarios)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.filtro_estado)
        toolbar_layout.addWidget(self.filtro_rol)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_nuevo)
        toolbar_layout.addWidget(self.btn_actualizar)

        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(6)
        self.tabla_usuarios.setHorizontalHeaderLabels(
            ["ID", "Usuario", "Nombre", "Email", "Rol", "Estado"]
        )

        # Configurar tabla
        header = self.tabla_usuarios.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        self.tabla_usuarios.setColumnWidth(0, 60)
        self.tabla_usuarios.setColumnWidth(4, 100)
        self.tabla_usuarios.setColumnWidth(5, 80)

        self.tabla_usuarios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.itemSelectionChanged.connect(self.on_usuario_seleccionado)

        layout.addWidget(toolbar)
        layout.addWidget(self.tabla_usuarios)

        return panel

    def crear_panel_detalles(self):
        """Crea el panel derecho con detalles del usuario."""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Título del panel
        titulo = QLabel("📋 Detalles del Usuario")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Área de scroll para el formulario
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Información básica
        info_group = QGroupBox("Información Básica")
        info_layout = QFormLayout(info_group)

        self.input_usuario = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_email = QLineEdit()
        self.input_telefono = QLineEdit()

        info_layout.addRow("Usuario:", self.input_usuario)
        info_layout.addRow("Nombre:", self.input_nombre)
        info_layout.addRow("Email:", self.input_email)
        info_layout.addRow("Teléfono:", self.input_telefono)

        # Configuración de cuenta
        config_group = QGroupBox("Configuración de Cuenta")
        config_layout = QFormLayout(config_group)

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Usuario", "Operador", "Administrador"])

        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Activo", "Inactivo", "Suspendido"])

        self.date_ultimo_acceso = QDateEdit()
        self.date_ultimo_acceso.setDate(QDate.currentDate())
        self.date_ultimo_acceso.setEnabled(False)

        config_layout.addRow("Rol:", self.combo_rol)
        config_layout.addRow("Estado:", self.combo_estado)
        config_layout.addRow("Último Acceso:", self.date_ultimo_acceso)

        # Permisos
        permisos_group = QGroupBox("Permisos")
        permisos_layout = QVBoxLayout(permisos_group)

        self.permisos_container = QWidget()
        permisos_grid = QGridLayout(self.permisos_container)

        # Crear checkboxes de permisos
        self.permisos_checkboxes = {}
        permisos_disponibles = [
            "obras",
            "inventario",
            "usuarios",
            "pedidos",
            "logistica",
            "mantenimiento",
            "configuracion",
            "auditoria",
            "contabilidad",
        ]

        row = 0
        col = 0
        for permiso in permisos_disponibles:
            checkbox = QCheckBox(permiso.capitalize())
            self.permisos_checkboxes[permiso] = checkbox
            permisos_grid.addWidget(checkbox, row, col)

            col += 1
            if col >= 3:
                col = 0
                row += 1

        permisos_layout.addWidget(self.permisos_container)

        # Notas
        notas_group = QGroupBox("Notas")
        notas_layout = QVBoxLayout(notas_group)

        self.text_notas = QTextEdit()
        self.text_notas.setMaximumHeight(100)
        notas_layout.addWidget(self.text_notas)

        # Botones de acción
        botones_layout = QHBoxLayout()

        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.clicked.connect(self.guardar_usuario)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)

        self.btn_resetear_password = QPushButton("🔑 Reset Password")
        self.btn_resetear_password.clicked.connect(self.resetear_password)

        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addWidget(self.btn_resetear_password)
        botones_layout.addStretch()

        # Agregar grupos al scroll
        scroll_layout.addWidget(info_group)
        scroll_layout.addWidget(config_group)
        scroll_layout.addWidget(permisos_group)
        scroll_layout.addWidget(notas_group)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        layout.addLayout(botones_layout)

        # Deshabilitar formulario inicialmente
        self.habilitar_formulario(False)

        return panel

    def aplicar_estilos(self):
        """Aplica estilos modernos al widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }

            QLabel {
                color: #2c3e50;
                font-weight: 500;
            }

            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }

            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }

            QPushButton {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }

            QPushButton:hover {
                background: linear-gradient(135deg, #2980b9, #1f618d);
                transform: translateY(-2px);
            }

            QPushButton:pressed {
                background: linear-gradient(135deg, #1f618d, #154360);
                transform: translateY(0px);
            }

            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }

            QHeaderView::section {
                background: linear-gradient(135deg, #34495e, #2c3e50);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                min-width: 100px;
            }

            QComboBox:focus {
                border-color: #3498db;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzZjNzU3ZCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }

            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }

            QCheckBox {
                spacing: 8px;
                font-size: 13px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }

            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }

            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }

            QTextEdit:focus {
                border-color: #3498db;
            }

            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }

            QDateEdit:focus {
                border-color: #3498db;
            }

            /* Estilos para las tarjetas de estadísticas */
            QFrame[objectName="stat_card"] {
                background: linear-gradient(135deg, #ffffff, #f8f9fa);
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        # Aplicar estilos específicos a las tarjetas de estadísticas
        for card in [
            self.stat_total,
            self.stat_activos,
            self.stat_inactivos,
            self.stat_admins,
        ]:
            card.setObjectName("stat_card")
            card.valor_label.setStyleSheet(f"color: {card.color}; font-weight: bold;")

    def cargar_usuarios_en_tabla(self, usuarios):
        """Carga la lista de usuarios en la tabla."""
        self.usuarios_data = usuarios
        self.tabla_usuarios.setRowCount(len(usuarios))

        for row, usuario in enumerate(usuarios):
            # ID
            item_id = QTableWidgetItem(str(usuario.get("id", "")))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_usuarios.setItem(row, 0, item_id)

            # Usuario
            self.tabla_usuarios.setItem(
                row, 1, QTableWidgetItem(usuario.get("username", ""))
            )

            # Nombre
            self.tabla_usuarios.setItem(
                row, 2, QTableWidgetItem(usuario.get("nombre", ""))
            )

            # Email
            self.tabla_usuarios.setItem(
                row, 3, QTableWidgetItem(usuario.get("email", ""))
            )

            # Rol
            item_rol = QTableWidgetItem(usuario.get("rol", ""))
            item_rol.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_usuarios.setItem(row, 4, item_rol)

            # Estado
            estado = usuario.get("estado", "Activo")
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Colorear según el estado
            if estado == "Activo":
                item_estado.setBackground(QColor("#d4edda"))
                item_estado.setForeground(QColor("#155724"))
            elif estado == "Inactivo":
                item_estado.setBackground(QColor("#f8d7da"))
                item_estado.setForeground(QColor("#721c24"))
            elif estado == "Suspendido":
                item_estado.setBackground(QColor("#fff3cd"))
                item_estado.setForeground(QColor("#856404"))

            self.tabla_usuarios.setItem(row, 5, item_estado)

        # Actualizar estadísticas
        self.actualizar_estadisticas()

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en el header."""
        if not self.usuarios_data:
            return

        total = len(self.usuarios_data)
        activos = len([u for u in self.usuarios_data if u.get("estado") == "Activo"])
        inactivos = len(
            [u for u in self.usuarios_data if u.get("estado") == "Inactivo"]
        )
        admins = len([u for u in self.usuarios_data if u.get("rol") == "Administrador"])

        self.stat_total.valor_label.setText(str(total))
        self.stat_activos.valor_label.setText(str(activos))
        self.stat_inactivos.valor_label.setText(str(inactivos))
        self.stat_admins.valor_label.setText(str(admins))

    def filtrar_usuarios(self):
        """Filtra usuarios según los criterios seleccionados."""
        texto_busqueda = self.search_input.text().lower()
        estado_filtro = self.filtro_estado.currentText()
        rol_filtro = self.filtro_rol.currentText()

        for row in range(self.tabla_usuarios.rowCount()):
            mostrar_fila = True

            # Filtro por texto
            if texto_busqueda:
                usuario = self.tabla_usuarios.item(row, 1).text().lower()
                nombre = self.tabla_usuarios.item(row, 2).text().lower()
                email = self.tabla_usuarios.item(row, 3).text().lower()

                if not (
                    texto_busqueda in usuario
                    or texto_busqueda in nombre
                    or texto_busqueda in email
                ):
                    mostrar_fila = False

            # Filtro por estado
            if estado_filtro != "Todos":
                estado_actual = self.tabla_usuarios.item(row, 5).text()
                if estado_actual != estado_filtro:
                    mostrar_fila = False

            # Filtro por rol
            if rol_filtro != "Todos":
                rol_actual = self.tabla_usuarios.item(row, 4).text()
                if rol_actual != rol_filtro:
                    mostrar_fila = False

            self.tabla_usuarios.setRowHidden(row, not mostrar_fila)

    def on_usuario_seleccionado(self):
        """Maneja la selección de un usuario en la tabla."""
        fila_actual = self.tabla_usuarios.currentRow()
        if fila_actual >= 0:
            usuario_id = self.tabla_usuarios.item(fila_actual, 0).text()
            usuario = next(
                (u for u in self.usuarios_data if str(u.get("id")) == usuario_id), None
            )

            if usuario:
                self.cargar_usuario_en_formulario(usuario)
                self.habilitar_formulario(True)
                self.usuario_actual = usuario

    def cargar_usuario_en_formulario(self, usuario):
        """Carga los datos del usuario en el formulario."""
        self.input_usuario.setText(usuario.get("username", ""))
        self.input_nombre.setText(usuario.get("nombre", ""))
        self.input_email.setText(usuario.get("email", ""))
        self.input_telefono.setText(usuario.get("telefono", ""))

        # Configuración
        self.combo_rol.setCurrentText(usuario.get("rol", "Usuario"))
        self.combo_estado.setCurrentText(usuario.get("estado", "Activo"))

        # Último acceso
        ultimo_acceso = usuario.get("ultimo_acceso")
        if ultimo_acceso:
            try:
                if isinstance(ultimo_acceso, str):
                    fecha = datetime.strptime(ultimo_acceso, "%Y-%m-%d").date()
                    self.date_ultimo_acceso.setDate(QDate(fecha))
            except:
                pass

        # Permisos
        permisos = usuario.get("permisos", [])
        if isinstance(permisos, str):
            try:
                permisos = json.loads(permisos)
            except:
                permisos = []

        for permiso, checkbox in self.permisos_checkboxes.items():
            checkbox.setChecked(permiso in permisos)

        # Notas
        self.text_notas.setText(usuario.get("notas", ""))

    def habilitar_formulario(self, habilitado):
        """Habilita o deshabilita el formulario."""
        campos = [
            self.input_usuario,
            self.input_nombre,
            self.input_email,
            self.input_telefono,
            self.combo_rol,
            self.combo_estado,
            self.text_notas,
        ]

        for campo in campos:
            campo.setEnabled(habilitado)

        for checkbox in self.permisos_checkboxes.values():
            checkbox.setEnabled(habilitado)

        # Botones
        self.btn_guardar.setEnabled(habilitado)
        self.btn_eliminar.setEnabled(habilitado)
        self.btn_resetear_password.setEnabled(habilitado)

    def mostrar_dialogo_nuevo_usuario(self):
        """Muestra el diálogo para crear un nuevo usuario."""
        dialogo = DialogoNuevoUsuario(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos_usuario = dialogo.obtener_datos()
            self.solicitud_crear_usuario.emit(datos_usuario)

    def guardar_usuario(self):
        """Guarda los cambios del usuario actual."""
        if not self.usuario_actual:
            return

        # Obtener permisos seleccionados
        permisos = []
        for permiso, checkbox in self.permisos_checkboxes.items():
            if checkbox.isChecked():
                permisos.append(permiso)

        datos_actualizados = {
            "id": self.usuario_actual["id"],
            "username": self.input_usuario.text(),
            "nombre": self.input_nombre.text(),
            "email": self.input_email.text(),
            "telefono": self.input_telefono.text(),
            "rol": self.combo_rol.currentText(),
            "estado": self.combo_estado.currentText(),
            "permisos": permisos,
            "notas": self.text_notas.toPlainText(),
        }

        self.solicitud_actualizar_usuario.emit(datos_actualizados)

    def eliminar_usuario(self):
        """Elimina el usuario actual."""
        if not self.usuario_actual:
            return

        self.solicitud_eliminar_usuario.emit(str(self.usuario_actual["id"]))

    def resetear_password(self):
        """Resetea la contraseña del usuario actual."""
        if not self.usuario_actual:
            return

        # Aquí implementarías la lógica para resetear password
        print(f"Resetear password para usuario {self.usuario_actual['username']}")

    def cargar_usuarios(self):
        """Solicita la carga de usuarios al controlador."""
        if self.controller:
            self.controller.cargar_usuarios()

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoNuevoUsuario(QDialog):
    """Diálogo para crear un nuevo usuario."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Usuario")
        self.setModal(True)
        self.setFixedSize(400, 600)

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        self.input_usuario = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_email = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password_confirm = QLineEdit()
        self.input_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Usuario", "Operador", "Administrador"])

        form_layout.addRow("Usuario:", self.input_usuario)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Teléfono:", self.input_telefono)
        form_layout.addRow("Contraseña:", self.input_password)
        form_layout.addRow("Confirmar:", self.input_password_confirm)
        form_layout.addRow("Rol:", self.combo_rol)

        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_crear = QPushButton("Crear Usuario")
        btn_crear.clicked.connect(self.validar_y_aceptar)

        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_crear)

        layout.addLayout(botones_layout)

    def validar_y_aceptar(self):
        """Valida los datos y acepta el diálogo."""
        # Validaciones básicas
        if not self.input_usuario.text():
            return

        if not self.input_nombre.text():
            return

        if self.input_password.text() != self.input_password_confirm.text():
            return

        self.accept()

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "username": self.input_usuario.text(),
            "nombre": self.input_nombre.text(),
            "email": self.input_email.text(),
            "telefono": self.input_telefono.text(),
            "password": self.input_password.text(),
            "rol": self.combo_rol.currentText(),
            "estado": "Activo",
        }
