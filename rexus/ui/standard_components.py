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

Componentes UI Estandarizados para Rexus.app
Proporciona componentes consistentes para todos los módulos.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QFrame, QGroupBox, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QVBoxLayout, QHeaderView
)


class StandardComponents:
    """Factoría de componentes UI estandarizados."""
    
    # Colores estándar de la aplicación
    COLORS = {
        'primary': '#1e40af',
        'secondary': '#3b82f6', 
        'success': '#059669',
        'warning': '#d97706',
        'danger': '#dc2626',
        'light': '#f8fafc',
        'dark': '#1e293b',
        'border': '#e2e8f0'
    }
    
    # Fuentes estándar
    FONTS = {
        'title': ('Segoe UI', 16, QFont.Weight.Bold),
        'subtitle': ('Segoe UI', 14, QFont.Weight.Normal),
        'body': ('Segoe UI', 13, QFont.Weight.Normal),
        'caption': ('Segoe UI', 11, QFont.Weight.Normal)
    }
    
    @classmethod
    def create_title(cls, text: str, parent_layout: QVBoxLayout) -> QLabel:
        """Crea un título estandarizado para módulos."""
        title_frame = QFrame()
        title_frame.setFrameStyle(QFrame.Shape.Box)
        title_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {cls.COLORS['primary']}, stop:1 {cls.COLORS['secondary']});
                border: none;
                border-radius: 8px;
                margin-bottom: 10px;
                padding: 5px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel(text)
        font = QFont(*cls.FONTS['title'])
        title_label.setFont(font)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        parent_layout.addWidget(title_frame)
        return title_label
    
    @classmethod 
    def create_control_panel(cls) -> QFrame:
        """Crea un panel de control estandarizado."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
        panel.setStyleSheet(f"""
            QFrame {{
                background: {cls.COLORS['light']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }}
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        return panel
    
    @classmethod
    def create_primary_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón primario estandarizado."""
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {cls.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: {cls.COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background: #1e3a8a;
            }}
            QPushButton:disabled {{
                background: #94a3b8;
                color: #64748b;
            }}
        """)
        
        return button
    
    @classmethod
    def create_secondary_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón secundario estandarizado."""
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {cls.COLORS['dark']};
                border: 2px solid {cls.COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                border-color: {cls.COLORS['primary']};
                color: {cls.COLORS['primary']};
                background: {cls.COLORS['light']};
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['border']};
                border-color: {cls.COLORS['secondary']};
            }}
            QPushButton:disabled {{
                background: #f1f5f9;
                border-color: #cbd5e1;
                color: #94a3b8;
            }}
        """)
        
        return button
    
    @classmethod
    def create_danger_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón de peligro estandarizado."""
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {cls.COLORS['danger']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: #b91c1c;
            }}
            QPushButton:pressed {{
                background: #991b1b;
            }}
            QPushButton:disabled {{
                background: #94a3b8;
                color: #64748b;
            }}
        """)
        
        return button
    
    @classmethod
    def create_success_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón de éxito estandarizado.""" 
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {cls.COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: #047857;
            }}
            QPushButton:pressed {{
                background: #065f46;
            }}
            QPushButton:disabled {{
                background: #94a3b8;
                color: #64748b;
            }}
        """)
        
        return button
    
    @classmethod
    def create_info_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón de información estandarizado."""
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {cls.COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: {cls.COLORS['primary']};
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['dark']};
            }}
            QPushButton:disabled {{
                background: #94a3b8;
                color: #cbd5e1;
            }}
        """)
        
        return button
    
    @classmethod
    def create_warning_button(cls, text: str, icon_path: str = None) -> QPushButton:
        """Crea un botón de advertencia estandarizado."""
        button = QPushButton(text)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {cls.COLORS['warning']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
                min-height: 28px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: #e68900;
            }}
            QPushButton:pressed {{
                background: #cc7700;
            }}
            QPushButton:disabled {{
                background: #94a3b8;
                color: #cbd5e1;
            }}
        """)
        
        return button
    
    @classmethod
    def create_standard_label(cls, text: str, style: str = 'body') -> QLabel:
        """Crea un label estandarizado."""
        label = QLabel(text)
        
        # Obtener fuente según el estilo
        font_info = cls.FONTS.get(style, cls.FONTS['body'])
        font = QFont(*font_info)
        label.setFont(font)
        
        # Aplicar estilos según el tipo
        if style == 'title':
            label.setStyleSheet(f"""
                QLabel {{
                    color: {cls.COLORS['dark']};
                    background: transparent;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
            """)
        elif style == 'subtitle':
            label.setStyleSheet(f"""
                QLabel {{
                    color: {cls.COLORS['dark']};
                    background: transparent;
                    font-weight: 600;
                    margin-bottom: 6px;
                }}
            """)
        elif style == 'caption':
            label.setStyleSheet(f"""
                QLabel {{
                    color: #64748b;
                    background: transparent;
                    font-size: 11px;
                }}
            """)
        else:  # body por defecto
            label.setStyleSheet(f"""
                QLabel {{
                    color: {cls.COLORS['dark']};
                    background: transparent;
                    font-size: 13px;
                    padding: 2px 4px;
                }}
            """)
        
        return label
    
    @classmethod
    def create_standard_table(cls) -> QTableWidget:
        """Crea una tabla ultra compacta y sin color de fondo."""
        table = QTableWidget()
        table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                alternate-background-color: transparent;
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                gridline-color: {cls.COLORS['border']};
                selection-background-color: #3b82f6;
                selection-color: white;
                font-size: 11px;
                font-weight: normal;
            }}
            QTableWidget::item {{
                padding: 2px 4px;
                border-bottom: 1px solid {cls.COLORS['border']};
                font-size: 11px;
                font-weight: normal;
                background: transparent;
                color: #1e293b;
            }}
            QTableWidget::item:selected {{
                background: #3b82f6;
                color: white;
            }}
            QHeaderView::section {{
                background: transparent;
                color: #374151;
                padding: 2px 4px;
                border: none;
                border-right: 1px solid #eee;
                border-bottom: 1px solid #eee;
                font-weight: normal;
                font-size: 10px;
            }}
            QHeaderView::section:hover {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.COLORS['border']};
                border-radius: 4px;
                min-height: 10px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #bdbdbd;
            }}
        """)
        table.setAlternatingRowColors(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setShowGrid(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.verticalHeader().setVisible(False)
        return table
    
    @classmethod
    def create_group_box(cls, title: str) -> QGroupBox:
        """Crea un group box estandarizado."""
        group = QGroupBox(title)
        
        font = QFont(*cls.FONTS['subtitle'])
        group.setFont(font)
        
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {cls.COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 5px 10px;
                background: {cls.COLORS['primary']};
                color: white;
                border-radius: 4px;
                font-size: 14px;
            }}
        """)
        
        return group