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
from typing import Dict, Optional

from PyQt6.QtWidgets import QApplication, QWidget


class StyleManager:
    """Gestor centralizado de estilos y temas para la aplicación."""
    
    _instance = None
    _current_theme = 'unified'
    _themes_path = Path('resources/qss')
    
    # Mapa de temas disponibles a archivos QSS  
    AVAILABLE_THEMES = {
        'professional': 'professional_theme_clean.qss',
        'light': 'theme_light_clean.qss',
        'dark': 'theme_dark_clean.qss',
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
            self._load_available_themes()
            self._detect_system_theme()
    
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
                
        except Exception as e:
            print(f"[WARNING] Error detectando tema del sistema: {e}")
            self._current_theme = 'professional'
            print("[STYLE] Usando tema por defecto 'professional' por error")
    
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
                print("[STYLE] Tema oscuro detectado en Windows - aplicando 'dark'")
            else:  # Light mode
                self._current_theme = 'light' 
                print("[STYLE] Tema claro detectado en Windows - aplicando 'light'")
                
        except (FileNotFoundError, OSError, ImportError):
            self._current_theme = 'professional'
            print("[STYLE] ⚠ No se pudo detectar tema de Windows - usando 'professional'")
    
    def _detect_macos_theme(self):
        """Detecta tema en macOS."""
        try:
            import subprocess
            result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'Dark' in result.stdout:
                self._current_theme = 'dark'
                print("[STYLE] Tema oscuro detectado en macOS - aplicando 'dark'")
            else:
                self._current_theme = 'light'
                print("[STYLE] Tema claro detectado en macOS - aplicando 'light'")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._current_theme = 'professional'
            print("[STYLE] ⚠ No se pudo detectar tema de macOS - usando 'professional'")
    
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
                    print("[STYLE] Tema oscuro detectado en GNOME - aplicando 'dark'")
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
                            print("[STYLE] Tema oscuro detectado en KDE - aplicando 'dark'")
                            return
            
            # Si llegamos aquí, usar tema claro por defecto en Linux
            self._current_theme = 'light'
            print("[STYLE] Usando tema claro por defecto en Linux")
            
        except Exception:
            self._current_theme = 'professional'
            print("[STYLE] ⚠ No se pudo detectar tema de Linux - usando 'professional'")
    
    def _load_available_themes(self):
        """Carga todos los temas disponibles en memoria."""
        for theme_name, filename in self.AVAILABLE_THEMES.items():
            theme_path = self._themes_path / filename
            
            if theme_path.exists():
                try:
                    with open(theme_path, 'r', encoding='utf-8') as f:
                        self._loaded_themes[theme_name] = f.read()
                    logging.info(f"Tema '{theme_name}' cargado exitosamente")
                except Exception as e:
                    logging.error(f"Error cargando tema '{theme_name}': {e}")
            else:
                logging.warning(f"Archivo de tema no encontrado: {theme_path}")
    
    def apply_global_theme(self, theme_name: str = None) -> bool:
        """Aplica un tema global a toda la aplicación."""
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
                # Obtener estilos base más estilos críticos para formularios
                base_styles = self._loaded_themes[theme_name]
                critical_form_styles = self._get_critical_form_styles(theme_name)
                
                # Combinar estilos
                combined_styles = f"{base_styles}\n\n/* CRITICAL FORM FIXES */\n{critical_form_styles}"
                
                app.setStyleSheet(combined_styles)
                self._current_theme = theme_name
                logging.info(f"Tema global '{theme_name}' aplicado exitosamente con correcciones críticas")
                print(f"[STYLE] Tema aplicado: {theme_name} con correcciones de contraste")
                return True
            else:
                logging.error("No se pudo obtener instancia de QApplication")
                return False
                
        except Exception as e:
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
                logging.info(f"Estilos unificados aplicados a {widget.__class__.__name__}")
                return True
            else:
                logging.warning("Archivo de estilos unificados no encontrado")
                return False
                
        except Exception as e:
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
            
            logging.info(f"Tema de módulo aplicado a {widget.__class__.__name__} ({module_name})")
            return True
            
        except Exception as e:
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
            
        except Exception as e:
            print(f"[WARNING] Error aplicando tema '{theme_name}': {e}")
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
                
        except Exception as e:
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
        logging.info("Temas recargados desde archivos")
    
    def _get_critical_form_styles(self, theme_name: str) -> str:
        """
        Obtiene estilos críticos para formularios con buen contraste.
        
        Args:
            theme_name: Nombre del tema activo
            
        Returns:
            str: CSS crítico para formularios legibles
        """
        if theme_name == 'dark':
            return """
            /* CORRECCIONES CRÍTICAS PARA TEMA OSCURO */
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, 
            QDateEdit, QTimeEdit, QDateTimeEdit, QPlainTextEdit {
                background-color: #2d3748 !important;
                color: #ffffff !important;
                border: 2px solid #4a5568 !important;
                border-radius: 8px !important;
                padding: 8px 12px !important;
                font-size: 14px !important;
                min-height: 20px !important;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, 
            QDateTimeEdit:focus, QPlainTextEdit:focus {
                background-color: #374151 !important;
                border: 2px solid #3b82f6 !important;
                color: #ffffff !important;
            }
            
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, 
            QSpinBox:disabled, QDoubleSpinBox:disabled, QDateEdit:disabled {
                background-color: #1f2937 !important;
                color: #9ca3af !important;
                border: 2px solid #374151 !important;
            }
            
            QLabel {
                color: #f9fafb !important;
                background: transparent !important;
            }
            
            QComboBox::drop-down {
                background-color: #4a5568 !important;
                border: none !important;
                border-radius: 6px !important;
            }
            
            QComboBox::down-arrow {
                image: none !important;
                width: 0px !important;
                height: 0px !important;
            }
            
            /* Asegurar que el texto en combobox sea visible */
            QComboBox QAbstractItemView {
                background-color: #2d3748 !important;
                color: #ffffff !important;
                selection-background-color: #3b82f6 !important;
                selection-color: #ffffff !important;
                border: 1px solid #4a5568 !important;
            }
            """
        else:
            # Para temas claros
            return """
            /* CORRECCIONES CRÍTICAS PARA TEMA CLARO */
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, 
            QDateEdit, QTimeEdit, QDateTimeEdit, QPlainTextEdit {
                background-color: #ffffff !important;
                color: #1f2937 !important;
                border: 2px solid #d1d5db !important;
                border-radius: 8px !important;
                padding: 8px 12px !important;
                font-size: 14px !important;
                min-height: 20px !important;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, 
            QDateTimeEdit:focus, QPlainTextEdit:focus {
                background-color: #f9fafb !important;
                border: 2px solid #3b82f6 !important;
                color: #1f2937 !important;
            }
            
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, 
            QSpinBox:disabled, QDoubleSpinBox:disabled, QDateEdit:disabled {
                background-color: #f3f4f6 !important;
                color: #6b7280 !important;
                border: 2px solid #e5e7eb !important;
            }
            
            QLabel {
                color: #1f2937 !important;
                background: transparent !important;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                color: #1f2937 !important;
                selection-background-color: #3b82f6 !important;
                selection-color: #ffffff !important;
                border: 1px solid #d1d5db !important;
            }
            """
    
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
                    print("[STYLE] Correcciones criticas de formularios aplicadas globalmente")
                    return True
            else:
                # Aplicar a widget específico
                current_styles = widget.styleSheet()
                new_styles = f"{current_styles}\n{critical_styles}"
                widget.setStyleSheet(new_styles)
                print(f"[STYLE] Correcciones criticas aplicadas a {widget.__class__.__name__}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error aplicando correcciones críticas: {e}")
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
                print("[STYLE] Tema de emergencia claro aplicado para formularios")
                return True
        except Exception as e:
            print(f"[ERROR] Error aplicando tema de emergencia: {e}")
            
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


# Instancia global del gestor de estilos
style_manager = StyleManager()