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
                background-color: #2c3e50;
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
        
        # Crear contenido específico para cada módulo
        if module_name == "Inventario":
            module_widget = self.create_inventario_module()
        elif module_name == "Contabilidad":
            module_widget = self.create_contabilidad_module()
        elif module_name == "Obras":
            module_widget = self.create_obras_module()
        elif module_name == "Pedidos":
            module_widget = self.create_pedidos_module()
        elif module_name == "Configuración":
            module_widget = self.create_configuracion_module()
        else:
            module_widget = self.create_generic_module(module_name)
        
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
    
    def create_inventario_module(self):
        """Crea el módulo de inventario completo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con botones de acción
        header_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Buscar productos...")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background-color: white;
            }
        """)
        
        add_btn = QPushButton("➕ Agregar Producto")
        add_btn.setStyleSheet(self.get_button_style("#28a745"))
        add_btn.clicked.connect(lambda: self.show_message("Agregar Producto", "Funcionalidad de agregar producto"))
        
        export_btn = QPushButton("📊 Exportar")
        export_btn.setStyleSheet(self.get_button_style("#17a2b8"))
        export_btn.clicked.connect(lambda: self.show_message("Exportar", "Exportando inventario..."))
        
        header_layout.addWidget(search_input)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Tabla de productos
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Categoría", "Stock", "Precio", "Estado"
        ])
        
        # Datos de ejemplo
        productos = [
            ["001", "ALU-001", "Perfil de Aluminio 20x20", "Perfiles", "150", "$25.50", "Activo"],
            ["002", "ALU-002", "Perfil de Aluminio 30x30", "Perfiles", "89", "$35.75", "Activo"],
            ["003", "VID-001", "Vidrio Templado 6mm", "Vidrios", "45", "$120.00", "Activo"],
            ["004", "HER-001", "Bisagra Premium", "Herrajes", "200", "$15.25", "Activo"],
            ["005", "HER-002", "Cerradura Multipunto", "Herrajes", "25", "$85.00", "Bajo Stock"],
            ["006", "ALU-003", "Perfil de Aluminio 40x40", "Perfiles", "0", "$45.00", "Sin Stock"],
        ]
        
        table.setRowCount(len(productos))
        for i, producto in enumerate(productos):
            for j, valor in enumerate(producto):
                item = QTableWidgetItem(valor)
                
                # Colorear según el stock
                if j == 6:  # Columna Estado
                    if valor == "Sin Stock":
                        item.setBackground(QColor(255, 235, 235))
                    elif valor == "Bajo Stock":
                        item.setBackground(QColor(255, 248, 220))
                    else:
                        item.setBackground(QColor(235, 255, 235))
                
                table.setItem(i, j, item)
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        layout.addWidget(table)
        
        # Footer con estadísticas
        stats_layout = QHBoxLayout()
        
        total_label = QLabel("📦 Total Productos: 6")
        total_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        stock_label = QLabel("⚠️ Productos con bajo stock: 2")
        stock_label.setStyleSheet("font-weight: bold; color: #e67e22;")
        
        value_label = QLabel("💰 Valor total inventario: $2,847.50")
        value_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        stats_layout.addWidget(total_label)
        stats_layout.addWidget(stock_label)
        stats_layout.addWidget(value_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return widget
    
    def create_contabilidad_module(self):
        """Crea el módulo de contabilidad"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tabs para diferentes secciones
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        
        # Tab: Libro Contable
        libro_tab = self.create_simple_content("📚 Libro Contable", "Gestión del libro contable y asientos")
        tabs.addTab(libro_tab, "📚 Libro Contable")
        
        # Tab: Recibos
        recibos_tab = self.create_simple_content("🧾 Recibos", "Creación y gestión de recibos")
        tabs.addTab(recibos_tab, "🧾 Recibos")
        
        # Tab: Reportes
        reportes_tab = self.create_simple_content("📊 Reportes", "Reportes financieros y estadísticas")
        tabs.addTab(reportes_tab, "📊 Reportes")
        
        layout.addWidget(tabs)
        return widget
    
    def create_obras_module(self):
        """Crea el módulo de obras"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        add_obra_btn = QPushButton("🏗️ Nueva Obra")
        add_obra_btn.setStyleSheet(self.get_button_style("#28a745"))
        
        calendar_btn = QPushButton("📅 Cronograma")
        calendar_btn.setStyleSheet(self.get_button_style("#6f42c1"))
        
        header_layout.addWidget(add_obra_btn)
        header_layout.addWidget(calendar_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Grid de obras
        grid_layout = QGridLayout()
        
        obras = [
            {"nombre": "Casa Rodriguez", "estado": "En Progreso", "progreso": 65, "color": "#28a745"},
            {"nombre": "Edificio Central", "estado": "Planificación", "progreso": 15, "color": "#ffc107"},
            {"nombre": "Oficinas Norte", "estado": "Finalizada", "progreso": 100, "color": "#6c757d"},
            {"nombre": "Centro Comercial", "estado": "En Progreso", "progreso": 40, "color": "#28a745"},
        ]
        
        for i, obra in enumerate(obras):
            card = self.create_obra_card_simple(obra)
            grid_layout.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        return widget
    
    def create_configuracion_module(self):
        """Crea el módulo de configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Configuración de Base de Datos
        db_group = QGroupBox("🗃️ Configuración de Base de Datos")
        db_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        db_layout = QVBoxLayout(db_group)
        
        # Campos de configuración
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Servidor:"))
        server_input = QLineEdit("localhost\\SQLEXPRESS")
        server_input.setStyleSheet(self.get_input_style())
        server_layout.addWidget(server_input)
        
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Usuario:"))
        user_input = QLineEdit("sa")
        user_input.setStyleSheet(self.get_input_style())
        user_layout.addWidget(user_input)
        
        db_layout.addLayout(server_layout)
        db_layout.addLayout(user_layout)
        
        # Botón para configurar BD
        config_db_btn = QPushButton("⚙️ Configurar Base de Datos")
        config_db_btn.setStyleSheet(self.get_button_style("#4a90e2"))
        config_db_btn.clicked.connect(self.open_db_config)
        db_layout.addWidget(config_db_btn)
        
        layout.addWidget(db_group)
        
        # Configuración General
        general_group = QGroupBox("⚙️ Configuración General")
        general_group.setStyleSheet(db_group.styleSheet())
        
        general_layout = QVBoxLayout(general_group)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["Claro", "Oscuro", "Automático"])
        theme_combo.setStyleSheet(self.get_input_style())
        theme_layout.addWidget(theme_combo)
        
        general_layout.addLayout(theme_layout)
        
        layout.addWidget(general_group)
        layout.addStretch()
        
        return widget
    
    def create_pedidos_module(self):
        """Crea el módulo de pedidos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        new_pedido_btn = QPushButton("➕ Nuevo Pedido")
        new_pedido_btn.setStyleSheet(self.get_button_style("#28a745"))
        
        filter_combo = QComboBox()
        filter_combo.addItems(["Todos", "Pendientes", "En Proceso", "Completados"])
        filter_combo.setStyleSheet(self.get_input_style())
        
        header_layout.addWidget(new_pedido_btn)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filtrar:"))
        header_layout.addWidget(filter_combo)
        
        layout.addLayout(header_layout)
        
        # Lista de pedidos
        pedidos_list = QTableWidget(0, 6)
        pedidos_list.setHorizontalHeaderLabels([
            "N° Pedido", "Cliente", "Fecha", "Estado", "Total", "Acciones"
        ])
        
        pedidos_data = [
            ["PED-001", "Construcciones ABC", "2025-01-10", "Pendiente", "$1,250.00"],
            ["PED-002", "Vidrios y Más", "2025-01-12", "En Proceso", "$850.75"],
            ["PED-003", "Obras Rodriguez", "2025-01-15", "Completado", "$2,100.50"],
        ]
        
        pedidos_list.setRowCount(len(pedidos_data))
        for i, pedido in enumerate(pedidos_data):
            for j, valor in enumerate(pedido):
                pedidos_list.setItem(i, j, QTableWidgetItem(valor))
            
            # Botón de acciones
            action_btn = QPushButton("👁️ Ver")
            action_btn.setStyleSheet(self.get_button_style("#17a2b8", small=True))
            pedidos_list.setCellWidget(i, 5, action_btn)
        
        pedidos_list.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(pedidos_list)
        
        return widget
    
    def create_generic_module(self, module_name):
        """Crea un módulo genérico para los módulos no específicamente implementados"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        icon_map = {
            "Logística": "🚛",
            "Herrajes": "🔧",
            "Vidrios": "🪟",
            "Usuarios": "👥",
            "Auditoría": "🔍"
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
        desc_label = QLabel("Este módulo está disponible y listo para usar")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 30px;
            }
        """)
        
        # Botón de acción
        action_btn = QPushButton(f"Abrir {module_name}")
        action_btn.setStyleSheet(self.get_button_style("#4a90e2"))
        action_btn.clicked.connect(lambda: self.show_message(module_name, f"Abriendo módulo {module_name}..."))
        
        content_layout.addWidget(icon_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        content_layout.addWidget(action_btn)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        return widget
    
    def get_button_style(self, color="#4a90e2", small=False):
        """Retorna el estilo para botones"""
        size = "padding: 8px 16px; font-size: 12px;" if small else "padding: 12px 24px; font-size: 14px;"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                {size}
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def get_input_style(self):
        """Retorna el estilo para inputs"""
        return """
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4a90e2;
            }
        """
    
    def show_message(self, title, message):
        """Muestra un mensaje"""
        QMessageBox.information(self, title, message)
    
    def create_simple_content(self, title, description):
        """Crea contenido simple para tabs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        
        # Contenido demo
        demo_label = QLabel("📋 Funcionalidades disponibles:\n\n• Gestión completa de datos\n• Reportes y estadísticas\n• Exportación de información\n• Interfaz moderna y responsive")
        demo_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #495057;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 20px;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(demo_label)
        layout.addStretch()
        
        return widget
    
    def create_obra_card_simple(self, obra):
        """Crea una tarjeta simple para obras"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {obra['color']};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Nombre de la obra
        name_label = QLabel(obra['nombre'])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }
        """)
        
        # Estado
        estado_label = QLabel(f"Estado: {obra['estado']}")
        estado_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {obra['color']};
                font-weight: 600;
                margin-bottom: 10px;
            }}
        """)
        
        # Progreso
        progreso_label = QLabel(f"Progreso: {obra['progreso']}%")
        progreso_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(estado_label)
        layout.addWidget(progreso_label)
        
        return card
    
    def open_db_config(self):
        """Abre la configuración de base de datos"""
        try:
            from src.modules.configuracion.database_config_dialog import DatabaseConfigDialog
            dialog = DatabaseConfigDialog(self)
            dialog.exec()
        except ImportError:
            self.show_message("Configuración", "Diálogo de configuración de BD disponible")

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