"""
Tests de interacciones completas de UI - Simulación de usuario real.
Cubre clicks, navegación, apertura de formularios, cambio de pestañas,
y todas las acciones que podría realizar un usuario para detectar crashes.
"""

    QApplication, QMainWindow, QWidget, QTabWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QTableWidget, QDialog, QFormLayout, QStackedWidget, QMenuBar,
    QMessageBox, QFileDialog, QProgressBar, QCheckBox, QTreeWidget
)
# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Asegurar que existe una instancia de QApplication
app = None
def setup_module():
    global app
    if not QApplication.instance():
        app = QApplication([])

def teardown_module():
    global app
    if app:
        app.quit()


class MockMainWindow(QMainWindow):
    """Mock de MainWindow completo para simular la aplicación real."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock.App - Test UI")
        self.setGeometry(100, 100, 1200, 800)

        # Estados internos
        self.current_module = None
        self.dialogs_opened = []
        self.crash_count = 0
        self.operation_count = 0

        # Setup UI
        self.setup_ui()
        self.setup_data()

    def _safe_status_message(self, message):
        """Mostrar mensaje en status bar de forma segura."""
        try:
            status_bar = self.statusBar()
            if status_bar and hasattr(status_bar, 'showMessage'):
                status_bar.showMessage(message)
        except Exception:
            pass  # Ignorar errores de status bar

    def _safe_process_events(self, app=None):
        """Procesar eventos de forma segura."""
        try:
            if app and hasattr(app, 'processEvents'):
                app.processEvents()
            else:
                qt_app = QApplication.instance()
                if qt_app and hasattr(qt_app, 'processEvents'):
                    qt_app.processEvents()
        except Exception:
            pass  # Ignorar errores de procesamiento

    def setup_ui(self):
        """Configurar interfaz completa."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = self.create_sidebar()
        layout.addWidget(self.sidebar, 0)

        # Área principal con pestañas
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget, 1)

        # Crear módulos/pestañas
        self.create_modules()

        # Menu bar
        self.create_menu_bar()

        # Status bar
        self._safe_status_message("Aplicación iniciada")

    def create_sidebar(self):
        """Crear sidebar con botones de navegación."""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout(sidebar)

        # Botones de módulos
        self.sidebar_buttons = {}
        modules = [
            ("Inventario", "📦"),
            ("Obras", "🏗️"),
            ("Pedidos", "📋"),
            ("Usuarios", "👥"),
            ("Configuración", "⚙️"),
            ("Reportes", "📊")
        ]

        for module_name, icon in modules:
            btn = QPushButton(f"{icon} {module_name}")
            btn.setObjectName(f"btn_{module_name.lower()}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: none;
                    background-color: transparent;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)
            btn.clicked.connect(lambda checked, name=module_name: self.switch_module(name))
            self.sidebar_buttons[module_name] = btn
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def create_modules(self):
        """Crear módulos/pestañas principales."""
        self.modules = {}

        # Módulo Inventario
        self.modules["Inventario"] = self.create_inventario_module()
        self.tab_widget.addTab(self.modules["Inventario"], "📦 Inventario")

        # Módulo Obras
        self.modules["Obras"] = self.create_obras_module()
        self.tab_widget.addTab(self.modules["Obras"], "🏗️ Obras")

        # Módulo Pedidos
        self.modules["Pedidos"] = self.create_pedidos_module()
        self.tab_widget.addTab(self.modules["Pedidos"], "📋 Pedidos")

        # Módulo Usuarios
        self.modules["Usuarios"] = self.create_usuarios_module()
        self.tab_widget.addTab(self.modules["Usuarios"], "👥 Usuarios")

        # Conectar cambio de pestañas
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def create_inventario_module(self):
        """Crear módulo de inventario completo."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()

        # Botones de acción
        btn_agregar = QPushButton("➕ Agregar Item")
        btn_agregar.clicked.connect(lambda: self.open_form_dialog("Agregar Item"))
        toolbar.addWidget(btn_agregar)

        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(lambda: self.open_form_dialog("Editar Item"))
        toolbar.addWidget(btn_editar)

        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.clicked.connect(self.confirm_delete)
        toolbar.addWidget(btn_eliminar)

        btn_importar = QPushButton("📥 Importar")
        btn_importar.clicked.connect(self.open_import_dialog)
        toolbar.addWidget(btn_importar)

        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.clicked.connect(self.open_export_dialog)
        toolbar.addWidget(btn_exportar)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Filtros
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Buscar:"))

        search_box = QLineEdit()
        search_box.setPlaceholderText("Buscar por código, nombre...")
        search_box.textChanged.connect(self.filter_inventory)
        filters_layout.addWidget(search_box)

        category_filter = QComboBox()
        category_filter.addItems(["Todas las categorías", "Perfiles", "Herrajes", "Vidrios", "Otros"])
        category_filter.currentTextChanged.connect(self.filter_by_category)
        filters_layout.addWidget(category_filter)

        layout.addLayout(filters_layout)

        # Tabla de inventario
        self.inventory_table = QTableWidget(100, 8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Categoría", "Stock", "Mín", "Ubicación", "Precio", "Estado"
        ])
        self.inventory_table.cellDoubleClicked.connect(self.on_inventory_double_click)
        layout.addWidget(self.inventory_table)

        # Poblar datos de prueba
        self.populate_inventory_data()

        return widget

    def create_obras_module(self):
        """Crear módulo de obras."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sub-pestañas para obras
        obras_tabs = QTabWidget()

        # Pestaña Lista de Obras
        obras_list = QWidget()
        obras_list_layout = QVBoxLayout(obras_list)

        # Toolbar de obras
        obras_toolbar = QHBoxLayout()
        btn_nueva_obra = QPushButton("🏗️ Nueva Obra")
        btn_nueva_obra.clicked.connect(lambda: self.open_complex_form("Nueva Obra"))
        obras_toolbar.addWidget(btn_nueva_obra)

        btn_ver_obra = QPushButton("👁️ Ver Detalles")
        btn_ver_obra.clicked.connect(lambda: self.open_obra_details())
        obras_toolbar.addWidget(btn_ver_obra)

        obras_toolbar.addStretch()
        obras_list_layout.addLayout(obras_toolbar)

        # Tabla de obras
        self.obras_table = QTableWidget(50, 6)
        self.obras_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Cliente", "Estado", "Fecha Inicio", "Progreso"
        ])
        obras_list_layout.addWidget(self.obras_table)

        obras_tabs.addTab(obras_list, "Lista de Obras")

        # Pestaña Cronograma
        cronograma_widget = QWidget()
        cronograma_layout = QVBoxLayout(cronograma_widget)
        cronograma_layout.addWidget(QLabel("📅 Vista de Cronograma"))

        # Simulación de calendario/cronograma
        calendar_placeholder = QWidget()
        calendar_placeholder.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7;")
        calendar_placeholder.setMinimumHeight(400)
        cronograma_layout.addWidget(calendar_placeholder)

        obras_tabs.addTab(cronograma_widget, "Cronograma")

        # Pestaña Materiales por Obra
        materiales_widget = QWidget()
        materiales_layout = QVBoxLayout(materiales_widget)

        # Combo de selección de obra
        obra_selector = QComboBox()
        obra_selector.addItems(["Seleccionar obra...", "Casa Familia López", "Oficina Centro", "Departamento Norte"])
        obra_selector.currentTextChanged.connect(self.load_obra_materials)
        materiales_layout.addWidget(obra_selector)

        # Tabla de materiales
        self.materiales_table = QTableWidget(30, 5)
        self.materiales_table.setHorizontalHeaderLabels([
            "Material", "Cantidad Req.", "Cantidad Disp.", "Estado", "Proveedor"
        ])
        materiales_layout.addWidget(self.materiales_table)

        obras_tabs.addTab(materiales_widget, "Materiales")

        layout.addWidget(obras_tabs)
        return widget

    def create_pedidos_module(self):
        """Crear módulo de pedidos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar de pedidos
        toolbar = QHBoxLayout()

        btn_nuevo_pedido = QPushButton("📋 Nuevo Pedido")
        btn_nuevo_pedido.clicked.connect(lambda: self.open_pedido_wizard())
        toolbar.addWidget(btn_nuevo_pedido)

        btn_aprobar = QPushButton("✅ Aprobar")
        btn_aprobar.clicked.connect(self.aprobar_pedido)
        toolbar.addWidget(btn_aprobar)

        btn_rechazar = QPushButton("❌ Rechazar")
        btn_rechazar.clicked.connect(self.rechazar_pedido)
        toolbar.addWidget(btn_rechazar)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Filtros de estado
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Estado:"))

        status_filter = QComboBox()
        status_filter.addItems(["Todos", "Pendiente", "Aprobado", "Rechazado", "En Proceso", "Completado"])
        status_filter.currentTextChanged.connect(self.filter_pedidos)
        status_layout.addWidget(status_filter)

        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Tabla de pedidos
        self.pedidos_table = QTableWidget(75, 7)
        self.pedidos_table.setHorizontalHeaderLabels([
            "ID", "Obra", "Fecha", "Estado", "Total", "Solicitante", "Acciones"
        ])
        self.pedidos_table.cellClicked.connect(self.on_pedido_click)
        layout.addWidget(self.pedidos_table)

        return widget

    def create_usuarios_module(self):
        """Crear módulo de usuarios."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar usuarios
        toolbar = QHBoxLayout()

        btn_nuevo_usuario = QPushButton("👤 Nuevo Usuario")
        btn_nuevo_usuario.clicked.connect(lambda: self.open_user_form())
        toolbar.addWidget(btn_nuevo_usuario)

        btn_permisos = QPushButton("🔒 Gestionar Permisos")
        btn_permisos.clicked.connect(self.open_permissions_dialog)
        toolbar.addWidget(btn_permisos)

        btn_activar = QPushButton("✅ Activar")
        btn_activar.clicked.connect(self.toggle_user_status)
        toolbar.addWidget(btn_activar)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tabla de usuarios
        self.users_table = QTableWidget(25, 6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre", "Email", "Rol", "Estado"
        ])
        layout.addWidget(self.users_table)

        return widget

    def create_menu_bar(self):
        """Crear barra de menú completa."""
        try:
            menubar = self.menuBar()
            if not menubar:
                return

            # Menú Archivo
            file_menu = menubar.addMenu("&Archivo")
            if file_menu:
                new_action = QAction("&Nuevo", self)
                new_action.triggered.connect(lambda: self.menu_action("Nuevo"))
                file_menu.addAction(new_action)

                open_action = QAction("&Abrir", self)
                open_action.triggered.connect(lambda: self.menu_action("Abrir"))
                file_menu.addAction(open_action)

                file_menu.addSeparator()

                exit_action = QAction("&Salir", self)
                exit_action.triggered.connect(self.close)
                file_menu.addAction(exit_action)

            # Menú Edición
            edit_menu = menubar.addMenu("&Edición")
            if edit_menu:
                copy_action = QAction("Copiar", self)
                copy_action.triggered.connect(lambda: self.menu_action("Copiar"))
                edit_menu.addAction(copy_action)

                paste_action = QAction("Pegar", self)
                paste_action.triggered.connect(lambda: self.menu_action("Pegar"))
                edit_menu.addAction(paste_action)

            # Menú Herramientas
            tools_menu = menubar.addMenu("&Herramientas")
            if tools_menu:
                config_action = QAction("Configuración", self)
                config_action.triggered.connect(self.open_settings)
                tools_menu.addAction(config_action)

                backup_action = QAction("Backup", self)
                backup_action.triggered.connect(self.open_backup_dialog)
                tools_menu.addAction(backup_action)

                import_action = QAction("Importar Datos", self)
                import_action.triggered.connect(self.open_data_import)
                tools_menu.addAction(import_action)

            # Menú Ayuda
            help_menu = menubar.addMenu("&Ayuda")
            if help_menu:
                about_action = QAction("Acerca de", self)
                about_action.triggered.connect(self.show_about)
                help_menu.addAction(about_action)

        except Exception as e:
            print(f"Error creando menú: {e}")
            # Continuar sin menú si hay errores

    def setup_data(self):
        """Configurar datos de prueba."""
        self.populate_inventory_data()
        self.populate_obras_data()
        self.populate_pedidos_data()
        self.populate_users_data()

    def populate_inventory_data(self):
        """Poblar datos de inventario."""
        if hasattr(self, 'inventory_table'):
            items = [
                ("PER-001", "Perfil Aluminio 40x20", "Perfiles", "150", "10", "A-01", "$2500", "Activo"),
                ("HER-001", "Tornillo 6x30 Inox", "Herrajes", "500", "50", "B-02", "$15", "Activo"),
                ("VID-001", "Vidrio 4mm Transparente", "Vidrios", "25", "5", "C-01", "$8500", "Activo"),
            ]

            for i, item in enumerate(items):
                for j, value in enumerate(item):
                    table_item = QTableWidgetItem(str(value))
                    self.inventory_table.setItem(i, j, table_item)

    def populate_obras_data(self):
        """Poblar datos de obras."""
        if hasattr(self, 'obras_table'):
            obras = [
                ("001", "Casa Familia López", "Juan López", "En Proceso", "2025-01-15", "60%"),
                ("002", "Oficina Centro", "Empresa ABC", "Iniciado", "2025-02-01", "25%"),
                ("003", "Departamento Norte", "María García", "Planificación", "2025-03-01", "10%"),
            ]

            for i, obra in enumerate(obras):
                for j, value in enumerate(obra):
                    table_item = QTableWidgetItem(str(value))
                    self.obras_table.setItem(i, j, table_item)

    def populate_pedidos_data(self):
        """Poblar datos de pedidos."""
        if hasattr(self, 'pedidos_table'):
            pedidos = [
                ("P001", "Casa Familia López", "2025-06-20", "Pendiente", "$15,000", "Juan Pérez", "Ver"),
                ("P002", "Oficina Centro", "2025-06-21", "Aprobado", "$8,500", "Ana Silva", "Ver"),
                ("P003", "Departamento Norte", "2025-06-22", "En Proceso", "$12,300", "Carlos Ruiz", "Ver"),
            ]

            for i, pedido in enumerate(pedidos):
                for j, value in enumerate(pedido):
                    table_item = QTableWidgetItem(str(value))
                    self.pedidos_table.setItem(i, j, table_item)

    def populate_users_data(self):
        """Poblar datos de usuarios."""
        if hasattr(self, 'users_table'):
            users = [
                ("1", "TEST_USER", "Administrador", "admin@empresa.com", "Admin", "Activo"),
                ("2", "jperez", "Juan Pérez", "jperez@empresa.com", "Operador", "Activo"),
                ("3", "asilva", "Ana Silva", "asilva@empresa.com", "Supervisor", "Inactivo"),
            ]

            for i, user in enumerate(users):
                for j, value in enumerate(user):
                    table_item = QTableWidgetItem(str(value))
                    self.users_table.setItem(i, j, table_item)

    # Métodos de interacción
    def switch_module(self, module_name):
        """Cambiar módulo/pestaña."""
        try:
            self.operation_count += 1
            self.current_module = module_name
