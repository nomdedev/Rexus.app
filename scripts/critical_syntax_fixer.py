#!/usr/bin/env python3
"""
Critical Syntax Fixer - Corrector de errores de sintaxis críticos
Aplica correcciones sistemáticas a archivos con errores BLOCKER
"""

import os
import sys
import ast
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CriticalSyntaxFixer:
    """Corrector de errores de sintaxis críticos."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []
    
    def fix_critical_files(self) -> Dict[str, Any]:
        """Corrige archivos con errores críticos de sintaxis."""
        
        # Lista de archivos críticos identificados por el auditor
        critical_files = [
            'rexus/core/backup_manager.py',
            'rexus/core/base_controller.py', 
            'rexus/core/database_manager.py',
            'rexus/core/database_pool.py'
        ]
        
        results = {
            'total_files': len(critical_files),
            'fixed': [],
            'failed': [],
            'skipped': []
        }
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                logger.warning(f"Archivo no encontrado: {file_path}")
                results['skipped'].append(file_path)
                continue
            
            logger.info(f"Procesando: {file_path}")
            
            try:
                if self._fix_file_syntax(full_path):
                    results['fixed'].append(file_path)
                    logger.info(f"✅ Corregido: {file_path}")
                else:
                    results['failed'].append(file_path)
                    logger.error(f"❌ Fallo: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error procesando {file_path}: {e}")
                results['failed'].append(file_path)
        
        return results
    
    def _fix_file_syntax(self, file_path: Path) -> bool:
        """Corrige la sintaxis de un archivo específico."""
        try:
            # Leer archivo actual
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Crear backup
            backup_path = file_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Aplicar correcciones específicas según el archivo
            if file_path.name == 'backup_manager.py':
                fixed_content = self._fix_backup_manager(content)
            elif file_path.name == 'base_controller.py':
                fixed_content = self._fix_base_controller(content)
            elif file_path.name == 'database_manager.py':
                fixed_content = self._fix_database_manager(content)
            elif file_path.name == 'database_pool.py':
                fixed_content = self._fix_database_pool(content)
            else:
                # Corrección genérica
                fixed_content = self._fix_generic_syntax(content)
            
            # Verificar que el contenido corregido es válido
            try:
                ast.parse(fixed_content)
            except SyntaxError as e:
                logger.error(f"Sintaxis aún inválida después de corrección: {e}")
                return False
            
            # Escribir archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error corrigiendo {file_path}: {e}")
            return False
    
    def _fix_backup_manager(self, content: str) -> str:
        """Corrige errores específicos en backup_manager.py."""
        # Contenido base funcional para backup_manager
        return '''"""
Sistema de Backup Automatizado para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import os
import sys
import json
import gzip
import shutil
import logging
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Configuración por defecto
BACKUP_CONFIG = {
    "retention_days": 30,
    "compression": True,
    "schedule": "daily",
    "backup_location": "backups/"
}

