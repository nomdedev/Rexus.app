# -*- coding: utf-8 -*-
"""
Componentes UI Modernos Avanzados - Rexus.app
Extensión de StandardComponents con elementos UI más modernos y interactivos

Características:
1. Componentes con animaciones sutiles
2. Estados visuales mejorados (hover, focus, disabled)
3. Soporte para temas oscuro/claro
4. Iconografía moderna
5. Feedback visual mejorado
6. Componentes responsivos
7. Mejores contrastes para accesibilidad

Autor: Rexus Development Team
Fecha: 23/08/2025
Versión: 1.0.0
"""

import sys
from typing import Optional, List, Dict, Any, Callable
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import (
    QFont, QIcon, QPalette, QColor, QPainter, QPixmap, 
    QFontMetrics, QLinearGradient, QBrush, QPen
)
from PyQt6.QtWidgets import (
    QFrame, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QVBoxLayout, QHeaderView, QWidget, QLineEdit,
    QComboBox, QSpinBox, QDateEdit, QTextEdit, QCheckBox,
    QRadioButton, QSlider, QProgressBar, QTabWidget, QSplitter,
    QScrollArea, QTreeWidget, QListWidget, QGraphicsEffect,
    QGraphicsDropShadowEffect, QApplication, QSizePolicy
)

# Configurar encoding UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class ModernTheme:
    """Tema moderno con soporte para modo claro y oscuro."""
    
    # Paleta de colores moderna
    LIGHT_THEME = {
        # Colores principales
        'primary': '#2563eb',      # Azul moderno
        'primary_hover': '#1d4ed8', # Azul más oscuro para hover
        'primary_pressed': '#1e40af', # Azul aún más oscuro para pressed
        'secondary': '#6366f1',    # Índigo
        'accent': '#06b6d4',       # Cyan
        'success': '#059669',      # Verde esmeralda
        'warning': '#d97706',      # Naranja ámbar
        'error': '#dc2626',        # Rojo
        'info': '#0284c7',         # Azul cielo
        
        # Colores de fondo
        'background': '#ffffff',    # Blanco puro
        'surface': '#f8fafc',      # Gris muy claro
        'surface_variant': '#f1f5f9', # Gris claro
        'surface_hover': '#e2e8f0', # Gris hover
        
        # Colores de texto
        'text_primary': '#0f172a',  # Texto principal (casi negro)
        'text_secondary': '#475569', # Texto secundario (gris)
        'text_disabled': '#94a3b8',  # Texto deshabilitado
        'text_inverse': '#ffffff',   # Texto inverso (blanco)
        
        # Bordes y divisores
        'border': '#e2e8f0',       # Borde normal
        'border_hover': '#cbd5e1',  # Borde hover
        'border_focus': '#3b82f6',  # Borde focus
        'divider': '#f1f5f9',      # Divisores
        
        # Sombras
        'shadow_light': 'rgba(0, 0, 0, 0.05)',
        'shadow_medium': 'rgba(0, 0, 0, 0.1)',
        'shadow_heavy': 'rgba(0, 0, 0, 0.25)'
    }
    
    DARK_THEME = {
        # Colores principales (más vibrantes en modo oscuro)
        'primary': '#3b82f6',
        'primary_hover': '#2563eb',
        'primary_pressed': '#1d4ed8',
        'secondary': '#8b5cf6',
        'accent': '#06b6d4',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#0ea5e9',
        
        # Colores de fondo (tonos oscuros)
        'background': '#0f172a',    # Azul muy oscuro
        'surface': '#1e293b',       # Gris azulado oscuro
        'surface_variant': '#334155', # Gris medio
        'surface_hover': '#475569',  # Gris hover
        
        # Colores de texto
        'text_primary': '#f8fafc',   # Blanco casi puro
        'text_secondary': '#cbd5e1', # Gris claro
        'text_disabled': '#64748b',  # Gris medio
        'text_inverse': '#0f172a',   # Negro para texto inverso
        
        # Bordes y divisores
        'border': '#334155',
        'border_hover': '#475569',
        'border_focus': '#3b82f6',
        'divider': '#334155',
        
        # Sombras (más prominentes en modo oscuro)
        'shadow_light': 'rgba(0, 0, 0, 0.2)',
        'shadow_medium': 'rgba(0, 0, 0, 0.3)',
        'shadow_heavy': 'rgba(0, 0, 0, 0.5)'
    }
    
    def __init__(self, dark_mode: bool = False):
        self.dark_mode = dark_mode
        self.colors = self.DARK_THEME if dark_mode else self.LIGHT_THEME
    
    def get_color(self, color_name: str) -> str:
        """Obtener color del tema actual."""
        return self.colors.get(color_name, '#000000')
    
    def toggle_dark_mode(self):
        """Alternar entre modo claro y oscuro."""
        self.dark_mode = not self.dark_mode
        self.colors = self.DARK_THEME if self.dark_mode else self.LIGHT_THEME


