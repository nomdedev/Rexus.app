"""
Base Components - Rexus.app v2.0.0

Componentes base para la UI de Rexus con estilos unificados y funcionalidad común.
Proporciona widgets estándar con estilos consistentes entre módulos.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)


class RexusColors:
    """Paleta de colores estándar para Rexus.app"""

    # Colores principales
    PRIMARY = "#2E86AB"  # Azul principal
    PRIMARY_LIGHT = "#A8DADC"  # Azul claro
    PRIMARY_DARK = "#1D5F8A"  # Azul oscuro

    # Colores secundarios
    SECONDARY = "#457B9D"  # Azul grisáceo
    ACCENT = "#F1FAEE"  # Blanco crema

    # Colores de estado
    SUCCESS = "#2D5016"  # Verde éxito
    WARNING = "#F77F00"  # Naranja advertencia
    ERROR = "#C73E1D"  # Rojo error
    INFO = "#3F88C5"  # Azul información

    # Colores neutros
    BACKGROUND = "#F8F9FA"  # Fondo principal
    BACKGROUND_LIGHT = "#FFFFFF"  # Fondo claro
    SURFACE = "#FFFFFF"  # Superficie de widgets
    BORDER = "#DEE2E6"  # Bordes
    BORDER_LIGHT = "#E9ECEF"  # Bordes claros
    BORDER_DARK = "#ADB5BD"  # Bordes oscuros
    TEXT = "#212529"  # Texto principal
    TEXT_PRIMARY = "#212529"  # Texto principal (alias)
    TEXT_SECONDARY = "#6C757D"  # Texto secundario
    TEXT_ACCENT = "#3F88C5"  # Texto de acento
    TEXT_LIGHT = "#ADB5BD"  # Texto claro
    TEXT_DARK = "#1A1A1A"  # Texto oscuro
    TEXT_WHITE = "#FFFFFF"  # Texto blanco
    TEXT_DISABLED = "#ADB5BD"  # Texto deshabilitado (alias de TEXT_LIGHT)
    DISABLED = "#ADB5BD"  # Elementos deshabilitados

    # Colores de estado extendidos para compatibilidad
    SUCCESS_LIGHT = "#d4edda"  # Verde claro
    SUCCESS_DARK = "#1e3a0e"  # Verde oscuro
    WARNING_LIGHT = "#fff3cd"  # Amarillo claro
    WARNING_DARK = "#856404"  # Amarillo oscuro
    ERROR_LIGHT = "#f8d7da"  # Rojo claro
    ERROR_DARK = "#a02914"  # Rojo oscuro
    DANGER = "#C73E1D"  # Alias para ERROR
    DANGER_LIGHT = "#f8d7da"  # Rojo claro (alias)
    DANGER_DARK = "#a02914"  # Rojo oscuro (alias)
    INFO_LIGHT = "#d1ecf1"  # Azul claro
    INFO_DARK = "#0c5460"  # Azul oscuro


class RexusFonts:
    """Tipografías estándar para Rexus.app"""

    # Constantes de fuentes
    FAMILY = "Segoe UI"
    BODY_SIZE = 13
    TITLE_SIZE = 16
    SUBTITLE_SIZE = 14

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

    def __init__(self,
text: str = "",
        button_type: str = "primary",
        parent=None):
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
            """,
        }

        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))

    def cleanup(self):
        """Limpia las conexiones y referencias de manera segura"""
        try:
            # Desconectar todas las señales
            self.clicked.disconnect()
        except:
            pass  # Ignorar si no hay conexiones

        # NOTA: setParent(None) puede causar errores "wrapped C/C++ object deleted"
        # Solo limpiar parent si realmente es necesario para evitar memory leaks
        # try:
        #     if self.parent():
        #         self.setParent(None)
        # except:
        #     pass

    def __del__(self):
        """Destructor seguro"""
        try:
            self.cleanup()
        except:
            pass


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
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
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
    def create_horizontal_layout(spacing: int = 8, margins: tuple = None) -> QHBoxLayout:
        """Crea un layout horizontal estándar"""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        if margins:
            layout.setContentsMargins(margins[0],
margins[1],
                margins[2],
                margins[3])
        return layout

    @staticmethod
    def create_vertical_layout(spacing: int = 8, margins: tuple = None) -> QVBoxLayout:
        """Crea un layout vertical estándar"""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        if margins:
            layout.setContentsMargins(margins[0],
margins[1],
                margins[2],
                margins[3])
        return layout

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
    def create_button_layout(
        buttons: List[QPushButton], alignment: str = "right"
    ) -> QHBoxLayout:
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


