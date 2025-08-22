# -*- coding: utf-8 -*-
"""
Vista de Notificaciones - Rexus.app
Interfaz gráfica para el sistema de notificaciones y alertas
"""

import sys
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QListWidget, QListWidgetItem, QLabel, QFrame,
                            QComboBox, QTextEdit, QProgressBar, QTabWidget,
                            QScrollArea, QSplitter, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

from rexus.core.logger import setup_logger
from .model import NotificacionesModel, TipoNotificacion

logger = setup_logger(__name__)

class NotificacionWidget(QFrame):
    """Widget individual para mostrar una notificación"""
    
    clicked = pyqtSignal(dict)
    dismissed = pyqtSignal(int)
    
    def __init__(self, notificacion: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.notificacion = notificacion
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """Configura la interfaz del widget de notificación"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Icono según tipo
        icon_label = QLabel()
        tipo = self.notificacion.get('tipo', 'info')
        icons = {
            'info': '🔵',
            'warning': '⚠️', 
            'error': '❌',
            'success': '✅',
            'critical': '🚨'
        }
        icon_label.setText(icons.get(tipo, '🔵'))
        icon_label.setFixedSize(24, 24)
        
        # Contenido principal
        content_layout = QVBoxLayout()
        
        # Título y timestamp
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.notificacion.get('titulo', 'Sin título'))
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        time_label = QLabel(self.notificacion.get('timestamp', ''))
        time_label.setStyleSheet("color: #666; font-size: 9px;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        # Mensaje
        message_label = QLabel(self.notificacion.get('mensaje', ''))
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #333; margin-top: 2px;")
        
        content_layout.addLayout(header_layout)
        content_layout.addWidget(message_label)
        
        # Botón descartar
        dismiss_btn = QPushButton('×')
        dismiss_btn.setFixedSize(20, 20)
        dismiss_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #999;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                color: #333;
            }
        """)
        dismiss_btn.clicked.connect(self.dismiss_notification)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        layout.addWidget(dismiss_btn)
    
    def apply_style(self):
        """Aplica estilos según el tipo de notificación"""
        tipo = self.notificacion.get('tipo', 'info')
        
        styles = {
            'info': "background: #e3f2fd; border-left: 4px solid #2196f3;",
            'warning': "background: #fff8e1; border-left: 4px solid #ff9800;",
            'error': "background: #ffebee; border-left: 4px solid #f44336;",
            'success': "background: #e8f5e8; border-left: 4px solid #4caf50;",
            'critical': "background: #fce4ec; border-left: 4px solid #e91e63;"
        }
        
        base_style = """
            QFrame {
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QFrame:hover {
                background: rgba(0,0,0,0.05);
            }
        """
        
        self.setStyleSheet(base_style + styles.get(tipo, styles['info']))
    
    def dismiss_notification(self):
        """Emite señal para descartar notificación"""
        notif_id = self.notificacion.get('id', 0)
        self.dismissed.emit(notif_id)
    
    def mousePressEvent(self, event):
        """Maneja click en la notificación"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.notificacion)
        super().mousePressEvent(event)

class NotificacionesView(QWidget):
    """Vista principal del sistema de notificaciones"""
    
    notificacion_selected = pyqtSignal(dict)
    notificacion_dismissed = pyqtSignal(int)
    filtro_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.notification_widgets = []
        self.setup_ui()
        self.setup_connections()
        self.setup_auto_refresh()
        logger.info("Vista de notificaciones inicializada")
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header con título y controles
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Centro de Notificaciones")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        
        # Filtros
        self.tipo_filter = QComboBox()
        self.tipo_filter.addItems(['Todas', 'Info', 'Advertencia', 'Error', 'Éxito', 'Crítico'])
        self.tipo_filter.setCurrentText('Todas')
        
        # Botones de acción
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.clear_all_btn = QPushButton("🗑️ Limpiar Todo")
        self.mark_read_btn = QPushButton("✓ Marcar Leídas")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filtrar:"))
        header_layout.addWidget(self.tipo_filter)
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.mark_read_btn)
        header_layout.addWidget(self.clear_all_btn)
        
        # Área de notificaciones con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.notifications_container)
        
        # Panel de estadísticas
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_label = QLabel("Sin notificaciones")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        # Layout principal
        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area, 1)
        layout.addWidget(stats_frame)
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.tipo_filter.currentTextChanged.connect(self.filter_notifications)
        self.refresh_btn.clicked.connect(self.refresh_notifications)
        self.clear_all_btn.clicked.connect(self.clear_all_notifications)
        self.mark_read_btn.clicked.connect(self.mark_all_read)
    
    def setup_auto_refresh(self):
        """Configura actualización automática"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_notifications)
        self.refresh_timer.start(30000)  # 30 segundos
    
    def set_model(self, model: NotificacionesModel):
        """Establece el modelo de notificaciones"""
        self.model = model
        logger.info("Modelo de notificaciones establecido")
        self.refresh_notifications()
    
    def refresh_notifications(self):
        """Actualiza la lista de notificaciones"""
        try:
            if not self.model:
                logger.warning("No hay modelo disponible para actualizar notificaciones")
                return
            
            # Limpiar widgets existentes
            self.clear_notification_widgets()
            
            # Obtener notificaciones del modelo
            notificaciones = self.model.obtener_notificaciones_activas()
            
            # Aplicar filtro
            filtro_tipo = self.tipo_filter.currentText().lower()
            if filtro_tipo != 'todas':
                tipo_map = {
                    'info': 'info',
                    'advertencia': 'warning', 
                    'error': 'error',
                    'éxito': 'success',
                    'crítico': 'critical'
                }
                filtro_real = tipo_map.get(filtro_tipo, 'info')
                notificaciones = [n for n in notificaciones if n.get('tipo') == filtro_real]
            
            # Crear widgets de notificación
            for notificacion in notificaciones:
                widget = NotificacionWidget(notificacion)
                widget.clicked.connect(self.notificacion_selected.emit)
                widget.dismissed.connect(self.dismiss_notification)
                
                self.notifications_layout.addWidget(widget)
                self.notification_widgets.append(widget)
            
            # Actualizar estadísticas
            self.update_stats(len(notificaciones))
            
            logger.info(f"Notificaciones actualizadas: {len(notificaciones)}")
            
        except Exception as e:
            logger.error(f"Error actualizando notificaciones: {e}")
    
    def clear_notification_widgets(self):
        """Limpia todos los widgets de notificación"""
        for widget in self.notification_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.notification_widgets.clear()
    
    def filter_notifications(self, tipo: str):
        """Filtra notificaciones por tipo"""
        self.filtro_changed.emit(tipo)
        self.refresh_notifications()
    
    def dismiss_notification(self, notif_id: int):
        """Descarta una notificación específica"""
        try:
            if self.model:
                self.model.marcar_leida(notif_id)
                self.notificacion_dismissed.emit(notif_id)
                self.refresh_notifications()
                logger.info(f"Notificación {notif_id} descartada")
        except Exception as e:
            logger.error(f"Error descartando notificación {notif_id}: {e}")
    
    def clear_all_notifications(self):
        """Limpia todas las notificaciones"""
        try:
            if self.model:
                self.model.limpiar_notificaciones()
                self.refresh_notifications()
                logger.info("Todas las notificaciones limpiadas")
        except Exception as e:
            logger.error(f"Error limpiando notificaciones: {e}")
    
    def mark_all_read(self):
        """Marca todas las notificaciones como leídas"""
        try:
            if self.model:
                self.model.marcar_todas_leidas()
                self.refresh_notifications()
                logger.info("Todas las notificaciones marcadas como leídas")
        except Exception as e:
            logger.error(f"Error marcando notificaciones como leídas: {e}")
    
    def update_stats(self, count: int):
        """Actualiza las estadísticas mostradas"""
        if count == 0:
            self.stats_label.setText("Sin notificaciones pendientes")
        elif count == 1:
            self.stats_label.setText("1 notificación pendiente")
        else:
            self.stats_label.setText(f"{count} notificaciones pendientes")
    
    def add_notification(self, titulo: str, mensaje: str, tipo: str = 'info'):
        """Agrega una nueva notificación"""
        try:
            if self.model:
                self.model.crear_notificacion(titulo, mensaje, tipo)
                self.refresh_notifications()
                logger.info(f"Nueva notificación agregada: {titulo}")
        except Exception as e:
            logger.error(f"Error agregando notificación: {e}")

