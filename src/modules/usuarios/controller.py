"""Controlador de Usuarios"""

from PyQt6.QtCore import QObject


class UsuariosController(QObject):
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

    def inicializar_vista(self):
        """Inicializa la vista de usuarios."""
        print("[USUARIOS] Vista inicializada")
