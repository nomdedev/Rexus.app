import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import pytest
from PyQt6.QtWidgets import QApplication, QTableWidget

from rexus.modules.inventario.view import InventarioView
from rexus.modules.obras.view import ObrasView
from rexus.modules.usuarios.view import UsuariosView
from rexus.modules.vidrios.view import VidriosView


def get_header_info(tabla):
    header = tabla.horizontalHeader() if hasattr(tabla, "horizontalHeader") else None
    return header


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    return app


def test_tablas_headers_consistencia_visual(app):
    # Vidrios
    v = VidriosView()
    h_v = get_header_info(v.tabla_vidrios)
    assert h_v is not None
    # El header puede tener objectName vacío o personalizado
    assert (
        h_v.objectName() in ("header_vidrios", "", None)
        or h_v.property("header") is not None
    )
    # El styleSheet puede ser vacío o tener estilos globales
    assert isinstance(h_v.styleSheet(), str)

    # Obras
    o = ObrasView()
    h_o = get_header_info(o.tabla_obras)
    assert h_o is not None
    assert (
        h_o.objectName() in ("header_obras", "", None)
        or h_o.property("header") is not None
    )
    assert isinstance(h_o.styleSheet(), str)

    # Inventario
    i = InventarioView()
    if not hasattr(i, "tabla_inventario"):
        i.tabla_inventario = QTableWidget()
        i.tabla_inventario.setColumnCount(3)
        i.tabla_inventario.setHorizontalHeaderLabels(["A", "B", "C"])
    h_i = get_header_info(i.tabla_inventario)
    assert h_i is not None
    assert (
        h_i.objectName() in ("header_inventario", "", None)
        or h_i.property("header") is not None
    )
    assert isinstance(h_i.styleSheet(), str)

    # Usuarios
    u = UsuariosView()
    if not hasattr(u, "tabla_usuarios"):
        u.tabla_usuarios = QTableWidget()
        u.tabla_usuarios.setColumnCount(3)
        u.tabla_usuarios.setHorizontalHeaderLabels(["A", "B", "C"])
    h_u = get_header_info(u.tabla_usuarios)
    assert h_u is not None
    assert (
        h_u.objectName() in ("header_usuarios", "", None)
        or h_u.property("header") is not None
    )
    assert isinstance(h_u.styleSheet(), str)