class NotificationToast(QWidget):
    """Widget flotante para mostrar notificaciones temporales"""
    
    def __init__(self, mensaje: str, tipo: str = 'info', duracion: int = 3000, parent=None):
        super().__init__(parent)
        self.duracion = duracion
        self.setup_ui(mensaje, tipo)
        self.setup_animation()
    
    def setup_ui(self, mensaje: str, tipo: str):
        """Configura la interfaz del toast"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icono
        icon_label = QLabel()
        icons = {
            'info': '🔵',
            'warning': '⚠️',
            'error': '❌', 
            'success': '✅'
        }
        icon_label.setText(icons.get(tipo, '🔵'))
        
        # Mensaje
        msg_label = QLabel(mensaje)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: white; font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(msg_label)
        
        # Estilo según tipo
        colors = {
            'info': '#2196f3',
            'warning': '#ff9800',
            'error': '#f44336',
            'success': '#4caf50'
        }
        
        color = colors.get(tipo, '#2196f3')
        self.setStyleSheet(f"""
            QWidget {{
                background: {color};
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
        """)
    
    def setup_animation(self):
        """Configura la animación del toast"""
        # Auto-cerrar después de la duración especificada
        QTimer.singleShot(self.duracion, self.close)
    
    def show_toast(self):
        """Muestra el toast en pantalla"""
        # Posicionar en la esquina superior derecha
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 20
            self.move(x, y)
        
        self.show()
        self.raise_()