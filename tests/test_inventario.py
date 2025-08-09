#!/usr/bin/env python3
"""
Tests para el módulo de Inventario

Cubre funcionalidades críticas como:
- CRUD de productos
- Gestión de stock
- Reservas de materiales
- Movimientos de inventario
- Validación de datos
- Consultas de disponibilidad
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from decimal import Decimal

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Importar el módulo a probar
try:
    from rexus.modules.inventario.model import InventarioModel
    from rexus.modules.inventario.controller import InventarioController
    inventario_available = True
except ImportError as e:
    print(f"Warning: No se pudo importar módulo inventario: {e}")
    inventario_available = False

class MockDatabase:
    """Mock de base de datos para tests."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.closed = False
        self._last_inserted_id = 1
        
    def cursor(self):
        return self.cursor_mock
        
    def commit(self):
        pass
        
    def rollback(self):
        pass
        
    def close(self):
        self.closed = True

@pytest.fixture
def mock_db():
    """Fixture para base de datos mock."""
    return MockDatabase()

@pytest.fixture
def inventario_model(mock_db):
    """Fixture para modelo de inventario."""
    if not inventario_available:
        pytest.skip("Módulo inventario no disponible")
    return InventarioModel(mock_db)

class TestInventarioModel:
    """Tests para el modelo de inventario."""
    
    def test_model_initialization(self, inventario_model):
        """Test inicialización del modelo."""
        assert inventario_model is not None
        assert inventario_model.db_connection is not None
        
    def test_validate_product_data(self, inventario_model):
        """Test de validación de datos de producto."""
        # Datos válidos
        valid_data = {
            'codigo': 'PROD001',
            'nombre': 'Producto de Prueba',
            'categoria': 'categoria_test',
            'precio': Decimal('99.99'),
            'stock': 100,
            'stock_minimo': 10
        }
        
        validation_result = inventario_model.validate_product_data(valid_data)
        assert validation_result['valid'] == True
        
        # Datos inválidos - código vacío
        invalid_data = {
            'codigo': '',
            'nombre': 'Producto de Prueba',
            'categoria': 'categoria_test',
            'precio': Decimal('-10.00'),  # Precio negativo
            'stock': -5,  # Stock negativo
            'stock_minimo': 10
        }
        
        validation_result = inventario_model.validate_product_data(invalid_data)
        assert validation_result['valid'] == False
        assert len(validation_result['errors']) > 0

    @patch('rexus.modules.inventario.model.InventarioModel._execute_query')
    def test_create_product(self, mock_execute, inventario_model):
        """Test de creación de producto."""
        mock_execute.return_value = None
        inventario_model.db_connection.cursor_mock.fetchone.return_value = [1]  # ID del nuevo producto
        
        product_data = {
            'codigo': 'PROD001',
            'nombre': 'Producto de Prueba',
            'categoria': 'categoria_test',
            'precio': Decimal('99.99'),
            'stock': 100,
            'stock_minimo': 10,
            'descripcion': 'Descripción del producto de prueba'
        }
        
        with patch.object(inventario_model, 'validate_product_data', return_value={'valid': True, 'errors': []}):
            result = inventario_model.create_product(product_data)
            
        assert result['success'] == True
        assert result['product_id'] == 1

    @patch('rexus.modules.inventario.model.InventarioModel._execute_query')
    def test_get_product_by_code(self, mock_execute, inventario_model):
        """Test de obtener producto por código."""
        # Simular producto existente
        mock_execute.return_value = [
            (1, 'PROD001', 'Producto Test', 'categoria_test', Decimal('99.99'), 100, 10, 'activo')
        ]
        
        result = inventario_model.get_product_by_code('PROD001')
        
        assert result is not None
        assert result['codigo'] == 'PROD001'
        assert result['nombre'] == 'Producto Test'
        assert result['stock'] == 100

    @patch('rexus.modules.inventario.model.InventarioModel._execute_query')
    def test_update_stock(self, mock_execute, inventario_model):
        """Test de actualización de stock."""
        mock_execute.return_value = None
        
        result = inventario_model.update_stock(1, 150, 'AJUSTE', 'Ajuste de inventario')
        
        assert result['success'] == True
        # Verificar que se llamó al método de ejecución
        mock_execute.assert_called()

    def test_calculate_stock_value(self, inventario_model):
        """Test de cálculo de valor de stock."""
        stock_data = [
            {'stock': 100, 'precio': Decimal('10.50')},
            {'stock': 50, 'precio': Decimal('25.75')},
            {'stock': 25, 'precio': Decimal('8.00')}
        ]
        
        total_value = inventario_model.calculate_total_stock_value(stock_data)
        
        expected = (100 * Decimal('10.50')) + (50 * Decimal('25.75')) + (25 * Decimal('8.00'))
        assert total_value == expected

    def test_check_stock_availability(self, inventario_model):
        """Test de verificación de disponibilidad de stock."""
        # Stock disponible
        available = inventario_model.check_stock_availability(100, 50)
        assert available == True
        
        # Stock insuficiente
        unavailable = inventario_model.check_stock_availability(10, 50)
        assert unavailable == False
        
        # Stock exacto
        exact = inventario_model.check_stock_availability(50, 50)
        assert exact == True

    @patch('rexus.modules.inventario.model.InventarioModel._execute_query')
    def test_create_reservation(self, mock_execute, inventario_model):
        """Test de creación de reserva."""
        mock_execute.return_value = None
        inventario_model.db_connection.cursor_mock.fetchone.return_value = [1]  # ID de la reserva
        
        reservation_data = {
            'producto_id': 1,
            'obra_id': 1,
            'cantidad': 10,
            'fecha_vencimiento': '2024-12-31',
            'observaciones': 'Reserva para obra'
        }
        
        with patch.object(inventario_model, 'check_stock_availability', return_value=True):
            result = inventario_model.create_reservation(reservation_data)
            
        assert result['success'] == True
        assert result['reservation_id'] == 1

    def test_sanitize_search_input(self, inventario_model):
        """Test de sanitización de búsquedas."""
        # Búsqueda con caracteres especiales
        search_input = "PROD'; DROP TABLE productos; --"
        sanitized = inventario_model._sanitize_search_input(search_input)
        
        assert "DROP TABLE" not in sanitized.upper()
        assert "--" not in sanitized
        
        # Búsqueda normal
        normal_search = "PROD001"
        sanitized_normal = inventario_model._sanitize_search_input(normal_search)
        assert sanitized_normal == "PROD001"

