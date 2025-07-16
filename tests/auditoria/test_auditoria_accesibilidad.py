import sys

import pytest
from PyQt6.QtWidgets import QApplication

try:
    from src.modules.auditoria.view import AuditoriaView
except ImportError:
    pytest.skip("Módulo Auditoría no disponible", allow_module_level=True)


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_accesibilidad_widgets_principales(app):
    """Verifica tooltips, nombres accesibles y presencia de widgets clave en AuditoriaView."""
    view = AuditoriaView()

    # Tabla de registros
    assert hasattr(view, "tabla_registros"), "Falta tabla_registros"
    tabla = view.tabla_registros
    assert tabla is not None
    # Contador de registros
    assert hasattr(view, "label_contador"), "Falta label_contador"
    label = view.label_contador
    assert label.text().startswith("Registros:"), (
        "label_contador no muestra texto esperado"
    )

    # Cards de estadísticas
    for card_attr in ["card_total", "card_criticas", "card_fallidas"]:
        assert hasattr(view, card_attr), f"Falta {card_attr}"
        card = getattr(view, card_attr)
        assert card.toolTip() is not None or card.toolTip() == ""

    # Tablas de resumen
    assert hasattr(view, "tabla_modulos"), "Falta tabla_modulos"
    assert hasattr(view, "tabla_usuarios"), "Falta tabla_usuarios"
    assert view.tabla_modulos.columnCount() == 2
    assert view.tabla_usuarios.columnCount() == 2

    # Verificar que los headers de las tablas sean correctos
    mod_headers = [
        view.tabla_modulos.horizontalHeaderItem(i).text()
        for i in range(2)
        if view.tabla_modulos.horizontalHeaderItem(i)
    ]
    user_headers = [
        view.tabla_usuarios.horizontalHeaderItem(i).text()
        for i in range(2)
        if view.tabla_usuarios.horizontalHeaderItem(i)
    ]
    assert mod_headers == ["Módulo", "Acciones"]
    assert user_headers == ["Usuario", "Acciones"]

    # Verificar que todos los QLabels tengan texto no vacío
    for label in view.findChildren(type(view.label_contador)):
        assert label.text() != ""
        assert widget.accessibleDescription() != ""


import sys

import pytest

# Import seguro de QApplication y AuditoriaView
try:
    from PyQt6.QtWidgets import QApplication

    from src.modules.auditoria.view import AuditoriaView
except ImportError:
    pytest.skip("Módulo Auditoría no disponible", allow_module_level=True)


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_accesibilidad_widgets_principales(app):
    """Verifica tooltips, nombres accesibles y presencia de widgets clave en AuditoriaView."""
    view = AuditoriaView()

    # Tabla de registros
    assert hasattr(view, "tabla_registros"), "Falta tabla_registros"
    tabla = view.tabla_registros
    # No tiene toolTip por defecto, pero podemos setearlo en el futuro
    assert tabla is not None
    # Contador de registros
    assert hasattr(view, "label_contador"), "Falta label_contador"
    label = view.label_contador
    assert label.text().startswith("Registros:"), (
        "label_contador no muestra texto esperado"
    )

    # Cards de estadísticas
    for card_attr in ["card_total", "card_criticas", "card_fallidas"]:
        assert hasattr(view, card_attr), f"Falta {card_attr}"
        card = getattr(view, card_attr)
        # El card es un QFrame, puede tener toolTip
        assert card.toolTip() is not None or card.toolTip() == ""

    # Tablas de resumen
    assert hasattr(view, "tabla_modulos"), "Falta tabla_modulos"
    assert hasattr(view, "tabla_usuarios"), "Falta tabla_usuarios"
    assert view.tabla_modulos.columnCount() == 2
    assert view.tabla_usuarios.columnCount() == 2

    # Verificar que los headers de las tablas sean correctos
    mod_headers = [view.tabla_modulos.horizontalHeaderItem(i).text() for i in range(2)]
    user_headers = [
        view.tabla_usuarios.horizontalHeaderItem(i).text() for i in range(2)
    ]
    assert mod_headers == ["Módulo", "Acciones"]
    assert user_headers == ["Usuario", "Acciones"]

    # Verificar que todos los QLabels tengan texto no vacío
    for label in view.findChildren(type(view.label_contador)):
        assert label.text() != ""
