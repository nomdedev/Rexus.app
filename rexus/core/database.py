"""
Módulo de conexión a base de datos
Configuración central para todas las conexiones de la aplicación

-------------------------------------------------------------
DOCUMENTACIÓN DE USO DE BASES DE DATOS EN LA APP
-------------------------------------------------------------

1. La base de datos 'users' SOLO debe usarse para:
   - Login de usuarios
   - Gestión de permisos y roles
   - Todo lo relacionado con autenticación y seguridad

2. TODOS los demás módulos (inventario,
obras,
    pedidos,
    vidrios,
    herrajes,
    etc.)
   deben usar la base de datos 'inventario' para sus tablas y operaciones.

3. La base de datos 'auditoria' se usa exclusivamente para trazabilidad y registro de eventos críticos.

NO mezclar tablas de negocio en 'users'. NO usar 'inventario' para login o permisos.
-------------------------------------------------------------
"""

import os
import logging
from typing import Optional

import pyodbc

# Configurar logger específico para el módulo de database
logger = logging.getLogger(__name__)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARNING] python-dotenv no disponible. Usando variables de sistema únicamente.")

# Configuración desde variables de entorno (sin valores por defecto)
DB_SERVER = os.getenv("DB_SERVER")
DB_DRIVER = os.getenv("DB_DRIVER")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Bases de datos desde variables de entorno
DB_USERS = os.getenv("DB_USERS")
DB_INVENTARIO = os.getenv("DB_INVENTARIO")
DB_AUDITORIA = os.getenv("DB_AUDITORIA")

# Validar que las variables críticas estén configuradas
def validate_environment():
    """Valida que todas las variables de entorno necesarias estén configuradas"""
    required_vars = {
        'DB_SERVER': DB_SERVER,
        'DB_DRIVER': DB_DRIVER,
        'DB_USERNAME': DB_USERNAME,
        'DB_PASSWORD': DB_PASSWORD,
        'DB_USERS': DB_USERS,
        'DB_INVENTARIO': DB_INVENTARIO,
        'DB_AUDITORIA': DB_AUDITORIA
    }

    missing = [var for var, value in required_vars.items() if not value]
    if missing:
        print(f"[WARNING] Variables de entorno faltantes: {', '.join(missing)}. Los módulos funcionarán en modo demo.")
        return False
    return True

# Validar al importar el módulo (no hacer crash si faltan variables)
_environment_valid = validate_environment()


class DatabaseConnection:
    """Clase base para conexiones a la base de datos"""

    def __init__(
        self,
        database: str = None,
        auto_connect: bool = False,
    ):
        self.server = DB_SERVER
        self.database = database
        self.driver = DB_DRIVER
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.trusted = False  # Siempre autenticación SQL Server
        self._connection: Optional[pyodbc.Connection] = None
        if auto_connect:
            self.connect()

    @property
    def connection(self) -> Optional[pyodbc.Connection]:
        """Proporciona acceso a la conexión actual"""
        return self._connection

    def switch_database(self, new_database: str) -> bool:
        """
        Cambia a una base de datos diferente usando la misma conexión

        Args:
            new_database: Nombre de la nueva base de datos

        Returns:
            True si el cambio fue exitoso, False si no
        """
        # Validate database name to prevent SQL injection
        if not new_database or not isinstance(new_database, str):
            print(f"[DB ERROR] Invalid database name: {new_database}")
            return False

        # Sanitize database name - only allow alphanumeric, underscore, and hyphen
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', new_database):
            print(f"[DB ERROR] Database name contains invalid characters: {new_database}")
            return False

        if not self._connection:
            self.database = new_database
            return self.connect()

        try:
            cursor = self._connection.cursor()
            # Use secure string concatenation with brackets for database names
            query = f"USE [{new_database}]"
            cursor.execute(query)
            self.database = new_database
            cursor.close()
            print(f"[DB] Cambiado a base de datos: {new_database}")
            return True
        except (pyodbc.Error, pyodbc.DatabaseError) as e:
            logger.error(f"No se pudo cambiar a la base de datos {new_database}: {e}")
            return False
        except (AttributeError, OSError) as e:
            logger.error(f"Error inesperado cambiando a base de datos {new_database}: {e}", exc_info=True)
            return False

    def connect(self):
        """Establece la conexión a la base de datos y registra el flujo"""
        logger.info("Intentando conectar a la base de datos")
        logger.info(f"Servidor: {self.server}")
        logger.info(f"Base de datos: {self.database}")
        logger.info(f"Driver: {self.driver}")
        logger.info(
            f"Usuario: {self.username if not self.trusted else '[Trusted_Connection]'}"
        )
        try:
            if self.trusted:
                connection_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                # String de conexión real (con contraseña)
                real_connection_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                    f"TrustServerCertificate=yes;"
                )
                # String para mostrar (sin contraseña)
                display_connection_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD=******;"
                    f"TrustServerCertificate=yes;"
                )
            if self.trusted:
                print(f"[DB] String de conexión: {connection_string}")
                self._connection = pyodbc.connect(connection_string)
            else:
                print(f"[DB] String de conexión: {display_connection_string}")
                self._connection = pyodbc.connect(real_connection_string)
            print("[DB] Conexión exitosa OK\n")
            return True
        except (pyodbc.Error, pyodbc.InterfaceError, pyodbc.OperationalError) as e:
            print(f"[DB ERROR] No se pudo conectar: {e}")
            logger.error(f"Database connection failed: {e}", exc_info=True)
            self._connection = None
            print("[DB] ERROR: Error al intentar conectar.\n")
            return False

    def disconnect(self):
        """Cierra la conexión a la base de datos"""
        if self._connection:
            try:
                self._connection.close()
            except (pyodbc.Error, AttributeError) as e:
                print(f"[DB ERROR] No se pudo cerrar la conexión: {e}")
                logger.error(f"Database disconnect failed: {e}", exc_info=True)
            self._connection = None

    def close(self):
        """Alias para disconnect() - cierra la conexión a la base de datos"""
        self.disconnect()

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


