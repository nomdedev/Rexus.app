"""Controlador de Pedidos"""

from PyQt6.QtCore import QObject


class PedidosController(QObject):
    def __init__(self, view=None, db_connection=None):
        super().__init__()
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
