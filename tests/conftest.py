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
def mock_db_connection():
    """Mock de conexión a base de datos para tests."""
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


@pytest.fixture(scope="session")
def test_database_path():
    """Path a la base de datos de testing."""
    return "tests/test_database.db"


@pytest.fixture(scope="function")
def performance_timer():
    """Timer para medir performance en tests."""
    import time
    from contextlib import contextmanager
    
    @contextmanager
    def timer():
        class Timer:
            def __init__(self):
                self.start = None
                self.end = None
                self.elapsed = None
        
        timer_obj = Timer()
        timer_obj.start = time.time()
        
        try:
            yield timer_obj
        finally:
            timer_obj.end = time.time()
            timer_obj.elapsed = timer_obj.end - timer_obj.start
    
    return timer


@pytest.fixture(scope="function")
def mock_logger():
    """Mock del sistema de logging."""
    from unittest.mock import Mock
    
    logger = Mock()
    logger.debug.return_value = None
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    logger.critical.return_value = None
    
    return logger


@pytest.fixture(scope="function")
def invalid_data_samples():
    """Conjuntos de datos inválidos para tests negativos."""
    return {
        'empty_strings': {
            'codigo': '',
            'nombre': '',
            'descripcion': ''
        },
        'null_values': {
            'codigo': None,
            'nombre': None,
            'precio': None
        },
        'wrong_types': {
            'id': 'not_an_integer',
            'precio': 'not_a_float',
            'activo': 'not_a_boolean',
            'fecha': 'not_a_date'
        },
        'out_of_range': {
            'stock_actual': -1,
            'precio_unitario': -10.50,
            'presupuesto_total': -1000.00
        }
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
