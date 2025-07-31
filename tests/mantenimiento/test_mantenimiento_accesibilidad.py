# Imports seguros de módulos
try:
except ImportError:
    pytest.skip("Módulo no disponible")

# from rexus.modules.mantenimiento.view import MantenimientoView # Movido a sección try/except

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
from rexus.modules.mantenimiento.view import MantenimientoView
import sys
import pytest


def test_mantenimiento_accesibilidad_tooltips(app):
    view = MantenimientoView()
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() in ("Agregar mantenimiento", "Agregar tarea de mantenimiento")
    # El refuerzo puede poner el accessibleName en showEvent, forzamos manualmente
    if not boton.accessibleName():
        view._reforzar_accesibilidad()
    assert boton.accessibleName() == "Botón agregar tarea de mantenimiento"
    # Tabla principal
    tabla = view.tabla_tareas
    assert tabla.toolTip() == "Tabla de tareas de mantenimiento"
    assert tabla.accessibleName() == "Tabla principal de mantenimiento"
    header = tabla.horizontalHeader()
    if header is not None:
        assert header.objectName() == "header_tareas"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de mantenimiento"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Mantenimiento"
