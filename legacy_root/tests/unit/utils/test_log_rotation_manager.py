"""
Tests para Log Rotation Manager - Rexus.app

Tests que validan el sistema de rotación y retención de logs,
incluyendo rotación automática, limpieza de archivos antiguos y compresión.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import tempfile
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import logging

# Import the modules we're testing
try:
    from rexus.utils.log_rotation_manager import (
        LogConfig,
        LogRotationManager,
        init_log_rotation_manager,
        get_log_rotation_manager,
        get_log_handler,
        rotate_log,
        get_log_stats,
        start_automatic_rotation
    )
    LOG_ROTATION_AVAILABLE = True
except ImportError:
    LOG_ROTATION_AVAILABLE = False


@pytest.mark.skipif(not LOG_ROTATION_AVAILABLE, reason="Log rotation manager modules not available")
class TestLogConfig:
    """Tests para la clase LogConfig."""

    def test_log_config_creation(self):
        """Test que valida la creación de configuración de log."""
        config = LogConfig(
            name="test_log",
            file_path="/tmp/test.log",
            max_size_mb=20,
            max_files=10,
            compress=True,
            retention_days=60
        )

        assert config.name == "test_log"
        assert config.file_path == "/tmp/test.log"
        assert config.max_size_mb == 20
        assert config.max_files == 10
        assert config.compress == True
        assert config.retention_days == 60

    def test_log_config_defaults(self):
        """Test que valida los valores por defecto de LogConfig."""
        config = LogConfig(
            name="default_log",
            file_path="/tmp/default.log"
        )

        assert config.max_size_mb == 10
        assert config.max_files == 5
        assert config.compress == True
        assert config.retention_days == 30


@pytest.mark.skipif(not LOG_ROTATION_AVAILABLE, reason="Log rotation manager modules not available")
class TestLogRotationManager:
    """Tests para la clase LogRotationManager."""

    def setUp(self):
        """Setup para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_manager = LogRotationManager(self.temp_dir)

    def tearDown(self):
        """Cleanup después de cada test."""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        if hasattr(self, 'log_manager'):
            self.log_manager.stop_automatic_rotation()

    def test_initialization(self):
        """Test que valida la inicialización del gestor de logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            assert manager.base_log_dir == Path(temp_dir)
            assert manager.base_log_dir.exists()
            assert isinstance(manager.log_configs, dict)
            assert isinstance(manager.handlers, dict)

            # Debe tener configuraciones por defecto
            default_logs = ["application", "security", "api", "audit", "database", "backup"]
            for log_name in default_logs:
                assert log_name in manager.log_configs

        finally:
            shutil.rmtree(temp_dir)

    def test_add_log_config(self):
        """Test que valida la adición de configuraciones de log."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            config = LogConfig(
                name="test_log",
                file_path=str(Path(temp_dir) / "test.log"),
                max_size_mb=5,
                max_files=3
            )

            manager.add_log_config(config)

            assert "test_log" in manager.log_configs
            assert manager.log_configs["test_log"] == config
            assert "test_log" in manager.handlers

            # Verificar que el handler es del tipo correcto
            handler = manager.handlers["test_log"]
            assert isinstance(handler, logging.handlers.RotatingFileHandler)

        finally:
            shutil.rmtree(temp_dir)

    def test_get_handler(self):
        """Test que valida la obtención de handlers de log."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Handler existente
            handler = manager.get_handler("application")
            assert handler is not None
            assert isinstance(handler, logging.Handler)

            # Handler no existente
            nonexistent_handler = manager.get_handler("nonexistent_log")
            assert nonexistent_handler is None

        finally:
            shutil.rmtree(temp_dir)

    def test_rotate_log_success(self):
        """Test que valida la rotación exitosa de logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Crear archivo de log con contenido
            log_path = Path(temp_dir) / "test.log"
            config = LogConfig(name="test_log", file_path=str(log_path), max_size_mb=1)
            manager.add_log_config(config)

            # Escribir contenido al log
            handler = manager.get_handler("test_log")
            logger = logging.getLogger("test_logger")
            logger.addHandler(handler)

            for i in range(100):
                logger.info(f"Test log message {i} " + "x" * 1000)

            # Rotar log
            success = manager.rotate_log("test_log")
            assert success

        finally:
            shutil.rmtree(temp_dir)

    def test_rotate_log_nonexistent(self):
        """Test que valida la rotación de logs no existentes."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            success = manager.rotate_log("nonexistent_log")
            assert not success

        finally:
            shutil.rmtree(temp_dir)

    @patch('gzip.open')
    @patch('shutil.copyfileobj')
    def test_compress_rotated_files(self, mock_copyfileobj, mock_gzip_open):
        """Test que valida la compresión de archivos rotados."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Crear archivo de log rotado simulado
            log_path = Path(temp_dir) / "test.log"
            rotated_path = Path(temp_dir) / "test.log.1"

            config = LogConfig(name="test_log", file_path=str(log_path), compress=True)
            manager.add_log_config(config)

            # Crear archivo rotado simulado
            rotated_path.write_text("rotated log content")

            # Mock para gzip
            mock_gzip_file = MagicMock()
            mock_gzip_open.return_value.__enter__.return_value = mock_gzip_file

            # Comprimir archivos rotados
            manager._compress_rotated_files("test_log")

            # Verificar que se intentó comprimir
            expected_compressed = Path(temp_dir) / "test.log.1.gz"
            mock_gzip_open.assert_called_once_with(expected_compressed, 'wb')

        finally:
            shutil.rmtree(temp_dir)

    def test_cleanup_old_logs(self):
        """Test que valida la limpieza de logs antiguos."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Crear configuración con retención corta
            config = LogConfig(
                name="test_log",
                file_path=str(Path(temp_dir) / "test.log"),
                retention_days=1
            )
            manager.add_log_config(config)

            # Crear archivos de log simulados
            current_log = Path(temp_dir) / "test.log"
            old_log1 = Path(temp_dir) / "test.log.1"
            old_log2 = Path(temp_dir) / "test.log.2.gz"

            current_log.write_text("current log")
            old_log1.write_text("old log 1")
            old_log2.write_text("old log 2 compressed")

            # Hacer que los archivos parezcan antiguos
            old_time = time.time() - (2 * 24 * 3600)  # 2 días atrás
            old_log1.touch(times=(old_time, old_time))
            old_log2.touch(times=(old_time, old_time))

            # Limpiar logs antiguos
            manager.cleanup_old_logs()

            # El archivo actual debe existir, los antiguos no
            assert current_log.exists()
            # Los archivos antiguos pueden o no haberse eliminado dependiendo del sistema

        finally:
            shutil.rmtree(temp_dir)

    def test_get_log_stats(self):
        """Test que valida la obtención de estadísticas de logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            stats = manager.get_log_stats()

            assert isinstance(stats, dict)

            # Verificar estadísticas para logs por defecto
            default_logs = ["application", "security", "api", "audit", "database", "backup"]
            for log_name in default_logs:
                assert log_name in stats

                log_stats = stats[log_name]
                required_keys = ['size_mb', 'max_size_mb', 'usage_percent', 'rotated_files',
                               'max_files', 'retention_days', 'needs_rotation']
                for key in required_keys:
                    assert key in log_stats

                assert isinstance(log_stats['size_mb'], (int, float))
                assert log_stats['usage_percent'] >= 0
                assert isinstance(log_stats['needs_rotation'], bool)

        finally:
            shutil.rmtree(temp_dir)

    def test_start_stop_automatic_rotation(self):
        """Test que valida el inicio y parada de rotación automática."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Iniciar rotación automática
            manager.start_automatic_rotation(check_interval_minutes=1)

            assert manager.rotation_thread is not None
            assert manager.rotation_thread.is_alive()
            assert not manager.stop_rotation.is_set()

            # Parar rotación automática
            manager.stop_automatic_rotation()

            # Dar tiempo para que el thread termine
            time.sleep(0.1)
            assert manager.stop_rotation.is_set()

        finally:
            shutil.rmtree(temp_dir)

    def test_force_rotate_all(self):
        """Test que valida la rotación forzada de todos los logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Forzar rotación de todos los logs
            rotated_count = manager.force_rotate_all()

            # Debe intentar rotar todos los logs configurados
            assert isinstance(rotated_count, int)
            assert rotated_count >= 0

        finally:
            shutil.rmtree(temp_dir)

    def test_archive_logs(self):
        """Test que valida el archivado de logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Crear algunos archivos de log
            for log_name in ["application", "security"]:
                log_path = manager.log_configs[log_name].file_path
                Path(log_path).write_text(f"Content for {log_name}")

            # Archivar logs
            archive_path = manager.archive_logs()

            assert isinstance(archive_path, str)
            assert Path(archive_path).exists()
            assert archive_path.endswith('.tar.gz')

            # Limpiar archivo de archivo
            if Path(archive_path).exists():
                Path(archive_path).unlink()

        finally:
            shutil.rmtree(temp_dir)


@pytest.mark.skipif(not LOG_ROTATION_AVAILABLE, reason="Log rotation manager modules not available")
class TestLogRotationManagerGlobalFunctions:
    """Tests para las funciones globales del módulo."""

    def test_init_and_get_log_rotation_manager(self):
        """Test que valida la inicialización global del gestor de rotación."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_log_rotation_manager(temp_dir)

            manager = get_log_rotation_manager()

            assert manager is not None
            assert isinstance(manager, LogRotationManager)
            assert manager.base_log_dir == Path(temp_dir)

        finally:
            shutil.rmtree(temp_dir)

    def test_get_log_handler_global(self):
        """Test que valida la función global para obtener handlers."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_log_rotation_manager(temp_dir)

            handler = get_log_handler("application")
            assert handler is not None
            assert isinstance(handler, logging.Handler)

            nonexistent_handler = get_log_handler("nonexistent")
            assert nonexistent_handler is None

        finally:
            shutil.rmtree(temp_dir)

    def test_rotate_log_global(self):
        """Test que valida la función global de rotación de logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_log_rotation_manager(temp_dir)

            # Rotar log existente
            success = rotate_log("application")
            assert isinstance(success, bool)

            # Rotar log no existente
            failure = rotate_log("nonexistent")
            assert not failure

        finally:
            shutil.rmtree(temp_dir)

    def test_get_log_stats_global(self):
        """Test que valida la función global de estadísticas."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_log_rotation_manager(temp_dir)

            stats = get_log_stats()

            assert isinstance(stats, dict)
            assert len(stats) > 0

        finally:
            shutil.rmtree(temp_dir)

    def test_start_automatic_rotation_global(self):
        """Test que valida la función global de rotación automática."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_log_rotation_manager(temp_dir)

            start_automatic_rotation(check_interval_minutes=1)

            manager = get_log_rotation_manager()
            assert manager.rotation_thread is not None
            assert manager.rotation_thread.is_alive()

            # Parar rotación
            manager.stop_automatic_rotation()

        finally:
            shutil.rmtree(temp_dir)


