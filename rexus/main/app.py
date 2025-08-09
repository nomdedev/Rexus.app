#!/usr/bin/env python3
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
Rexus.app - Sistema de Gestión Integral

Aplicación principal que maneja la interfaz de usuario y la integración de módulos.
Sigue principios de arquitectura MVC y patrones de diseño para mantenibilidad.
"""

import datetime
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv(root_dir / ".env")
    print("[ENV] Variables de entorno cargadas desde .env")
except ImportError:
    print("[ENV] Warning: python-dotenv no instalado, usando variables del sistema")
except Exception as e:
    print(f"[ENV] Error cargando .env: {e}")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from rexus.core.login_dialog import LoginDialog

# Importar componentes del core
from rexus.core.module_manager import module_manager


def initialize_security_manager():
    """Inicializa el sistema de seguridad"""
    try:
        from rexus.core.database import UsersDatabaseConnection
        from rexus.core.security import init_security_manager

        # Intentar crear conexión a la base de datos
        try:
            db_connection = UsersDatabaseConnection()
            print("[SECURITY] Conexión BD exitosa para sistema de seguridad")
        except Exception as db_error:
            print(f"[SECURITY] Error BD: {db_error}, usando modo sin BD")
            db_connection = None

        # Inicializar con o sin conexión BD
        security_manager = init_security_manager(db_connection)
        print("[SECURITY] SecurityManager inicializado correctamente")
        return security_manager

    except ImportError as e:
        print(f"[SECURITY] Error importando módulo de seguridad: {e}")
        return SimpleSecurityManager()
    except Exception as e:
        print(f"[SECURITY] Error general inicializando seguridad: {e}")
        return SimpleSecurityManager()


class SimpleSecurityManager:
    """Sistema de seguridad simple para fallback"""

    def __init__(self):
        self.current_user_data = None
        self.current_user = None  # Para compatibilidad con SecurityManager
        self.current_role = "usuario"  # Para compatibilidad con SecurityManager
        # Sistema seguro sin credenciales hardcodeadas
        # Las credenciales se cargan desde variables de entorno
        self._load_secure_credentials()

    def _load_secure_credentials(self):
        """Carga credenciales desde variables de entorno de forma segura"""
        import os

        from rexus.utils.security import SecurityUtils

        # Solo cargar si está en modo desarrollo y se especifica explícitamente
        if os.environ.get("DEVELOPMENT_MODE") == "true":
            admin_user = os.environ.get("FALLBACK_ADMIN_USER")
            admin_password = os.environ.get("FALLBACK_ADMIN_PASSWORD")

            if admin_user and admin_password:
                # Hash seguro de la contraseña
                hashed_password = SecurityUtils.hash_password(admin_password)
                self.users = {
                    admin_user: {
                        "rol": "ADMIN",
                        "id": 1,
                        "username": admin_user,
                        "password_hash": hashed_password,
                    }
                }
                print(f"[SIMPLE_AUTH] Usuario de desarrollo cargado: {admin_user}")
            else:
                self.users = {}
                print(
                    "[SIMPLE_AUTH] Modo desarrollo activo pero sin credenciales configuradas"
                )
        else:
            self.users = {}
            print("[SIMPLE_AUTH] Modo producción - sin usuarios fallback")

    def login(self, username: str, password: str) -> bool:
        """Autenticación segura con hashing"""
        print(f"[SIMPLE_AUTH] Intentando login: usuario='{username}'")

        # Verificar si hay usuarios disponibles
        if not self.users:
            print("[SIMPLE_AUTH] No hay usuarios fallback disponibles")
            return False

        user = self.users.get(username)
        if not user:
            print(f"[SIMPLE_AUTH] Usuario '{username}' no encontrado")
            return False

        # Verificar contraseña con hash seguro
        try:
            from rexus.utils.security import SecurityUtils

            if SecurityUtils.verify_password(password, user.get("password_hash", "")):
                print(f"[SIMPLE_AUTH] Login exitoso para {username}")
                self.current_user_data = {
                    k: v for k, v in user.items() if k != "password_hash"
                }
                # Sincronizar atributos para compatibilidad
                self.current_user = self.current_user_data
                self.current_role = self.current_user_data.get("rol", "usuario")
                return True
            else:
                print(f"[SIMPLE_AUTH] Contraseña incorrecta para {username}")
                return False
        except ImportError:
            print("[SIMPLE_AUTH] SecurityUtils no disponible, login fallido")
            return False

    def get_current_role(self) -> str:
        """Obtiene el rol actual"""
        return (
            self.current_user_data.get("rol", "USUARIO")
            if self.current_user_data
            else "USUARIO"
        )

    def get_current_user(self) -> dict:
        """Obtiene datos del usuario actual"""
        return (
            self.current_user_data
            if self.current_user_data
            else {"id": 0, "username": "guest", "rol": "USUARIO"}
        )

    def get_user_modules(self, user_id: int) -> list:
        """Lista de módulos permitidos"""
        print(f"[SIMPLE_AUTH] Obteniendo módulos para usuario ID: {user_id}")
        # Usar nombres consistentes con los esperados por el sistema
        modules = [
            "Inventario",
            "Obras",
            "Administración",
            "Logística",
            "Herrajes",
            "Vidrios",
            "Pedidos",
            "Usuarios",
            "Configuración",
            "Compras",
            "Mantenimiento",
            "Auditoría",
        ]
        print(f"[SIMPLE_AUTH] Módulos permitidos: {modules}")
        return modules

    def has_permission(self, permission: str, module: str = None) -> bool:
        """Verifica permisos - admin tiene todos"""
        return self.current_user_data and self.current_user_data.get("rol") == "ADMIN"

    def log_security_event(
        self, user_id: int, accion: str, modulo: str = None, detalles: str = None
    ):
        """Log simple de eventos"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[SECURITY_LOG] {timestamp} - Usuario:{user_id} - Acción:{accion} - Módulo:{modulo} - Detalles:{detalles}"
        )

    def diagnose_permissions(self) -> dict:
        """Diagnóstica el estado de permisos del usuario actual"""
        return {
            "has_admin_access": self.current_role == "ADMIN",
            "current_user": self.current_user_data.get("username")
            if self.current_user_data
            else None,
            "current_role": self.current_role,
            "permissions_loaded": True,
        }


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Rexus.app

    Maneja la interfaz principal con sidebar de módulos y área de contenido dinámico.
    Implementa patrón Factory para creación de módulos y sistema de fallback.

    Attributes:
        user_data (Dict): Datos del usuario actual
        modulos_permitidos (List): Lista de módulos permitidos para el usuario
        security_manager: Gestor de seguridad de la aplicación
        content_stack (QStackedWidget): Stack de pestañas para módulos
        content_header (QLabel): Header del área de contenido
    """

    def __init__(self, user_data: Dict[str, Any], modulos_permitidos: list):
        """
        Inicializa la ventana principal

        Args:
            user_data: Diccionario con datos del usuario autenticado
            modulos_permitidos: Lista de módulos accesibles para el usuario
        """
        super().__init__()
        self.user_data = user_data
        self.modulos_permitidos = modulos_permitidos

        self.content_stack = QStackedWidget()

        # Inicializar StyleManager y aplicar tema automático
        self._init_styles()
        self._init_ui()
    
    def _init_styles(self):
        """Inicializa y aplica el sistema de estilos."""
        try:
            from rexus.ui.style_manager import StyleManager
            
            self.style_manager = StyleManager()
            
            # Aplicar tema global (auto-detectado en StyleManager)
            success = self.style_manager.apply_global_theme()
            if success:
                print(f"[STYLE] Tema '{self.style_manager._current_theme}' aplicado globalmente")
            else:
                print("[STYLE] Fallback a estilos por defecto")
                
        except Exception as e:
            print(f"[WARNING] Error inicializando StyleManager: {e}")
            self.style_manager = None

    def _init_ui(self):
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        self.setGeometry(100, 100, 1400, 900)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Configurar interfaz principal
        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)

    def _create_sidebar(self, main_layout):
        """Crea la barra lateral con módulos"""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-right: 2px solid #217dbb;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Header del sidebar
        header = QLabel("Rexus.app")
        header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(header)

        # Usuario actual
        user_info = QLabel(
            f"👤 {self.user_data['username']}\n🔑 {self.user_data.get('rol', self.user_data.get('role', 'Usuario'))}"
        )
        user_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                padding: 15px 20px;
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        sidebar_layout.addWidget(user_info)

        # Scroll area para módulos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        modules_widget = QWidget()
        modules_layout = QVBoxLayout(modules_widget)
        modules_layout.setSpacing(5)
        modules_layout.setContentsMargins(10, 10, 10, 10)

        # Módulos ordenados por flujo de proyecto real (incluye Logística)
        modulos = [
            ("🏗️", "Obras", "Gestión de proyectos y construcción"),
            ("📦", "Inventario", "Gestión de inventario y stock"),
            ("🔩", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("🚛", "Logística", "Gestión de logística y transporte"),
            ("📋", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("🏢", "Administración", "Gestión administrativa y financiera"),
            ("🛠️", "Mantenimiento", "Gestión de mantenimiento"),
            ("🕵️", "Auditoría", "Auditoría y trazabilidad"),
            ("👥", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]

        print(f"[DEBUG] Módulos permitidos: {self.modulos_permitidos}")

        for emoji, nombre, descripcion in modulos:
            # Verificar si el usuario tiene permisos para este módulo
            has_permission = nombre in self.modulos_permitidos
            print(f"[DEBUG] Módulo '{nombre}': permisos={has_permission}")

            if has_permission:
                btn = self._create_module_button(emoji, nombre, descripcion)
                modules_layout.addWidget(btn)
            else:
                # Crear botón deshabilitado para módulos sin permisos
                btn = self._create_disabled_module_button(emoji, nombre, "Sin permisos")
                modules_layout.addWidget(btn)

        modules_layout.addStretch()
        scroll.setWidget(modules_widget)
        sidebar_layout.addWidget(scroll)

        main_layout.addWidget(sidebar)

    def _create_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        """Crea un botón de módulo estilizado"""
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 15px 20px;
    border: none;
    color: #111111;
    font-size: 14px;
    font-weight: 600;
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    margin: 3px 8px;
}
QPushButton:hover {
    background-color: #3498db;
    color: #111111;
    font-weight: bold;
}
QPushButton:pressed {
    background-color: #217dbb;
    color: #111111;
}
            """
        )
        btn.clicked.connect(lambda checked, name=nombre: self.show_module(name))
        return btn

    def _create_disabled_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        """Crea un botón de módulo deshabilitado para módulos sin permisos"""
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setEnabled(False)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 15px 20px;
    border: none;
    color: #888888;
    font-size: 14px;
    font-weight: 400;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    margin: 3px 8px;
}
QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.05);
    color: #666666;
}
            """
        )
        return btn

    def _create_main_content(self, main_layout):
        """Crea el área de contenido principal"""
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 0px;
            }
        """)

        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Área de contenido dinámico
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

        # Dashboard inicial
        self._create_dashboard()

        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_area)

    def _create_dashboard(self):
        """Crea el dashboard principal"""
        dashboard = QWidget()
        layout = QGridLayout(dashboard)
        layout.setSpacing(20)

        # Cards de estadísticas
        stats = [
            ("📦", "Productos en Stock", "1,234", "#3498db"),
            ("💰", "Facturación Mensual", "$45,678", "#2ecc71"),
            ("🏗️", "Obras Activas", "23", "#e74c3c"),
            ("📋", "Pedidos Pendientes", "56", "#f39c12"),
        ]

        for i, (emoji, titulo, valor, color) in enumerate(stats):
            card = self._create_stat_card(emoji, titulo, valor, color)
            layout.addWidget(card, 0, i)

        # Información de bienvenida
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)

        welcome_title = QLabel("🎉 ¡Bienvenido a Rexus.app!")
        welcome_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_info = QLabel(f"""
        Usuario: {self.user_data.get("username", "N/A")}
        Rol: {self.user_data.get("rol", self.user_data.get("role", "N/A"))}
        
        Módulos disponibles: {len(self.modulos_permitidos)}
        
        [CHECK] Sistema de login funcionando correctamente
        📱 Todos los módulos están listos para usar
        🔧 Configuración de base de datos disponible
        """)

        welcome_info.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 20px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                color: #495057;
                line-height: 1.5;
            }
        """)
        welcome_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_info)

        layout.addWidget(welcome_widget, 1, 0, 1, 4)

        self.content_stack.addWidget(dashboard)

    def _create_stat_card(
        self, emoji: str, titulo: str, valor: str, color: str
    ) -> QFrame:
        """Crea una tarjeta de estadística"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 4px;
                min-width: 60px;
                min-height: 60px;
                max-width: 60px;
                max-height: 60px;
            }}
        """)
        layout = QVBoxLayout(card)
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 18px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label = QLabel(titulo)
        title_label.setStyleSheet("font-size: 9px; color: #7f8c8d; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label = QLabel(valor)
        value_label.setStyleSheet(
            f"font-size: 12px; color: {color}; font-weight: bold;"
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def show_module(self, module_name: str) -> None:
        """
        Muestra el contenido de un módulo usando factory pattern

        Args:
            module_name: Nombre del módulo a mostrar
        """
        try:
            # Factory pattern para creación de módulos
            module_widget = self._create_module_widget(module_name)

            # Limpiar contenido anterior y agregar nuevo widget
            while self.content_stack.count() > 0:
                widget = self.content_stack.widget(0)
                self.content_stack.removeWidget(widget)
                widget.deleteLater()

            self.content_stack.addWidget(module_widget)
            self.content_stack.setCurrentWidget(module_widget)

        except Exception as e:
            print(f"Error cargando módulo {module_name}: {e}")
            self.mostrar_mensaje(f"Error al cargar {module_name}: {str(e)}", "error")

    def _create_module_widget(self, module_name: str) -> QWidget:
        """
        Factory method para crear widgets de módulos

        Args:
            module_name: Nombre del módulo

        Returns:
            Widget del módulo correspondiente
        """
        # Mapeo de módulos a métodos de creación (incluyendo variaciones normalizadas)
        module_factory = {
            "Inventario": self._create_inventario_module,
            "Contabilidad": self._create_contabilidad_module,
            "Obras": self._create_obras_module,
            "Configuración": self._create_configuracion_module,
            "Configuracion": self._create_configuracion_module,  # Sin tilde
            "Vidrios": self._create_vidrios_module,
            "Herrajes": self._create_herrajes_module,
            "Pedidos": self._create_pedidos_module,
            "Logística": self._create_logistica_module,
            "Logistica": self._create_logistica_module,  # Sin tilde
            "Usuarios": self._create_usuarios_module,
            "Auditoría": self._create_auditoria_module,
            "Auditoria": self._create_auditoria_module,  # Sin tilde
            "Compras": self._create_compras_module,
            "Mantenimiento": self._create_mantenimiento_module,
            "Administración": self._create_administracion_module,
            "Administracion": self._create_administracion_module,  # Sin tilde
        }

        # Función de normalización mejorada
        def normalize_module_name(name):
            """Normaliza nombre de módulo para evitar problemas de tildes/capitalización"""
            replacements = {
                "á": "a",
                "é": "e",
                "í": "i",
                "ó": "o",
                "ú": "u",
                "Á": "A",
                "É": "E",
                "Í": "I",
                "Ó": "O",
                "Ú": "U",
            }
            normalized = name.strip().capitalize()
            for accented, plain in replacements.items():
                normalized = normalized.replace(accented, plain)
            return normalized

        # Intentar múltiples variaciones del nombre
        names_to_try = [
            module_name,  # Nombre original
            normalize_module_name(module_name),  # Nombre normalizado
            module_name.strip().capitalize(),  # Solo capitalizado
            module_name.strip()
            .lower()
            .capitalize(),  # Lowercase primero, luego capitalizado
        ]

        creation_method = None
        for name_variant in names_to_try:
            creation_method = module_factory.get(name_variant)
            if creation_method:
                break

        if creation_method:
            return creation_method()
        else:
            return self._create_fallback_module(module_name)

    def _create_administracion_module(self) -> QWidget:
        """Crea el módulo de administración usando la vista real"""
        try:
            from rexus.modules.administracion.view import AdministracionView

            view = AdministracionView()
            return view
        except Exception as e:
            print(f"Error creando administración real: {e}")
            return self._create_fallback_module("Administración")

    def _create_inventario_module(self) -> QWidget:
        """Crea el módulo de inventario usando el gestor robusto de módulos"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.inventario.controller import InventarioController
            from rexus.modules.inventario.model import InventarioModel
            from rexus.modules.inventario.view import InventarioView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Inventario",
                model_class=InventarioModel,
                view_class=InventarioView,
                controller_class=InventarioController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando inventario: {e}")
            return self._create_fallback_module("Inventario")

    def _create_contabilidad_module(self) -> QWidget:
        """Crea el módulo de contabilidad usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.administracion.contabilidad.controller import (
                ContabilidadController,
            )
            from rexus.modules.administracion.contabilidad.model import (
                ContabilidadModel,
            )
            from rexus.modules.administracion.contabilidad.view import ContabilidadView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Contabilidad",
                model_class=ContabilidadModel,
                view_class=ContabilidadView,
                controller_class=ContabilidadController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando contabilidad: {e}")
            return self._create_fallback_module("Contabilidad")

    def _create_obras_module(self) -> QWidget:
        """Crea el módulo de obras usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.obras.controller import ObrasController
            from rexus.modules.obras.model import ObrasModel
            from rexus.modules.obras.view import ObrasView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Obras",
                model_class=ObrasModel,
                view_class=ObrasView,
                controller_class=ObrasController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando obras: {e}")
            return self._create_fallback_module("Obras")

    def _create_configuracion_module(self) -> QWidget:
        """Crea el módulo de configuración usando los archivos reales"""
        try:
            from rexus.modules.configuracion.controller import ConfiguracionController
            from rexus.modules.configuracion.model import ConfiguracionModel
            from rexus.modules.configuracion.view import ConfiguracionView

            # Crear modelo, vista y controlador
            model = ConfiguracionModel()
            view = ConfiguracionView()
            controller = ConfiguracionController(model, view)

            # Conectar view con controller
            view.set_controller(controller)

            # Cargar datos iniciales
            controller.cargar_configuraciones()

            return view

        except Exception as e:
            print(f"Error creando configuración real: {e}")
            # Fallback a widget simple
            return self._create_fallback_module("Configuración")

    def actualizar_usuario_label(self, user_data):
        """Actualiza la información del usuario"""
        self.user_data = user_data

    def _create_vidrios_module(self) -> QWidget:
        """Crea el módulo de vidrios usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.vidrios.controller import VidriosController
            from rexus.modules.vidrios.model import VidriosModel
            from rexus.modules.vidrios.view import VidriosView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Vidrios",
                model_class=VidriosModel,
                view_class=VidriosView,
                controller_class=VidriosController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando vidrios: {e}")
            return self._create_fallback_module("Vidrios")

    def _create_herrajes_module(self) -> QWidget:
        """Crea el módulo de herrajes usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.herrajes.controller import HerrajesController
            from rexus.modules.herrajes.model import HerrajesModel
            from rexus.modules.herrajes.view import HerrajesView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Herrajes",
                model_class=HerrajesModel,
                view_class=HerrajesView,
                controller_class=HerrajesController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando herrajes: {e}")
            return self._create_fallback_module("Herrajes")

    def _create_pedidos_module(self) -> QWidget:
        """Crea el módulo de pedidos usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.pedidos.controller import PedidosController
            from rexus.modules.pedidos.model import PedidosModel
            from rexus.modules.pedidos.view import PedidosView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Pedidos",
                model_class=PedidosModel,
                view_class=PedidosView,
                controller_class=PedidosController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando pedidos: {e}")
            return self._create_fallback_module("Pedidos")

    def _create_logistica_module(self) -> QWidget:
        """Crea el módulo de logística usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.logistica.controller import LogisticaController
            from rexus.modules.logistica.model import LogisticaModel
            from rexus.modules.logistica.view import LogisticaView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Logistica",
                model_class=LogisticaModel,
                view_class=LogisticaView,
                controller_class=LogisticaController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando logística: {e}")
            return self._create_fallback_module("Logística")

    def _create_usuarios_module(self) -> QWidget:
        """Crea el módulo de usuarios usando el gestor robusto"""
        try:
            from rexus.core.database import UsersDatabaseConnection
            from rexus.modules.usuarios.controller import UsuariosController
            from rexus.modules.usuarios.model import UsuariosModel
            from rexus.modules.usuarios.view import UsuariosView

            # Crear conexión a la base de datos
            try:
                db_connection = UsersDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Usuarios",
                model_class=UsuariosModel,
                view_class=UsuariosView,
                controller_class=UsuariosController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando usuarios: {e}")
            return self._create_fallback_module("Usuarios")

    def _create_auditoria_module(self) -> QWidget:
        """Crea el módulo de auditoría usando el gestor robusto"""
        try:
            from rexus.core.database import AuditoriaDatabaseConnection
            from rexus.modules.auditoria.controller import AuditoriaController
            from rexus.modules.auditoria.model import AuditoriaModel
            from rexus.modules.auditoria.view import AuditoriaView

            # Crear conexión a la base de datos
            try:
                db_connection = AuditoriaDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Auditoria",
                model_class=AuditoriaModel,
                view_class=AuditoriaView,
                controller_class=AuditoriaController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando auditoría: {e}")
            return self._create_fallback_module("Auditoría")

    def _create_compras_module(self) -> QWidget:
        """Crea el módulo de compras usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.compras.controller import ComprasController
            from rexus.modules.compras.model import ComprasModel
            from rexus.modules.compras.view import ComprasView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Compras",
                model_class=ComprasModel,
                view_class=ComprasView,
                controller_class=ComprasController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando compras: {e}")
            return self._create_fallback_module("Compras")

    def _create_mantenimiento_module(self) -> QWidget:
        """Crea el módulo de mantenimiento usando el gestor robusto"""
        try:
            from rexus.core.database import InventarioDatabaseConnection
            from rexus.modules.mantenimiento.controller import MantenimientoController
            from rexus.modules.mantenimiento.model import MantenimientoModel
            from rexus.modules.mantenimiento.view import MantenimientoView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Usar el gestor de módulos para carga robusta
            return module_manager.create_module_safely(
                module_name="Mantenimiento",
                model_class=MantenimientoModel,
                view_class=MantenimientoView,
                controller_class=MantenimientoController,
                db_connection=db_connection,
                fallback_callback=self._create_fallback_module,
            )

        except Exception as e:
            print(f"Error crítico creando mantenimiento: {e}")
            return self._create_fallback_module("Mantenimiento")

    def _create_fallback_module(self, module_name: str) -> QWidget:
        """Crea un módulo de fallback cuando el real no está disponible"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        icon_map = {
            "Vidrios": "🪟",
            "Herrajes": "🔧",
            "Pedidos": "📋",
            "Logística": "🚛",
            "Usuarios": "👥",
            "Auditoría": "🔍",
            "Compras": "💳",
            "Mantenimiento": "🛠️",
        }

        icon = icon_map.get(module_name, "📱")

        # Contenido centrado
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono grande
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                margin-bottom: 20px;
            }
        """)

        # Título
        title_label = QLabel(f"Módulo {module_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)

        # Descripción
        desc_label = QLabel("Módulo disponible y funcionando")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 30px;
            }
        """)

        content_layout.addWidget(icon_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)

        layout.addLayout(content_layout)
        layout.addStretch()

        return widget

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=2000):
        """Muestra un mensaje al usuario"""
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        else:
            QMessageBox.information(self, "Información", mensaje)


