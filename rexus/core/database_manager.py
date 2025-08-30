from rexus.utils.sql_query_manager import SQLQueryManager
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
        except sqlite3.Error as e:
            logger.error(f"Error de SQLite conectando a BD {self.db_path}: {e}", exc_info=True)
            return False
        except OSError as e:
            logger.error(f"Error de sistema de archivos conectando a BD {self.db_path}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error inesperado conectando a BD {self.db_path}: {e}", exc_info=True)
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con la base de datos."""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("Conexión con BD cerrada exitosamente")
        except sqlite3.Error as e:
            logger.error(f"Error de SQLite cerrando conexión: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error inesperado cerrando conexión: {e}", exc_info=True)
    
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

        except sqlite3.OperationalError as e:
            logger.error(f"Error operacional de SQLite ejecutando query '{query[:50]}...': {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return []
        except sqlite3.IntegrityError as e:
            logger.error(f"Error de integridad de SQLite ejecutando query '{query[:50]}...': {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return []
        except sqlite3.Error as e:
            logger.error(f"Error de SQLite ejecutando query '{query[:50]}...': {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return []
        except Exception as e:
            logger.error(f"Error inesperado ejecutando query '{query[:50]}...': {e}", exc_info=True)
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
                # Validar nombre de tabla (de sqlite_master, pero por seguridad)
                import re
                if not re.match(r'^[a-zA-Z_]\w*$', table_name):
                    logger.warning(f"Nombre de tabla inválido omitido: {table_name}")
                    continue
                    
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")  # nosec B608
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


# ===== DEPENDENCY INJECTION FACTORY =====

class DatabaseManagerFactory:
    """
    Factory para crear instancias de DatabaseManager con Dependency Injection.

    Esta clase reemplaza el patrón Singleton y permite:
    - Mejor testabilidad
    - Inyección de dependencias
    - Configuración flexible
    - Manejo de múltiples conexiones
    """

    _instances: Dict[str, DatabaseManager] = {}

    @classmethod
    def create_manager(cls, db_path: str, name: str = "default") -> DatabaseManager:
        """
        Crea o retorna una instancia de DatabaseManager.

        Args:
            db_path: Ruta a la base de datos
            name: Nombre identificador de la instancia

        Returns:
            Instancia de DatabaseManager
        """
        if name not in cls._instances:
            cls._instances[name] = DatabaseManager(db_path)

        return cls._instances[name]

    @classmethod
    def get_manager(cls, name: str = "default") -> DatabaseManager:
        """
        Obtiene una instancia existente de DatabaseManager.

        Args:
            name: Nombre identificador de la instancia

        Returns:
            Instancia de DatabaseManager

        Raises:
            KeyError: Si la instancia no existe
        """
        if name not in cls._instances:
            raise KeyError(f"DatabaseManager '{name}' no encontrado. Use create_manager() primero.")

        return cls._instances[name]

    @classmethod
    def close_manager(cls, name: str = "default") -> None:
        """
        Cierra y elimina una instancia de DatabaseManager.

        Args:
            name: Nombre identificador de la instancia
        """
        if name in cls._instances:
            cls._instances[name].disconnect()
            del cls._instances[name]

    @classmethod
    def close_all(cls) -> None:
        """Cierra todas las instancias de DatabaseManager."""
        for name, manager in cls._instances.items():
            try:
                manager.disconnect()
            except Exception as e:
                logger.warning(f"Error cerrando DatabaseManager '{name}': {e}")

        cls._instances.clear()

    @classmethod
    def list_managers(cls) -> List[str]:
        """Lista los nombres de todas las instancias activas."""
        return list(cls._instances.keys())


# ===== CONTEXT MANAGER PARA DATABASEMANAGER =====

class DatabaseManagerContext:
    """
    Context manager para DatabaseManager que asegura limpieza automática.

    Uso:
        with DatabaseManagerContext(db_path) as db:
            db.execute_query("SELECT * FROM users")
    """

    def __init__(self, db_path: str, name: str = None):
        self.db_path = db_path
        self.name = name or f"context_{id(self)}"
        self.manager = None

    def __enter__(self) -> DatabaseManager:
        self.manager = DatabaseManagerFactory.create_manager(self.db_path, self.name)
        return self.manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.manager:
            try:
                self.manager.disconnect()
            except Exception as e:
                logger.warning(f"Error cerrando DatabaseManager en context: {e}")
            finally:
                DatabaseManagerFactory.close_manager(self.name)
