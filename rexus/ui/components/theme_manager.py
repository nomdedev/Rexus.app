"""
Rexus.app - Theme Manager

Gestor de temas y estilos de la aplicación.
Maneja los temas claro/oscuro y personalización de colores.
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from rexus.utils.app_logger import log_info


class ThemeManager(QObject):
    """
    Gestor de temas para la aplicación.
    Maneja el cambio entre temas claro y oscuro.
    """

    theme_changed = pyqtSignal(str)  # Señal emitida cuando cambia el tema

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "light"
        self.themes = self._load_themes()

    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Carga la configuración de temas disponibles."""
        return {
            "light": {
                "name": "Claro",
                "colors": {
                    "primary": "#3498db",
                    "secondary": "#2c3e50",
                    "background": "#ecf0f1",
                    "surface": "#ffffff",
                    "text": "#2c3e50",
                    "text_secondary": "#7f8c8d",
                    "border": "#bdc3c7",
                    "hover": "#f8f9fa",
                    "selected": "#e3f2fd"
                }
            },
            "dark": {
                "name": "Oscuro",
                "colors": {
                    "primary": "#64b5f6",
                    "secondary": "#ffffff",
                    "background": "#121212",
                    "surface": "#1e1e1e",
                    "text": "#ffffff",
                    "text_secondary": "#b0b0b0",
                    "border": "#333333",
                    "hover": "#2a2a2a",
                    "selected": "#1a237e"
                }
            }
        }

    def set_theme(self, theme_name: str) -> bool:
        """
        Establece el tema actual.

        Args:
            theme_name: Nombre del tema ('light' o 'dark')

        Returns:
            True si el tema se cambió exitosamente
        """
        if theme_name not in self.themes:
            log_info(f"Tema no encontrado: {theme_name}", "theme_manager")
            return False

        if theme_name != self.current_theme:
            self.current_theme = theme_name
            self._apply_theme()
            self.theme_changed.emit(theme_name)
            log_info(f"Tema cambiado a: {theme_name}", "theme_manager")
            return True

        return False

    def _apply_theme(self):
        """Aplica el tema actual a la aplicación."""
        theme = self.themes[self.current_theme]

        # Aplicar estilos CSS a la aplicación
        app = QApplication.instance()
        if app:
            # Aquí se aplicaría el CSS, pero por simplicidad lo omitimos
            log_info(f"Estilos del tema {theme['name']} preparados", "theme_manager")

    def _adjust_color(self, color: str, amount: int) -> str:
        """Ajusta el brillo de un color hexadecimal."""
        # Implementación simplificada
        if amount > 0:
            return color  # Más claro
        else:
            return color  # Más oscuro

    def get_current_theme(self) -> str:
        """Obtiene el nombre del tema actual."""
        return self.current_theme

    def get_theme_colors(self) -> Dict[str, str]:
        """Obtiene los colores del tema actual."""
        return self.themes[self.current_theme]["colors"]

    def toggle_theme(self) -> str:
        """
        Alterna entre tema claro y oscuro.

        Returns:
            Nombre del nuevo tema
        """
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
        return new_theme

    def apply_theme(self, theme_name: Optional[str] = None):
        """
        Aplica un tema específico o el tema actual.

        Args:
            theme_name: Nombre del tema a aplicar (opcional)
        """
        if theme_name:
            self.set_theme(theme_name)
        else:
            self._apply_theme()


# Instancia global del gestor de temas
theme_manager = ThemeManager()
