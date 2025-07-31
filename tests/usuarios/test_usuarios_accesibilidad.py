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

import sys

import pytest
from PyQt6.QtWidgets import QApplication

from rexus.modules.usuarios.view import UsuariosView


def test_usuarios_accesibilidad_tooltips(app):
    view = UsuariosView(usuario_actual="test")
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() == "Agregar usuario"
    # Tabla principal
    tabla = view.tabla_usuarios
    assert tabla.objectName() == "tabla_usuarios"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de usuarios"
    assert (
        view.label_feedback.accessibleDescription()
        == "Mensaje de feedback visual y accesible para el usuario"
    )
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Usuarios"
    # ComboBox de permisos (si existe)
    if hasattr(view, "combo_usuario"):
        assert view.combo_usuario.toolTip() == "Selector de usuario"
        assert (
            view.combo_usuario.accessibleName() == "Selector de usuario para permisos"
        )
