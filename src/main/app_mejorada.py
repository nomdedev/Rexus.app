#!/usr/bin/env python3
"""
Rexus.app - Sistema de Gestión Integral (Versión Mejorada)

Aplicación principal con sidebar animado y UI mejorada
"""

import os
import platform
import sys
from typing import Dict, Optional, Any

# PyQt6 Core Imports
from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QTabWidget,
    QGridLayout, QGraphicsDropShadowEffect, QSplitter
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QColor, QFont

# Core Application Imports
from src.core.login_dialog import LoginDialog
from src.core.security import initialize_security_manager


class AnimatedSidebar(QFrame):
    """Sidebar animado que se puede expandir/contraer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.expanded = True
        self.animation_duration = 300
        self.collapsed_width = 60
        self.expanded_width = 280
        
        self.init_ui()
        self.setup_animation()
    
    def init_ui(self):
        """Inicializa la interfaz del sidebar"""
        self.setFixedWidth(self.expanded_width)
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
        
        # Header con botón de colapso
        self.create_header()
        
        # Usuario actual
        self.create_user_info()
        
        # Scroll area para módulos
        self.create_modules_area()
    
    def create_header(self):
        """Crea el header con botón de colapso"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Título de la aplicación
        self.app_title = QLabel("Rexus.app")
        self.app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
        """)
        header_layout.addWidget(self.app_title)
        
        # Botón de colapso
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.collapse_btn)
        
        self.main_layout.addWidget(header_frame)
    
    def create_user_info(self):
        """Crea la información del usuario"""
        user_data = getattr(self.parent_window, 'user_data', {'username': 'Usuario', 'rol': 'Usuario'})
        
        self.user_info = QLabel(f"👤 {user_data['username']}\n🔑 {user_data['rol']}")
        self.user_info.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                padding: 15px 20px;
                background-color: rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.main_layout.addWidget(self.user_info)
    
    def create_modules_area(self):
        """Crea el área de módulos"""
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.modules_widget = QWidget()
        self.modules_layout = QVBoxLayout(self.modules_widget)
        self.modules_layout.setSpacing(5)
        self.modules_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear botones de módulos
        self.module_buttons = []
        modulos = [
            ("🏗️", "Obras", "Gestión de proyectos y construcción"),
            ("📦", "Inventario", "Gestión de inventario y stock"),
            ("🔧", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("📋", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("💼", "Administración", "Gestión administrativa y financiera"),
            ("🛠️", "Mantenimiento", "Gestión de mantenimiento"),
            ("🚛", "Logística", "Gestión logística y entregas"),
            ("🔍", "Auditoría", "Auditoría y trazabilidad"),
            ("👥", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]
        
        for emoji, nombre, descripcion in modulos:
            btn = self.create_module_button(emoji, nombre, descripcion)
            self.module_buttons.append(btn)
            self.modules_layout.addWidget(btn)
        
        self.modules_layout.addStretch()
        self.scroll.setWidget(self.modules_widget)
        self.main_layout.addWidget(self.scroll)
    
    def create_module_button(self, emoji: str, nombre: str, descripcion: str) -> QPushButton:
        """Crea un botón de módulo"""
        btn = QPushButton()
        btn.emoji = emoji
        btn.nombre = nombre
        btn.descripcion = descripcion
        
        self.update_button_text(btn)
        
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                color: #ecf0f1;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
                border-radius: 6px;
                margin: 3px 8px;
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
        
        btn.clicked.connect(lambda checked: self.parent_window.show_module(nombre))
        return btn
    
    def update_button_text(self, btn):
        """Actualiza el texto del botón según el estado del sidebar"""
        if self.expanded:
            btn.setText(f"{btn.emoji}  {btn.nombre}")
        else:
            btn.setText(btn.emoji)
        btn.setToolTip(btn.descripcion)
    
    def setup_animation(self):
        """Configura la animación del sidebar"""
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self.on_animation_finished)
    
    def toggle_sidebar(self):
        """Alterna entre expandido y contraído"""
        if self.expanded:
            self.collapse_sidebar()
        else:
            self.expand_sidebar()
    
    def collapse_sidebar(self):
        """Contrae el sidebar"""
        self.animation.setStartValue(self.expanded_width)
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()
        self.expanded = False
        self.collapse_btn.setText("▶")
        
        # Ocultar textos
        self.app_title.setVisible(False)
        self.user_info.setVisible(False)
        
        # Actualizar botones
        for btn in self.module_buttons:
            self.update_button_text(btn)
    
    def expand_sidebar(self):
        """Expande el sidebar"""
        self.animation.setStartValue(self.collapsed_width)
        self.animation.setEndValue(self.expanded_width)
        self.animation.start()
        self.expanded = True
        self.collapse_btn.setText("◀")
        
        # Mostrar textos
        self.app_title.setVisible(True)
        self.user_info.setVisible(True)
        
        # Actualizar botones
        for btn in self.module_buttons:
            self.update_button_text(btn)
    
    def on_animation_finished(self):
        """Callback cuando termina la animación"""
        self.setFixedWidth(self.width())


class ImprovedMainWindow(QMainWindow):
    """Ventana principal mejorada con sidebar animado"""
    
    def __init__(self, user_data: Dict[str, Any], modulos_permitidos: list):
        super().__init__()
        self.user_data = user_data
        self.modulos_permitidos = modulos_permitidos
        self.security_manager = None
        self.content_stack = QTabWidget()
        self.content_header = QLabel()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal con splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear splitter para sidebar y contenido
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar animado
        self.sidebar = AnimatedSidebar(self)
        splitter.addWidget(self.sidebar)
        
        # Área de contenido
        self.content_area = self.create_content_area()
        splitter.addWidget(self.content_area)
        
        # Configurar splitter
        splitter.setSizes([280, 1120])  # Sidebar: 280px, Contenido: resto
        splitter.setCollapsible(0, False)  # Sidebar no completamente colapsible
        
        main_layout.addWidget(splitter)
        
        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
    
    def create_content_area(self):
        """Crea el área de contenido principal"""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 0px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 20, 30, 30)  # Reducido el margen superior
        
        # Header del contenido (más pequeño)
        self.content_header = QLabel("🏠 Dashboard Principal")
        self.content_header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                max-height: 40px;
            }
        """)
        content_layout.addWidget(self.content_header)
        
        # Área de contenido dinámico
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
                padding: 8px 16px;
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
        
        return content_frame
    
    def create_dashboard(self):
        """Crea el dashboard principal"""
        dashboard = QWidget()
        layout = QGridLayout(dashboard)
        layout.setSpacing(20)
        
        # Cards de estadísticas más pequeños
        stats = [
            ("📦", "Productos", "1,234", "#3498db"),
            ("💰", "Facturación", "$45,678", "#2ecc71"),
            ("🏗️", "Obras", "23", "#e74c3c"),
            ("📋", "Pedidos", "56", "#f39c12"),
        ]
        
        for i, (emoji, titulo, valor, color) in enumerate(stats):
            card = self.create_stat_card(emoji, titulo, valor, color)
            layout.addWidget(card, 0, i)
        
        # Información de bienvenida más compacta
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        
        welcome_title = QLabel("🎉 ¡Bienvenido a Rexus.app!")
        welcome_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_info = QLabel(f"""
        Usuario: {self.user_data.get('username', 'N/A')} | 
        Rol: {self.user_data.get('rol', 'N/A')} | 
        Módulos: {len(self.modulos_permitidos)}
        
        ✅ Sistema funcionando | 📱 Módulos listos | 🔧 BD configurada
        """)
        
        welcome_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                color: #495057;
            }
        """)
        welcome_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_info)
        
        layout.addWidget(welcome_widget, 1, 0, 1, 4)
        
        self.content_stack.addTab(dashboard, "🏠 Dashboard")
    
    def create_stat_card(self, emoji: str, titulo: str, valor: str, color: str) -> QFrame:
        """Crea una tarjeta de estadística más pequeña"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 2px;
                min-height: 80px;
                max-height: 80px;
            }}
        """)
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        
        # Emoji
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 24px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        title_label = QLabel(titulo)
        title_label.setStyleSheet("font-size: 10px; color: #7f8c8d; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valor
        value_label = QLabel(valor)
        value_label.setStyleSheet(f"font-size: 16px; color: {color}; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(emoji_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def show_module(self, module_name: str) -> None:
        """Muestra el contenido de un módulo"""
        try:
            # Actualizar header más pequeño
            self.content_header.setText(f"📱 {module_name}")
            
            # Factory pattern para creación de módulos
            module_widget = self.create_module_widget(module_name)
            
            # Agregar o actualizar pestaña
            tab_exists = False
            for i in range(self.content_stack.count()):
                if self.content_stack.tabText(i).endswith(module_name):
                    self.content_stack.setCurrentIndex(i)
                    tab_exists = True
                    break
            
            if not tab_exists:
                icon_map = {
                    "Inventario": "📦", "Contabilidad": "💰", "Obras": "🏗️",
                    "Pedidos": "📋", "Logística": "🚛", "Herrajes": "🔧",
                    "Vidrios": "🪟", "Usuarios": "👥", "Auditoría": "🔍",
                    "Configuración": "⚙️", "Compras": "🛒", "Mantenimiento": "🛠️",
                    "Administración": "💼"
                }
                icon = icon_map.get(module_name, "📱")
                self.content_stack.addTab(module_widget, f"{icon} {module_name}")
                self.content_stack.setCurrentWidget(module_widget)
                
        except Exception as e:
            print(f"Error cargando módulo {module_name}: {e}")
            self.mostrar_mensaje(f"Error al cargar {module_name}: {str(e)}", "error")
    
    def create_module_widget(self, module_name: str) -> QWidget:
        """Factory method para crear widgets de módulos"""
        # Usar el mismo factory del app original pero con herrajes mejorado
        if module_name == "Herrajes":
            try:
                from src.modules.herrajes.view_completa import HerrajesCompletaView
                return HerrajesCompletaView()
            except Exception as e:
                print(f"Error creando herrajes completo: {e}")
                return self.create_fallback_module(module_name)
        
        # Para otros módulos, usar factory original
        module_factory = {
            "Inventario": self.create_inventario_module,
            "Contabilidad": self.create_contabilidad_module,
            "Obras": self.create_obras_module,
            "Configuración": self.create_configuracion_module,
            "Vidrios": self.create_vidrios_module,
            "Pedidos": self.create_pedidos_module,
            "Logística": self.create_logistica_module,
            "Usuarios": self.create_usuarios_module,
            "Auditoría": self.create_auditoria_module,
            "Compras": self.create_compras_module,
            "Mantenimiento": self.create_mantenimiento_module,
            "Administración": self.create_administracion_module,
        }
        
        creation_method = module_factory.get(module_name)
        if creation_method:
            return creation_method()
        else:
            return self.create_fallback_module(module_name)
    
    def create_inventario_module(self) -> QWidget:
        """Crea el módulo de inventario"""
        try:
            from src.modules.inventario.view import InventarioView
            from src.modules.inventario.model import InventarioModel
            from src.modules.inventario.controller import InventarioController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = InventarioModel(db_connection)
            view = InventarioView()
            controller = InventarioController(model, view, db_connection)
            
            view.set_controller(controller)
            return view
            
        except Exception as e:
            print(f"Error creando inventario: {e}")
            return self.create_fallback_module("Inventario")
    
    def create_obras_module(self) -> QWidget:
        """Crea el módulo de obras"""
        try:
            from src.modules.obras.view import ObrasView
            from src.modules.obras.model import ObrasModel
            from src.modules.obras.controller import ObrasController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = ObrasModel(db_connection)
            view = ObrasView()
            controller = ObrasController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando obras: {e}")
            return self.create_fallback_module("Obras")
    
    def create_usuarios_module(self) -> QWidget:
        """Crea el módulo de usuarios"""
        try:
            from src.modules.usuarios.view_admin import UsersAdminView
            return UsersAdminView()
        except Exception as e:
            print(f"Error creando usuarios: {e}")
            return self.create_fallback_module("Usuarios")
    
    def create_configuracion_module(self) -> QWidget:
        """Crea el módulo de configuración"""
        try:
            from src.modules.configuracion.view import ConfiguracionView
            from src.modules.configuracion.model import ConfiguracionModel
            from src.modules.configuracion.controller import ConfiguracionController
            
            model = ConfiguracionModel()
            view = ConfiguracionView()
            controller = ConfiguracionController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando configuración: {e}")
            return self.create_fallback_module("Configuración")
    
    def create_administracion_module(self) -> QWidget:
        """Crea el módulo de administración"""
        try:
            from src.modules.administracion.view_completa import AdministracionCompletaView
            return AdministracionCompletaView()
        except Exception as e:
            print(f"Error creando administración completa: {e}")
            # Fallback a la versión básica
            try:
                from src.modules.administracion.view import AdministracionView
                from src.modules.administracion.model import AdministracionModel
                from src.modules.administracion.controller import AdministracionController
                from src.core.database import InventarioDatabaseConnection
                
                try:
                    db_connection = InventarioDatabaseConnection()
                except Exception as e:
                    print(f"Error BD: {e}, usando datos demo")
                    db_connection = None
                
                model = AdministracionModel(db_connection)
                view = AdministracionView()
                controller = AdministracionController(model, view)
                
                return view
            except Exception as e:
                print(f"Error creando administración: {e}")
                return self.create_fallback_module("Administración")
    
    def create_logistica_module(self) -> QWidget:
        """Crea el módulo de logística"""
        try:
            from src.modules.logistica.view import LogisticaView
            from src.modules.logistica.model import LogisticaModel
            from src.modules.logistica.controller import LogisticaController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = LogisticaModel(db_connection)
            view = LogisticaView()
            controller = LogisticaController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando logística: {e}")
            return self.create_fallback_module("Logística")
    
    def create_mantenimiento_module(self) -> QWidget:
        """Crea el módulo de mantenimiento"""
        try:
            from src.modules.mantenimiento.view_completa import MantenimientoCompletaView
            return MantenimientoCompletaView()
        except Exception as e:
            print(f"Error creando mantenimiento completo: {e}")
            # Fallback a la versión básica
            try:
                from src.modules.mantenimiento.view import MantenimientoView
                from src.modules.mantenimiento.model import MantenimientoModel
                from src.modules.mantenimiento.controller import MantenimientoController
                from src.core.database import InventarioDatabaseConnection
                
                try:
                    db_connection = InventarioDatabaseConnection()
                except Exception as e:
                    print(f"Error BD: {e}, usando datos demo")
                    db_connection = None
                
                model = MantenimientoModel(db_connection)
                view = MantenimientoView()
                controller = MantenimientoController(model, view)
                
                return view
            except Exception as e:
                print(f"Error creando mantenimiento: {e}")
                return self.create_fallback_module("Mantenimiento")
    
    def create_compras_module(self) -> QWidget:
        """Crea el módulo de compras"""
        try:
            from src.modules.compras.view import ComprasView
            from src.modules.compras.model import ComprasModel
            from src.modules.compras.controller import ComprasController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = ComprasModel(db_connection)
            view = ComprasView()
            controller = ComprasController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando compras: {e}")
            return self.create_fallback_module("Compras")
    
    def create_contabilidad_module(self) -> QWidget:
        """Crea el módulo de contabilidad"""
        try:
            from src.modules.contabilidad.view import ContabilidadView
            from src.modules.contabilidad.model import ContabilidadModel
            from src.modules.contabilidad.controller import ContabilidadController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = ContabilidadModel(db_connection)
            view = ContabilidadView()
            controller = ContabilidadController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando contabilidad: {e}")
            return self.create_fallback_module("Contabilidad")
    
    def create_vidrios_module(self) -> QWidget:
        """Crea el módulo de vidrios"""
        try:
            from src.modules.vidrios.view import VidriosView
            from src.modules.vidrios.model import VidriosModel
            from src.modules.vidrios.controller import VidriosController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = VidriosModel(db_connection)
            view = VidriosView()
            controller = VidriosController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando vidrios: {e}")
            return self.create_fallback_module("Vidrios")
    
    def create_pedidos_module(self) -> QWidget:
        """Crea el módulo de pedidos"""
        try:
            from src.modules.pedidos.view import PedidosView
            from src.modules.pedidos.model import PedidosModel
            from src.modules.pedidos.controller import PedidosController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = PedidosModel(db_connection)
            view = PedidosView()
            controller = PedidosController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando pedidos: {e}")
            return self.create_fallback_module("Pedidos")
    
    def create_auditoria_module(self) -> QWidget:
        """Crea el módulo de auditoría"""
        try:
            from src.modules.auditoria.view import AuditoriaView
            from src.modules.auditoria.model import AuditoriaModel
            from src.modules.auditoria.controller import AuditoriaController
            from src.core.database import InventarioDatabaseConnection
            
            try:
                db_connection = InventarioDatabaseConnection()
            except Exception as e:
                print(f"Error BD: {e}, usando datos demo")
                db_connection = None
            
            model = AuditoriaModel(db_connection)
            view = AuditoriaView()
            controller = AuditoriaController(model, view)
            
            return view
            
        except Exception as e:
            print(f"Error creando auditoría: {e}")
            return self.create_fallback_module("Auditoría")
    
    def create_fallback_module(self, module_name: str) -> QWidget:
        """Crea un módulo de fallback"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        icon_map = {
            "Vidrios": "🪟", "Herrajes": "🔧", "Pedidos": "📋",
            "Logística": "🚛", "Usuarios": "👥", "Auditoría": "🔍",
            "Compras": "🛒", "Mantenimiento": "🛠️", "Administración": "💼"
        }
        
        icon = icon_map.get(module_name, "📱")
        
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("QLabel { font-size: 72px; margin-bottom: 20px; }")
        
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
    
    def actualizar_usuario_label(self, user_data):
        """Actualiza la información del usuario"""
        self.user_data = user_data
        if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'user_info'):
            self.sidebar.user_info.setText(f"👤 {user_data['username']}\n🔑 {user_data['rol']}")


