# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Base de Datos para Rexus.app
Proporciona gestión centralizada de conexiones y operaciones de BD
"""

import logging
import pyodbc
import sqlite3
from typing import Optional, Dict, Any, List, Tuple
from .database import get_inventario_connection, get_users_connection
try:
    from .logger import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

logger.info("Sistema de logging inicializado")

class DatabaseManager:
    """Administrador centralizado de bases de datos para Rexus.app"""
    
    def __init__(self):
        self.connections = {}
        self.current_connection = None
        logger.info("DatabaseManager inicializado")
    
    def get_connection(self, database_name: str = None) -> Optional[pyodbc.Connection]:
        """Obtiene una conexión a la base de datos especificada"""
        try:
            if database_name is None:
                database_name = "inventario"
            
            # Usar funciones específicas de la base
            if database_name == "users":
                return get_users_connection()
            else:
                return get_inventario_connection()
            
            if database_name in self.connections:
                return self.connections[database_name]
            
            # Crear nueva conexión
            connection = self._create_connection(database_name)
            if connection:
                self.connections[database_name] = connection
                self.current_connection = connection
                logger.info(f"Conexión establecida para BD: {database_name}")
                return connection
            
        except Exception as e:
            logger.error(f"Error al obtener conexión BD {database_name}: {e}")
            return None
    
    def _create_connection(self, database_name: str) -> Optional[pyodbc.Connection]:
        """Crea una nueva conexión a la base de datos"""
        try:
            # Usar configuración existente pero cambiar BD
            temp_config = DatabaseConnection()
            temp_config.database = database_name
            temp_config.connect()
            return temp_config.connection
            
        except Exception as e:
            logger.error(f"Error creando conexión {database_name}: {e}")
            return None
    
    def execute_query(self, query: str, params: Tuple = None, database: str = None) -> List[Dict]:
        """Ejecuta una consulta SQL y retorna resultados"""
        try:
            connection = self.get_connection(database)
            if not connection:
                logger.error("No hay conexión disponible")
                return []
            
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Si es SELECT, retornar resultados
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                # INSERT, UPDATE, DELETE
                connection.commit()
                return [{"affected_rows": cursor.rowcount}]
                
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            if connection:
                connection.rollback()
            return []
    
    def close_connection(self, database_name: str = None):
        """Cierra una conexión específica"""
        try:
            if database_name and database_name in self.connections:
                self.connections[database_name].close()
                del self.connections[database_name]
                logger.info(f"Conexión {database_name} cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión {database_name}: {e}")
    
    def close_all_connections(self):
        """Cierra todas las conexiones activas"""
        for db_name in list(self.connections.keys()):
            self.close_connection(db_name)
        self.current_connection = None
        logger.info("Todas las conexiones cerradas")
    
    def get_table_info(self, table_name: str, database: str = None) -> List[Dict]:
        """Obtiene información sobre una tabla"""
        try:
            query = f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            """
            
            return self.execute_query(query, database=database)
            
        except Exception as e:
            logger.error(f"Error obteniendo info tabla {table_name}: {e}")
            return []
    
    def table_exists(self, table_name: str, database: str = None) -> bool:
        """Verifica si una tabla existe"""
        try:
            # Usar consulta parametrizada para prevenir SQL injection
            query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?"
            
            results = self.execute_query(query, (table_name,), database=database)
            return len(results) > 0
            
        except Exception as e:
            logger.error(f"Error verificando tabla {table_name}: {e}")
            return False

# Instancia global del administrador
_database_manager = None

def get_database_manager() -> DatabaseManager:
    """Obtiene la instancia global del administrador de BD"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def get_connection(database_name: str = None):
    """Función de conveniencia para obtener conexión BD"""
    return get_database_manager().get_connection(database_name)

def execute_query(query: str, params: Tuple = None, database: str = None):
    """Función de conveniencia para ejecutar queries"""
    return get_database_manager().execute_query(query, params, database)