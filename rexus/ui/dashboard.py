"""
Rexus.app - Dashboard Controller

Controlador del dashboard principal de la aplicación.
Maneja la interfaz y lógica del panel principal.
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from rexus.utils.app_logger import log_info

class DashboardWidget(QWidget):
    """
    Widget personalizado para el dashboard con señal de navegación.
    """

    # Señal emitida cuando se solicita cambiar a un módulo
    modulo_solicitado = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz del dashboard."""
        layout = QVBoxLayout(self)

        # Título del dashboard
        title_label = QLabel("Dashboard - Rexus.app")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px;
            }
        """)
        layout.addWidget(title_label)

        # Contenido del dashboard
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)

        welcome_label = QLabel("Bienvenido al sistema Rexus.app")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin: 10px;
            }
        """)
        content_layout.addWidget(welcome_label)

        status_label = QLabel("Sistema operativo correctamente")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #27ae60;
                margin: 10px;
            }
        """)
        content_layout.addWidget(status_label)

        # Botones de navegación rápida
        buttons_layout = QHBoxLayout()

        modules = ["Inventario", "Ventas", "Compras", "Reportes"]
        for module in modules:
            btn = QPushButton(f"Ir a {module}")
            btn.clicked.connect(lambda checked, m=module.lower(): self._navigate_to_module(m))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            buttons_layout.addWidget(btn)

        content_layout.addLayout(buttons_layout)
        layout.addWidget(content_frame)
        layout.addStretch()

    def _navigate_to_module(self, module_name: str):
        """Emite la señal para navegar a un módulo."""
        self.modulo_solicitado.emit(module_name)
        log_info(f"Navegación solicitada a módulo: {module_name}", "dashboard")


class DashboardController:
    """
    Controlador del dashboard principal.
    Gestiona la interfaz y funcionalidad del panel principal.
    """

    def __init__(self, user_data=None, parent=None):
        self.parent = parent
        self.user_data = user_data
        self.widget = None
        self._create_dashboard()

    def _create_dashboard(self):
        """Crea la interfaz del dashboard."""
        self.widget = DashboardWidget(self.parent)
        log_info("Dashboard creado exitosamente", "dashboard")

    def get_widget(self) -> Optional[QWidget]:
        """Obtiene el widget del dashboard."""
        return self.widget

    def get_view(self):
        """Obtiene la vista del dashboard (alias de get_widget)."""
        return self.get_widget()

    def show_module(self, module_name: str):
        """Muestra un módulo específico en el dashboard."""
        log_info(f"Solicitud para mostrar módulo: {module_name}", "dashboard")
