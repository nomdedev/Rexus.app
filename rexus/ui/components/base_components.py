"""
Base Components - Rexus.app v2.0.0

Componentes UI base para consistencia entre módulos.
Proporciona widgets estándar con estilos unificados y funcionalidad común.
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QFrame, QHBoxLayout, QVBoxLayout,
    QGridLayout, QHeaderView, QWidget, QMessageBox, QProgressBar,
    QTabWidget, QSplitter, QTextEdit, QCheckBox, QRadioButton
)


class RexusColors:
    """Paleta de colores estándar para Rexus.app"""
    
    # Colores principales
    PRIMARY = "#2E86AB"        # Azul principal
    PRIMARY_LIGHT = "#A8DADC"  # Azul claro
    PRIMARY_DARK = "#1D5F8A"   # Azul oscuro
    
    # Colores secundarios
    SECONDARY = "#457B9D"      # Azul grisáceo
    ACCENT = "#F1FAEE"         # Blanco crema
    
    # Colores de estado
    SUCCESS = "#2D5016"        # Verde éxito
    WARNING = "#F77F00"        # Naranja advertencia
    ERROR = "#C73E1D"          # Rojo error
    INFO = "#3F88C5"           # Azul información
    
    # Colores neutros
    BACKGROUND = "#F8F9FA"     # Fondo principal
    SURFACE = "#FFFFFF"        # Superficie de widgets
    BORDER = "#DEE2E6"         # Bordes
    TEXT = "#212529"           # Texto principal
    TEXT_SECONDARY = "#6C757D" # Texto secundario
    DISABLED = "#ADB5BD"       # Elementos deshabilitados


class RexusFonts:
    """Tipografías estándar para Rexus.app"""
    
    @staticmethod
    def get_title_font(size: int = 14) -> QFont:
        """Fuente para títulos"""
        font = QFont("Segoe UI", size)
        font.setWeight(QFont.Weight.Bold)
        return font
    
    @staticmethod
    def get_subtitle_font(size: int = 12) -> QFont:
        """Fuente para subtítulos"""
        font = QFont("Segoe UI", size)
        font.setWeight(QFont.Weight.DemiBold)
        return font
    
    @staticmethod
    def get_body_font(size: int = 10) -> QFont:
        """Fuente para texto normal"""
        return QFont("Segoe UI", size)
    
    @staticmethod
    def get_code_font(size: int = 9) -> QFont:
        """Fuente para código y monospace"""
        return QFont("Consolas", size)


class RexusButton(QPushButton):
    """Botón estándar de Rexus con estilos unificados"""
    
    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_button()
    
    def _setup_button(self):
        """Configura el estilo del botón"""
        self.setFont(RexusFonts.get_body_font(10))
        self.setMinimumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Aplicar estilo según el tipo
        styles = {
            "primary": f"""
                QPushButton {{
                    background-color: {RexusColors.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {RexusColors.PRIMARY_DARK};
                }}
                QPushButton:pressed {{
                    background-color: {RexusColors.PRIMARY_DARK};
                }}
                QPushButton:disabled {{
                    background-color: {RexusColors.DISABLED};
                    color: white;
                }}
            """,
            "secondary": f"""
                QPushButton {{
                    background-color: {RexusColors.SURFACE};
                    color: {RexusColors.TEXT};
                    border: 1px solid {RexusColors.BORDER};
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {RexusColors.ACCENT};
                    border-color: {RexusColors.PRIMARY};
                }}
                QPushButton:pressed {{
                    background-color: {RexusColors.PRIMARY_LIGHT};
                }}
                QPushButton:disabled {{
                    background-color: {RexusColors.DISABLED};
                    color: {RexusColors.TEXT_SECONDARY};
                    border-color: {RexusColors.DISABLED};
                }}
            """,
            "success": f"""
                QPushButton {{
                    background-color: {RexusColors.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1e3a0e;
                }}
            """,
            "warning": f"""
                QPushButton {{
                    background-color: {RexusColors.WARNING};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #d6690a;
                }}
            """,
            "error": f"""
                QPushButton {{
                    background-color: {RexusColors.ERROR};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #a02914;
                }}
            """
        }
        
        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))


class RexusLabel(QLabel):
    """Label estándar con tipografía unificada"""
    
    def __init__(self, text: str = "", label_type: str = "body", parent=None):
        super().__init__(text, parent)
        self.label_type = label_type
        self._setup_label()
    
    def _setup_label(self):
        """Configura el estilo del label"""
        if self.label_type == "title":
            self.setFont(RexusFonts.get_title_font(16))
            self.setStyleSheet(f"color: {RexusColors.TEXT}; font-weight: bold;")
        elif self.label_type == "subtitle":
            self.setFont(RexusFonts.get_subtitle_font(13))
            self.setStyleSheet(f"color: {RexusColors.TEXT}; font-weight: 600;")
        elif self.label_type == "caption":
            self.setFont(RexusFonts.get_body_font(9))
            self.setStyleSheet(f"color: {RexusColors.TEXT_SECONDARY};")
        else:  # body
            self.setFont(RexusFonts.get_body_font(10))
            self.setStyleSheet(f"color: {RexusColors.TEXT};")


class RexusLineEdit(QLineEdit):
    """Campo de entrada estándar"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._setup_input()
    
    def _setup_input(self):
        """Configura el estilo del input"""
        self.setFont(RexusFonts.get_body_font(10))
        self.setMinimumHeight(32)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {RexusColors.SURFACE};
                border: 1px solid {RexusColors.BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                color: {RexusColors.TEXT};
            }}
            QLineEdit:focus {{
                border-color: {RexusColors.PRIMARY};
                outline: none;
            }}
            QLineEdit:disabled {{
                background-color: {RexusColors.ACCENT};
                color: {RexusColors.TEXT_SECONDARY};
                border-color: {RexusColors.DISABLED};
            }}
        """)


class RexusComboBox(QComboBox):
    """ComboBox estándar"""
    
    def __init__(self, items: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        self._setup_combo()
    
    def _setup_combo(self):
        """Configura el estilo del combo"""
        self.setFont(RexusFonts.get_body_font(10))
        self.setMinimumHeight(32)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {RexusColors.SURFACE};
                border: 1px solid {RexusColors.BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                color: {RexusColors.TEXT};
            }}
            QComboBox:focus {{
                border-color: {RexusColors.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {RexusColors.SURFACE};
                border: 1px solid {RexusColors.BORDER};
                selection-background-color: {RexusColors.PRIMARY_LIGHT};
                outline: none;
            }}
        """)


