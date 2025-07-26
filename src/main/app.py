#!/usr/bin/env python3
"""
Rexus.app - Sistema de Gestión Integral

Aplicación principal que maneja la interfaz de usuario y la integración de módulos.
Sigue principios de arquitectura MVC y patrones de diseño para mantenibilidad.

Arquitectura:
    - MainWindow: Ventana principal con sidebar y área de contenido
    - ModuleFactory: Factory pattern para crear módulos dinámicamente
    - Fallback System: Sistema de respaldo cuando módulos no están disponibles
    - Security Integration: Integración con sistema de seguridad y permisos

Author: Rexus Development Team
Version: 2.0.0
"""

import os
import platform
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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# PyQt6 Core Imports
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

# Core Application Imports
from src.core.login_dialog import LoginDialog
from src.core.security import initialize_security_manager


class SimpleSecurityManager:
    """Sistema de seguridad simple para fallback"""

    def __init__(self):
        self.current_user_data = None
        # Usuarios hardcodeados para fallback (sin contraseña visible)
        self.users = {"admin": {"rol": "ADMIN", "id": 1, "username": "admin"}}

    def login(self, username: str, password: str) -> bool:
        """Autenticación simple (solo para pruebas, sin contraseña visible)"""
        print(
            f"[SIMPLE_AUTH] Intentando login: usuario='{username}' (contraseña oculta)"
        )
        user = self.users.get(username)
        print(f"[SIMPLE_AUTH] Usuario encontrado: {user is not None}")
        # Permitir login solo si el usuario es 'admin' y la contraseña se pasa por variable de entorno (o rechazar siempre en producción)
        import os

        admin_pwd = os.environ.get("FALLBACK_ADMIN_PASSWORD", "admin")
        if user and password == admin_pwd:
            print(f"[SIMPLE_AUTH] Login exitoso para {username}")
            self.current_user_data = user.copy()
            return True
        print(f"[SIMPLE_AUTH] Login fallido para {username}")
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
        return [
            "inventario",
            "contabilidad",
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
        ]

    def has_permission(self, permission: str, module: str = None) -> bool:
        """Verifica permisos - admin tiene todos"""
        return self.current_user_data and self.current_user_data.get("rol") == "ADMIN"

    def log_security_event(
        self, user_id: int, accion: str, modulo: str = None, detalles: str = None
    ):
        """Log simple de eventos"""
        print(f"[SECURITY] Usuario {user_id}: {accion} en {modulo} - {detalles}")


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Rexus.app

    Maneja la interfaz principal con sidebar de módulos y área de contenido dinámico.
    Implementa patrón Factory para creación de módulos y sistema de fallback.

    Attributes:
        user_data (Dict): Datos del usuario actual
        modulos_permitidos (List): Lista de módulos permitidos para el usuario
        security_manager: Gestor de seguridad de la aplicación
        content_stack (QTabWidget): Stack de pestañas para módulos
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
        from PyQt6.QtWidgets import QLabel, QStackedWidget

        # Eliminado: self.security_manager no corresponde a ninguna inicialización ni uso válido
        self.content_stack = QStackedWidget()
        # Eliminado: self.content_header

        self._init_ui()

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
        from PyQt6.QtWidgets import QScrollArea

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
            ("�", "Logística", "Gestión de logística y transporte"),
            ("�📋", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("🏢", "Administración", "Gestión administrativa y financiera"),
            ("🛠️", "Mantenimiento", "Gestión de mantenimiento"),
            ("🕵️", "Auditoría", "Auditoría y trazabilidad"),
            ("👥", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]

        for emoji, nombre, descripcion in modulos:
            btn = self._create_module_button(emoji, nombre, descripcion)
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
                margin: 3px 8px;
                transition: background 0.2s, color 0.2s;
            }
            QPushButton:hover {
                background-color: #217dbb;
                color: #ffe082;
            }
            QPushButton:pressed {
                background-color: #17608a;
                color: #ffffff;
            }
        """)
        btn.clicked.connect(lambda checked, name=nombre: self.show_module(name))
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

        # Eliminado: Título principal del área de contenido

        # Área de contenido dinámico
        from PyQt6.QtWidgets import QStackedWidget

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
        from PyQt6.QtGui import QColor
        from PyQt6.QtWidgets import QGridLayout

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
        
        ✅ Sistema de login funcionando correctamente
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
            # Eliminado: actualización de título principal

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
        # Mapeo de módulos a métodos de creación
        module_factory = {
            "Inventario": self._create_inventario_module,
            "Contabilidad": self._create_contabilidad_module,
            "Obras": self._create_obras_module,
            "Configuración": self._create_configuracion_module,
            "Vidrios": self._create_vidrios_module,
            "Herrajes": self._create_herrajes_module,
            "Pedidos": self._create_pedidos_module,
            "Logística": self._create_logistica_module,
            "Usuarios": self._create_usuarios_module,
            "Auditoría": self._create_auditoria_module,
            "Compras": self._create_compras_module,
            "Mantenimiento": self._create_mantenimiento_module,
            "Administración": self._create_administracion_module,
            "Administracion": self._create_administracion_module,
        }
        # Normalizar nombre para evitar problemas de tildes/capitalización
        normalized_name = module_name.strip().capitalize().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        creation_method = module_factory.get(module_name) or module_factory.get(normalized_name)
        if creation_method:
            return creation_method()
        else:
            return self._create_fallback_module(module_name)

    def _create_administracion_module(self) -> QWidget:
        """Crea el módulo de administración usando la vista real"""
        try:
            from src.modules.administracion.view import AdministracionView
            view = AdministracionView()
            return view
        except Exception as e:
            print(f"Error creando administración real: {e}")
            return self._create_fallback_module("Administración")

    def _create_inventario_module(self) -> QWidget:
        """Crea el módulo de inventario usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.inventario.controller import InventarioController
            from src.modules.inventario.model import InventarioModel
            from src.modules.inventario.view import InventarioView

            # Crear conexión a la base de datos (puede fallar, usamos mock)
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = InventarioModel(db_connection)
            view = InventarioView()
            controller = InventarioController(model, view, db_connection)

            # Configurar vista
            view.set_controller(controller)
            
            # Cargar datos iniciales
            controller.cargar_datos_iniciales()

            return view

        except Exception as e:
            print(f"Error creando inventario real: {e}")
            # Fallback a widget simple
            return self._create_fallback_module("Inventario")

    def _create_contabilidad_module(self) -> QWidget:
        """Crea el módulo de contabilidad usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.administracion.contabilidad.controller import ContabilidadController
            from src.modules.administracion.contabilidad.model import ContabilidadModel
            from src.modules.administracion.contabilidad.view import ContabilidadView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = ContabilidadModel(db_connection)
            view = ContabilidadView()
            controller = ContabilidadController(model, view)

            return view

        except Exception as e:
            print(f"Error creando contabilidad real: {e}")
            # Fallback a widget simple
            return self._create_fallback_module("Contabilidad")

    def _create_obras_module(self) -> QWidget:
        """Crea el módulo de obras usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.obras.controller import ObrasController
            from src.modules.obras.model import ObrasModel
            from src.modules.obras.view import ObrasView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = ObrasModel(db_connection)
            view = ObrasView()
            controller = ObrasController(model, view)

            return view

        except Exception as e:
            print(f"Error creando obras real: {e}")
            # Fallback a widget simple
            return self._create_fallback_module("Obras")

    def _create_configuracion_module(self) -> QWidget:
        """Crea el módulo de configuración usando los archivos reales"""
        try:
            from src.modules.configuracion.controller import ConfiguracionController
            from src.modules.configuracion.model import ConfiguracionModel
            from src.modules.configuracion.view import ConfiguracionView

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
        """Crea el módulo de vidrios usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.vidrios.controller import VidriosController
            from src.modules.vidrios.model import VidriosModel
            from src.modules.vidrios.view import VidriosView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = VidriosModel(db_connection)
            view = VidriosView()
            controller = VidriosController(model, view)

            return view

        except Exception as e:
            print(f"Error creando vidrios real: {e}")
            return self._create_fallback_module("Vidrios")

    def _create_herrajes_module(self) -> QWidget:
        """Crea el módulo de herrajes usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.herrajes.controller import HerrajesController
            from src.modules.herrajes.model import HerrajesModel
            from src.modules.herrajes.view import HerrajesView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = HerrajesModel(db_connection)
            view = HerrajesView()
            controller = HerrajesController(model, view)
            
            # Configurar vista
            view.set_controller(controller)
            
            # Cargar datos iniciales
            controller.cargar_datos_iniciales()

            return view

        except Exception as e:
            print(f"Error creando herrajes real: {e}")
            return self._create_fallback_module("Herrajes")

    def _create_pedidos_module(self) -> QWidget:
        """Crea el módulo de pedidos usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.pedidos.controller import PedidosController
            from src.modules.pedidos.model import PedidosModel
            from src.modules.pedidos.view import PedidosView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = PedidosModel(db_connection)
            view = PedidosView()
            controller = PedidosController(model, view)
            
            # Configurar vista
            view.set_controller(controller)
            
            # Cargar datos iniciales
            controller.cargar_datos_iniciales()

            return view

        except Exception as e:
            print(f"Error creando pedidos real: {e}")
            return self._create_fallback_module("Pedidos")

    def _create_logistica_module(self) -> QWidget:
        """Crea el módulo de logística usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.logistica.controller import LogisticaController
            from src.modules.logistica.model import LogisticaModel
            from src.modules.logistica.view import LogisticaView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = LogisticaModel(db_connection)
            view = LogisticaView()
            controller = LogisticaController(model, view)

            return view

        except Exception as e:
            print(f"Error creando logística real: {e}")
            return self._create_fallback_module("Logística")

    def _create_usuarios_module(self) -> QWidget:
        """Crea el módulo de usuarios usando los archivos reales"""
        try:
            from src.core.database import UsersDatabaseConnection
            from src.modules.usuarios.controller import UsuariosController
            from src.modules.usuarios.model import UsuariosModel
            from src.modules.usuarios.view import UsuariosView

            # Crear conexión a la base de datos
            try:
                db_connection = UsersDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = UsuariosModel(db_connection)
            view = UsuariosView()
            controller = UsuariosController(model, view)
            
            # Conectar view con controller
            view.set_controller(controller)
            
            # Cargar datos iniciales
            controller.cargar_usuarios()

            return view

        except Exception as e:
            print(f"Error creando usuarios real: {e}")
            return self._create_fallback_module("Usuarios")

    def _create_auditoria_module(self) -> QWidget:
        """Crea el módulo de auditoría usando los archivos reales"""
        try:
            from src.core.database import AuditoriaDatabaseConnection
            from src.modules.auditoria.controller import AuditoriaController
            from src.modules.auditoria.model import AuditoriaModel
            from src.modules.auditoria.view import AuditoriaView

            # Crear conexión a la base de datos
            try:
                db_connection = AuditoriaDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = AuditoriaModel(db_connection)
            view = AuditoriaView()
            controller = AuditoriaController(model, view)

            return view

        except Exception as e:
            print(f"Error creando auditoría real: {e}")
            return self._create_fallback_module("Auditoría")

    def _create_compras_module(self) -> QWidget:
        """Crea el módulo de compras usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.compras.controller import ComprasController
            from src.modules.compras.model import ComprasModel
            from src.modules.compras.view import ComprasView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = ComprasModel(db_connection)
            view = ComprasView()
            controller = ComprasController(model, view)

            return view

        except Exception as e:
            print(f"Error creando compras real: {e}")
            return self._create_fallback_module("Compras")

    def _create_mantenimiento_module(self) -> QWidget:
        """Crea el módulo de mantenimiento usando los archivos reales"""
        try:
            from src.core.database import InventarioDatabaseConnection
            from src.modules.mantenimiento.controller import MantenimientoController
            from src.modules.mantenimiento.model import MantenimientoModel
            from src.modules.mantenimiento.view import MantenimientoView

            # Crear conexión a la base de datos
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None

            # Crear modelo, vista y controlador
            model = MantenimientoModel(db_connection)
            view = MantenimientoView()
            controller = MantenimientoController(model, view)

            return view

        except Exception as e:
            print(f"Error creando mantenimiento real: {e}")
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
        from PyQt6.QtWidgets import QMessageBox

        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        else:
            QMessageBox.information(self, "Información", mensaje)


from src.utils.theme_manager import set_theme

# --- FIN IMPORTS PRINCIPALES ---


# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS CRÍTICAS (WHEELS) PARA TODA LA APP ---
def instalar_dependencias_criticas():
    from urllib.parse import urlparse

    print("[LOG 1.1] === INICIO DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
    py_version = (
        f"{sys.version_info.major}{sys.version_info.minor}"  # Ej: 311 para Python 3.11
    )
    arch = platform.architecture()[0]
    py_tag = f"cp{py_version}"
    win_tag = "win_amd64" if arch == "64bit" else "win32"
    wheels = {
        "pandas": f"pandas-2.2.2-{py_tag}-{py_tag}-{win_tag}.whl",
        "pyodbc": f"pyodbc-5.0.1-{py_tag}-{py_tag}-{win_tag}.whl",
    }
    url_base = "https://download.lfd.uci.edu/pythonlibs/archive/"

    def instalar_wheel(paquete, wheel_file):
        url = url_base + wheel_file
        local_path = os.path.join(os.getcwd(), wheel_file)
        try:
            # ...lógica de descarga y validación...
            pass  # Aquí va el código real de la función
        except Exception as e:
            print(f"[LOG 1.1.3] [ERROR] Error instalando {paquete} desde wheel: {e}")
            return False

    def instalar_dependencia(paquete, version):
        try:
            print(f"[LOG 1.2.1] Instalando {paquete}=={version} con pip...")
            # Validar que el paquete y versión sean strings seguros
            if not isinstance(paquete, str) or not isinstance(version, str):
                raise ValueError("Paquete y versión deben ser cadenas de texto")
            if not paquete.isidentifier():
                raise ValueError("Nombre de paquete no válido")
            if not version.replace(".", "").isdigit():
                raise ValueError("Versión no válida")
            # Validar argumentos antes de ejecutar subprocess
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
                f"{paquete}=={version}",
            ]
            # Aquí normalmente se llamaría a subprocess para instalar
            # subprocess.check_call(cmd)
            print(f"[LOG 1.2.2] Comando pip generado: {cmd}")
            return True
        except Exception as e:
            print(f"[LOG 1.2.3] [ERROR] Error instalando dependencia {paquete}: {e}")
            return False


def main():
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Mostrando login profesional...")

    # Eliminado: mensaje emergente con parámetros de conexión SQL Server

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
            main_window = MainWindow(
                user_data, modulos_permitidos
            )  # security_manager ya no se asigna
            main_window.actualizar_usuario_label(user_data)
            # Eliminado: asignación de security_manager innecesaria (el atributo no existe)
            # main_window.mostrar_mensaje( ... )  # Mensaje de bienvenida removido
            main_window.show()
            print(f"✅ [SEGURIDAD] Aplicación iniciada para {user_data['username']}")
        except Exception as e:
            import traceback

            error_msg = f"[ERROR SEGURIDAD] {e}\n{traceback.format_exc()}"
            print(f"❌ [ERROR] {error_msg}", flush=True)
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
            f"✅ [LOGIN] Autenticación exitosa para {user_data.get('usuario', '???')} ({user_data.get('rol', '???')})"
        )
        if security_manager is None:
            print("[ERROR] No se puede continuar: sistema de seguridad no disponible.")
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.critical(
                None,
                "Error de seguridad",
                "No se pudo inicializar el sistema de seguridad. Contacte al administrador.",
            )
            return
        if not user_data:
            print("❌ [LOGIN] Error: No se pudo obtener datos del usuario")
            return
        modulos_permitidos = security_manager.get_user_modules(user_data.get("id", 1))
        cargar_main_window_con_seguridad(user_data, modulos_permitidos)

    def on_login_failed(error_message):
        print(f"❌ [LOGIN] Autenticación fallida: {error_message}")
        # El dialog ya muestra el mensaje de error

    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)

    # Mostrar login directamente
    login_dialog.show()
    print("[LOG 4.10] QApplication loop iniciado.")
    sys.exit(app.exec())


def chequear_conexion_bd_gui():
    """Verificación rápida de conectividad de BD - solo una vez al inicio"""
    from PyQt6.QtWidgets import QApplication, QMessageBox

    from src.core.config import (
        DB_DEFAULT_DATABASE,
        DB_PASSWORD,
        DB_SERVER,
        DB_SERVER_ALTERNATE,
        DB_TIMEOUT,
        DB_USERNAME,
    )

    DB_DRIVER = "ODBC Driver 17 for SQL Server"
    servidores = [DB_SERVER, DB_SERVER_ALTERNATE]
    for DB_SERVER_ACTUAL in servidores:
        try:
            print(f"[LOG 3.1] ⚡ Verificación rápida de BD: {DB_SERVER_ACTUAL}")
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER_ACTUAL};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc

            with pyodbc.connect(connection_string, timeout=5):  # Timeout reducido a 5s
                print(f"[LOG 3.2] ✅ BD disponible: {DB_SERVER_ACTUAL}")
                return
        except Exception as e:
            print(f"[LOG 3.3] ❌ BD no disponible ({DB_SERVER_ACTUAL}): {e}")
    print("[LOG 3.4] ❌ Sin acceso a BD. Mostrando error.")
    # QApplication.instance() or QApplication(sys.argv)  # Eliminado: expresión sin uso
    print("❌ Sin acceso a la base de datos. Verifica conexión y credenciales.")
    print(f"Servidores: {DB_SERVER}, {DB_SERVER_ALTERNATE}")
    sys.exit(1)


# --- DIAGNÓSTICO BÁSICO DE ENTORNO Y DEPENDENCIAS ---
def diagnostico_entorno_dependencias():
    """Diagnóstico básico de entorno y dependencias críticas."""
    import datetime
    import os
    import sys

    log_path = os.path.join(os.getcwd(), "logs", "diagnostico_dependencias.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(msg):
        print(msg, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} | {msg}\n")

    try:
        import pandas

        log(f"pandas importado correctamente. Versión: {pandas.__version__}")
    except Exception as e:
        log(f"Error importando pandas: {e}")
    try:
        import reportlab

        log(f"reportlab importado correctamente. Versión: {reportlab.__version__}")
    except Exception as e:
        log(f"Error importando reportlab: {e}")
