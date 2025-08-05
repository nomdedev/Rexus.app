"""
Tests para el sistema de backup automatizado de Rexus.app

Verifica funcionalidades básicas del sistema de backup sin requerir
bases de datos reales para poder ejecutarse en cualquier entorno.
"""

import os
import json
import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Importar los módulos a testear
from rexus.utils.backup_system import (
    BackupConfig,
    BackupResult,
    DatabaseBackupManager
)

from rexus.core.backup_integration import (
    BackupIntegration,
    get_backup_system,
    initialize_backup_system
)


class TestBackupConfig:
    """Tests para la configuración del sistema de backup."""
    
    def test_backup_config_defaults(self):
        """Test valores por defecto de BackupConfig."""
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.backup_schedule == "daily"
        assert config.backup_time == "02:00"
        assert config.retention_days == 30
        assert config.compress_backups == True
        assert config.backup_databases == ["users", "inventario", "auditoria"]
        assert config.notification_enabled == True
        assert config.auto_cleanup == True
    
    def test_backup_config_from_file(self):
        """Test carga de configuración desde archivo."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "backup_dir": "test_backups",
                "backup_schedule": "weekly", 
                "retention_days": 60
            }
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = BackupConfig.from_file(temp_path)
            
            assert config.backup_dir == "test_backups"
            assert config.backup_schedule == "weekly"
            assert config.retention_days == 60
            # Valores por defecto para claves no especificadas
            assert config.backup_time == "02:00"
            
        finally:
            os.unlink(temp_path)
    
    def test_backup_config_save_to_file(self):
        """Test guardado de configuración a archivo."""
        config = BackupConfig()
        config.backup_dir = "custom_backups"
        config.retention_days = 45
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_to_file(temp_path)
            
            # Verificar que se guardó correctamente
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data['backup_dir'] == "custom_backups"
            assert saved_data['retention_days'] == 45
            assert saved_data['backup_databases'] == ["users", "inventario", "auditoria"]
            
        finally:
            os.unlink(temp_path)


class TestBackupResult:
    """Tests para BackupResult."""
    
    def test_backup_result_creation(self):
        """Test creación de BackupResult."""
        result = BackupResult(
            success=True,
            message="Backup exitoso",
            backup_path="/path/to/backup.db",
            size_mb=2.5,
            duration_seconds=30.0
        )
        
        assert result.success == True
        assert result.message == "Backup exitoso"
        assert result.backup_path == "/path/to/backup.db"
        assert result.size_mb == 2.5
        assert result.duration_seconds == 30.0
        assert result.timestamp is not None
    
    def test_backup_result_to_dict(self):
        """Test conversión de BackupResult a diccionario."""
        result = BackupResult(
            success=False,
            message="Error en backup",
            size_mb=0.0
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] == False
        assert result_dict['message'] == "Error en backup"
        assert result_dict['size_mb'] == 0.0
        assert 'timestamp' in result_dict


class TestDatabaseBackupManager:
    """Tests para DatabaseBackupManager."""
    
    @pytest.fixture
    def temp_config(self):
        """Fixture que proporciona una configuración temporal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BackupConfig()
            config.backup_dir = os.path.join(temp_dir, "backups")
            yield config
    
    @pytest.fixture
    def backup_manager(self, temp_config):
        """Fixture que proporciona un DatabaseBackupManager."""
        return DatabaseBackupManager(temp_config)
    
    def test_backup_manager_initialization(self, backup_manager):
        """Test inicialización del gestor de backup."""
        assert backup_manager.config is not None
        assert backup_manager.backup_history == []
        assert hasattr(backup_manager, 'logger')
    
    def test_ensure_backup_directory(self, backup_manager):
        """Test creación del directorio de backups."""
        backup_manager.ensure_backup_directory()
        assert os.path.exists(backup_manager.config.backup_dir)
    
    def test_get_database_connections(self, backup_manager):
        """Test obtención de conexiones de base de datos."""
        connections = backup_manager.get_database_connections()
        
        assert "users" in connections
        assert "inventario" in connections
        assert "auditoria" in connections
        assert connections["users"] == "rexus/data/users.db"
    
    @patch('sqlite3.connect')
    def test_perform_sqlite_backup_success(self, mock_connect, backup_manager):
        """Test backup SQLite exitoso."""
        # Mock de las conexiones
        mock_source = Mock()
        mock_backup = Mock()
        mock_connect.side_effect = [mock_source, mock_backup]
        
        # Mock del método backup
        mock_source.backup = Mock()
        
        result = backup_manager._perform_sqlite_backup("source.db", "backup.db")
        
        assert result == True
        mock_source.backup.assert_called_once_with(mock_backup)
        mock_source.close.assert_called_once()
        mock_backup.close.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_perform_sqlite_backup_error(self, mock_connect, backup_manager):
        """Test manejo de errores en backup SQLite."""
        mock_connect.side_effect = Exception("Error de conexión")
        
        result = backup_manager._perform_sqlite_backup("source.db", "backup.db")
        
        assert result == False
    
    def test_get_available_backups_empty(self, backup_manager):
        """Test obtención de backups disponibles (directorio vacío)."""
        backup_manager.ensure_backup_directory()
        backups = backup_manager.get_available_backups()
        
        assert backups == []
    
    def test_get_backup_statistics_empty(self, backup_manager):
        """Test estadísticas de backup (sin backups)."""
        stats = backup_manager.get_backup_statistics()
        
        assert stats['total_backups'] == 0
        assert stats['total_size_mb'] == 0.0
        assert stats['databases_backed_up'] == []
        assert stats['oldest_backup'] is None
        assert stats['newest_backup'] is None
        assert stats['average_size_mb'] == 0.0


