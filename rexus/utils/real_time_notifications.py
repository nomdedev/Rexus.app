"""
Sistema de Notificaciones en Tiempo Real - Rexus.app
Proporciona notificaciones instantáneas y gestión de eventos del sistema

Fecha: 23/08/2025
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from queue import Queue, Empty
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPainter, QColor

logger = logging.getLogger(__name__)

class NotificationLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class NotificationType(Enum):
    SYSTEM = "system"
    USER_ACTION = "user_action"
    DATABASE = "database"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MODULE = "module"

@dataclass
class Notification:
    id: str
    title: str
    message: str
    level: NotificationLevel
    type: NotificationType
    timestamp: datetime
    module: Optional[str] = None
    user_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    read: bool = False
    persistent: bool = False
    auto_dismiss: bool = True
    dismiss_after: int = 5000  # milliseconds

class NotificationWidget(QFrame):
    """Widget individual para mostrar una notificación."""
    
    dismissed = pyqtSignal(str)  # notification_id
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setup_ui()
        
        # Auto-dismiss timer
        if self.notification.auto_dismiss and not self.notification.persistent:
            QTimer.singleShot(self.notification.dismiss_after, self.auto_dismiss)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Color según nivel
        colors = {
            NotificationLevel.INFO: "#3498db",
            NotificationLevel.SUCCESS: "#2ecc71",
            NotificationLevel.WARNING: "#f39c12",
            NotificationLevel.ERROR: "#e74c3c",
            NotificationLevel.CRITICAL: "#c0392b"
        }
        
        bg_colors = {
            NotificationLevel.INFO: "#ebf3fd",
            NotificationLevel.SUCCESS: "#eafaf1",
            NotificationLevel.WARNING: "#fef5e7",
            NotificationLevel.ERROR: "#fdebea",
            NotificationLevel.CRITICAL: "#f9ebea"
        }
        
        color = colors.get(self.notification.level, "#3498db")
        bg_color = bg_colors.get(self.notification.level, "#ebf3fd")
        
        self.setStyleSheet(f"""
            QFrame {{
                border-left: 4px solid {color};
                background-color: {bg_color};
                border-radius: 4px;
                margin: 2px 0;
            }}
        """)
        
        # Icono
        icon_label = QLabel()
        icons = {
            NotificationLevel.INFO: "ℹ",
            NotificationLevel.SUCCESS: "✓",
            NotificationLevel.WARNING: "⚠",
            NotificationLevel.ERROR: "✗",
            NotificationLevel.CRITICAL: "🔥"
        }
        
        icon_label.setText(icons.get(self.notification.level, "ℹ"))
        icon_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        icon_label.setFixedSize(24, 24)
        
        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Título
        title_label = QLabel(self.notification.title)
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # Mensaje
        message_label = QLabel(self.notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #34495e; font-size: 12px;")
        
        # Timestamp y módulo
        info_text = self.notification.timestamp.strftime("%H:%M:%S")
        if self.notification.module:
            info_text += f" • {self.notification.module}"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        content_layout.addWidget(info_label)
        
        # Botón cerrar
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                color: {color};
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }}
        """)
        close_btn.clicked.connect(self.dismiss)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        layout.addWidget(close_btn)
        
    def dismiss(self):
        """Cierra la notificación."""
        self.dismissed.emit(self.notification.id)
        
    def auto_dismiss(self):
        """Auto-cierre de la notificación."""
        if not self.notification.persistent:
            self.dismiss()

