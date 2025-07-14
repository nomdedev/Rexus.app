"""Controlador de Compras/Pedidos"""

from PyQt6.QtCore import QObject


class ComprasPedidosController(QObject):
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"

    def cargar_pedidos(self):
        """Carga los pedidos de compras."""
        print("[COMPRAS] Pedidos cargados")
