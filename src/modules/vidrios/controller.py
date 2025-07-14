"""Controlador de Vidrios"""

from PyQt6.QtCore import QObject


class VidriosController(QObject):
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

    def actualizar_por_obra(self, obra_data):
        """Actualiza vidrios cuando se crea una obra."""
        print(f"[VIDRIOS] Actualizando por obra: {obra_data}")
