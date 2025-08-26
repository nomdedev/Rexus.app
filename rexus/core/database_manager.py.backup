"""
DatabaseManager - Gestor avanzado de base de datos para Rexus
Manejo centralizado de conexiones y operaciones de BD
"""

import logging
import sqlite3
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor centralizado de base de datos."""
    
    def __init__(self, db_path: str = None):
        """Inicializa el gestor de base de datos."""
        self.db_path = db_path or "rexus.db"
        self.connection = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Establece conexión con la base de datos."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.is_connected = True
            logger.info(f"Conexión establecida con BD: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con la base de datos."""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("Conexión con BD cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def execute_query(self, query: str, params: tuple = (), database: str = None) -> List[Dict]:
        """Ejecuta una consulta y retorna resultados."""
        try:
            if not self.is_connected:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self.connection.commit()
                return [{"affected_rows": cursor.rowcount}]
                
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            if self.connection:
                self.connection.rollback()
            return []
    
    def get_table_info(self, table_name: str, database: str = None) -> List[Dict]:
        """Obtiene información sobre una tabla."""
        try:
            query = f"PRAGMA table_info({table_name})"
            return self.execute_query(query, database=database)
        except Exception as e:
            logger.error(f"Error obteniendo info de tabla {table_name}: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe."""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = self.execute_query(query, (table_name,))
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error verificando tabla {table_name}: {e}")
            return False
    
    def create_table_if_not_exists(self, table_name: str, columns: Dict[str, str]) -> bool:
        """Crea una tabla si no existe."""
        try:
            if self.table_exists(table_name):
                return True
            
            column_definitions = []
            for col_name, col_type in columns.items():
                column_definitions.append(f"{col_name} {col_type}")
            
            query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
            self.execute_query(query)
            
            logger.info(f"Tabla {table_name} creada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tabla {table_name}: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Crea backup de la base de datos."""
        try:
            if not self.is_connected:
                self.connect()
            
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            logger.info(f"Backup creado en: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos."""
        try:
            stats = {}
            
            # Obtener lista de tablas
            tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            stats['total_tables'] = len(tables)
            stats['tables'] = []
            
            for table in tables:
                table_name = table['name']
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = count_result[0]['count'] if count_result else 0
                
                stats['tables'].append({
                    'name': table_name,
                    'row_count': row_count
                })
            
            # Tamaño de BD
            if Path(self.db_path).exists():
                stats['size_mb'] = round(Path(self.db_path).stat().st_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

# Instancia global
_database_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Obtiene la instancia global del gestor de BD."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def init_database_manager(db_path: str = None) -> DatabaseManager:
    """Inicializa el gestor global de BD."""
    global _database_manager
    _database_manager = DatabaseManager(db_path)
    return _database_manager
