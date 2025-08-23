"""Stubs para diálogos de servicios de logística usados por tests.

Proporciona implementaciones ligeras y sin GUI para permitir importaciones en tests.
"""

import logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import QDialog

class DialogoGenerarServicio(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def obtener_datos(self):
        return {}

class DialogoPreviewServicios(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mostrar_preview(self, datos):
        return True