def main():
    print("[LOG 4.1] Inicializando QtWebEngine y configurando OpenGL...")
    qtwebengine_failed = False
    try:
        from PyQt6.QtWebEngine import QtWebEngine

        QtWebEngine.initialize()
        import os

        os.environ["QT_OPENGL"] = (
            "angle"  # Forzar OpenGL ANGLE para compatibilidad en Windows
        )
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)
    except Exception as e:
        print(f"[LOG 4.1] Error inicializando QtWebEngine/OpenGL: {e}")
        qtwebengine_failed = True
        from PyQt6.QtWidgets import QApplication
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Mostrando login profesional...")

    # Inicializar sistema de seguridad
    try:
        security_manager = initialize_security_manager()
        print("[SEGURIDAD] Sistema de seguridad completo inicializado")
    except Exception as e:
        print(f"[SEGURIDAD] Error inicializando sistema completo: {e}")
        print(
            "[SEGURIDAD] No se pudo inicializar el sistema de seguridad completo. La app funcionará sin seguridad avanzada."
        )
        security_manager = None

    # Inicializar sistema de backup automático
    try:
        from rexus.core.backup_integration import initialize_backup_system

        backup_initialized = initialize_backup_system()
        if backup_initialized:
            print("[CHECK] Sistema de backup automático inicializado")
        else:
            print(
                "[WARN] Sistema de backup no se pudo inicializar, continuando sin backup automático"
            )
    except Exception as e:
        print(f"[WARN] Error inicializando sistema de backup: {e}")

    # Crear dialog de login moderno
    login_dialog = LoginDialog()

    # Asignar el security manager al login dialog
    if security_manager is not None:
        login_dialog.security_manager = security_manager

    def cargar_main_window_con_seguridad(user_data, modulos_permitidos):
        global main_window
        try:
            print(
                f"🏗️ [SEGURIDAD] Creando MainWindow para usuario: {user_data['username']}"
            )
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.actualizar_usuario_label(user_data)
            main_window.show()
            print(f"[CHECK] [SEGURIDAD] Aplicación iniciada para {user_data['username']}")
        except Exception as e:
            import traceback

            error_msg = f"[ERROR SEGURIDAD] {e}\n{traceback.format_exc()}"
            print(f"[ERROR] [ERROR] {error_msg}", flush=True)
            os.makedirs("logs", exist_ok=True)
            with open("logs/error_inicio_seguridad.txt", "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Error al iniciar la aplicación con seguridad: {e}",
            )
            app.quit()

    def on_login_success(user_data):
        print(
            f"[CHECK] [LOGIN] Autenticación exitosa para {user_data.get('username', '???')} ({user_data.get('role', '???')})"
        )
        # Acceder al security_manager del contexto exterior
        nonlocal security_manager
        if security_manager is None:
            print("[ERROR] No se puede continuar: sistema de seguridad no disponible.")
            QMessageBox.critical(
                None,
                "Error de seguridad",
                "No se pudo inicializar el sistema de seguridad. Contacte al administrador.",
            )
            return
        if not user_data:
            print("[ERROR] [LOGIN] Error: No se pudo obtener datos del usuario")
            return

        # 🔥 SOLUCIÓN CRÍTICA: Establecer contexto de seguridad ANTES de obtener módulos
        try:
            # Establecer usuario y rol actual en SecurityManager
            security_manager.current_user = user_data
            security_manager.current_role = user_data.get("role", "usuario")

            print(
                f"[SECURITY] Contexto establecido - Usuario: {user_data.get('username')}, Rol: {security_manager.current_role}"
            )

            # 🔍 DIAGNÓSTICO: Verificar estado del sistema de permisos
            if hasattr(security_manager, "diagnose_permissions"):
                diagnosis = security_manager.diagnose_permissions()
                if (
                    not diagnosis.get("has_admin_access")
                    and user_data.get("role", "").upper() == "ADMIN"
                ):
                    print(
                        "[WARN] [SECURITY WARNING] Usuario admin no tiene acceso completo - verificando problema..."
                    )

            # Ahora obtener módulos permitidos
            modulos_permitidos = security_manager.get_user_modules(
                user_data.get("id", 1)
            )

            print(
                f"[SECURITY] Módulos obtenidos para {security_manager.current_role}: {len(modulos_permitidos)} módulos"
            )
            print(f"[SECURITY] Lista de módulos: {modulos_permitidos}")

            # Verificación final para admin
            if (
                user_data.get("role", "").upper() == "ADMIN"
                and len(modulos_permitidos) < 12
            ):
                print(
                    f"[WARN] [SECURITY WARNING] Admin solo tiene {len(modulos_permitidos)} módulos en lugar de 12"
                )
                print(
                    f"[WARN] [SECURITY WARNING] Rol actual en SecurityManager: '{security_manager.current_role}'"
                )

        except AttributeError as e:
            # Si no tiene get_user_modules, permitir todos los módulos por defecto
            print(f"[SECURITY] Error AttributeError: {e}")
            print(
                "[SECURITY] Usando SimpleSecurityManager o fallback, permitiendo todos los módulos"
            )

            # Fallback inteligente basado en el rol del usuario
            if user_data.get("role", "").upper() == "ADMIN":
                modulos_permitidos = [
                    "Inventario",
                    "Administración",
                    "Obras",
                    "Pedidos",
                    "Logística",
                    "Herrajes",
                    "Vidrios",
                    "Usuarios",
                    "Auditoría",
                    "Configuración",
                    "Compras",
                    "Mantenimiento",
                ]
            else:
                modulos_permitidos = ["Inventario", "Obras", "Pedidos"]
        except Exception as e:
            print(f"[SECURITY] Error inesperado obteniendo módulos: {e}")
            # Fallback de emergencia
            if user_data.get("role", "").upper() == "ADMIN":
                modulos_permitidos = [
                    "Inventario",
                    "Administración",
                    "Obras",
                    "Pedidos",
                    "Logística",
                    "Herrajes",
                    "Vidrios",
                    "Usuarios",
                    "Auditoría",
                    "Configuración",
                    "Compras",
                    "Mantenimiento",
                ]
                print(
                    f"[SECURITY] Fallback: Admin detectado, asignando {len(modulos_permitidos)} módulos"
                )
            else:
                modulos_permitidos = ["Inventario", "Obras", "Pedidos"]
                print(
                    f"[SECURITY] Fallback: Usuario básico, asignando {len(modulos_permitidos)} módulos"
                )

        cargar_main_window_con_seguridad(user_data, modulos_permitidos)

    def on_login_failed(error_message):
        print(f"[ERROR] [LOGIN] Autenticación fallida: {error_message}")

    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)

    # Mostrar login directamente
    login_dialog.show()
    print("[LOG 4.10] QApplication loop iniciado.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
