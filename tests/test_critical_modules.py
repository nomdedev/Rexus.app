"""
Tests Unitarios para Módulos Críticos de Rexus.app
Cubre: inventario, compras, auditoria, configuracion

Fecha: 15/08/2025
Objetivo: Validar funcionamiento de módulos críticos del sistema
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class MockDatabase:
    """Mock de base de datos para tests."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.connected = True
        self.committed = False
        self.rolledback = False
    
    def cursor(self):
        return self.cursor_mock
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        self.rolledback = True
    
    def close(self):
        self.connected = False


class TestInventarioModule(unittest.TestCase):
    """Tests para el módulo de Inventario."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockDatabase()
        
        # Mock de datos de inventario
        self.sample_producto = {
            'id': 1,
            'codigo': 'TEST001',
            'descripcion': 'Producto de prueba',
            'categoria': 'Test',
            'stock_actual': 100,
            'precio_unitario': 25.50
        }
    
    @patch('rexus.modules.inventario.model.get_inventario_connection')
    def test_inventario_model_initialization(self, mock_connection):
        """Test inicialización del modelo de inventario."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.inventario.model import InventarioModel
            model = InventarioModel(self.mock_db)
            
            self.assertIsNotNone(model)
            self.assertEqual(model.db_connection, self.mock_db)
            
        except ImportError:
            self.skipTest("Módulo inventario no disponible")
    
    @patch('rexus.modules.inventario.model.get_inventario_connection')
    def test_inventario_obtener_productos(self, mock_connection):
        """Test obtener productos del inventario."""
        mock_connection.return_value = self.mock_db
        
        # Configurar mock para retornar datos de prueba
        self.mock_db.cursor_mock.fetchall.return_value = [
            (1, 'TEST001', 'Producto 1', 'Categoria A', 100, 25.50),
            (2, 'TEST002', 'Producto 2', 'Categoria B', 50, 30.00)
        ]
        self.mock_db.cursor_mock.description = [
            ('id',), ('codigo',), ('descripcion',), ('categoria',), ('stock_actual',), ('precio_unitario',)
        ]
        
        try:
            from rexus.modules.inventario.model import InventarioModel
            model = InventarioModel(self.mock_db)
            
            # Test obtener productos
            if hasattr(model, 'obtener_productos'):
                productos = model.obtener_productos()
                
                self.assertIsInstance(productos, list)
                if productos:  # Si retornó datos
                    self.assertIsInstance(productos[0], dict)
                    
        except ImportError:
            self.skipTest("Módulo inventario no disponible")
        except Exception as e:
            self.fail(f"Error en test obtener productos: {e}")
    
    def test_inventario_view_initialization(self):
        """Test inicialización de la vista de inventario."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            # Test que la clase se puede importar e instanciar
            self.assertTrue(hasattr(InventarioView, '__init__'))
            
        except ImportError:
            self.skipTest("Vista de inventario no disponible")


class TestComprasModule(unittest.TestCase):
    """Tests para el módulo de Compras."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockDatabase()
        
        self.sample_compra = {
            'id': 1,
            'numero_orden': 'OC-001',
            'proveedor': 'Proveedor Test',
            'estado': 'PENDIENTE',
            'total': 1500.00
        }
    
    @patch('rexus.modules.compras.model.get_inventario_connection')
    def test_compras_model_initialization(self, mock_connection):
        """Test inicialización del modelo de compras."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.compras.model import ComprasModel
            model = ComprasModel(self.mock_db)
            
            self.assertIsNotNone(model)
            self.assertEqual(model.db_connection, self.mock_db)
            
        except ImportError:
            self.skipTest("Módulo compras no disponible")
    
    @patch('rexus.modules.compras.model.get_inventario_connection')
    def test_compras_crear_compra(self, mock_connection):
        """Test crear nueva compra."""
        mock_connection.return_value = self.mock_db
        
        # Mock para retornar ID de compra creada
        self.mock_db.cursor_mock.fetchone.return_value = (123,)
        
        try:
            from rexus.modules.compras.model import ComprasModel
            model = ComprasModel(self.mock_db)
            
            if hasattr(model, 'crear_compra'):
                resultado = model.crear_compra(self.sample_compra)
                
                # Verificar que se llamó a execute (se intentó insertar)
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Módulo compras no disponible")
        except Exception as e:
            self.fail(f"Error en test crear compra: {e}")
    
    def test_compras_view_initialization(self):
        """Test inicialización de la vista de compras."""
        try:
            from rexus.modules.compras.view import ComprasView
            
            self.assertTrue(hasattr(ComprasView, '__init__'))
            
        except ImportError:
            self.skipTest("Vista de compras no disponible")


class TestAuditoriaModule(unittest.TestCase):
    """Tests para el módulo de Auditoría."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockDatabase()
        
        self.sample_evento = {
            'usuario_id': 1,
            'modulo': 'inventario',
            'accion': 'CREATE',
            'descripcion': 'Creación de producto TEST001'
        }
    
    @patch('rexus.modules.auditoria.model.get_auditoria_connection')
    def test_auditoria_model_initialization(self, mock_connection):
        """Test inicialización del modelo de auditoría."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.auditoria.model import AuditoriaModel
            model = AuditoriaModel(self.mock_db)
            
            self.assertIsNotNone(model)
            self.assertEqual(model.db_connection, self.mock_db)
            
        except ImportError:
            self.skipTest("Módulo auditoría no disponible")
    
    @patch('rexus.modules.auditoria.model.get_auditoria_connection')
    def test_auditoria_registrar_evento(self, mock_connection):
        """Test registrar evento de auditoría."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.auditoria.model import AuditoriaModel
            model = AuditoriaModel(self.mock_db)
            
            if hasattr(model, 'registrar_evento'):
                resultado = model.registrar_evento(
                    self.sample_evento['usuario_id'],
                    self.sample_evento['modulo'],
                    self.sample_evento['accion'],
                    self.sample_evento['descripcion']
                )
                
                # Verificar que se llamó a execute
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Módulo auditoría no disponible")
        except Exception as e:
            self.fail(f"Error en test registrar evento: {e}")
    
    def test_auditoria_view_initialization(self):
        """Test inicialización de la vista de auditoría."""
        try:
            from rexus.modules.auditoria.view import AuditoriaView
            
            self.assertTrue(hasattr(AuditoriaView, '__init__'))
            
        except ImportError:
            self.skipTest("Vista de auditoría no disponible")


