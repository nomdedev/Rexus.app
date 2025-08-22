# -*- coding: utf-8 -*-
"""
Activity Widget - Feed de actividad reciente del sistema
Muestra las últimas acciones, alertas y eventos importantes
"""

from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QPushButton, QMenu
)
from PyQt6.QtGui import QFont, QAction
import datetime


class ActivityWidget(QFrame):
    """Widget para mostrar feed de actividad reciente."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.actividades = []
        self.max_actividades = 50
        
        self.setup_ui()
        self.aplicar_estilos()
        
        # Cargar actividades de ejemplo
        self.cargar_actividades_ejemplo()
        
        # Timer para limpiar actividades antiguas
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.limpiar_actividades_antiguas)
        self.cleanup_timer.start(300000)  # 5 minutos
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # Header con título y controles
        header_layout = QHBoxLayout()
        
        self.titulo_label = QLabel("🔔 Actividad Reciente")
        self.titulo_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.titulo_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        
        # Botón de filtros
        self.btn_filtros = QPushButton("⚙️")
        self.btn_filtros.setFixedSize(24, 24)
        self.btn_filtros.setToolTip("Filtros de actividad")
        self.btn_filtros.clicked.connect(self.mostrar_menu_filtros)
        
        # Botón limpiar
        self.btn_limpiar = QPushButton("🗑️")
        self.btn_limpiar.setFixedSize(24, 24)
        self.btn_limpiar.setToolTip("Limpiar actividades")
        self.btn_limpiar.clicked.connect(self.limpiar_todas_actividades)
        
        header_layout.addWidget(self.titulo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_filtros)
        header_layout.addWidget(self.btn_limpiar)
        
        # Área de scroll para actividades
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget contenedor de actividades
        self.actividades_container = QWidget()
        self.actividades_layout = QVBoxLayout(self.actividades_container)
        self.actividades_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.actividades_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.actividades_container)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area)
    
    def aplicar_estilos(self):
        """Aplica estilos al widget."""
        self.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: none;
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
    
    def agregar_actividad(self, icono, titulo, descripcion, timestamp=None, tipo="info"):
        """Agrega una nueva actividad al feed."""
        if timestamp is None:
            timestamp = QDateTime.currentDateTime()
        
        actividad = {
            'icono': icono,
            'titulo': titulo,
            'descripcion': descripcion,
            'timestamp': timestamp,
            'tipo': tipo
        }
        
        self.actividades.insert(0, actividad)  # Agregar al inicio
        
        # Limitar número de actividades
        if len(self.actividades) > self.max_actividades:
            self.actividades = self.actividades[:self.max_actividades]
        
        self.actualizar_vista()
    
    def actualizar_vista(self):
        """Actualiza la vista de actividades."""
        # Limpiar layout
        self.limpiar_layout()
        
        # Agregar actividades
        for actividad in self.actividades:
            widget_actividad = self.crear_widget_actividad(actividad)
            self.actividades_layout.addWidget(widget_actividad)
        
        # Scroll al top para mostrar la más reciente
        self.scroll_area.verticalScrollBar().setValue(0)
    
    def crear_widget_actividad(self, actividad):
        """Crea un widget para una actividad individual."""
        widget = QFrame()
        widget.setFixedHeight(60)
        widget.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 1px;
                padding: 8px;
            }}
            QFrame:hover {{
                background: #f8f9ff;
                border: 1px solid {self.get_color_tipo(actividad['tipo'])};
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # Icono
        icono_label = QLabel(actividad['icono'])
        icono_label.setFont(QFont("Segoe UI", 16))
        icono_label.setFixedSize(24, 24)
        icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Contenido
        contenido_layout = QVBoxLayout()
        contenido_layout.setSpacing(2)
        
        # Título
        titulo_label = QLabel(actividad['titulo'])
        titulo_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #333;")
        
        # Descripción
        desc_label = QLabel(actividad['descripcion'])
        desc_label.setFont(QFont("Segoe UI", 8))
        desc_label.setStyleSheet("color: #666;")
        desc_label.setWordWrap(True)
        
        contenido_layout.addWidget(titulo_label)
        contenido_layout.addWidget(desc_label)
        
        # Timestamp
        tiempo_layout = QVBoxLayout()
        tiempo_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        tiempo_label = QLabel(self.format_timestamp(actividad['timestamp']))
        tiempo_label.setFont(QFont("Segoe UI", 7))
        tiempo_label.setStyleSheet("color: #999;")
        tiempo_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Indicador de tipo
        tipo_indicator = QFrame()
        tipo_indicator.setFixedSize(8, 8)
        tipo_indicator.setStyleSheet(f"""
            QFrame {{
                background: {self.get_color_tipo(actividad['tipo'])};
                border-radius: 4px;
            }}
        """)
        
        tiempo_layout.addWidget(tiempo_label)
        tiempo_layout.addStretch()
        tiempo_layout.addWidget(tipo_indicator)
        
        layout.addWidget(icono_label)
        layout.addLayout(contenido_layout, 1)
        layout.addLayout(tiempo_layout)
        
        return widget
    
    def get_color_tipo(self, tipo):
        """Retorna el color según el tipo de actividad."""
        colores = {
            'info': '#2196f3',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'system': '#9c27b0'
        }
        return colores.get(tipo, '#2196f3')
    
    def format_timestamp(self, timestamp):
        """Formatea el timestamp para mostrar."""
        now = QDateTime.currentDateTime()
        diff = timestamp.secsTo(now)
        
        if diff < 60:
            return "Ahora"
        elif diff < 3600:
            minutos = diff // 60
            return f"hace {minutos}m"
        elif diff < 86400:
            horas = diff // 3600
            return f"hace {horas}h"
        else:
            dias = diff // 86400
            return f"hace {dias}d"
    
    def limpiar_layout(self):
        """Limpia todos los widgets del layout."""
        while self.actividades_layout.count():
            child = self.actividades_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def limpiar_actividades_antiguas(self):
        """Limpia actividades más antiguas de 24 horas."""
        ahora = QDateTime.currentDateTime()
        self.actividades = [
            act for act in self.actividades
            if act['timestamp'].secsTo(ahora) < 86400  # 24 horas
        ]
        self.actualizar_vista()
    
    def limpiar_todas_actividades(self):
        """Limpia todas las actividades."""
        self.actividades.clear()
        self.actualizar_vista()
    
    def mostrar_menu_filtros(self):
        """Muestra el menú de filtros."""
        menu = QMenu(self)
        
        # Acciones de filtro
        todo_action = QAction("📋 Mostrar todo", self)
        todo_action.triggered.connect(lambda: self.filtrar_por_tipo(None))
        
        info_action = QAction("ℹ️ Solo información", self)
        info_action.triggered.connect(lambda: self.filtrar_por_tipo("info"))
        
        success_action = QAction("✅ Solo éxitos", self)
        success_action.triggered.connect(lambda: self.filtrar_por_tipo("success"))
        
        warning_action = QAction("⚠️ Solo advertencias", self)
        warning_action.triggered.connect(lambda: self.filtrar_por_tipo("warning"))
        
        error_action = QAction("❌ Solo errores", self)
        error_action.triggered.connect(lambda: self.filtrar_por_tipo("error"))
        
        menu.addAction(todo_action)
        menu.addSeparator()
        menu.addAction(info_action)
        menu.addAction(success_action)
        menu.addAction(warning_action)
        menu.addAction(error_action)
        
        # Mostrar menú
        menu.exec(self.btn_filtros.mapToGlobal(self.btn_filtros.rect().bottomLeft()))
    
    def filtrar_por_tipo(self, tipo_filtro):
        """Filtra actividades por tipo."""
        # TODO: Implementar filtrado
        pass
    
    def cargar_actividades_ejemplo(self):
        """Carga actividades de ejemplo para testing."""
        ejemplos = [
            ("👤", "Nuevo usuario registrado", "Juan Pérez se ha registrado en el sistema", "success"),
            ("📦", "Stock bajo detectado", "Producto 'Vidrio 6mm' tiene stock inferior a 10 unidades", "warning"),
            ("💰", "Nueva venta realizada", "Pedido #1234 completado por $2,500.00", "success"),
            ("🔧", "Mantenimiento programado", "Backup de base de datos ejecutado correctamente", "system"),
            ("⚠️", "Error de conexión", "Fallo temporal en conexión con proveedor ABC", "error"),
            ("📋", "Pedido actualizado", "Estado de pedido #1235 cambiado a 'En tránsito'", "info"),
            ("🏢", "Obra completada", "Obra 'Edificio Central' marcada como completada", "success"),
            ("🔔", "Notificación enviada", "Email de confirmación enviado a cliente", "info")
        ]
        
        for i, (icono, titulo, desc, tipo) in enumerate(ejemplos):
            # Crear timestamps distribuidos en las últimas horas
            timestamp = QDateTime.currentDateTime().addSecs(-(i * 1800))  # Cada 30 minutos
            self.agregar_actividad(icono, titulo, desc, timestamp, tipo)


class ActivityCompactWidget(QFrame):
    """Versión compacta del widget de actividad para espacios reducidos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.actividades = []
        self.max_actividades = 5  # Menos actividades en versión compacta
        
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura la interfaz compacta."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)
        
        # Título
        titulo = QLabel("🔔 Actividad")
        titulo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #333; margin-bottom: 8px;")
        
        # Lista de actividades
        self.actividades_layout = QVBoxLayout()
        self.actividades_layout.setSpacing(4)
        self.actividades_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(titulo)
        layout.addLayout(self.actividades_layout)
        layout.addStretch()
    
    def aplicar_estilos(self):
        """Aplica estilos compactos."""
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
    
    def agregar_actividad_compacta(self, icono, texto, tipo="info"):
        """Agrega una actividad en formato compacto."""
        widget = QFrame()
        widget.setFixedHeight(30)
        widget.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-left: 3px solid {self.get_color_tipo(tipo)};
                padding-left: 8px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 4, 0, 4)
        
        # Icono
        icono_label = QLabel(icono)
        icono_label.setFont(QFont("Segoe UI", 12))
        icono_label.setFixedSize(16, 16)
        
        # Texto
        texto_label = QLabel(texto)
        texto_label.setFont(QFont("Segoe UI", 8))
        texto_label.setStyleSheet("color: #333;")
        
        layout.addWidget(icono_label)
        layout.addWidget(texto_label, 1)
        
        # Agregar al layout principal
        self.actividades_layout.insertWidget(0, widget)
        
        # Limitar número de actividades
        if self.actividades_layout.count() > self.max_actividades:
            last_widget = self.actividades_layout.takeAt(self.max_actividades)
            if last_widget.widget():
                last_widget.widget().deleteLater()
    
    def get_color_tipo(self, tipo):
        """Retorna el color según el tipo de actividad."""
        colores = {
            'info': '#2196f3',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'system': '#9c27b0'
        }
        return colores.get(tipo, '#2196f3')