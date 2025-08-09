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
Componentes Avanzados de Feedback Visual - Rexus.app
Versión: 2.0.0 - Enterprise Ready

Spinners, progress bars, toast notifications y otros componentes
avanzados de feedback integrados con el sistema de temas.
"""

from typing import Optional, Union
from PyQt6.QtCore import (
    QTimer, QPropertyAnimation, QRect, QEasingCurve, 
    pyqtSignal, QObject, QParallelAnimationGroup
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QFrame, QVBoxLayout, 
    QHBoxLayout, QGraphicsDropShadowEffect, QApplication
)

from ..core.themes import get_theme, ColorPalette
from ..utils.theme_manager import ThemeManager
from ..core.logger import get_logger

logger = get_logger("advanced_feedback")


class AnimatedSpinner(QLabel):
    """
    Spinner animado integrado con el sistema de temas.
    Útil para indicar procesos en curso.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
        # Configuración inicial
        self.setFixedSize(32, 32)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Aplicar tema inicial
        self._apply_theme()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_theme(self):
        """Aplicar estilos del tema actual"""
        colors = self._get_theme_colors()
        
        # Crear pixmap del spinner con colores del tema
        pixmap = self._create_spinner_pixmap(colors)
        self.setPixmap(pixmap)
    
    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            return get_theme("light")
    
    def _create_spinner_pixmap(self, colors: ColorPalette) -> QPixmap:
        """Crear pixmap del spinner con colores del tema"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparente
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configurar pen con color del tema
        pen = QPen(QColor(colors.primary))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Dibujar arcos con opacidades decrecientes
        for i in range(8):
            opacity = max(0.1, 1.0 - (i * 0.125))
            pen.setColor(QColor(colors.primary))
            color = pen.color()
            color.setAlphaF(opacity)
            pen.setColor(color)
            painter.setPen(pen)
            
            angle = (self.angle + i * 45) % 360
            painter.drawArc(6, 6, 20, 20, angle * 16, 30 * 16)
        
        painter.end()
        return pixmap
    
    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema"""
        self._apply_theme()
    
    def rotate(self):
        """Rotar el spinner"""
        self.angle = (self.angle + 45) % 360
        colors = self._get_theme_colors()
        pixmap = self._create_spinner_pixmap(colors)
        self.setPixmap(pixmap)
    
    def start(self):
        """Iniciar animación"""
        self.timer.start(100)  # 100ms = animación suave
        self.show()
    
    def stop(self):
        """Detener animación"""
        self.timer.stop()
        self.hide()


class ThemedProgressBar(QProgressBar):
    """
    Progress bar integrado con el sistema de temas.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self._apply_theme()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_theme(self):
        """Aplicar estilos del tema actual"""
        colors = self._get_theme_colors()
        
        style = f"""
            QProgressBar {{
                border: 2px solid {colors.border};
                border-radius: 8px;
                background-color: {colors.surface_variant};
                text-align: center;
                font-weight: bold;
                font-size: 11px;
                color: {colors.on_surface};
                padding: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0.5, x2:1, y2:0.5,
                    stop:0 {colors.primary}, stop:1 {self._lighten_color(colors.primary)});
                border-radius: 6px;
                margin: 1px;
            }}
        """
        
        self.setStyleSheet(style)
    
    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            return get_theme("light")
    
    def _lighten_color(self, color: str, factor: float = 1.2) -> str:
        """Aclarar un color hexadecimal"""
        if not color.startswith('#'):
            return color
        
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c * factor)) for c in rgb)
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        except (ValueError, IndexError):
            return color
    
    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema"""
        self._apply_theme()


class ToastNotification(QFrame):
    """
    Notificación toast no intrusiva que aparece temporalmente.
    """
    
    # Señal emitida cuando la notificación se cierra
    closed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_animated)
        
        # Configuración inicial
        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icono
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        
        # Mensaje
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)
        
        # Aplicar tema y efectos
        self._apply_theme()
        self._setup_shadow()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Inicialmente oculto
        self.hide()
    
    def _apply_theme(self, message_type: str = "info"):
        """Aplicar estilos del tema según el tipo de mensaje"""
        colors = self._get_theme_colors()
        
        # Mapeo de tipos a colores
        type_colors = {
            "info": colors.info,
            "success": colors.success,
            "warning": colors.warning,
            "error": colors.error
        }
        
        accent_color = type_colors.get(message_type, colors.info)
        
        style = f"""
            QFrame {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-left: 4px solid {accent_color};
                border-radius: 8px;
                color: {colors.on_surface};
            }}
            QLabel {{
                color: {colors.on_surface};
                background: transparent;
                border: none;
            }}
        """
        
        self.setStyleSheet(style)
    
    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            return get_theme("light")
    
    def _setup_shadow(self):
        """Configurar sombra para el toast"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
    
    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema"""
        self._apply_theme()
    
    def show_message(self, message: str, message_type: str = "info", duration: int = 4000):
        """
        Mostrar mensaje toast.
        
        Args:
            message: Mensaje a mostrar
            message_type: Tipo ('info', 'success', 'warning', 'error')
            duration: Duración en ms
        """
        # Iconos por tipo
        icons = {
            "info": "ℹ️",
            "success": "[CHECK]", 
            "warning": "[WARN]",
            "error": "[ERROR]"
        }
        
        # Configurar contenido
        self.icon_label.setText(icons.get(message_type, "ℹ️"))
        self.icon_label.setStyleSheet("font-size: 18px;")
        
        self.message_label.setText(message)
        self.message_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        
        # Aplicar estilos del tipo
        self._apply_theme(message_type)
        
        # Mostrar con animación
        self.show_animated()
        
        # Programar ocultación
        if duration > 0:
            self.timer.start(duration)
        
        logger.debug(f"Toast mostrado: {message_type} - {message}")
    
    def show_animated(self):
        """Mostrar con animación de deslizamiento"""
        if not self.parent():
            return
        
        # Posicionar en la esquina superior derecha
        parent_rect = self.parent().rect()
        self.move(parent_rect.width() - self.width() - 20, 20)
        
        # Animación de entrada (desde fuera de la pantalla)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        start_rect = QRect(parent_rect.width(), 20, self.width(), self.height())
        end_rect = QRect(parent_rect.width() - self.width() - 20, 20, self.width(), self.height())
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        
        self.show()
        self.animation.start()
    
    def hide_animated(self):
        """Ocultar con animación de deslizamiento"""
        if not self.parent():
            self.hide()
            return
        
        # Animación de salida (hacia fuera de la pantalla)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        current_rect = self.geometry()
        end_rect = QRect(self.parent().width(), current_rect.y(), current_rect.width(), current_rect.height())
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self.hide)
        self.animation.finished.connect(self.closed.emit)
        
        self.animation.start()


