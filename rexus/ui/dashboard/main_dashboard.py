# -*- coding: utf-8 -*-
"""
Dashboard Principal - Rexus.app v2.0.0

Dashboard centralizado con métricas en tiempo real de todos los módulos,
KPIs principales, gráficos interactivos y feed de actividad.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QScrollArea, QSplitter, QTabWidget, QPushButton, QProgressBar
)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

from ..templates.base_module_view import BaseModuleView
from ..components.base_components import RexusLabel, RexusFrame, RexusGroupBox
from .widgets.kpi_widget import KPIWidget
from .widgets.chart_widget import ChartWidget  
from .widgets.activity_widget import ActivityWidget


class MainDashboard(BaseModuleView):
    """Dashboard principal de Rexus.app con métricas centralizadas."""
    
    # Señales para comunicación
    modulo_solicitado = pyqtSignal(str)  # Cuando se solicita abrir un módulo
    reporte_solicitado = pyqtSignal(str)  # Cuando se solicita un reporte
    
    def __init__(self, parent=None):
        super().__init__("🏠 Dashboard Principal", parent=parent)
        
        self.datos_modulos = {}
        self.widgets_kpi = {}
        
        # Timer para actualización automática
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.actualizar_metricas)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
        
        self.setup_dashboard_ui()
        
    def setup_dashboard_ui(self):
        """Configura la interfaz del dashboard."""
        # Header del dashboard
        self.crear_header_dashboard()
        
        # Grid principal de KPIs
        self.crear_seccion_kpis()
        
        # Splitter para gráficos y actividad
        self.crear_seccion_graficos_actividad()
        
        # Sección de acceso rápido a módulos
        self.crear_seccion_acceso_rapido()
        
        # self.apply_theme()  # TODO: Implementar método de aplicación de tema
    
    def crear_header_dashboard(self):
        """Crea el header del dashboard con información general."""
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
                color: white;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Título y descripción
        left_layout = QVBoxLayout()
        
        titulo = QLabel("🏠 Dashboard Ejecutivo")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titulo.setStyleSheet("color: white; margin: 0;")
        
        descripcion = QLabel("Gestión empresarial centralizada - Rexus.app")
        descripcion.setFont(QFont("Segoe UI", 10))
        descripcion.setStyleSheet("color: rgba(255,255,255,0.8); margin: 0;")
        
        left_layout.addWidget(titulo)
        left_layout.addWidget(descripcion)
        
        # Métricas rápidas en header
        right_layout = QHBoxLayout()
        
        self.header_usuarios_online = self.crear_metric_header("👥", "0", "Usuarios Online")
        self.header_alertas = self.crear_metric_header("🔔", "0", "Alertas")
        self.header_estado_sistema = self.crear_metric_header("⚡", "OK", "Sistema")
        
        right_layout.addWidget(self.header_usuarios_online)
        right_layout.addWidget(self.header_alertas)
        right_layout.addWidget(self.header_estado_sistema)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        layout.addLayout(right_layout)
        
        self.add_to_main_content(header_frame)
    
    def crear_metric_header(self, icono, valor, label):
        """Crea una métrica para el header."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Icono y valor
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icono_lbl = QLabel(icono)
        icono_lbl.setFont(QFont("Segoe UI", 16))
        icono_lbl.setStyleSheet("color: white;")
        
        valor_lbl = QLabel(valor)
        valor_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        valor_lbl.setStyleSheet("color: white; margin-left: 5px;")
        
        top_layout.addWidget(icono_lbl)
        top_layout.addWidget(valor_lbl)
        
        # Label
        label_lbl = QLabel(label)
        label_lbl.setFont(QFont("Segoe UI", 8))
        label_lbl.setStyleSheet("color: rgba(255,255,255,0.7);")
        label_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(top_layout)
        layout.addWidget(label_lbl)
        
        # Guardar referencia al valor para actualizar
        setattr(widget, 'valor_label', valor_lbl)
        
        return widget
    
    def crear_seccion_kpis(self):
        """Crea la sección principal de KPIs."""
        kpis_frame = RexusGroupBox("📊 Métricas Principales")
        kpis_layout = QGridLayout(kpis_frame)
        kpis_layout.setSpacing(15)
        
        # KPIs por módulo - Primera fila
        self.widgets_kpi['usuarios'] = KPIWidget("👥 Usuarios", "0", "Total usuarios registrados")
        self.widgets_kpi['inventario'] = KPIWidget("📦 Inventario", "0", "Productos en stock")
        self.widgets_kpi['obras'] = KPIWidget("🏢 Obras", "0", "Obras activas")
        self.widgets_kpi['pedidos'] = KPIWidget("📋 Pedidos", "0", "Pedidos pendientes")
        
        kpis_layout.addWidget(self.widgets_kpi['usuarios'], 0, 0)
        kpis_layout.addWidget(self.widgets_kpi['inventario'], 0, 1)
        kpis_layout.addWidget(self.widgets_kpi['obras'], 0, 2)
        kpis_layout.addWidget(self.widgets_kpi['pedidos'], 0, 3)
        
        # KPIs financieros - Segunda fila
        self.widgets_kpi['ventas'] = KPIWidget("💰 Ventas", "$0", "Ventas del mes")
        self.widgets_kpi['compras'] = KPIWidget("🛒 Compras", "$0", "Compras del mes")
        self.widgets_kpi['margen'] = KPIWidget("📈 Margen", "0%", "Margen de ganancia")
        self.widgets_kpi['alertas'] = KPIWidget("⚠️ Alertas", "0", "Alertas del sistema")
        
        kpis_layout.addWidget(self.widgets_kpi['ventas'], 1, 0)
        kpis_layout.addWidget(self.widgets_kpi['compras'], 1, 1)
        kpis_layout.addWidget(self.widgets_kpi['margen'], 1, 2)
        kpis_layout.addWidget(self.widgets_kpi['alertas'], 1, 3)
        
        self.add_to_main_content(kpis_frame)
    
    def crear_seccion_graficos_actividad(self):
        """Crea la sección de gráficos y actividad."""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Gráficos
        graficos_frame = RexusGroupBox("📈 Análisis de Tendencias")
        graficos_layout = QVBoxLayout(graficos_frame)
        
        # Tabs para diferentes gráficos
        graficos_tabs = QTabWidget()
        
        # Tab 1: Ventas
        self.chart_ventas = ChartWidget("ventas")
        graficos_tabs.addTab(self.chart_ventas, "💰 Ventas")
        
        # Tab 2: Inventario
        self.chart_inventario = ChartWidget("inventario")
        graficos_tabs.addTab(self.chart_inventario, "📦 Inventario")
        
        # Tab 3: Obras
        self.chart_obras = ChartWidget("obras")
        graficos_tabs.addTab(self.chart_obras, "🏢 Obras")
        
        graficos_layout.addWidget(graficos_tabs)
        
        # Panel derecho - Actividad
        actividad_frame = RexusGroupBox("🔔 Actividad Reciente")
        actividad_layout = QVBoxLayout(actividad_frame)
        
        self.widget_actividad = ActivityWidget()
        actividad_layout.addWidget(self.widget_actividad)
        
        # Configurar splitter
        splitter.addWidget(graficos_frame)
        splitter.addWidget(actividad_frame)
        splitter.setSizes([600, 300])  # 2:1 ratio
        
        self.add_to_main_content(splitter)
    
    def crear_seccion_acceso_rapido(self):
        """Crea la sección de acceso rápido a módulos."""
        acceso_frame = RexusGroupBox("🚀 Acceso Rápido")
        acceso_layout = QGridLayout(acceso_frame)
        acceso_layout.setSpacing(10)
        
        # Botones de módulos con métricas
        modulos = [
            ("👥 Usuarios", "usuarios", "Gestionar usuarios y permisos"),
            ("📦 Inventario", "inventario", "Control de stock y productos"),
            ("🏢 Obras", "obras", "Gestión de proyectos y obras"),
            ("📋 Pedidos", "pedidos", "Gestión de pedidos de clientes"),
            ("🛒 Compras", "compras", "Órdenes de compra y proveedores"),
            ("🪟 Vidrios", "vidrios", "Gestión especializada de vidrios"),
            ("🔔 Notificaciones", "notificaciones", "Centro de notificaciones"),
            ("📊 Configuración", "configuracion", "Configuración del sistema")
        ]
        
        for i, (titulo, modulo, descripcion) in enumerate(modulos):
            btn = self.crear_boton_modulo(titulo, modulo, descripcion)
            fila = i // 4
            columna = i % 4
            acceso_layout.addWidget(btn, fila, columna)
        
        self.add_to_main_content(acceso_frame)
    
    def crear_boton_modulo(self, titulo, modulo, descripcion):
        """Crea un botón de acceso rápido a módulo."""
        btn_frame = QFrame()
        btn_frame.setFixedSize(200, 100)
        btn_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #667eea;
                background: #f8f9ff;
            }
        """)
        btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(btn_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        titulo_lbl = QLabel(titulo)
        titulo_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        titulo_lbl.setStyleSheet("color: #333; margin-bottom: 5px;")
        
        # Descripción
        desc_lbl = QLabel(descripcion)
        desc_lbl.setFont(QFont("Segoe UI", 8))
        desc_lbl.setStyleSheet("color: #666;")
        desc_lbl.setWordWrap(True)
        
        # Métrica rápida (placeholder)
        metrica_lbl = QLabel("---")
        metrica_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        metrica_lbl.setStyleSheet("color: #667eea;")
        metrica_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(titulo_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()
        layout.addWidget(metrica_lbl)
        
        # Conectar click
        btn_frame.mousePressEvent = lambda event: self.modulo_solicitado.emit(modulo)
        
        # Guardar referencia para actualizar métrica
        setattr(btn_frame, 'metrica_label', metrica_lbl)
        setattr(btn_frame, 'modulo', modulo)
        
        return btn_frame
    
    # =================================================================
    # MÉTODOS PÚBLICOS PARA ACTUALIZACIÓN
    # =================================================================
    
    def actualizar_metricas(self):
        """Actualiza todas las métricas del dashboard."""
        # Este método será llamado por el controlador principal
        pass
    
    def actualizar_kpi(self, modulo, valor, tendencia=None):
        """Actualiza un KPI específico."""
        if modulo in self.widgets_kpi:
            self.widgets_kpi[modulo].actualizar_valor(valor, tendencia)
    
    def actualizar_grafico(self, tipo, datos):
        """Actualiza un gráfico específico."""
        if tipo == "ventas" and hasattr(self, 'chart_ventas'):
            self.chart_ventas.actualizar_datos(datos)
        elif tipo == "inventario" and hasattr(self, 'chart_inventario'):
            self.chart_inventario.actualizar_datos(datos)
        elif tipo == "obras" and hasattr(self, 'chart_obras'):
            self.chart_obras.actualizar_datos(datos)
    
    def agregar_actividad(self, icono, titulo, descripcion, timestamp=None):
        """Agrega una nueva actividad al feed."""
        if hasattr(self, 'widget_actividad'):
            self.widget_actividad.agregar_actividad(icono, titulo, descripcion, timestamp)
    
    def actualizar_header_metric(self, tipo, valor):
        """Actualiza métricas del header."""
        if tipo == "usuarios" and hasattr(self, 'header_usuarios_online'):
            self.header_usuarios_online.valor_label.setText(str(valor))
        elif tipo == "alertas" and hasattr(self, 'header_alertas'):
            self.header_alertas.valor_label.setText(str(valor))
        elif tipo == "sistema" and hasattr(self, 'header_estado_sistema'):
            self.header_estado_sistema.valor_label.setText(str(valor))
    
    def actualizar_metrica_modulo(self, modulo, valor):
        """Actualiza la métrica de un botón de módulo."""
        # Buscar el botón del módulo
        for child in self.findChildren(QFrame):
            if hasattr(child, 'modulo') and child.modulo == modulo:
                if hasattr(child, 'metrica_label'):
                    child.metrica_label.setText(str(valor))
                break