# Añadir métodos de compatibilidad a las clases existentes
RexusLabel.apply_icon_style = lambda self, color_type="primary": None
RexusLabel.apply_subtitle_style = lambda self, color_type="primary": None
RexusLabel.apply_stat_value_style = lambda self, color_type="primary": None
RexusButton.apply_action_button_style = lambda self: None
RexusLineEdit.apply_search_style = lambda self: None
RexusComboBox.apply_filter_style = lambda self: None
RexusColors.get_background_color = classmethod(lambda cls, color_type: cls.get_background_color_static(color_type))
RexusColors.get_text_color = classmethod(lambda cls, color_type: cls.get_text_color_static(color_type))

# Métodos estáticos de compatibilidad para RexusColors
@classmethod
def get_background_color_static(cls, color_type):
    """Método estático para obtener colores de fondo."""
    colors = {
        'primary': cls.PRIMARY_LIGHT,
        'success': "#d4edda",
        'warning': "#fff3cd",
        'danger': "#f8d7da",
        'info': cls.PRIMARY_LIGHT
    }
    from PyQt6.QtGui import QColor
    return QColor(colors.get(color_type, colors['primary']))

@classmethod
def get_text_color_static(cls, color_type):
    """Método estático para obtener colores de texto."""
    colors = {
        'primary': cls.PRIMARY,
        'success': cls.SUCCESS,
        'warning': "#856404",
        'danger': cls.ERROR,
        'info': cls.INFO
    }
    from PyQt6.QtGui import QColor
    return QColor(colors.get(color_type, colors['primary']))

RexusColors.get_background_color_static = get_background_color_static
RexusColors.get_text_color_static = get_text_color_static

# Añadir método setup_columns a RexusTable
def setup_columns_method(self, columnas):
    """Configura columnas de la tabla con compatibilidad."""
    self.setColumnCount(len(columnas))

    headers = []
    for i, columna in enumerate(columnas):
        header_text = f"{columna.get('icono', '')} {columna.get('titulo', '')}"
        headers.append(header_text.strip())

        # Configurar ancho
        if columna.get('ancho', 0) > 0:
            self.setColumnWidth(i, columna['ancho'])
        elif columna.get('ancho') == -1:
            header = self.horizontalHeader()
            if header:
                header.setStretchLastSection(True)

    self.setHorizontalHeaderLabels(headers)

RexusTable.setup_columns = setup_columns_method

class RexusSpinBox(QSpinBox):
    """SpinBox con estilo Rexus"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """Configura el estilo del SpinBox"""
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {RexusColors.SURFACE};
                border: 1px solid {RexusColors.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                color: {RexusColors.TEXT};
                min-height: 20px;
            }}

            QSpinBox:focus {{
                border: 2px solid {RexusColors.PRIMARY};
                background-color: {RexusColors.ACCENT};
            }}

            QSpinBox:disabled {{
                background-color: {RexusColors.BACKGROUND};
                color: {RexusColors.DISABLED};
                border-color: {RexusColors.DISABLED};
            }}

            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {RexusColors.BORDER};
                border-radius: 0 6px 0 0;
                background-color: {RexusColors.BACKGROUND};
            }}

            QSpinBox::up-button:hover {{
                background-color: {RexusColors.PRIMARY_LIGHT};
            }}

            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid {RexusColors.BORDER};
                border-radius: 0 0 6px 0;
                background-color: {RexusColors.BACKGROUND};
            }}

            QSpinBox::down-button:hover {{
                background-color: {RexusColors.PRIMARY_LIGHT};
            }}
        """)

        # Configuración por defecto
        self.setMinimum(1)
        self.setMaximum(9999)
        self.setValue(1)

    # Métodos de compatibilidad para el sistema Inventario migrado
    def apply_icon_style(self, color_type="primary"):
        """Aplica estilo de icono para compatibilidad."""
        pass  # Los estilos ya están aplicados

    def apply_subtitle_style(self, color_type="primary"):
        """Aplica estilo de subtítulo para compatibilidad."""
        pass  # Los estilos ya están aplicados

    def apply_stat_value_style(self, color_type="primary"):
        """Aplica estilo de valor estadístico para compatibilidad."""
        pass  # Los estilos ya están aplicados

    def apply_action_button_style(self):
        """Aplica estilo para botones de acción en tabla."""
        pass  # Los estilos ya están aplicados

    def apply_search_style(self):
        """Aplica estilo de campo de búsqueda."""
        pass  # Los estilos ya están aplicados

    def apply_filter_style(self):
        """Aplica estilo de filtro."""
        pass  # Los estilos ya están aplicados

    def setup_columns(self, columnas):
        """Configura columnas de la tabla con compatibilidad."""
        self.setColumnCount(len(columnas))

        headers = []
        for i, columna in enumerate(columnas):
            header_text = f"{columna.get('icono', '')} {columna.get('titulo', '')}"
            headers.append(header_text.strip())

            # Configurar ancho
            if columna.get('ancho', 0) > 0:
                self.setColumnWidth(i, columna['ancho'])
            elif columna.get('ancho') == -1:
                header = self.horizontalHeader()
                if header:
                    header.setStretchLastSection(True)

        self.setHorizontalHeaderLabels(headers)

    @classmethod
    def get_background_color(cls, color_type):
        """Método de compatibilidad para obtener colores de fondo."""
        colors = {
            'primary': cls.PRIMARY_LIGHT,
            'success': "#d4edda",
            'warning': "#fff3cd",
            'danger': "#f8d7da",
            'info': cls.PRIMARY_LIGHT
        }
        from PyQt6.QtGui import QColor
        return QColor(colors.get(color_type, colors['primary']))

    @classmethod
    def get_text_color(cls, color_type):
        """Método de compatibilidad para obtener colores de texto."""
        colors = {
            'primary': cls.PRIMARY,
            'success': cls.SUCCESS,
            'warning': "#856404",
            'danger': cls.ERROR,
            'info': cls.INFO
        }
        from PyQt6.QtGui import QColor
        return QColor(colors.get(color_type, colors['primary']))