class LoadingOverlay(QWidget):
    """
    Overlay de carga que cubre todo el widget padre.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner
        self.spinner = AnimatedSpinner(self, theme_manager)
        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje
        self.message_label = QLabel("Cargando...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Aplicar tema
        self._apply_theme()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Inicialmente oculto
        self.hide()
    
    def _apply_theme(self):
        """Aplicar estilos del tema actual"""
        colors = self._get_theme_colors()
        
        # Overlay semi-transparente
        overlay_color = QColor(colors.overlay.replace('rgba', '').replace('(', '').replace(')', '').replace(' ', ''))
        if overlay_color.isValid():
            bg_color = f"rgba({overlay_color.red()}, {overlay_color.green()}, {overlay_color.blue()}, 0.8)"
        else:
            bg_color = "rgba(0, 0, 0, 0.5)"
        
        style = f"""
            QWidget {{
                background-color: {bg_color};
            }}
            QLabel {{
                color: {colors.on_primary};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 10px;
            }}
        """
        
        self.setStyleSheet(style)
    
    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            return get_theme("light")
    
    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema"""
        self._apply_theme()
    
    def show_loading(self, message: str = "Cargando..."):
        """Mostrar overlay de carga"""
        self.message_label.setText(message)
        
        # Ajustar tamaño al widget padre
        if self.parent():
            self.resize(self.parent().size())
        
        self.spinner.start()
        self.show()
        self.raise_()  # Traer al frente
        
        logger.debug(f"Loading overlay mostrado: {message}")
    
    def hide_loading(self):
        """Ocultar overlay de carga"""
        self.spinner.stop()
        self.hide()
        
        logger.debug("Loading overlay ocultado")
    
    def resizeEvent(self, event):
        """Ajustar tamaño cuando cambia el padre"""
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())


class StatusIndicator(QLabel):
    """
    Indicador de estado en tiempo real (punto coloreado + texto).
    """
    
    def __init__(self, parent: Optional[QWidget] = None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.current_status = "inactive"
        
        # Configuración inicial
        self.setFixedHeight(20)
        
        # Aplicar tema
        self._apply_theme()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_theme(self):
        """Aplicar estilos del tema actual"""
        colors = self._get_theme_colors()
        
        # Mapeo de estados a colores
        status_colors = {
            "active": colors.success,
            "warning": colors.warning,
            "error": colors.error,
            "inactive": colors.on_surface_variant
        }
        
        color = status_colors.get(self.current_status, colors.on_surface_variant)
        
        style = f"""
            QLabel {{
                color: {colors.on_surface};
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 2px 5px;
            }}
        """
        
        self.setStyleSheet(style)
    
    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            return get_theme("light")
    
    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema"""
        self._apply_theme()
    
    def set_status(self, status: str, message: str = ""):
        """
        Actualizar estado del indicador.
        
        Args:
            status: Estado ('active', 'warning', 'error', 'inactive')
            message: Mensaje descriptivo
        """
        self.current_status = status
        
        # Iconos por estado
        status_icons = {
            "active": "🟢",
            "warning": "🟡", 
            "error": "🔴",
            "inactive": "⚫"
        }
        
        icon = status_icons.get(status, "⚫")
        text = f"{icon} {message}" if message else icon
        
        self.setText(text)
        self._apply_theme()
        
        logger.debug(f"Status indicator actualizado: {status} - {message}")


# Funciones de conveniencia para crear componentes

def create_spinner(parent: QWidget, theme_manager: Optional[ThemeManager] = None) -> AnimatedSpinner:
    """Crear un spinner animado"""
    return AnimatedSpinner(parent, theme_manager)

def create_progress_bar(parent: QWidget, theme_manager: Optional[ThemeManager] = None) -> ThemedProgressBar:
    """Crear una progress bar temática"""
    return ThemedProgressBar(parent, theme_manager)

def create_toast(parent: QWidget, theme_manager: Optional[ThemeManager] = None) -> ToastNotification:
    """Crear una notificación toast"""
    return ToastNotification(parent, theme_manager)

def create_loading_overlay(parent: QWidget, theme_manager: Optional[ThemeManager] = None) -> LoadingOverlay:
    """Crear un overlay de carga"""
    return LoadingOverlay(parent, theme_manager)

def create_status_indicator(parent: QWidget, theme_manager: Optional[ThemeManager] = None) -> StatusIndicator:
    """Crear un indicador de estado"""
    return StatusIndicator(parent, theme_manager)