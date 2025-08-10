from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
"""Modelo de Producción"""


class ProduccionModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
