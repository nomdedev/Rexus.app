"""Controlador de Producción"""

from PyQt6.QtCore import QObject
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class ProduccionController(QObject):
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