# Instancia global del tema
_current_theme = ModernTheme(dark_mode=False)


def get_current_theme() -> ModernTheme:
    """Obtener la instancia actual del tema."""
    return _current_theme


class ModernButton(QPushButton):
    """Botón moderno con estados visuales mejorados."""
    
    def __init__(self, text: str = "", button_type: str = "primary", 
                 icon: Optional[QIcon] = None, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.theme = get_current_theme()
        self._animation_timer = QTimer()
        self._hover_opacity = 1.0
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(self.size() * 0.6)  # Icono 60% del tamaño del botón
        
        self._setup_style()
        self._setup_animations()
    
    def _setup_style(self):
        """Configurar estilos del botón."""
        base_style = f"""
            QPushButton {{
                border: 2px solid {self.theme.get_color('border')};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
                text-align: center;
            }}
            
            QPushButton:disabled {{
                color: {self.theme.get_color('text_disabled')};
                background: {self.theme.get_color('surface_variant')};
                border-color: {self.theme.get_color('border')};
            }}
        """
        
        # Estilos específicos por tipo
        if self.button_type == "primary":
            style = base_style + f"""
                QPushButton {{
                    background: {self.theme.get_color('primary')};
                    color: {self.theme.get_color('text_inverse')};
                    border-color: {self.theme.get_color('primary')};
                }}
                
                QPushButton:hover {{
                    background: {self.theme.get_color('primary_hover')};
                    border-color: {self.theme.get_color('primary_hover')};
                }}
                
                QPushButton:pressed {{
                    background: {self.theme.get_color('primary_pressed')};
                    border-color: {self.theme.get_color('primary_pressed')};
                }}
            """
        elif self.button_type == "secondary":
            style = base_style + f"""
                QPushButton {{
                    background: {self.theme.get_color('surface')};
                    color: {self.theme.get_color('primary')};
                    border-color: {self.theme.get_color('primary')};
                }}
                
                QPushButton:hover {{
                    background: {self.theme.get_color('surface_hover')};
                    color: {self.theme.get_color('primary_hover')};
                }}
            """
        elif self.button_type == "success":
            style = base_style + f"""
                QPushButton {{
                    background: {self.theme.get_color('success')};
                    color: {self.theme.get_color('text_inverse')};
                    border-color: {self.theme.get_color('success')};
                }}
                
                QPushButton:hover {{
                    background: #047857;
                    border-color: #047857;
                }}
            """
        elif self.button_type == "warning":
            style = base_style + f"""
                QPushButton {{
                    background: {self.theme.get_color('warning')};
                    color: {self.theme.get_color('text_inverse')};
                    border-color: {self.theme.get_color('warning')};
                }}
                
                QPushButton:hover {{
                    background: #b45309;
                    border-color: #b45309;
                }}
            """
        elif self.button_type == "error":
            style = base_style + f"""
                QPushButton {{
                    background: {self.theme.get_color('error')};
                    color: {self.theme.get_color('text_inverse')};
                    border-color: {self.theme.get_color('error')};
                }}
                
                QPushButton:hover {{
                    background: #b91c1c;
                    border-color: #b91c1c;
                }}
            """
        else:  # ghost/outline
            style = base_style + f"""
                QPushButton {{
                    background: transparent;
                    color: {self.theme.get_color('text_primary')};
                    border-color: {self.theme.get_color('border')};
                }}
                
                QPushButton:hover {{
                    background: {self.theme.get_color('surface_hover')};
                    border-color: {self.theme.get_color('border_hover')};
                }}
            """
        
        self.setStyleSheet(style)
    
    def _setup_animations(self):
        """Configurar animaciones sutiles."""
        self._animation_timer.timeout.connect(self._animate_hover)
        self._animation_timer.setSingleShot(True)
    
    def _animate_hover(self):
        """Animación sutil de hover."""
        # Implementación básica - se podría expandir con QPropertyAnimation
        pass
    
    def enterEvent(self, event):
        """Evento al entrar el mouse."""
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def leaveEvent(self, event):
        """Evento al salir el mouse."""
        super().leaveEvent(event)
        self.setCursor(Qt.CursorShape.ArrowCursor)


class ModernLineEdit(QLineEdit):
    """Campo de entrada moderno con estados visuales mejorados."""
    
    def __init__(self, placeholder: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        
        if placeholder:
            self.setPlaceholderText(placeholder)
        
        self._setup_style()
    
    def _setup_style(self):
        """Configurar estilos del campo de entrada."""
        style = f"""
            QLineEdit {{
                border: 2px solid {self.theme.get_color('border')};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background: {self.theme.get_color('background')};
                color: {self.theme.get_color('text_primary')};
                selection-background-color: {self.theme.get_color('primary')};
                selection-color: {self.theme.get_color('text_inverse')};
            }}
            
            QLineEdit:focus {{
                border-color: {self.theme.get_color('border_focus')};
                outline: none;
            }}
            
            QLineEdit:hover {{
                border-color: {self.theme.get_color('border_hover')};
            }}
            
            QLineEdit:disabled {{
                background: {self.theme.get_color('surface_variant')};
                color: {self.theme.get_color('text_disabled')};
                border-color: {self.theme.get_color('border')};
            }}
        """
        
        self.setStyleSheet(style)


class ModernComboBox(QComboBox):
    """ComboBox moderno con mejor apariencia."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        self._setup_style()
    
    def _setup_style(self):
        """Configurar estilos del combo box."""
        style = f"""
            QComboBox {{
                border: 2px solid {self.theme.get_color('border')};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background: {self.theme.get_color('background')};
                color: {self.theme.get_color('text_primary')};
                min-width: 120px;
            }}
            
            QComboBox:focus {{
                border-color: {self.theme.get_color('border_focus')};
            }}
            
            QComboBox:hover {{
                border-color: {self.theme.get_color('border_hover')};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                background: {self.theme.get_color('text_secondary')};
            }}
            
            QComboBox QAbstractItemView {{
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 6px;
                background: {self.theme.get_color('background')};
                selection-background-color: {self.theme.get_color('surface_hover')};
                selection-color: {self.theme.get_color('text_primary')};
            }}
        """
        
        self.setStyleSheet(style)


class ModernTable(QTableWidget):
    """Tabla moderna con mejor apariencia y funcionalidad."""
    
    def __init__(self, rows: int = 0, columns: int = 0, parent: Optional[QWidget] = None):
        super().__init__(rows, columns, parent)
        self.theme = get_current_theme()
        self._setup_style()
        self._setup_behavior()
    
    def _setup_style(self):
        """Configurar estilos de la tabla."""
        style = f"""
            QTableWidget {{
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 8px;
                background: {self.theme.get_color('background')};
                alternate-background-color: {self.theme.get_color('surface')};
                gridline-color: {self.theme.get_color('border')};
                font-size: 14px;
                color: {self.theme.get_color('text_primary')};
            }}
            
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background: {self.theme.get_color('primary')};
                color: {self.theme.get_color('text_inverse')};
            }}
            
            QTableWidget::item:hover {{
                background: {self.theme.get_color('surface_hover')};
            }}
            
            QHeaderView::section {{
                background: {self.theme.get_color('surface_variant')};
                color: {self.theme.get_color('text_primary')};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {self.theme.get_color('border')};
                font-weight: 600;
            }}
            
            QHeaderView::section:hover {{
                background: {self.theme.get_color('surface_hover')};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {self.theme.get_color('surface')};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {self.theme.get_color('border_hover')};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {self.theme.get_color('text_disabled')};
            }}
        """
        
        self.setStyleSheet(style)
    
    def _setup_behavior(self):
        """Configurar comportamiento de la tabla."""
        # Alternar colores de filas
        self.setAlternatingRowColors(True)
        
        # Configurar selección
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Configurar headers
        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)  # Ocultar números de fila por defecto


class ModernCard(QFrame):
    """Tarjeta moderna con sombra y bordes redondeados."""
    
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        self.title = title
        
        self._setup_layout()
        self._setup_style()
        self._setup_shadow()
    
    def _setup_layout(self):
        """Configurar layout de la tarjeta."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)
        
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 18px;
                    font-weight: 600;
                    color: {self.theme.get_color('text_primary')};
                    margin-bottom: 8px;
                }}
            """)
            self.main_layout.addWidget(self.title_label)
        
        # Contenedor para contenido personalizado
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_widget)
    
    def _setup_style(self):
        """Configurar estilos de la tarjeta."""
        style = f"""
            QFrame {{
                background: {self.theme.get_color('background')};
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 12px;
            }}
        """
        
        self.setStyleSheet(style)
    
    def _setup_shadow(self):
        """Configurar sombra de la tarjeta."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))  # Sombra sutil
        self.setGraphicsEffect(shadow)
    
    def add_content(self, widget: QWidget):
        """Añadir widget al contenido de la tarjeta."""
        self.content_layout.addWidget(widget)


