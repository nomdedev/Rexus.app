"""
Módulo de conexión a base de datos
Configuración central para todas las conexiones de la aplicación
"""

import os
from typing import Optional

import pyodbc

# Configuración por defecto (debe ir antes de la clase)
DB_SERVER = os.getenv("STOCKAPP_DB_SERVER", "localhost")
DB_DEFAULT_DATABASE = os.getenv("STOCKAPP_DB_NAME", "stock_app")
DB_DRIVER = os.getenv("STOCKAPP_DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_USERNAME = os.getenv("STOCKAPP_DB_USER", "")
DB_PASSWORD = os.getenv("STOCKAPP_DB_PASS", "")


class DatabaseConnection:
    """Clase base para conexiones a la base de datos"""

    def __init__(
        self,
        server: str = DB_SERVER,
        database: str = DB_DEFAULT_DATABASE,
        driver: str = DB_DRIVER,
        username: str = DB_USERNAME,
        password: str = DB_PASSWORD,
        trusted: bool = True,
    ):
        self.server = server
        self.database = database
        self.driver = driver
        self.username = username
        self.password = password
        self.trusted = trusted
        self._connection: Optional[pyodbc.Connection] = None

    def connect(self) -> bool:
        """Establece conexión con la base de datos. Devuelve True si conecta, False si falla."""
        try:
            if self.trusted:
                connection_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                connection_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};PWD={self.password};"
                )
            self._connection = pyodbc.connect(connection_string)
            return True
        except Exception as e:
            print(f"[DB ERROR] No se pudo conectar: {e}")
            self._connection = None
            return False

    def disconnect(self):
        """Cierra la conexión a la base de datos"""
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                print(f"[DB ERROR] No se pudo cerrar la conexión: {e}")
            self._connection = None

    def cursor(self):
        """Obtiene un cursor de la conexión activa."""
        if not self._connection:
            if not self.connect():
                raise Exception("No se pudo establecer conexión con la base de datos")
        return self._connection.cursor()

    def commit(self):
        """Confirma las transacciones pendientes."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Deshace las transacciones pendientes."""
        if self._connection:
            self._connection.rollback()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Ejecuta una consulta SELECT y devuelve los resultados como lista de tuplas."""
        if not self._connection:
            if not self.connect():
                return []
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"[DB ERROR] Consulta fallida: {e}\nQuery: {query}\nParams: {params}")
            return []

    def execute_non_query(self, query: str, params: tuple = ()) -> bool:
        """Ejecuta consultas INSERT, UPDATE, DELETE. Devuelve True si tiene éxito."""
        if not self._connection:
            if not self.connect():
                return False
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"[DB ERROR] Comando fallido: {e}\nQuery: {query}\nParams: {params}")
            return False


class InventarioDatabaseConnection(DatabaseConnection):
    """Conexión específica para el módulo de inventario"""

    def __init__(self):
        super().__init__(database="inventario_db")

    def get_productos(self) -> list:
        """Obtiene lista de productos del inventario"""
        return self.execute_query("SELECT * FROM productos")

    def get_stock(self, producto_id: int) -> int:
        """Obtiene el stock actual de un producto por su ID"""
        result = self.execute_query(
            "SELECT stock FROM productos WHERE id = ?", (producto_id,)
        )
        try:
            return int(result[0][0]) if result else 0
        except Exception:
            return 0


# Configuración por defecto
DB_SERVER = os.getenv("STOCKAPP_DB_SERVER", "localhost")
DB_DEFAULT_DATABASE = os.getenv("STOCKAPP_DB_NAME", "stock_app")
DB_DRIVER = os.getenv("STOCKAPP_DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_USERNAME = os.getenv("STOCKAPP_DB_USER", "")
DB_PASSWORD = os.getenv("STOCKAPP_DB_PASS", "")
