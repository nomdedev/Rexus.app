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

# ===== CONSTANTES =====
AUDITORIA_MODULE = "Auditoría"

# ===== IMPORTS CONSOLIDADOS =====
# Imports estándar
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# PyQt6 imports
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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

# Configuración básica de logging
logger = logging.getLogger("rexus.main")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Importar sistema de logging centralizado
try:
    from rexus.utils.app_logger import (
        get_logger, log_info, log_error, log_critical, log_warning, 
        log_security, app_logger
    )
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback si el logger no está disponible
    def get_logger(name): return logging.getLogger(name)
    def log_info(msg, comp="general"): logger.info(msg)
    def log_error(msg, comp="general"): logger.error(msg)
    def log_critical(msg, comp="general"): print(f"[CRITICAL] {msg}")
    def log_warning(msg, comp="general"): logger.warning(msg)
    def log_security(level, msg, user=None): print(f"[SECURITY-{level}] {msg}")
    app_logger = None  # Agregar fallback para app_logger
    LOGGING_AVAILABLE = False

# Importar validador de dependencias críticas
try:
    from rexus.utils.dependency_validator import validate_system_dependencies, DependencyValidator
    DEPENDENCY_VALIDATION_AVAILABLE = True
except ImportError:
    def validate_system_dependencies() -> Tuple[bool, Dict[str, Any]]: return True, {"status": "FALLBACK"}
    DependencyValidator = None  # Agregar fallback para DependencyValidator
    DEPENDENCY_VALIDATION_AVAILABLE = False

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv(root_dir / ".env")
    log_info("Variables de entorno cargadas desde .env", "startup")
except ImportError:
    log_warning("python-dotenv no instalado, usando variables del sistema", "startup")
except Exception as e:
    print(f"[ENV] Error cargando .env: {e}")

# Imports del core de Rexus
from rexus.core.login_dialog import LoginDialog
from rexus.core.module_manager import module_manager
from rexus.ui.dashboard import DashboardController
from rexus.ui.components.theme_manager import ThemeManager


def initialize_security_manager():
    # Inicializa el sistema de seguridad
    try:
        from rexus.core.database import UsersDatabaseConnection
        from rexus.core.security import init_security_manager

        # Intentar crear conexión a la base de datos
        try:
            db_connection = UsersDatabaseConnection()
            logger.info("[SECURITY] Conexión BD exitosa para sistema de seguridad")
        except Exception as db_error:
            logger.warning("[SECURITY] Error BD: %s, usando modo sin BD", db_error)
            db_connection = None

        # Inicializar con o sin conexión BD
        security_manager = init_security_manager(db_connection)
        log_security("INFO", "SecurityManager inicializado correctamente")
        return security_manager

    except ImportError as e:
        log_security("CRITICAL", f"Error importando módulo de seguridad: {e}")
        return SimpleSecurityManager()
    except Exception as e:
        log_security("CRITICAL", f"Error general inicializando seguridad: {e}")
        return SimpleSecurityManager()