class RexusTable(QTableWidget):
    """Tabla estándar con estilos unificados"""
    
    def __init__(self, rows: int = 0, columns: int = 0, parent=None):
        super().__init__(rows, columns, parent)
        self._setup_table()
    
    def _setup_table(self):
        """Configura el estilo de la tabla"""
        self.setFont(RexusFonts.get_body_font(9))
        
        # Configuración del header
        self.horizontalHeader().setFont(RexusFonts.get_subtitle_font(10))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        
        # Configuración de selección
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Aplicar estilos
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RexusColors.SURFACE};
                alternate-background-color: {RexusColors.ACCENT};
                border: 1px solid {RexusColors.BORDER};
                border-radius: 6px;
                gridline-color: {RexusColors.BORDER};
                color: {RexusColors.TEXT};
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {RexusColors.PRIMARY_LIGHT};
                color: {RexusColors.TEXT};
            }}
            QHeaderView::section {{
                background-color: {RexusColors.SECONDARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 6px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 6px;
            }}
        """)


class RexusGroupBox(QGroupBox):
    """GroupBox estándar para agrupar controles"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        self._setup_group()
    
    def _setup_group(self):
        """Configura el estilo del grupo"""
        self.setFont(RexusFonts.get_subtitle_font(11))
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 2px solid {RexusColors.BORDER};
                border-radius: 8px;
                margin: 12px 0px 0px 0px;
                padding: 12px;
                color: {RexusColors.TEXT};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 8px 0px 8px;
                background-color: {RexusColors.BACKGROUND};
                color: {RexusColors.PRIMARY};
            }}
        """)


class RexusFrame(QFrame):
    """Frame estándar para separación visual"""
    
    def __init__(self, frame_type: str = "card", parent=None):
        super().__init__(parent)
        self.frame_type = frame_type
        self._setup_frame()
    
    def _setup_frame(self):
        """Configura el estilo del frame"""
        if self.frame_type == "card":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {RexusColors.SURFACE};
                    border: 1px solid {RexusColors.BORDER};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
        elif self.frame_type == "separator":
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFrameShadow(QFrame.Shadow.Sunken)
            self.setStyleSheet(f"""
                QFrame {{
                    color: {RexusColors.BORDER};
                    background-color: {RexusColors.BORDER};
                }}
            """)
        else:  # default
            self.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {RexusColors.BORDER};
                    border-radius: 4px;
                }}
            """)


