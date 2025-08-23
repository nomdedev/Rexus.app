"""Modelo de Producción"""

import logging
logger = logging.getLogger(__name__)

class ProduccionModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
