"""
Gestor de Temas Moderno para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont

from ..core.themes import (
    DEFAULT_THEME, THEMES, THEME_METADATA, 
    get_theme, get_available_themes, is_dark_theme,
    ColorPalette
)
from ..core.config import get_env_var, PROJECT_ROOT
from ..core.logger import get_logger

logger = get_logger("theme_manager")

class ThemeManager(QObject):
    """
    Gestor centralizado de temas con persistencia y funcionalidades avanzadas
    """
    
    # Señales para notificar cambios de tema
    theme_changed = pyqtSignal(str, dict)  # theme_name, theme_colors
    font_changed = pyqtSignal(str, int)    # font_family, font_size
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("theme_manager")
        
        # Configuración
        self.config_file = PROJECT_ROOT / "config" / "theme_preferences.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Estado actual
        self.current_theme_name = DEFAULT_THEME
        self.current_theme = get_theme(DEFAULT_THEME)
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        
        # Callbacks para actualización
        self.theme_callbacks: list[Callable] = []
        
        # Cargar preferencias guardadas
        self._load_preferences()
        
        self.logger.info("ThemeManager inicializado", extra={
            "current_theme": self.current_theme_name,
            "font": f"{self.current_font_family} {self.current_font_size}pt"
        })
    
    def _load_preferences(self):
        """Cargar preferencias de tema desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Cargar tema
                theme_name = prefs.get("theme", DEFAULT_THEME)
                if theme_name in THEMES:
                    self.current_theme_name = theme_name
                    self.current_theme = get_theme(theme_name)
                
                # Cargar fuente
                self.current_font_family = prefs.get("font_family", "Segoe UI")
                self.current_font_size = prefs.get("font_size", 10)
                
                self.logger.info("Preferencias de tema cargadas", extra=prefs)
                
        except Exception as e:
            self.logger.warning("Error cargando preferencias de tema", extra={
                "error": str(e)
            })
            # Usar valores por defecto
            self.current_theme_name = DEFAULT_THEME
            self.current_theme = get_theme(DEFAULT_THEME)
    
    def _save_preferences(self):
        """Guardar preferencias de tema en archivo"""
        try:
            prefs = {
                "theme": self.current_theme_name,
                "font_family": self.current_font_family,
                "font_size": self.current_font_size,
                "last_updated": os.path.getmtime(self.config_file) if self.config_file.exists() else None
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Preferencias de tema guardadas", extra=prefs)
            
        except Exception as e:
            self.logger.error("Error guardando preferencias de tema", extra={
                "error": str(e)
            })
    
    def set_theme(self, theme_name: str, apply_immediately: bool = True) -> bool:
        """
        Establecer tema activo
        
        Args:
            theme_name: Nombre del tema
            apply_immediately: Si aplicar inmediatamente a la aplicación
        
        Returns:
            True si el tema fue aplicado exitosamente
        """
        if theme_name not in THEMES:
            self.logger.warning("Tema no encontrado", extra={"theme": theme_name})
            return False
        
        old_theme = self.current_theme_name
        self.current_theme_name = theme_name
        self.current_theme = get_theme(theme_name)
        
        # Guardar preferencias
        self._save_preferences()
        
        # Aplicar inmediatamente si se solicita
        if apply_immediately:
            self.apply_theme_to_application()
        
        # Emitir señal de cambio
        self.theme_changed.emit(theme_name, self.current_theme.to_dict())
        
        # Ejecutar callbacks
        for callback in self.theme_callbacks:
            try:
                callback(theme_name, self.current_theme)
            except Exception as e:
                self.logger.error("Error en callback de tema", extra={
                    "error": str(e)
                })
        
        self.logger.info("Tema cambiado", extra={
            "old_theme": old_theme,
            "new_theme": theme_name
        })
        
        return True
    
    def set_font(self, font_family: str, font_size: int, apply_immediately: bool = True):
        """Establecer fuente de la aplicación"""
        old_family = self.current_font_family
        old_size = self.current_font_size
        
        self.current_font_family = font_family
        self.current_font_size = font_size
        
        # Guardar preferencias
        self._save_preferences()
        
        # Aplicar inmediatamente si se solicita
        if apply_immediately:
            self.apply_theme_to_application()
        
        # Emitir señal
        self.font_changed.emit(font_family, font_size)
        
        self.logger.info("Fuente cambiada", extra={
            "old_font": f"{old_family} {old_size}pt",
            "new_font": f"{font_family} {font_size}pt"
        })
    
    def apply_theme_to_application(self):
        """Aplicar tema actual a toda la aplicación PyQt6"""
        app = QApplication.instance()
        if not app:
            self.logger.warning("No hay instancia de QApplication")
            return
        
        # Aplicar fuente global
        font = QFont(self.current_font_family, self.current_font_size)
        app.setFont(font)
        
        # Generar y aplicar stylesheet
        stylesheet = self._generate_complete_stylesheet()
        app.setStyleSheet(stylesheet)
        
        self.logger.info("Tema aplicado a la aplicación", extra={
            "theme": self.current_theme_name,
            "stylesheet_length": len(stylesheet)
        })
    
    def _generate_complete_stylesheet(self) -> str:
        """Generar stylesheet completo basado en el tema actual"""
        if not self.current_theme:
            return ""
        
        colors = self.current_theme.to_dict()
        
        return f"""
/* ===== ESTILOS GLOBALES ===== */
QWidget {{
    font-family: "{self.current_font_family}";
    font-size: {self.current_font_size}pt;
    color: {colors['on_background']};
    background-color: {colors['background']};
}}

/* ===== APLICACIÓN PRINCIPAL ===== */
QMainWindow {{
    background-color: {colors['background']};
    border: none;
}}

QMainWindow::separator {{
    background-color: {colors['border']};
    width: 1px;
    height: 1px;
}}

/* ===== BOTONES ===== */
QPushButton {{
    background-color: {colors['primary']};
    color: {colors['on_primary']};
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {colors['button_hover']};
}}

QPushButton:pressed {{
    background-color: {colors['button_active']};
}}

QPushButton:disabled {{
    background-color: {colors['surface_variant']};
    color: {colors['on_surface_variant']};
}}

QPushButton[buttonType="secondary"] {{
    background-color: {colors['surface']};
    color: {colors['on_surface']};
    border: 1px solid {colors['border']};
}}

QPushButton[buttonType="secondary"]:hover {{
    background-color: {colors['surface_variant']};
}}

QPushButton[buttonType="danger"] {{
    background-color: {colors['error']};
    color: white;
}}

QPushButton[buttonType="danger"]:hover {{
    background-color: #dc2626;
}}

QPushButton[buttonType="success"] {{
    background-color: {colors['success']};
    color: white;
}}

/* ===== CAMPOS DE ENTRADA ===== */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {colors['input_bg']};
    border: 2px solid {colors['border']};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {colors['primary']};
    selection-color: {colors['on_primary']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {colors['border_focus']};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {colors['surface_variant']};
    color: {colors['on_surface_variant']};
}}

/* ===== COMBOBOX ===== */
QComboBox {{
    background-color: {colors['input_bg']};
    border: 2px solid {colors['border']};
    border-radius: 6px;
    padding: 6px 12px;
    min-width: 100px;
}}

QComboBox:focus {{
    border-color: {colors['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {colors['on_surface']};
}}

QComboBox QAbstractItemView {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 6px;
    selection-background-color: {colors['primary']};
    selection-color: {colors['on_primary']};
}}

/* ===== LABELS ===== */
QLabel[labelType="title"] {{
    font-size: {self.current_font_size + 2}pt;
    font-weight: 600;
    color: {colors['on_background']};
}}

QLabel[labelType="subtitle"] {{
    font-size: {self.current_font_size + 1}pt;
    font-weight: 500;
    color: {colors['on_surface']};
}}

QLabel[labelType="error"] {{
    color: {colors['error']};
    font-weight: 500;
}}

QLabel[labelType="success"] {{
    color: {colors['success']};
    font-weight: 500;
}}

QLabel[labelType="warning"] {{
    color: {colors['warning']};
    font-weight: 500;
}}

QLabel[labelType="info"] {{
    color: {colors['info']};
    font-weight: 500;
}}

/* ===== DIÁLOGOS ===== */
QDialog {{
    background-color: {colors['card_bg']};
    border-radius: 12px;
}}

QMessageBox {{
    background-color: {colors['card_bg']};
    border-radius: 8px;
}}

QMessageBox QLabel {{
    color: {colors['on_surface']};
}}

/* ===== TABLAS ===== */
QTableWidget, QTableView {{
    background-color: {colors['card_bg']};
    alternate-background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    gridline-color: {colors['border']};
    selection-background-color: {colors['primary']};
    selection-color: {colors['on_primary']};
}}

QTableWidget::item, QTableView::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {colors['primary']};
    color: {colors['on_primary']};
}}

QHeaderView::section {{
    background-color: {colors['surface']};
    color: {colors['on_surface']};
    padding: 8px;
    border: none;
    border-bottom: 2px solid {colors['primary']};
    font-weight: 600;
}}

/* ===== MENÚS ===== */
QMenuBar {{
    background-color: {colors['header_bg']};
    border-bottom: 1px solid {colors['border']};
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 12px;
}}

QMenuBar::item:selected {{
    background-color: {colors['surface_variant']};
    border-radius: 4px;
}}

QMenu {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 16px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {colors['primary']};
    color: {colors['on_primary']};
}}

/* ===== TOOLBAR ===== */
QToolBar {{
    background-color: {colors['surface']};
    border: none;
    spacing: 4px;
    padding: 4px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px;
}}

QToolButton:hover {{
    background-color: {colors['surface_variant']};
}}

QToolButton:pressed {{
    background-color: {colors['primary']};
    color: {colors['on_primary']};
}}

/* ===== SIDEBAR ===== */
QWidget[widgetType="sidebar"] {{
    background-color: {colors['sidebar_bg']};
    border-right: 1px solid {colors['border']};
}}

QPushButton[buttonType="sidebar"] {{
    background-color: transparent;
    color: {colors['on_surface']};
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 500;
}}

QPushButton[buttonType="sidebar"]:hover {{
    background-color: {colors['sidebar_hover']};
}}

QPushButton[buttonType="sidebar"]:checked {{
    background-color: {colors['sidebar_active']};
    color: {colors['on_primary']};
}}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {{
    background-color: {colors['surface']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['surface_variant']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['border']};
}}

QScrollBar:horizontal {{
    background-color: {colors['surface']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors['surface_variant']};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {colors['border']};
    border-radius: 8px;
    background-color: {colors['card_bg']};
}}

QTabBar::tab {{
    background-color: {colors['surface']};
    padding: 8px 12px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 80px;
    min-height: 24px;
    max-height: 24px;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {colors['primary']};
    color: {colors['on_primary']};
}}

QTabBar::tab:hover {{
    background-color: {colors['surface_variant']};
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    background-color: {colors['surface']};
    border: 1px solid {colors['border']};
    border-radius: 10px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors['primary']};
    border-radius: 10px;
}}

/* ===== CHECKBOX Y RADIO ===== */
QCheckBox, QRadioButton {{
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
}}

QCheckBox::indicator:unchecked {{
    background-color: {colors['input_bg']};
    border: 2px solid {colors['border']};
    border-radius: 4px;
}}

QCheckBox::indicator:checked {{
    background-color: {colors['primary']};
    border: 2px solid {colors['primary']};
    border-radius: 4px;
}}

QRadioButton::indicator:unchecked {{
    background-color: {colors['input_bg']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
}}

QRadioButton::indicator:checked {{
    background-color: {colors['primary']};
    border: 2px solid {colors['primary']};
    border-radius: 8px;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: {colors['surface']};
    border-top: 1px solid {colors['border']};
    color: {colors['on_surface']};
}}

/* ===== TOOLTIPS ===== */
QToolTip {{
    background-color: {colors['surface_variant']};
    color: {colors['on_surface_variant']};
    border: 1px solid {colors['border']};
    border-radius: 6px;
    padding: 6px 8px;
}}

/* ===== TARJETAS PERSONALIZADAS ===== */
QWidget[widgetType="card"] {{
    background-color: {colors['card_bg']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
}}

QWidget[widgetType="header"] {{
    background-color: {colors['header_bg']};
    border-bottom: 1px solid {colors['border']};
}}
"""
    
    def get_current_theme_name(self) -> str:
        """Obtener nombre del tema actual"""
        return self.current_theme_name
    
    def get_current_theme(self) -> Optional[ColorPalette]:
        """Obtener objeto del tema actual"""
        return self.current_theme
    
    def get_current_colors(self) -> Dict[str, str]:
        """Obtener diccionario de colores del tema actual"""
        return self.current_theme.to_dict() if self.current_theme else {}
    
    def get_available_themes(self) -> Dict[str, Dict[str, Any]]:
        """Obtener temas disponibles con metadata"""
        return get_available_themes()
    
    def is_dark_theme(self) -> bool:
        """Verificar si el tema actual es oscuro"""
        return is_dark_theme(self.current_theme_name)
    
    def register_theme_callback(self, callback: Callable):
        """Registrar callback para cambios de tema"""
        self.theme_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback: Callable):
        """Desregistrar callback de cambios de tema"""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
    
    def reset_to_default(self):
        """Restablecer tema por defecto"""
        self.set_theme(DEFAULT_THEME)
        self.set_font("Segoe UI", 10)
    
    def get_preferences(self) -> Dict[str, Any]:
        """Obtener preferencias actuales"""
        return {
            "theme": self.current_theme_name,
            "font_family": self.current_font_family, 
            "font_size": self.current_font_size
        }

# Instancia global del gestor de temas
theme_manager = ThemeManager()

# Funciones de conveniencia para compatibilidad
def aplicar_tema(app, theme_name: str = DEFAULT_THEME):
    """Aplica un tema a la aplicación (función legacy)"""
    theme_manager.set_theme(theme_name, apply_immediately=True)

def cargar_modo_tema() -> str:
    """Carga el tema guardado o devuelve el por defecto"""
    return theme_manager.get_current_theme_name()

def set_theme(theme_name: str):
    """Establece un tema específico"""
    theme_manager.set_theme(theme_name)

def get_current_theme_colors() -> Dict[str, str]:
    """Obtener colores del tema actual"""
    return theme_manager.get_current_colors()

def is_current_theme_dark() -> bool:
    """Verificar si el tema actual es oscuro"""
    return theme_manager.is_dark_theme()
