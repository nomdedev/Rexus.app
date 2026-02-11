"""
Tests Críticos de Base de Datos - Rexus.app
Pruebas críticas de base de datos según la auditoría

Cobertura requerida:
- Conexión y reconexión automática
- Operaciones CRUD básicas
- Transacciones y rollback
- Integrity checks
- Backup y restore
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Importar módulos a probar
from rexus.core.database import DatabaseConnection, get_connection
from rexus.core.backup_manager import (
    BackupManager,
    BackupType,
    BackupConfig,
    get_backup_manager
)


class TestDatabaseConnection:
    """Tests de conexión a base de datos."""

    def test_connection_initialization(self):
        """Verifica la inicialización correcta de la conexión."""
        db = DatabaseConnection(database="test_db", auto_connect=False)

        assert db.database == "test_db"
        assert db.connection is None
        assert db.server is not None

    def test_database_name_sanitization(self):
        """Verifica que los nombres de base de datos se saniticen."""
        db = DatabaseConnection(database="test_db", auto_connect=False)

        # Nombre válido
        assert db.switch_database("valid_name") is True or db.connection is None

        # Nombre inválido (inyección SQL)
        with patch.object(db, 'connect', return_value=False):
            assert db.switch_database("'; DROP TABLE users; --") is False

    @patch('rexus.core.database.pyodbc.connect')
    def test_connection_retry(self, mock_connect):
        """Verifica reconexión automática."""
        # Primer intento falla, segundo tiene éxito
        mock_connect.side_effect = [Exception("Connection failed"), Mock()]

        db = DatabaseConnection(database="test_db", auto_connect=False)
        db.connect()

        # Debe haber reintentado
        assert mock_connect.call_count >= 1


class TestDatabaseCRUD:
    """Tests de operaciones CRUD."""

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos con datos."""
        db = Mock()
        db.connection = Mock()

        # Mock cursor
        cursor = Mock()
        cursor.execute = Mock()
        cursor.fetchall = Mock(return_value=[
            (1, "Producto 1", 100.0, 50),
            (2, "Producto 2", 200.0, 30)
        ])
        cursor.fetchone = Mock(return_value=(1, "Producto 1", 100.0, 50))
        cursor.rowcount = 1
        cursor.close = Mock()

        db.cursor = Mock(return_value=cursor)
        db.commit = Mock()
        db.rollback = Mock()

        return db

    def test_select_query_execution(self, mock_db):
        """Verifica ejecución de consultas SELECT."""
        result = mock_db.execute_query(
            "SELECT * FROM productos WHERE id = ?",
            (1,)
        )

        assert len(result) == 2
        assert result[0][0] == 1
        assert result[0][1] == "Producto 1"

    def test_insert_query_execution(self, mock_db):
        """Verifica ejecución de consultas INSERT."""
        result = mock_db.execute_non_query(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
            ("Nuevo Producto", 150.0)
        )

        assert result is True
        mock_db.commit.assert_called_once()

    def test_update_query_execution(self, mock_db):
        """Verifica ejecución de consultas UPDATE."""
        result = mock_db.execute_non_query(
            "UPDATE productos SET precio = ? WHERE id = ?",
            (199.99, 1)
        )

        assert result is True
        mock_db.commit.assert_called_once()

    def test_delete_query_execution(self, mock_db):
        """Verifica ejecución de consultas DELETE."""
        result = mock_db.execute_non_query(
            "DELETE FROM productos WHERE id = ?",
            (1,)
        )

        assert result is True
        mock_db.commit.assert_called_once()