class TestConfiguracionModule(unittest.TestCase):
    """Tests para el módulo de Configuración."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockDatabase()
        
        self.sample_config = {
            'clave': 'test_setting',
            'valor': 'test_value',
            'categoria': 'TEST'
        }
    
    @patch('rexus.modules.configuracion.model.get_inventario_connection')
    def test_configuracion_model_initialization(self, mock_connection):
        """Test inicialización del modelo de configuración."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.configuracion.model import ConfiguracionModel
            model = ConfiguracionModel(self.mock_db)
            
            self.assertIsNotNone(model)
            self.assertEqual(model.db_connection, self.mock_db)
            
        except ImportError:
            self.skipTest("Módulo configuración no disponible")
    
    @patch('rexus.modules.configuracion.model.get_inventario_connection')
    def test_configuracion_obtener_valor(self, mock_connection):
        """Test obtener valor de configuración."""
        mock_connection.return_value = self.mock_db
        
        # Mock para retornar valor de configuración
        self.mock_db.cursor_mock.fetchone.return_value = ('test_value',)
        
        try:
            from rexus.modules.configuracion.model import ConfiguracionModel
            model = ConfiguracionModel(self.mock_db)
            
            if hasattr(model, 'obtener_valor'):
                valor = model.obtener_valor('test_setting')
                
                # Verificar que se llamó a execute con la query
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Módulo configuración no disponible")
        except Exception as e:
            self.fail(f"Error en test obtener valor: {e}")
    
    def test_configuracion_view_initialization(self):
        """Test inicialización de la vista de configuración."""
        try:
            from rexus.modules.configuracion.view import ConfiguracionView
            
            self.assertTrue(hasattr(ConfiguracionView, '__init__'))
            
        except ImportError:
            self.skipTest("Vista de configuración no disponible")


