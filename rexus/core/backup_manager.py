"""
Sistema de Backup Automatizado para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import sys
import json
import gzip
import shutil
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import threading
import time

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

try:
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from .config import (
    BACKUP_CONFIG, DATABASE_CONFIG, FILES_CONFIG,
    LOGS_DIR, PROJECT_ROOT
)
from .logger import get_logger

logger = get_logger("backup")

@dataclass
class BackupResult:
    """Resultado de una operación de backup"""
    success: bool
    backup_type: str
    file_path: Optional[str]
    size_bytes: int
    duration_seconds: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BackupManager:
    """
    Manager centralizado para todas las operaciones de backup
    Soporta backup de bases de datos, archivos y configuraciones
    """

    def __init__(self):
        self.logger = get_logger("backup_manager")
        self.backup_dir = FILES_CONFIG["backup_path"]
        self.retention_days = BACKUP_CONFIG["retention_days"]
        self.compression_enabled = BACKUP_CONFIG["compression"]

        # Configurar directorio de backups
        self.backup_dir.mkdir(exist_ok=True)

        # Configurar subdirectorios
        self.db_backup_dir = self.backup_dir / "database"
        self.files_backup_dir = self.backup_dir / "files"
        self.config_backup_dir = self.backup_dir / "config"

        for dir_path in [self.db_backup_dir, self.files_backup_dir, self.config_backup_dir]:
            dir_path.mkdir(exist_ok=True)

        # Estado del scheduler
        self._scheduler_running = False
        self._scheduler_thread = None

        self.logger.info("BackupManager inicializado", extra={
            "backup_dir": str(self.backup_dir),
            "retention_days": self.retention_days,
            "compression": self.compression_enabled
        })

    def start_scheduler(self):
        """Iniciar el scheduler de backups automáticos"""
        if self._scheduler_running:
            self.logger.warning("Scheduler ya está ejecutándose")
            return

        # Configurar schedule
        schedule_cron = BACKUP_CONFIG.get("schedule", "0 2 * * *")  # 2 AM diariamente por defecto

        # Convertir cron a schedule (simplificado)
        if schedule_cron == "0 2 * * *":
            schedule.every().day.at("02:00").do(self._run_scheduled_backup)
        else:
            # Para otros formatos, usar daily por defecto
            schedule.every().day.at("02:00").do(self._run_scheduled_backup)

        self._scheduler_running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

        self.logger.info("Scheduler de backups iniciado", extra={
            "schedule": schedule_cron
        })

    def stop_scheduler(self):
        """Detener el scheduler"""
        self._scheduler_running = False
        schedule.clear()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

        self.logger.info("Scheduler de backups detenido")

    def _scheduler_loop(self):
        """Loop principal del scheduler"""
        while self._scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                self.logger.error("Error en scheduler loop", extra={
                    "error": str(e)
                })
                time.sleep(300)  # Esperar 5 minutos en caso de error

    def _run_scheduled_backup(self):
        """Ejecutar backup programado"""
        try:
            self.logger.info("Iniciando backup programado")
            results = self.backup_all()

            success_count = sum(1 for r in results if r.success)
            total_count = len(results)

            self.logger.info("Backup programado completado", extra={
                "successful": success_count,
                "total": total_count,
                "results": [r.__dict__ for r in results]
            })

            # Limpiar backups antiguos
            self.cleanup_old_backups()

        except Exception as e:
            self.logger.error("Error en backup programado", extra={
                "error": str(e)
            }, exc_info=True)

    def backup_all(self) -> List[BackupResult]:
        """Ejecutar backup completo de todo el sistema"""
        results = []

        # Backup de bases de datos
        for db_name in DATABASE_CONFIG["databases"].values():
            result = self.backup_database(db_name)
            results.append(result)

        # Backup de archivos importantes
        result = self.backup_files()
        results.append(result)

        # Backup de configuraciones
        result = self.backup_configurations()
        results.append(result)

        return results

    def backup_database(self, database_name: str) -> BackupResult:
        """
        Backup de una base de datos específica
        """
        start_time = datetime.now()

        try:
            if not PYODBC_AVAILABLE:
                raise ImportError("pyodbc no disponible para backup de BD")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{database_name}_backup_{timestamp}.sql"
            backup_path = self.db_backup_dir / backup_filename

            # Generar script de backup
            backup_script = self._generate_database_backup_script(database_name)

            # Escribir backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_script)

            # Comprimir si está habilitado
            if self.compression_enabled:
                compressed_path = backup_path.with_suffix('.sql.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Eliminar archivo sin comprimir
                backup_path.unlink()
                backup_path = compressed_path

            file_size = backup_path.stat().st_size
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Backup de BD {database_name} completado", extra={
                "database": database_name,
                "file_path": str(backup_path),
                "size_mb": round(file_size / 1024 / 1024, 2),
                "duration_seconds": duration
            })

            return BackupResult(
                success=True,
                backup_type="database",
                file_path=str(backup_path),
                size_bytes=file_size,
                duration_seconds=duration,
                metadata={"database_name": database_name}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.error(f"Error en backup de BD {database_name}", extra={
                "database": database_name,
                "error": str(e),
                "duration_seconds": duration
            }, exc_info=True)

            return BackupResult(
                success=False,
                backup_type="database",
                file_path=None,
                size_bytes=0,
                duration_seconds=duration,
                error_message=str(e),
                metadata={"database_name": database_name}
            )

    def _generate_database_backup_script(self, database_name: str) -> str:
        """Generar script SQL para backup de base de datos"""
        try:
            connection_string = (
                f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
                f"SERVER={DATABASE_CONFIG['server']};"
                f"DATABASE={database_name};"
                f"UID={DATABASE_CONFIG['username']};"
                f"PWD={DATABASE_CONFIG['password']};"
                f"TrustServerCertificate=yes;"
            )

            backup_script = f"""