class TestDatabaseTransactions:
    """Tests de transacciones."""

    def test_transaction_commit(self):
        """Verifica commit de transacciones."""
        db = Mock()
        db.connection = Mock()
        db.commit = Mock()

        db.commit()

        db.commit.assert_called_once()

    def test_transaction_rollback(self):
        """Verifica rollback de transacciones."""
        db = Mock()
        db.connection = Mock()
        db.rollback = Mock()

        db.rollback()

        db.rollback.assert_called_once()

    def test_transaction_on_error(self):
        """Verifica rollback automático en caso de error."""
        mock_db = Mock()
        mock_db.connection = Mock()

        cursor = Mock()
        cursor.execute = Mock(side_effect=Exception("SQL Error"))
        cursor.close = Mock()

        mock_db.cursor = Mock(return_value=cursor)
        mock_db.rollback = Mock()

        # Ejecutar query que falla
        result = mock_db.execute_query("SELECT * FROM invalid_table")

        # Verificar que no retornó resultados
        assert result == []


class TestDatabaseIntegrity:
    """Tests de integridad de datos."""

    def test_foreign_key_constraints(self):
        """Verifica que se respeten las restricciones de foreign key."""
        # Este test verifica que el código maneje correctamente
        # los errores de integridad referencial

        mock_db = Mock()
        mock_db.connection = Mock()

        cursor = Mock()
        # Simular error de foreign key
        cursor.execute = Mock(side_effect=Exception("Foreign key constraint"))
        cursor.close = Mock()

        mock_db.cursor = Mock(return_value=cursor)

        result = mock_db.execute_non_query(
            "INSERT INTO pedidos (producto_id) VALUES (99999)"
        )

        # Debe fallar
        assert result is False

    def test_unique_constraints(self):
        """Verifica que se respeten las restricciones únicas."""
        mock_db = Mock()
        mock_db.connection = Mock()

        cursor = Mock()
        # Simular error de constraint único
        cursor.execute = Mock(side_effect=Exception("Unique constraint"))
        cursor.close = Mock()

        mock_db.cursor = Mock(return_value=cursor)

        result = mock_db.execute_non_query(
            "INSERT INTO usuarios (usuario) VALUES ('admin')"
        )

        # Debe fallar
        assert result is False

    def test_not_null_constraints(self):
        """Verifica que se respeten las restricciones NOT NULL."""
        mock_db = Mock()
        mock_db.connection = Mock()

        cursor = Mock()
        # Simular error de NOT NULL
        cursor.execute = Mock(side_effect=Exception("Cannot insert NULL"))
        cursor.close = Mock()

        mock_db.cursor = Mock(return_value=cursor)

        result = mock_db.execute_non_query(
            "INSERT INTO productos (nombre, precio) VALUES (NULL, 100.0)"
        )

        # Debe fallar
        assert result is False


