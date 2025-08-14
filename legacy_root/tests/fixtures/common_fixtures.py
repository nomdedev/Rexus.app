"""
Fixtures compartidas para toda la suite de tests de Rexus.app

Este módulo contiene fixtures reutilizables que proporcionan
datos de prueba y mocks comunes para todos los tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, date


@pytest.fixture(scope="function")
def mock_db_connection():
    """
    Mock de conexión a base de datos.

    Proporciona un mock completo de la conexión a DB
    con cursor y métodos básicos mockeados.
    """
    db = Mock()
    cursor = Mock()

    # Configurar cursor mock
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.execute.return_value = None
    cursor.executemany.return_value = None
    cursor.rowcount = 0
    cursor.lastrowid = 1
    cursor.description = []

    # Configurar conexión mock
    db.cursor.return_value = cursor
    db.commit.return_value = None
    db.rollback.return_value = None
    db.close.return_value = None

    return db


@pytest.fixture(scope="function")
def sample_usuario_data():
    """Datos de usuario válidos para tests."""
    return {
        'id': 1,
        'username': 'test_user',
        'password': 'SecurePass123!',
        'email': 'test@rexus.app',
        'nombre': 'Usuario',
        'apellido': 'Test',
        'rol': 'USER',
        'activo': True,
        'fecha_creacion': datetime.now(),
        'ultimo_acceso': datetime.now()
    }


@pytest.fixture(scope="function")
def sample_producto_data():
    """Datos de producto válidos para tests."""
    return {
        'id': 1,
        'codigo': 'PROD001',
        'nombre': 'Producto Test',
        'descripcion': 'Descripción de producto para testing',
        'categoria': 'CATEGORIA_TEST',
        'stock_actual': 100,
        'stock_minimo': 10,
        'stock_maximo': 1000,
        'precio_unitario': 25.50,
        'precio_venta': 35.75,
        'proveedor': 'Proveedor Test S.A.',
        'ubicacion': 'A1-B2-C3',
        'activo': True,
        'fecha_creacion': date.today()
    }


@pytest.fixture(scope="function")
def sample_obra_data():
    """Datos de obra válidos para tests."""
    return {
        'id': 1,
        'codigo_obra': 'OBRA001',
        'nombre_obra': 'Obra de Prueba',
        'cliente': 'Cliente Test S.R.L.',
        'estado': 'EN_PROCESO',
        'presupuesto_total': 150000.00,
        'presupuesto_ejecutado': 45000.00,
        'descripcion': 'Obra de testing para validar funcionalidad',
        'ubicacion': 'Calle Falsa 123, Ciudad Test',
        'fecha_inicio': date(2024, 1, 1),
        'fecha_fin_estimada': date(2024, 12, 31),
        'fecha_fin_real': None,
        'responsable': 'Ing. Test Manager',
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_transporte_data():
    """Datos de transporte válidos para tests."""
    return {
        'id': 1,
        'origen': 'Almacén Central',
        'destino': 'Obra Test Site',
        'conductor': 'Juan Pérez González',
        'vehiculo': 'ABC-123',
        'fecha': date.today(),
        'hora_salida': '08:00',
        'hora_llegada': None,
        'estado': 'Pendiente',
        'observaciones': 'Transporte de materiales para obra',
        'carga': 'Cemento, hierros, arena',
        'peso_total': 2500.0,
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_material_data():
    """Datos de material válidos para tests."""
    return {
        'id': 1,
        'codigo': 'MAT001',
        'nombre': 'Cemento Portland',
        'descripcion': 'Cemento para construcción general',
        'unidad_medida': 'BOLSA',
        'cantidad_por_unidad': 50.0,  # kg por bolsa
        'precio_unitario': 8.50,
        'categoria': 'CONSTRUCCION',
        'proveedor': 'Cementos Test S.A.',
        'activo': True
    }


@pytest.fixture(scope="function")
def sample_movimiento_data():
    """Datos de movimiento de inventario válidos para tests."""
    return {
        'id': 1,
        'producto_id': 1,
        'tipo_movimiento': 'ENTRADA',
        'cantidad': 50,
        'precio_unitario': 25.50,
        'motivo': 'Compra a proveedor',
        'documento': 'FAC-001-123',
        'fecha': datetime.now(),
        'usuario_id': 1,
        'observaciones': 'Entrada de mercadería según factura',
        'activo': True
    }


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
        },
        'too_long_strings': {
            'codigo': 'X' * 256,  # Muy largo para código
            'nombre': 'X' * 1024,  # Muy largo para nombre
            'descripcion': 'X' * 10000  # Muy largo para descripción
        }
    }


@pytest.fixture(scope="function")
def mock_security_manager():
    """Mock del gestor de seguridad."""
    security = Mock()

    # Configurar métodos comunes
    security.validate_user.return_value = True
    security.check_permissions.return_value = True
    security.sanitize_input.side_effect = lambda x: x  # Passthrough
    security.validate_sql.return_value = True
    security.log_security_event.return_value = None

    return security


@pytest.fixture(scope="function")
def mock_logger():
    """Mock del sistema de logging."""
    logger = Mock()

    # Configurar niveles de log
    logger.debug.return_value = None
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    logger.critical.return_value = None

    return logger


@pytest.fixture(scope="function")
def mock_config():
    """Mock de configuración del sistema."""
    config = Mock()

    # Configuraciones típicas
    config.get.return_value = "test_value"
    config.database_url = "sqlite:///:memory:"
    config.debug = True
    config.testing = True
    config.max_connections = 10
    config.timeout = 30

    return config


@pytest.fixture(scope="session")
def test_database_path():
    """Path a la base de datos de testing."""
    return "tests/test_database.db"


@pytest.fixture(scope="function")
def clean_database(test_database_path):
    """
    Limpia la base de datos de testing antes y después de cada test.

    Asegura que cada test empiece con un estado limpio.
    """
    import sqlite3
    import os

    # Limpiar antes del test
    if os.path.exists(test_database_path):
        os.remove(test_database_path)

    # Crear base de datos limpia
    conn = sqlite3.connect(test_database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()

    yield test_database_path

    # Limpiar después del test
    if os.path.exists(test_database_path):
        os.remove(test_database_path)


@pytest.fixture(scope="function")
def performance_timer():
    """
    Timer para medir performance en tests.

    Usage:
        with performance_timer() as timer:
            # código a medir
            pass
        assert timer.elapsed < 1.0  # menos de 1 segundo
    """
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