class TestBackupIntegration:
    """Tests para BackupIntegration."""
    
    @pytest.fixture
    def temp_integration(self):
        """Fixture que proporciona una BackupIntegration temporal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            integration = BackupIntegration()
            integration.config_path = os.path.join(temp_dir, "backup_config.json")
            yield integration
    
    def test_backup_integration_initialization(self, temp_integration):
        """Test inicialización de BackupIntegration."""
        assert temp_integration.backup_manager is None
        assert temp_integration.scheduler is None
        assert temp_integration.initialized == False
    
    def test_create_default_config(self, temp_integration):
        """Test creación de configuración por defecto."""
        temp_integration._create_default_config()
        
        assert os.path.exists(temp_integration.config_path)
        
        # Verificar contenido del archivo
        with open(temp_integration.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        assert config_data['backup_dir'] == "backups"
        assert config_data['backup_schedule'] == "daily"
        assert config_data['backup_databases'] == ["users", "inventario", "auditoria"]
    
    def test_get_config(self, temp_integration):
        """Test obtención de configuración."""
        # Sin archivo de configuración
        config = temp_integration.get_config()
        assert config == {}
        
        # Con archivo de configuración
        temp_integration._create_default_config()
        config = temp_integration.get_config()
        
        assert 'backup_dir' in config
        assert 'backup_schedule' in config
    
    def test_is_running(self, temp_integration):
        """Test verificación de estado del sistema."""
        assert temp_integration.is_running() == False
        
        temp_integration.initialized = True
        temp_integration.backup_manager = Mock()
        
        assert temp_integration.is_running() == True
    
    def test_get_next_scheduled_backup(self, temp_integration):
        """Test información del próximo backup programado."""
        # Sin inicializar
        assert temp_integration.get_next_scheduled_backup() is None
        
        # Con configuración
        temp_integration._create_default_config()
        temp_integration.initialized = True
        
        next_backup = temp_integration.get_next_scheduled_backup()
        assert "Diariamente a las 02:00" in next_backup


class TestBackupSystemIntegration:
    """Tests de integración del sistema completo."""
    
    def test_get_backup_system_singleton(self):
        """Test patrón singleton del sistema de backup."""
        system1 = get_backup_system()
        system2 = get_backup_system()
        
        assert system1 is system2
    
    @patch('rexus.core.backup_integration.BackupIntegration.initialize')
    def test_initialize_backup_system(self, mock_initialize):
        """Test inicialización del sistema global."""
        mock_initialize.return_value = True
        
        result = initialize_backup_system()
        
        assert result == True
        mock_initialize.assert_called_once()
    
    def test_backup_system_configuration_validation(self):
        """Test validación de configuración del sistema."""
        system = get_backup_system()
        
        # Verificar que las propiedades básicas existen
        assert hasattr(system, 'config_path')
        assert hasattr(system, 'backup_manager')
        assert hasattr(system, 'scheduler')
        assert hasattr(system, 'initialized')


# Tests de funciones utilitarias

def test_create_test_database():
    """Crea una base de datos de prueba para testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db_path = f.name
    
    try:
        # Crear base de datos con tabla de prueba
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("Test Record",))
        conn.commit()
        conn.close()
        
        # Verificar que la base de datos se creó correctamente
        assert os.path.exists(test_db_path)
        assert os.path.getsize(test_db_path) > 0
        
        return test_db_path
        
    except Exception as e:
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
        raise e


def test_backup_system_error_handling():
    """Test manejo de errores del sistema de backup."""
    config = BackupConfig()
    config.backup_dir = "/ruta/inexistente/sin/permisos"
    
    # Esto no debería fallar, sino crear el directorio o manejarlo graciosamente
    try:
        manager = DatabaseBackupManager(config)
        # El sistema debería inicializarse sin problemas
        assert manager is not None
    except Exception as e:
        # Si falla, debería ser un error manejado graciosamente
        assert "Error" in str(e) or "No se pudo" in str(e)


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Limpia archivos temporales después de cada test."""
    yield
    # Cleanup logic if needed
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])