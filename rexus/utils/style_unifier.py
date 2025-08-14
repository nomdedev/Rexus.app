"""
StyleUnifier - Centralizador de estilos comunes para toda la aplicación.
Evita duplicación de código CSS y asegura consistencia visual.

Autor: Sistema Rexus
Fecha: 13/08/2025
"""

class StyleUnifier:
    """Centralizador de estilos comunes para todos los módulos"""

    # Estándares de tamaños unificados
    SIZES = {
        'tab_height': 24,
        'tab_min_width': 80,
        'tab_padding': '8px 12px',
        'button_height': 32,
        'button_padding': '8px 16px',
        'input_height': 28,
        'input_padding': '6px 12px',
        'header_height': 22,
        'font_size_normal': 12,
        'font_size_small': 10,
        'margin_normal': 12,
        'margin_small': 8,
    }

    # Colores estándar (material design inspired)
    COLORS = {
        'primary': '#3b82f6',
        'primary_hover': '#2563eb',
        'surface': '#f8fafc',
        'surface_hover': '#f1f5f9',
        'background': '#ffffff',
        'border': '#e5e7eb',
        'border_active': '#3b82f6',
        'text_primary': '#1f2937',
        'text_secondary': '#6b7280',
        'text_muted': '#9ca3af',
    }

    @classmethod
    def get_standard_tab_style(cls, custom_colors=None):
        """
        Retorna el estilo estándar para QTabWidget/QTabBar

        Args:
            custom_colors (dict): Colores personalizados para sobrescribir los por defecto
        """
        colors = cls.COLORS.copy()
        if custom_colors:
            colors.update(custom_colors)

        return f"""
            QTabWidget {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {colors['surface']};
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: {cls.SIZES['tab_padding']};
                margin-right: 2px;
                font-weight: 500;
                min-width: {cls.SIZES['tab_min_width']}px;
                min-height: {cls.SIZES['tab_height']}px;
                max-height: {cls.SIZES['tab_height']}px;
                font-size: {cls.SIZES['font_size_normal']}px;
            }}
            QTabBar::tab:selected {{
                background: {colors['background']};
                color: {colors['text_primary']};
                border-color: {colors['border']};
                border-bottom: 3px solid {colors['primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                background: {colors['surface_hover']};
                color: {colors['text_primary']};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-top: none;
                background: {colors['background']};
                border-radius: 0 0 8px 8px;
            }}
        """

    @classmethod
    def get_standard_button_style(cls, custom_colors=None):
        """
        Retorna el estilo estándar para QPushButton

        Args:
            custom_colors (dict): Colores personalizados para sobrescribir los por defecto
        """
        colors = cls.COLORS.copy()
        if custom_colors:
            colors.update(custom_colors)

        return f"""
            QPushButton {{
                background: {colors['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: {cls.SIZES['button_padding']};
                font-size: {cls.SIZES['font_size_normal']}px;
                font-weight: 500;
                min-height: {cls.SIZES['button_height']}px;
                max-height: {cls.SIZES['button_height']}px;
            }}
            QPushButton:hover {{
                background: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background: {colors['primary_hover']};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background: {colors['text_muted']};
                color: white;
            }}
        """

    @classmethod
    def get_standard_input_style(cls, custom_colors=None):
        """
        Retorna el estilo estándar para QLineEdit/QTextEdit

        Args:
            custom_colors (dict): Colores personalizados para sobrescribir los por defecto
        """
        colors = cls.COLORS.copy()
        if custom_colors:
            colors.update(custom_colors)

        return f"""
            QLineEdit, QTextEdit {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: {cls.SIZES['input_padding']};
                font-size: {cls.SIZES['font_size_normal']}px;
                background: {colors['background']};
                color: {colors['text_primary']};
                min-height: {cls.SIZES['input_height']}px;
                max-height: {cls.SIZES['input_height']}px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['border_active']};
                outline: none;
            }}
            QLineEdit:disabled, QTextEdit:disabled {{
                background: {colors['surface']};
                color: {colors['text_muted']};
            }}
        """

    @classmethod
    def get_standard_table_style(cls, custom_colors=None):
        """
        Retorna el estilo estándar para QTableWidget

        Args:
            custom_colors (dict): Colores personalizados para sobrescribir los por defecto
        """
        colors = cls.COLORS.copy()
        if custom_colors:
            colors.update(custom_colors)

        return f"""
            QTableWidget {{
                border: 1px solid {colors['border']};
                border-radius: 6px;
                background: {colors['background']};
                gridline-color: {colors['border']};
                font-size: {cls.SIZES['font_size_normal']}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {colors['border']};
            }}
            QTableWidget::item:selected {{
                background: {colors['primary']};
                color: white;
            }}
            QHeaderView::section {{
                background: {colors['surface']};
                border: none;
                border-bottom: 2px solid {colors['border']};
                padding: 8px;
                font-weight: 600;
                font-size: {cls.SIZES['font_size_normal']}px;
                color: {colors['text_primary']};
                min-height: {cls.SIZES['header_height']}px;
                max-height: {cls.SIZES['header_height']}px;
            }}
        """

    @classmethod
    def get_compact_layout_margins(cls):
        """Retorna márgenes compactos estándar"""
        return {
            'small': (cls.SIZES['margin_small'], cls.SIZES['margin_small'],
                     cls.SIZES['margin_small'], cls.SIZES['margin_small']),
            'normal': (cls.SIZES['margin_normal'], cls.SIZES['margin_normal'],
                      cls.SIZES['margin_normal'], cls.SIZES['margin_normal']),
            'spacing_small': cls.SIZES['margin_small'],
            'spacing_normal': cls.SIZES['margin_normal'],
        }

    @classmethod
    def apply_to_widget(cls, widget, style_type="tab", custom_colors=None):
        """
        Aplica un estilo estándar a un widget específico

        Args:
            widget: El widget al que aplicar el estilo
            style_type (str): Tipo de estilo ('tab',
'button',
                'input',
                'table')
            custom_colors (dict): Colores personalizados
        """
        style_map = {
            'tab': cls.get_standard_tab_style,
            'button': cls.get_standard_button_style,
            'input': cls.get_standard_input_style,
            'table': cls.get_standard_table_style,
        }

        if style_type in style_map:
            style = style_map[style_type](custom_colors)
            widget.setStyleSheet(style)
        else:
            raise ValueError(f"Tipo de estilo no soportado: {style_type}")

# Constantes de acceso rápido
STANDARD_TAB_STYLE = StyleUnifier.get_standard_tab_style()
STANDARD_BUTTON_STYLE = StyleUnifier.get_standard_button_style()
STANDARD_INPUT_STYLE = StyleUnifier.get_standard_input_style()
STANDARD_TABLE_STYLE = StyleUnifier.get_standard_table_style()
COMPACT_MARGINS = StyleUnifier.get_compact_layout_margins()
