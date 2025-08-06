"""
Script de Prueba Completa - Prioridades 1, 2 y 3
Verifica funcionamiento de navegación por teclado e integración del sistema
"""

import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Añadir path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rexus.utils.keyboard_help import ShortcutHelpDialog
from rexus.utils.keyboard_navigation import (
    KeyboardNavigationMode,
    setup_keyboard_navigation,
)
from rexus.utils.system_integration import (
    create_module,
    get_system_integration_manager,
    setup_system_integration,
)


class TestMainWindow(QMainWindow):
    """Ventana principal de prueba."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Sistema Integrado - Rexus.app")
        self.setGeometry(100, 100, 1000, 700)

        # Configurar el sistema de integración
        self.system_manager = setup_system_integration()

        self.setup_ui()
        self.setup_keyboard_navigation()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Panel de control
        control_layout = QHBoxLayout()

        # Botones para cargar módulos
        self.btn_herrajes = QPushButton("Cargar Herrajes")
        self.btn_herrajes.clicked.connect(lambda: self.load_module("herrajes"))

        self.btn_usuarios = QPushButton("Cargar Usuarios")
        self.btn_usuarios.clicked.connect(lambda: self.load_module("usuarios"))

        self.btn_inventario = QPushButton("Cargar Inventario")
        self.btn_inventario.clicked.connect(lambda: self.load_module("inventario"))

        self.btn_help = QPushButton("Ayuda (F1)")
        self.btn_help.clicked.connect(self.show_keyboard_help)

        self.btn_status = QPushButton("Estado Sistema")
        self.btn_status.clicked.connect(self.show_system_status)

        control_layout.addWidget(self.btn_herrajes)
        control_layout.addWidget(self.btn_usuarios)
        control_layout.addWidget(self.btn_inventario)
        control_layout.addWidget(self.btn_help)
        control_layout.addWidget(self.btn_status)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Área de contenido del módulo
        self.module_container = QWidget()
        self.module_container.setMinimumHeight(400)
        self.module_container.setStyleSheet("""
            QWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.module_container)

        # Log de eventos
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(150)
        self.log_area.setReadOnly(True)
        self.log_area.setPlainText(
            "Sistema de integración inicializado.\nUse F1 para ver atajos de teclado.\n"
        )
        layout.addWidget(self.log_area)

        # Conectar eventos del sistema
        self.system_manager.module_loaded.connect(self.on_module_loaded)
        self.system_manager.error_occurred.connect(self.on_error_occurred)

    def setup_keyboard_navigation(self):
        """Configura la navegación por teclado para la ventana principal."""
        self.nav_manager = setup_keyboard_navigation(self, KeyboardNavigationMode.FORM)

        # Atajos personalizados
        self.nav_manager.register_action(
            "cargar_herrajes", lambda: self.load_module("herrajes"), ["Ctrl+1"]
        )
        self.nav_manager.register_action(
            "cargar_usuarios", lambda: self.load_module("usuarios"), ["Ctrl+2"]
        )
        self.nav_manager.register_action(
            "cargar_inventario", lambda: self.load_module("inventario"), ["Ctrl+3"]
        )
        self.nav_manager.register_action(
            "mostrar_estado", self.show_system_status, ["Ctrl+I"]
        )

    def load_module(self, module_name: str):
        """Carga un módulo específico."""
        self.log_area.append(f"Cargando módulo: {module_name}...")

        try:
            # Limpiar contenedor anterior
            current_layout = self.module_container.layout()
            if current_layout:
                for i in reversed(range(current_layout.count())):
                    child_item = current_layout.takeAt(i)
                    if child_item:
                        widget = child_item.widget()
                        if widget:
                            widget.deleteLater()

            # Crear nuevo layout si no existe
            if not current_layout:
                QVBoxLayout(self.module_container)

            # Cargar módulo usando el sistema de integración
            module_widget = create_module(module_name, self.module_container)

            if module_widget:
                final_layout = self.module_container.layout()
                if final_layout:
                    final_layout.addWidget(module_widget)
                self.log_area.append(f"✓ Módulo {module_name} cargado exitosamente")

                # Mostrar información del módulo
                module_info = self.system_manager.get_module_info(module_name)
                if module_info:
                    self.log_area.append(f"  - {module_info.description}")
                    self.log_area.append(
                        f"  - Navegación: {'✓' if module_info.keyboard_enabled else '✗'}"
                    )
                    self.log_area.append(
                        f"  - Errores: {'✓' if module_info.error_enabled else '✗'}"
                    )
                    self.log_area.append(
                        f"  - Loading: {'✓' if module_info.loading_enabled else '✗'}"
                    )
            else:
                self.log_area.append(
                    f"✗ Error: No se pudo cargar el módulo {module_name}"
                )

        except Exception as e:
            self.log_area.append(f"✗ Error cargando {module_name}: {str(e)}")

    def show_keyboard_help(self):
        """Muestra la ayuda de atajos de teclado."""
        shortcuts = self.nav_manager.get_shortcuts_help()

        # Añadir atajos específicos de la aplicación
        app_shortcuts = {
            "Cargar Herrajes": "Ctrl+1",
            "Cargar Usuarios": "Ctrl+2",
            "Cargar Inventario": "Ctrl+3",
            "Estado del Sistema": "Ctrl+I",
            "Ayuda": "F1",
        }

        all_shortcuts = {**shortcuts, **app_shortcuts}

        dialog = ShortcutHelpDialog(all_shortcuts, self)
        dialog.exec()

    def show_system_status(self):
        """Muestra el estado del sistema."""
        status = self.system_manager.get_system_status()

        self.log_area.append("=== ESTADO DEL SISTEMA ===")
        self.log_area.append(f"Módulos registrados: {status['modules_registered']}")
        self.log_area.append(f"Módulos activos: {status['modules_active']}")
        self.log_area.append(f"Lista activos: {', '.join(status['active_modules'])}")
        self.log_area.append(
            f"Navegación por teclado: {'✓' if status['keyboard_enabled'] else '✗'}"
        )
        self.log_area.append(
            f"Gestión de errores: {'✓' if status['error_management_enabled'] else '✗'}"
        )
        self.log_area.append(
            f"Indicadores de carga: {'✓' if status['loading_enabled'] else '✗'}"
        )
        self.log_area.append("========================")

    def on_module_loaded(self, module_name: str):
        """Callback cuando se carga un módulo."""
        self.log_area.append(f"🔗 Evento: Módulo {module_name} conectado al sistema")

    def on_error_occurred(self, module: str, error_code: str, message: str):
        """Callback cuando ocurre un error."""
        self.log_area.append(f"⚠️ Error en {module} [{error_code}]: {message}")

    def mostrar_ayuda_atajos(self):
        """Implementa la interfaz esperada por el sistema de navegación."""
        self.show_keyboard_help()


