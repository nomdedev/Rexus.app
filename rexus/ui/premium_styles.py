"""
Premium Styles - Rexus.app v2.0.0

Sistema de estilos premium y modernos para todos los formularios y componentes.
Garantiza una experiencia visual consistente y profesional.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPalette, QColor


class PremiumStyleManager:
    """Manager de estilos premium para toda la aplicación."""

    # Paleta de colores premium
    COLORS = {
        # Colores primarios
        'PRIMARY': '#3b82f6',           # Azul moderno
        'PRIMARY_HOVER': '#2563eb',     # Azul hover
        'PRIMARY_ACTIVE': '#1d4ed8',    # Azul activo
        'PRIMARY_LIGHT': '#dbeafe',     # Azul claro

        # Colores secundarios
        'SECONDARY': '#64748b',         # Gris moderno
        'SECONDARY_HOVER': '#475569',   # Gris hover
        'SECONDARY_LIGHT': '#f1f5f9',   # Gris muy claro

        # Estados
        'SUCCESS': '#16a34a',           # Verde éxito
        'SUCCESS_LIGHT': '#dcfce7',     # Verde claro
        'WARNING': '#f59e0b',           # Amarillo warning
        'WARNING_LIGHT': '#fef3c7',     # Amarillo claro
        'ERROR': '#ef4444',             # Rojo error
        'ERROR_LIGHT': '#fee2e2',       # Rojo claro
        'INFO': '#8b5cf6',              # Púrpura info
        'INFO_LIGHT': '#e9d5ff',        # Púrpura claro

        # Neutros
        'WHITE': '#ffffff',
        'BLACK': '#000000',
        'GRAY_50': '#f9fafb',
        'GRAY_100': '#f3f4f6',
        'GRAY_200': '#e5e7eb',
        'GRAY_300': '#d1d5db',
        'GRAY_400': '#9ca3af',
        'GRAY_500': '#6b7280',
        'GRAY_600': '#4b5563',
        'GRAY_700': '#374151',
        'GRAY_800': '#1f2937',
        'GRAY_900': '#111827',

        # Fondos
        'BACKGROUND': '#ffffff',
        'BACKGROUND_DARK': '#f8fafc',
        'BACKGROUND_DARKER': '#f1f5f9',
        'SURFACE': '#ffffff',
        'SURFACE_HOVER': '#f8fafc',

        # Bordes
        'BORDER': '#e2e8f0',
        'BORDER_LIGHT': '#f1f5f9',
        'BORDER_FOCUS': '#3b82f6',

        # Texto
        'TEXT_PRIMARY': '#1e293b',
        'TEXT_SECONDARY': '#64748b',
        'TEXT_MUTED': '#94a3b8',
        'TEXT_ON_PRIMARY': '#ffffff',

        # Selección
        'SELECTION': '#dbeafe',
        'SELECTION_TEXT': '#1e40af',

        # Alternancia
        'ALTERNATE_ROW': '#f8fafc',
    }

    @classmethod
    def get_premium_dialog_style(cls) -> str:
        """Retorna estilos premium para diálogos."""
        return f"""
        QDialog {{
            background-color: {cls.COLORS['BACKGROUND']};
            color: {cls.COLORS['TEXT_PRIMARY']};
            font-family: "Segoe UI", "San Francisco", "Helvetica Neue", sans-serif;
            font-size: 13px;
        }}

        /* Estilos para GroupBox */
        QGroupBox {{
            font-weight: 600;
            font-size: 14px;
            color: {cls.COLORS['TEXT_PRIMARY']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 16px;
            padding-left: 4px;
            padding-right: 4px;
            padding-bottom: 8px;
            background-color: {cls.COLORS['SURFACE']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 2px;
            padding: 0 8px;
            background-color: {cls.COLORS['BACKGROUND']};
            color: {cls.COLORS['PRIMARY']};
            font-weight: 700;
        }}

        /* Estilos para Tabs */
        QTabWidget::pane {{
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 10px;
            background-color: {cls.COLORS['SURFACE']};
            padding: 8px;
        }}

        QTabBar::tab {{
            background-color: {cls.COLORS['SECONDARY_LIGHT']};
            color: {cls.COLORS['TEXT_SECONDARY']};
            border: 1px solid {cls.COLORS['BORDER']};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
            min-width: 120px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.COLORS['PRIMARY']};
            color: {cls.COLORS['TEXT_ON_PRIMARY']};
            border-bottom-color: {cls.COLORS['PRIMARY']};
            margin-bottom: -1px;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {cls.COLORS['PRIMARY_LIGHT']};
            color: {cls.COLORS['PRIMARY']};
        }}

        /* Estilos para botones */
        QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['PRIMARY']},
                stop: 1 #2563eb);
            color: {cls.COLORS['TEXT_ON_PRIMARY']};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
            min-height: 18px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['PRIMARY_HOVER']},
                stop: 1 {cls.COLORS['PRIMARY']});
            transform: translateY(-1px);
        }}

        QPushButton:pressed {{
            background: {cls.COLORS['PRIMARY_ACTIVE']};
            transform: translateY(0px);
        }}

        QPushButton:disabled {{
            background-color: {cls.COLORS['GRAY_300']};
            color: {cls.COLORS['GRAY_500']};
        }}

        /* Botones específicos por tipo */
        QPushButton[buttonType="success"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['SUCCESS']},
                stop: 1 #15803d);
        }}

        QPushButton[buttonType="warning"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['WARNING']},
                stop: 1 #d97706);
        }}

        QPushButton[buttonType="error"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['ERROR']},
                stop: 1 #dc2626);
        }}

        QPushButton[buttonType="secondary"] {{
            background-color: {cls.COLORS['SECONDARY_LIGHT']};
            color: {cls.COLORS['TEXT_PRIMARY']};
            border: 2px solid {cls.COLORS['BORDER']};
        }}

        QPushButton[buttonType="secondary"]:hover {{
            background-color: {cls.COLORS['GRAY_200']};
            border-color: {cls.COLORS['SECONDARY']};
        }}

        /* Campos de entrada */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['SURFACE']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            color: {cls.COLORS['TEXT_PRIMARY']};
            selection-background-color: {cls.COLORS['SELECTION']};
            selection-color: {cls.COLORS['SELECTION_TEXT']};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.COLORS['BORDER_FOCUS']};
            background-color: {cls.COLORS['WHITE']};
            outline: 2px solid rgba(59, 130, 246, 0.2);
            outline-offset: -1px;
        }}

        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {cls.COLORS['SECONDARY']};
        }}

        QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {{
            color: {cls.COLORS['TEXT_MUTED']};
            font-style: italic;
        }}

        /* ComboBox */
        QComboBox {{
            background-color: {cls.COLORS['SURFACE']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            color: {cls.COLORS['TEXT_PRIMARY']};
            min-height: 20px;
        }}

        QComboBox:focus {{
            border-color: {cls.COLORS['BORDER_FOCUS']};
            background-color: {cls.COLORS['WHITE']};
        }}

        QComboBox:hover {{
            border-color: {cls.COLORS['SECONDARY']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border: 5px solid transparent;
            border-top: 6px solid {cls.COLORS['TEXT_SECONDARY']};
            width: 0px;
            height: 0px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['SURFACE']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            padding: 4px;
            selection-background-color: {cls.COLORS['SELECTION']};
            selection-color: {cls.COLORS['SELECTION_TEXT']};
        }}

        /* SpinBox y DoubleSpinBox */
        QSpinBox, QDoubleSpinBox {{
            background-color: {cls.COLORS['SURFACE']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            color: {cls.COLORS['TEXT_PRIMARY']};
            min-height: 20px;
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {cls.COLORS['BORDER_FOCUS']};
            background-color: {cls.COLORS['WHITE']};
        }}

        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {cls.COLORS['SECONDARY']};
        }}

        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {cls.COLORS['SECONDARY_LIGHT']};
            border: 1px solid {cls.COLORS['BORDER']};
            width: 20px;
            border-radius: 4px;
        }}

        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {cls.COLORS['PRIMARY_LIGHT']};
        }}

        /* DateEdit */
        QDateEdit {{
            background-color: {cls.COLORS['SURFACE']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            color: {cls.COLORS['TEXT_PRIMARY']};
            min-height: 20px;
        }}

        QDateEdit:focus {{
            border-color: {cls.COLORS['BORDER_FOCUS']};
            background-color: {cls.COLORS['WHITE']};
        }}

        QDateEdit:hover {{
            border-color: {cls.COLORS['SECONDARY']};
        }}

        QDateEdit::drop-down {{
            background-color: {cls.COLORS['PRIMARY']};
            border: none;
            border-radius: 4px;
            width: 25px;
        }}

        /* CheckBox */
        QCheckBox {{
            color: {cls.COLORS['TEXT_PRIMARY']};
            font-size: 13px;
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 4px;
            background-color: {cls.COLORS['SURFACE']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {cls.COLORS['PRIMARY']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['PRIMARY']};
            border-color: {cls.COLORS['PRIMARY']};
            image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 9.293l6.646-6.647a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e");
        }}

        /* TableWidget */
        QTableWidget {{
            background-color: {cls.COLORS['SURFACE']};
            alternate-background-color: {cls.COLORS['ALTERNATE_ROW']};
            gridline-color: {cls.COLORS['BORDER_LIGHT']};
            border: 2px solid {cls.COLORS['BORDER']};
            border-radius: 8px;
            selection-background-color: {cls.COLORS['SELECTION']};
            selection-color: {cls.COLORS['SELECTION_TEXT']};
        }}

        QTableWidget::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {cls.COLORS['BORDER_LIGHT']};
            color: {cls.COLORS['TEXT_PRIMARY']};
        }}

        QTableWidget::item:selected {{
            background-color: {cls.COLORS['SELECTION']};
            color: {cls.COLORS['SELECTION_TEXT']};
        }}

        QTableWidget::item:hover {{
            background-color: {cls.COLORS['SURFACE_HOVER']};
        }}

        QHeaderView::section {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {cls.COLORS['GRAY_100']},
                stop: 1 {cls.COLORS['GRAY_200']});
            color: {cls.COLORS['TEXT_PRIMARY']};
            font-weight: 600;
            border: 1px solid {cls.COLORS['BORDER']};
            padding: 8px 12px;
        }}

        QHeaderView::section:hover {{
            background-color: {cls.COLORS['PRIMARY_LIGHT']};
            color: {cls.COLORS['PRIMARY']};
        }}

        /* ScrollBar */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['GRAY_100']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['GRAY_400']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['GRAY_500']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        /* Labels */
        QLabel {{
            color: {cls.COLORS['TEXT_PRIMARY']};
            font-size: 13px;
        }}

        QLabel[labelType="title"] {{
            font-size: 18px;
            font-weight: 700;
            color: {cls.COLORS['PRIMARY']};
        }}

        QLabel[labelType="subtitle"] {{
            font-size: 15px;
            font-weight: 600;
            color: {cls.COLORS['TEXT_PRIMARY']};
        }}

        QLabel[labelType="caption"] {{
            font-size: 11px;
            color: {cls.COLORS['TEXT_MUTED']};
        }}

        /* Frames */
        QFrame {{
            background-color: {cls.COLORS['SURFACE']};
            border-radius: 8px;
        }}

        QFrame[frameType="card"] {{
            background-color: {cls.COLORS['SURFACE']};
            border: 1px solid {cls.COLORS['BORDER']};
            border-radius: 10px;
            padding: 16px;
        }}

        QFrame[frameType="separator"] {{
            background-color: {cls.COLORS['BORDER']};
            max-height: 1px;
            border: none;
        }}
        """

    @classmethod
    def get_premium_main_window_style(cls) -> str:
        """Retorna estilos premium para ventanas principales."""
        return f"""
        QMainWindow {{
            background-color: {cls.COLORS['BACKGROUND_DARK']};
            color: {cls.COLORS['TEXT_PRIMARY']};
            font-family: "Segoe UI", "San Francisco", "Helvetica Neue", sans-serif;
        }}

        QMainWindow::separator {{
            background-color: {cls.COLORS['BORDER']};
            width: 2px;
            height: 2px;
        }}

        QMainWindow::separator:hover {{
            background-color: {cls.COLORS['PRIMARY']};
        }}

        /* Sidebar premium */
        QFrame[frameType="sidebar"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {cls.COLORS['WHITE']},
                stop: 1 {cls.COLORS['GRAY_50']});
            border-right: 2px solid {cls.COLORS['BORDER']};
        }}

        /* Content area */
        QFrame[frameType="content"] {{
            background-color: {cls.COLORS['BACKGROUND']};
            border-radius: 12px;
            margin: 8px;
        }}
        """

    @classmethod
    def apply_premium_style_to_widget(cls, widget: QWidget):
        """Aplica estilos premium a un widget específico."""
        if hasattr(widget, 'setStyleSheet'):
            if 'Dialog' in widget.__class__.__name__:
                widget.setStyleSheet(cls.get_premium_dialog_style())
            elif 'MainWindow' in widget.__class__.__name__:
                widget.setStyleSheet(cls.get_premium_main_window_style())

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Obtiene un color de la paleta."""
        return cls.COLORS.get(color_name.upper(), cls.COLORS['PRIMARY'])

    @classmethod
    def create_gradient_button_style(cls, color: str, hover_color: str) -> str:
        """Crea estilo de botón con gradiente personalizado."""
        return f"""
        QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {color}, stop: 1 {hover_color});
            color: {cls.COLORS['TEXT_ON_PRIMARY']};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
            min-height: 18px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {hover_color}, stop: 1 {color});
            transform: translateY(-1px);
        }}
        QPushButton:pressed {{
            background: {hover_color};
            transform: translateY(0px);
        }}
        """


def apply_premium_styles_globally():
    """Aplica estilos premium a toda la aplicación."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        # Aplicar estilo global
        app.setStyleSheet(PremiumStyleManager.get_premium_dialog_style())

        # Configurar paleta de colores
        palette = app.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PremiumStyleManager.COLORS['BACKGROUND']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PremiumStyleManager.COLORS['TEXT_PRIMARY']))
        palette.setColor(QPalette.ColorRole.Base, QColor(PremiumStyleManager.COLORS['SURFACE']))
        palette.setColor(QPalette.ColorRole.Text, QColor(PremiumStyleManager.COLORS['TEXT_PRIMARY']))
        palette.setColor(QPalette.ColorRole.Button, QColor(PremiumStyleManager.COLORS['PRIMARY']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(PremiumStyleManager.COLORS['TEXT_ON_PRIMARY']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(PremiumStyleManager.COLORS['SELECTION']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(PremiumStyleManager.COLORS['SELECTION_TEXT']))
        app.setPalette(palette)
