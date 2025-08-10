import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Fixture global para inicializar QApplication antes de cualquier test
@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Asegura que QApplication esté inicializado para todos los tests de UI."""
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        pytest.skip("PyQt6 no está instalado")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture(scope="function")
def mock_db():
    """Mock de base de datos para tests unitarios."""
    from unittest.mock import Mock
    
    db = Mock()
    cursor = Mock()
    db.cursor.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.execute.return_value = None
    cursor.rowcount = 0
    cursor.lastrowid = 1
    
    return db


@pytest.fixture(scope="function")
def sample_user_data():
    """Datos de usuario de ejemplo para tests."""
    return {
        'id': 1,
        'username': 'test_user',
        'password': 'test_password',
        'email': 'test@example.com',
        'nombre': 'Test',
        'apellido': 'User',
        'rol': 'USER',
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_inventario_data():
    """Datos de inventario de ejemplo para tests."""
    return {
        'id': 1,
        'codigo': 'PROD001',
        'nombre': 'Producto Test',
        'descripcion': 'Descripción de prueba',
        'categoria': 'CATEGORIA_TEST',
        'stock_actual': 100,
        'stock_minimo': 10,
        'precio_unitario': 25.50,
        'proveedor': 'Proveedor Test',
        'ubicacion': 'A1-B2',
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_obra_data():
    """Datos de obra de ejemplo para tests."""
    return {
        'id': 1,
        'codigo_obra': 'OBRA001',
        'nombre_obra': 'Obra Test',
        'cliente': 'Cliente Test',
        'estado': 'EN_PROCESO',
        'presupuesto_total': 100000.00,
        'descripcion': 'Descripción de obra test',
        'ubicacion': 'Ubicación test',
        'fecha_inicio': '2024-01-01',
        'fecha_fin_estimada': '2024-12-31',
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_logistica_data():
    """Datos de logística de ejemplo para tests."""
    return {
        'id': 1,
        'origen': 'Almacén Central',
        'destino': 'Obra Test',
        'conductor': 'Juan Pérez',
        'vehiculo': 'ABC-123',
        'fecha': '2024-08-10',
        'estado': 'Pendiente',
        'observaciones': 'Transporte de materiales'
    }
