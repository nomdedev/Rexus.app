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

# Imports estándar
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

# Imports de PyQt6
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

# Imports del core de Rexus
from rexus.core.login_dialog import LoginDialog
from rexus.core.module_manager import module_manager
from rexus.main.dashboard_premium import PremiumDashboard


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

    def has_permission(self, permission: str, module: str | None = None) -> bool:
        """Verifica permisos - admin tiene todos"""
        return bool(self.current_user_data and self.current_user_data.get("rol") == "ADMIN")

    def log_security_event(
        self, user_id: int, accion: str, modulo: str | None = None, detalles: str | None = None
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
            print(f"[WARNING] Error inicializando StyleManager: {e}")
            self.style_manager = None

    def _init_ui(self):
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        # Configurar para iniciar en fullscreen maximizado
        self.showMaximized()

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
        """Crea la barra lateral con módulos"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
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
            ("🛠️", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("🚚", "Logística", "Gestión de logística y transporte"),
            ("[NOTE]", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("💼", "Administración", "Gestión administrativa y financiera"),
            ("🧰", "Mantenimiento", "Gestión de mantenimiento"),
            ("🔎", "Auditoría", "Auditoría y trazabilidad"),
            ("👤", "Usuarios", "Gestión de personal y roles"),
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
    padding: 8px 16px;
    border: none;
    font-size: 13px;
    font-weight: 500;
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    margin: 2px 8px;
    max-height: 36px;
    min-height: 36px;
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

        # Dashboard inicial premium
        self._create_premium_dashboard()

        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_area)

    def _create_dashboard(self):
        """Crea el dashboard principal - RENOVADO COMPLETAMENTE"""
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
        """Crea el dashboard premium moderno."""
        dashboard = PremiumDashboard(self.user_data)
        dashboard.navegar_modulo.connect(self.cargar_modulo)
        self.content_stack.addWidget(dashboard)

    def _create_simple_header(self):
        """Header limpio y compacto"""
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
        """Grid de estadísticas principales"""
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
        """Tarjeta de estadística simple"""
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
        """Acceso rápido minimalista"""
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
        """Footer minimalista"""
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
        """Crea el header del dashboard moderno y limpio"""
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
                padding: 12px 20px;
                min-width: 120px;
                text-align: center;
            }
        """)
        logo_space.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(user_info)
        header_layout.addStretch()
        header_layout.addWidget(logo_space)
        
        return header_widget

    def _create_left_dashboard_column(self):
        """Crea la columna izquierda con estadísticas y KPIs"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # KPIs principales
        kpi_section = self._create_kpi_section()
        left_layout.addWidget(kpi_section)
        
        # Gráfico o tabla de actividad reciente
        activity_section = self._create_activity_section()
        left_layout.addWidget(activity_section)
        
        return left_widget

    def _create_right_dashboard_column(self):
        """Crea la columna derecha con acceso rápido"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Acceso rápido a módulos
        quick_access = self._create_quick_access_section()
        right_layout.addWidget(quick_access)
        
        # Notificaciones o alertas
        notifications = self._create_notifications_section()
        right_layout.addWidget(notifications)
        
        return right_widget

    def _create_kpi_section(self):
        """Crea la sección de KPIs principales"""
        kpi_widget = QWidget()
        kpi_layout = QVBoxLayout(kpi_widget)
        
        title = QLabel("[CHART] Resumen Ejecutivo")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        kpi_layout.addWidget(title)
        
        # Grid de KPIs
        grid_layout = QGridLayout()
        
        # KPIs con datos dinámicos (simulados por ahora)
        kpis = [
            ("📦", "Productos", "1,234", "#3498db", "Stock total disponible"),
            ("[MONEY]", "Facturación", "$45,678", "#2ecc71", "Ingresos del mes"),
            ("🏗️", "Obras", "23", "#e74c3c", "Proyectos activos"),
            ("📋", "Pedidos", "56", "#f39c12", "Pendientes de procesar"),
            ("👥", "Usuarios", f"{len(self.modulos_permitidos)}", "#9b59b6", "Módulos activos"),
            ("⚙️", "Sistema", "100%", "#34495e", "Estado operativo")
        ]
        
        for i, (icon, title_text, value, color, subtitle) in enumerate(kpis):
            card = self._create_modern_kpi_card(icon, title_text, value, color, subtitle)
            row, col = i // 3, i % 3
            grid_layout.addWidget(card, row, col)
        
        kpi_layout.addLayout(grid_layout)
        return kpi_widget

    def _create_modern_kpi_card(self, icon, title, value, color, subtitle):
        """Crea una tarjeta KPI moderna y limpia"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e1e4e8;
                border-left: 4px solid {color};
                border-radius: 6px;
                padding: 16px;
                margin: 4px;
            }}
            QFrame:hover {{
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            font-weight: 600;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #24292e;
            margin: 8px 0px;
        """)
        
        # Subtítulo
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 11px;
            color: #586069;
        """)
        subtitle_label.setWordWrap(True)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        
        return card

    def _create_activity_section(self):
        """Crea la sección de actividad reciente"""
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        
        title = QLabel("📈 Actividad Reciente")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #24292e;
                margin-bottom: 12px;
            }
        """)
        activity_layout.addWidget(title)
        
        # Lista de actividades
        activities_frame = QFrame()
        activities_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 16px;
            }
        """)
        
        activities_layout = QVBoxLayout(activities_frame)
        
        # Actividades simuladas
        activities = [
            ("[OK]", "Nuevo pedido registrado", "Hace 2 horas", "#28a745"),
            ("📦", "Inventario actualizado", "Hace 4 horas", "#0366d6"),
            ("🏗️", "Obra finalizada", "Ayer", "#d73a49"),
            ("👤", "Usuario conectado", "Hace 1 hora", "#6f42c1"),
            ("💾", "Backup completado", "Hace 6 horas", "#586069")
        ]
        
        for icon, text, time, color in activities:
            activity_item = self._create_activity_item(icon, text, time, color)
            activities_layout.addWidget(activity_item)
        
        activity_layout.addWidget(activities_frame)
        return activity_widget

    def _create_activity_item(self, icon, text, time, color):
        """Crea un elemento de actividad individual"""
        item_widget = QWidget()
        item_widget.setFixedHeight(48)
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(8, 8, 8, 8)
        
        # Ícono con background
        icon_label = QLabel(icon)
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color}10;
                border-radius: 12px;
                font-size: 12px;
                color: {color};
            }}
        """)
        
        # Contenido vertical
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(12, 0, 0, 0)
        
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #24292e;
            }
        """)
        
        time_label = QLabel(time)
        time_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #586069;
            }
        """)
        
        content_layout.addWidget(text_label)
        content_layout.addWidget(time_label)
        
        item_layout.addWidget(icon_label)
        item_layout.addLayout(content_layout)
        item_layout.addStretch()
        
        # Hover effect
        item_widget.setStyleSheet("""
            QWidget {
                border-radius: 4px;
                background-color: transparent;
            }
            QWidget:hover {
                background-color: #f6f8fa;
            }
        """)
        
        return item_widget

    def _create_quick_access_section(self):
        """Crea la sección de acceso rápido"""
        quick_widget = QWidget()
        quick_layout = QVBoxLayout(quick_widget)
        
        title = QLabel("[ROCKET] Acceso Rápido")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #24292e;
                margin-bottom: 12px;
            }
        """)
        quick_layout.addWidget(title)
        
        # Botones de acceso rápido
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 16px;
            }
        """)
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(8)
        
        # Módulos principales con acceso rápido
        quick_modules = [
            ("📦", "Inventario", "inventario"),
            ("🏗️", "Obras", "obras"),
            ("[MONEY]", "Compras", "compras"),
            ("👥", "Usuarios", "usuarios"),
            ("⚙️", "Configuración", "configuracion")
        ]
        
        for icon, name, module_key in quick_modules:
            if module_key in [m.lower().replace(' ', '').replace('ó', 'o') for m in self.modulos_permitidos]:
                button = self._create_quick_access_button(icon, name, module_key)
                buttons_layout.addWidget(button)
        
        quick_layout.addWidget(buttons_frame)
        return quick_widget

    def _create_quick_access_button(self, icon, name, module_key):
        """Crea un botón de acceso rápido"""
        button = QPushButton(f"{icon} {name}")
        button.setFixedHeight(40)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-size: 13px;
                font-weight: 500;
                color: #24292e;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #0366d6;
                color: #0366d6;
            }
            QPushButton:pressed {
                background-color: #e1e4e8;
            }
        """)
        
        # Conectar al módulo correspondiente
        button.clicked.connect(lambda: self._navigate_to_module(name))
        return button

    def _navigate_to_module(self, module_name):
        """Navega a un módulo específico"""
        try:
            # Buscar el módulo en la lista y navegar directamente
            for modulo in self.modulos_permitidos:
                if modulo.lower().replace(' ', '').replace('ó', 'o') == module_name.lower().replace(' ', '').replace('ó', 'o'):
                    self.show_module(modulo)
                    break
        except Exception as e:
            print(f"Error navegando a módulo {module_name}: {e}")
    
    def cargar_modulo(self, module_name):
        """Carga un módulo específico - método requerido por PremiumDashboard."""
        self._navigate_to_module(module_name)

    def _create_notifications_section(self):
        """Crea la sección de notificaciones"""
        notif_widget = QWidget()
        notif_layout = QVBoxLayout(notif_widget)
        
        title = QLabel("🔔 Alertas y Notificaciones")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #24292e;
                margin-bottom: 12px;
            }
        """)
        notif_layout.addWidget(title)
        
        # Frame de notificaciones
        notif_frame = QFrame()
        notif_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 16px;
            }
        """)
        
        notif_frame_layout = QVBoxLayout(notif_frame)
        
        # Notificaciones simuladas
        notifications = [
            ("[WARNING]", "Stock bajo en herrajes", "warning"),
            ("[OK]", "Backup completado", "success"),
            ("[CHART]", "Reporte mensual listo", "info"),
            ("🔄", "Sistema actualizado", "info")
        ]
        
        for icon, text, type_notif in notifications:
            notif_item = self._create_notification_item(icon, text, type_notif)
            notif_frame_layout.addWidget(notif_item)
        
        notif_layout.addWidget(notif_frame)
        return notif_widget

    def _create_notification_item(self, icon, text, notif_type):
        """Crea un elemento de notificación"""
        item = QWidget()
        item.setFixedHeight(44)
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(12, 8, 12, 8)
        
        colors = {
            "warning": "#fbbf24",
            "success": "#10b981", 
            "info": "#3b82f6",
            "error": "#ef4444"
        }
        
        color = colors.get(notif_type, "#6b7280")
        
        # Ícono con background circular
        icon_label = QLabel(icon)
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color}20;
                border-radius: 10px;
                font-size: 10px;
                color: {color};
            }}
        """)
        
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
                margin-left: 8px;
            }
        """)
        
        item_layout.addWidget(icon_label)
        item_layout.addWidget(text_label)
        item_layout.addStretch()
        
        # Background color and hover effect
        item.setStyleSheet(f"""
            QWidget {{
                background-color: {color}08;
                border-left: 3px solid {color};
                border-radius: 4px;
            }}
            QWidget:hover {{
                background-color: {color}15;
            }}
        """)
        
        return item

    def _create_dashboard_footer(self):
        """Crea el footer del dashboard"""
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        
        footer.setStyleSheet("""
            QWidget {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 12px 16px;
                margin-top: 8px;
            }
        """)
        
        # Información del sistema
        system_info = QLabel("🖥️ Sistema Operativo | [LOCK] Seguridad Activa | 💾 Base de Datos Conectada")
        system_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #586069;
            }
        """)
        
        # Versión
        version_info = QLabel("Rexus.app v0.1.0")
        version_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
                color: #24292e;
            }
        """)
        
        footer_layout.addWidget(system_info)
        footer_layout.addStretch()
        footer_layout.addWidget(version_info)
        
        return footer


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
            # Crear fallback con error específico
            fallback_widget = self._create_fallback_module(module_name, str(e))
            self.content_stack.addWidget(fallback_widget)
            self.content_stack.setCurrentWidget(fallback_widget)

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
            return self._create_fallback_module(module_name, f"Módulo {module_name} no implementado o no encontrado")

    def _create_administracion_module(self) -> QWidget:
        """Crea el módulo de administración usando la vista real"""
        try:
            from rexus.modules.administracion.view import AdministracionView

            view = AdministracionView()
            return view
        except Exception as e:
            print(f"Error creando administración real: {e}")
            return self._create_fallback_module("Administración", str(e))

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
            return self._create_fallback_module("Inventario", str(e))

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
            
            # Import condicional para la vista
            try:
                from rexus.modules.administracion.contabilidad.view import ContabilidadView
            except ImportError:
                print("ContabilidadView no encontrada, usando fallback")
                return self._create_fallback_module("Contabilidad", "Vista no disponible")

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
            return self._create_fallback_module("Contabilidad", str(e))

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
            return self._create_fallback_module("Obras", str(e))

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
            return self._create_fallback_module("Configuración", str(e))

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
            return self._create_fallback_module("Vidrios", str(e))

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
            return self._create_fallback_module("Herrajes", str(e))

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
            return self._create_fallback_module("Pedidos", str(e))

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
            return self._create_fallback_module("Logística", str(e))

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
            return self._create_fallback_module("Usuarios", str(e))

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
            return self._create_fallback_module("Auditoría", str(e))

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
            return self._create_fallback_module("Compras", str(e))

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
            return self._create_fallback_module("Mantenimiento", str(e))

    def _create_fallback_module(self, module_name: str, error_details: str | None = None) -> QWidget:
        """Crea un módulo de fallback cuando el real no está disponible"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        icon_map = {
            "Vidrios": "🪟",
            "Herrajes": "[TOOL]",
            "Pedidos": "[NOTE]",
            "Logística": "🚚",
            "Usuarios": "👤",
            "Auditoría": "[SEARCH]",
            "Compras": "🛒",
            "Mantenimiento": "🧰",
            "Obras": "🏗️",
            "Inventario": "📦",
            "Administración": "💼",
            "Configuración": "⚙️",
        }

        # Obtener icono para el módulo
        module_icon = icon_map.get(module_name, "[WARNING]")

        # Contenido centrado
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono grande con estado de error
        icon_label = QLabel(module_icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                margin-bottom: 20px;
                color: #f39c12;
            }
        """)

        # Título
        title_label = QLabel(f"Error cargando {module_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
                margin-bottom: 15px;
            }
        """)

        # Descripción del error específico
        if error_details:
            desc_label = QLabel(f"Error específico: {error_details}")
        else:
            desc_label = QLabel("El módulo no pudo iniciarse. Consulta los logs para más detalles.")
            
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(600)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #95a5a6;
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                line-height: 1.4;
            }
        """)

        # Información adicional
        help_label = QLabel("Posibles causas:\n• Faltan dependencias del módulo\n• Error en la configuración\n• Problemas de permisos de base de datos")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_label.setWordWrap(True)
        help_label.setMaximumWidth(500)
        help_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                margin-top: 15px;
                padding: 10px;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 6px;
                line-height: 1.3;
            }
        """)

        content_layout.addWidget(icon_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        content_layout.addWidget(help_label)

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
    print("[LOG 4.1] Inicializando QtWebEngine de forma robusta...")
    
    # Usar el gestor robusto de WebEngine
    from rexus.utils.webengine_manager import webengine_manager
    
    qtwebengine_available = webengine_manager.is_webengine_available()
    
    if qtwebengine_available:
        print("[LOG 4.1] QtWebEngine disponible y inicializado")
        import os
        os.environ["QT_OPENGL"] = "angle"  # Forzar OpenGL ANGLE para compatibilidad
        
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)
    else:
        print("[LOG 4.1] QtWebEngine no disponible, usando fallbacks")
        webengine_status = webengine_manager.get_status_info()
        print(f"[LOG 4.1] Razones: {webengine_status['fallback_reasons']}")
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
                f"[SEGURIDAD] Creando MainWindow para usuario: {user_data['username']}"
            )
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.actualizar_usuario_label(user_data)
            main_window.show()
            print(f"[CHECK] [SEGURIDAD] Aplicación iniciada para {user_data['username']}")
        except Exception as e:
            import traceback

            error_msg = f"[ERROR SEGURIDAD] {e}\n{traceback.format_exc()}"
            print(f"[ERROR] [ERROR] {error_msg}", flush=True)
            Path("logs").mkdir(exist_ok=True)
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

        # [HOT] SOLUCIÓN CRÍTICA: Establecer contexto de seguridad ANTES de obtener módulos
        try:
            # Establecer usuario y rol actual en SecurityManager
            security_manager.current_user = user_data
            security_manager.current_role = user_data.get("role", "usuario")

            print(
                f"[SECURITY] Contexto establecido - Usuario: {user_data.get('username')}, Rol: {security_manager.current_role}"
            )

            # [SEARCH] DIAGNÓSTICO: Verificar estado del sistema de permisos
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
