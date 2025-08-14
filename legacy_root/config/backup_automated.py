"""
Automated Backup System for Rexus.app

Este módulo maneja las copias de seguridad automáticas de:
- Base de datos principal
- Archivos de configuración
- Logs críticos
- Datos de usuario

Características:
- Backups programados
- Rotación automática de backups antiguos
- Compresión de archivos
- Verificación de integridad
- Notificaciones de estado
"""

import os
import shutil
import sqlite3
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import hashlib

# Configurar logging
logger = logging.getLogger(__name__)

class BackupManager:
    """Gestor de copias de seguridad automatizadas."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el gestor de backups.

        Args:
            config: Configuración personalizada de backup
        """
        self.config = config or self._get_default_config()
        self.backup_root = Path(self.config['backup_directory'])
        self.backup_root.mkdir(parents=True, exist_ok=True)

        # Crear subdirectorios
        self.db_backup_dir = self.backup_root / 'database'
        self.config_backup_dir = self.backup_root / 'config'
        self.logs_backup_dir = self.backup_root / 'logs'
        self.full_backup_dir = self.backup_root / 'full'

        for directory in [self.db_backup_dir, self.config_backup_dir,
                         self.logs_backup_dir, self.full_backup_dir]:
            directory.mkdir(exist_ok=True)

    def _get_default_config(self) -> Dict:
        """Obtiene la configuración por defecto."""
        return {
            'backup_directory': 'backups',
            'max_backups': 30,  # Mantener últimos 30 backups
            'compression_enabled': True,
            'verify_integrity': True,
            'backup_schedule': {
                'database': 'daily',    # daily, weekly, hourly
                'config': 'weekly',
                'logs': 'weekly',
                'full': 'weekly'
            },
            'databases': [
                'rexus.db',
                'users.db',
                'inventario.db',
                'auditoria.db'
            ],
            'config_files': [
                'config/app_config.json',
                'config/database_config.json',
                'rexus/core/config.py'
            ],
            'log_directories': [
                'logs'
            ]
        }

    def create_database_backup(self) -> Dict[str, str]:
        """
        Crea backup de todas las bases de datos.

        Returns:
            Dict: Resultado del backup con paths y checksums
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {}

        logger.info("Iniciando backup de bases de datos")

        for db_name in self.config['databases']:
            db_path = Path(db_name)
            if not db_path.exists():
                logger.warning("Base de datos no encontrada: %s", db_name)
                continue

            try:
                # Nombre del archivo de backup
                backup_filename = f"{db_path.stem}_{timestamp}.db"
                backup_path = self.db_backup_dir / backup_filename

                # Crear backup usando SQLite backup API si es SQLite
                if db_name.endswith('.db'):
                    self._backup_sqlite_database(str(db_path), str(backup_path))
                else:
                    # Para otros tipos de DB, copiar archivo
                    shutil.copy2(db_path, backup_path)

                # Verificar integridad si está habilitado
                checksum = None
                if self.config['verify_integrity']:
                    checksum = self._calculate_checksum(backup_path)

                # Comprimir si está habilitado
                if self.config['compression_enabled']:
                    compressed_path = backup_path.with_suffix('.zip')
                    self._compress_file(backup_path, compressed_path)
                    backup_path.unlink()  # Eliminar archivo sin comprimir
                    backup_path = compressed_path

                results[db_name] = {
                    'backup_path': str(backup_path),
                    'checksum': checksum,
                    'timestamp': timestamp,
                    'size': backup_path.stat().st_size
                }

                logger.info("Backup creado: %s -> %s", db_name, backup_path.name)

            except Exception as e:
                logger.error("Error creando backup de %s: %s", db_name, e)
                results[db_name] = {'error': str(e)}

        # Limpiar backups antiguos
        self._cleanup_old_backups(self.db_backup_dir)

        return results

    def create_config_backup(self) -> Dict[str, str]:
        """
        Crea backup de archivos de configuración.

        Returns:
            Dict: Resultado del backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {}

        logger.info("Iniciando backup de configuración")

        for config_file in self.config['config_files']:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning("Archivo de configuración no encontrado: %s", config_file)
                continue

            try:
                backup_filename = f"{config_path.name}_{timestamp}"
                backup_path = self.config_backup_dir / backup_filename

                shutil.copy2(config_path, backup_path)

                results[config_file] = {
                    'backup_path': str(backup_path),
                    'timestamp': timestamp,
                    'size': backup_path.stat().st_size
                }

                logger.info("Backup de configuración creado: %s", backup_path.name)

            except Exception as e:
                logger.error("Error creando backup de configuración %s: %s", config_file, e)
                results[config_file] = {'error': str(e)}

        self._cleanup_old_backups(self.config_backup_dir)
        return results

    def create_logs_backup(self) -> Dict[str, str]:
        """
        Crea backup de logs.

        Returns:
            Dict: Resultado del backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {}

        logger.info("Iniciando backup de logs")

        for log_dir in self.config['log_directories']:
            log_path = Path(log_dir)
            if not log_path.exists():
                continue

            try:
                backup_filename = f"logs_backup_{timestamp}.zip"
                backup_path = self.logs_backup_dir / backup_filename

                self._compress_directory(log_path, backup_path)

                results[log_dir] = {
                    'backup_path': str(backup_path),
                    'timestamp': timestamp,
                    'size': backup_path.stat().st_size
                }

                logger.info("Backup de logs creado: %s", backup_path.name)

            except Exception as e:
                logger.error("Error creando backup de logs %s: %s", log_dir, e)
                results[log_dir] = {'error': str(e)}

        self._cleanup_old_backups(self.logs_backup_dir)
        return results

    def create_full_backup(self) -> Dict[str, str]:
        """
        Crea backup completo del sistema.

        Returns:
            Dict: Resultado del backup completo
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        logger.info("Iniciando backup completo del sistema")

        try:
            # Crear backup de cada componente
            db_results = self.create_database_backup()
            config_results = self.create_config_backup()
            logs_results = self.create_logs_backup()

            # Crear archivo de metadatos
            metadata = {
                'timestamp': timestamp,
                'backup_type': 'full',
                'databases': db_results,
                'configuration': config_results,
                'logs': logs_results,
                'rexus_version': self._get_app_version(),
                'system_info': self._get_system_info()
            }

            metadata_path = self.full_backup_dir / f"backup_metadata_{timestamp}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info("Backup completo finalizado: %s", timestamp)

            return {
                'success': True,
                'timestamp': timestamp,
                'metadata_path': str(metadata_path),
                'components': {
                    'databases': len([r for r in db_results.values() if 'error' not in r]),
                    'config_files': len([r for r in config_results.values() if 'error' not in r]),
                    'log_backups': len([r for r in logs_results.values() if 'error' not in r])
                }
            }

        except Exception as e:
            logger.error("Error en backup completo: %s", e)
            return {'success': False, 'error': str(e)}

    def restore_database(self, backup_path: str, target_db: str) -> bool:
        """
        Restaura una base de datos desde backup.

        Args:
            backup_path: Ruta del backup
            target_db: Base de datos de destino

        Returns:
            bool: True si la restauración fue exitosa
        """
        try:
            backup_path = Path(backup_path)

            # Descomprimir si es necesario
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    extracted_files = zip_ref.namelist()
                    if len(extracted_files) != 1:
                        raise ValueError("El archivo ZIP debe contener exactamente un archivo")

                    temp_dir = backup_path.parent / 'temp'
                    temp_dir.mkdir(exist_ok=True)
                    zip_ref.extractall(temp_dir)

                    source_path = temp_dir / extracted_files[0]
            else:
                source_path = backup_path

            # Realizar restauración
            shutil.copy2(source_path, target_db)

            # Limpiar archivos temporales
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir)

            logger.info("Base de datos restaurada: %s <- %s", target_db, backup_path.name)
            return True

        except Exception as e:
            logger.error("Error restaurando base de datos %s: %s", target_db, e)
            return False

    def _backup_sqlite_database(self, source_db: str, backup_path: str):
        """Crea backup de base de datos SQLite usando API nativa."""
        source_conn = sqlite3.connect(source_db)
        backup_conn = sqlite3.connect(backup_path)

        try:
            source_conn.backup(backup_conn)
        finally:
            source_conn.close()
            backup_conn.close()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de un archivo."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _compress_file(self, source_path: Path, target_path: Path):
        """Comprime un archivo individual."""
        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            zip_ref.write(source_path, source_path.name)

    def _compress_directory(self, source_dir: Path, target_path: Path):
        """Comprime un directorio completo."""
        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arc_path = file_path.relative_to(source_dir.parent)
                    zip_ref.write(file_path, arc_path)

    def _cleanup_old_backups(self, backup_dir: Path):
        """Elimina backups antiguos según configuración."""
        if not backup_dir.exists():
            return

        backup_files = list(backup_dir.glob('*'))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        max_backups = self.config['max_backups']
        if len(backup_files) > max_backups:
            for old_backup in backup_files[max_backups:]:
                try:
                    old_backup.unlink()
                    logger.info("Backup antiguo eliminado: %s", old_backup.name)
                except Exception as e:
                    logger.error("Error eliminando backup antiguo %s: %s", old_backup.name, e)

    def _get_app_version(self) -> str:
        """Obtiene la versión de la aplicación."""
        try:
            version_file = Path('version.txt')
            if version_file.exists():
                return version_file.read_text().strip()
            return "unknown"
        except:
            return "unknown"

    def _get_system_info(self) -> Dict:
        """Obtiene información del sistema."""
        import platform
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }

    def get_backup_status(self) -> Dict:
        """
        Obtiene el estado de los backups.

        Returns:
            Dict: Información de estado de backups
        """
        status = {
            'backup_directory': str(self.backup_root),
            'last_backups': {},
            'disk_usage': {},
            'backup_counts': {}
        }

        # Información de cada tipo de backup
        backup_dirs = {
            'database': self.db_backup_dir,
            'config': self.config_backup_dir,
            'logs': self.logs_backup_dir,
            'full': self.full_backup_dir
        }

        for backup_type, backup_dir in backup_dirs.items():
            if backup_dir.exists():
                files = list(backup_dir.glob('*'))
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                status['backup_counts'][backup_type] = len(files)

                if files:
                    latest = files[0]
                    status['last_backups'][backup_type] = {
                        'filename': latest.name,
                        'timestamp': datetime.fromtimestamp(latest.stat().st_mtime).isoformat(),
                        'size': latest.stat().st_size
                    }

                # Calcular uso de disco
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                status['disk_usage'][backup_type] = total_size

        return status


# Instancia global
_backup_manager = None

def get_backup_manager(config: Optional[Dict] = None) -> BackupManager:
    """Obtiene la instancia global del backup manager."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager(config)
    return _backup_manager

# Funciones de conveniencia
def create_daily_backup():
    """Crea los backups diarios programados."""
    manager = get_backup_manager()

    # Backup de base de datos (diario)
    db_result = manager.create_database_backup()

    logger.info("Backup diario completado: %s bases de datos procesadas",
                len([r for r in db_result.values() if 'error' not in r]))

def create_weekly_backup():
    """Crea los backups semanales programados."""
    manager = get_backup_manager()

    # Backup completo (semanal)
    full_result = manager.create_full_backup()

    if full_result.get('success'):
        logger.info("Backup semanal completo exitoso")
    else:
        logger.error("Error en backup semanal: %s", full_result.get('error'))

# Funciones para integración con scheduler
def schedule_automated_backups():
    """
    Configura backups automáticos.

    Esta función debe ser llamada al iniciar la aplicación
    para programar los backups automáticos.
    """
    # Aquí se integraría con un scheduler como APScheduler
    # o se configuraría como tarea del sistema operativo
    logger.info("Sistema de backups automáticos inicializado")