def main():
    """Función principal de la aplicación mejorada"""
    print("[APP MEJORADA] Iniciando QApplication...")
    app = QApplication(sys.argv)
    
    # Crear dialog de login
    login_dialog = LoginDialog()
    
    def on_login_success(username, role):
        print(f"[LOGIN] Éxito: {username} ({role})")
        login_dialog.close()
        
        # Datos del usuario
        user_data = {
            'username': username,
            'rol': role,
            'id': 1
        }
        
        # Módulos según rol
        if role == 'admin':
            modulos_permitidos = ['inventario', 'obras', 'usuarios', 'configuracion', 'herrajes', 'vidrios', 'compras', 'administracion', 'logistica', 'mantenimiento', 'auditoria']
        elif role == 'supervisor':
            modulos_permitidos = ['inventario', 'obras', 'herrajes', 'vidrios', 'compras', 'administracion', 'logistica']
        else:
            modulos_permitidos = ['inventario', 'obras', 'herrajes', 'vidrios']
        
        # Crear ventana principal mejorada
        main_window = ImprovedMainWindow(user_data, modulos_permitidos)
        main_window.show()
    
    def on_login_failed(error_message):
        print(f"[LOGIN] Error: {error_message}")
    
    # Conectar señales
    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)
    
    # Mostrar login
    login_dialog.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()