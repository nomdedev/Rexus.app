# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Base de Datos para Rexus.app
Proporciona gestión centralizada de conexiones y operaciones de BD
"""

import logging
import pyodbc
import sqlite3
                
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
    
    def table_exists(self, table_name: str, database: str = None) -> bool:
        """Verifica si una tabla existe"""
        try:
            # Usar consulta parametrizada para prevenir SQL injection
            query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?"
            
            results = self.execute_query(query, (table_name,), database=database)
            return len(results) > 0
            
        except Exception as e:

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