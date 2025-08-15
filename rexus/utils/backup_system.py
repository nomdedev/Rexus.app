"""
Sistema de Backup Automatizado para Rexus.app

Proporciona funcionalidades de backup automático para las 3 bases de datos
del sistema con compresión, rotación y notificaciones.
"""

import os
import shutil
import sqlite3
import zipfile
import json
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path
import logging
from PyQt6.QtCore import QObject, pyqtSignal


class BackupConfig:
    """Configuración del sistema de backups."""

    def __init__(self):
        self.backup_dir = "backups"
        self.backup_schedule = "daily"  # daily, weekly, monthly
        self.backup_time = "02:00"  # HH:MM
        self.retention_days = 30
        self.compress_backups = True
        self.backup_databases = ["users", "inventario", "auditoria"]
        self.notification_enabled = True
        self.auto_cleanup = True

    @classmethod
    def from_file(cls, config_path: str):
        """Carga configuración desde archivo JSON."""
        config = cls()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
        except Exception as e:
            logging.error(f"Error cargando configuración de backup: {e}")
        return config

    def save_to_file(self, config_path: str):
        """Guarda configuración a archivo JSON."""
        try:
            config_data = {
                'backup_dir': self.backup_dir,
                'backup_schedule': self.backup_schedule,
                'backup_time': self.backup_time,
                'retention_days': self.retention_days,
                'compress_backups': self.compress_backups,
                'backup_databases': self.backup_databases,
                'notification_enabled': self.notification_enabled,
                'auto_cleanup': self.auto_cleanup
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando configuración de backup: {e}")


class BackupResult:
    """Resultado de una operación de backup."""

    def __init__(self, success: bool = False, message: str = "",
                 backup_path: str = "", size_mb: float = 0.0,
                 duration_seconds: float = 0.0):
        self.success = success
        self.message = message
        self.backup_path = backup_path
        self.size_mb = size_mb
        self.duration_seconds = duration_seconds
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convierte el resultado a diccionario."""
        return {
            'success': self.success,
            'message': self.message,
            'backup_path': self.backup_path,
            'size_mb': self.size_mb,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat()
        }


class DatabaseBackupManager(QObject):
    """Gestor de backups para bases de datos."""

    # Señales para notificaciones
    backup_started = pyqtSignal(str)  # database_name
    backup_completed = pyqtSignal(str,
bool, str)  # database_name, success, message
    backup_error = pyqtSignal(str, str)  # database_name, error_message

    def __init__(self, config: BackupConfig):
        super().__init__()
        self.config = config
        self.backup_history = []
        self.setup_logging()
        self.ensure_backup_directory()

    def setup_logging(self):
        """Configura el sistema de logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('BackupManager')

    def ensure_backup_directory(self):
        """Asegura que el directorio de backups exista."""
        backup_path = Path(self.config.backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

    def get_database_connections(self) -> Dict[str, str]:
        """Obtiene las rutas de las bases de datos."""
        return {
            "users": "rexus/data/users.db",
            "inventario": "rexus/data/inventario.db",
            "auditoria": "rexus/data/auditoria.db"
        }

    def backup_single_database(self, db_name: str, db_path: str) -> BackupResult:
        """Realiza backup de una base de datos específica."""
        start_time = datetime.now()

        try:
            self.backup_started.emit(db_name)
            self.logger.info(f"Iniciando backup de {db_name}")

            # Verificar que la base de datos existe
            if not os.path.exists(db_path):
                error_msg = f"Base de datos no encontrada: {db_path}"
                self.logger.error(error_msg)
                return BackupResult(False, error_msg)

            # Crear nombre del archivo de backup
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{db_name}_backup_{timestamp}.db"
            backup_path = Path(self.config.backup_dir) / backup_filename

            # Realizar backup usando SQLite backup API (más seguro que copiar archivo)
            success = self._perform_sqlite_backup(db_path, str(backup_path))

            if not success:
                error_msg = f"Error en backup SQLite de {db_name}"
                return BackupResult(False, error_msg)

            # Comprimir si está habilitado
            final_path = str(backup_path)
            if self.config.compress_backups:
                compressed_path = str(backup_path).replace('.db', '.zip')
                success = self._compress_backup(str(backup_path), compressed_path)
                if success:
                    os.remove(str(backup_path))  # Eliminar archivo sin comprimir
                    final_path = compressed_path

            # Calcular tamaño y duración
            file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
            duration = (datetime.now() - start_time).total_seconds()

            # Crear resultado exitoso
            result = BackupResult(
                success=True,
                message=f"Backup de {db_name} completado exitosamente",
                backup_path=final_path,
                size_mb=file_size_mb,
                duration_seconds=duration
            )

            self.backup_history.append(result)
            self.backup_completed.emit(db_name, True, result.message)
            self.logger.info(f"Backup de {db_name} completado: {final_path} ({file_size_mb:.2f} MB)")

            return result

        except Exception as e:
            error_msg = f"Error en backup de {db_name}: {str(e)}"
            self.logger.error(error_msg)
            self.backup_error.emit(db_name, error_msg)

            duration = (datetime.now() - start_time).total_seconds()
            return BackupResult(False, error_msg, duration_seconds=duration)

    def _perform_sqlite_backup(self, source_path: str, backup_path: str) -> bool:
        """Realiza backup usando la API nativa de SQLite."""
        try:
            # Conectar a la base de datos fuente
            source_conn = sqlite3.connect(source_path)

            # Crear base de datos de backup
            backup_conn = sqlite3.connect(backup_path)

            # Realizar backup usando la función nativa
            source_conn.backup(backup_conn)

            # Cerrar conexiones
            backup_conn.close()
            source_conn.close()

            return True

        except Exception as e:
            self.logger.error(f"Error en backup SQLite: {e}")
            return False

    def _compress_backup(self, source_path: str, compressed_path: str) -> bool:
        """Comprime un archivo de backup."""
        try:
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(source_path, os.path.basename(source_path))
            return True
        except Exception as e:
            self.logger.error(f"Error comprimiendo backup: {e}")
            return False

    def backup_all_databases(self) -> List[BackupResult]:
        """Realiza backup de todas las bases de datos configuradas."""
        results = []
        db_connections = self.get_database_connections()

        self.logger.info("Iniciando backup completo del sistema")

        for db_name in self.config.backup_databases:
            if db_name in db_connections:
                db_path = db_connections[db_name]
                result = self.backup_single_database(db_name, db_path)
                results.append(result)
            else:
                error_msg = f"Base de datos no configurada: {db_name}"
                self.logger.error(error_msg)
                results.append(BackupResult(False, error_msg))

        # Ejecutar limpieza automática si está habilitada
        if self.config.auto_cleanup:
            self.cleanup_old_backups()

        self.logger.info("Backup completo del sistema finalizado")
        return results

    def cleanup_old_backups(self):
        """Elimina backups antiguos según la política de retención."""
        try:
            backup_dir = Path(self.config.backup_dir)
            if not backup_dir.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            deleted_count = 0

            for backup_file in backup_dir.glob("*_backup_*"):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Backup antiguo eliminado: {backup_file.name}")

            if deleted_count > 0:
                self.logger.info(f"Limpieza completada: {deleted_count} backups eliminados")

        except Exception as e:
            self.logger.error(f"Error en limpieza de backups: {e}")

    def restore_database(self, backup_path: str, target_db_path: str) -> bool:
        """Restaura una base de datos desde un backup."""
        try:
            self.logger.info(f"Iniciando restauración desde {backup_path}")

            # Verificar que el backup existe
            if not os.path.exists(backup_path):
                self.logger.error(f"Archivo de backup no encontrado: {backup_path}")
                return False

            # Si es un archivo comprimido, extraerlo primero
            temp_db_path = None
            if backup_path.endswith('.zip'):
                temp_db_path = backup_path.replace('.zip', '_temp.db')
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    # Extraer el primer archivo .db encontrado
                    for file_name in zip_file.namelist():
                        if file_name.endswith('.db'):
                            zip_file.extract(file_name, os.path.dirname(temp_db_path))
                            extracted_path = os.path.join(os.path.dirname(temp_db_path), file_name)
                            shutil.move(extracted_path, temp_db_path)
                            break
                source_path = temp_db_path
            else:
                source_path = backup_path

            # Hacer backup de la base de datos actual si existe
            if os.path.exists(target_db_path):
                backup_current = f"{target_db_path}.backup_before_restore"
                shutil.copy2(target_db_path, backup_current)
                self.logger.info(f"Backup de seguridad creado: {backup_current}")

            # Restaurar la base de datos
            shutil.copy2(source_path, target_db_path)

            # Limpiar archivo temporal si se creó
            if temp_db_path and os.path.exists(temp_db_path):
                os.remove(temp_db_path)

            self.logger.info(f"Base de datos restaurada exitosamente: {target_db_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error en restauración: {e}")
            return False

    def get_available_backups(self) -> List[Dict]:
        """Obtiene lista de backups disponibles."""
        backups = []
        backup_dir = Path(self.config.backup_dir)

        if not backup_dir.exists():
            return backups

        for backup_file in backup_dir.glob("*_backup_*"):
            if backup_file.is_file():
                try:
                    # Extraer información del nombre del archivo
                    parts = backup_file.stem.split('_backup_')
                    if len(parts) == 2:
                        db_name = parts[0]
                        timestamp_str = parts[1]

                        # Parsear timestamp
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                        # Información del archivo
                        file_size_mb = backup_file.stat().st_size / (1024 * 1024)

                        backups.append({
                            'database': db_name,
                            'timestamp': timestamp,
                            'file_path': str(backup_file),
                            'file_name': backup_file.name,
                            'size_mb': file_size_mb,
                            'compressed': backup_file.suffix == '.zip'
                        })
                except Exception as e:
                    self.logger.error(f"Error procesando backup {backup_file}: {e}")

        # Ordenar por timestamp descendente (más recientes primero)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups

    def get_backup_statistics(self) -> Dict:
        """Obtiene estadísticas del sistema de backups."""
        backups = self.get_available_backups()

        if not backups:
            return {
                'total_backups': 0,
                'total_size_mb': 0.0,
                'databases_backed_up': [],
                'oldest_backup': None,
                'newest_backup': None,
                'average_size_mb': 0.0
            }

        total_size = sum(b['size_mb'] for b in backups)
        databases = list(set(b['database'] for b in backups))

        return {
            'total_backups': len(backups),
            'total_size_mb': total_size,
            'databases_backed_up': databases,
            'oldest_backup': backups[-1]['timestamp'] if backups else None,
            'newest_backup': backups[0]['timestamp'] if backups else None,
            'average_size_mb': total_size / len(backups) if backups else 0.0
        }


class AutomatedBackupScheduler:
    """Programador automático de backups."""

    def __init__(self, backup_manager: DatabaseBackupManager, config: BackupConfig):
        self.backup_manager = backup_manager
        self.config = config
        self.scheduler_thread = None
        self.running = False
        self.setup_schedule()

    def setup_schedule(self):
        """Configura el horario de backups automáticos."""
        schedule.clear()  # Limpiar horarios previos

        if self.config.backup_schedule == "daily":
            schedule.every().day.at(self.config.backup_time).do(self._run_scheduled_backup)
        elif self.config.backup_schedule == "weekly":
            schedule.every().monday.at(self.config.backup_time).do(self._run_scheduled_backup)
        elif self.config.backup_schedule == "monthly":
            schedule.every().month.do(self._run_scheduled_backup)

    def _run_scheduled_backup(self):
        """Ejecuta backup programado."""
        try:
            logging.info("Ejecutando backup programado")
            results = self.backup_manager.backup_all_databases()

            # Log de resultados
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)

            if success_count == total_count:
                logging.info(f"Backup programado completado exitosamente: {success_count}/{total_count}")
            else:
                logging.warning(f"Backup programado completado con errores: {success_count}/{total_count}")

        except Exception as e:
            logging.error(f"Error en backup programado: {e}")

    def start_scheduler(self):
        """Inicia el programador de backups."""
        if self.running:
            return

        self.running = True

        def run_scheduler():
            while self.running:
                schedule.run_pending()
                threading.Event().wait(60)  # Verificar cada minuto

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logging.info("Programador de backups iniciado")

    def stop_scheduler(self):
        """Detiene el programador de backups."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logging.info("Programador de backups detenido")


# Funciones de utilidad para integración fácil

def create_backup_system(config_path: str = "config/backup_config.json") -> Tuple[DatabaseBackupManager, AutomatedBackupScheduler]:
    """
    Crea e inicializa el sistema completo de backups.

    Args:
        config_path: Ruta al archivo de configuración

    Returns:
        Tupla (backup_manager, scheduler)
    """
    # Cargar configuración
    config = BackupConfig.from_file(config_path)

    # Crear gestor de backups
    backup_manager = DatabaseBackupManager(config)

    # Crear programador
    scheduler = AutomatedBackupScheduler(backup_manager, config)

    return backup_manager, scheduler


def perform_immediate_backup() -> List[BackupResult]:
    """
    Realiza un backup inmediato de todas las bases de datos.

    Returns:
        Lista de resultados de backup
    """
    config = BackupConfig()
    backup_manager = DatabaseBackupManager(config)
    return backup_manager.backup_all_databases()


def get_backup_status() -> Dict:
    """
    Obtiene el estado actual del sistema de backups.

    Returns:
        Diccionario con estadísticas y estado
    """
    config = BackupConfig()
    backup_manager = DatabaseBackupManager(config)
    return backup_manager.get_backup_statistics()


# Ejemplo de uso
if __name__ == "__main__":
    # Crear sistema de backups
    backup_manager, scheduler = create_backup_system()

    # Realizar backup inmediato
    print("Realizando backup inmediato...")
    results = backup_manager.backup_all_databases()

    for result in results:
        if result.success:
            print(f"[CHECK] Backup exitoso: {result.backup_path} ({result.size_mb:.2f} MB)")
        else:
            print(f"[ERROR] Error en backup: {result.message}")

    # Mostrar estadísticas
    stats = backup_manager.get_backup_statistics()
    print(f"\nEstadísticas de backups:")
    print(f"Total de backups: {stats['total_backups']}")
    print(f"Tamaño total: {stats['total_size_mb']:.2f} MB")
    print(f"Bases de datos: {', '.join(stats['databases_backed_up'])}")

    # Iniciar programador automático
    print("\nIniciando programador automático...")
    scheduler.start_scheduler()
