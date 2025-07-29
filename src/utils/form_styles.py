"""
Estilos mejorados para formularios - Rexus.app

Este módulo proporciona estilos consistentes y modernos para todos los formularios
de la aplicación.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ModernFormStyles:
    """Clase que contiene todos los estilos modernos para formularios."""

    # Paleta de colores moderna
    COLORS = {
        "primary": "#3498db",
        "primary_hover": "#2980b9",
        "secondary": "#95a5a6",
        "success": "#27ae60",
        "success_hover": "#219a52",
        "danger": "#e74c3c",
        "danger_hover": "#c0392b",
        "warning": "#f39c12",
        "warning_hover": "#e67e22",
        "background": "#f8f9fa",
        "surface": "#ffffff",
        "text_primary": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "border": "#bdc3c7",
        "border_focus": "#3498db",
        "shadow": "rgba(0, 0, 0, 0.1)",
    }

    @staticmethod
    def get_dialog_style():
        """Estilo base para diálogos."""
        return f"""
            QDialog {{
                background-color: {ModernFormStyles.COLORS["background"]};
                font-family: 'Segoe UI', 'System', sans-serif;
                font-size: 12px;
            }}
        """

    @staticmethod
    def get_form_input_style():
        """Estilo para campos de entrada (QLineEdit, QComboBox, etc.)."""
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QTextEdit {{
                padding: 10px 12px;
                border: 2px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 6px;
                background-color: {ModernFormStyles.COLORS["surface"]};
                font-size: 12px;
                color: {ModernFormStyles.COLORS["text_primary"]};
                selection-background-color: {ModernFormStyles.COLORS["primary"]};
                selection-color: white;
            }}
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {{
                border-color: {ModernFormStyles.COLORS["border_focus"]};
                background-color: white;
                outline: none;
            }}
            
            QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled,
            QDoubleSpinBox:disabled, QDateEdit:disabled, QTimeEdit:disabled, QTextEdit:disabled {{
                background-color: #f5f5f5;
                color: {ModernFormStyles.COLORS["text_secondary"]};
                border-color: #e0e0e0;
            }}
            
            /* Placeholder text styling */
            QLineEdit[placeholderText] {{
                color: {ModernFormStyles.COLORS["text_secondary"]};
            }}
            
            /* ComboBox dropdown styling */
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border: 6px solid transparent;
                border-top: 6px solid {ModernFormStyles.COLORS["text_secondary"]};
                margin-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 1px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 4px;
                background-color: white;
                selection-background-color: {ModernFormStyles.COLORS["primary"]};
                selection-color: white;
                outline: none;
            }}
        """

    @staticmethod
    def get_button_style(button_type="primary"):
        """Estilo para botones con diferentes tipos."""
        colors = {
            "primary": (
                ModernFormStyles.COLORS["primary"],
                ModernFormStyles.COLORS["primary_hover"],
            ),
            "success": (
                ModernFormStyles.COLORS["success"],
                ModernFormStyles.COLORS["success_hover"],
            ),
            "danger": (
                ModernFormStyles.COLORS["danger"],
                ModernFormStyles.COLORS["danger_hover"],
            ),
            "warning": (
                ModernFormStyles.COLORS["warning"],
                ModernFormStyles.COLORS["warning_hover"],
            ),
            "secondary": (ModernFormStyles.COLORS["secondary"], "#8c9599"),
        }

        bg_color, hover_color = colors.get(button_type, colors["primary"])

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-height: 20px;
                text-align: center;
            }}
            
            QPushButton:hover {{
                background-color: {hover_color};
                /* transform eliminado */
            }}
            
            QPushButton:pressed {{
                background-color: {hover_color};
                /* transform eliminado */
            }}
            
            QPushButton:disabled {{
                background-color: {ModernFormStyles.COLORS["secondary"]};
                color: #ffffff;
                opacity: 0.6;
            }}
        """

    @staticmethod
    def get_label_style(label_type="normal"):
        """Estilo para etiquetas con diferentes tipos."""
        styles = {
            "normal": f"""
                QLabel {{
                    color: {ModernFormStyles.COLORS["text_primary"]};
                    font-weight: 500;
                    font-size: 12px;
                    padding: 2px 0px;
                }}
            """,
            "title": f"""
                QLabel {{
                    color: {ModernFormStyles.COLORS["text_primary"]};
                    font-weight: 700;
                    font-size: 16px;
                    padding: 8px 0px;
                }}
            """,
            "subtitle": f"""
                QLabel {{
                    color: {ModernFormStyles.COLORS["text_secondary"]};
                    font-weight: 500;
                    font-size: 14px;
                    padding: 4px 0px;
                }}
            """,
            "error": f"""
                QLabel {{
                    color: {ModernFormStyles.COLORS["danger"]};
                    font-weight: 500;
                    font-size: 11px;
                    padding: 2px 0px;
                }}
            """,
        }

        return styles.get(label_type, styles["normal"])

    @staticmethod
    def get_group_box_style():
        """Estilo para QGroupBox."""
        return f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                color: {ModernFormStyles.COLORS["text_primary"]};
                border: 2px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: {ModernFormStyles.COLORS["surface"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {ModernFormStyles.COLORS["surface"]};
            }}
        """

    @staticmethod
    def get_table_style():
        """Estilo moderno para tablas."""
        return f"""
            QTableWidget {{
                gridline-color: {ModernFormStyles.COLORS["border"]};
                background-color: {ModernFormStyles.COLORS["surface"]};
                border: 1px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 6px;
                selection-background-color: {ModernFormStyles.COLORS["primary"]};
                selection-color: white;
                font-size: 11px;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {ModernFormStyles.COLORS["primary"]};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {ModernFormStyles.COLORS["background"]};
                color: {ModernFormStyles.COLORS["text_primary"]};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {ModernFormStyles.COLORS["border"]};
                font-weight: 600;
                font-size: 11px;
            }}
            
            QTableWidget::item:alternate {{
                background-color: #f8f9fa;
            }}
        """

    @staticmethod
    def get_tab_style():
        """Estilo moderno para pestañas."""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 8px;
                background-color: {ModernFormStyles.COLORS["surface"]};
                padding: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {ModernFormStyles.COLORS["background"]};
                color: {ModernFormStyles.COLORS["text_secondary"]};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid {ModernFormStyles.COLORS["border"]};
                border-bottom: none;
                font-weight: 500;
                min-width: 100px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {ModernFormStyles.COLORS["surface"]};
                color: {ModernFormStyles.COLORS["text_primary"]};
                border-bottom: 2px solid {ModernFormStyles.COLORS["primary"]};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover {{
                background-color: #e9ecef;
                color: {ModernFormStyles.COLORS["text_primary"]};
            }}
        """

    @staticmethod
    def get_scrollbar_style():
        """Estilo moderno para barras de desplazamiento."""
        return f"""
            QScrollBar:vertical {{
                border: none;
                background-color: {ModernFormStyles.COLORS["background"]};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {ModernFormStyles.COLORS["border"]};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {ModernFormStyles.COLORS["text_secondary"]};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {ModernFormStyles.COLORS["background"]};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {ModernFormStyles.COLORS["border"]};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {ModernFormStyles.COLORS["text_secondary"]};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
        """


class ModernFormBuilder:
    """Constructor de formularios modernos."""

    def __init__(self, parent_widget):
        """Inicializa el constructor con el widget padre."""
        self.parent = parent_widget
        self.form_layout = None
        self.main_layout = None

    def create_form_dialog(self, title, width=500, height=400):
        """Crea un diálogo de formulario moderno."""
        from PyQt6.QtWidgets import QDialog

        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(width, height)
        dialog.setStyleSheet(ModernFormStyles.get_dialog_style())

        # Layout principal
        self.main_layout = QVBoxLayout(dialog)
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(24, 24, 24, 24)

        return dialog

    def add_form_section(self, title=None):
        """Añade una nueva sección de formulario."""
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(ModernFormStyles.get_label_style("subtitle"))
            self.main_layout.addWidget(title_label)

        # Crear layout de formulario
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Frame contenedor para el formulario
        form_frame = QFrame()
        form_frame.setLayout(self.form_layout)
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernFormStyles.COLORS["surface"]};
                border: 1px solid {ModernFormStyles.COLORS["border"]};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        self.main_layout.addWidget(form_frame)
        return self.form_layout

    def add_form_field(self, label_text, widget, required=False, help_text=None):
        """Añade un campo al formulario actual."""
        if not self.form_layout:
            raise ValueError("Debe crear una sección de formulario primero")

        # Crear etiqueta
        label = QLabel(label_text + ("*" if required else ""))
        label.setStyleSheet(ModernFormStyles.get_label_style())

        # Aplicar estilos al widget
        widget.setStyleSheet(ModernFormStyles.get_form_input_style())

        # Añadir al formulario
        self.form_layout.addRow(label, widget)

        # Añadir texto de ayuda si existe
        if help_text:
            help_label = QLabel(help_text)
            help_label.setStyleSheet(ModernFormStyles.get_label_style("error"))
            help_label.setWordWrap(True)
            self.form_layout.addRow("", help_label)

    def add_button_row(self, buttons_config):
        """
        Añade una fila de botones al formulario.

        buttons_config: Lista de tuplas (texto, callback, tipo)
        Ejemplo: [("Guardar", self.save, "success"), ("Cancelar", self.cancel, "secondary")]
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()  # Empujar botones hacia la derecha

        for text, callback, button_type in buttons_config:
            button = QPushButton(text)
            button.setStyleSheet(ModernFormStyles.get_button_style(button_type))
            button.clicked.connect(callback)
            button_layout.addWidget(button)

        self.main_layout.addLayout(button_layout)

    def apply_global_styles(self, widget):
        """Aplica estilos globales a un widget."""
        combined_styles = (
            ModernFormStyles.get_form_input_style()
            + ModernFormStyles.get_group_box_style()
            + ModernFormStyles.get_table_style()
            + ModernFormStyles.get_tab_style()
            + ModernFormStyles.get_scrollbar_style()
        )

        widget.setStyleSheet(combined_styles)


# Funciones de conveniencia para aplicar estilos rápidamente
def apply_modern_form_styles(dialog):
    """Aplica estilos modernos a un diálogo de formulario."""
    dialog.setStyleSheet(
        ModernFormStyles.get_dialog_style()
        + ModernFormStyles.get_form_input_style()
        + ModernFormStyles.get_group_box_style()
    )


def apply_modern_button_style(button, button_type="primary"):
    """Aplica estilo moderno a un botón específico."""
    button.setStyleSheet(ModernFormStyles.get_button_style(button_type))


def apply_modern_table_style(table):
    """Aplica estilo moderno a una tabla."""
    table.setStyleSheet(ModernFormStyles.get_table_style())


def apply_modern_tab_style(tab_widget):
    """Aplica estilo moderno a un widget de pestañas."""
    tab_widget.setStyleSheet(ModernFormStyles.get_tab_style())
