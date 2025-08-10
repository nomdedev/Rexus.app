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
"""

"""
Vista de Usuarios Modernizada - Rexus.app
Interfaz moderna con LoadingManager integrado y UX mejorada
"""

import os
import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

# Importaciones PyQt6
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Importaciones del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from rexus.utils.loading_manager import LoadingManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class UsuariosViewModern(QWidget):
    """Vista modernizada para el módulo de usuarios con interfaz profesional."""

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.loading_manager = LoadingManager()

        # Variables de estado
        self.usuarios_data = []
        self.current_page = 1
        self.items_per_page = 50
        self.total_pages = 1

        # Filtros activos
        self.active_filters = {}

        self.init_ui()
        self.setup_shortcuts()
        self.cargar_datos_iniciales()

    def init_ui(self):
        """Inicializa la interfaz de usuario moderna."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título
        self.crear_titulo(layout)

        # Panel principal dividido
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel superior con controles
        panel_superior = self.crear_panel_superior()
        splitter.addWidget(panel_superior)

        # Panel inferior con tabla
        panel_tabla = self.crear_panel_tabla()
        splitter.addWidget(panel_tabla)

        splitter.setSizes([250, 550])
        layout.addWidget(splitter)

        # Panel de estado
        self.crear_panel_estado(layout)

        # Aplicar estilos
        self.aplicar_estilos()

    def crear_titulo(self, layout):
        """Crea el título del módulo."""
        titulo_frame = QFrame()
        titulo_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #28a745, stop:1 #20c997);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        titulo_layout = QHBoxLayout(titulo_frame)

        titulo_label = QLabel("👥 Gestión de Usuarios")
        titulo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }
        """)
        titulo_layout.addWidget(titulo_label)
        titulo_layout.addStretch()

        layout.addWidget(titulo_frame)

    def crear_panel_superior(self):
        """Crea el panel superior con controles y estadísticas."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)

        # Panel de búsqueda y filtros
        grupo_busqueda = QGroupBox("🔍 Búsqueda y Filtros")
        layout_busqueda = QVBoxLayout(grupo_busqueda)

        # Búsqueda rápida
        busqueda_layout = QHBoxLayout()
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por username, nombre o email...")
        self.campo_busqueda.textChanged.connect(self.buscar_usuarios)

        self.btn_limpiar_busqueda = QPushButton("Limpiar")
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)

        busqueda_layout.addWidget(QLabel("Buscar:"))
        busqueda_layout.addWidget(self.campo_busqueda)
        busqueda_layout.addWidget(self.btn_limpiar_busqueda)
        layout_busqueda.addLayout(busqueda_layout)

        # Filtros rápidos
        filtros_layout = QHBoxLayout()

        # Filtro por rol
        filtros_layout.addWidget(QLabel("Rol:"))
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(
            ["Todos", "Admin", "Supervisor", "Operador", "Usuario", "Invitado"]
        )
        self.combo_rol.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.combo_rol)

        # Filtro por estado
        filtros_layout.addWidget(QLabel("Estado:"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Activos", "Inactivos", "Bloqueados"])
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.combo_estado)

        layout_busqueda.addLayout(filtros_layout)
        layout.addWidget(grupo_busqueda)

        # Panel de acciones
        grupo_acciones = QGroupBox("⚡ Acciones de Usuario")
        layout_acciones = QVBoxLayout(grupo_acciones)

        acciones_layout = QHBoxLayout()

        self.btn_nuevo = QPushButton("👤 Nuevo Usuario")
        self.btn_nuevo.clicked.connect(self.nuevo_usuario)

        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.clicked.connect(self.editar_usuario)
        self.btn_editar.setEnabled(False)

        self.btn_cambiar_password = QPushButton("🔑 Cambiar Password")
        self.btn_cambiar_password.clicked.connect(self.cambiar_password)
        self.btn_cambiar_password.setEnabled(False)

        self.btn_activar_desactivar = QPushButton("🔄 Activar/Desactivar")
        self.btn_activar_desactivar.clicked.connect(self.toggle_estado_usuario)
        self.btn_activar_desactivar.setEnabled(False)

        acciones_layout.addWidget(self.btn_nuevo)
        acciones_layout.addWidget(self.btn_editar)
        acciones_layout.addWidget(self.btn_cambiar_password)
        acciones_layout.addWidget(self.btn_activar_desactivar)
        layout_acciones.addLayout(acciones_layout)

        # Acciones adicionales
        acciones2_layout = QHBoxLayout()

        self.btn_permisos = QPushButton("🛡️ Permisos")
        self.btn_permisos.clicked.connect(self.gestionar_permisos)
        self.btn_permisos.setEnabled(False)

        self.btn_sesiones = QPushButton("🖥️ Sesiones")
        self.btn_sesiones.clicked.connect(self.ver_sesiones)
        self.btn_sesiones.setEnabled(False)

        self.btn_auditoria = QPushButton("📋 Auditoría")
        self.btn_auditoria.clicked.connect(self.ver_auditoria)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)

        acciones2_layout.addWidget(self.btn_permisos)
        acciones2_layout.addWidget(self.btn_sesiones)
        acciones2_layout.addWidget(self.btn_auditoria)
        acciones2_layout.addWidget(self.btn_actualizar)
        layout_acciones.addLayout(acciones2_layout)

        layout.addWidget(grupo_acciones)

        # Panel de estadísticas
        grupo_stats = self.crear_panel_estadisticas()
        layout.addWidget(grupo_stats)

        return widget

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas."""
        grupo_stats = QGroupBox("[CHART] Estadísticas de Usuarios")
        layout_stats = QVBoxLayout(grupo_stats)

        # Labels de estadísticas
        self.label_total = QLabel("Total usuarios: 0")
        self.label_activos = QLabel("Activos: 0")
        self.label_online = QLabel("En línea: 0")
        self.label_bloqueados = QLabel("Bloqueados: 0")

        layout_stats.addWidget(self.label_total)
        layout_stats.addWidget(self.label_activos)
        layout_stats.addWidget(self.label_online)
        layout_stats.addWidget(self.label_bloqueados)

        return grupo_stats

    def crear_panel_tabla(self):
        """Crea el panel con la tabla de usuarios."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Tabla
        self.tabla_usuarios = QTableWidget()
        self.configurar_tabla()
        self.tabla_usuarios.itemSelectionChanged.connect(self.seleccion_cambiada)
        layout.addWidget(self.tabla_usuarios)

        # Panel de paginación
        paginacion_layout = QHBoxLayout()

        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))

        self.btn_anterior = QPushButton("⏪ Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)

        self.label_pagina = QLabel("Página 1 de 1")

        self.btn_siguiente = QPushButton("Siguiente ⏩")
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)

        self.btn_ultima = QPushButton("Última ⏭️")
        self.btn_ultima.clicked.connect(self.ir_a_ultima_pagina)

        paginacion_layout.addWidget(self.btn_primera)
        paginacion_layout.addWidget(self.btn_anterior)
        paginacion_layout.addStretch()
        paginacion_layout.addWidget(self.label_pagina)
        paginacion_layout.addStretch()
        paginacion_layout.addWidget(self.btn_siguiente)
        paginacion_layout.addWidget(self.btn_ultima)

        layout.addLayout(paginacion_layout)

        return widget

    def crear_panel_estado(self, layout):
        """Crea el panel de estado inferior."""
        estado_frame = QFrame()
        estado_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 5px;
            }
        """)
        estado_layout = QHBoxLayout(estado_frame)

        self.label_estado = QLabel("Listo")
        self.label_registros = QLabel("0 usuarios")
        self.label_ultima_actualizacion = QLabel("Última actualización: --")

        estado_layout.addWidget(self.label_estado)
        estado_layout.addStretch()
        estado_layout.addWidget(self.label_registros)
        estado_layout.addWidget(QLabel("|"))
        estado_layout.addWidget(self.label_ultima_actualizacion)

        layout.addWidget(estado_frame)

    def configurar_tabla(self):
        """Configura la tabla de usuarios."""
        columnas = [
            "ID",
            "Username",
            "Nombre",
            "Email",
            "Rol",
            "Estado",
            "Último Acceso",
            "Fecha Creación",
        ]

        self.tabla_usuarios.setColumnCount(len(columnas))
        self.tabla_usuarios.setHorizontalHeaderLabels(columnas)

        # Configurar encabezados
        header = self.tabla_usuarios.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Username
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nombre
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Email
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Rol
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Estado
            header.setSectionResizeMode(
                6, QHeaderView.ResizeMode.Fixed
            )  # Último Acceso
            header.setSectionResizeMode(
                7, QHeaderView.ResizeMode.Fixed
            )  # Fecha Creación

        # Tamaños de columnas
        self.tabla_usuarios.setColumnWidth(0, 50)
        self.tabla_usuarios.setColumnWidth(1, 120)
        self.tabla_usuarios.setColumnWidth(4, 100)
        self.tabla_usuarios.setColumnWidth(5, 80)
        self.tabla_usuarios.setColumnWidth(6, 120)
        self.tabla_usuarios.setColumnWidth(7, 120)

        # Propiedades de la tabla
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_usuarios.setSortingEnabled(True)

    def aplicar_estilos(self):
        """Aplica estilos CSS al widget."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28a745;
            }
            
            QPushButton {
                background-color: #28a745;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #218838;
            }
            
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            
            QPushButton:disabled {
                background-color: #6c757d;
            }
            
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #28a745;
                outline: none;
            }
            
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #28a745;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)

    def setup_shortcuts(self):
        """Configura atajos de teclado."""
        shortcuts = {
            "Ctrl+N": self.nuevo_usuario,
            "Ctrl+E": self.editar_usuario,
            "Delete": self.toggle_estado_usuario,
            "F5": self.actualizar_datos,
            "Ctrl+F": lambda: self.campo_busqueda.setFocus(),
            "Escape": self.limpiar_busqueda,
            "Ctrl+P": self.gestionar_permisos,
        }

        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales."""
        self.loading_manager.show_loading(self, "Cargando usuarios...")

        # Simular carga de datos
        QTimer.singleShot(1000, self._cargar_datos_demo)

    def _cargar_datos_demo(self):
        """Carga datos de demostración."""
        self.usuarios_data = [
            {
                "id": 1,
                "username": "admin",
                "nombre": "Administrador",
                "email": "admin@rexus.app",
                "rol": "Admin",
                "activo": True,
                "ultimo_acceso": "2024-01-15 14:30:00",
                "fecha_creacion": "2024-01-01",
            },
            {
                "id": 2,
                "username": "supervisor1",
                "nombre": "Juan Pérez",
                "email": "juan.perez@rexus.app",
                "rol": "Supervisor",
                "activo": True,
                "ultimo_acceso": "2024-01-15 09:15:00",
                "fecha_creacion": "2024-01-02",
            },
            {
                "id": 3,
                "username": "operador1",
                "nombre": "María García",
                "email": "maria.garcia@rexus.app",
                "rol": "Operador",
                "activo": False,
                "ultimo_acceso": "2024-01-10 16:45:00",
                "fecha_creacion": "2024-01-03",
            },
        ]

        self.actualizar_tabla()
        self.actualizar_estadisticas()
        self.loading_manager.hide_loading(self)
        self.actualizar_estado("Usuarios cargados correctamente")

    def actualizar_tabla(self):
        """Actualiza la tabla con los datos filtrados."""
        datos_filtrados = self.aplicar_filtros_datos()

        # Calcular paginación
        total_items = len(datos_filtrados)
        self.total_pages = max(
            1, (total_items + self.items_per_page - 1) // self.items_per_page
        )

        # Obtener datos de la página actual
        inicio = (self.current_page - 1) * self.items_per_page
        fin = inicio + self.items_per_page
        datos_pagina = datos_filtrados[inicio:fin]

        # Llenar tabla
        self.tabla_usuarios.setRowCount(len(datos_pagina))

        for row, usuario in enumerate(datos_pagina):
            items = [
                QTableWidgetItem(str(usuario.get("id", ""))),
                QTableWidgetItem(str(usuario.get("username", ""))),
                QTableWidgetItem(str(usuario.get("nombre", ""))),
                QTableWidgetItem(str(usuario.get("email", ""))),
                QTableWidgetItem(str(usuario.get("rol", ""))),
                QTableWidgetItem("Activo" if usuario.get("activo") else "Inactivo"),
                QTableWidgetItem(str(usuario.get("ultimo_acceso", ""))),
                QTableWidgetItem(str(usuario.get("fecha_creacion", ""))),
            ]

            for col, item in enumerate(items):
                if item is not None:
                    self.tabla_usuarios.setItem(row, col, item)

                    # Colorear según estado
                    if col == 5:  # Columna estado
                        if not usuario.get("activo"):
                            item.setBackground(Qt.GlobalColor.yellow)

        # Actualizar paginación
        self.actualizar_paginacion()

    def aplicar_filtros_datos(self):
        """Aplica los filtros activos a los datos."""
        datos = self.usuarios_data.copy()

        # Filtro de búsqueda
        busqueda = self.campo_busqueda.text().lower()
        if busqueda:
            datos = [
                u
                for u in datos
                if (
                    busqueda in u.get("username", "").lower()
                    or busqueda in u.get("nombre", "").lower()
                    or busqueda in u.get("email", "").lower()
                )
            ]

        # Filtro por rol
        rol = self.combo_rol.currentText()
        if rol and rol != "Todos":
            datos = [u for u in datos if u.get("rol") == rol]

        # Filtro por estado
        estado_filter = self.combo_estado.currentText()
        if estado_filter == "Activos":
            datos = [u for u in datos if u.get("activo")]
        elif estado_filter == "Inactivos":
            datos = [u for u in datos if not u.get("activo")]
        elif estado_filter == "Bloqueados":
            datos = [u for u in datos if u.get("bloqueado", False)]

        return datos

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas."""
        total = len(self.usuarios_data)
        activos = len([u for u in self.usuarios_data if u.get("activo")])
        online = 1  # Simulado
        bloqueados = len([u for u in self.usuarios_data if u.get("bloqueado", False)])

        self.label_total.setText(f"Total usuarios: {total}")
        self.label_activos.setText(f"Activos: {activos}")
        self.label_online.setText(f"En línea: {online}")
        self.label_bloqueados.setText(f"Bloqueados: {bloqueados}")

    def actualizar_paginacion(self):
        """Actualiza los controles de paginación."""
        self.label_pagina.setText(f"Página {self.current_page} de {self.total_pages}")

        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado."""
        self.label_estado.setText(mensaje)
        self.label_registros.setText(f"{len(self.usuarios_data)} usuarios")
        self.label_ultima_actualizacion.setText(
            f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"
        )

    # Métodos de eventos
    def seleccion_cambiada(self):
        """Maneja el cambio de selección en la tabla."""
        hay_seleccion = len(self.tabla_usuarios.selectedItems()) > 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_cambiar_password.setEnabled(hay_seleccion)
        self.btn_activar_desactivar.setEnabled(hay_seleccion)
        self.btn_permisos.setEnabled(hay_seleccion)
        self.btn_sesiones.setEnabled(hay_seleccion)

    def buscar_usuarios(self):
        """Busca usuarios según el texto ingresado."""
        self.current_page = 1
        self.actualizar_tabla()

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        self.current_page = 1
        self.actualizar_tabla()

    def limpiar_busqueda(self):
        """Limpia la búsqueda y filtros."""
        self.campo_busqueda.clear()
        self.combo_rol.setCurrentIndex(0)
        self.combo_estado.setCurrentIndex(0)
        self.current_page = 1
        self.actualizar_tabla()

    # Métodos de paginación
    def ir_a_pagina(self, pagina):
        """Va a una página específica."""
        if 1 <= pagina <= self.total_pages:
            self.current_page = pagina
            self.actualizar_tabla()

    def pagina_anterior(self):
        """Va a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        """Va a la página siguiente."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.actualizar_tabla()

    def ir_a_ultima_pagina(self):
        """Va a la última página."""
        self.current_page = self.total_pages
        self.actualizar_tabla()

    # Métodos de acciones
    def nuevo_usuario(self):
        """Abre el diálogo para crear un nuevo usuario."""
        QMessageBox.information(self, "Nuevo Usuario", "Funcionalidad en desarrollo")

    def editar_usuario(self):
        """Edita el usuario seleccionado."""
        row = self.tabla_usuarios.currentRow()
        if row >= 0:
            username_item = self.tabla_usuarios.item(row, 1)
            if username_item:
                username = username_item.text()
                QMessageBox.information(
                    self, "Editar Usuario", f"Editando usuario: {username}"
                )

    def cambiar_password(self):
        """Cambia la contraseña del usuario seleccionado."""
        row = self.tabla_usuarios.currentRow()
        if row >= 0:
            username_item = self.tabla_usuarios.item(row, 1)
            if username_item:
                username = username_item.text()
                QMessageBox.information(
                    self, "Cambiar Password", f"Cambiando password de: {username}"
                )

    def toggle_estado_usuario(self):
        """Activa/desactiva el usuario seleccionado."""
        row = self.tabla_usuarios.currentRow()
        if row >= 0:
            username_item = self.tabla_usuarios.item(row, 1)
            estado_item = self.tabla_usuarios.item(row, 5)
            if username_item and estado_item:
                username = username_item.text()
                estado_actual = estado_item.text()
                nuevo_estado = (
                    "Activar" if estado_actual == "Inactivo" else "Desactivar"
                )
                reply = QMessageBox.question(
                    self,
                    f"{nuevo_estado} Usuario",
                    f"¿Está seguro de {nuevo_estado.lower()} al usuario {username}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    QMessageBox.information(
                        self,
                        "Estado Cambiado",
                        f"Usuario {username} {nuevo_estado.lower()}do",
                    )

    def gestionar_permisos(self):
        """Gestiona los permisos del usuario seleccionado."""
        row = self.tabla_usuarios.currentRow()
        if row >= 0:
            username_item = self.tabla_usuarios.item(row, 1)
            if username_item:
                username = username_item.text()
                QMessageBox.information(
                    self, "Gestionar Permisos", f"Gestionando permisos de: {username}"
                )

    def ver_sesiones(self):
        """Ver sesiones activas del usuario."""
        row = self.tabla_usuarios.currentRow()
        if row >= 0:
            username_item = self.tabla_usuarios.item(row, 1)
            if username_item:
                username = username_item.text()
                QMessageBox.information(self, "Sesiones", f"Sesiones de: {username}")

    def ver_auditoria(self):
        """Ver auditoría de usuarios."""
        QMessageBox.information(
            self, "Auditoría", "Funcionalidad de auditoría en desarrollo"
        )

    def actualizar_datos(self):
        """Actualiza los datos desde la base de datos."""
        self.loading_manager.show_loading(self, "Actualizando datos de usuarios...")
        QTimer.singleShot(
            1000,
            lambda: (
                self.loading_manager.hide_loading(self),
                self.actualizar_estado("Datos de usuarios actualizados"),
            ),
        )


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    vista = UsuariosViewModern()
    vista.show()
    sys.exit(app.exec())