class ModernProgressBar(QProgressBar):
    """Barra de progreso moderna con mejor apariencia."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        self._setup_style()
    
    def _setup_style(self):
        """Configurar estilos de la barra de progreso."""
        style = f"""
            QProgressBar {{
                border: 2px solid {self.theme.get_color('border')};
                border-radius: 8px;
                background: {self.theme.get_color('surface')};
                height: 20px;
                text-align: center;
                font-size: 12px;
                font-weight: 500;
                color: {self.theme.get_color('text_primary')};
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.theme.get_color('primary')},
                    stop: 1 {self.theme.get_color('accent')}
                );
                border-radius: 6px;
                margin: 2px;
            }}
        """
        
        self.setStyleSheet(style)


class ModernTabWidget(QTabWidget):
    """Widget de pestañas moderno."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        self._setup_style()
    
    def _setup_style(self):
        """Configurar estilos de las pestañas."""
        style = f"""
            QTabWidget::pane {{
                border: 1px solid {self.theme.get_color('border')};
                background: {self.theme.get_color('background')};
                border-radius: 8px;
                margin-top: -1px;
            }}
            
            QTabBar::tab {{
                background: {self.theme.get_color('surface')};
                color: {self.theme.get_color('text_secondary')};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid {self.theme.get_color('border')};
                border-bottom: none;
                font-size: 14px;
                font-weight: 500;
            }}
            
            QTabBar::tab:selected {{
                background: {self.theme.get_color('background')};
                color: {self.theme.get_color('primary')};
                border-color: {self.theme.get_color('border')};
                border-bottom: 2px solid {self.theme.get_color('primary')};
            }}
            
            QTabBar::tab:hover:!selected {{
                background: {self.theme.get_color('surface_hover')};
                color: {self.theme.get_color('text_primary')};
            }}
        """
        
        self.setStyleSheet(style)


