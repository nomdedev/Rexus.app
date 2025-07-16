import pytest

from src.ui.styles import get_base_styles, get_shadow_effect


class DummyConfig:
    """Config dummy para testear estilos sin depender de UI_CONFIG real."""

    colors = {
        "text_primary": "#222",
        "button_primary": "#1976d2",
        "button_secondary": "#e0e0e0",
        "text_error": "#e53935",
        "text_success": "#43a047",
        "text_warning": "#fbc02d",
    }
    typography = {
        "family": "Arial",
        "size_normal": 14,
        "size_title": 22,
        "weight_medium": 500,
        "weight_semibold": 600,
    }
    borders = {
        "radius": 8,
        "button_radius": 6,
    }
    button = {
        "padding_horizontal": 12,
        "min_width": 80,
        "min_height": 32,
    }


@pytest.fixture(autouse=True)
def patch_ui_config(monkeypatch):
    # Parchea UI_CONFIG para los tests
    monkeypatch.setattr(
        "src.ui.styles.UI_CONFIG",
        {
            "colors": DummyConfig.colors,
            "typography": DummyConfig.typography,
            "borders": DummyConfig.borders,
            "button": DummyConfig.button,
        },
    )


def test_get_base_styles():
    styles = get_base_styles()
    # Debe contener los selectores principales
    for selector in [
        "QWidget",
        "QPushButton",
        "QLineEdit",
        'QLabel[labelType="title"]',
    ]:
        assert selector in styles
    # Verifica dinámicamente que todos los valores de la config dummy estén presentes en el QSS
    config_dict = {
        **DummyConfig.colors,
        **DummyConfig.typography,
        **DummyConfig.borders,
        **DummyConfig.button,
    }
    for key, value in config_dict.items():
        # Si es int, conviértelo a str
        if isinstance(value, int):
            value = str(value)
        assert value in styles, (
            f"El valor '{value}' de la clave '{key}' no está en el QSS generado"
        )


def test_get_shadow_effect():
    shadow = get_shadow_effect()
    # Debe ser una instancia de QGraphicsDropShadowEffect
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect

    assert isinstance(shadow, QGraphicsDropShadowEffect)
    # Debe tener los valores configurados
    assert shadow.blurRadius() == 15
    assert shadow.xOffset() == 0
    assert shadow.yOffset() == 4
    color = shadow.color()
    assert color.alpha() == 160
    assert color.red() == 0 and color.green() == 0 and color.blue() == 0