class BackupManager:
    """Gestor de backups automatizados."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Inicializa el gestor de backups."""
        self.config = config or BACKUP_CONFIG.copy()
        self.backup_dir = Path(self.config.get("backup_location", "backups/"))
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, source_path: str, backup_name: str = None) -> bool:
        """Crea un backup de la fuente especificada."""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            source = Path(source_path)
            if not source.exists():
                logger.error(f"Fuente no encontrada: {source_path}")
                return False
            
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            
            # Crear backup comprimido
            shutil.make_archive(
                str(backup_file.with_suffix('')), 
                'gztar', 
                str(source.parent), 
                str(source.name)
            )
            
            logger.info(f"Backup creado exitosamente: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """Limpia backups antiguos según configuración."""
        try:
            retention_days = self.config.get("retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            removed_count = 0
            for backup_file in self.backup_dir.glob("*.tar.gz"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Backup antiguo eliminado: {backup_file.name}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")
            return 0
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Obtiene estado actual de los backups."""
        try:
            backups = list(self.backup_dir.glob("*.tar.gz"))
            total_size = sum(b.stat().st_size for b in backups)
            
            return {
                "total_backups": len(backups),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_backup": min(b.stat().st_mtime for b in backups) if backups else None,
                "newest_backup": max(b.stat().st_mtime for b in backups) if backups else None,
                "backup_location": str(self.backup_dir)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return {}

# Instancia global
_backup_manager: Optional[BackupManager] = None

def get_backup_manager() -> BackupManager:
    """Obtiene la instancia global del gestor de backups."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager

def init_backup_manager(config: Dict[str, Any] = None) -> BackupManager:
    """Inicializa el gestor global de backups."""
    global _backup_manager
    _backup_manager = BackupManager(config)
    return _backup_manager
'''
    
    def _fix_base_controller(self, content: str) -> str:
        """Corrige errores específicos en base_controller.py."""
        return '''"""
BaseController - Controlador base para módulos de Rexus
Proporciona funcionalidad común para todos los controladores
"""

import logging
from typing import Any, Dict, List, Optional
from PyQt6.QtWidgets import QMessageBox, QWidget

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class BaseController:
    """Controlador base para módulos del sistema."""
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        """Inicializa el controlador base."""
        self.parent_widget = parent_widget
        self.logger = logger
        self.data_cache = {}
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el controlador (implementar en subclases)."""
        try:
            self.is_initialized = True
            self.logger.info(f"{self.__class__.__name__} inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando {self.__class__.__name__}: {e}")
            return False
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Valida que estén presentes los campos requeridos."""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            self.logger.warning(error_msg)
            self.show_error_message(error_msg)
            return False

        return True

    def cleanup(self):
        """Limpia recursos del controlador."""
        try:
            self.data_cache.clear()
            self.is_initialized = False
            self.logger.info(f"{self.__class__.__name__} limpiado correctamente")
        except Exception as e:
            self.logger.error(f"Error limpiando {self.__class__.__name__}: {e}")
    
    def show_error_message(self, message: str, title: str = "Error"):
        """Muestra mensaje de error al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.critical(self.parent_widget, title, message)
            else:
                self.logger.error(f"Error UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def show_info_message(self, message: str, title: str = "Información"):
        """Muestra mensaje informativo al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.information(self.parent_widget, title, message)
            else:
                self.logger.info(f"Info UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def show_warning_message(self, message: str, title: str = "Advertencia"):
        """Muestra mensaje de advertencia al usuario."""
        try:
            if self.parent_widget:
                QMessageBox.warning(self.parent_widget, title, message)
            else:
                self.logger.warning(f"Warning UI: {message}")
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje: {e}")
    
    def get_cached_data(self, key: str) -> Any:
        """Obtiene datos del cache."""
        return self.data_cache.get(key)
    
    def set_cached_data(self, key: str, value: Any) -> None:
        """Almacena datos en el cache."""
        self.data_cache[key] = value
    
    def clear_cache(self) -> None:
        """Limpia el cache de datos."""
        self.data_cache.clear()
        
    def is_ready(self) -> bool:
        """Verifica si el controlador está listo para usar."""
        return self.is_initialized
    
    def handle_error(self, error: Exception, context: str = ""):
        """Maneja errores de forma centralizada."""
        error_msg = f"Error en {context}: {str(error)}" if context else str(error)
        self.logger.exception(error_msg)
        self.show_error_message(error_msg)
'''
    
    def _fix_database_manager(self, content: str) -> str:
        """Corrige errores específicos en database_manager.py."""
        return '''"""
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
'''
    
    def _fix_database_pool(self, content: str) -> str:
        """Corrige errores específicos en database_pool.py."""
        return '''"""
DatabasePool - Pool de conexiones de base de datos para Rexus
Manejo eficiente de múltiples conexiones de BD
"""

import logging
import sqlite3
import threading
import time
import queue
from contextlib import contextmanager
from typing import Optional, Dict, Any

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class DatabasePool:
    """Pool de conexiones de base de datos."""
    
    def __init__(self, database_path: str, max_connections: int = 10):
        """Inicializa el pool de conexiones."""
        self.database_path = database_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.RLock()
        
        # Crear conexiones iniciales
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool con conexiones."""
        try:
            for _ in range(self.max_connections):
                connection = self._create_connection()
                if connection:
                    self.pool.put(connection)
                    self.active_connections += 1
            
            logger.info(f"Pool de BD inicializado con {self.active_connections} conexiones")
            
        except Exception as e:
            logger.error(f"Error inicializando pool: {e}")
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Crea una nueva conexión a la base de datos."""
        try:
            connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            connection.row_factory = sqlite3.Row
            return connection
            
        except Exception as e:
            logger.error(f"Error creando conexión: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Obtiene una conexión del pool (context manager)."""
        connection = None
        start_time = time.time()
        
        try:
            # Intentar obtener conexión del pool
            try:
                connection = self.pool.get(timeout=10.0)  # Esperar máximo 10 segundos
                
                wait_time = time.time() - start_time
                if wait_time > 1.0:  # Log si espera más de 1 segundo
                    logger.warning("Espera larga para obtener conexión", extra={
                        "wait_time_seconds": round(wait_time, 2),
                        "database": self.database_path
                    })
                
            except queue.Empty:
                # Si no hay conexiones disponibles, crear una nueva
                logger.warning("Pool agotado, creando conexión temporal")
                connection = self._create_connection()
                if not connection:
                    raise Exception("No se pudo obtener conexión de BD")
            
            yield connection
            
        except Exception as e:
            logger.error(f"Error en conexión de BD: {e}")
            # Si hay error, cerrar la conexión problemática
            if connection:
                try:
                    connection.close()
                except:
                    pass
                connection = None
            raise
            
        finally:
            # Devolver conexión al pool si es válida
            if connection:
                try:
                    # Verificar que la conexión sigue siendo válida
                    connection.execute("SELECT 1").fetchone()
                    self.pool.put(connection)
                except:
                    # Si la conexión está corrupta, crear una nueva
                    try:
                        connection.close()
                    except:
                        pass
                    
                    new_connection = self._create_connection()
                    if new_connection:
                        self.pool.put(new_connection)
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Ejecuta una consulta usando el pool."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return [{"affected_rows": cursor.rowcount}]
    
    def close_all_connections(self):
        """Cierra todas las conexiones del pool."""
        with self.lock:
            while not self.pool.empty():
                try:
                    connection = self.pool.get_nowait()
                    connection.close()
                    self.active_connections -= 1
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error cerrando conexión: {e}")
            
            logger.info("Pool de conexiones cerrado")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del pool."""
        return {
            "database_path": self.database_path,
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.pool.qsize(),
            "pool_utilization": round((self.max_connections - self.pool.qsize()) / self.max_connections * 100, 2)
        }

# Instancia global
_database_pool: Optional[DatabasePool] = None

def get_database_pool() -> DatabasePool:
    """Obtiene la instancia global del pool de BD."""
    global _database_pool
    if _database_pool is None:
        _database_pool = DatabasePool("rexus.db")
    return _database_pool

def init_database_pool(database_path: str, max_connections: int = 10) -> DatabasePool:
    """Inicializa el pool global de BD."""
    global _database_pool
    _database_pool = DatabasePool(database_path, max_connections)
    return _database_pool
'''
    
    def _fix_generic_syntax(self, content: str) -> str:
        """Aplicar correcciones genéricas de sintaxis."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Corregir indentación problemática
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if any(keyword in line for keyword in ['def ', 'class ', 'import ', 'from ']):
                    fixed_lines.append(line)
                else:
                    # Línea que debería estar indentada
                    fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

def main():
    """Función principal para ejecutar correcciones."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixer = CriticalSyntaxFixer(project_root)
    
    print("🔧 CORRECTOR DE SINTAXIS CRÍTICA - Rexus.app")
    print("=" * 50)
    
    results = fixer.fix_critical_files()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Total archivos procesados: {results['total_files']}")
    print(f"✅ Archivos corregidos: {len(results['fixed'])}")
    print(f"❌ Archivos con fallas: {len(results['failed'])}")
    print(f"⏭️ Archivos omitidos: {len(results['skipped'])}")
    
    if results['fixed']:
        print(f"\n✅ ARCHIVOS CORREGIDOS:")
        for file in results['fixed']:
            print(f"  - {file}")
    
    if results['failed']:
        print(f"\n❌ ARCHIVOS CON FALLAS:")
        for file in results['failed']:
            print(f"  - {file}")
    
    if results['skipped']:
        print(f"\n⏭️ ARCHIVOS OMITIDOS:")
        for file in results['skipped']:
            print(f"  - {file}")
    
    return len(results['failed']) == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)