class ModernComponents:
    """Factoría de componentes UI modernos."""
    
    @staticmethod
    def create_button(text: str, button_type: str = "primary", 
                     icon: Optional[QIcon] = None) -> ModernButton:
        """Crear botón moderno."""
        return ModernButton(text, button_type, icon)
    
    @staticmethod
    def create_line_edit(placeholder: str = "") -> ModernLineEdit:
        """Crear campo de entrada moderno."""
        return ModernLineEdit(placeholder)
    
    @staticmethod
    def create_combo_box(items: Optional[List[str]] = None) -> ModernComboBox:
        """Crear combo box moderno."""
        combo = ModernComboBox()
        if items:
            combo.addItems(items)
        return combo
    
    @staticmethod
    def create_table(rows: int = 0, columns: int = 0, 
                    headers: Optional[List[str]] = None) -> ModernTable:
        """Crear tabla moderna."""
        table = ModernTable(rows, columns)
        if headers:
            table.setHorizontalHeaderLabels(headers)
        return table
    
    @staticmethod
    def create_card(title: str = "") -> ModernCard:
        """Crear tarjeta moderna."""
        return ModernCard(title)
    
    @staticmethod
    def create_progress_bar() -> ModernProgressBar:
        """Crear barra de progreso moderna."""
        return ModernProgressBar()
    
    @staticmethod
    def create_tab_widget() -> ModernTabWidget:
        """Crear widget de pestañas moderno."""
        return ModernTabWidget()
    
    @staticmethod
    def create_search_box(placeholder: str = "Buscar...") -> QWidget:
        """Crear caja de búsqueda moderna con ícono."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Campo de búsqueda
        search_field = ModernLineEdit(placeholder)
        
        # Botón de búsqueda
        search_button = ModernButton("🔍", "secondary")
        search_button.setMaximumWidth(40)
        
        layout.addWidget(search_field)
        layout.addWidget(search_button)
        
        # Exponer el campo para acceso externo
        container.search_field = search_field
        container.search_button = search_button
        
        return container
    
    @staticmethod
    def create_button_panel(buttons: List[Dict[str, Any]]) -> QWidget:
        """Crear panel de botones moderno."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        created_buttons = []
        for button_config in buttons:
            button = ModernButton(
                button_config.get('text', ''),
                button_config.get('type', 'secondary'),
                button_config.get('icon')
            )
            
            if button_config.get('callback'):
                button.clicked.connect(button_config['callback'])
            
            layout.addWidget(button)
            created_buttons.append(button)
        
        # Espaciador para empujar botones a la izquierda
        layout.addStretch()
        
        # Exponer botones para acceso externo
        container.buttons = created_buttons
        
        return container
    
    @staticmethod
    def create_stats_card(title: str, value: str, subtitle: str = "", 
                         trend: Optional[str] = None) -> ModernCard:
        """Crear tarjeta de estadísticas moderna."""
        card = ModernCard()
        
        # Layout principal
        main_layout = QVBoxLayout()
        card.content_layout.addLayout(main_layout)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {get_current_theme().get_color('text_secondary')};
                margin-bottom: 4px;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: 700;
                color: {get_current_theme().get_color('text_primary')};
                margin-bottom: 4px;
            }}
        """)
        main_layout.addWidget(value_label)
        
        # Subtítulo y tendencia
        if subtitle or trend:
            bottom_layout = QHBoxLayout()
            
            if subtitle:
                subtitle_label = QLabel(subtitle)
                subtitle_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 12px;
                        color: {get_current_theme().get_color('text_secondary')};
                    }}
                """)
                bottom_layout.addWidget(subtitle_label)
            
            if trend:
                trend_color = get_current_theme().get_color('success') if trend.startswith('+') else get_current_theme().get_color('error')
                trend_label = QLabel(trend)
                trend_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 12px;
                        font-weight: 600;
                        color: {trend_color};
                    }}
                """)
                bottom_layout.addWidget(trend_label)
            
            bottom_layout.addStretch()
            main_layout.addLayout(bottom_layout)
        
        return card
    
    @staticmethod
    def apply_modern_theme(widget: QWidget, theme: Optional[ModernTheme] = None):
        """Aplicar tema moderno a un widget existente."""
        if not theme:
            theme = get_current_theme()
        
        # Aplicar estilos base al widget
        base_style = f"""
            QWidget {{
                background: {theme.get_color('background')};
                color: {theme.get_color('text_primary')};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
        """
        
        widget.setStyleSheet(base_style)


def toggle_dark_mode():
    """Alternar entre modo claro y oscuro globalmente."""
    global _current_theme
    _current_theme.toggle_dark_mode()
    
    # Notificar a la aplicación para actualizar estilos
    if QApplication.instance():
        # Re-aplicar estilos a todos los widgets
        for widget in QApplication.allWidgets():
            if hasattr(widget, '_setup_style'):
                widget._setup_style()


def set_theme(dark_mode: bool):
    """Establecer tema específico."""
    global _current_theme
    _current_theme = ModernTheme(dark_mode=dark_mode)


# Ejemplo de uso y testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # Crear ventana principal
    window = QMainWindow()
    window.setWindowTitle("Componentes UI Modernos - Rexus.app")
    window.setGeometry(100, 100, 800, 600)
    
    # Widget central
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Layout principal
    layout = QVBoxLayout(central_widget)
    
    # Crear componentes de ejemplo
    
    # Botones
    buttons = [
        {'text': 'Primario', 'type': 'primary'},
        {'text': 'Secundario', 'type': 'secondary'},
        {'text': 'Éxito', 'type': 'success'},
        {'text': 'Advertencia', 'type': 'warning'},
        {'text': 'Error', 'type': 'error'}
    ]
    button_panel = ModernComponents.create_button_panel(buttons)
    layout.addWidget(button_panel)
    
    # Caja de búsqueda
    search_box = ModernComponents.create_search_box("Buscar productos...")
    layout.addWidget(search_box)
    
    # Tarjetas de estadísticas
    stats_layout = QHBoxLayout()
    
    stats1 = ModernComponents.create_stats_card(
        "Productos Totales", "1,247", "En inventario", "+12%"
    )
    stats2 = ModernComponents.create_stats_card(
        "Valor Total", "$45,289", "USD", "+8.3%"
    )
    stats3 = ModernComponents.create_stats_card(
        "Productos Críticos", "23", "Bajo mínimo", "-5%"
    )
    
    stats_layout.addWidget(stats1)
    stats_layout.addWidget(stats2)
    stats_layout.addWidget(stats3)
    layout.addLayout(stats_layout)
    
    # Tabla moderna
    table = ModernComponents.create_table(5, 4, ['ID', 'Producto', 'Stock', 'Precio'])
    layout.addWidget(table)
    
    # Barra de progreso
    progress = ModernComponents.create_progress_bar()
    progress.setValue(65)
    layout.addWidget(progress)
    
    # Botón para alternar tema
    theme_button = ModernComponents.create_button("🌙 Modo Oscuro", "secondary")
    theme_button.clicked.connect(lambda: toggle_dark_mode())
    layout.addWidget(theme_button)
    
    window.show()
    sys.exit(app.exec())