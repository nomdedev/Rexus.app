# -*- coding: utf-8 -*-
"""
Theme Manager - Gestor de temas para Rexus.app
Maneja cambios entre tema claro y oscuro
"""

from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
import os


class ThemeManager(QObject):
    """Gestor de temas de la aplicación."""
    
    # Señales
    theme_changed = pyqtSignal(str)  # 'light' or 'dark'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = QSettings("Rexus", "RexusApp")
        self.current_theme = self.settings.value("theme", "light")
        self.themes = {
            'light': self.get_light_theme(),
            'dark': self.get_dark_theme()
        }
    
    def get_light_theme(self):
        """Retorna el tema claro."""
        return {
            'name': 'light',
            'primary_color': '#667eea',
            'secondary_color': '#764ba2',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text_primary': '#333333',
            'text_secondary': '#666666',
            'border': '#e0e0e0',
            'accent': '#2196f3',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'stylesheet': self.get_light_stylesheet()
        }
    
    def get_dark_theme(self):
        """Retorna el tema oscuro."""
        return {
            'name': 'dark',
            'primary_color': '#667eea',
            'secondary_color': '#764ba2', 
            'background': '#1e1e1e',
            'surface': '#2d2d2d',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'border': '#404040',
            'accent': '#64b5f6',
            'success': '#66bb6a',
            'warning': '#ffb74d',
            'error': '#ef5350',
            'stylesheet': self.get_dark_stylesheet()
        }
    
    def get_light_stylesheet(self):
        """Retorna el stylesheet para tema claro."""
        return """
        /* Tema Claro - Rexus.app */
        QMainWindow {
            background-color: #f8f9fa;
            color: #333333;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #333333;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        
        QPushButton {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #5a67d8;
        }
        
        QPushButton:pressed {
            background-color: #4c51bf;
        }
        
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #999999;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
            color: #333333;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: #667eea;
        }
        
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            gridline-color: #e0e0e0;
            selection-background-color: #e3f2fd;
        }
        
        QHeaderView::section {
            background-color: #f5f5f5;
            color: #333333;
            padding: 8px;
            border: 1px solid #e0e0e0;
            font-weight: bold;
        }
        
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f5f5f5;
            color: #666666;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #667eea;
            color: white;
        }
        
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #cccccc;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #999999;
        }
        
        QMenuBar {
            background-color: #ffffff;
            color: #333333;
            border-bottom: 1px solid #e0e0e0;
        }
        
        QMenuBar::item:selected {
            background-color: #e3f2fd;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #e3f2fd;
        }
        
        QProgressBar {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: #f5f5f5;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #667eea;
            border-radius: 3px;
        }
        """
    
    def get_dark_stylesheet(self):
        """Retorna el stylesheet para tema oscuro."""
        return """
        /* Tema Oscuro - Rexus.app */
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        
        QFrame {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        
        QPushButton {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #5a67d8;
        }
        
        QPushButton:pressed {
            background-color: #4c51bf;
        }
        
        QPushButton:disabled {
            background-color: #404040;
            color: #666666;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            background-color: #1e1e1e;
            border: 2px solid #404040;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: #667eea;
        }
        
        QTableWidget {
            background-color: #2d2d2d;
            alternate-background-color: #1e1e1e;
            gridline-color: #404040;
            selection-background-color: #3d4851;
            color: #ffffff;
        }
        
        QHeaderView::section {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #404040;
            font-weight: bold;
        }
        
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
        }
        
        QTabBar::tab {
            background-color: #1e1e1e;
            color: #cccccc;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #667eea;
            color: white;
        }
        
        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #404040;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-bottom: 1px solid #404040;
        }
        
        QMenuBar::item:selected {
            background-color: #3d4851;
        }
        
        QMenu {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 4px;
            color: #ffffff;
        }
        
        QMenu::item:selected {
            background-color: #3d4851;
        }
        
        QProgressBar {
            border: 1px solid #404040;
            border-radius: 4px;
            background-color: #1e1e1e;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #667eea;
            border-radius: 3px;
        }
        
        QLabel {
            color: #ffffff;
        }
        """
    
    def apply_theme(self, theme_name=None):
        """Aplica un tema específico a la aplicación."""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name not in self.themes:
            theme_name = 'light'
        
        theme = self.themes[theme_name]
        app = QApplication.instance()
        
        if app:
            # Aplicar stylesheet
            app.setStyleSheet(theme['stylesheet'])
            
            # Configurar paleta de colores
            palette = self.create_palette(theme)
            app.setPalette(palette)
            
            # Guardar tema actual
            self.current_theme = theme_name
            self.settings.setValue("theme", theme_name)
            
            # Emitir señal de cambio
            self.theme_changed.emit(theme_name)
    
    def create_palette(self, theme):
        """Crea una paleta de colores para el tema."""
        palette = QPalette()
        
        # Colores de fondo
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme['surface']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme['border']))
        
        # Colores de texto
        palette.setColor(QPalette.ColorRole.Text, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme['text_secondary']))
        
        # Colores de botones
        palette.setColor(QPalette.ColorRole.Button, QColor(theme['primary_color']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('#ffffff'))
        
        # Colores de highlight
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))
        
        return palette
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
    
    def get_current_theme(self):
        """Retorna el tema actual."""
        return self.current_theme
    
    def get_theme_data(self, theme_name=None):
        """Retorna los datos del tema especificado."""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['light'])
    
    def is_dark_theme(self):
        """Verifica si el tema actual es oscuro."""
        return self.current_theme == 'dark'
    
    def add_custom_theme(self, name, theme_data):
        """Agrega un tema personalizado."""
        self.themes[name] = theme_data
    
    def remove_custom_theme(self, name):
        """Elimina un tema personalizado."""
        if name in ['light', 'dark']:
            return False  # No permitir eliminar temas base
        
        if name in self.themes:
            del self.themes[name]
            return True
        return False
    
    def get_available_themes(self):
        """Retorna lista de temas disponibles."""
        return list(self.themes.keys())
    
    def export_theme(self, theme_name, file_path):
        """Exporta un tema a archivo."""
        if theme_name not in self.themes:
            return False
        
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes[theme_name], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exportando tema: {e}")
            return False
    
    def import_theme(self, file_path):
        """Importa un tema desde archivo."""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme_name = theme_data.get('name', 'custom')
            self.add_custom_theme(theme_name, theme_data)
            return theme_name
        except Exception as e:
            print(f"Error importando tema: {e}")
            return None