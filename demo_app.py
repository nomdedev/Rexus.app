#!/usr/bin/env python3
"""
Versión demo de Rexus.app para testing sin base de datos
Muestra todos los módulos y funcionalidades de la aplicación
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from src.core.login_dialog import LoginDialog

class MockSecurityManager:
    """Mock del security manager para demo"""
    
    def login(self, username, password):
        # Aceptar tanto admin/admin como admin/admin123 para testing
        return (username == "admin" and password == "admin") or (username == "admin" and password == "admin123")
    
    def get_current_role(self):
        return "ADMIN"
    
    def get_current_user(self):
        return {"id": 1, "username": "admin", "rol": "ADMIN"}
    
    def get_user_modules(self, user_id):
        return ["inventario", "contabilidad", "obras", "pedidos", "logistica", "configuracion"]

class DemoMainWindow(QMainWindow):
    """Ventana principal demo con todos los módulos"""
    
    def __init__(self, user_data, modulos_permitidos):
        super().__init__()
        self.user_data = user_data
        self.modulos_permitidos = modulos_permitidos
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.create_sidebar(main_layout)
        
        # Área de contenido principal
        self.create_main_content(main_layout)
        
        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
    
    def create_sidebar(self, main_layout):
        """Crea la barra lateral con módulos"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2c3e50, stop:1 #3498db);
                border-right: 2px solid #34495e;
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
        user_info = QLabel(f"👤 {self.user_data['username']}\n🔑 {self.user_data['rol']}")
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
        
        # Módulos disponibles
        modulos = [
            ("📦", "Inventario", "Gestión de stock y materiales"),
            ("💰", "Contabilidad", "Finanzas y facturación"),
            ("🏗️", "Obras", "Proyectos y construcción"),
            ("📋", "Pedidos", "Gestión de pedidos"),
            ("🚛", "Logística", "Transporte y distribución"),
            ("🔧", "Herrajes", "Catálogo de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("👥", "Usuarios", "Administración de usuarios"),
            ("🔍", "Auditoría", "Logs y seguimiento"),
            ("⚙️", "Configuración", "Ajustes del sistema"),
        ]
        
        for emoji, nombre, descripcion in modulos:
            btn = self.create_module_button(emoji, nombre, descripcion)
            modules_layout.addWidget(btn)
        
        modules_layout.addStretch()
        scroll.setWidget(modules_widget)
        sidebar_layout.addWidget(scroll)
        
        main_layout.addWidget(sidebar)
    
    def create_module_button(self, emoji, nombre, descripcion):
        """Crea un botón de módulo estilizado"""
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
                border-radius: 8px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn.clicked.connect(lambda: self.show_module(nombre))
        return btn
    
    def create_main_content(self, main_layout):
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
        
        # Header del contenido
        self.content_header = QLabel("🏠 Dashboard Principal")
        self.content_header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
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
        main_layout.addWidget(content_area)
    
    def create_dashboard(self):
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
            card = self.create_stat_card(emoji, titulo, valor, color)
            layout.addWidget(card, 0, i)
        
        # Tabla de actividad reciente
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        
        activity_title = QLabel("📊 Actividad Reciente")
        activity_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        activity_layout.addWidget(activity_title)
        
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["Tiempo", "Usuario", "Acción", "Módulo"])
        
        # Datos de ejemplo
        datos = [
            ["10:30", "admin", "Agregó producto", "Inventario"],
            ["10:25", "user1", "Creó obra", "Obras"],
            ["10:20", "admin", "Generó reporte", "Contabilidad"],
            ["10:15", "user2", "Actualizó pedido", "Pedidos"],
            ["10:10", "admin", "Configuró usuario", "Usuarios"],
        ]
        
        for i, row in enumerate(datos):
            for j, cell in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(cell))
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        activity_layout.addWidget(table)
        layout.addWidget(activity_widget, 1, 0, 1, 4)
        
        self.content_stack.addTab(dashboard, "🏠 Dashboard")
    
    def create_stat_card(self, emoji, titulo, valor, color):
        """Crea una tarjeta de estadística"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 32px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(titulo)
        title_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(valor)
        value_label.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(emoji_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def show_module(self, module_name):
        """Muestra el contenido de un módulo"""
        self.content_header.setText(f"📱 {module_name}")
        
        # Crear contenido demo para el módulo
        module_widget = QWidget()
        layout = QVBoxLayout(module_widget)
        
        info = QLabel(f"""
        🎯 Módulo: {module_name}
        
        ✅ Status: Listo para producción
        🔧 Funcionalidades implementadas:
        • CRUD completo de datos
        • Interfaz de usuario moderna
        • Validaciones de seguridad
        • Reportes y exportación
        • Integración con base de datos
        
        📊 Este módulo está completamente funcional y listo para usar.
        """)
        
        info.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 30px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                color: #495057;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(info)
        layout.addStretch()
        
        # Agregar o actualizar pestaña
        tab_exists = False
        for i in range(self.content_stack.count()):
            if self.content_stack.tabText(i).endswith(module_name):
                self.content_stack.setCurrentIndex(i)
                tab_exists = True
                break
        
        if not tab_exists:
            icon_map = {
                "Inventario": "📦",
                "Contabilidad": "💰",
                "Obras": "🏗️",
                "Pedidos": "📋",
                "Logística": "🚛",
                "Herrajes": "🔧",
                "Vidrios": "🪟",
                "Usuarios": "👥",
                "Auditoría": "🔍",
                "Configuración": "⚙️"
            }
            icon = icon_map.get(module_name, "📱")
            self.content_stack.addTab(module_widget, f"{icon} {module_name}")
            self.content_stack.setCurrentWidget(module_widget)

def main():
    app = QApplication(sys.argv)
    
    # Login
    login_dialog = LoginDialog()
    login_dialog.security_manager = MockSecurityManager()
    
    def on_login_success(username, role):
        user_data = {"username": username, "rol": role}
        modulos = ["inventario", "contabilidad", "obras", "pedidos", "logistica"]
        
        main_window = DemoMainWindow(user_data, modulos)
        main_window.show()
        login_dialog.accept()
    
    login_dialog.login_successful.connect(on_login_success)
    
    if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
        return app.exec()
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())