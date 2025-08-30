"""
Rexus.app - Style Manager

Gestor de estilos y temas visuales de la aplicación.
Centraliza la gestión de colores, fuentes y estilos CSS.
"""

from typing import Dict, Any
from PyQt6.QtWidgets import QApplication

from rexus.utils.app_logger import log_info


class StyleManager:
    """
    Gestor de estilos para la aplicación.
    Maneja temas, colores y estilos CSS globales.
    """

    def __init__(self):
        self._current_theme = "default"
        self._themes = self._load_styles()

    def apply_global_theme(self) -> bool:
        """
        Aplica el tema global a la aplicación.

        Returns:
            True si se aplicó exitosamente
        """
        try:
            self.apply_stylesheet("global")
            log_info(f"Tema global aplicado: {self._current_theme}", "style_manager")
            return True
        except OSError as e:
            log_info(f"Error aplicando tema global: {e}", "style_manager")
            return False

    def apply_emergency_readable_forms(self) -> bool:
        """
        Aplica estilos de emergencia para formularios legibles.

        Returns:
            True si se aplicó exitosamente
        """
        try:
            emergency_css = """
            QLineEdit, QTextEdit, QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                font-size: 12px;
            }
            QLabel {
                color: black;
            }
            """
            app = QApplication.instance()
            if app:
                current_css = getattr(app, 'styleSheet', lambda: "")()
                setattr(app, 'styleSheet', current_css + emergency_css)
            log_info("Estilos de emergencia aplicados", "style_manager")
            return True
        except Exception as e:
            log_info(f"Error aplicando estilos de emergencia: {e}", "style_manager")
            return False

    def apply_critical_form_fixes(self) -> bool:
        """
        Aplica correcciones críticas para formularios.

        Returns:
            True si se aplicó exitosamente
        """
        return self.apply_emergency_readable_forms()

    def force_light_theme_for_forms(self) -> bool:
        """
        Fuerza tema claro para formularios.

        Returns:
            True si se aplicó exitosamente
        """
        try:
            light_css = """
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #ced4da;
            }
            """
            app = QApplication.instance()
            if app:
                current_css = getattr(app, 'styleSheet', lambda: "")()
                setattr(app, 'styleSheet', current_css + light_css)
            log_info("Tema claro forzado para formularios", "style_manager")
            return True
        except Exception as e:
            log_info(f"Error forzando tema claro: {e}", "style_manager")
            return False

    def _load_styles(self) -> Dict[str, Dict[str, Any]]:
        """Carga los estilos disponibles."""
        return {
            "default": {
                "name": "Predeterminado",
                "colors": {
                    "primary": "#3498db",
                    "secondary": "#2c3e50",
                    "success": "#27ae60",
                    "warning": "#f39c12",
                    "danger": "#e74c3c",
                    "info": "#17a2b8",
                    "light": "#f8f9fa",
                    "dark": "#343a40"
                },
                "fonts": {
                    "default": "Arial",
                    "heading": "Arial",
                    "mono": "Consolas"
                }
            }
        }

    def get_stylesheet(self, component: str = "global") -> str:
        """
        Obtiene el CSS para un componente específico.

        Args:
            component: Nombre del componente

        Returns:
            CSS del componente
        """
        theme = self._themes[self._current_theme]

        if component == "button":
            return f"""
            QPushButton {{
                background-color: {theme['colors']['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-family: {theme['fonts']['default']};
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
            """

        elif component == "input":
            return f"""
            QLineEdit {{
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: {theme['fonts']['default']};
            }}
            QLineEdit:focus {{
                border-color: {theme['colors']['primary']};
            }}
            """

        else:  # global
            return f"""
            QWidget {{
                font-family: {theme['fonts']['default']};
                color: {theme['colors']['secondary']};
            }}

            QLabel {{
                color: {theme['colors']['secondary']};
            }}

            QFrame {{
                background-color: white;
                border: 1px solid #e1e8ed;
            }}
            """

    def apply_stylesheet(self, component: str = "global"):
        """
        Aplica los estilos a la aplicación.

        Args:
            component: Componente al que aplicar los estilos
        """
        css = self.get_stylesheet(component)
        app = QApplication.instance()
        if app and hasattr(app, 'setStyleSheet'):
            try:
                current_css = getattr(app, 'styleSheet', lambda: "")()
                getattr(app, 'setStyleSheet')(current_css + css)
                log_info(f"Estilos aplicados para componente: {component}", "style_manager")
            except Exception as e:
                log_info(f"No se pudieron aplicar estilos para: {component} - {e}", "style_manager")

    def get_color(self, color_name: str) -> str:
        """
        Obtiene un color del tema actual.

        Args:
            color_name: Nombre del color

        Returns:
            Código hexadecimal del color
        """
        theme = self._themes[self._current_theme]
        return theme['colors'].get(color_name, "#000000")

    def get_font(self, font_name: str) -> str:
        """
        Obtiene una fuente del tema actual.

        Args:
            font_name: Nombre de la fuente

        Returns:
            Nombre de la fuente
        """
        theme = self._themes[self._current_theme]
        return theme['fonts'].get(font_name, "Arial")


# Instancia global del gestor de estilos
style_manager = StyleManager()
