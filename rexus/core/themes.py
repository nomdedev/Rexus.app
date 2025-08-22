"""
Sistema de Temas Moderno para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

# Tema por defecto
DEFAULT_THEME = "light"

@dataclass
class ColorPalette:
    """Paleta de colores para un tema"""
    # Colores base
    primary: str
    secondary: str
    background: str
    surface: str
    surface_variant: str

    # Colores de texto
    on_primary: str
    on_secondary: str
    on_background: str
    on_surface: str
    on_surface_variant: str

    # Colores de estado
    success: str
    warning: str
    error: str
    info: str

    # Colores de borde y sombra
    border: str
    border_focus: str
    shadow: str
    overlay: str

    # Colores específicos de UI
    sidebar_bg: str
    sidebar_active: str
    sidebar_hover: str
    header_bg: str
    input_bg: str
    button_hover: str
    button_active: str
    card_bg: str

    def to_dict(self) -> Dict[str, str]:
        """Convertir a diccionario para fácil acceso"""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "background": self.background,
            "surface": self.surface,
            "surface_variant": self.surface_variant,
            "on_primary": self.on_primary,
            "on_secondary": self.on_secondary,
            "on_background": self.on_background,
            "on_surface": self.on_surface,
            "on_surface_variant": self.on_surface_variant,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
            "border": self.border,
            "border_focus": self.border_focus,
            "shadow": self.shadow,
            "overlay": self.overlay,
            "sidebar_bg": self.sidebar_bg,
            "sidebar_active": self.sidebar_active,
            "sidebar_hover": self.sidebar_hover,
            "header_bg": self.header_bg,
            "input_bg": self.input_bg,
            "button_hover": self.button_hover,
            "button_active": self.button_active,
            "card_bg": self.card_bg
        }

# Tema Light (Material Design 3 inspirado)
LIGHT_THEME = ColorPalette(
    primary="#2563eb",
    secondary="#64748b",
    background="#ffffff",
    surface="#f8fafc",
    surface_variant="#f1f5f9",
    on_primary="#ffffff",
    on_secondary="#ffffff",
    on_background="#0f172a",
    on_surface="#1e293b",
    on_surface_variant="#475569",
    success="#10b981",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",
    border="#e2e8f0",
    border_focus="#2563eb",
    shadow="rgba(0, 0, 0, 0.1)",
    overlay="rgba(0, 0, 0, 0.5)",
    sidebar_bg="#f8fafc",
    sidebar_active="#2563eb",
    sidebar_hover="#d1d5db",
    header_bg="#ffffff",
    input_bg="#ffffff",
    button_hover="#1d4ed8",
    button_active="#1e40af",
    card_bg="#ffffff"
)

# Tema Dark (Material Design 3 Dark)
DARK_THEME = ColorPalette(
    primary="#3b82f6",
    secondary="#64748b",
    background="#0f172a",
    surface="#1e293b",
    surface_variant="#334155",
    on_primary="#ffffff",
    on_secondary="#ffffff",
    on_background="#f8fafc",
    on_surface="#e2e8f0",
    on_surface_variant="#cbd5e1",
    success="#22c55e",
    warning="#fbbf24",
    error="#f87171",
    info="#60a5fa",
    border="#334155",
    border_focus="#3b82f6",
    shadow="rgba(0, 0, 0, 0.3)",
    overlay="rgba(0, 0, 0, 0.7)",
    sidebar_bg="#1e293b",
    sidebar_active="#3b82f6",
    sidebar_hover="#475569",
    header_bg="#1e293b",
    input_bg="#334155",
    button_hover="#2563eb",
    button_active="#1d4ed8",
    card_bg="#1e293b"
)

# Tema Blue (Corporate)
BLUE_THEME = ColorPalette(
    primary="#1e40af",
    secondary="#475569",
    background="#f0f9ff",
    surface="#e0f2fe",
    surface_variant="#bae6fd",
    on_primary="#ffffff",
    on_secondary="#ffffff",
    on_background="#0c4a6e",
    on_surface="#0369a1",
    on_surface_variant="#0284c7",
    success="#059669",
    warning="#d97706",
    error="#dc2626",
    info="#0ea5e9",
    border="#7dd3fc",
    border_focus="#1e40af",
    shadow="rgba(30, 64, 175, 0.1)",
    overlay="rgba(30, 64, 175, 0.5)",
    sidebar_bg="#e0f2fe",
    sidebar_active="#1e40af",
    sidebar_hover="#bae6fd",
    header_bg="#f0f9ff",
    input_bg="#ffffff",
    button_hover="#1e3a8a",
    button_active="#1e3a8a",
    card_bg="#ffffff"
)

# Tema High Contrast (Accesibilidad)
HIGH_CONTRAST_THEME = ColorPalette(
    primary="#000000",
    secondary="#333333",
    background="#ffffff",
    surface="#ffffff",
    surface_variant="#f5f5f5",
    on_primary="#ffffff",
    on_secondary="#ffffff",
    on_background="#000000",
    on_surface="#000000",
    on_surface_variant="#000000",
    success="#006600",
    warning="#cc6600",
    error="#cc0000",
    info="#0066cc",
    border="#000000",
    border_focus="#000000",
    shadow="rgba(0, 0, 0, 0.5)",
    overlay="rgba(0, 0, 0, 0.8)",
    sidebar_bg="#f5f5f5",
    sidebar_active="#000000",
    sidebar_hover="#e5e5e5",
    header_bg="#ffffff",
    input_bg="#ffffff",
    button_hover="#333333",
    button_active="#666666",
    card_bg="#ffffff"
)

# Tema Green (Nature/Eco)
GREEN_THEME = ColorPalette(
    primary="#059669",
    secondary="#64748b",
    background="#f0fdf4",
    surface="#dcfce7",
    surface_variant="#bbf7d0",
    on_primary="#ffffff",
    on_secondary="#ffffff",
    on_background="#14532d",
    on_surface="#166534",
    on_surface_variant="#15803d",
    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",
    border="#86efac",
    border_focus="#059669",
    shadow="rgba(5, 150, 105, 0.1)",
    overlay="rgba(5, 150, 105, 0.5)",
    sidebar_bg="#dcfce7",
    sidebar_active="#059669",
    sidebar_hover="#bbf7d0",
    header_bg="#f0fdf4",
    input_bg="#ffffff",
    button_hover="#047857",
    button_active="#065f46",
    card_bg="#ffffff"
)

# Configuración de temas
THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "blue": BLUE_THEME,
    "high_contrast": HIGH_CONTRAST_THEME,
    "green": GREEN_THEME
}

# Metadatos de temas
THEME_METADATA = {
    "light": {
        "name": "Claro",
        "description": "Tema claro moderno con tonos azules",
        "icon": "[LIGHT]",
        "category": "standard"
    },
    "dark": {
        "name": "Oscuro",
        "description": "Tema oscuro elegante para uso nocturno",
        "icon": "[DARK]",
        "category": "standard"
    },
    "blue": {
        "name": "Azul Corporativo",
        "description": "Tema azul profesional para entornos empresariales",
        "icon": "🏢",
        "category": "professional"
    },
    "high_contrast": {
        "name": "Alto Contraste",
        "description": "Tema de alta accesibilidad con máximo contraste",
        "icon": "👁️",
        "category": "accessibility"
    },
    "green": {
        "name": "Verde Naturaleza",
        "description": "Tema verde inspirado en la naturaleza",
        "icon": "🌿",
        "category": "themed"
    }
}

def get_theme(theme_name: str) -> Optional[ColorPalette]:
    """Obtener tema por nombre"""
    return THEMES.get(theme_name)

def get_available_themes() -> Dict[str, Dict[str, Any]]:
    """Obtener lista de temas disponibles con metadata"""
    return {
        theme_id: {
            **metadata,
            "colors": theme.to_dict()
        }
        for theme_id, (theme, metadata) in zip(THEMES.keys(),
                                             [(theme, THEME_METADATA[theme_id])
                                              for theme_id, theme in THEMES.items()])
    }

def is_dark_theme(theme_name: str) -> bool:
    """Verificar si un tema es oscuro"""
    dark_themes = ["dark"]
    return theme_name in dark_themes

def get_theme_preview_colors(theme_name: str) -> Dict[str, str]:
    """Obtener colores principales para preview del tema"""
    theme = get_theme(theme_name)
    if not theme:
        return {}

    return {
        "primary": theme.primary,
        "background": theme.background,
        "surface": theme.surface,
        "text": theme.on_background
    }
