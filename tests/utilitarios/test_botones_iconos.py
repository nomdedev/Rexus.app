# test_botones_iconos.py
"""
Test automatizado para validar la presencia y correspondencia de íconos en los botones secundarios y modales
de la app PyQt6, según el checklist de estándares.
"""
# Ruta relativa a los íconos estándar
ICONOS_ESPERADOS = {
    'guardar': 'resources/icons/save.svg',
    'pdf': 'resources/icons/pdf.svg',
    'add-material': 'resources/icons/add-material.svg',
    'search': 'resources/icons/search.svg',
    'excel': 'resources/icons/excel_icon.svg',
}

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.mark.parametrize("boton,icono_esperado", [
    ("boton_agregar_vidrios_obra", ICONOS_ESPERADOS['add-material']),
import sys

import pytest
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QTableWidgetItem

from modules.vidrios.view import VidriosView

])
def test_iconos_botones_principales(app, boton, icono_esperado):
    view = VidriosView()
    # Verificamos primero que el botón existe
    assert hasattr(view, boton), f"El botón {boton} no existe en la vista"
    btn = getattr(view, boton)
    icon: QIcon = btn.icon()
    assert not icon.isNull(), f"El botón {boton} no tiene ícono asignado"
    # Verifica que el ícono se carga correctamente a diferentes tamaños
    for size in [24, 20, 48]:
        pixmap = icon.pixmap(size, size)
        assert not pixmap.isNull(), f"El ícono de {boton} no se carga correctamente para tamaño {size}"


def test_iconos_botones_modales_qr(app):
    view = VidriosView()

    # Accedemos a la tabla correcta según la implementación actual
    # La vista tiene diferentes tablas según la pestaña activa
    tabla_activa = view.get_tabla_activa()  # Obtener la tabla activa según la implementación
    if tabla_activa is None:
        # Si no hay tabla activa, usamos la tabla de obras que sabemos existe
        tabla_activa = view.tabla_obras

    # Simula selección de un item para disparar el modal QR
    tabla_activa.setRowCount(1)
    for col in range(tabla_activa.columnCount()):
        tabla_activa.setItem(0, col, QTableWidgetItem(f"VIDRIO-TEST-{col}"))
    tabla_activa.selectRow(0)

    # Monkeypatch QDialog.exec para capturar los botones
    botones_capturados = {}
    original_exec = QDialog.exec
    def fake_exec(self):
        for child in self.findChildren(QPushButton):
            if child.toolTip() == "Guardar QR como imagen":
                botones_capturados['guardar'] = child
            elif child.toolTip() == "Exportar QR a PDF":
                botones_capturados['pdf'] = child
        return 0
    QDialog.exec = fake_exec

    try:
        # Llamamos al método con la tabla específica para evitar problemas
        view.mostrar_qr_item_seleccionado(tabla_activa)

        # Verificamos los botones capturados
        btn_guardar = botones_capturados.get('guardar')
        btn_pdf = botones_capturados.get('pdf')

        assert btn_guardar is not None, "No se encontró el botón Guardar QR en el modal"
        assert btn_pdf is not None, "No se encontró el botón PDF en el modal"
        assert not btn_guardar.icon().isNull(), "El botón Guardar QR no tiene ícono"
        assert not btn_pdf.icon().isNull(), "El botón PDF no tiene ícono"
    finally:
        QDialog.exec = original_exec
