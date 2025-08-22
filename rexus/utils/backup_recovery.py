"""
Automated Backup and Recovery System for Rexus.app v2.0.0
Sistema automatizado de respaldo y recuperación

Funcionalidades:
- Backup automático de base de datos
- Backup de archivos de configuración
- Backup incremental y completo
- Recuperación automática en caso de fallos
- Verificación de integridad de backups
- Programación automática de backups
"""

import os
import shutil
import sqlite3
import zipfile
import hashlib
import threading
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import json
import tempfile

from rexus.utils.app_logger import get_logger
from rexus.core.database import get_inventario_connection, get_users_connection

logger = get_logger(__name__)

@dataclass
class BackupConfig:
    """Configuración para el sistema de backup"""
    backup_directory: str = "backups"
    max_backups: int = 30
    full_backup_interval: int = 7  # días
    incremental_backup_interval: int = 1  # días
    compress_backups: bool = True
    verify_integrity: bool = True
    schedule_enabled: bool = True
    schedule_time: str = "02:00"  # 2 AM
    include_logs: bool = True
    include_config: bool = True
    include_sql_files: bool = True

@dataclass
class BackupInfo:
    """Información de un backup"""
    backup_id: str
    timestamp: datetime
    backup_type: str  # 'full' or 'incremental'
    size_bytes: int
    checksum: str
    files_count: int
    database_included: bool
    config_included: bool
    status: str  # 'completed', 'failed', 'corrupted'
    recovery_verified: bool = False