class SimpleSecurityManager:
    # Sistema de seguridad simple para fallback

    def __init__(self):
        self.current_user_data = None
        self.current_user = None  # Para compatibilidad con SecurityManager
        self.current_role = "usuario"  # Para compatibilidad con SecurityManager
        # Sistema seguro sin credenciales hardcodeadas
        # Las credenciales se cargan desde variables de entorno
        self._load_secure_credentials()

    def _load_secure_credentials(self):
        # Carga credenciales desde variables de entorno de forma segura
        from rexus.utils.security import SecurityUtils

        # Solo cargar si está en modo desarrollo y se especifica explícitamente
        if os.environ.get("DEVELOPMENT_MODE") == "true":
            admin_user = os.environ.get("FALLBACK_ADMIN_USER")
            admin_password = os.environ.get("FALLBACK_ADMIN_PASSWORD")

            if admin_user and admin_password:
                # Hash seguro de la contraseña (devuelve hash y salt)
                hashed_password, salt = SecurityUtils.hash_password(admin_password)
                self.users = {
                    admin_user: {
                        "rol": "ADMIN",
                        "id": 1,
                        "username": admin_user,
                        "password_hash": hashed_password,
                        "salt": salt,
                    }
                }
                logger.info("[SIMPLE_AUTH] Usuario de desarrollo cargado: %s", admin_user)
            else:
                self.users = {}
                logger.warning("[SIMPLE_AUTH] Modo desarrollo activo pero sin credenciales configuradas")
        else:
            self.users = {}
            logger.info("[SIMPLE_AUTH] Modo producción - sin usuarios fallback")
    def login(self, username: str, password: str) -> bool:
        # Autenticación segura con hashing
        logger.info("[SIMPLE_AUTH] Intentando login: usuario='%s'", username)

        # Verificar si hay usuarios disponibles
        if not self.users:
            logger.warning("[SIMPLE_AUTH] No hay usuarios fallback disponibles")
            return False

        user = self.users.get(username)
        if not user:
            print(f"[SIMPLE_AUTH] Usuario '{username}' no encontrado")
            return False

        # Verificar contraseña con hash seguro
        try:
            from rexus.utils.security import SecurityUtils

            salt = user.get("salt", "")
            if SecurityUtils.verify_password(password, user.get("password_hash", ""), salt):
                print(f"[SIMPLE_AUTH] Login exitoso para {username}")
                self.current_user_data = {
                    k: v for k, v in user.items() if k not in ["password_hash", "salt"]
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
            return False

    def get_current_role(self) -> str:
        # Obtiene el rol actual
        return (
            self.current_user_data.get("rol", "USUARIO")
            if self.current_user_data
            else "USUARIO"
        )

    def get_current_user(self) -> dict:
        # Obtiene datos del usuario actual
        return (
            self.current_user_data
            if self.current_user_data
            else {"id": 0, "username": "guest", "rol": "USUARIO"}
        )

    def has_permission(self, permission: str, module: str | None = None) -> bool:
        # Verifica permisos - admin tiene todos
        return bool(self.current_user_data and \
            self.current_user_data.get("rol") == "ADMIN")

    def log_security_event(
        self, user_id: int, accion: str, modulo: str | None = None, detalles: str | None = None
    ):
        # Log simple de eventos
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[SECURITY_LOG] {timestamp} - Usuario:{user_id} - Acción:{accion} - Módulo:{modulo} - Detalles:{detalles}"
        )

    def diagnose_permissions(self) -> dict:
        # Diagnóstica el estado de permisos del usuario actual
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
        
        # Inicializar gestores de tema y dashboard
        self._init_theme_manager()
        self._init_dashboard_controller()
        self._init_executive_dashboard()

        # Inicializar StyleManager y aplicar tema automático
        self._init_styles()
        self._init_ui()
    
    def _init_theme_manager(self):
        # Inicializa el gestor de temas.
        try:
            self.theme_manager = ThemeManager(self)
            self.theme_manager.apply_theme()  # Aplicar tema por defecto
            print("[THEME] Gestor de temas inicializado correctamente")
        except Exception as e:
            logger.warning(f"Error inicializando ThemeManager: {e}")
            self.theme_manager = None
    
    def _init_dashboard_controller(self):
        # Inicializa el controlador del dashboard.
        try:
            # Crear controlador del dashboard sin db_manager por ahora
            self.dashboard_controller = DashboardController(None, self)
            print("[DASHBOARD] Controlador de dashboard inicializado")
        except Exception as e:
            logger.warning(f"Error inicializando DashboardController: {e}")
            self.dashboard_controller = None
    
    def _init_executive_dashboard(self):
        # Inicializa el dashboard ejecutivo.
        try:
            from rexus.ui.executive_dashboard import get_dashboard_manager
            self.executive_dashboard_manager = get_dashboard_manager()
            print("[EXECUTIVE_DASHBOARD] Gestor de dashboard ejecutivo inicializado")
        except Exception as e:
            logger.warning(f"Error inicializando Executive Dashboard: {e}")
            self.executive_dashboard_manager = None

    def _init_styles(self):
        # Inicializa y aplica el sistema de estilos.
        try:
            from rexus.ui.style_manager import StyleManager

            self.style_manager = StyleManager()

            # Aplicar tema global (auto-detectado en StyleManager)
            success = self.style_manager.apply_global_theme()
            if success:
                print(f"[STYLE] Tema '{self.style_manager._current_theme}' aplicado globalmente")

                # CRÍTICO: Aplicar correcciones de formularios inmediatamente
                # Aplicar correcciones ultra-seguras para todos los temas
                emergency_success = self.style_manager.apply_emergency_readable_forms()
                if emergency_success:
                    print("[STYLE] [OK] Formularios ultra-legibles aplicados correctamente")
                else:
                    print("[STYLE] [WARNING] Intentando correcciones alternativas...")

                    # Fallback: Intentar correcciones específicas por tema
                    if self.style_manager._current_theme == 'dark':
                        print("[STYLE] Tema oscuro detectado - aplicando correcciones críticas")
                        fix_success = self.style_manager.apply_critical_form_fixes()
                        if not fix_success:
                            # Si falla, forzar tema claro para formularios
                            fallback_success = self.style_manager.force_light_theme_for_forms()
                            if fallback_success:
                                print("[STYLE] Tema de emergencia aplicado - formularios legibles")
                            else:
                                print("[STYLE] [ERROR] ERROR: No se pudieron aplicar correcciones críticas")
                    else:
                        # Para temas claros, asegurar contraste
                        self.style_manager.apply_critical_form_fixes()
            else:
                print("[STYLE] Fallback a estilos por defecto")

        except Exception as e:
            logger.warning(f"Error inicializando StyleManager: {e}")
            self.style_manager = None

    def _init_ui(self):
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        
        # Configurar ventana con tamaño mínimo
        self.setMinimumSize(1024, 768)
        
        # Configurar para iniciar maximizado de forma más robusta
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.showMaximized)

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

        # Aplicar estilos respetando el theme manager
        if self.style_manager:
            # No aplicar estilos inline que sobrescriban el theme manager
            # El StyleManager ya maneja los colores de fondo apropiados
            pass
        else:
            # Solo si no hay StyleManager disponible
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                }
            """)

    def _create_sidebar(self, main_layout):
        # Crea la barra lateral con módulos
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2563eb !important;
                border-right: 2px solid #1d4ed8 !important;
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

        # Usuario actual y dashboard
        user_info_container = QWidget()
        user_info_layout = QVBoxLayout(user_info_container)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(5)
        
        user_info = QLabel(
            f"Usuario: {self.user_data['username']}\nRol: {self.user_data.get('rol', self.user_data.get('role', 'Usuario'))}"
        )
        user_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                padding: 15px 20px;
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Botón para dashboard ejecutivo
        from rexus.ui.dashboard_integration import create_dashboard_button
        dashboard_btn = create_dashboard_button()
        dashboard_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                margin: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        user_info_layout.addWidget(user_info)
        user_info_layout.addWidget(dashboard_btn)
        sidebar_layout.addWidget(user_info_container)

        # Scroll area para módulos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.8);
                border-color: #ffffff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        modules_widget = QWidget()
        modules_layout = QVBoxLayout(modules_widget)
        # Módulos ordenados por flujo de proyecto real (incluye Logística)
        modulos = [
            ("🏗️", "Obras", "Gestión de proyectos y construcción"),
            ("📦", "Inventario", "Gestión de inventario y stock"),
            ("🛠️", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("🚚", "Logística", "Gestión de logística y transporte"),
            ("[NOTE]", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("💼", "Administración", "Gestión administrativa y financiera"),
            ("🧰", "Mantenimiento", "Gestión de mantenimiento"),
            ("🔎", AUDITORIA_MODULE, "Auditoría y trazabilidad"),
            ("👤", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]

        logger.debug(f"Módulos permitidos: {self.modulos_permitidos}")

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
        
        # Agregar botón de toggle de tema al final del sidebar
        if self.theme_manager:
            theme_btn = QPushButton("🌙 Alternar Tema")
            theme_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.3);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                    padding: 8px;
                    margin: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.5);
                }
            """)
            theme_btn.clicked.connect(self.toggle_theme)
            sidebar_layout.addWidget(theme_btn)

        main_layout.addWidget(sidebar)

    def _create_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        # Crea un botón de módulo estilizado
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 10px 16px;
    border: 2px solid #1e40af !important;
    font-size: 13px;
    font-weight: 600;
    background-color: #3b82f6 !important;
    color: #ffffff !important;
    border-radius: 8px;
    margin: 3px 8px;
    max-height: 40px;
    min-height: 40px;
}
QPushButton:hover {
    background-color: #1d4ed8 !important;
    border-color: #1e3a8a !important;
    color: #ffffff !important;
    font-weight: bold;
    transform: none;
}
QPushButton:pressed {
    background-color: #1e40af !important;
    border-color: #1e3a8a !important;
    color: #ffffff !important;
}
            """
        )
        btn.clicked.connect(lambda checked, name=nombre: self.show_module(name))
        return btn

    def _create_disabled_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        # Crea un botón de módulo deshabilitado para módulos sin permisos
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setEnabled(False)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 8px 16px;
    border: none;
    color: #888888;
    font-size: 13px;
    font-weight: 400;
    max-height: 36px;
    min-height: 36px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    margin: 2px 8px;
}
QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.05);
    color: #666666;
}
            """
        )
        return btn

    def _create_main_content(self, main_layout):
        # Crea el área de contenido principal
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

        # Dashboard inicial premium
        self._create_premium_dashboard()

        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_area)

    def _create_dashboard(self):
        # Crea el dashboard principal - RENOVADO COMPLETAMENTE
        dashboard = QWidget()
        dashboard.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #1a1a1a;
            }
        """)
        main_layout = QVBoxLayout(dashboard)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header compacto y limpio
        header = self._create_simple_header()
        main_layout.addWidget(header)

        # Grid principal con estadísticas
        stats_grid = self._create_stats_grid()
        main_layout.addWidget(stats_grid)

        # Sección de acceso rápido
        quick_access = self._create_simple_quick_access()
        main_layout.addWidget(quick_access)

        # Footer minimalista
        footer = self._create_simple_footer()
        main_layout.addWidget(footer)

        self.content_stack.addWidget(dashboard)

    def _create_premium_dashboard(self):
        # Crea el dashboard moderno con widgets especializados.
        try:
            if self.dashboard_controller:
                dashboard = self.dashboard_controller.get_view()
                dashboard.modulo_solicitado.connect(self.show_module)
                self.content_stack.addWidget(dashboard)
                print("[DASHBOARD] Dashboard moderno cargado correctamente")
            else:
                # Fallback al dashboard básico si el controlador no está disponible
                self._create_dashboard()
                print("[DASHBOARD] Usando dashboard básico como fallback")
        except Exception as e:
            logger.error(f"Error creando dashboard moderno: {e}")
            self._create_dashboard()  # Fallback seguro

    def _create_simple_header(self):
        # Header limpio y compacto
        from datetime import datetime

        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)

        # Título principal
        title = QLabel("Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #212529;
            }
        """)

        # Fecha actual
        date_label = QLabel(datetime.now().strftime("%d de %B, %Y"))
        date_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
            }
        """)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(date_label)

        return header

    def _create_stats_grid(self):
        # Grid de estadísticas principales
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(stats_widget)

        # Título de sección
        section_title = QLabel("[CHART] Estadísticas del Sistema")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(section_title)

        # Grid de tarjetas
        grid = QGridLayout()
        grid.setSpacing(15)

        # Estadísticas simples
        stats = [
            ("Productos", "1,234", "#007bff"),
            ("Obras", "23", "#28a745"),
            ("Pedidos", "56", "#ffc107"),
            ("Usuarios", f"{len(self.modulos_permitidos)}", "#6f42c1")
        ]

        for i, (label, value, color) in enumerate(stats):
            card = self._create_simple_stat_card(label, value, color)
            grid.addWidget(card, 0, i)

        layout.addLayout(grid)
        return stats_widget

    def _create_simple_stat_card(self, label, value, color):
        # Tarjeta de estadística simple
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 20px;
                min-height: 80px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border-color: {color};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: {color};
                margin: 0;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                margin: 0;
            }
        """)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(label_widget)

        return card

    def _create_simple_quick_access(self):
        # Acceso rápido minimalista
        quick_widget = QWidget()
        quick_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(quick_widget)

        # Título
        title = QLabel("[ROCKET] Acceso Rápido")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)

        # Botones principales
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        quick_modules = [
            ("📦", "Inventario"),
            ("🏗️", "Obras"),
            ("[NOTE]", "Pedidos"),
            ("👤", "Usuarios")
        ]

        for emoji, name in quick_modules:
            if name in self.modulos_permitidos:
                btn = QPushButton(f"{emoji} {name}")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 15px 25px;
                        font-size: 14px;
                        font-weight: 500;
                        min-width: 120px;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                """)
                btn.clicked.connect(lambda checked, module=name: self.show_module(module))
                buttons_layout.addWidget(btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return quick_widget

    def _create_simple_footer(self):
        # Footer minimalista
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 5, 20, 5)

        # Información del sistema
        info = QLabel("Rexus.app v2.0.0 - Sistema Operativo")
        info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)

        # Usuario actual
        user_info = QLabel(f"Usuario: {self.user_data.get('username', 'N/A')}")
        user_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)

        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(user_info)

        return footer

    def _create_dashboard_header(self):
        # Crea el header del dashboard moderno y limpio
        from datetime import datetime

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            }
        """)

        # Información del usuario
        user_info = QWidget()
        user_layout = QVBoxLayout(user_info)

        welcome_title = QLabel(f"¡Bienvenido, {self.user_data.get('username', 'Usuario')}!")
        welcome_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }
        """)

        user_role = QLabel(f"Rol: {self.user_data.get('rol', self.user_data.get('role', 'N/A'))}")
        user_role.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #586069;
                margin-top: 5px;
            }
        """)

        current_date = QLabel(f"Hoy es {datetime.now().strftime('%d de %B de %Y')}")
        current_date.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                margin-top: 5px;
            }
        """)

        user_layout.addWidget(welcome_title)
        user_layout.addWidget(user_role)
        user_layout.addWidget(current_date)

        # Logo o espacio para empresa - moderno y limpio
        logo_space = QLabel("REXUS.APP")
        logo_space.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #0366d6;
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 8px 16px;
            }
        """)

        header_layout.addWidget(user_info)
        header_layout.addStretch()
        header_layout.addWidget(logo_space)

        return header_widget

    def show_module(self, module_name: str):
        """Muestra el módulo seleccionado en el área de contenido."""
        try:
            logger.info(f"Cargando módulo: {module_name}")

            # Obtener el módulo desde el module_manager
            module = module_manager.get_module(module_name)

            if module:
                # Crear vista del módulo
                module_view = module.get_view()
                module_view.modulo_solicitado.connect(self.show_module)

                # Agregar al stack si no existe
                for i in range(self.content_stack.count()):
                    if self.content_stack.widget(i).objectName() == module_name:
                        self.content_stack.setCurrentIndex(i)
                        return

                module_view.setObjectName(module_name)
                self.content_stack.addWidget(module_view)
                self.content_stack.setCurrentWidget(module_view)

                logger.info(f"Módulo {module_name} cargado exitosamente")
            else:
                logger.error(f"Módulo {module_name} no encontrado")
                self._show_error_message(f"Módulo '{module_name}' no disponible")

        except Exception as e:
            logger.error(f"Error cargando módulo {module_name}: {e}")
            self._show_error_message(f"Error cargando módulo: {str(e)}")

    def _show_error_message(self, message: str):
        """Muestra un mensaje de error al usuario."""
        QMessageBox.warning(self, "Error", message)

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        if self.theme_manager:
            try:
                self.theme_manager.toggle_theme()
                logger.info("Tema alternado exitosamente")
            except Exception as e:
                logger.error(f"Error alternando tema: {e}")
        else:
            logger.warning("ThemeManager no disponible")

    def closeEvent(self, event):
        """Maneja el evento de cierre de la aplicación."""
        logger.info("Cerrando aplicación Rexus.app")
        event.accept()