class RexusProgressBar(QProgressBar):
    """Barra de progreso estándar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_progress()
    
    def _setup_progress(self):
        """Configura el estilo de la barra"""
        self.setTextVisible(True)
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {RexusColors.ACCENT};
                border: 1px solid {RexusColors.BORDER};
                border-radius: 6px;
                text-align: center;
                color: {RexusColors.TEXT};
                font-weight: 500;
            }}
            QProgressBar::chunk {{
                background-color: {RexusColors.PRIMARY};
                border-radius: 5px;
            }}
        """)


class RexusMessageBox:
    """Mensajes estándar con estilos unificados"""
    
    @staticmethod
    def information(parent, title: str, message: str):
        """Mensaje informativo"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {RexusColors.SURFACE};
                color: {RexusColors.TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {RexusColors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {RexusColors.PRIMARY_DARK};
            }}
        """)
        return msg.exec()
    
    @staticmethod
    def warning(parent, title: str, message: str):
        """Mensaje de advertencia"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {RexusColors.SURFACE};
                color: {RexusColors.TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {RexusColors.WARNING};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #d6690a;
            }}
        """)
        return msg.exec()
    
    @staticmethod
    def error(parent, title: str, message: str):
        """Mensaje de error"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {RexusColors.SURFACE};
                color: {RexusColors.TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {RexusColors.ERROR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #a02914;
            }}
        """)
        return msg.exec()
    
    @staticmethod
    def question(parent, title: str, message: str):
        """Mensaje de confirmación"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {RexusColors.SURFACE};
                color: {RexusColors.TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {RexusColors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {RexusColors.PRIMARY_DARK};
            }}
        """)
        return msg.exec()


class RexusLayoutHelper:
    """Utilidades para crear layouts estándar"""
    
    @staticmethod
    def create_form_layout(items: List[tuple]) -> QGridLayout:
        """Crea un layout de formulario estándar"""
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        for i, (label_text, widget) in enumerate(items):
            label = RexusLabel(label_text, "body")
            layout.addWidget(label, i, 0)
            layout.addWidget(widget, i, 1)
        
        return layout
    
    @staticmethod
    def create_button_layout(buttons: List[QPushButton], alignment: str = "right") -> QHBoxLayout:
        """Crea un layout de botones estándar"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        if alignment == "center":
            layout.addStretch()
        
        for button in buttons:
            layout.addWidget(button)
        
        if alignment == "left":
            layout.addStretch()
        elif alignment == "center":
            layout.addStretch()
        
        return layout
    
    @staticmethod
    def create_toolbar_layout(actions: List[QPushButton]) -> QHBoxLayout:
        """Crea un layout de barra de herramientas"""
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        for action in actions:
            layout.addWidget(action)
        
        layout.addStretch()  # Push buttons to the left
        
        return layout