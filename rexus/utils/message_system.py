"""
Sistema de Mensajes Mejorado para Rexus.app

Proporciona mensajes visuales consistentes y atractivos usando QMessageBox
con iconos, estilos y comportamientos personalizados.
"""

from enum import Enum
from typing import Optional, Callable
from PyQt6.QtWidgets import QMessageBox, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor


class MessageType(Enum):
    """Tipos de mensajes disponibles."""
    SUCCESS = "success"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"
    QUESTION = "question"


class MessageSystem:
    """Sistema centralizado de mensajes para la aplicación."""
    
    # Configuración de iconos y colores por tipo
    MESSAGE_CONFIG = {
        MessageType.SUCCESS: {
            'icon': QMessageBox.Icon.Information,
            'title_prefix': '✅ Éxito',
            'color': '#27ae60',
            'button_style': 'success'
        },
        MessageType.ERROR: {
            'icon': QMessageBox.Icon.Critical,
            'title_prefix': '❌ Error',
            'color': '#e74c3c',
            'button_style': 'error'
        },
        MessageType.WARNING: {
            'icon': QMessageBox.Icon.Warning,
            'title_prefix': '⚠️ Advertencia',
            'color': '#f39c12',
            'button_style': 'warning'
        },
        MessageType.INFO: {
            'icon': QMessageBox.Icon.Information,
            'title_prefix': 'ℹ️ Información',
            'color': '#3498db',
            'button_style': 'info'
        },
        MessageType.QUESTION: {
            'icon': QMessageBox.Icon.Question,
            'title_prefix': '❓ Confirmación',
            'color': '#9b59b6',
            'button_style': 'question'
        }
    }
    
    @staticmethod
    def _get_message_style(message_type: MessageType) -> str:
        """Obtiene el estilo CSS para el tipo de mensaje."""
        config = MessageSystem.MESSAGE_CONFIG[message_type]
        color = config['color']
        
        return f"""
        QMessageBox {{
            background-color: white;
            border: 2px solid {color};
            border-radius: 8px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }}
        QMessageBox QLabel {{
            color: #2c3e50;
            padding: 10px;
            font-size: 14px;
            line-height: 1.4;
        }}
        QMessageBox QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {MessageSystem._darken_color(color)};
        }}
        QMessageBox QPushButton:pressed {{
            background-color: {MessageSystem._darken_color(color, 0.8)};
        }}
        """
    
    @staticmethod
    def _darken_color(hex_color: str, factor: float = 0.85) -> str:
        """Oscurece un color hexadecimal por un factor dado."""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            dark_rgb = tuple(int(c * factor) for c in rgb)
            return f"#{dark_rgb[0]:02x}{dark_rgb[1]:02x}{dark_rgb[2]:02x}"
        except:
            return "#666666"  # Color por defecto si falla
    
    @staticmethod
    def show_message(
        parent: Optional[QWidget],
        message_type: MessageType,
        title: str,
        text: str,
        detailed_text: Optional[str] = None,
        auto_close_ms: Optional[int] = None
    ) -> QMessageBox.StandardButton:
        """
        Muestra un mensaje con estilo personalizado.
        
        Args:
            parent: Widget padre
            message_type: Tipo de mensaje
            title: Título del mensaje
            text: Texto principal
            detailed_text: Texto detallado opcional
            auto_close_ms: Tiempo en ms para cerrar automáticamente
            
        Returns:
            Botón presionado por el usuario
        """
        try:
            config = MessageSystem.MESSAGE_CONFIG[message_type]
            
            # Crear message box
            msg_box = QMessageBox(parent)
            msg_box.setIcon(config['icon'])
            msg_box.setWindowTitle(f"{config['title_prefix']} - {title}")
            msg_box.setText(text)
            
            if detailed_text:
                msg_box.setDetailedText(detailed_text)
            
            # Aplicar estilo
            msg_box.setStyleSheet(MessageSystem._get_message_style(message_type))
            
            # Configurar botones según el tipo
            if message_type == MessageType.QUESTION:
                msg_box.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            else:
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            # Auto cierre si se especifica
            if auto_close_ms:
                timer = QTimer()
                timer.timeout.connect(msg_box.accept)
                timer.start(auto_close_ms)
                msg_box.finished.connect(timer.stop)
            
            # Mostrar y devolver resultado
            return msg_box.exec()
            
        except Exception as e:
            # Fallback a mensaje básico si hay error
            fallback_msg = QMessageBox(parent)
            fallback_msg.setText(f"{title}: {text}")
            fallback_msg.exec()
            return QMessageBox.StandardButton.Ok
    
    @staticmethod
    def success(
        parent: Optional[QWidget],
        title: str,
        message: str,
        auto_close_ms: Optional[int] = 3000
    ):
        """Muestra un mensaje de éxito."""
        return MessageSystem.show_message(
            parent, MessageType.SUCCESS, title, message, auto_close_ms=auto_close_ms
        )
    
    @staticmethod
    def error(
        parent: Optional[QWidget],
        title: str,
        message: str,
        detailed_error: Optional[str] = None
    ):
        """Muestra un mensaje de error."""
        return MessageSystem.show_message(
            parent, MessageType.ERROR, title, message, detailed_text=detailed_error
        )
    
    @staticmethod
    def warning(
        parent: Optional[QWidget],
        title: str, 
        message: str
    ):
        """Muestra un mensaje de advertencia."""
        return MessageSystem.show_message(
            parent, MessageType.WARNING, title, message
        )
    
    @staticmethod
    def info(
        parent: Optional[QWidget],
        title: str,
        message: str,
        auto_close_ms: Optional[int] = None
    ):
        """Muestra un mensaje informativo."""
        return MessageSystem.show_message(
            parent, MessageType.INFO, title, message, auto_close_ms=auto_close_ms
        )
    
    @staticmethod
    def question(
        parent: Optional[QWidget],
        title: str,
        message: str
    ) -> bool:
        """
        Muestra una pregunta de confirmación.
        
        Returns:
            True si el usuario selecciona Sí, False si selecciona No
        """
        result = MessageSystem.show_message(
            parent, MessageType.QUESTION, title, message
        )
        return result == QMessageBox.StandardButton.Yes