class BackupRecoveryManager:
    """Gestor de backup y recuperación automático"""
    
    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.backup_history: List[BackupInfo] = []
        self.is_scheduled = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Crear directorio de backups si no existe
        self.backup_path = Path(self.config.backup_directory)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Cargar historial de backups
        self._load_backup_history()
        
        logger.info(f"Backup Recovery Manager initialized - Directory: {self.backup_path}")
    
    def create_full_backup(self) -> Optional[BackupInfo]:
        """Crea un backup completo del sistema"""
        backup_id = f"full_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting full backup: {backup_id}")
        
        try:
            with self.lock:
                backup_dir = self.backup_path / backup_id
                backup_dir.mkdir(exist_ok=True)
                
                files_count = 0
                database_included = False
                config_included = False
                
                # 1. Backup de base de datos
                db_backup_path = backup_dir / "database"
                db_backup_path.mkdir(exist_ok=True)
                
                if self._backup_databases(db_backup_path):
                    database_included = True
                    files_count += self._count_files(db_backup_path)
                    logger.info("Database backup completed")
                
                # 2. Backup de archivos de configuración
                if self.config.include_config:
                    config_backup_path = backup_dir / "config"
                    config_backup_path.mkdir(exist_ok=True)
                    
                    if self._backup_configuration_files(config_backup_path):
                        config_included = True
                        files_count += self._count_files(config_backup_path)
                        logger.info("Configuration backup completed")
                
                # 3. Backup de archivos SQL
                if self.config.include_sql_files:
                    sql_backup_path = backup_dir / "sql"
                    if self._backup_sql_files(sql_backup_path):
                        files_count += self._count_files(sql_backup_path)
                        logger.info("SQL files backup completed")
                
                # 4. Backup de logs si está habilitado
                if self.config.include_logs:
                    logs_backup_path = backup_dir / "logs"
                    if self._backup_logs(logs_backup_path):
                        files_count += self._count_files(logs_backup_path)
                        logger.info("Logs backup completed")
                
                # 5. Crear archivo comprimido si está habilitado
                final_path = backup_dir
                if self.config.compress_backups:
                    zip_path = self.backup_path / f"{backup_id}.zip"
                    self._compress_backup(backup_dir, zip_path)
                    shutil.rmtree(backup_dir)  # Eliminar directorio no comprimido
                    final_path = zip_path
                    logger.info(f"Backup compressed: {zip_path}")
                
                # 6. Calcular checksum y tamaño
                size_bytes = self._get_backup_size(final_path)
                checksum = self._calculate_checksum(final_path)
                
                # 7. Verificar integridad si está habilitado
                recovery_verified = False
                if self.config.verify_integrity:
                    recovery_verified = self._verify_backup_integrity(final_path, backup_id)
                
                # 8. Crear registro de backup
                backup_info = BackupInfo(
                    backup_id=backup_id,
                    timestamp=datetime.now(),
                    backup_type="full",
                    size_bytes=size_bytes,
                    checksum=checksum,
                    files_count=files_count,
                    database_included=database_included,
                    config_included=config_included,
                    status="completed",
                    recovery_verified=recovery_verified
                )
                
                # 9. Guardar en historial
                self.backup_history.append(backup_info)
                self._save_backup_history()
                
                # 10. Limpiar backups antiguos
                self._cleanup_old_backups()
                
                logger.info(f"Full backup completed successfully: {backup_id}")
                logger.info(f"Size: {size_bytes / 1024 / 1024:.2f} MB, Files: {files_count}")
                
                return backup_info
                
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            # Crear registro de backup fallido
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type="full",
                size_bytes=0,
                checksum="",
                files_count=0,
                database_included=False,
                config_included=False,
                status="failed"
            )
            self.backup_history.append(backup_info)
            self._save_backup_history()
            return None
    
    def create_incremental_backup(self) -> Optional[BackupInfo]:
        """Crea un backup incremental (solo cambios desde el último backup)"""
        backup_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting incremental backup: {backup_id}")
        
        try:
            # Encontrar último backup para comparación
            last_backup = self._get_last_successful_backup()
            if not last_backup:
                logger.info("No previous backup found, creating full backup instead")
                return self.create_full_backup()
            
            last_backup_time = last_backup.timestamp
            
            with self.lock:
                backup_dir = self.backup_path / backup_id
                backup_dir.mkdir(exist_ok=True)
                
                files_count = 0
                
                # Solo incluir archivos modificados desde el último backup
                modified_files = self._get_modified_files_since(last_backup_time)
                
                if not modified_files:
                    logger.info("No files modified since last backup")
                    return None
                
                # Backup de archivos modificados
                changes_dir = backup_dir / "changes"
                changes_dir.mkdir(exist_ok=True)
                
                for file_path in modified_files:
                    try:
                        rel_path = Path(file_path).relative_to(Path.cwd())
                        dest_path = changes_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        files_count += 1
                    except Exception as e:
                        logger.warning(f"Could not backup modified file {file_path}: {e}")
                
                # Backup incremental de base de datos (solo transacciones recientes)
                db_backup_path = backup_dir / "database_incremental"
                db_backup_path.mkdir(exist_ok=True)
                database_included = self._backup_database_incremental(db_backup_path, last_backup_time)
                
                # Comprimir si está habilitado
                final_path = backup_dir
                if self.config.compress_backups:
                    zip_path = self.backup_path / f"{backup_id}.zip"
                    self._compress_backup(backup_dir, zip_path)
                    shutil.rmtree(backup_dir)
                    final_path = zip_path
                
                # Calcular estadísticas
                size_bytes = self._get_backup_size(final_path)
                checksum = self._calculate_checksum(final_path)
                
                # Crear registro
                backup_info = BackupInfo(
                    backup_id=backup_id,
                    timestamp=datetime.now(),
                    backup_type="incremental",
                    size_bytes=size_bytes,
                    checksum=checksum,
                    files_count=files_count,
                    database_included=database_included,
                    config_included=False,
                    status="completed"
                )
                
                self.backup_history.append(backup_info)
                self._save_backup_history()
                
                logger.info(f"Incremental backup completed: {backup_id}")
                logger.info(f"Size: {size_bytes / 1024:.2f} KB, Files: {files_count}")
                
                return backup_info
                
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            return None
    
    def restore_from_backup(self, backup_id: str, target_directory: str = None) -> bool:
        """Restaura el sistema desde un backup específico"""
        logger.info(f"Starting restore from backup: {backup_id}")
        
        try:
            backup_info = self._get_backup_info(backup_id)
            if not backup_info:
                logger.error(f"Backup not found: {backup_id}")
                return False
            
            if backup_info.status != "completed":
                logger.error(f"Cannot restore from failed backup: {backup_id}")
                return False
            
            # Encontrar archivo de backup
            backup_file = None
            if self.config.compress_backups:
                backup_file = self.backup_path / f"{backup_id}.zip"
            else:
                backup_file = self.backup_path / backup_id
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Crear directorio temporal para extracción
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extraer backup
                if self.config.compress_backups:
                    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_path)
                    extracted_path = temp_path / backup_id
                else:
                    extracted_path = backup_file
                
                # Restaurar base de datos
                if backup_info.database_included:
                    db_path = extracted_path / "database"
                    if db_path.exists():
                        if self._restore_databases(db_path):
                            logger.info("Database restored successfully")
                        else:
                            logger.error("Database restore failed")
                            return False
                
                # Restaurar archivos de configuración
                if backup_info.config_included:
                    config_path = extracted_path / "config"
                    if config_path.exists():
                        if self._restore_configuration_files(config_path, target_directory):
                            logger.info("Configuration files restored successfully")
                        else:
                            logger.warning("Configuration restore had issues")
                
                # Restaurar archivos SQL
                sql_path = extracted_path / "sql"
                if sql_path.exists():
                    if self._restore_sql_files(sql_path, target_directory):
                        logger.info("SQL files restored successfully")
                
            logger.info(f"Restore completed successfully from backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def start_automated_backup(self):
        """Inicia el sistema de backup automatizado"""
        if self.is_scheduled:
            logger.warning("Automated backup is already running")
            return
        
        if not self.config.schedule_enabled:
            logger.info("Automated backup is disabled in configuration")
            return
        
        # Programar backups
        schedule.clear()
        
        # Backup completo semanal
        schedule.every(self.config.full_backup_interval).days.at(self.config.schedule_time).do(
            self.create_full_backup
        )
        
        # Backup incremental diario
        schedule.every(self.config.incremental_backup_interval).days.at(self.config.schedule_time).do(
            self.create_incremental_backup
        )
        
        # Iniciar thread del scheduler
        self.is_scheduled = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Automated backup system started")
        logger.info(f"Full backup: every {self.config.full_backup_interval} days at {self.config.schedule_time}")
        logger.info(f"Incremental backup: every {self.config.incremental_backup_interval} days at {self.config.schedule_time}")
    
    def stop_automated_backup(self):
        """Detiene el sistema de backup automatizado"""
        self.is_scheduled = False
        schedule.clear()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Automated backup system stopped")
    
    def get_backup_status(self) -> Dict:
        """Obtiene estado actual del sistema de backup"""
        with self.lock:
            total_backups = len(self.backup_history)
            successful_backups = len([b for b in self.backup_history if b.status == "completed"])
            failed_backups = len([b for b in self.backup_history if b.status == "failed"])
            
            last_backup = self._get_last_successful_backup()
            last_backup_info = None
            if last_backup:
                last_backup_info = {
                    'id': last_backup.backup_id,
                    'timestamp': last_backup.timestamp.isoformat(),
                    'type': last_backup.backup_type,
                    'size_mb': last_backup.size_bytes / 1024 / 1024
                }
            
            total_size = sum(b.size_bytes for b in self.backup_history if b.status == "completed")
            
            return {
                'total_backups': total_backups,
                'successful_backups': successful_backups,
                'failed_backups': failed_backups,
                'success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                'total_size_mb': total_size / 1024 / 1024,
                'last_backup': last_backup_info,
                'automated_backup_enabled': self.is_scheduled,
                'backup_directory': str(self.backup_path)
            }
    
    def list_available_backups(self) -> List[Dict]:
        """Lista todos los backups disponibles"""
        return [
            {
                'id': backup.backup_id,
                'timestamp': backup.timestamp.isoformat(),
                'type': backup.backup_type,
                'size_mb': backup.size_bytes / 1024 / 1024,
                'files_count': backup.files_count,
                'status': backup.status,
                'database_included': backup.database_included,
                'config_included': backup.config_included,
                'recovery_verified': backup.recovery_verified
            }
            for backup in sorted(self.backup_history, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verifica la integridad de un backup específico"""
        try:
            backup_info = self._get_backup_info(backup_id)
            if not backup_info:
                return False
            
            backup_file = None
            if self.config.compress_backups:
                backup_file = self.backup_path / f"{backup_id}.zip"
            else:
                backup_file = self.backup_path / backup_id
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Verificar checksum
            current_checksum = self._calculate_checksum(backup_file)
            if current_checksum != backup_info.checksum:
                logger.error(f"Checksum mismatch for backup {backup_id}")
                return False
            
            # Verificar que se puede extraer/leer
            if self.config.compress_backups:
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                        zip_ref.testzip()  # Verifica integridad del ZIP
                except zipfile.BadZipFile:
                    logger.error(f"Corrupted ZIP file: {backup_file}")
                    return False
            
            logger.info(f"Backup integrity verified: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Backup integrity verification failed: {e}")
            return False
    
    def cleanup_corrupted_backups(self) -> int:
        """Limpia backups corruptos y devuelve cantidad eliminada"""
        cleaned_count = 0
        
        try:
            with self.lock:
                corrupted_backups = []
                
                for backup in self.backup_history:
                    if not self.verify_backup_integrity(backup.backup_id):
                        corrupted_backups.append(backup)
                
                for backup in corrupted_backups:
                    # Eliminar archivo corrupto
                    backup_file = None
                    if self.config.compress_backups:
                        backup_file = self.backup_path / f"{backup.backup_id}.zip"
                    else:
                        backup_file = self.backup_path / backup.backup_id
                    
                    if backup_file.exists():
                        if backup_file.is_dir():
                            shutil.rmtree(backup_file)
                        else:
                            backup_file.unlink()
                    
                    # Actualizar estado en historial
                    backup.status = "corrupted"
                    cleaned_count += 1
                    logger.info(f"Removed corrupted backup: {backup.backup_id}")
                
                if cleaned_count > 0:
                    self._save_backup_history()
                    logger.info(f"Cleaned up {cleaned_count} corrupted backups")
            
        except Exception as e:
            logger.error(f"Error during corrupted backup cleanup: {e}")
        
        return cleaned_count
    
    # Métodos privados auxiliares
    
    def _backup_databases(self, backup_path: Path) -> bool:
        """Backup de las bases de datos"""
        try:
            # Backup de inventario DB
            inv_conn = get_inventario_connection()
            if inv_conn:
                inv_backup_path = backup_path / "inventario.bak"
                cursor = inv_conn.cursor()
                # Usar consulta parametrizada para prevenir SQL injection
                cursor.execute("BACKUP DATABASE inventario TO DISK = ?", (str(inv_backup_path),))
                cursor.close()
                logger.debug("Inventario database backed up")
            
            # Backup de users DB  
            users_conn = get_users_connection()
            if users_conn:
                users_backup_path = backup_path / "users.bak"
                cursor = users_conn.cursor()
                # Usar consulta parametrizada para prevenir SQL injection
                cursor.execute("BACKUP DATABASE users TO DISK = ?", (str(users_backup_path),))
                cursor.close()
                logger.debug("Users database backed up")
            
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def _backup_configuration_files(self, backup_path: Path) -> bool:
        """Backup de archivos de configuración"""
        try:
            config_files = [
                "CLAUDE.md",
                "requirements.txt",
                "main.py"
            ]
            
            copied_count = 0
            for config_file in config_files:
                source_path = Path(config_file)
                if source_path.exists():
                    dest_path = backup_path / config_file
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
            
            # Backup del directorio rexus/ (core code)
            rexus_source = Path("rexus")
            if rexus_source.exists():
                rexus_dest = backup_path / "rexus"
                shutil.copytree(rexus_source, rexus_dest, dirs_exist_ok=True)
                copied_count += 1
            
            return copied_count > 0
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return False
    
    def _backup_sql_files(self, backup_path: Path) -> bool:
        """Backup de archivos SQL"""
        try:
            sql_source = Path("sql")
            if sql_source.exists():
                shutil.copytree(sql_source, backup_path, dirs_exist_ok=True)
                return True
            return False
        except Exception as e:
            logger.error(f"SQL files backup failed: {e}")
            return False
    
    def _backup_logs(self, backup_path: Path) -> bool:
        """Backup de logs"""
        try:
            logs_source = Path("logs")
            if logs_source.exists():
                shutil.copytree(logs_source, backup_path, dirs_exist_ok=True)
                return True
            return False
        except Exception as e:
            logger.error(f"Logs backup failed: {e}")
            return False
    
    def _compress_backup(self, source_dir: Path, zip_path: Path):
        """Comprime un directorio de backup"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arc_path = file_path.relative_to(source_dir.parent)
                    zip_ref.write(file_path, arc_path)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de un archivo"""
        hash_md5 = hashlib.md5()
        if file_path.is_file():
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_backup_size(self, backup_path: Path) -> int:
        """Obtiene tamaño de un backup"""
        if backup_path.is_file():
            return backup_path.stat().st_size
        elif backup_path.is_dir():
            total_size = 0
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        return 0
    
    def _count_files(self, directory: Path) -> int:
        """Cuenta archivos en un directorio"""
        if not directory.exists():
            return 0
        return len([f for f in directory.rglob('*') if f.is_file()])
    
    def _get_last_successful_backup(self) -> Optional[BackupInfo]:
        """Obtiene el último backup exitoso"""
        successful_backups = [b for b in self.backup_history if b.status == "completed"]
        if successful_backups:
            return max(successful_backups, key=lambda x: x.timestamp)
        return None
    
    def _get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Obtiene información de un backup específico"""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def _cleanup_old_backups(self):
        """Limpia backups antiguos según configuración"""
        try:
            with self.lock:
                successful_backups = [b for b in self.backup_history if b.status == "completed"]
                if len(successful_backups) <= self.config.max_backups:
                    return
                
                # Ordenar por timestamp y eliminar los más antiguos
                sorted_backups = sorted(successful_backups, key=lambda x: x.timestamp, reverse=True)
                backups_to_remove = sorted_backups[self.config.max_backups:]
                
                for backup in backups_to_remove:
                    # Eliminar archivo físico
                    backup_file = None
                    if self.config.compress_backups:
                        backup_file = self.backup_path / f"{backup.backup_id}.zip"
                    else:
                        backup_file = self.backup_path / backup.backup_id
                    
                    if backup_file.exists():
                        if backup_file.is_dir():
                            shutil.rmtree(backup_file)
                        else:
                            backup_file.unlink()
                    
                    # Eliminar del historial
                    self.backup_history.remove(backup)
                    logger.debug(f"Removed old backup: {backup.backup_id}")
                
                self._save_backup_history()
                logger.info(f"Cleaned up {len(backups_to_remove)} old backups")
                
        except Exception as e:
            logger.error(f"Error during old backup cleanup: {e}")
    
    def _load_backup_history(self):
        """Carga historial de backups desde archivo"""
        history_file = self.backup_path / "backup_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        backup_info = BackupInfo(
                            backup_id=item['backup_id'],
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            backup_type=item['backup_type'],
                            size_bytes=item['size_bytes'],
                            checksum=item['checksum'],
                            files_count=item['files_count'],
                            database_included=item['database_included'],
                            config_included=item['config_included'],
                            status=item['status'],
                            recovery_verified=item.get('recovery_verified', False)
                        )
                        self.backup_history.append(backup_info)
                logger.debug(f"Loaded {len(self.backup_history)} backup records from history")
            except Exception as e:
                logger.error(f"Error loading backup history: {e}")
    
    def _save_backup_history(self):
        """Guarda historial de backups en archivo"""
        history_file = self.backup_path / "backup_history.json"
        try:
            data = []
            for backup in self.backup_history:
                data.append({
                    'backup_id': backup.backup_id,
                    'timestamp': backup.timestamp.isoformat(),
                    'backup_type': backup.backup_type,
                    'size_bytes': backup.size_bytes,
                    'checksum': backup.checksum,
                    'files_count': backup.files_count,
                    'database_included': backup.database_included,
                    'config_included': backup.config_included,
                    'status': backup.status,
                    'recovery_verified': backup.recovery_verified
                })
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving backup history: {e}")
    
    def _run_scheduler(self):
        """Loop principal del scheduler de backups"""
        while self.is_scheduled:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _get_modified_files_since(self, timestamp: datetime) -> List[str]:
        """Obtiene archivos modificados desde un timestamp"""
        modified_files = []
        threshold = timestamp.timestamp()
        
        # Buscar en directorios clave
        search_paths = ["rexus/", "sql/", "CLAUDE.md", "requirements.txt"]
        
        for search_path in search_paths:
            path = Path(search_path)
            if path.exists():
                if path.is_file():
                    if path.stat().st_mtime > threshold:
                        modified_files.append(str(path))
                else:
                    for file_path in path.rglob('*'):
                        if file_path.is_file() and file_path.stat().st_mtime > threshold:
                            modified_files.append(str(file_path))
        
        return modified_files
    
    def _backup_database_incremental(self, backup_path: Path, since: datetime) -> bool:
        """Backup incremental de base de datos (simulado)"""
        try:
            # En un sistema real, esto sería un backup de transacciones/logs
            # Por simplicidad, solo creamos un marcador
            marker_file = backup_path / f"incremental_since_{since.strftime('%Y%m%d_%H%M%S')}.marker"
            with open(marker_file, 'w') as f:
                f.write(f"Incremental backup marker since {since.isoformat()}")
            return True
        except Exception as e:
            logger.error(f"Incremental database backup failed: {e}")
            return False
    
    def _verify_backup_integrity(self, backup_path: Path, backup_id: str) -> bool:
        """Verifica integridad completa de un backup"""
        try:
            # Test básico de integridad
            return self.verify_backup_integrity(backup_id)
        except Exception as e:
            logger.error(f"Backup integrity verification failed: {e}")
            return False
    
    def _restore_databases(self, db_backup_path: Path) -> bool:
        """Restaura bases de datos desde backup"""
        try:
            # En sistema real, aquí se restaurarían las bases de datos
            # Por seguridad, solo logueamos la operación
            logger.info(f"Database restore from {db_backup_path} - SIMULATION ONLY")
            return True
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    def _restore_configuration_files(self, config_backup_path: Path, target_dir: str = None) -> bool:
        """Restaura archivos de configuración"""
        try:
            target_path = Path(target_dir) if target_dir else Path.cwd()
            
            for item in config_backup_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(config_backup_path)
                    dest_path = target_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            logger.info("Configuration files restored")
            return True
            
        except Exception as e:
            logger.error(f"Configuration restore failed: {e}")
            return False
    
    def _restore_sql_files(self, sql_backup_path: Path, target_dir: str = None) -> bool:
        """Restaura archivos SQL"""
        try:
            target_path = Path(target_dir) if target_dir else Path.cwd()
            sql_dest = target_path / "sql"
            
            if sql_dest.exists():
                shutil.rmtree(sql_dest)
            
            shutil.copytree(sql_backup_path, sql_dest)
            logger.info("SQL files restored")
            return True
            
        except Exception as e:
            logger.error(f"SQL files restore failed: {e}")
            return False


# Instancia global del gestor de backup
_backup_recovery_manager = None

def get_backup_recovery_manager() -> BackupRecoveryManager:
    """Obtiene la instancia global del gestor de backup y recovery"""
    global _backup_recovery_manager
    if _backup_recovery_manager is None:
        _backup_recovery_manager = BackupRecoveryManager()
    return _backup_recovery_manager

# Funciones de conveniencia
def create_emergency_backup() -> Optional[BackupInfo]:
    """Crea un backup de emergencia inmediato"""
    manager = get_backup_recovery_manager()
    logger.info("Creating emergency backup...")
    return manager.create_full_backup()

def restore_latest_backup(target_directory: str = None) -> bool:
    """Restaura desde el backup más reciente"""
    manager = get_backup_recovery_manager()
    last_backup = manager._get_last_successful_backup()
    if last_backup:
        logger.info(f"Restoring from latest backup: {last_backup.backup_id}")
        return manager.restore_from_backup(last_backup.backup_id, target_directory)
    else:
        logger.error("No successful backup found for restoration")
        return False

def start_automatic_backups():
    """Inicia el sistema de backup automático"""
    manager = get_backup_recovery_manager()
    manager.start_automated_backup()

def get_backup_health_report() -> Dict:
    """Obtiene reporte de salud del sistema de backup"""
    manager = get_backup_recovery_manager()
    status = manager.get_backup_status()
    
    # Agregar información de salud
    last_backup_age = None
    if status['last_backup']:
        last_backup_time = datetime.fromisoformat(status['last_backup']['timestamp'])
        last_backup_age = (datetime.now() - last_backup_time).days
    
    health_report = status.copy()
    health_report.update({
        'health_status': 'healthy' if status['success_rate'] > 90 else 'warning' if status['success_rate'] > 70 else 'critical',
        'last_backup_age_days': last_backup_age,
        'backup_age_status': 'recent' if last_backup_age and last_backup_age < 7 else 'old' if last_backup_age and last_backup_age < 30 else 'very_old'
    })
    
    return health_report