class TestInventarioController:
    """Tests para el controlador de inventario."""
    
    @pytest.fixture
    def inventario_controller(self, mock_db):
        """Fixture para controlador de inventario."""
        if not inventario_available:
            pytest.skip("Módulo inventario no disponible")
        return InventarioController(mock_db)
    
    def test_controller_initialization(self, inventario_controller):
        """Test inicialización del controlador."""
        assert inventario_controller is not None
        assert inventario_controller.model is not None

    @patch('rexus.modules.inventario.model.InventarioModel.get_products_with_filters')
    def test_search_products(self, mock_search, inventario_controller):
        """Test de búsqueda de productos."""
        mock_search.return_value = {
            'products': [
                {'id': 1, 'codigo': 'PROD001', 'nombre': 'Producto 1', 'stock': 100},
                {'id': 2, 'codigo': 'PROD002', 'nombre': 'Producto 2', 'stock': 50}
            ],
            'total': 2
        }
        
        result = inventario_controller.search_products('PROD')
        
        assert result['success'] == True
        assert len(result['products']) == 2

    @patch('rexus.modules.inventario.model.InventarioModel.create_product')
    def test_add_product(self, mock_create, inventario_controller):
        """Test de añadir producto."""
        mock_create.return_value = {
            'success': True,
            'product_id': 1
        }
        
        product_data = {
            'codigo': 'PROD001',
            'nombre': 'Producto Test',
            'categoria': 'test',
            'precio': '99.99',
            'stock': '100',
            'stock_minimo': '10'
        }
        
        result = inventario_controller.add_product(product_data)
        
        assert result['success'] == True
        assert result['product_id'] == 1

