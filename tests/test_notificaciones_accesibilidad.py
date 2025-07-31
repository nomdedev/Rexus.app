# Imports seguros de módulos
try:
except ImportError:
    pytest.skip("Módulo no disponible")

# from rexus.modules.notificaciones.view import NotificacionesView # Movido a sección try/except

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from rexus.modules.notificaciones.view import NotificacionesView
import sys
import pytest


def test_notificaciones_accesibilidad_tooltips(app):
    view = NotificacionesView()
    # Botones principales
    boton_agregar = view.boton_agregar
    boton_leido = view.boton_marcar_leido
    assert boton_agregar.toolTip() == "Agregar notificación"
    assert boton_agregar.accessibleName() == "Botón de acción de notificaciones"
    assert boton_leido.toolTip() == "Marcar como leído"
    assert boton_leido.accessibleName() == "Botón de acción de notificaciones"
    # Tabla principal
    tabla = view.tabla_notificaciones
    assert tabla.toolTip() == "Tabla de notificaciones"
    assert tabla.accessibleName() == "Tabla principal de notificaciones"
    header = tabla.horizontalHeader()
    if header is not None:
        assert header.objectName() == "header_notificaciones"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Notificaciones"
