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

Gestor de Estilos Centralizado para Rexus.app
Proporciona gestión consistente de estilos y temas para toda la aplicación.
"""

import logging
from pathlib import Path
from typing import Dict

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger
logger = get_logger()

from PyQt6.QtWidgets import QApplication, QWidget


class StyleManager:
    """Gestor centralizado de estilos y temas para la aplicación."""

    _instance = None
    _current_theme = 'unified'
    _themes_path = Path('resources/qss')

    # Mapa de temas disponibles a archivos QSS
    AVAILABLE_THEMES = {
        'professional': 'professional_theme_clean.qss',
        'light': 'theme_light_contrast_fixed.qss',  # CORREGIDO: Contraste alto optimizado
        'light_original': 'theme_light_clean.qss',  # Respaldo del original
        'dark': 'theme_dark_contrast_fixed.qss',  # CORREGIDO: Contraste forzado para legibilidad
        'dark_original': 'theme_dark_clean.qss',  # Respaldo del original
        'minimal': 'theme_light_minimal_clean.qss',
        'optimized': 'theme_optimized_clean.qss',
        'consolidated': 'consolidated_theme_clean.qss',
        'unified': 'unified_module_styles.qss'  # Nuevo estilo unificado
    }

    # Mapa de estilos específicos por módulo
    MODULE_STYLES = {
        'inventario': 'inventario.qss',
        'administracion': 'administracion.qss',
        'obras': 'obras.qss',
        'usuarios': 'usuarios.qss'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._loaded_themes: Dict[str, str] = {}
            self._auto_apply_dark_fixes = False
            self._load_available_themes()
            self._detect_system_theme()

            # APLICAR CORRECCIONES AUTOMÁTICAMENTE si se detectó tema oscuro
            if hasattr(self, '_auto_apply_dark_fixes') and \
                self._auto_apply_dark_fixes:
                logger.info("[STYLE] Aplicando correcciones criticas automaticas para tema oscuro")
                self._apply_automatic_dark_fixes()

    def _detect_system_theme(self):
        """
        Detecta si el sistema está en modo oscuro y ajusta el tema por defecto.
        Funciona en Windows 10/11, macOS y algunos Linux.
        """
        try:
            import platform
            system = platform.system().lower()

            if system == "windows":
                self._detect_windows_theme()
            elif system == "darwin":  # macOS
                self._detect_macos_theme()
            else:  # Linux y otros
                self._detect_linux_theme()

        except (OSError, ImportError, AttributeError, RuntimeError) as e:
            logger.warning(f"Error detectando tema del sistema: {e}")
            self._current_theme = 'professional'
            logger.info("[STYLE] Usando tema por defecto 'professional' por error")

    def _detect_windows_theme(self):
        """Detecta tema en Windows."""
        try:
            import winreg

            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)

            # AppsUseLightTheme: 0 = dark mode, 1 = light mode
            apps_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)

            if apps_light_theme == 0:  # Dark mode
                self._current_theme = 'dark'
                logger.info("[STYLE] Tema oscuro detectado en Windows - aplicando correcciones criticas")
                logger.info("[STYLE] Aplicando correcciones criticas automaticas para tema oscuro")
                # APLICAR INMEDIATAMENTE las correcciones críticas para tema oscuro
                self._auto_apply_dark_fixes = True
                self._apply_critical_dark_theme_fixes()
            else:  # Light mode
                self._current_theme = 'light'
                logger.info("[STYLE] Tema claro detectado en Windows - aplicando tema optimizado")
                self._auto_apply_dark_fixes = False

        except (FileNotFoundError, OSError, ImportError):
            self._current_theme = 'professional'
            self._auto_apply_dark_fixes = False
            logger.info("[STYLE] WARNING: No se pudo detectar tema de Windows - usando 'professional'")

    def _detect_macos_theme(self):
        """Detecta tema en macOS."""
        try:
            import subprocess
            result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                                  capture_output=True, text=True)

            if result.returncode == 0 and 'Dark' in result.stdout:
                self._current_theme = 'dark'
                self._auto_apply_dark_fixes = True
                logger.info("[STYLE] [DARK] Tema oscuro detectado en macOS - aplicando correcciones críticas")
            else:
                self._current_theme = 'light'
                self._auto_apply_dark_fixes = False
                logger.info("[STYLE] [LIGHT] Tema claro detectado en macOS - aplicando 'light'")

        except (subprocess.CalledProcessError, FileNotFoundError):
            self._current_theme = 'professional'
            self._auto_apply_dark_fixes = False
            logger.info("[STYLE] [WARNING] No se pudo detectar tema de macOS - usando 'professional'")

    def _detect_linux_theme(self):
        """Detecta tema en Linux (GNOME/KDE)."""
        try:
            import subprocess
            import os

            # Intentar GNOME primero
            if os.environ.get('GNOME_DESKTOP_SESSION_ID') or os.environ.get('XDG_CURRENT_DESKTOP') == 'GNOME':
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and ('dark' in result.stdout.lower() or 'adwaita-dark' in result.stdout.lower()):
                    self._current_theme = 'dark'
                    self._auto_apply_dark_fixes = True
                    logger.info("[STYLE] [DARK] Tema oscuro detectado en GNOME - aplicando correcciones críticas")
                    return

            # Intentar KDE
            elif os.environ.get('KDE_SESSION_VERSION'):
                # KDE usa archivos de configuración
                kde_config = os.path.expanduser('~/.config/kdeglobals')
                if os.path.exists(kde_config):
                    with open(kde_config, 'r') as f:
                        content = f.read()
                        if 'ColorScheme=Breeze Dark' in content or 'ColorScheme=BreezeDark' in content:
                            self._current_theme = 'dark'
                            self._auto_apply_dark_fixes = True
                            logger.info("[STYLE] [DARK] Tema oscuro detectado en KDE - aplicando correcciones críticas")
                            return

            # Si llegamos aquí, usar tema claro por defecto en Linux
            self._current_theme = 'light'
            self._auto_apply_dark_fixes = False
            logger.info("[STYLE] [LIGHT] Usando tema claro por defecto en Linux")

        except (OSError, ImportError, AttributeError, RuntimeError):
            self._current_theme = 'professional'
            self._auto_apply_dark_fixes = False
            logger.info("[STYLE] [WARNING] No se pudo detectar tema de Linux - usando 'professional'")

    def _load_available_themes(self):
        """Carga todos los temas disponibles en memoria."""
        for theme_name, filename in self.AVAILABLE_THEMES.items():
            theme_path = self._themes_path / filename

            if theme_path.exists():
                try:
                    with open(theme_path, 'r', encoding='utf-8') as f:
                        self._loaded_themes[theme_name] = f.read()
                    logging.debug(f"Tema '{theme_name}' cargado exitosamente")
                except (IOError, OSError, FileNotFoundError, UnicodeDecodeError) as e:
                    logging.error(f"Error cargando tema '{theme_name}': {e}")
            else:
                logging.warning(f"Archivo de tema no encontrado: {theme_path}")

    def apply_global_theme(self, theme_name: str = None) -> bool:
        """Aplica un tema global a toda la aplicación sin modificaciones invasivas."""
        if theme_name is None:
            theme_name = self._current_theme

        if theme_name not in self._loaded_themes:
            logging.error(f"Tema '{theme_name}' no disponible")
            # Si el tema solicitado no existe, intentar con el tema por defecto
            if 'professional' in self._loaded_themes:
                theme_name = 'professional'
                print(f"[STYLE] Usando tema por defecto 'professional' en lugar de '{theme_name}'")
            else:
                return False

        try:
            app = QApplication.instance()
            if app:
                # Aplicar solo los estilos base del archivo QSS sin modificaciones
                base_styles = self._loaded_themes[theme_name]

                app.setStyleSheet(base_styles)
                self._current_theme = theme_name

                # SOLUCIÓN CRÍTICA: Aplicar correcciones de contraste automáticamente para tema oscuro
                if 'dark' in theme_name.lower():
                    print(f"[STYLE] [DARK] Detectado tema oscuro '{theme_name}' - aplicando correcciones críticas automáticas")
                    critical_success = self.apply_critical_contrast_fixes()
                    if not critical_success:
                        logger.info("[STYLE] [WARNING] Aplicando tema claro de emergencia por problemas de contraste")
                        self.force_light_theme_for_forms()

                logging.debug(f"Tema global '{theme_name}' aplicado exitosamente")
                print(f"[STYLE] Tema aplicado: {theme_name}")
                return True
            else:
                logging.error("No se pudo obtener instancia de QApplication")
                return False

        except (AttributeError, RuntimeError, OSError) as e:
            logging.error(f"Error aplicando tema global '{theme_name}': {e}")
            return False

    def apply_unified_module_style(self, widget: QWidget):
        """Aplica el estilo unificado basado en Logística a cualquier widget/módulo."""
        try:
            if not widget:
                return

            # Leer el archivo de estilos unificados
            unified_style_path = self._themes_path / 'unified_module_styles.qss'
            if unified_style_path.exists():
                with open(unified_style_path, 'r', encoding='utf-8') as file:
                    unified_styles = file.read()

                # Aplicar estilos al widget
                widget.setStyleSheet(unified_styles)
                logging.debug(f"Estilos unificados aplicados a {widget.__class__.__name__}")
                return True
            else:
                logging.warning("Archivo de estilos unificados no encontrado")
                return False

        except (IOError, OSError, FileNotFoundError, UnicodeDecodeError, AttributeError) as e:
            logging.error(f"Error aplicando estilos unificados: {e}")
            return False

    def get_module_styles(self) -> str:
        """Retorna estilos específicos para módulos."""
        return """
            /* Estilos específicos para módulos de Rexus */
            QWidget[moduleView="true"] {
                background: #fafbfc;
                border: none;
                font-size: 11px;
            }

            /* Títulos de módulo estándar */
            QLabel[moduleTitle="true"] {
                font-size: 11px;
                font-weight: bold;
                color: white;
                background: transparent;
                border: none;
                padding: 0px;
            }

            /* Paneles de control estándar */
            QFrame[controlPanel="true"] {
                background: #fafbfc;
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                margin: 4px;
                padding: 6px;
            }

            /* Botones de acción principales */
            QPushButton[actionButton="primary"] {
                background: #1e40af;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-height: 36px;
            }

            QPushButton[actionButton="primary"]:hover {
                background: #3b82f6;
                /* transform no soportado en Qt - removido */
            }

            QPushButton[actionButton="primary"]:pressed {
                background: #1e3a8a;
                /* transform no soportado en Qt - removido */
            }

            /* Botones secundarios */
            QPushButton[actionButton="secondary"] {
                background: white;
                color: #1e293b;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-height: 36px;
            }

            QPushButton[actionButton="secondary"]:hover {
                border-color: #1e40af;
                color: #1e40af;
                background: #f8fafc;
            }

            /* Botones de peligro */
            QPushButton[actionButton="danger"] {
                background: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-height: 36px;
            }

            QPushButton[actionButton="danger"]:hover {
                background: #b91c1c;
                /* transform no soportado en Qt - removido */
            }

            /* Tablas estándard */
            QTableWidget[standardTable="true"] {
                background-color: white;
                alternate-background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                font-size: 13px;
            }

            QTableWidget[standardTable="true"]::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
            }

            QTableWidget[standardTable="true"]::item:selected {
                background: #3b82f6;
                color: white;
            }

            QHeaderView::section[standardTable="true"] {
                background: #1e40af;
                color: white;
                padding: 12px 8px;
                border: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 13px;
            }

            QHeaderView::section[standardTable="true"]:hover {
                background: #3b82f6;
            }
        """

    def apply_module_theme(self, widget: QWidget, module_name: str = None) -> bool:
        """Aplica tema específico a un módulo."""
        try:
            # Aplicar propiedades para identificación
            widget.setProperty("moduleView", True)

            # Aplicar estilos del módulo base
            current_style = widget.styleSheet()
            module_styles = self.get_module_styles()

            # Cargar estilos específicos del módulo si existe
            specific_styles = ""
            if module_name and module_name in self.MODULE_STYLES:
                specific_styles = self.load_module_stylesheet(module_name)

            # Combinar todos los estilos
            combined_style = f"{current_style}\n{module_styles}\n{specific_styles}"
            widget.setStyleSheet(combined_style)

            # Forzar actualización de estilos
            widget.style().unpolish(widget)
            widget.style().polish(widget)

            logging.debug(f"Tema de módulo aplicado a {widget.__class__.__name__} ({module_name})")
            return True

        except (AttributeError, RuntimeError, OSError, IOError) as e:
            logging.error(f"Error aplicando tema a módulo: {e}")
            return False

    def apply_theme(self, widget: QWidget, theme_name: str = None) -> bool:
        """
        Aplica un tema específico a un widget.

        Args:
            widget: Widget al que aplicar el tema
            theme_name: Nombre del tema (si es None, usa el tema actual)
        """
        try:
            if theme_name is None:
                theme_name = self._current_theme

            # Si el tema no existe, usar el módulo
            if theme_name not in self._loaded_themes:
                return self.apply_module_theme(widget, theme_name)

            # Aplicar el tema específico
            widget.setStyleSheet(self._loaded_themes[theme_name])

            # Forzar actualización
            widget.style().unpolish(widget)
            widget.style().polish(widget)

            return True

        except (AttributeError, RuntimeError, OSError, IOError) as e:
            print(f"[WARNING] Error aplicando tema '{theme_name}': {e}")
            return False

    def apply_critical_contrast_fixes(self, widget: QWidget = None) -> bool:
        """
        Aplica correcciones críticas de contraste para resolver formularios negros.
        SOLUCIÓN PARA: QLineEdit, QTextEdit, QComboBox ilegibles con tema oscuro.

        Args:
            widget: Widget específico o None para aplicar globalmente
        """
        try:
            # Estilos críticos que SIEMPRE deben ser aplicados para legibilidad
            critical_styles = """
            /* CORRECCIÓN CRÍTICA: Formularios legibles con tema oscuro */
            QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {
                background-color: #1e293b !important;
                border: 2px solid #475569 !important;
                border-radius: 6px !important;
                color: #f1f5f9 !important;
                font-size: 14px !important;
                padding: 8px 12px !important;
                min-height: 18px !important;
            }

            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                background-color: #334155 !important;
                border: 2px solid #60a5fa !important;
                color: #ffffff !important;
            }

            QLineEdit:disabled, QComboBox:disabled, QTextEdit:disabled {
                background-color: #374151 !important;
                border: 2px solid #6b7280 !important;
                color: #9ca3af !important;
            }

            /* Corrección ComboBox dropdown */
            QComboBox QAbstractItemView {
                background-color: #1e293b !important;
                border: 2px solid #475569 !important;
                color: #f1f5f9 !important;
                selection-background-color: #3b82f6 !important;
                selection-color: #ffffff !important;
            }

            /* Corrección botones críticos */
            QPushButton {
                background-color: #1e40af !important;
                color: #ffffff !important;
                border: 1px solid #3b82f6 !important;
                border-radius: 6px !important;
                min-height: 32px !important;
                padding: 8px 16px !important;
            }

            QPushButton:hover {
                background-color: #2563eb !important;
            }

            /* Corrección labels */
            QLabel {
                color: #e2e8f0 !important;
            }
            """

            if widget:
                # Aplicar a widget específico
                current_style = widget.styleSheet()
                widget.setStyleSheet(current_style + critical_styles)
                print(f"[STYLE] Correcciones críticas aplicadas a {widget.__class__.__name__}")
            else:
                # Aplicar globalmente
                app = QApplication.instance()
                if app:
                    current_style = app.styleSheet()
                    app.setStyleSheet(current_style + critical_styles)
                    logger.info("[STYLE] Correcciones críticas de contraste aplicadas globalmente")

            return True

        except (AttributeError, RuntimeError, OSError) as e:
            logger.error(f"Error aplicando correcciones críticas: {e}")
            return False

    def load_module_stylesheet(self, module_name: str) -> str:
        """Carga hoja de estilos específica de un módulo."""
        try:
            if module_name not in self.MODULE_STYLES:
                return ""

            stylesheet_path = self._themes_path / self.MODULE_STYLES[module_name]

            if stylesheet_path.exists():
                with open(stylesheet_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                logging.warning(f"Archivo de estilos no encontrado: {stylesheet_path}")
                return ""

        except (IOError, OSError, FileNotFoundError, UnicodeDecodeError) as e:
            logging.error(f"Error cargando estilos del módulo {module_name}: {e}")
            return ""

    def apply_stats_panel_theme(self, panel_widget):
        """Aplica tema específico a paneles de estadísticas."""
        panel_widget.setObjectName("panel_estadisticas")

    def apply_stat_card_theme(self, card_widget, color_class):
        """Aplica tema a tarjetas de estadísticas individuales."""
        card_widget.setProperty("class", "stat-widget")
        if color_class:
            card_widget.setProperty("colorType", color_class)

    def apply_table_theme(self, table_widget, module_name: str):
        """Aplica tema específico a tablas."""
        table_widget.setObjectName(f"tabla_{module_name}")
        table_widget.setProperty("standardTable", True)

    def apply_input_theme(self, input_widget):
        """Aplica tema a campos de entrada."""
        if hasattr(input_widget, 'setObjectName'):
            input_widget.setObjectName("input_busqueda")

    def get_current_theme(self) -> str:
        """Retorna el tema actualmente activo."""
        return self._current_theme

    def get_available_themes(self) -> list:
        """Retorna lista de temas disponibles."""
        return list(self.AVAILABLE_THEMES.keys())

    def reload_themes(self):
        """Recarga todos los temas desde archivos."""
        self._loaded_themes.clear()
        self._load_available_themes()
        logging.debug("Temas recargados desde archivos")

    def apply_unified_module_styles(self, widget):
        """
        Aplica estilos unificados según especificaciones del usuario:
        - Pestañas de 20px de alto
        - Botones del tamaño del módulo logística
        """
        try:
            from rexus.ui.unified_styles import UnifiedStyles
            from PyQt6.QtWidgets import QTabWidget, QPushButton

            # Aplicar estilos específicos a QTabWidget encontrados
            for tab_widget in widget.findChildren(QTabWidget):
                UnifiedStyles.apply_tab_styles_only(tab_widget)
                print(f"[STYLE] Pestañas de 20px aplicadas a {tab_widget.objectName()}")

            # Aplicar estilos de botones (sin sobreescribir colores)
            for button in widget.findChildren(QPushButton):
                if not button.styleSheet():  # Solo si no tiene estilos específicos
                    button.setStyleSheet(UnifiedStyles.get_button_styles())

            print(f"[STYLE] Estilos unificados aplicados a {widget.__class__.__name__}")
            return True
        except ImportError as e:
            print(f"[STYLE] Error importando estilos unificados: {e}")
            return False
        except (AttributeError, RuntimeError, OSError, IOError) as e:
            print(f"[STYLE] Error aplicando estilos unificados: {e}")
            return False

    def _get_critical_form_styles(self, theme_name: str) -> str:
        """
        DESHABILITADO: No retorna estilos invasivos.

        Este método causaba cambios invasivos en toda la UI.
        Los estilos se manejan directamente desde archivos QSS.

        Args:
            theme_name: Nombre del tema activo

        Returns:
            str: Cadena vacía (sin estilos invasivos)
        """
        print(f"[STYLE] _get_critical_form_styles DESHABILITADO para tema: {theme_name}")
        return ""

    def apply_critical_form_fixes(self, widget: QWidget = None) -> bool:
        """
        Aplica correcciones críticas de formularios independientemente del tema.

        Args:
            widget: Widget específico o None para aplicar globalmente

        Returns:
            bool: True si se aplicaron las correcciones
        """
        try:
            critical_styles = self._get_critical_form_styles(self._current_theme)

            if widget is None:
                # Aplicar globalmente
                app = QApplication.instance()
                if app:
                    current_styles = app.styleSheet()
                    new_styles = f"{current_styles}\n\n/* EMERGENCY FORM FIXES */\n{critical_styles}"
                    app.setStyleSheet(new_styles)
                    logger.info("[STYLE] Correcciones criticas de formularios aplicadas globalmente")
                    return True
            else:
                # Aplicar a widget específico
                current_styles = widget.styleSheet()
                new_styles = f"{current_styles}\n{critical_styles}"
                widget.setStyleSheet(new_styles)
                print(f"[STYLE] Correcciones criticas aplicadas a {widget.__class__.__name__}")
                return True

        except (AttributeError, RuntimeError, OSError) as e:
            logger.error(f"Error aplicando correcciones críticas: {e}")
            return False

        return False

    def force_light_theme_for_forms(self) -> bool:
        """
        Fuerza tema claro específicamente para formularios críticos.
        Útil cuando el tema oscuro causa problemas de legibilidad.

        Returns:
            bool: True si se aplicó correctamente
        """
        emergency_light_styles = """
        /* EMERGENCY LIGHT THEME FOR FORMS */
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
        QDateEdit, QTimeEdit, QDateTimeEdit, QPlainTextEdit {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            border-radius: 4px !important;
            padding: 6px !important;
            font-size: 14px !important;
            font-weight: normal !important;
        }

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus,
        QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus,
        QDateTimeEdit:focus, QPlainTextEdit:focus {
            background-color: #ffffff !important;
            border: 2px solid #0066cc !important;
            color: #000000 !important;
        }

        QLabel {
            color: #000000 !important;
            background: transparent !important;
            font-weight: normal !important;
        }

        QPushButton {
            background-color: #0066cc !important;
            color: #ffffff !important;
            border: 1px solid #0066cc !important;
            border-radius: 4px !important;
            padding: 8px 16px !important;
            font-size: 14px !important;
        }

        QPushButton:hover {
            background-color: #0052a3 !important;
        }

        QComboBox QAbstractItemView {
            background-color: #ffffff !important;
            color: #000000 !important;
            selection-background-color: #0066cc !important;
            selection-color: #ffffff !important;
        }
        """

        try:
            app = QApplication.instance()
            if app:
                current_styles = app.styleSheet()
                new_styles = f"{current_styles}\n{emergency_light_styles}"
                app.setStyleSheet(new_styles)
                logger.info("[STYLE] Tema de emergencia claro aplicado para formularios")
                return True
        except (AttributeError, RuntimeError, OSError) as e:
            logger.error(f"Error aplicando tema de emergencia: {e}")

        return False

    def apply_emergency_readable_forms(self) -> bool:
        """
        DESHABILITADO: No se aplican correcciones invasivas.

        Este método fue causante de problemas de UI invasivos.
        Los temas se aplican directamente desde archivos QSS.

        Returns:
            bool: True (sin aplicar correcciones)
        """
        logger.info("[STYLE] apply_emergency_readable_forms DESHABILITADO - sin correcciones invasivas")
        return True

    def _apply_automatic_dark_fixes(self) -> bool:
        """
        Aplica correcciones automáticas cuando se detecta tema oscuro del sistema.
        Este método se ejecuta automáticamente durante la inicialización.
        """
        try:
            # Primero aplicar el tema oscuro mejorado
            if 'dark' in self._loaded_themes:
                logger.info("[STYLE] [ART] Aplicando tema oscuro mejorado")

            # Luego aplicar correcciones críticas
            logger.info("[STYLE]  Aplicando correcciones críticas de contraste")
            critical_success = self.apply_critical_contrast_fixes()

            if critical_success:
                logger.info("[STYLE] [OK] Correcciones automáticas aplicadas exitosamente")
                return True
            else:
                logger.info("[STYLE] [WARNING] Advertencia: No se pudieron aplicar todas las correcciones")
                return False

        except (AttributeError, RuntimeError, OSError, IOError) as e:
            print(f"[STYLE] [ERROR] Error aplicando correcciones automáticas: {e}")
            return False

    @classmethod
    def get_colors(cls) -> Dict[str, str]:
        """Retorna diccionario con colores estándar de la aplicación."""
        return {
            'primary': '#1e40af',
            'secondary': '#3b82f6',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'light': '#f8fafc',
            'dark': '#1e293b',
            'border': '#e2e8f0',
            'background': '#ffffff',
            'muted': '#64748b'
        }

    @classmethod
    def get_standard_spacing(cls) -> Dict[str, int]:
        """Retorna espaciados estándar para layouts."""
        return {
            'small': 5,
            'medium': 10,
            'large': 20,
            'xlarge': 30
        }
    
    def _apply_critical_dark_theme_fixes(self):
        """
        Aplica correcciones críticas automáticamente cuando se detecta tema oscuro.
        Soluciona problemas de legibilidad inmediatamente.
        """
        try:
            logger.info("[STYLE] [ART] Aplicando tema oscuro mejorado")
            
            # Cargar y aplicar el tema oscuro corregido
            dark_theme_path = self._themes_path / 'theme_dark_contrast_fixed.qss'
            
            if dark_theme_path.exists():
                with open(dark_theme_path, 'r', encoding='utf-8') as file:
                    dark_styles = file.read()
                
                # Aplicar estilos globalmente
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(dark_styles)
                    logger.info("[STYLE]  Aplicando correcciones críticas de contraste")
                    logger.info("[STYLE] [OK] Correcciones automáticas aplicadas exitosamente")
                else:
                    logger.info("[STYLE] [WARNING] No se pudo obtener instancia de QApplication")
            else:
                logger.info("[STYLE] [ERROR] Archivo de tema oscuro corregido no encontrado")
                # Fallback: aplicar estilos críticos inline
                self._apply_inline_dark_fixes()
                
        except (IOError, OSError, FileNotFoundError, AttributeError, RuntimeError) as e:
            print(f"[STYLE] [ERROR] Error aplicando correcciones de tema oscuro: {e}")
            self._apply_inline_dark_fixes()
    
    def _apply_inline_dark_fixes(self):
        """Aplica correcciones críticas inline como fallback."""
        critical_fixes = """
        QLineEdit { 
            background-color: #404040 !important; 
            color: #ffffff !important; 
            border: 2px solid #555555; 
        }
        QTextEdit { 
            background-color: #404040 !important; 
            color: #ffffff !important; 
            border: 2px solid #555555; 
        }
        QComboBox { 
            background-color: #404040 !important; 
            color: #ffffff !important; 
            border: 2px solid #555555; 
        }
        QPushButton { 
            background-color: #0078d4 !important; 
            color: #ffffff !important; 
            border: none; 
            padding: 8px 16px; 
        }
        QLabel { 
            color: #ffffff !important; 
        }
        """
        
        try:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(critical_fixes)
                logger.info("[STYLE] [OK] Correcciones críticas inline aplicadas")
        except (AttributeError, RuntimeError, OSError) as e:
            print(f"[STYLE] [ERROR] Error aplicando correcciones inline: {e}")


# Instancia global del gestor de estilos
style_manager = StyleManager()
