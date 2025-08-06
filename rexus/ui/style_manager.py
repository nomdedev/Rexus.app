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
    _current_theme = 'professional'
    _themes_path = Path('resources/qss')
    
    # Mapa de temas disponibles a archivos QSS  
    AVAILABLE_THEMES = {
        'professional': 'professional_theme_clean.qss',
        'light': 'theme_light_clean.qss',
        'minimal': 'theme_light_minimal_clean.qss',
        'optimized': 'theme_optimized_clean.qss',
        'consolidated': 'consolidated_theme_clean.qss'
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
            return False
        
        try:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(self._loaded_themes[theme_name])
                self._current_theme = theme_name
                logging.info(f"Tema global '{theme_name}' aplicado exitosamente")
                return True
            else:
                logging.error("No se pudo obtener instancia de QApplication")
                return False
                
        except Exception as e:
            logging.error(f"Error aplicando tema global '{theme_name}': {e}")
            return False
    
    def get_module_styles(self) -> str:
        """Retorna estilos específicos para módulos."""
        return """
            /* Estilos específicos para módulos de Rexus */
            QWidget[moduleView="true"] {
                background: #f8fafc;
                border: none;
            }
            
            /* Títulos de módulo estándar */
            QLabel[moduleTitle="true"] {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: transparent;
                border: none;
                padding: 0px;
            }
            
            /* Paneles de control estándar */
            QFrame[controlPanel="true"] {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
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
                transform: translateY(-1px);
            }
            
            QPushButton[actionButton="primary"]:pressed {
                background: #1e3a8a;
                transform: translateY(0px);
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
                transform: translateY(-1px);
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
    
    def apply_module_theme(self, widget: QWidget) -> bool:
        """Aplica tema específico a un módulo."""
        try:
            # Aplicar propiedades para identificación
            widget.setProperty("moduleView", True)
            
            # Aplicar estilos del módulo
            current_style = widget.styleSheet()
            module_styles = self.get_module_styles()
            
            # Combinar estilos existentes con los del módulo
            combined_style = f"{current_style}\n{module_styles}"
            widget.setStyleSheet(combined_style)
            
            # Forzar actualización de estilos
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            
            logging.info(f"Tema de módulo aplicado a {widget.__class__.__name__}")
            return True
            
        except Exception as e:
            logging.error(f"Error aplicando tema a módulo: {e}")
            return False
    
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