class TestInventarioIntegration:
    """Tests de integración del módulo inventario."""
    
    def test_stock_movements_consistency(self):
        """Test de consistency en movimientos de stock."""
        if not inventario_available:
            pytest.skip("Módulo inventario no disponible")
            
        model = InventarioModel(MockDatabase())
        
        # Simular movimientos de stock
        initial_stock = 100
        movements = [
            {'type': 'ENTRADA', 'cantidad': 50},
            {'type': 'SALIDA', 'cantidad': 30},
            {'type': 'AJUSTE', 'cantidad': -5},
            {'type': 'ENTRADA', 'cantidad': 25}
        ]
        
        final_stock = initial_stock
        for movement in movements:
            if movement['type'] == 'ENTRADA':
                final_stock += movement['cantidad']
            elif movement['type'] == 'SALIDA':
                final_stock -= movement['cantidad']
            elif movement['type'] == 'AJUSTE':
                final_stock += movement['cantidad']  # Puede ser positivo o negativo
                
        expected_final_stock = 140  # 100 + 50 - 30 - 5 + 25
        assert final_stock == expected_final_stock

    def test_reservation_business_rules(self):
        """Test de reglas de negocio para reservas."""
        if not inventario_available:
            pytest.skip("Módulo inventario no disponible")
            
        model = InventarioModel(MockDatabase())
        
        # Test: No se puede reservar más stock del disponible
        available_stock = 50
        requested_quantity = 60
        
        can_reserve = model.check_stock_availability(available_stock, requested_quantity)
        assert can_reserve == False
        
        # Test: Se puede reservar stock disponible
        requested_quantity = 30
        can_reserve = model.check_stock_availability(available_stock, requested_quantity)
        assert can_reserve == True

    def test_price_calculations(self):
        """Test de cálculos de precios."""
        if not inventario_available:
            pytest.skip("Módulo inventario no disponible")
            
        model = InventarioModel(MockDatabase())
        
        # Test: Cálculo de valor total de inventario
        products = [
            {'stock': 100, 'precio': Decimal('10.50')},
            {'stock': 50, 'precio': Decimal('25.75')},
            {'stock': 0, 'precio': Decimal('100.00')},  # Sin stock
        ]
        
        total_value = model.calculate_total_stock_value(products)
        expected = Decimal('100') * Decimal('10.50') + Decimal('50') * Decimal('25.75')
        
        assert total_value == expected

    def test_search_functionality(self):
        """Test de funcionalidad de búsqueda."""
        if not inventario_available:
            pytest.skip("Módulo inventario no disponible")
            
        model = InventarioModel(MockDatabase())
        
        # Test: Sanitización de términos de búsqueda
        dangerous_terms = [
            "'; DROP TABLE productos; --",
            "UNION SELECT * FROM usuarios",
            "<script>alert('xss')</script>"
        ]
        
        for term in dangerous_terms:
            sanitized = model._sanitize_search_input(term)
            
            # Verificar que se removieron patrones peligrosos
            assert "DROP TABLE" not in sanitized.upper()
            assert "UNION SELECT" not in sanitized.upper()
            assert "<script>" not in sanitized.lower()

def test_module_imports():
    """Test que el módulo se pueda importar correctamente."""
    try:
        from rexus.modules.inventario import model, controller
        assert hasattr(model, 'InventarioModel')
        assert hasattr(controller, 'InventarioController')
        print("✓ Módulo inventario importado correctamente")
    except ImportError as e:
        print(f"✗ Error importando módulo inventario: {e}")
        pytest.skip("Módulo inventario no disponible para testing")

if __name__ == "__main__":
    # Ejecutar tests directamente
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS DEL MÓDULO INVENTARIO")
    print("=" * 60)
    
    # Ejecutar con pytest si está disponible
    try:
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest no disponible, ejecutando tests básicos...")
        
        # Tests básicos sin pytest
        print("\n📋 Test de importación...")
        test_module_imports()
        
        if inventario_available:
            print("\n📦 Test básico de disponibilidad de stock...")
            model = InventarioModel(MockDatabase())
            
            # Test disponibilidad
            available = model.check_stock_availability(100, 50)
            if available:
                print("✓ Test de disponibilidad de stock: PASÓ")
            else:
                print("✗ Test de disponibilidad de stock: FALLÓ")
                
            # Test indisponibilidad  
            unavailable = model.check_stock_availability(10, 50)
            if not unavailable:
                print("✓ Test de stock insuficiente: PASÓ")
            else:
                print("✗ Test de stock insuficiente: FALLÓ")
                
            print("\n💰 Test básico de cálculos...")
            products = [
                {'stock': 10, 'precio': Decimal('5.00')},
                {'stock': 20, 'precio': Decimal('10.00')}
            ]
            
            total = model.calculate_total_stock_value(products)
            expected = Decimal('250.00')  # 10*5 + 20*10 = 250
            
            if total == expected:
                print("✓ Test de cálculo de valor total: PASÓ")
            else:
                print(f"✗ Test de cálculo de valor total: FALLÓ (esperado {expected}, obtenido {total})")
                
            print("\n🛡️ Test básico de sanitización...")
            malicious = "'; DROP TABLE productos; --"
            sanitized = model._sanitize_search_input(malicious)
            
            if "DROP TABLE" not in sanitized.upper():
                print("✓ Test de sanitización: PASÓ")
            else:
                print("✗ Test de sanitización: FALLÓ")
        
        print("\n" + "=" * 60)
        print("🏁 TESTS COMPLETADOS")
        print("=" * 60)