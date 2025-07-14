"""Controlador de Configuración"""

from PyQt6.QtCore import QObject


class ConfiguracionController(QObject):
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"