def test_keyboard_navigation():
    """Prueba específica del sistema de navegación."""
    print("=== PRUEBA DE NAVEGACIÓN POR TECLADO ===")

    from rexus.utils.keyboard_navigation import KeyboardAction, StandardShortcuts

    # Probar atajos estándar
    print("Atajos estándar disponibles:")
    for action in [
        KeyboardAction.NEW_RECORD,
        KeyboardAction.EDIT_RECORD,
        KeyboardAction.DELETE_RECORD,
        KeyboardAction.FOCUS_SEARCH,
    ]:
        shortcuts = StandardShortcuts.get_shortcuts(action)
        print(f"  {action}: {', '.join(shortcuts)}")

    print("✓ Sistema de navegación por teclado funcional")


def test_system_integration():
    """Prueba específica del sistema de integración."""
    print("\n=== PRUEBA DE INTEGRACIÓN DEL SISTEMA ===")

    manager = get_system_integration_manager()

    # Probar registro de módulos
    modules = manager.modules
    print(f"Módulos registrados: {len(modules)}")
    for name, info in modules.items():
        print(f"  - {name}: {info.display_name}")

    # Probar estado del sistema
    status = manager.get_system_status()
    print(f"Estado del sistema: {status['modules_registered']} módulos disponibles")

    print("✓ Sistema de integración funcional")


def main():
    """Función principal de prueba."""
    print("Iniciando prueba completa del sistema Rexus...")

    # Pruebas unitarias
    test_keyboard_navigation()
    test_system_integration()

    # Prueba de interfaz
    app = QApplication(sys.argv)

    window = TestMainWindow()
    window.show()

    print("\n=== INSTRUCCIONES DE PRUEBA ===")
    print("1. Use Ctrl+1, Ctrl+2, Ctrl+3 para cargar módulos")
    print("2. Use F1 para ver todos los atajos disponibles")
    print("3. Use Ctrl+I para ver el estado del sistema")
    print("4. Pruebe la navegación por Tab en los módulos cargados")
    print("5. Observe los logs en la parte inferior")
    print("================================")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