-- Backup script for {database_name}
-- Generated on {datetime.now().isoformat()}
-- Rexus Backup System v2.0.0

USE [{database_name}];

-- Backup schema and data
"""

            with pyodbc.connect(connection_string, timeout=30) as conn:
                cursor = conn.cursor()

                # Obtener lista de tablas
                cursor.execute("""
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """)

                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    backup_script += f"\n-- Table: {table}\n"

                    # Obtener estructura de tabla
                    cursor.execute("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION
                    """, (table,))

                    columns_info = cursor.fetchall()
                    backup_script += f"-- Columns: {len(columns_info)}\n"

                    # Obtener datos de la tabla (limitado para evitar archivos muy grandes)
                    # Use f-string for safe table name construction (table names are from system tables)
                    count_query = f"SELECT COUNT(*) FROM [{table}]"
                    cursor.execute(count_query)
                    row_count = cursor.fetchone()[0]

                    if row_count > 0 and \
                        row_count < 10000:  # Solo backup de tablas pequeñas
                        # Use f-string for safe table name construction (table names are from system tables)
                        select_query = f"SELECT * FROM [{table}]"
                        cursor.execute(select_query)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [desc[0] for desc in cursor.description]
                            backup_script += f"INSERT INTO [{table}] ({', '.join(columns)}) VALUES\n"

                            for i, row in enumerate(rows):
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append("NULL")
                                    elif isinstance(value, str):
                                        escaped_value = value.replace("'", "''")
                                        values.append(f"'{escaped_value}'")
                                    else:
                                        values.append(str(value))

                                backup_script += f"({', '.join(values)})"

                                if i < len(rows) - 1:
                                    backup_script += ",\n"
                                else:
                                    backup_script += ";\n"
                    else:
                        backup_script += f"-- Table {table} skipped (too large: {row_count} rows)\n"

                backup_script += f"\n-- Backup completed: {datetime.now().isoformat()}\n"

            return backup_script

        except Exception as e:
            self.logger.error("Error generando script de backup", extra={
                "database": database_name,
                "error": str(e)
            })
            return f"-- Error generating backup script: {str(e)}\n"

    def backup_files(self) -> BackupResult:
        """Backup de archivos importantes del sistema"""
        start_time = datetime.now()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"files_backup_{timestamp}.tar.gz"
            backup_path = self.files_backup_dir / backup_filename

            # Directorios a incluir en backup
            dirs_to_backup = [
                FILES_CONFIG["upload_path"],
                LOGS_DIR,
                PROJECT_ROOT / "config",
                PROJECT_ROOT / "resources"
            ]

            # Crear archive
            import tarfile

            with tarfile.open(backup_path, 'w:gz' if self.compression_enabled else 'w') as tar:
                for dir_path in dirs_to_backup:
                    if dir_path.exists():
                        tar.add(dir_path, arcname=dir_path.name)

            file_size = backup_path.stat().st_size
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info("Backup de archivos completado", extra={
                "file_path": str(backup_path),
                "size_mb": round(file_size / 1024 / 1024, 2),
                "duration_seconds": duration,
                "directories": [str(d) for d in dirs_to_backup if d.exists()]
            })

            return BackupResult(
                success=True,
                backup_type="files",
                file_path=str(backup_path),
                size_bytes=file_size,
                duration_seconds=duration,
                metadata={"directories_count": len([d for d in dirs_to_backup if d.exists()])}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.error("Error en backup de archivos", extra={
                "error": str(e),
                "duration_seconds": duration
            }, exc_info=True)

            return BackupResult(
                success=False,
                backup_type="files",
                file_path=None,
                size_bytes=0,
                duration_seconds=duration,
                error_message=str(e)
            )

    def backup_configurations(self) -> BackupResult:
        """Backup de configuraciones del sistema"""
        start_time = datetime.now()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"config_backup_{timestamp}.json"
            backup_path = self.config_backup_dir / backup_filename

            # Recopilar configuraciones (sin secretos)
            config_data = {
                "timestamp": datetime.now().isoformat(),
                "app_version": "2.0.0",
                "database_config": {
                    "driver": DATABASE_CONFIG["driver"],
                    "server": DATABASE_CONFIG["server"],
                    "databases": DATABASE_CONFIG["databases"],
                    # No incluir credenciales
                },
                "backup_config": {
                    "retention_days": BACKUP_CONFIG["retention_days"],
                    "compression": BACKUP_CONFIG["compression"],
                    "schedule": BACKUP_CONFIG.get("schedule")
                },
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "project_root": str(PROJECT_ROOT)
                }
            }

            # Escribir configuración
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            # Comprimir si está habilitado
            if self.compression_enabled:
                compressed_path = backup_path.with_suffix('.json.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                backup_path.unlink()
                backup_path = compressed_path

            file_size = backup_path.stat().st_size
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.info("Backup de configuración completado", extra={
                "file_path": str(backup_path),
                "size_bytes": file_size,
                "duration_seconds": duration
            })

            return BackupResult(
                success=True,
                backup_type="configuration",
                file_path=str(backup_path),
                size_bytes=file_size,
                duration_seconds=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            self.logger.error("Error en backup de configuración", extra={
                "error": str(e),
                "duration_seconds": duration
            }, exc_info=True)

            return BackupResult(
                success=False,
                backup_type="configuration",
                file_path=None,
                size_bytes=0,
                duration_seconds=duration,
                error_message=str(e)
            )

    def cleanup_old_backups(self):
        """Limpiar backups antiguos según política de retención"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            freed_bytes = 0

            for backup_subdir in [self.db_backup_dir, self.files_backup_dir, self.config_backup_dir]:
                for backup_file in backup_subdir.iterdir():
                    if backup_file.is_file():
                        file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                        if file_mtime < cutoff_date:
                            file_size = backup_file.stat().st_size
                            backup_file.unlink()
                            deleted_count += 1
                            freed_bytes += file_size

            self.logger.info("Limpieza de backups completada", extra={
                "deleted_files": deleted_count,
                "freed_mb": round(freed_bytes / 1024 / 1024, 2),
                "retention_days": self.retention_days
            })

        except Exception as e:
            self.logger.error("Error en limpieza de backups", extra={
                "error": str(e)
            }, exc_info=True)

    def restore_database(self, backup_file: str, target_database: str) -> bool:
        """Restaurar base de datos desde backup"""
        try:
            backup_path = Path(backup_file)

            if not backup_path.exists():
                raise FileNotFoundError(f"Archivo de backup no encontrado: {backup_file}")

            # Leer script de backup
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    script_content = f.read()
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()

            # Ejecutar script (en producción, usar transacciones)
            connection_string = (
                f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
                f"SERVER={DATABASE_CONFIG['server']};"
                f"DATABASE={target_database};"
                f"UID={DATABASE_CONFIG['username']};"
                f"PWD={DATABASE_CONFIG['password']};"
                f"TrustServerCertificate=yes;"
            )

            with pyodbc.connect(connection_string, timeout=300) as conn:
                # Ejecutar script por partes (para evitar timeouts)
                statements = script_content.split(';')

                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        cursor = conn.cursor()
                        cursor.execute(statement)
                        cursor.close()

                conn.commit()

            self.logger.info("Restauración de BD completada", extra={
                "backup_file": backup_file,
                "target_database": target_database
            })

            return True

        except Exception as e:
            self.logger.error("Error en restauración de BD", extra={
                "backup_file": backup_file,
                "target_database": target_database,
                "error": str(e)
            }, exc_info=True)

            return False

    def get_backup_status(self) -> Dict[str, Any]:
        """Obtener estado actual del sistema de backup"""
        try:
            status = {
                "scheduler_running": self._scheduler_running,
                "backup_directory": str(self.backup_dir),
                "retention_days": self.retention_days,
                "compression_enabled": self.compression_enabled,
                "recent_backups": [],
                "storage_usage": {}
            }

            # Obtener backups recientes
            all_backups = []
            for backup_subdir in [self.db_backup_dir, self.files_backup_dir, self.config_backup_dir]:
                for backup_file in backup_subdir.iterdir():
                    if backup_file.is_file():
                        stat = backup_file.stat()
                        all_backups.append({
                            "name": backup_file.name,
                            "type": backup_subdir.name,
                            "size_mb": round(stat.st_size / 1024 / 1024, 2),
                            "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })

            # Ordenar por fecha
            all_backups.sort(key=lambda x: x["created"], reverse=True)
            status["recent_backups"] = all_backups[:10]  # Últimos 10

            # Calcular uso de almacenamiento
            for backup_subdir in [self.db_backup_dir, self.files_backup_dir, self.config_backup_dir]:
                total_size = sum(f.stat().st_size for f in backup_subdir.iterdir() if f.is_file())
                file_count = len([f for f in backup_subdir.iterdir() if f.is_file()])

                status["storage_usage"][backup_subdir.name] = {
                    "total_mb": round(total_size / 1024 / 1024, 2),
                    "file_count": file_count
                }

            return status

        except Exception as e:
            self.logger.error("Error obteniendo estado de backup", extra={
                "error": str(e)
            }, exc_info=True)

            return {"error": str(e)}

# Instancia global del backup manager
backup_manager = BackupManager()

# Funciones de conveniencia
def start_backup_scheduler():
    """Iniciar scheduler de backups"""
    backup_manager.start_scheduler()

def stop_backup_scheduler():
    """Detener scheduler de backups"""
    backup_manager.stop_scheduler()

def run_backup_now() -> List[BackupResult]:
    """Ejecutar backup inmediatamente"""
    return backup_manager.backup_all()

def get_backup_status() -> Dict[str, Any]:
    """Obtener estado del sistema de backup"""
    return backup_manager.get_backup_status()
