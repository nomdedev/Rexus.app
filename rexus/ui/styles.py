"""
Módulo de utilidades para estilos QSS
Centraliza todos los estilos de la aplicación
"""

from src.core.config import UI_CONFIG


def get_base_styles():
    """Retorna los estilos base para toda la aplicación"""
    colors = UI_CONFIG["colors"]
    typography = UI_CONFIG["typography"]

    return f"""
    QWidget {{
        font-family: {typography['family']};
        font-size: {typography['size_normal']}px;
        color: {colors['text_primary']};
    }}

    QDialog {{
        background-color: white;
        border-radius: {UI_CONFIG['borders']['radius']}px;
    }}

    QPushButton {{
        background-color: {colors['button_primary']};
        color: white;
        border: none;
        border-radius: {UI_CONFIG['borders']['button_radius']}px;
        padding: {UI_CONFIG['button']['padding_horizontal']}px;
        font-weight: {typography['weight_medium']};
        min-width: {UI_CONFIG['button']['min_width']}px;
        min-height: {UI_CONFIG['button']['min_height']}px;
    }}

    QPushButton:hover {{
        background-color: #1d4ed8;
    }}

    QPushButton:pressed {{
        background-color: #1e40af;
    }}

    QPushButton[buttonType="secondary"] {{
        background-color: {colors['button_secondary']};
        color: {colors['text_primary']};
    }}

    QPushButton[buttonType="secondary"]:hover {{
        background-color: #e2e8f0;
    }}

    QLineEdit {{
        border: 2px solid #e2e8f0;
        border-radius: {UI_CONFIG['borders']['radius']}px;
        padding: 8px 12px;
        font-size: {typography['size_normal']}px;
    }}

    QLineEdit:focus {{
        border-color: {colors['button_primary']};
    }}

    QLabel[labelType="title"] {{
        font-size: {typography['size_title']}px;
        font-weight: {typography['weight_semibold']};
        color: {colors['text_primary']};
    }}

    QLabel[labelType="error"] {{
        color: {colors['text_error']};
        font-weight: {typography['weight_medium']};
    }}

    QLabel[labelType="success"] {{
        color: {colors['text_success']};
        font-weight: {typography['weight_medium']};
    }}

    QLabel[labelType="warning"] {{
        color: {colors['text_warning']};
        font-weight: {typography['weight_medium']};
    }}
    """


def get_shadow_effect():
    """Retorna el efecto de sombra estándar para widgets"""
    from PyQt6.QtGui import QColor
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 160))
    return shadow