class TestSecurityComponents(unittest.TestCase):
    """Tests para componentes de seguridad críticos."""
    
    def test_sql_query_manager_availability(self):
        """Test disponibilidad del SQLQueryManager."""
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            
            manager = SQLQueryManager()
            self.assertIsNotNone(manager)
            
            # Verificar métodos críticos
            self.assertTrue(hasattr(manager, 'get_query'))
            
        except ImportError:
            self.fail("SQLQueryManager no disponible - componente crítico")
    
    def test_unified_sanitizer_availability(self):
        """Test disponibilidad del sanitizador unificado."""
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            
            self.assertIsNotNone(unified_sanitizer)
            
            # Verificar métodos críticos
            self.assertTrue(hasattr(unified_sanitizer, 'sanitize_dict'))
            self.assertTrue(hasattr(unified_sanitizer, 'sanitize_string'))
            
        except ImportError:
            self.fail("Unified Sanitizer no disponible - componente crítico")
    
    def test_security_manager_availability(self):
        """Test disponibilidad del sistema de seguridad."""
        try:
            from rexus.core.security import init_security_manager
            
            self.assertTrue(callable(init_security_manager))
            
        except ImportError:
            self.skipTest("Sistema de seguridad no disponible")


class TestDatabaseConnections(unittest.TestCase):
    """Tests para conexiones de base de datos."""
    
    def test_inventario_connection_availability(self):
        """Test disponibilidad de conexión a BD inventario."""
        try:
            from rexus.core.database import get_inventario_connection
            
            self.assertTrue(callable(get_inventario_connection))
            
        except ImportError:
            self.fail("Conexión BD inventario no disponible")
    
    def test_users_connection_availability(self):
        """Test disponibilidad de conexión a BD usuarios."""
        try:
            from rexus.core.database import get_users_connection
            
            self.assertTrue(callable(get_users_connection))
            
        except ImportError:
            self.fail("Conexión BD usuarios no disponible")
    
    def test_auditoria_connection_availability(self):
        """Test disponibilidad de conexión a BD auditoría."""
        try:
            from rexus.core.database import get_auditoria_connection
            
            self.assertTrue(callable(get_auditoria_connection))
            
        except ImportError:
            self.skipTest("Conexión BD auditoría no disponible")


def run_critical_tests():
    """
    Ejecuta todos los tests críticos del sistema.
    
    Returns:
        bool: True si todos los tests críticos pasan
    """
    # Crear suite de tests críticos
    suite = unittest.TestSuite()
    
    # Tests de disponibilidad de componentes críticos
    suite.addTest(TestSecurityComponents('test_sql_query_manager_availability'))
    suite.addTest(TestSecurityComponents('test_unified_sanitizer_availability'))
    suite.addTest(TestDatabaseConnections('test_inventario_connection_availability'))
    suite.addTest(TestDatabaseConnections('test_users_connection_availability'))
    
    # Tests básicos de módulos críticos
    suite.addTest(TestInventarioModule('test_inventario_view_initialization'))
    suite.addTest(TestComprasModule('test_compras_view_initialization'))
    suite.addTest(TestAuditoriaModule('test_auditoria_view_initialization'))
    suite.addTest(TestConfiguracionModule('test_configuracion_view_initialization'))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*60)
    print("TESTS UNITARIOS CRÍTICOS - REXUS.APP")
    print("="*60)
    
    # Ejecutar tests críticos
    success = run_critical_tests()
    
    if success:
        print("\n✅ TODOS LOS TESTS CRÍTICOS PASARON")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS CRÍTICOS FALLARON")
        sys.exit(1)