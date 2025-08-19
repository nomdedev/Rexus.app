"""
MIT License

Copyright (c) 2024 Rexus.app

Log Rotation Manager - Sistema de rotación y retención de logs
"""

import os
import gzip
import shutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
import logging
import logging.handlers


@dataclass
class LogConfig:
    """Configuración para un log específico."""
    name: str
    file_path: str
    max_size_mb: int = 10
    max_files: int = 5
    compress: bool = True
    retention_days: int = 30


class LogRotationManager:
    """Gestor de rotación y retención de logs del sistema."""

    def __init__(self, base_log_dir: str = None):
        """
        Inicializar gestor de rotación de logs.

        Args:
            base_log_dir: Directorio base para logs
        """
        self.base_log_dir = Path(base_log_dir or "logs")
        self.base_log_dir.mkdir(exist_ok=True)

        # Configuraciones de logs por defecto
        self.log_configs: Dict[str, LogConfig] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.rotation_thread: Optional[threading.Thread] = None
        self.stop_rotation = threading.Event()

        # Configurar logs del sistema
        self._setup_default_logs()

    def _setup_default_logs(self):
        """Configura los logs por defecto del sistema."""
        default_logs = [
            LogConfig(
                name="application",
                file_path=str(self.base_log_dir / "rexus.log"),
                max_size_mb=50,
                max_files=10,
                retention_days=90
            ),
            LogConfig(
                name="security",
                file_path=str(self.base_log_dir / "security.log"),
                max_size_mb=20,
                max_files=20,
                retention_days=180  # Logs de seguridad se mantienen más tiempo
            ),
            LogConfig(
                name="api",
                file_path=str(self.base_log_dir / "api.log"),
                max_size_mb=30,
                max_files=15,
                retention_days=60
            ),
            LogConfig(
                name="audit",
                file_path=str(self.base_log_dir / "audit.log"),
                max_size_mb=100,
                max_files=50,
                retention_days=365  # Logs de auditoría se mantienen un año
            ),
            LogConfig(
                name="database",
                file_path=str(self.base_log_dir / "database.log"),
                max_size_mb=25,
                max_files=12,
                retention_days=30
            ),
            LogConfig(
                name="backup",
                file_path=str(self.base_log_dir / "backup.log"),
                max_size_mb=15,
                max_files=8,
                retention_days=90
            )
        ]

        for config in default_logs:
            self.add_log_config(config)

    def add_log_config(self, config: LogConfig):
        """
        Añade configuración de log.

        Args:
            config: Configuración del log
        """
        self.log_configs[config.name] = config

        # Crear directorio si no existe
        log_path = Path(config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear handler rotativo
        handler = logging.handlers.RotatingFileHandler(
            filename=config.file_path,
            maxBytes=config.max_size_mb * 1024 * 1024,
            backupCount=config.max_files,
            encoding='utf-8'
        )

        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        self.handlers[config.name] = handler

        # Configurar permisos restrictivos del archivo
        self._set_secure_permissions(config.file_path)

    def _set_secure_permissions(self, file_path: str):
        """Establece permisos seguros para archivos de log."""
        try:
            # En Windows, establecer permisos básicos
            import stat
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # Solo lectura/escritura para el propietario
        except Exception as e:
            # Fallar silenciosamente si no se pueden establecer permisos
            pass

    def get_handler(self, log_name: str) -> Optional[logging.Handler]:
        """
        Obtiene handler para un log específico.

        Args:
            log_name: Nombre del log

        Returns:
            Handler del log o None si no existe
        """
        return self.handlers.get(log_name)

    def rotate_log(self, log_name: str) -> bool:
        """
        Rota un log específico manualmente.

        Args:
            log_name: Nombre del log a rotar

        Returns:
            True si la rotación fue exitosa
        """
        if log_name not in self.handlers:
            return False

        try:
            handler = self.handlers[log_name]
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.doRollover()

                # Comprimir archivos rotados si está habilitado
                config = self.log_configs[log_name]
                if config.compress:
                    self._compress_rotated_files(log_name)

                return True
        except Exception as e:
            print(f"Error rotando log {log_name}: {e}")

        return False

    def _compress_rotated_files(self, log_name: str):
        """Comprime archivos de log rotados."""
        config = self.log_configs[log_name]
        log_path = Path(config.file_path)
        log_dir = log_path.parent
        base_name = log_path.stem
        extension = log_path.suffix

        # Buscar archivos rotados (.log.1, .log.2, etc.)
        for i in range(1, config.max_files + 1):
            rotated_file = log_dir / f"{base_name}{extension}.{i}"
            compressed_file = log_dir / f"{base_name}{extension}.{i}.gz"

            if rotated_file.exists() and not compressed_file.exists():
                try:
                    with open(rotated_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Eliminar archivo original
                    rotated_file.unlink()

                    # Establecer permisos seguros
                    self._set_secure_permissions(str(compressed_file))

                except Exception as e:
                    print(f"Error comprimiendo {rotated_file}: {e}")

    def cleanup_old_logs(self):
        """Limpia logs antiguos según la política de retención."""
        current_time = datetime.now()

        for log_name, config in self.log_configs.items():
            try:
                log_path = Path(config.file_path)
                log_dir = log_path.parent
                base_name = log_path.stem
                extension = log_path.suffix

                # Buscar todos los archivos relacionados con este log
                pattern = f"{base_name}{extension}*"
                old_files = []

                for file_path in log_dir.glob(pattern):
                    if file_path == log_path:
                        continue  # No eliminar el archivo actual

                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_age.days > config.retention_days:
                        old_files.append(file_path)

                # Eliminar archivos antiguos
                for old_file in old_files:
                    try:
                        old_file.unlink()
                        print(f"Log antiguo eliminado: {old_file}")
                    except Exception as e:
                        print(f"Error eliminando {old_file}: {e}")

            except Exception as e:
                print(f"Error limpiando logs para {log_name}: {e}")

    def get_log_stats(self) -> Dict[str, Dict]:
        """
        Obtiene estadísticas de los logs.

        Returns:
            Diccionario con estadísticas de cada log
        """
        stats = {}

        for log_name, config in self.log_configs.items():
            try:
                log_path = Path(config.file_path)

                if log_path.exists():
                    stat = log_path.stat()
                    size_mb = stat.st_size / (1024 * 1024)

                    # Contar archivos rotados
                    log_dir = log_path.parent
                    base_name = log_path.stem
                    extension = log_path.suffix

                    rotated_files = len(list(log_dir.glob(f"{base_name}{extension}.*")))

                    stats[log_name] = {
                        'size_mb': round(size_mb, 2),
                        'max_size_mb': config.max_size_mb,
                        'usage_percent': round((size_mb / config.max_size_mb) * 100, 1),
                        'rotated_files': rotated_files,
                        'max_files': config.max_files,
                        'retention_days': config.retention_days,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'needs_rotation': size_mb >= config.max_size_mb * 0.9  # 90% del tamaño máximo
                    }
                else:
                    stats[log_name] = {
                        'size_mb': 0,
                        'max_size_mb': config.max_size_mb,
                        'usage_percent': 0,
                        'rotated_files': 0,
                        'max_files': config.max_files,
                        'retention_days': config.retention_days,
                        'last_modified': None,
                        'needs_rotation': False
                    }

            except Exception as e:
                stats[log_name] = {'error': str(e)}

        return stats

    def start_automatic_rotation(self, check_interval_minutes: int = 60):
        """
        Inicia rotación automática de logs.

        Args:
            check_interval_minutes: Intervalo de verificación en minutos
        """
        if self.rotation_thread and self.rotation_thread.is_alive():
            return  # Ya está ejecutándose

        def rotation_worker():
            while not self.stop_rotation.wait(check_interval_minutes * 60):
                try:
                    # Verificar si algún log necesita rotación
                    stats = self.get_log_stats()

                    for log_name, log_stat in stats.items():
                        if log_stat.get('needs_rotation', False):
                            self.rotate_log(log_name)

                    # Limpiar logs antiguos
                    self.cleanup_old_logs()

                except Exception as e:
                    print(f"Error en rotación automática: {e}")

        self.stop_rotation.clear()
        self.rotation_thread = threading.Thread(target=rotation_worker, daemon=True)
        self.rotation_thread.start()

    def stop_automatic_rotation(self):
        """Detiene la rotación automática de logs."""
        if self.rotation_thread:
            self.stop_rotation.set()
            self.rotation_thread.join(timeout=5)

    def force_rotate_all(self):
        """Fuerza la rotación de todos los logs."""
        rotated_count = 0

        for log_name in self.log_configs:
            if self.rotate_log(log_name):
                rotated_count += 1

        # Limpiar logs antiguos
        self.cleanup_old_logs()

        return rotated_count

    def archive_logs(self, archive_path: str = None) -> str:
        """
        Archiva todos los logs actuales.

        Args:
            archive_path: Ruta del archivo de archivo (opcional)

        Returns:
            Ruta del archivo creado
        """
        if not archive_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = str(self.base_log_dir / f"logs_archive_{timestamp}.tar.gz")

        import tarfile

        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                for log_name, config in self.log_configs.items():
                    log_path = Path(config.file_path)

                    if log_path.exists():
                        tar.add(log_path, arcname=f"{log_name}.log")

                    # Añadir archivos rotados
                    log_dir = log_path.parent
                    base_name = log_path.stem
                    extension = log_path.suffix

                    for rotated_file in log_dir.glob(f"{base_name}{extension}.*"):
                        tar.add(rotated_file, arcname=rotated_file.name)

            return archive_path

        except Exception as e:
            raise Exception(f"Error archivando logs: {e}")


# Instancia global del gestor de logs
log_rotation_manager: Optional[LogRotationManager] = None


def init_log_rotation_manager(base_log_dir: str = None):
    """
    Inicializa el gestor de rotación de logs.

    Args:
        base_log_dir: Directorio base para logs
    """
    global log_rotation_manager
    log_rotation_manager = LogRotationManager(base_log_dir)


def get_log_rotation_manager() -> LogRotationManager:
    """
    Obtiene la instancia del gestor de rotación de logs.

    Returns:
        Instancia de LogRotationManager
    """
    if log_rotation_manager is None:
        init_log_rotation_manager()

    return log_rotation_manager


def get_log_handler(log_name: str) -> Optional[logging.Handler]:
    """
    Función de conveniencia para obtener handler de log.

    Args:
        log_name: Nombre del log

    Returns:
        Handler del log
    """
    return get_log_rotation_manager().get_handler(log_name)


def rotate_log(log_name: str) -> bool:
    """
    Función de conveniencia para rotar log.

    Args:
        log_name: Nombre del log

    Returns:
        True si la rotación fue exitosa
    """
    return get_log_rotation_manager().rotate_log(log_name)


def get_log_stats() -> Dict[str, Dict]:
    """
    Función de conveniencia para obtener estadísticas de logs.

    Returns:
        Estadísticas de logs
    """
    return get_log_rotation_manager().get_log_stats()


def start_automatic_rotation(check_interval_minutes: int = 60):
    """
    Función de conveniencia para iniciar rotación automática.

    Args:
        check_interval_minutes: Intervalo de verificación
    """
    get_log_rotation_manager().start_automatic_rotation(check_interval_minutes)