# Singleton para conexiones reutilizables
class SmartDatabaseConnection:
    """Conexión inteligente que permite cambiar de base de datos dinámicamente"""

    _instance = None
    _connection_obj = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self, database: str, auto_connect: bool = True) -> DatabaseConnection:
        """
        Obtiene una conexión a la base de datos especificada

        Args:
            database: Nombre de la base de datos
            auto_connect: Si debe conectar automáticamente

        Returns:
            Objeto DatabaseConnection configurado para la base de datos
        """
        if self._connection_obj is None:
            self._connection_obj = DatabaseConnection(database=database, auto_connect=auto_connect)
        elif self._connection_obj.database != database:
            # Cambiar a la nueva base de datos
            self._connection_obj.switch_database(database)
        elif not self._connection_obj._connection and auto_connect:
            # Reconectar si no hay conexión activa
            self._connection_obj.connect()

        return self._connection_obj

    def disconnect(self):
        """Desconecta la conexión actual"""
        if self._connection_obj:
            self._connection_obj.disconnect()
            self._connection_obj = None

# Instancia global del gestor de conexiones
_db_manager = SmartDatabaseConnection()

def get_connection(database: str, auto_connect: bool = True) -> DatabaseConnection:
    """
    Función global para obtener conexión a cualquier base de datos
    
    Args:
        database: Nombre de la base de datos ('inventario', 'users', 'auditoria')
        auto_connect: Si debe conectar automáticamente
    
    Returns:
        Objeto DatabaseConnection configurado
    """
    return _db_manager.get_connection(database, auto_connect)

def get_inventario_connection(auto_connect: bool = True) -> DatabaseConnection:
    """Obtiene conexión a la base de datos de inventario"""
    return _db_manager.get_connection(DB_INVENTARIO, auto_connect)

def get_users_connection(auto_connect: bool = True) -> DatabaseConnection:
    """Obtiene conexión a la base de datos de usuarios"""
    return _db_manager.get_connection(DB_USERS, auto_connect)

def get_auditoria_connection(auto_connect: bool = True) -> DatabaseConnection:
    """Obtiene conexión a la base de datos de auditoría"""
    return _db_manager.get_connection(DB_AUDITORIA, auto_connect)

# Clases de compatibilidad (mantener para no romper código existente)
class InventarioDatabaseConnection(DatabaseConnection):
    """Conexión específica para el módulo de inventario"""
    def __init__(self, auto_connect: bool = False):
        super().__init__(database=DB_INVENTARIO, auto_connect=auto_connect)

class UsersDatabaseConnection(DatabaseConnection):
    """Conexión específica para el módulo de usuarios"""
    def __init__(self, auto_connect: bool = False):
        super().__init__(database=DB_USERS, auto_connect=auto_connect)

class AuditoriaDatabaseConnection(DatabaseConnection):
    """Conexión específica para el módulo de auditoría"""
    def __init__(self, auto_connect: bool = False):
        super().__init__(database=DB_AUDITORIA, auto_connect=auto_connect)

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
        except (ValueError, TypeError, IndexError, AttributeError):
            return 0
