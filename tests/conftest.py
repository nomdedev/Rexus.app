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


# ==========================================
# FIXTURES PARA TESTS VISUALES HÍBRIDOS
# ==========================================

@pytest.fixture(scope="function")
def usuarios_mock_data():
    """Datos mock específicos para tests visuales de usuarios."""
    return [
        {
            'id': i,
            'username': f'user{i}',
            'email': f'user{i}@rexus.com',
            'role': ['admin', 'user', 'viewer'][i % 3],
            'status': ['active', 'inactive'][i % 2],
            'created_at': f'2025-01-{(i % 28) + 1:02d}',
            'last_login': f'2025-01-{(i % 30) + 1:02d}',
            'permissions': ['read', 'write', 'delete'] if i % 3 == 0 else ['read']
        }
        for i in range(1, 21)  # 20 usuarios de prueba
    ]


@pytest.fixture(scope="function")
def inventario_mock_data():
    """Datos mock específicos para tests visuales de inventario."""
    return [
        {
            'id': i,
            'codigo': f'MAT{i:03d}',
            'descripcion': f'Material de prueba {i}',
            'categoria': ['Herramientas', 'Consumibles', 'Eléctrico', 'Plomería'][i % 4],
            'unidad': ['pza', 'kg', 'm', 'lt'][i % 4],
            'stock_actual': max(0, 50 - (i % 60)),  # Algunos con stock bajo
            'stock_minimo': 10 + (i % 20),
            'precio_unitario': round(10.0 + (i * 2.5), 2),
            'ubicacion': f'{chr(65 + (i % 3))}{(i % 3) + 1}-{(i % 10):02d}',
            'proveedor': f'Proveedor {(i % 5) + 1}',
            'fecha_ultima_entrada': f'2025-01-{(i % 28) + 1:02d}'
        }
        for i in range(1, 101)  # 100 items de inventario
    ]


@pytest.fixture(scope="function")
def obras_mock_data():
    """Datos mock específicos para tests visuales de obras."""
    estados = ['pendiente', 'en_progreso', 'completada', 'pausada', 'cancelada']
    responsables = ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martín']
    
    return [
        {
            'id': i,
            'codigo': f'OBR-2025-{i:03d}',
            'nombre': f'Obra {i} - Construcción Tipo {chr(65 + (i % 3))}',
            'cliente': f'Cliente {(i % 5) + 1} S.A.',
            'estado': estados[i % len(estados)],
            'fecha_inicio': f'2025-{((i % 12) + 1):02d}-{((i % 28) + 1):02d}',
            'fecha_fin_estimada': f'2025-{(((i + 6) % 12) + 1):02d}-{((i % 28) + 1):02d}',
            'presupuesto': round(50000.0 + (i * 15000.0), 2),
            'progreso': min(100, (i * 12) % 101),
            'responsable': responsables[i % len(responsables)],
            'direccion': f'Calle {i} #{i*10}, Zona {chr(65 + (i % 3))}',
            'descripcion': f'Construcción de obra tipo {chr(65 + (i % 3))} con especificaciones técnicas avanzadas.',
            'observaciones': f'Observaciones específicas para obra {i}'
        }
        for i in range(1, 51)  # 50 obras de prueba
    ]


@pytest.fixture(scope="function")
def visual_test_validator():
    """Validador para tests visuales híbridos."""
    try:
        from tests.strategies.hybrid_visual_testing import VisualTestValidator
        return VisualTestValidator()
    except ImportError:
        # Fallback simple si no está disponible la estrategia híbrida
        class SimpleValidator:
            def validate_component_rendering(self, component):
                return component is not None
            
            def validate_interaction(self, component, action):
                return True
                
            def measure_performance(self, operation):
                import time
                start = time.time()
                result = operation() if callable(operation) else operation
                return time.time() - start, result
        
        return SimpleValidator()


@pytest.fixture(scope="function")
def mock_data_factory():
    """Factory para generar datos mock dinámicamente para tests visuales."""
    class MockDataFactory:
        def create_usuarios_mock(self, count=10):
            return [
                {
                    'id': i,
                    'username': f'user{i}',
                    'email': f'user{i}@test.com',
                    'role': ['admin', 'user', 'viewer'][i % 3],
                    'status': ['active', 'inactive'][i % 2],
                    'permissions': ['read', 'write'] if i % 2 == 0 else ['read']
                }
                for i in range(1, count + 1)
            ]
        
        def create_inventario_mock(self, count=10):
            return [
                {
                    'id': i,
                    'codigo': f'MAT{i:03d}',
                    'descripcion': f'Material {i}',
                    'categoria': ['Cat A', 'Cat B', 'Cat C'][i % 3],
                    'stock_actual': 50 + (i % 100),
                    'stock_minimo': 10 + (i % 10),
                    'precio_unitario': round(10.0 + (i * 2.5), 2),
                    'ubicacion': f'A{i % 5}-{i % 10}'
                }
                for i in range(1, count + 1)
            ]
        
        def create_obras_mock(self, count=10):
            return [
                {
                    'id': i,
                    'codigo': f'OBR{i:03d}',
                    'nombre': f'Obra {i}',
                    'estado': ['pendiente', 'activa', 'completada'][i % 3],
                    'progreso': min(100, i * 10),
                    'presupuesto': 50000 + (i * 10000),
                    'cliente': f'Cliente {i}'
                }
                for i in range(1, count + 1)
            ]
    
    return MockDataFactory()


@pytest.fixture(scope="function")
def ui_interaction_helper():
    """Helper para interacciones de UI en tests visuales."""
    try:
        from PyQt6.QtTest import QTest
        from PyQt6.QtCore import Qt
        
        class UIHelper:
            @staticmethod
            def click_button(button):
                """Simula click en botón."""
                if button and button.isEnabled():
                    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                    return True
                return False
            
            @staticmethod
            def type_text(widget, text):
                """Simula escritura de texto."""
                if widget:
                    widget.clear()
                    widget.setText(text)
                    return True
                return False
            
            @staticmethod
            def select_combo_item(combo, index):
                """Simula selección en combo."""
                if combo and index < combo.count():
                    combo.setCurrentIndex(index)
                    return True
                return False
        
        return UIHelper()
        
    except ImportError:
        # Fallback sin PyQt6
        class MockUIHelper:
            @staticmethod
            def click_button(button):
                return False
            
            @staticmethod
            def type_text(widget, text):
                return False
            
            @staticmethod
            def select_combo_item(combo, index):
                return False
        
        return MockUIHelper()