class NotificationCenter(QWidget):
    """Centro de notificaciones con historial."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Centro de Notificaciones")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header.setFont(header_font)
        
        # Botones de control
        controls_layout = QHBoxLayout()
        
        clear_all_btn = QPushButton("Limpiar Todo")
        clear_all_btn.clicked.connect(self.clear_all)
        
        mark_read_btn = QPushButton("Marcar Leídas")
        mark_read_btn.clicked.connect(self.mark_all_read)
        
        controls_layout.addWidget(clear_all_btn)
        controls_layout.addWidget(mark_read_btn)
        controls_layout.addStretch()
        
        # Scroll area para notificaciones
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.addStretch()
        
        self.scroll_area.setWidget(self.notifications_widget)
        
        layout.addWidget(header)
        layout.addLayout(controls_layout)
        layout.addWidget(self.scroll_area)
        
    def add_notification(self, notification: Notification):
        """Añade una nueva notificación."""
        self.notifications.insert(0, notification)
        
        # Crear widget
        widget = NotificationWidget(notification)
        widget.dismissed.connect(self.remove_notification)
        
        # Insertar al inicio
        self.notifications_layout.insertWidget(0, widget)
        
        # Limitar número de notificaciones mostradas
        if self.notifications_layout.count() > 51:  # 50 + stretch
            item = self.notifications_layout.takeAt(50)
            if item and item.widget():
                item.widget().deleteLater()
                
    def remove_notification(self, notification_id: str):
        """Remueve una notificación."""
        self.notifications = [n for n in self.notifications if n.id != notification_id]
        
        # Buscar y remover widget
        for i in range(self.notifications_layout.count()):
            item = self.notifications_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), NotificationWidget):
                if item.widget().notification.id == notification_id:
                    item.widget().deleteLater()
                    break
                    
    def clear_all(self):
        """Limpia todas las notificaciones."""
        self.notifications.clear()
        
        # Remover widgets
        for i in reversed(range(self.notifications_layout.count())):
            item = self.notifications_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), NotificationWidget):
                item.widget().deleteLater()
                
    def mark_all_read(self):
        """Marca todas las notificaciones como leídas."""
        for notification in self.notifications:
            notification.read = True

class NotificationManager(QObject):
    """Gestor principal de notificaciones."""
    
    notification_added = pyqtSignal(object)  # Notification
    
    def __init__(self):
        super().__init__()
        self.notifications = []
        self.subscribers = {}
        self.persistent_storage = Path("notifications.json")
        self.notification_queue = Queue()
        self.processing_thread = None
        self.system_tray = None
        
        self.load_persistent_notifications()
        self.start_processing()
        
    def add_notification(self, 
                        title: str,
                        message: str,
                        level: NotificationLevel = NotificationLevel.INFO,
                        notification_type: NotificationType = NotificationType.SYSTEM,
                        module: Optional[str] = None,
                        user_id: Optional[str] = None,
                        data: Optional[Dict[str, Any]] = None,
                        persistent: bool = False,
                        auto_dismiss: bool = True,
                        dismiss_after: int = 5000) -> str:
        """Añade una nueva notificación."""
        
        notification_id = f"{int(time.time() * 1000)}_{hash(title + message) % 10000}"
        
        notification = Notification(
            id=notification_id,
            title=title,
            message=message,
            level=level,
            type=notification_type,
            timestamp=datetime.now(),
            module=module,
            user_id=user_id,
            data=data,
            persistent=persistent,
            auto_dismiss=auto_dismiss,
            dismiss_after=dismiss_after
        )
        
        self.notifications.append(notification)
        self.notification_queue.put(notification)
        
        if persistent:
            self.save_persistent_notifications()
            
        logger.info(f"Notificación añadida: {title} [{level.value}]")
        return notification_id
    
    def subscribe(self, callback: Callable[[Notification], None], 
                 filter_level: Optional[NotificationLevel] = None,
                 filter_type: Optional[NotificationType] = None):
        """Suscribe un callback a las notificaciones."""
        subscriber_id = f"sub_{int(time.time() * 1000)}"
        self.subscribers[subscriber_id] = {
            'callback': callback,
            'filter_level': filter_level,
            'filter_type': filter_type
        }
        return subscriber_id
    
    def unsubscribe(self, subscriber_id: str):
        """Desuscribe un callback."""
        self.subscribers.pop(subscriber_id, None)
    
    def start_processing(self):
        """Inicia el hilo de procesamiento de notificaciones."""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self._process_notifications, daemon=True)
            self.processing_thread.start()
    
    def _process_notifications(self):
        """Procesa notificaciones en hilo separado."""
        while True:
            try:
                notification = self.notification_queue.get(timeout=1.0)
                
                # Enviar a suscriptores
                for subscriber in self.subscribers.values():
                    if self._should_notify_subscriber(notification, subscriber):
                        try:
                            subscriber['callback'](notification)
                        except Exception as e:
                            logger.error(f"Error en callback de notificación: {e}")
                
                # Emitir señal Qt
                self.notification_added.emit(notification)
                
                # Mostrar en system tray si está disponible
                if self.system_tray:
                    self._show_tray_notification(notification)
                    
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error procesando notificación: {e}")
    
    def _should_notify_subscriber(self, notification: Notification, subscriber: dict) -> bool:
        """Determina si se debe notificar a un suscriptor."""
        if subscriber['filter_level'] and notification.level != subscriber['filter_level']:
            return False
            
        if subscriber['filter_type'] and notification.type != subscriber['filter_type']:
            return False
            
        return True
    
    def _show_tray_notification(self, notification: Notification):
        """Muestra notificación en system tray."""
        if self.system_tray and self.system_tray.isVisible():
            icon = QSystemTrayIcon.MessageIcon.Information
            
            if notification.level in [NotificationLevel.ERROR, NotificationLevel.CRITICAL]:
                icon = QSystemTrayIcon.MessageIcon.Critical
            elif notification.level == NotificationLevel.WARNING:
                icon = QSystemTrayIcon.MessageIcon.Warning
                
            self.system_tray.showMessage(
                notification.title,
                notification.message,
                icon,
                notification.dismiss_after
            )
    
    def setup_system_tray(self, app: QApplication):
        """Configura el system tray."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.system_tray = QSystemTrayIcon()
            
            # Crear icono simple
            icon = QIcon()
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(52, 152, 219))
            icon.addPixmap(pixmap)
            
            self.system_tray.setIcon(icon)
            self.system_tray.setToolTip("Rexus.app - Notificaciones")
            
            # Menú contextual
            menu = QMenu()
            menu.addAction("Mostrar Notificaciones", self._show_notification_center)
            menu.addSeparator()
            menu.addAction("Salir", app.quit)
            
            self.system_tray.setContextMenu(menu)
            self.system_tray.show()
            
    def _show_notification_center(self):
        """Muestra el centro de notificaciones."""
        pass  # Implementar cuando sea necesario
    
    def load_persistent_notifications(self):
        """Carga notificaciones persistentes."""
        try:
            if self.persistent_storage.exists():
                with open(self.persistent_storage, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    notification = Notification(
                        id=item['id'],
                        title=item['title'],
                        message=item['message'],
                        level=NotificationLevel(item['level']),
                        type=NotificationType(item['type']),
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        module=item.get('module'),
                        user_id=item.get('user_id'),
                        data=item.get('data'),
                        read=item.get('read', False),
                        persistent=item.get('persistent', False)
                    )
                    
                    # Solo cargar si no han expirado (7 días)
                    if datetime.now() - notification.timestamp < timedelta(days=7):
                        self.notifications.append(notification)
                        
        except Exception as e:
            logger.error(f"Error cargando notificaciones persistentes: {e}")
    
    def save_persistent_notifications(self):
        """Guarda notificaciones persistentes."""
        try:
            persistent_notifications = [n for n in self.notifications if n.persistent]
            
            data = []
            for notification in persistent_notifications:
                data.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'level': notification.level.value,
                    'type': notification.type.value,
                    'timestamp': notification.timestamp.isoformat(),
                    'module': notification.module,
                    'user_id': notification.user_id,
                    'data': notification.data,
                    'read': notification.read,
                    'persistent': notification.persistent
                })
                
            with open(self.persistent_storage, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando notificaciones persistentes: {e}")
    
    def get_notifications(self, 
                         limit: Optional[int] = None,
                         level: Optional[NotificationLevel] = None,
                         type: Optional[NotificationType] = None,
                         unread_only: bool = False) -> List[Notification]:
        """Obtiene notificaciones con filtros."""
        
        filtered = self.notifications
        
        if level:
            filtered = [n for n in filtered if n.level == level]
            
        if type:
            filtered = [n for n in filtered if n.type == type]
            
        if unread_only:
            filtered = [n for n in filtered if not n.read]
            
        # Ordenar por timestamp descendente
        filtered.sort(key=lambda n: n.timestamp, reverse=True)
        
        if limit:
            filtered = filtered[:limit]
            
        return filtered

# Instancia global del gestor
_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Obtiene la instancia global del gestor de notificaciones."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

# Funciones de conveniencia
def notify_info(title: str, message: str, **kwargs):
    """Notificación informativa."""
    manager = get_notification_manager()
    return manager.add_notification(title, message, NotificationLevel.INFO, **kwargs)

def notify_success(title: str, message: str, **kwargs):
    """Notificación de éxito."""
    manager = get_notification_manager()
    return manager.add_notification(title, message, NotificationLevel.SUCCESS, **kwargs)

def notify_warning(title: str, message: str, **kwargs):
    """Notificación de advertencia."""
    manager = get_notification_manager()
    return manager.add_notification(title, message, NotificationLevel.WARNING, **kwargs)

def notify_error(title: str, message: str, **kwargs):
    """Notificación de error."""
    manager = get_notification_manager()
    return manager.add_notification(title, message, NotificationLevel.ERROR, **kwargs)

def notify_critical(title: str, message: str, **kwargs):
    """Notificación crítica."""
    manager = get_notification_manager()
    return manager.add_notification(title, message, NotificationLevel.CRITICAL, **kwargs)

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # Test del sistema de notificaciones
    manager = get_notification_manager()
    center = NotificationCenter()
    
    # Conectar centro a manager
    manager.notification_added.connect(center.add_notification)
    
    # Configurar system tray
    manager.setup_system_tray(app)
    
    # Notificaciones de prueba
    notify_info("Sistema Iniciado", "Rexus.app iniciado correctamente")
    notify_success("Conexión Establecida", "Base de datos conectada")
    notify_warning("Advertencia", "Espacio en disco bajo")
    notify_error("Error de Conexión", "No se pudo conectar al servidor")
    notify_critical("Error Crítico", "Fallo en el sistema de seguridad")
    
    center.show()
    center.resize(400, 600)
    
    sys.exit(app.exec())