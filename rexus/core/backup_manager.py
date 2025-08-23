"""
Sistema de Backup Automatizado para Rexus
Versión: 2.0.0 - Enterprise Ready
"""


import logging
logger = logging.getLogger(__name__)

import sys
import json
import gzip
import shutil
import schedule
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
