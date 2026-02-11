"""
Sistema de Backups - Rexus.app
Implementa backups full, diferenciales y de log para SQL Server

Características:
- Backups Full diarios
- Backups Diferenciales cada 4 horas
- Backups de Log cada 15 minutos
- Retención configurable (30 días por defecto)
- Compresión de backups
- Encriptación opcional
- Notificaciones de estado
"""

import os
import sys
import logging
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

# Configurar logging
logger = logging.getLogger(__name__)


class BackupType:
    """Tipos de backup disponibles."""
    FULL = "FULL"
    DIFFERENTIAL = "DIFFERENTIAL"
    LOG = "LOG"


class BackupStatus:
    """Estados de backup."""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"


class BackupConfig:
    """Configuración del sistema de backups."""

    def __init__(self, config_file: str = None):
        """
        Inicializa la configuración de backups.

        Args:
            config_file: Ruta al archivo de configuración JSON
        """
        # Configuración por defecto
        self.backup_dir = os.getenv("BACKUP_DIR", "./backups")
        self.compression = True
        self.encryption = False
        self.encryption_key = None

        # Retención en días
        self.full_retention_days = 30
        self.differential_retention_days = 7
        self.log_retention_days = 2

        # Programación
        self.full_backup_hour = 2  # 2 AM
        self.differential_interval_hours = 4
        self.log_interval_minutes = 15

        # Bases de datos a respaldar
        self.databases = [
            os.getenv("DB_USERS", "users"),
            os.getenv("DB_INVENTARIO", "inventario"),
            os.getenv("DB_AUDITORIA", "auditoria")
        ]

        # Cargar configuración desde archivo si existe
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

        # Crear directorio de backups
        self._ensure_backup_dirs()

    def _ensure_backup_dirs(self):
        """Crea la estructura de directorios para backups."""
        dirs = [
            self.backup_dir,
            os.path.join(self.backup_dir, "full"),
            os.path.join(self.backup_dir, "differential"),
            os.path.join(self.backup_dir, "log"),
            os.path.join(self.backup_dir, "temp"),
            os.path.join(self.backup_dir, "logs")
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def load_from_file(self, config_file: str):
        """Carga configuración desde un archivo JSON."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except Exception as e:
            logger.warning(f"No se pudo cargar configuración desde {config_file}: {e}")

    def save_to_file(self, config_file: str):
        """Guarda la configuración actual en un archivo JSON."""
        try:
            config = {
                'backup_dir': self.backup_dir,
                'compression': self.compression,
                'encryption': self.encryption,
                'full_retention_days': self.full_retention_days,
                'differential_retention_days': self.differential_retention_days,
                'log_retention_days': self.log_retention_days,
                'full_backup_hour': self.full_backup_hour,
                'differential_interval_hours': self.differential_interval_hours,
                'log_interval_minutes': self.log_interval_minutes,
                'databases': self.databases
            }

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Configuración guardada en {config_file}")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")


class BackupMetadata:
    """Metadatos de un backup."""

    def __init__(self,
                 database: str,
                 backup_type: str,
                 file_path: str,
                 size_bytes: int,
                 status: str,
                 start_time: datetime,
                 end_time: datetime = None,
                 error_message: str = None):
        self.database = database
        self.backup_type = backup_type
        self.file_path = file_path
        self.size_bytes = size_bytes
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.error_message = error_message

    def to_dict(self) -> dict:
        """Convierte los metadatos a diccionario."""
        return {
            'database': self.database,
            'backup_type': self.backup_type,
            'file_path': self.file_path,
            'size_bytes': self.size_bytes,
            'size_mb': round(self.size_bytes / (1024 * 1024), 2),
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'error_message': self.error_message
        }


class BackupManager:
    """
    Gestor principal de backups para Rexus.app.

    Implementa estrategia de backups con:
    - Backups Full diarios (madrugada)
    - Backups Diferenciales cada 4 horas
    - Backups de Log cada 15 minutos
    """

    def __init__(self, config: BackupConfig = None):
        """
        Inicializa el gestor de backups.

        Args:
            config: Configuración de backups (usa default si no se proporciona)
        """
        self.config = config or BackupConfig()
        self.metadata_dir = os.path.join(self.config.backup_dir, "metadata")
        Path(self.metadata_dir).mkdir(parents=True, exist_ok=True)

        # Obtener configuración de base de datos
        self.db_server = os.getenv("DB_SERVER", "localhost")
        self.db_username = os.getenv("DB_USERNAME", "sa")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    def create_backup(self,
                     database: str,
                     backup_type: str = BackupType.FULL) -> BackupMetadata:
        """
        Crea un backup de la base de datos especificada.

        Args:
            database: Nombre de la base de datos
            backup_type: Tipo de backup (FULL, DIFFERENTIAL, LOG)

        Returns:
            BackupMetadata con el resultado del backup
        """
        start_time = datetime.now()
        status = BackupStatus.IN_PROGRESS

        # Validar que la base de datos esté en la lista
        if database not in self.config.databases:
            return BackupMetadata(
                database=database,
                backup_type=backup_type,
                file_path="",
                size_bytes=0,
                status=BackupStatus.FAILED,
                start_time=start_time,
                error_message=f"Base de datos '{database}' no configurada para backups"
            )

        # Generar nombre de archivo
        filename = self._generate_filename(database, backup_type, start_time)

        # Determinar directorio según tipo
        if backup_type == BackupType.FULL:
            backup_dir = os.path.join(self.config.backup_dir, "full")
        elif backup_type == BackupType.DIFFERENTIAL:
            backup_dir = os.path.join(self.config.backup_dir, "differential")
        else:  # LOG
            backup_dir = os.path.join(self.config.backup_dir, "log")

        file_path = os.path.join(backup_dir, filename)

        try:
            # Construir comando SQL para backup
            sql_command = self._build_backup_command(database, backup_type, file_path)

            # Ejecutar backup usando sqlcmd
            result = self._execute_sql_command(sql_command)

            if result['success']:
                # Obtener tamaño del archivo
                size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0

                # Guardar metadatos
                metadata = BackupMetadata(
                    database=database,
                    backup_type=backup_type,
                    file_path=file_path,
                    size_bytes=size_bytes,
                    status=BackupStatus.SUCCESS,
                    start_time=start_time,
                    end_time=datetime.now()
                )

                self._save_metadata(metadata)

                logger.info(f"Backup {backup_type} de {database} completado: {file_path}")
                return metadata
            else:
                metadata = BackupMetadata(
                    database=database,
                    backup_type=backup_type,
                    file_path=file_path,
                    size_bytes=0,
                    status=BackupStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message=result['error']
                )

                self._save_metadata(metadata)
                logger.error(f"Backup {backup_type} de {database} falló: {result['error']}")
                return metadata

        except Exception as e:
            metadata = BackupMetadata(
                database=database,
                backup_type=backup_type,
                file_path=file_path,
                size_bytes=0,
                status=BackupStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e)
            )

            self._save_metadata(metadata)
            logger.error(f"Error creando backup {backup_type} de {database}: {e}")
            return metadata

    def _generate_filename(self, database: str, backup_type: str, timestamp: datetime) -> str:
        """Genera un nombre de archivo para el backup."""
        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")

        if backup_type == BackupType.FULL:
            return f"{database}_FULL_{date_str}_{time_str}.bak"
        elif backup_type == BackupType.DIFFERENTIAL:
            return f"{database}_DIFF_{date_str}_{time_str}.bak"
        else:  # LOG
            return f"{database}_LOG_{date_str}_{time_str}.trn"

    def _build_backup_command(self, database: str, backup_type: str, file_path: str) -> str:
        """Construye el comando SQL de backup."""
        compression = "COMPRESSION" if self.config.compression else "NO_COMPRESSION"

        if backup_type == BackupType.LOG:
            return f"""
            BACKUP LOG [{database}]
            TO DISK = '{file_path}'
            WITH {compression},
                 STATS = 10;
            """
        elif backup_type == BackupType.DIFFERENTIAL:
            return f"""
            BACKUP DATABASE [{database}]
            TO DISK = '{file_path}'
            WITH DIFFERENTIAL,
                 {compression},
                 STATS = 10;
            """
        else:  # FULL
            return f"""
            BACKUP DATABASE [{database}]
            TO DISK = '{file_path}'
            WITH {compression},
                 STATS = 10;
            """

    def _execute_sql_command(self, sql_command: str) -> dict:
        """Ejecuta un comando SQL usando sqlcmd."""
        try:
            # Construir comando sqlcmd
            cmd = [
                "sqlcmd",
                "-S", self.db_server,
                "-U", self.db_username,
                "-P", self.db_password,
                "-Q", sql_command,
                "-t", "120"  # Timeout de 120 segundos
            ]

            # Ejecutar comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )

            if result.returncode == 0:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': result.stderr or "Error desconocido ejecutando sqlcmd"
                }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout ejecutando backup'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _save_metadata(self, metadata: BackupMetadata):
        """Guarda los metadatos de un backup."""
        try:
            meta_file = os.path.join(
                self.metadata_dir,
                f"{metadata.database}_{metadata.backup_type}_{metadata.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(meta_file, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)

        except Exception as e:
            logger.error(f"Error guardando metadatos: {e}")

    def create_all_backups(self, backup_type: str = BackupType.FULL) -> List[BackupMetadata]:
        """
        Crea backups de todas las bases de datos configuradas.

        Args:
            backup_type: Tipo de backup a crear

        Returns:
            Lista de BackupMetadata con los resultados
        """
        results = []

        for database in self.config.databases:
            metadata = self.create_backup(database, backup_type)
            results.append(metadata)

        return results

    def restore_backup(self,
                      database: str,
                      backup_file: str,
                      with_recovery: bool = True) -> dict:
        """
        Restaura un backup de la base de datos.

        Args:
            database: Nombre de la base de datos
            backup_file: Ruta al archivo de backup
            with_recovery: Si debe recuperar la base de datos (dejarla usable)

        Returns:
            Diccionario con el resultado de la restauración
        """
        try:
            recovery_state = "WITH RECOVERY" if with_recovery else "WITH NORECOVERY"

            sql_command = f"""
            RESTORE DATABASE [{database}]
            FROM DISK = '{backup_file}'
            {recovery_state},
            REPLACE;
            """

            result = self._execute_sql_command(sql_command)

            if result['success']:
                logger.info(f"Base de datos {database} restaurada desde {backup_file}")
            else:
                logger.error(f"Error restaurando {database}: {result['error']}")

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cleanup_old_backups(self) -> dict:
        """
        Elimina backups antiguos según la política de retención.

        Returns:
            Estadísticas de la limpieza
        """
        now = datetime.now()
        stats = {
            'deleted': {'full': 0, 'differential': 0, 'log': 0},
            'space_freed': 0,
            'errors': []
        }

        try:
            # Limpiar backups full
            full_dir = os.path.join(self.config.backup_dir, "full")
            stats['deleted']['full'] = self._cleanup_directory(
                full_dir,
                now - timedelta(days=self.config.full_retention_days)
            )

            # Limpiar backups diferenciales
            diff_dir = os.path.join(self.config.backup_dir, "differential")
            stats['deleted']['differential'] = self._cleanup_directory(
                diff_dir,
                now - timedelta(days=self.config.differential_retention_days)
            )

            # Limpiar backups de log
            log_dir = os.path.join(self.config.backup_dir, "log")
            stats['deleted']['log'] = self._cleanup_directory(
                log_dir,
                now - timedelta(days=self.config.log_retention_days)
            )

            # Limpiar metadatos antiguos
            self._cleanup_old_metadata(now - timedelta(days=self.config.full_retention_days))

            logger.info(f"Limpieza completada: {stats}")

        except Exception as e:
            logger.error(f"Error en limpieza de backups: {e}")
            stats['errors'].append(str(e))

        return stats

    def _cleanup_directory(self, directory: str, older_than: datetime) -> int:
        """Elimina archivos en un directorio más antiguos que la fecha especificada."""
        deleted = 0

        try:
            if not os.path.exists(directory):
                return 0

            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)

                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_time < older_than:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted += 1

                        logger.debug(f"Eliminado backup antiguo: {file_path}")

        except Exception as e:
            logger.error(f"Error limpiando directorio {directory}: {e}")

        return deleted

    def _cleanup_old_metadata(self, older_than: datetime):
        """Elimina metadatos antiguos."""
        try:
            for filename in os.listdir(self.metadata_dir):
                file_path = os.path.join(self.metadata_dir, filename)

                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_time < older_than:
                        os.remove(file_path)

        except Exception as e:
            logger.error(f"Error limpiando metadatos: {e}")

    def get_backup_status(self) -> dict:
        """
        Obtiene el estado actual del sistema de backups.

        Returns:
            Diccionario con estadísticas de backups
        """
        stats = {
            'last_full_backups': {},
            'last_differential_backups': {},
            'last_log_backups': {},
            'total_size_mb': 0,
            'backup_count': {'full': 0, 'differential': 0, 'log': 0}
        }

        try:
            for database in self.config.databases:
                # Obtener último backup de cada tipo
                stats['last_full_backups'][database] = self._get_latest_backup(database, BackupType.FULL)
                stats['last_differential_backups'][database] = self._get_latest_backup(database, BackupType.DIFFERENTIAL)
                stats['last_log_backups'][database] = self._get_latest_backup(database, BackupType.LOG)

            # Calcular tamaño total y conteos
            for backup_type in ['full', 'differential', 'log']:
                backup_dir = os.path.join(self.config.backup_dir, backup_type)

                if os.path.exists(backup_dir):
                    for filename in os.listdir(backup_dir):
                        file_path = os.path.join(backup_dir, filename)
                        if os.path.isfile(file_path):
                            stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
                            stats['backup_count'][backup_type] += 1

            stats['total_size_mb'] = round(stats['total_size_mb'], 2)

        except Exception as e:
            logger.error(f"Error obteniendo estado de backups: {e}")

        return stats

    def _get_latest_backup(self, database: str, backup_type: str) -> Optional[dict]:
        """Obtiene información del backup más reciente de una base de datos."""
        try:
            if backup_type == BackupType.FULL:
                backup_dir = os.path.join(self.config.backup_dir, "full")
            elif backup_type == BackupType.DIFFERENTIAL:
                backup_dir = os.path.join(self.config.backup_dir, "differential")
            else:
                backup_dir = os.path.join(self.config.backup_dir, "log")

            if not os.path.exists(backup_dir):
                return None

            # Buscar archivos que coincidan con la base de datos
            prefix = f"{database}_"
            if backup_type == BackupType.FULL:
                prefix += "FULL_"
            elif backup_type == BackupType.DIFFERENTIAL:
                prefix += "DIFF_"
            else:
                prefix += "LOG_"

            latest_file = None
            latest_time = None

            for filename in os.listdir(backup_dir):
                if filename.startswith(prefix):
                    file_path = os.path.join(backup_dir, filename)
                    file_time = os.path.getmtime(file_path)

                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path

            if latest_file:
                return {
                    'file_path': latest_file,
                    'file_name': os.path.basename(latest_file),
                    'size_mb': round(os.path.getsize(latest_file) / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(latest_time).isoformat()
                }

        except Exception as e:
            logger.error(f"Error obteniendo backup más reciente: {e}")

        return None


# Funciones de conveniencia para uso global
_backup_manager_instance = None


def get_backup_manager() -> BackupManager:
    """Obtiene la instancia singleton del BackupManager."""
    global _backup_manager_instance
    if _backup_manager_instance is None:
        _backup_manager_instance = BackupManager()
    return _backup_manager_instance


def create_full_backup(database: str) -> BackupMetadata:
    """Crea un backup completo de la base de datos especificada."""
    return get_backup_manager().create_backup(database, BackupType.FULL)


def create_differential_backup(database: str) -> BackupMetadata:
    """Crea un backup diferencial de la base de datos especificada."""
    return get_backup_manager().create_backup(database, BackupType.DIFFERENTIAL)


def create_log_backup(database: str) -> BackupMetadata:
    """Crea un backup de log de la base de datos especificada."""
    return get_backup_manager().create_backup(database, BackupType.LOG)


def create_all_backups(backup_type: str = BackupType.FULL) -> List[BackupMetadata]:
    """Crea backups de todas las bases de datos."""
    return get_backup_manager().create_all_backups(backup_type)