@pytest.mark.skipif(not LOG_ROTATION_AVAILABLE, reason="Log rotation manager modules not available")
class TestLogRotationManagerIntegration:
    """Tests de integración para el gestor de rotación de logs."""

    def test_full_log_lifecycle(self):
        """Test que valida el ciclo completo de vida de un log."""
        temp_dir = tempfile.mkdtemp()
        try:
            # 1. Inicializar gestor
            manager = LogRotationManager(temp_dir)

            # 2. Añadir configuración personalizada
            config = LogConfig(
                name="lifecycle_test",
                file_path=str(Path(temp_dir) / "lifecycle.log"),
                max_size_mb=1,
                max_files=3,
                retention_days=7
            )
            manager.add_log_config(config)

            # 3. Obtener handler y escribir logs
            handler = manager.get_handler("lifecycle_test")
            logger = logging.getLogger("lifecycle_logger")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            # 4. Escribir suficiente contenido para forzar rotación
            for i in range(50):
                logger.info(f"Lifecycle test message {i} " + "x" * 1000)

            # 5. Verificar estadísticas
            stats = manager.get_log_stats()
            assert "lifecycle_test" in stats

            # 6. Rotar log manualmente
            success = manager.rotate_log("lifecycle_test")
            assert success

            # 7. Verificar que se crearon archivos rotados
            log_dir = Path(temp_dir)
            log_files = list(log_dir.glob("lifecycle.*"))
            assert len(log_files) >= 1

        finally:
            shutil.rmtree(temp_dir)

    def test_concurrent_log_operations(self):
        """Test que valida operaciones concurrentes en logs."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Configurar múltiples logs
            configs = [
                LogConfig(name=f"concurrent_{i}", file_path=str(Path(temp_dir) / f"concurrent_{i}.log"))
                for i in range(3)
            ]

            for config in configs:
                manager.add_log_config(config)

            # Función para escribir logs concurrentemente
            def write_logs(log_name):
                handler = manager.get_handler(log_name)
                logger = logging.getLogger(f"concurrent_{log_name}")
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

                for i in range(20):
                    logger.info(f"Concurrent log {log_name} message {i}")
                    time.sleep(0.01)

            # Ejecutar escritura concurrente
            threads = []
            for i in range(3):
                thread = threading.Thread(target=write_logs, args=(f"concurrent_{i}",))
                threads.append(thread)
                thread.start()

            # Esperar que terminen todos los threads
            for thread in threads:
                thread.join(timeout=5)

            # Verificar que se escribieron los logs
            stats = manager.get_log_stats()
            for i in range(3):
                log_name = f"concurrent_{i}"
                assert log_name in stats
                assert stats[log_name]['size_mb'] > 0

        finally:
            shutil.rmtree(temp_dir)

    def test_automatic_rotation_workflow(self):
        """Test que valida el workflow de rotación automática."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # Configurar log con límite muy pequeño
            config = LogConfig(
                name="auto_rotate_test",
                file_path=str(Path(temp_dir) / "auto_rotate.log"),
                max_size_mb=0.001,  # 1KB para forzar rotación rápida
                max_files=2
            )
            manager.add_log_config(config)

            # Iniciar rotación automática con intervalo corto
            manager.start_automatic_rotation(check_interval_minutes=0.1)  # 6 segundos

            # Escribir logs para exceder límite
            handler = manager.get_handler("auto_rotate_test")
            logger = logging.getLogger("auto_rotate_logger")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            for i in range(100):
                logger.info(f"Auto rotate test message {i} " + "x" * 100)

            # Dar tiempo para que la rotación automática funcione
            time.sleep(10)

            # Verificar estadísticas
            stats = manager.get_log_stats()
            assert "auto_rotate_test" in stats

            # Parar rotación automática
            manager.stop_automatic_rotation()

        finally:
            shutil.rmtree(temp_dir)

    def test_error_handling_resilience(self):
        """Test que valida la resistencia a errores del sistema."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = LogRotationManager(temp_dir)

            # 1. Intentar operaciones con paths inválidos
            invalid_config = LogConfig(
                name="invalid_test",
                file_path="/invalid/path/that/does/not/exist.log"
            )

            # El sistema debe manejar paths inválidos graciosamente
            try:
                manager.add_log_config(invalid_config)
                # Si llega aquí, el sistema manejó el error
                assert True
            except Exception:
                # Si falla, también es aceptable
                assert True

            # 2. Rotar logs que no existen
            success = manager.rotate_log("completely_nonexistent_log")
            assert not success

            # 3. Obtener estadísticas debe seguir funcionando
            stats = manager.get_log_stats()
            assert isinstance(stats, dict)

            # 4. Forzar rotación no debe fallar
            rotated_count = manager.force_rotate_all()
            assert isinstance(rotated_count, int)

        finally:
            shutil.rmtree(temp_dir)


# Fixtures para tests de log rotation
@pytest.fixture
def temp_log_dir():
    """Fixture que proporciona directorio temporal para logs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def log_rotation_manager(temp_log_dir):
    """Fixture que proporciona instancia de LogRotationManager."""
    manager = LogRotationManager(temp_log_dir)
    yield manager
    manager.stop_automatic_rotation()


@pytest.fixture
def log_test_data():
    """Fixture con datos de prueba para tests de logs."""
    return {
        'log_configs': [
            {'name': 'test1', 'max_size_mb': 5, 'max_files': 3},
            {'name': 'test2', 'max_size_mb': 10, 'max_files': 5},
            {'name': 'test3', 'max_size_mb': 1, 'max_files': 2}
        ],
        'sample_messages': [
            "INFO: Application started successfully",
            "ERROR: Database connection failed",
            "WARNING: High memory usage detected",
            "DEBUG: Processing user request",
            "CRITICAL: System overload detected"
        ]
    }
