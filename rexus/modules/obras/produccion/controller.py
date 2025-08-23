"""Controlador de Producción"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtCore import QObject


class ProduccionController(QObject):
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = 
