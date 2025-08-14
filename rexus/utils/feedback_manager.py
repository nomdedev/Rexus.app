"""
Sistema de Feedback Visual Centralizado - Rexus.app
Versión: 2.0.0 - Enterprise Ready

Sistema centralizado para mostrar mensajes de feedback visual
integrado con el sistema de temas de la aplicación.
"""

from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox, QWidget, QLabel

from ..core.themes import get_theme, ColorPalette
from ..utils.theme_manager import ThemeManager
from ..core.logger import get_logger

logger = get_logger("feedback_manager")


class FeedbackManager(QObject):
    """
    Gestor centralizado de feedback visual que se integra con el sistema de temas.
    Proporciona mensajes consistentes en toda la aplicación.
    """

    # Señales para notificar eventos
    message_shown = pyqtSignal(str, str, str)  # titulo, mensaje, tipo
    message_hidden = pyqtSignal()

    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        super().__init__()
        self.logger = get_logger("feedback_manager")
        self.theme_manager = theme_manager

        # Cache de estilos
        self._style_cache: Dict[str, str] = {}

        # Conectar con el tema manager si existe
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)

        self.logger.info("FeedbackManager inicializado")

    def _on_theme_changed(self,
theme_name: str,
        theme_colors: Dict[str,
        str]):
        """Callback cuando cambia el tema - limpiar cache de estilos"""
        self._style_cache.clear()
        self.logger.debug(f"Cache de estilos limpiado - nuevo tema: {theme_name}")

    def _get_theme_colors(self) -> ColorPalette:
        """Obtener colores del tema actual"""
        if self.theme_manager:
            return self.theme_manager.current_theme
        else:
            # Fallback al tema por defecto
            return get_theme("light")

    def _generate_message_style(self, tipo: str) -> str:
        """Generar estilo CSS para un tipo de mensaje específico"""

        # Verificar cache
        cache_key = f"{tipo}_{getattr(self.theme_manager, 'current_theme_name', 'light')}"
        if cache_key in self._style_cache:
            return self._style_cache[cache_key]

        colors = self._get_theme_colors()

        # Mapeo de tipos a colores del tema
        type_colors = {
            "info": {
                "bg": colors.info,
                "text": colors.on_primary,
                "border": colors.border_focus,
                "hover": colors.button_hover
            },
            "success": {
                "bg": colors.success,
                "text": colors.on_primary,
                "border": colors.success,
                "hover": self._darken_color(colors.success)
            },
            "warning": {
                "bg": colors.warning,
                "text": colors.on_primary,
                "border": colors.warning,
                "hover": self._darken_color(colors.warning)
            },
            "error": {
                "bg": colors.error,
                "text": colors.on_primary,
                "border": colors.error,
                "hover": self._darken_color(colors.error)
            }
        }

        # Colores por defecto si el tipo no existe
        color_set = type_colors.get(tipo, type_colors["info"])

        style = f"""
            QMessageBox {{
                background-color: {colors.surface};
                color: {colors.on_surface};
                border: 2px solid {color_set['border']};
                border-radius: 8px;
                font-size: 12px;
                padding: 16px;
            }}
            QMessageBox QLabel {{
                color: {colors.on_surface};
                font-weight: 500;
                padding: 8px;
            }}
            QMessageBox QPushButton {{
                background-color: {color_set['bg']};
                color: {color_set['text']};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {color_set['hover']};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {self._darken_color(color_set['hover'])};
            }}
            QMessageBox QIcon {{
                padding: 8px;
            }}
        """

        # Guardar en cache
        self._style_cache[cache_key] = style
        return style

    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """Oscurecer un color hexadecimal"""
        if not color.startswith('#'):
            return color

        try:
            # Convertir hex a RGB
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

            # Aplicar factor de oscurecimiento
            darkened = tuple(max(0, int(c * factor)) for c in rgb)

            # Convertir de vuelta a hex
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except (ValueError, IndexError):
            return color

    def show_message(self,
parent: QWidget,
        titulo: str,
        mensaje: str,
        tipo: str = "info") -> int:
        """
        Mostrar mensaje de feedback visual integrado con el tema actual.

        Args:
            parent: Widget padre para el mensaje
            titulo: Título del mensaje
            mensaje: Contenido del mensaje
            tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')

        Returns:
            Código de respuesta del diálogo
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(titulo)
            msg_box.setText(mensaje)

            # Configurar icono según el tipo
            icons = {
                "info": QMessageBox.Icon.Information,
                "success": QMessageBox.Icon.Information,
                "warning": QMessageBox.Icon.Warning,
                "error": QMessageBox.Icon.Critical
            }

            msg_box.setIcon(icons.get(tipo, QMessageBox.Icon.Information))

            # Aplicar estilo del tema
            style = self._generate_message_style(tipo)
            msg_box.setStyleSheet(style)

            # Configurar botones
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            # Emitir señal
            self.message_shown.emit(titulo, mensaje, tipo)

            # Log del evento
            self.logger.debug(f"Mensaje mostrado: {tipo} - {titulo}", extra={
                "message": mensaje,
                "parent": parent.__class__.__name__ if parent else "None"
            })

            result = msg_box.exec()

            self.message_hidden.emit()
            return result

        except Exception as e:
            self.logger.error(f"Error mostrando mensaje de feedback: {e}", extra={
                "titulo": titulo,
                "mensaje": mensaje,
                "tipo": tipo
            })

            # Fallback a mensaje básico
            QMessageBox.information(parent, titulo, mensaje)
            return QMessageBox.StandardButton.Ok

    def show_confirmation(self, parent: QWidget, titulo: str, mensaje: str,
                         botones: QMessageBox.StandardButton = None) -> int:
        """
        Mostrar diálogo de confirmación integrado con el tema.

        Args:
            parent: Widget padre
            titulo: Título del diálogo
            mensaje: Mensaje de confirmación
            botones: Botones a mostrar (por defecto Yes/No)

        Returns:
            Botón presionado por el usuario
        """
        try:
            if botones is None:
                botones = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No

            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(titulo)
            msg_box.setText(mensaje)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(botones)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            # Aplicar estilo del tema
            style = self._generate_message_style("info")
            msg_box.setStyleSheet(style)

            self.logger.debug(f"Confirmación mostrada: {titulo}")

            result = msg_box.exec()
            return result

        except Exception as e:
            self.logger.error(f"Error mostrando confirmación: {e}")
            return QMessageBox.question(parent, titulo, mensaje, botones)

    def create_status_label(self, parent: QWidget) -> QLabel:
        """
        Crear un label de estado integrado con el tema para feedback inline.

        Args:
            parent: Widget padre

        Returns:
            QLabel configurado con estilos del tema
        """
        colors = self._get_theme_colors()

        label = QLabel(parent)
        label.setVisible(False)

        # Estilo base integrado con el tema
        base_style = f"""
            QLabel {{
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 500;
                font-size: 11px;
                border: 1px solid transparent;
                background-color: {colors.surface_variant};
                color: {colors.on_surface_variant};
            }}
        """

        # Estilos específicos por tipo (se aplicarán dinámicamente)
        type_styles = {
            "info": f"""
                background-color: {colors.info}20;
                color: {colors.info};
                border-color: {colors.info}40;
            """,
            "success": f"""
                background-color: {colors.success}20;
                color: {colors.success};
                border-color: {colors.success}40;
            """,
            "warning": f"""
                background-color: {colors.warning}20;
                color: {colors.warning};
                border-color: {colors.warning}40;
            """,
            "error": f"""
                background-color: {colors.error}20;
                color: {colors.error};
                border-color: {colors.error}40;
            """
        }

        # Almacenar estilos en propiedades del widget para uso posterior
        label.setProperty("base_style", base_style)
        label.setProperty("type_styles", type_styles)

        label.setStyleSheet(base_style)

        return label

    def show_status_message(self, status_label: QLabel, mensaje: str,
                          tipo: str = "info", duration: int = 3000):
        """
        Mostrar mensaje en un status label temporal.

        Args:
            status_label: Label de estado creado con create_status_label
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje
            duration: Duración en ms (0 = permanente)
        """
        try:
            # Iconos para cada tipo
            icons = {
                "info": "ℹ️",
                "success": "[CHECK]",
                "warning": "[WARN]",
                "error": "[ERROR]"
            }

            icon = icons.get(tipo, "ℹ️")
            status_label.setText(f"{icon} {mensaje}")

            # Aplicar estilo específico del tipo
            base_style = status_label.property("base_style") or ""
            type_styles = status_label.property("type_styles") or {}
            type_style = type_styles.get(tipo, "")

            status_label.setStyleSheet(base_style + type_style)
            status_label.setVisible(True)

            # Auto-ocultar si se especifica duración
            if duration > 0:
                QTimer.singleShot(duration, lambda: status_label.setVisible(False))

            self.logger.debug(f"Status mostrado: {tipo} - {mensaje}")

        except Exception as e:
            self.logger.error(f"Error mostrando status: {e}")


# Instancia global singleton
_feedback_manager: Optional[FeedbackManager] = None

def get_feedback_manager(theme_manager: Optional[ThemeManager] = None) -> FeedbackManager:
    """Obtener la instancia global del FeedbackManager"""
    global _feedback_manager
    if _feedback_manager is None:
        _feedback_manager = FeedbackManager(theme_manager)
    return _feedback_manager

def show_message(parent: QWidget,
titulo: str,
    mensaje: str,
    tipo: str = "info") -> int:
    """Función de conveniencia para mostrar mensajes"""
    fm = get_feedback_manager()
    return fm.show_message(parent, titulo, mensaje, tipo)

def show_confirmation(parent: QWidget, titulo: str, mensaje: str) -> int:
    """Función de conveniencia para mostrar confirmaciones"""
    fm = get_feedback_manager()
    return fm.show_confirmation(parent, titulo, mensaje)