class ProgressMessage:
    """Mensaje de progreso no bloqueante."""
    
    def __init__(self, parent: Optional[QWidget], title: str, message: str):
        self.parent = parent
        self.msg_box = QMessageBox(parent)
        self.msg_box.setIcon(QMessageBox.Icon.Information)
        self.msg_box.setWindowTitle(f"⏳ {title}")
        self.msg_box.setText(message)
        self.msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        self.msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                padding: 15px;
                font-size: 14px;
            }
        """)
    
    def show(self):
        """Muestra el mensaje de progreso."""
        self.msg_box.show()
    
    def update_message(self, new_message: str):
        """Actualiza el texto del mensaje."""
        self.msg_box.setText(new_message)
    
    def close(self):
        """Cierra el mensaje de progreso."""
        self.msg_box.close()


class StatusMessage:
    """Mensaje de estado temporal (toast-like)."""
    
    def __init__(self, parent: Optional[QWidget]):
        self.parent = parent
        self.current_message = None
    
    def show_status(
        self, 
        message: str, 
        message_type: MessageType = MessageType.INFO,
        duration_ms: int = 2000
    ):
        """Muestra un mensaje de estado temporal."""
        if self.current_message:
            self.current_message.close()
        
        config = MessageSystem.MESSAGE_CONFIG[message_type]
        
        self.current_message = QMessageBox(self.parent)
        self.current_message.setIcon(config['icon'])
        self.current_message.setWindowTitle("Estado")
        self.current_message.setText(message)
        self.current_message.setStandardButtons(QMessageBox.StandardButton.NoButton)
        self.current_message.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                border: 2px solid {config['color']};
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QMessageBox QLabel {{
                color: #2c3e50;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
        """)
        
        # Auto cerrar después del tiempo especificado
        timer = QTimer()
        timer.timeout.connect(self.current_message.close)
        timer.start(duration_ms)
        
        self.current_message.show()


# Funciones de conveniencia para uso directo
def show_success(parent: QWidget, title: str, message: str, auto_close: bool = True):
    """Función de conveniencia para mostrar mensaje de éxito."""
    return MessageSystem.success(
        parent, title, message, 
        auto_close_ms=3000 if auto_close else None
    )

def show_error(parent: QWidget, title: str, message: str, details: str = None):
    """Función de conveniencia para mostrar mensaje de error."""
    return MessageSystem.error(parent, title, message, details)

def show_warning(parent: QWidget, title: str, message: str):
    """Función de conveniencia para mostrar mensaje de advertencia."""
    return MessageSystem.warning(parent, title, message)

def show_info(parent: QWidget, title: str, message: str, auto_close: bool = False):
    """Función de conveniencia para mostrar mensaje informativo."""
    return MessageSystem.info(
        parent, title, message,
        auto_close_ms=4000 if auto_close else None
    )

def ask_question(parent: QWidget, title: str, message: str) -> bool:
    """Función de conveniencia para hacer una pregunta."""
    return MessageSystem.question(parent, title, message)