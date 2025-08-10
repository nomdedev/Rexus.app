#!/usr/bin/env python3
"""
Rexus.app - Sistema de Gestión Integral con Sidebar Colapsible
"""

import os
import sys
from typing import Any, Dict, Optional

# Cargar variables de entorno antes de cualquier otra importación
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("[ENV] Variables de entorno cargadas desde .env")
except ImportError:
    print("[ENV] python-dotenv no disponible, usando variables del sistema")
except Exception as e:
    print(f"[ENV] Error cargando variables: {e}")

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rexus.core.login_dialog import LoginDialog


class CollapsibleSidebar(QFrame):
    """Sidebar colapsible con animación suave"""

    module_clicked = pyqtSignal(str)

    def __init__(self, user_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_collapsed = False
        self.expanded_width = 280
        self.collapsed_width = 70

        self.setFixedWidth(self.expanded_width)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del sidebar"""
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 2px solid #34495e;
            }
        """)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Header con botón toggle
        self.create_header()

        # Info del usuario
        self.create_user_info()

        # Módulos
        self.create_modules()

    def create_header(self):
        """Crea el header con botón toggle"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border: none;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 15, 10, 15)

        # Título
        self.title_label = QLabel("Rexus.app")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)

        # Botón toggle
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                color: white;
                border: 1px solid #34495e;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_btn)

        self.main_layout.addWidget(header_frame)

    def create_user_info(self):
        """Crea la información del usuario"""
        self.user_frame = QFrame()
        self.user_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.1);
                border: none;
            }
        """)

        user_layout = QVBoxLayout(self.user_frame)
        user_layout.setContentsMargins(15, 10, 15, 10)

        self.user_label = QLabel(f"👤 {self.user_data.get('username', 'Usuario')}")
        self.user_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: 500;
            }
        """)

        self.role_label = QLabel(f"🔑 {self.user_data.get('rol', 'Rol')}")
        self.role_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 11px;
            }
        """)

        user_layout.addWidget(self.user_label)
        user_layout.addWidget(self.role_label)

        self.main_layout.addWidget(self.user_frame)

    def create_modules(self):
        """Crea los módulos del sidebar"""
        # Scroll area para módulos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        modules_widget = QWidget()
        self.modules_layout = QVBoxLayout(modules_widget)
        self.modules_layout.setSpacing(5)
        self.modules_layout.setContentsMargins(10, 10, 10, 10)

        # Módulos ordenados
        self.modules = [
            ("🏗️", "Obras", "Gestión de proyectos y construcción"),
            ("📦", "Inventario", "Gestión de inventario y stock"),
            ("🔧", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("📋", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("💼", "Administración", "Gestión administrativa y financiera"),
            ("🛠️", "Mantenimiento", "Gestión de mantenimiento"),
            ("[CHART]", "Auditoría", "Auditoría y trazabilidad"),
            ("👥", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]

        self.module_buttons = []
        for emoji, nombre, descripcion in self.modules:
            btn = self.create_module_button(emoji, nombre, descripcion)
            self.module_buttons.append(btn)
            self.modules_layout.addWidget(btn)

        self.modules_layout.addStretch()
        scroll.setWidget(modules_widget)
        self.main_layout.addWidget(scroll)

    def create_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        """Crea un botón de módulo"""
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
                border-radius: 6px;
                margin: 2px 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #3498db;
                color: #ffffff;
            }
        """)
        btn.clicked.connect(lambda checked, name=nombre: self.module_clicked.emit(name))
        return btn

    def toggle_sidebar(self):
        """Alterna entre estado expandido y colapsado"""
        if self.is_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()

    def collapse_sidebar(self):
        """Colapsa el sidebar"""
        self.is_collapsed = True
        self.setFixedWidth(self.collapsed_width)

        # Cambiar botón toggle
        self.toggle_btn.setText("▶")

        # Ocultar texto
        self.title_label.setVisible(False)
        self.user_frame.setVisible(False)

        # Cambiar botones a solo íconos
        for i, btn in enumerate(self.module_buttons):
            emoji = self.modules[i][0]
            btn.setText(emoji)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 12px 8px;
                    border: none;
                    color: #ffffff;
                    font-size: 16px;
                    background-color: transparent;
                    border-radius: 6px;
                    margin: 2px 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #3498db;
                    color: #ffffff;
                }
            """)

    def expand_sidebar(self):
        """Expande el sidebar"""
        self.is_collapsed = False
        self.setFixedWidth(self.expanded_width)

        # Cambiar botón toggle
        self.toggle_btn.setText("◀")

        # Mostrar texto
        self.title_label.setVisible(True)
        self.user_frame.setVisible(True)

        # Restaurar botones con texto
        for i, btn in enumerate(self.module_buttons):
            emoji, nombre, _ = self.modules[i]
            btn.setText(f"{emoji}  {nombre}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 15px 20px;
                    border: none;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 600;
                    background-color: transparent;
                    border-radius: 6px;
                    margin: 2px 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #3498db;
                    color: #ffffff;
                }
            """)


class MainWindow(QMainWindow):
    """Ventana principal con sidebar colapsible"""

    def __init__(self, user_data: Dict[str, Any], modulos_permitidos: list):
        super().__init__()
        self.user_data = user_data
        self.modulos_permitidos = modulos_permitidos
        self.current_module = None

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        self.setGeometry(100, 100, 1400, 900)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar colapsible
        self.sidebar = CollapsibleSidebar(self.user_data)
        self.sidebar.module_clicked.connect(self.show_module)
        main_layout.addWidget(self.sidebar)

        # Área de contenido
        self.create_content_area(main_layout)

        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)

    def create_content_area(self, main_layout):
        """Crea el área de contenido principal"""
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;
            }
        """)

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Header del contenido (SIN título redundante)
        self.content_stack = QTabWidget()
        self.content_stack.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        # Dashboard inicial
        self.create_dashboard()

        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(self.content_area)

    def create_dashboard(self):
        """Crea el dashboard principal"""
        dashboard = QWidget()
        layout = QGridLayout(dashboard)
        layout.setSpacing(20)

        # Cards de estadísticas mejoradas
        stats = [
            ("📦", "Stock", "1,234", "#3498db"),
            ("💰", "Ventas", "$45,678", "#2ecc71"),
            ("🏗️", "Obras", "23", "#e74c3c"),
            ("📋", "Pedidos", "56", "#f39c12"),
        ]

        for i, (emoji, titulo, valor, color) in enumerate(stats):
            card = self.create_stat_card(emoji, titulo, valor, color)
            layout.addWidget(card, 0, i)

        # Información de bienvenida
        welcome_widget = self.create_welcome_widget()
        layout.addWidget(welcome_widget, 1, 0, 1, 4)

        self.content_stack.addTab(dashboard, "🏠 Dashboard")

    def create_stat_card(
        self, emoji: str, titulo: str, valor: str, color: str
    ) -> QFrame:
        """Crea una tarjeta de estadística mejorada"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 10px;
                padding: 20px;
                min-height: 100px;
            }}
            QFrame:hover {{
                /* box-shadow eliminado: usar QGraphicsDropShadowEffect en el widget correspondiente */
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Emoji grande
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 32px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Valor principal
        value_label = QLabel(valor)
        value_label.setStyleSheet(f"""
            font-size: 24px; 
            color: {color}; 
            font-weight: bold;
            text-align: center;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title_label = QLabel(titulo)
        title_label.setStyleSheet("""
            font-size: 14px; 
            color: #7f8c8d; 
            font-weight: 500;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(emoji_label)
        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return card

    def create_welcome_widget(self) -> QWidget:
        """Crea el widget de bienvenida"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setSpacing(20)

        # Título de bienvenida
        welcome_title = QLabel("🎉 ¡Bienvenido a Rexus.app!")
        welcome_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
            }
        """)
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Información del usuario
        user_info = QLabel(f"""
        👤 Usuario: {self.user_data.get("username", "N/A")}
        🔑 Rol: {self.user_data.get("rol", "N/A")}
        📱 Módulos disponibles: {len(self.modulos_permitidos)}
        
        [CHECK] Sistema funcionando correctamente
        🔧 Sidebar colapsible implementado
        [CHART] Dashboard optimizado
        """)

        user_info.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 30px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                color: #495057;
                line-height: 1.6;
            }
        """)
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(user_info)

        return welcome_widget

    def show_module(self, module_name: str):
        """Muestra un módulo específico"""
        print(f"Mostrando módulo: {module_name}")

        # Crear un widget placeholder para el módulo
        module_widget = QWidget()
        module_layout = QVBoxLayout(module_widget)
        module_layout.setContentsMargins(20, 20, 20, 20)

        # Contenido del módulo (sin título redundante)
        content_label = QLabel(f"Contenido del módulo {module_name}")
        content_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #2c3e50;
                padding: 40px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                text-align: center;
            }
        """)
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        module_layout.addWidget(content_label)

        # Agregar o actualizar pestaña
        tab_title = f"{self.get_module_emoji(module_name)} {module_name}"

        # Buscar si ya existe la pestaña
        for i in range(self.content_stack.count()):
            if self.content_stack.tabText(i) == tab_title:
                self.content_stack.setCurrentIndex(i)
                return

        # Agregar nueva pestaña
        self.content_stack.addTab(module_widget, tab_title)
        self.content_stack.setCurrentWidget(module_widget)

    def get_module_emoji(self, module_name: str) -> str:
        """Obtiene el emoji correspondiente al módulo"""
        emoji_map = {
            "Obras": "🏗️",
            "Inventario": "📦",
            "Herrajes": "🔧",
            "Vidrios": "🪟",
            "Pedidos": "📋",
            "Compras": "🛒",
            "Administración": "💼",
            "Mantenimiento": "🛠️",
            "Auditoría": "[CHART]",
            "Usuarios": "👥",
            "Configuración": "⚙️",
        }
        return emoji_map.get(module_name, "📱")


class SimpleSecurityManager:
    """Sistema de seguridad simple para fallback"""

    def __init__(self):
        self.current_user_data = None
        self.users = {"admin": {"rol": "ADMIN", "id": 1, "username": "admin"}}

    def login(self, username: str, password: str) -> bool:
        """Autenticación simple"""
        user = self.users.get(username)
        if user and password == "admin":
            self.current_user_data = user.copy()
            return True
        return False

    def get_current_role(self) -> str:
        return (
            self.current_user_data.get("rol", "USUARIO")
            if self.current_user_data
            else "USUARIO"
        )

    def get_current_user(self) -> dict:
        return (
            self.current_user_data
            if self.current_user_data
            else {"id": 0, "username": "guest", "rol": "USUARIO"}
        )

    def get_user_modules(self, user_id: int) -> list:
        return [
            "inventario",
            "obras",
            "pedidos",
            "logistica",
            "herrajes",
            "vidrios",
            "usuarios",
            "auditoria",
            "configuracion",
            "compras",
            "mantenimiento",
            "administracion",
        ]


def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Crear gestor de seguridad
    security_manager = SimpleSecurityManager()

    # Mostrar login
    login_dialog = LoginDialog()

    def handle_login_success(user_data):
        """Maneja login exitoso con dict completo del usuario"""
        # user_data es el dict completo emitido por login_dialog
        modulos_permitidos = security_manager.get_user_modules(user_data.get("id", 1))
        main_window = MainWindow(user_data, modulos_permitidos)
        main_window.showFullScreen()
        login_dialog.close()

    def handle_login_failed(error):
        """Maneja login fallido"""
        print(f"Login fallido: {error}")

    # Conectar señales
    login_dialog.login_successful.connect(handle_login_success)
    login_dialog.login_failed.connect(handle_login_failed)

    # Mostrar dialog de login
    if login_dialog.exec() == login_dialog.DialogCode.Accepted:
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