class RexusCheckBox(QCheckBox):
    """CheckBox estándar de Rexus con estilos unificados."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.apply_theme()

    def apply_theme(self):
        """Aplica el tema estándar al CheckBox."""
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {RexusColors.TEXT_PRIMARY};
                font: {RexusFonts.BODY_SIZE}px "{RexusFonts.FAMILY}";
                spacing: 8px;
                padding: 4px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {RexusColors.BORDER};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {RexusColors.PRIMARY};
                border-color: {RexusColors.PRIMARY};
            }}
            QCheckBox::indicator:hover {{
                border-color: {RexusColors.PRIMARY_LIGHT};
            }}
        """)


class RexusRadioButton(QRadioButton):
    """RadioButton estándar de Rexus con estilos unificados."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.apply_theme()

    def apply_theme(self):
        """Aplica el tema estándar al RadioButton."""
        self.setStyleSheet(f"""
            QRadioButton {{
                color: {RexusColors.TEXT_PRIMARY};
                font: {RexusFonts.BODY_SIZE}px "{RexusFonts.FAMILY}";
                spacing: 8px;
                padding: 4px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {RexusColors.BORDER};
                border-radius: 9px;
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {RexusColors.PRIMARY};
                border-color: {RexusColors.PRIMARY};
            }}
            QRadioButton::indicator:hover {{
                border-color: {RexusColors.PRIMARY_LIGHT};
            }}
        """)


class RexusTabWidget(QTabWidget):
    """TabWidget estándar de Rexus con estilos unificados."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apply_theme()

    def apply_theme(self):
        """Aplica el tema estándar al TabWidget."""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {RexusColors.BORDER};
                background-color: white;
                border-radius: 6px;
                margin-top: -1px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: {RexusColors.BACKGROUND_LIGHT};
                color: {RexusColors.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid {RexusColors.BORDER};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font: {RexusFonts.BODY_SIZE}px "{RexusFonts.FAMILY}";
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {RexusColors.PRIMARY};
                color: white;
                border-color: {RexusColors.PRIMARY};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {RexusColors.PRIMARY_LIGHT};
                color: {RexusColors.PRIMARY_DARK};
            }}
            QTabBar::tab:first {{
                margin-left: 0px;
            }}
        """)


class RexusTextEdit(QTextEdit):
    """TextEdit estándar de Rexus con estilos unificados."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apply_theme()

    def apply_theme(self):
        """Aplica el tema estándar al TextEdit."""
        self.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {RexusColors.BORDER};
                border-radius: 6px;
                padding: 12px;
                font: {RexusFonts.BODY_SIZE}px "{RexusFonts.FAMILY}";
                color: {RexusColors.TEXT_PRIMARY};
                background-color: white;
                selection-background-color: {RexusColors.PRIMARY_LIGHT};
                min-height: 100px;
            }}
            QTextEdit:focus {{
                border-color: {RexusColors.PRIMARY};
                background-color: {RexusColors.ACCENT};
            }}
            QTextEdit:disabled {{
                background-color: {RexusColors.BACKGROUND_LIGHT};
                color: {RexusColors.TEXT_DISABLED};
                border-color: {RexusColors.BORDER_LIGHT};
            }}
        """)
