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
            logger.exception(f"Consulta fallida: {e}\nQuery: {query}\nParams: {params}")
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn []

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
            logger.exception(f"Comando fallido: {e}\nQuery: {query}\nParams: {params}")
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn False


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