def main():
    """Función principal de la aplicación."""
    try:
        # Validar dependencias críticas
        if DEPENDENCY_VALIDATION_AVAILABLE:
            success, deps_info = validate_system_dependencies()
            if not success:
                print("[CRITICAL] Dependencias faltantes:")
                for dep, status in deps_info.items():
                    if not status.get('available', False):
                        print(f"  - {dep}: {status.get('error', 'No disponible')}")
                return 1

        # Inicializar aplicación Qt
        from PyQt6.QtWidgets import QApplication
        import sys

        app = QApplication(sys.argv)

        # Configurar aplicación
        app.setApplicationName("Rexus.app")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Rexus")

        # Inicializar sistema de seguridad
        security_manager = initialize_security_manager()

        # Mostrar diálogo de login
        login_dialog = LoginDialog(security_manager)
        if login_dialog.exec() == LoginDialog.Accepted:
            user_data = login_dialog.get_user_data()
            modulos_permitidos = login_dialog.get_modulos_permitidos()

            # Crear ventana principal
            window = MainWindow(user_data, modulos_permitidos)
            window.show()

            # Ejecutar aplicación
            return app.exec()
        else:
            logger.info("Login cancelado por el usuario")
            return 0

    except Exception as e:
        logger.critical(f"Error crítico en main(): {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