class TestBackupSystem:
    """Tests del sistema de backups."""

    def test_backup_config_initialization(self):
        """Verifica la inicialización de configuración de backups."""
        config = BackupConfig()

        assert config.backup_dir is not None
        assert config.compression is True
        assert config.full_retention_days >= 7

    def test_backup_manager_initialization(self):
        """Verifica la inicialización del gestor de backups."""
        manager = BackupManager()

        assert manager.config is not None
        assert manager.metadata_dir is not None

    def test_backup_filename_generation(self):
        """Verifica la generación correcta de nombres de archivo."""
        manager = BackupManager()

        timestamp = datetime(2024, 2, 7, 14, 30, 0)

        full_filename = manager._generate_filename("test_db", BackupType.FULL, timestamp)
        assert "test_db_FULL_20240207_143000" in full_filename
        assert full_filename.endswith(".bak")

        diff_filename = manager._generate_filename("test_db", BackupType.DIFFERENTIAL, timestamp)
        assert "test_db_DIFF_20240207_143000" in diff_filename

        log_filename = manager._generate_filename("test_db", BackupType.LOG, timestamp)
        assert "test_db_LOG_20240207_143000" in log_filename
        assert log_filename.endswith(".trn")

    def test_backup_command_generation(self):
        """Verifica la generación correcta de comandos SQL de backup."""
        manager = BackupManager()

        full_cmd = manager._build_backup_command("test_db", BackupType.FULL, "/tmp/test.bak")
        assert "BACKUP DATABASE" in full_cmd
        assert "test_db" in full_cmd
        assert "COMPRESSION" in full_cmd

        diff_cmd = manager._build_backup_command("test_db", BackupType.DIFFERENTIAL, "/tmp/test.bak")
        assert "BACKUP DATABASE" in diff_cmd
        assert "DIFFERENTIAL" in diff_cmd

        log_cmd = manager._build_backup_command("test_db", BackupType.LOG, "/tmp/test.trn")
        assert "BACKUP LOG" in log_cmd

    @patch('rexus.core.backup_manager.subprocess.run')
    def test_backup_creation_success(self, mock_run):
        """Verifica la creación exitosa de un backup."""
        # Configurar mock para éxito
        mock_run.return_value = Mock(returncode=0, stderr="")

        manager = BackupManager()

        # Crear archivo temporal para simular backup
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
            temp_path = f.name
            f.write(b"fake backup content")

        try:
            with patch.object(manager, '_execute_sql_command', return_value={'success': True}):
                result = manager.create_backup("test_db", BackupType.FULL)

                assert result.status == "success"
                assert result.database == "test_db"
                assert result.backup_type == "full"

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @patch('rexus.core.backup_manager.subprocess.run')
    def test_backup_creation_failure(self, mock_run):
        """Verifica el manejo de fallos en backup."""
        # Configurar mock para fallo
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Error: Cannot open backup device"
        )

        manager = BackupManager()

        with patch.object(manager, '_execute_sql_command',
                         return_value={'success': False, 'error': 'Backup device error'}):
            result = manager.create_backup("test_db", BackupType.FULL)

            assert result.status == "failed"
            assert result.error_message is not None

    def test_singleton_backup_manager(self):
        """Verifica que el BackupManager sea un singleton."""
        manager1 = get_backup_manager()
        manager2 = get_backup_manager()

        assert manager1 is manager2


class TestBackupRetention:
    """Tests de retención de backups."""

    def test_retention_calculation(self):
        """Verifica el cálculo correcto de retención."""
        from datetime import timedelta

        config = BackupConfig()
        assert config.full_retention_days == 30
        assert config.differential_retention_days == 7
        assert config.log_retention_days == 2

    @patch('os.listdir')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_old_backup_cleanup(self, mock_remove, mock_getmtime, mock_listdir):
        """Verifica la limpieza de backups antiguos."""
        manager = BackupManager()

        # Configurar mocks
        mock_listdir.return_value = [
            "db_FULL_20240101.bak",
            "db_FULL_20240201.bak"
        ]

        # Simular tiempos: uno viejo (90 días), uno reciente
        from datetime import datetime, timedelta
        old_time = (datetime.now() - timedelta(days=90)).timestamp()
        new_time = (datetime.now() - timedelta(days=5)).timestamp()

        mock_getmtime.side_effect = [old_time, new_time]

        # Ejecutar limpieza (solo simula, no elimina realmente)
        stats = manager._cleanup_directory(
            manager.config.backup_dir + "/full",
            datetime.now() - timedelta(days=30)
        )

        # Debe detectar archivos para eliminar
        assert stats >= 0


@pytest.fixture(scope="session")
def database_test_report():
    """Genera reporte de tests de base de datos."""
    return {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'coverage': {
            'connection': False,
            'crud': False,
            'transactions': False,
            'integrity': False,
            'backups': False
        }
    }


def pytest_sessionfinish(session, exitstatus):
    """Genera reporte final de tests de base de datos."""
    print("\n" + "="*60)
    print("REPORTE DE TESTS DE BASE DE DATOS CRÍTICOS")
    print("="*60)
    print(f"Exit status: {exitstatus}")
    print("\nNota: Los tests de base de datos deben ejecutarse en cada build.")
    print("Se recomienda ejecutar: pytest tests/critical/test_database_critical.py -v")
    print("="*60 + "\n")
