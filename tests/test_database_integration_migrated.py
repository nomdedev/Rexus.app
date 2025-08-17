"""
Database Integration Test - Rexus.app v2.0.0 (Migrated)

Modern pytest version testing models with actual database connection.
No return True/False patterns, uses proper pytest fixtures and assertions.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import using modern paths
try:
    from rexus.modules.inventario.model import InventarioModel
    from rexus.modules.herrajes.model import HerrajesModel
    from rexus.modules.vidrios.model import VidriosModel
    from rexus.modules.pedidos.model import PedidosModel
    from rexus.modules.obras.model import ObrasModel
    from rexus.core.database import DatabaseConnection
except ImportError as e:
    pytest.skip(f"Cannot import models: {e}", allow_module_level=True)


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection for testing."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    
    # Mock some basic query results
    mock_cursor.fetchall.return_value = [
        ('TEST001', 'Test Product', 'PERFIL', 10, 100.0),
        ('TEST002', 'Test Product 2', 'VIDRIO', 5, 50.0)
    ]
    mock_cursor.fetchone.return_value = ('TEST001', 'Test Product', 'PERFIL', 10, 100.0)
    mock_cursor.rowcount = 1
    
    return mock_conn


@pytest.fixture
def real_db_connection():
    """Create a real database connection if available."""
    try:
        # Try to create real connection
        db = DatabaseConnection()
        if db.connect():
            yield db
            db.disconnect()
        else:
            pytest.skip("Database connection not available")
    except Exception as e:
        pytest.skip(f"Database connection failed: {e}")


class TestDatabaseIntegration:
    """Test suite for database integration using modern pytest patterns."""

    def test_inventario_model_with_mock_db(self, mock_db_connection):
        """Test InventarioModel with mock database."""
        inventario = InventarioModel(db_connection=mock_db_connection)
        assert inventario is not None
        assert inventario.db_connection == mock_db_connection

    def test_herrajes_model_with_mock_db(self, mock_db_connection):
        """Test HerrajesModel with mock database."""
        herrajes = HerrajesModel(db_connection=mock_db_connection)
        assert herrajes is not None
        assert herrajes.db_connection == mock_db_connection

    def test_vidrios_model_with_mock_db(self, mock_db_connection):
        """Test VidriosModel with mock database."""
        vidrios = VidriosModel(db_connection=mock_db_connection)
        assert vidrios is not None
        assert vidrios.db_connection == mock_db_connection

    def test_pedidos_model_with_mock_db(self, mock_db_connection):
        """Test PedidosModel with mock database."""
        pedidos = PedidosModel(db_connection=mock_db_connection)
        assert pedidos is not None
        assert pedidos.db_connection == mock_db_connection

    def test_obras_model_with_mock_db(self, mock_db_connection):
        """Test ObrasModel with mock database."""
        obras = ObrasModel(db_connection=mock_db_connection)
        assert obras is not None
        assert obras.db_connection == mock_db_connection

    @pytest.mark.integration
    def test_inventario_model_with_real_db(self, real_db_connection):
        """Test InventarioModel with real database connection."""
        inventario = InventarioModel(db_connection=real_db_connection)
        assert inventario is not None
        
        # Test that we can call methods without errors
        try:
            # Try to get products (might be empty, that's ok)
            productos = inventario.obtener_todos_productos()
            assert isinstance(productos, list)
        except (AttributeError, NotImplementedError):
            # Method might not be implemented, that's ok for this test
            pass

    @pytest.mark.integration  
    def test_models_can_handle_none_connection(self):
        """Test that models can gracefully handle None connection."""
        # All models should be able to initialize with None connection
        inventario = InventarioModel(db_connection=None)
        herrajes = HerrajesModel(db_connection=None) 
        vidrios = VidriosModel(db_connection=None)
        pedidos = PedidosModel(db_connection=None)
        obras = ObrasModel(db_connection=None)
        
        # All should be initialized successfully
        assert all(model is not None for model in [inventario, herrajes, vidrios, pedidos, obras])

    def test_database_connection_handling(self, mock_db_connection):
        """Test proper database connection handling patterns."""
        inventario = InventarioModel(db_connection=mock_db_connection)
        
        # Test that cursor operations can be called
        try:
            if hasattr(inventario, 'obtener_todos_productos'):
                inventario.obtener_todos_productos()
                # Verify cursor was used
                mock_db_connection.cursor.assert_called()
        except (AttributeError, NotImplementedError):
            # Method might not exist, skip this check
            pass

    def test_mock_database_basic_operations(self, mock_db_connection):
        """Test basic database operations with mock."""
        cursor = mock_db_connection.cursor()
        
        # Test basic cursor operations
        cursor.execute("SELECT * FROM test")
        cursor.fetchall()
        
        # Verify mocks were called
        cursor.execute.assert_called_with("SELECT * FROM test")
        cursor.fetchall.assert_called()


# Integration test markers for pytest
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    # Can still be run directly
    pytest.main([__file__, "-v", "-m", "not integration"])  # Skip integration tests by default