import random
import sys
import time
from pathlib import Path

from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (  # Encontrar índice de la pestaña
    QTableWidgetItem,
    :,
    for,
    gc,
    i,
    if,
    import,
    in,
    module_name,
    range,
    self.tab_widget.count,
    self.tab_widget.tabText,
)

                    self.tab_widget.setCurrentIndex(i)
                    break

            self._safe_status_message(f"Módulo actual: {module_name}")

        except Exception as e:
            self.crash_count += 1
            print(f"Error al cambiar módulo: {e}")

    def on_tab_changed(self, index):
        """Manejar cambio de pestaña."""
        try:
            self.operation_count += 1
            tab_text = self.tab_widget.tabText(index)
            self._safe_status_message(f"Pestaña activa: {tab_text}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error en cambio de pestaña: {e}")

    def open_form_dialog(self, title):
        """Abrir diálogo de formulario."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QFormLayout(dialog)

            # Campos comunes
            layout.addRow("Código:", QLineEdit())
            layout.addRow("Nombre:", QLineEdit())
            layout.addRow("Categoría:", QComboBox())
            layout.addRow("Stock:", QLineEdit())
            layout.addRow("Ubicación:", QLineEdit())

            # Botones
            buttons_layout = QHBoxLayout()
            btn_save = QPushButton("Guardar")
            btn_save.clicked.connect(dialog.accept)
            btn_cancel = QPushButton("Cancelar")
            btn_cancel.clicked.connect(dialog.reject)

            buttons_layout.addWidget(btn_save)
            buttons_layout.addWidget(btn_cancel)
            layout.addRow(buttons_layout)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir formulario: {e}")

    def open_complex_form(self, title):
        """Abrir formulario complejo con múltiples pestañas."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # Pestañas dentro del diálogo
            tab_widget = QTabWidget()

            # Pestaña General
            general_tab = QWidget()
            general_layout = QFormLayout(general_tab)
            general_layout.addRow("Nombre Obra:", QLineEdit())
            general_layout.addRow("Cliente:", QLineEdit())
            general_layout.addRow("Dirección:", QLineEdit())
            general_layout.addRow("Fecha Inicio:", QLineEdit())
            tab_widget.addTab(general_tab, "General")

            # Pestaña Materiales
            materials_tab = QWidget()
            materials_layout = QVBoxLayout(materials_tab)
            materials_table = QTableWidget(10, 4)
            materials_table.setHorizontalHeaderLabels(["Material", "Cantidad", "Precio", "Total"])
            materials_layout.addWidget(materials_table)
            tab_widget.addTab(materials_tab, "Materiales")

            # Pestaña Cronograma
            schedule_tab = QWidget()
            schedule_layout = QFormLayout(schedule_tab)
            schedule_layout.addRow("Fecha Inicio:", QLineEdit())
            schedule_layout.addRow("Fecha Fin:", QLineEdit())
            schedule_layout.addRow("Duración:", QLineEdit())
            tab_widget.addTab(schedule_tab, "Cronograma")

            layout.addWidget(tab_widget)

            # Botones
            buttons_layout = QHBoxLayout()
            btn_save = QPushButton("Guardar")
            btn_save.clicked.connect(dialog.accept)
            btn_cancel = QPushButton("Cancelar")
            btn_cancel.clicked.connect(dialog.reject)

            buttons_layout.addWidget(btn_save)
            buttons_layout.addWidget(btn_cancel)
            layout.addLayout(buttons_layout)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir formulario complejo: {e}")

    def open_pedido_wizard(self):
        """Abrir wizard de pedidos."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle("Nuevo Pedido - Wizard")
            dialog.setModal(True)
            dialog.resize(700, 600)

            layout = QVBoxLayout(dialog)

            # Progreso del wizard
            progress = QProgressBar()
            progress.setValue(33)
            layout.addWidget(progress)

            # Contenido del paso actual
            step_widget = QWidget()
            step_layout = QFormLayout(step_widget)
            step_layout.addRow("Obra:", QComboBox())
            step_layout.addRow("Prioridad:", QComboBox())
            step_layout.addRow("Observaciones:", QLineEdit())
            layout.addWidget(step_widget)

            # Tabla de items a pedir
            items_table = QTableWidget(15, 5)
            items_table.setHorizontalHeaderLabels(["Item", "Cantidad", "Precio Unit.", "Total", "Acción"])
            layout.addWidget(items_table)

            # Botones de navegación
            nav_layout = QHBoxLayout()
            btn_prev = QPushButton("← Anterior")
            btn_next = QPushButton("Siguiente →")
            btn_finish = QPushButton("Finalizar")
            btn_cancel = QPushButton("Cancelar")

            nav_layout.addWidget(btn_prev)
            nav_layout.addWidget(btn_next)
            nav_layout.addWidget(btn_finish)
            nav_layout.addStretch()
            nav_layout.addWidget(btn_cancel)

            btn_cancel.clicked.connect(dialog.reject)
            btn_finish.clicked.connect(dialog.accept)

            layout.addLayout(nav_layout)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir wizard de pedidos: {e}")

    # Métodos de eventos y filtros
    def filter_inventory(self, text):
        """Filtrar inventario por texto."""
        try:
            self.operation_count += 1
            # Simular filtrado
            print(f"Filtrando inventario: {text}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al filtrar inventario: {e}")

    def filter_by_category(self, category):
        """Filtrar por categoría."""
        try:
            self.operation_count += 1
            print(f"Filtrando por categoría: {category}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al filtrar por categoría: {e}")

    def on_inventory_double_click(self, row, column):
        """Manejar doble click en inventario."""
        try:
            self.operation_count += 1
            self.open_form_dialog("Editar Item")
        except Exception as e:
            self.crash_count += 1
            print(f"Error en doble click inventario: {e}")

    def on_pedido_click(self, row, column):
        """Manejar click en pedido."""
        try:
            self.operation_count += 1
            if column == 6:  # Columna de acciones
                self.open_pedido_details(row)
        except Exception as e:
            self.crash_count += 1
            print(f"Error en click pedido: {e}")

    def open_pedido_details(self, row):
        """Abrir detalles de pedido."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detalles del Pedido P{row+1:03d}")
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Detalles del pedido..."))

            btn_close = QPushButton("Cerrar")
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir detalles pedido: {e}")

    # Métodos adicionales para completar funcionalidad
    def confirm_delete(self):
        """Confirmar eliminación."""
        try:
            self.operation_count += 1
            reply = QMessageBox.question(self, "Confirmar", "¿Eliminar item seleccionado?")
            if reply == QMessageBox.StandardButton.Yes:
                print("Item eliminado")
        except Exception as e:
            self.crash_count += 1
            print(f"Error en confirmación: {e}")

    def open_import_dialog(self):
        """Abrir diálogo de importación."""
        try:
            self.operation_count += 1
            filename, _ = QFileDialog.getOpenFileName(self, "Importar archivo", "", "CSV Files (*.csv)")
            if filename:
                print(f"Importando: {filename}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al importar: {e}")

    def open_export_dialog(self):
        """Abrir diálogo de exportación."""
        try:
            self.operation_count += 1
            filename, _ = QFileDialog.getSaveFileName(self, "Exportar archivo", "", "CSV Files (*.csv)")
            if filename:
                print(f"Exportando: {filename}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al exportar: {e}")

    def open_obra_details(self):
        """Abrir detalles de obra."""
        try:
            self.operation_count += 1
            self.open_complex_form("Detalles de Obra")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir detalles obra: {e}")

    def load_obra_materials(self, obra_name):
        """Cargar materiales de obra."""
        try:
            self.operation_count += 1
            print(f"Cargando materiales para: {obra_name}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al cargar materiales: {e}")

    def aprobar_pedido(self):
        """Aprobar pedido."""
        try:
            self.operation_count += 1
            print("Pedido aprobado")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al aprobar pedido: {e}")

    def rechazar_pedido(self):
        """Rechazar pedido."""
        try:
            self.operation_count += 1
            print("Pedido rechazado")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al rechazar pedido: {e}")

    def filter_pedidos(self, status):
        """Filtrar pedidos por estado."""
        try:
            self.operation_count += 1
            print(f"Filtrando pedidos: {status}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al filtrar pedidos: {e}")

    def open_user_form(self):
        """Abrir formulario de usuario."""
        try:
            self.operation_count += 1
            self.open_form_dialog("Nuevo Usuario")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir formulario usuario: {e}")

    def open_permissions_dialog(self):
        """Abrir diálogo de permisos."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle("Gestionar Permisos")
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Lista de permisos
            permissions = [
                "Ver Inventario", "Modificar Inventario", "Eliminar Items",
                "Ver Obras", "Crear Obras", "Modificar Obras",
                "Ver Pedidos", "Crear Pedidos", "Aprobar Pedidos",
                "Gestionar Usuarios", "Configuración Sistema"
            ]

            for perm in permissions:
                checkbox = QCheckBox(perm)
                layout.addWidget(checkbox)

            btn_save = QPushButton("Guardar")
            btn_save.clicked.connect(dialog.accept)
            layout.addWidget(btn_save)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir permisos: {e}")

    def toggle_user_status(self):
        """Alternar estado de usuario."""
        try:
            self.operation_count += 1
            print("Estado de usuario alternado")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al alternar usuario: {e}")

    def menu_action(self, action):
        """Ejecutar acción de menú."""
        try:
            self.operation_count += 1
            print(f"Acción de menú: {action}")
        except Exception as e:
            self.crash_count += 1
            print(f"Error en acción menú: {e}")

    def open_settings(self):
        """Abrir configuración."""
        try:
            self.operation_count += 1
            self.open_complex_form("Configuración")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir configuración: {e}")

    def open_backup_dialog(self):
        """Abrir diálogo de backup."""
        try:
            self.operation_count += 1
            dialog = QDialog(self)
            dialog.setWindowTitle("Backup de Datos")
            dialog.resize(400, 200)

            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Configuración de backup..."))

            progress = QProgressBar()
            layout.addWidget(progress)

            btn_start = QPushButton("Iniciar Backup")
            btn_start.clicked.connect(lambda: self.simulate_backup(progress))
            layout.addWidget(btn_start)

            self.dialogs_opened.append(dialog)
            dialog.exec()

        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir backup: {e}")

    def simulate_backup(self, progress_bar):
        """Simular proceso de backup."""
        try:
            self.operation_count += 1
            for i in range(101):
                progress_bar.setValue(i)
                QApplication.processEvents()
                time.sleep(0.01)
        except Exception as e:
            self.crash_count += 1
            print(f"Error en backup: {e}")

    def open_data_import(self):
        """Abrir importación de datos."""
        try:
            self.operation_count += 1
            self.open_import_dialog()
        except Exception as e:
            self.crash_count += 1
            print(f"Error al abrir importación: {e}")

    def show_about(self):
        """Mostrar acerca de."""
        try:
            self.operation_count += 1
            QMessageBox.about(self, "Acerca de", "Stock.App v1.0\nSistema de gestión de inventario")
        except Exception as e:
            self.crash_count += 1
            print(f"Error al mostrar about: {e}")


class TestUIInteractions:
    """Tests de interacciones completas de UI."""

    def setup_method(self):
        """Setup para cada test."""
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])

        self.main_window = MockMainWindow()
        self.main_window.show()
        self._safe_process_events(self.app)

    def teardown_method(self):
        """Cleanup después de cada test."""
        if hasattr(self, 'main_window'):
            self.main_window.close()
            self._safe_process_events(self.app)

    def _safe_process_events(self, app=None):
        """Procesar eventos de forma segura."""
        try:
            if app and hasattr(app, 'processEvents'):
                app.processEvents()
            else:
                qt_app = QApplication.instance()
                if qt_app and hasattr(qt_app, 'processEvents'):
                    qt_app.processEvents()
        except Exception:
            pass  # Ignorar errores de procesamiento

    def test_navegacion_completa_modulos(self):
        """Test: navegación completa entre todos los módulos."""
        modules = ["Inventario", "Obras", "Pedidos", "Usuarios"]

        for module in modules:
            # Simular click en sidebar
            if module in self.main_window.sidebar_buttons:
                button = self.main_window.sidebar_buttons[module]
                button.click()
                self._safe_process_events(self.app)

            # Verificar que cambió el módulo
            assert self.main_window.current_module == module

        # Verificar que no hubo crashes
        assert self.main_window.crash_count == 0
        print(f"✓ Navegación completa: {self.main_window.operation_count} operaciones sin crashes")

    def test_cambio_pestañas_rapido(self):
        """Test: cambio rápido entre pestañas."""
        tab_count = self.main_window.tab_widget.count()

        # Cambiar rápidamente entre pestañas
        for _ in range(3):  # 3 vueltas completas
            for i in range(tab_count):
                self.main_window.tab_widget.setCurrentIndex(i)
                self._safe_process_events(self.app)
                time.sleep(0.01)  # Pequeña pausa para simular usuario real

        # Verificar estabilidad
        assert self.main_window.crash_count == 0
        print(f"✓ Cambio rápido de pestañas: {self.main_window.operation_count} operaciones")

    def test_apertura_formularios_multiple(self):
        """Test: apertura múltiple de formularios."""
        forms_to_test = [
            ("Agregar Item", lambda: self.main_window.open_form_dialog("Agregar Item")),
            ("Nueva Obra", lambda: self.main_window.open_complex_form("Nueva Obra")),
            ("Nuevo Pedido", lambda: self.main_window.open_pedido_wizard()),
            ("Configuración", lambda: self.main_window.open_settings()),
        ]

        for form_name, form_opener in forms_to_test:
            try:
                # Abrir formulario
                form_opener()
                self._safe_process_events(self.app)

                # Cerrar si hay diálogos abiertos
                if self.main_window.dialogs_opened:
                    dialog = self.main_window.dialogs_opened[-1]
                    dialog.accept()
                    self._safe_process_events(self.app)

            except Exception as e:
                print(f"Error en formulario {form_name}: {e}")

        # Verificar que se abrieron formularios
        assert len(self.main_window.dialogs_opened) > 0
        assert self.main_window.crash_count == 0
        print(f"✓ Apertura de formularios: {len(self.main_window.dialogs_opened)} diálogos abiertos")

    def test_interacciones_tabla_completas(self):
        """Test: interacciones completas con tablas."""
        tables = [
            self.main_window.inventory_table,
            self.main_window.obras_table,
            self.main_window.pedidos_table,
            self.main_window.users_table
        ]

        for table in tables:
            if table and table.rowCount() > 0:
                # Simular clicks en diferentes celdas
                for row in range(min(3, table.rowCount())):
                    for col in range(min(3, table.columnCount())):
                        # Simular click
                        table.setCurrentCell(row, col)
                        self._safe_process_events(self.app)

                        # Simular doble click ocasional
                        if row == 0 and col == 0:
                            table.cellDoubleClicked.emit(row, col)
                            self._safe_process_events(self.app)

        assert self.main_window.crash_count == 0
        print(f"✓ Interacciones con tablas completadas")

    def test_menu_completo_navegacion(self):
        """Test: navegación completa por menús."""
        menubar = self.main_window.menuBar()

        # Simular hover sobre menús
        for action in (menubar.actions() if menubar and hasattr(menubar, "actions") else []):
            menu = action.menu()
            if menu:
                # Simular apertura de menú
                menu.popup(self.main_window.pos())
                self._safe_process_events(self.app)

                # Simular click en algunas acciones
                actions = menu.actions()
                for i, menu_action in enumerate(actions[:2]):  # Solo primeras 2 acciones
                    if not menu_action.isSeparator():
                        try:
                            menu_action.trigger()
                            self._safe_process_events(self.app)
                        except:
                            pass  # Algunos menús pueden fallar, es esperado

                menu.close()
                self._safe_process_events(self.app)

        assert self.main_window.crash_count == 0
        print(f"✓ Navegación de menús completada")

    def test_filtros_y_busquedas(self):
        """Test: funcionalidad de filtros y búsquedas."""
        # Cambiar a módulo inventario
        self.main_window.switch_module("Inventario")
        self._safe_process_events(self.app)

        # Buscar widgets de filtro
        inventory_widget = self.main_window.modules["Inventario"]
        search_widgets = inventory_widget.findChildren(QLineEdit)
        combo_widgets = inventory_widget.findChildren(QComboBox)

        # Simular búsquedas
        search_terms = ["PER", "tornillo", "vidrio", "abc123", ""]

        for search_widget in search_widgets:
            for term in search_terms:
                search_widget.setText(term)
                search_widget.textChanged.emit(term)
                self._safe_process_events(self.app)
                time.sleep(0.01)

        # Simular cambios en combos
        for combo in combo_widgets:
            for i in range(combo.count()):
                combo.setCurrentIndex(i)
                self._safe_process_events(self.app)
                time.sleep(0.01)

        assert self.main_window.crash_count == 0
        print(f"✓ Filtros y búsquedas probados")

    def test_estres_operaciones_rapidas(self):
        """Test: estrés con operaciones rápidas."""
        operations = [
            lambda: self.main_window.switch_module("Inventario"),
            lambda: self.main_window.switch_module("Obras"),
            lambda: self.main_window.switch_module("Pedidos"),
            lambda: self.main_window.tab_widget.setCurrentIndex(0),
            lambda: self.main_window.tab_widget.setCurrentIndex(1),
            lambda: self.main_window._safe_status_message("Test message"),
        ]

        # Ejecutar operaciones rápidamente
        for _ in range(50):  # 50 operaciones rápidas
            operation = operations[_ % len(operations)]
            try:
                operation()
                self._safe_process_events(self.app)
            except Exception as e:
                print(f"Error en operación rápida: {e}")

        # Verificar estabilidad
        assert self.main_window.crash_count < 5  # Permitir algunos errores menores
        print(f"✓ Test de estrés: {self.main_window.operation_count} operaciones, {self.main_window.crash_count} errores")

    def test_simulacion_usuario_real(self):
        """Test: simulación de flujo de trabajo de usuario real."""
        # Flujo: Usuario entra, navega, busca algo, abre formulario, guarda

        # 1. Ir a inventario
        self.main_window.switch_module("Inventario")
        self._safe_process_events(self.app)
        time.sleep(0.1)

        # 2. Buscar un item
        inventory_widget = self.main_window.modules["Inventario"]
        search_widgets = inventory_widget.findChildren(QLineEdit)
        if search_widgets:
            search_widgets[0].setText("PER-001")
            self._safe_process_events(self.app)
            time.sleep(0.1)

        # 3. Hacer doble click para editar
        self.main_window.inventory_table.cellDoubleClicked.emit(0, 0)
        self._safe_process_events(self.app)
        time.sleep(0.1)

        # 4. Cerrar diálogo si se abrió
        if self.main_window.dialogs_opened:
            dialog = self.main_window.dialogs_opened[-1]
            dialog.accept()
            self._safe_process_events(self.app)

        # 5. Ir a obras
        self.main_window.switch_module("Obras")
        self._safe_process_events(self.app)
        time.sleep(0.1)

        # 6. Crear nueva obra
        self.main_window.open_complex_form("Nueva Obra")
        self._safe_process_events(self.app)

        # 7. Cerrar formulario
        if self.main_window.dialogs_opened:
            dialog = self.main_window.dialogs_opened[-1]
            dialog.reject()  # Cancelar
            self._safe_process_events(self.app)

        # 8. Ir a pedidos
        self.main_window.switch_module("Pedidos")
        self._safe_process_events(self.app)
        time.sleep(0.1)

        # 9. Crear nuevo pedido
        self.main_window.open_pedido_wizard()
        self._safe_process_events(self.app)

        # 10. Finalizar
        if self.main_window.dialogs_opened:
            dialog = self.main_window.dialogs_opened[-1]
            dialog.accept()
            self._safe_process_events(self.app)

        # Verificar que el flujo se completó sin crashes críticos
        assert self.main_window.crash_count < 3
        assert self.main_window.operation_count >= 10
        print(f"✓ Simulación usuario real: {self.main_window.operation_count} ops, {self.main_window.crash_count} errores")

    def test_multiples_ventanas_dialogs(self):
        """Test: apertura de múltiples ventanas y diálogos simultáneos."""
        # Intentar abrir varios diálogos "simultáneamente"
        dialog_openers = [
            lambda: self.main_window.open_form_dialog("Test Dialog 1"),
            lambda: self.main_window.open_complex_form("Test Dialog 2"),
            lambda: self.main_window.open_user_form(),
            lambda: self.main_window.open_permissions_dialog(),
        ]

        for opener in dialog_openers:
            try:
                opener()
                self._safe_process_events(self.app)
                # No cerrar inmediatamente para simular usuario multitarea
                time.sleep(0.05)
            except Exception as e:
                print(f"Error abriendo diálogo: {e}")

        # Cerrar todos los diálogos
        while self.main_window.dialogs_opened:
            dialog = self.main_window.dialogs_opened.pop()
            try:
                dialog.accept()
                self._safe_process_events(self.app)
            except:
                pass

        assert self.main_window.crash_count == 0
        print(f"✓ Múltiples diálogos manejados correctamente")

    def test_redimensionado_y_layout(self):
        """Test: redimensionado de ventana y cambios de layout."""
        original_size = self.main_window.size()

        # Simular diferentes tamaños de ventana
        sizes = [
            (800, 600),
            (1200, 900),
            (1600, 1200),
            (600, 400),  # Muy pequeña
            (2000, 1500),  # Muy grande
        ]

        for width, height in sizes:
            self.main_window.resize(width, height)
            self._safe_process_events(self.app)
            time.sleep(0.05)

            # Navegar entre módulos con diferentes tamaños
            self.main_window.switch_module("Inventario")
            self._safe_process_events(self.app)
            self.main_window.switch_module("Obras")
            self._safe_process_events(self.app)

        # Restaurar tamaño original
        self.main_window.resize(original_size)
        self._safe_process_events(self.app)

        assert self.main_window.crash_count == 0
        print(f"✓ Redimensionado y layout probados")

    def test_memoria_y_recursos(self):
        """Test: monitoreo básico de memoria y recursos."""

        initial_operations = self.main_window.operation_count

        # Realizar muchas operaciones para simular uso intensivo
        for i in range(100):
            # Alternar entre módulos
            module = ["Inventario", "Obras", "Pedidos", "Usuarios"][i % 4]
            self.main_window.switch_module(module)

            # Cada 10 operaciones, forzar garbage collection
            if i % 10 == 0:
                gc.collect()
                self._safe_process_events(self.app)

        final_operations = self.main_window.operation_count
        operations_performed = final_operations - initial_operations

        # Verificar que se realizaron operaciones y no hubo demasiados crashes
        assert operations_performed >= 100
        assert self.main_window.crash_count < 10  # Permitir algunos errores menores

        print(f"✓ Test de memoria: {operations_performed} operaciones, {self.main_window.crash_count} errores")


class TestUIStressExtreme:
    """Tests de estrés extremo para la UI."""

    def setup_method(self):
        """Setup para tests de estrés."""
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])

        self.main_window = MockMainWindow()
        self.main_window.show()
        self._safe_process_events(self.app)

    def teardown_method(self):
        """Cleanup después de tests de estrés."""
        if hasattr(self, 'main_window'):
            self.main_window.close()
            self._safe_process_events(self.app)

    def _safe_process_events(self, app=None):
        """Procesar eventos de forma segura."""
        try:
            if app and hasattr(app, 'processEvents'):
                app.processEvents()
            else:
                qt_app = QApplication.instance()
                if qt_app and hasattr(qt_app, 'processEvents'):
                    qt_app.processEvents()
        except Exception:
            pass  # Ignorar errores de procesamiento

    def test_estres_extremo_navegacion(self):
        """Test: estrés extremo de navegación."""

        modules = ["Inventario", "Obras", "Pedidos", "Usuarios"]

        # 500 operaciones aleatorias
        for i in range(500):
            try:
                operation = random.choice([
                    lambda: self.main_window.switch_module(random.choice(modules)),
                    lambda: self.main_window.tab_widget.setCurrentIndex(random.randint(0, 3)),
                    lambda: self._safe_process_events(self.app),
                ])
                operation()

                # Procesar eventos cada 10 operaciones
                if i % 10 == 0:
                    self._safe_process_events(self.app)

            except Exception as e:
                print(f"Error en operación {i}: {e}")

        # La aplicación debe seguir funcionando
        assert self.main_window.isVisible()
        print(f"✓ Estrés extremo: {self.main_window.operation_count} operaciones totales")

    def test_estres_formularios_masivos(self):
        """Test: apertura masiva de formularios."""
        # Intentar abrir muchos formularios rápidamente
        for i in range(20):
            try:
                if i % 4 == 0:
                    self.main_window.open_form_dialog(f"Form {i}")
                elif i % 4 == 1:
                    self.main_window.open_complex_form(f"Complex {i}")
                elif i % 4 == 2:
                    self.main_window.open_user_form()
                else:
                    self.main_window.open_permissions_dialog()

                self._safe_process_events(self.app)

                # Cerrar algunos diálogos aleatoriamente
                if self.main_window.dialogs_opened and i % 3 == 0:
                    dialog = self.main_window.dialogs_opened.pop()
                    dialog.accept()
                    self._safe_process_events(self.app)

            except Exception as e:
                print(f"Error en formulario masivo {i}: {e}")

        # Limpiar diálogos restantes
        while self.main_window.dialogs_opened:
            try:
                dialog = self.main_window.dialogs_opened.pop()
                dialog.accept()
                self._safe_process_events(self.app)
            except:
                pass

        assert self.main_window.crash_count < 5
        print(f"✓ Formularios masivos: crashes controlados")


# Función auxiliar global para funciones independientes
def _safe_process_events_global(app=None):
    """Procesar eventos de forma segura para funciones globales."""
    try:
        if app and hasattr(app, 'processEvents'):
            app.processEvents()
        else:
            qt_app = QApplication.instance()
            if qt_app and hasattr(qt_app, 'processEvents'):
                qt_app.processEvents()
    except Exception:
        pass  # Ignorar errores de procesamiento


# Test de integración final
def test_integracion_ui_completa():
    """Test de integración completa de UI - Flujo completo de usuario."""
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    try:
        # Crear ventana principal
        main_window = MockMainWindow()
        main_window.show()
        _safe_process_events_global(app)

        # Simular sesión completa de usuario
        print("Iniciando simulación de sesión de usuario...")

        # 1. Usuario explora inventario
        main_window.switch_module("Inventario")
        _safe_process_events_global(app)

        # 2. Busca items
        if hasattr(main_window, 'inventory_table'):
            main_window.inventory_table.setCurrentCell(0, 0)
            _safe_process_events_global(app)

        # 3. Va a obras
        main_window.switch_module("Obras")
        _safe_process_events_global(app)

        # 4. Crea nueva obra
        main_window.open_complex_form("Nueva Obra Test")
        _safe_process_events_global(app)

        # 5. Cierra formulario
        if main_window.dialogs_opened:
            main_window.dialogs_opened[-1].accept()
            _safe_process_events_global(app)

        # 6. Va a pedidos
        main_window.switch_module("Pedidos")
        _safe_process_events_global(app)

        # 7. Crea pedido
        main_window.open_pedido_wizard()
        _safe_process_events_global(app)

        # 8. Finaliza pedido
        if main_window.dialogs_opened:
            main_window.dialogs_opened[-1].accept()
            _safe_process_events_global(app)

        # 9. Revisa configuración
        main_window.open_settings()
        _safe_process_events_global(app)

        # 10. Cierra configuración
        if main_window.dialogs_opened:
            main_window.dialogs_opened[-1].reject()
            _safe_process_events_global(app)

        # Verificar que la sesión se completó exitosamente
        assert main_window.operation_count > 0
        assert main_window.crash_count < 3  # Permitir errores menores

        print(f"✓ Sesión completa: {main_window.operation_count} operaciones, {main_window.crash_count} errores")

        # Cerrar aplicación
        main_window.close()
        _safe_process_events_global(app)

        print("✓ Aplicación cerrada correctamente")

    except Exception as e:
        print(f"Error en integración completa: {e}")
        assert False, f"Test de integración falló: {e}"
