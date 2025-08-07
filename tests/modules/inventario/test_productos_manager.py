"""
Tests unitarios para ProductosManager del módulo inventario.
Valida funcionalidad de CRUD, validaciones y generación de códigos QR.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

# Configurar path antes de imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rexus.modules.inventario.submodules.productos_manager import ProductosManager


class TestProductosManager(unittest.TestCase):
    """Test suite para ProductosManager."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Mock de conexión de base de datos
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor
        
        # Configurar comportamiento del cursor
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [('id',), ('codigo',), ('descripcion',)]
        
        # Crear instancia del manager con mock
        with patch('rexus.modules.inventario.submodules.productos_manager.SQLQueryManager'), \
             patch('rexus.modules.inventario.submodules.productos_manager.DataSanitizer') as mock_sanitizer_class:
            
            mock_sanitizer = Mock()
            mock_sanitizer.sanitize_text.return_value = "texto_limpio"
            mock_sanitizer_class.return_value = mock_sanitizer
            
            self.manager = ProductosManager(self.mock_db_connection)
    
    def test_inicializacion(self):
        """Test de inicialización correcta del manager."""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.db_connection)
        self.assertIsNotNone(self.manager.sql_manager)
        self.assertIsNotNone(self.manager.data_sanitizer)
    
    def test_agregar_producto_exitoso(self):
        """Test de adición exitosa de producto."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        self.mock_db.get_scalar.return_value = 1
        
        # Datos de prueba
        datos_producto = {
            'codigo': 'TEST001',
            'descripcion': 'Producto de prueba',
            'precio': 100.50,
            'categoria': 'Test'
        }
        
        # Ejecutar
        resultado = self.manager.agregar_producto(datos_producto)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
        self.mock_sanitizer.sanitize_text.assert_called()
    
    def test_agregar_producto_datos_invalidos(self):
        """Test de validación con datos inválidos."""
        # Datos inválidos (sin código)
        datos_invalidos = {
            'descripcion': 'Producto sin código',
            'precio': 100.50
        }
        
        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError):
            self.manager.agregar_producto(datos_invalidos)
    
    def test_obtener_producto_por_id_existente(self):
        """Test de obtención de producto existente."""
        # Mock de resultado
        producto_mock = {
            'id': 1,
            'codigo': 'TEST001',
            'descripcion': 'Producto test',
            'precio': 100.50
        }
        self.mock_db.fetch_one.return_value = producto_mock
        
        # Ejecutar
        resultado = self.manager.obtener_producto_por_id(1)
        
        # Verificar
        self.assertEqual(resultado, producto_mock)
        self.mock_db.fetch_one.assert_called_once()
    
    def test_obtener_producto_por_id_inexistente(self):
        """Test de obtención de producto inexistente."""
        # Mock sin resultado
        self.mock_db.fetch_one.return_value = None
        
        # Ejecutar
        resultado = self.manager.obtener_producto_por_id(999)
        
        # Verificar
        self.assertIsNone(resultado)
    
    def test_actualizar_producto_exitoso(self):
        """Test de actualización exitosa de producto."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        
        # Datos de actualización
        datos_actualizacion = {
            'descripcion': 'Descripción actualizada',
            'precio': 150.75
        }
        
        # Ejecutar
        resultado = self.manager.actualizar_producto(1, datos_actualizacion)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_eliminar_producto_exitoso(self):
        """Test de eliminación exitosa de producto."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        
        # Ejecutar
        resultado = self.manager.eliminar_producto(1)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_validar_codigo_producto_unico(self):
        """Test de validación de código único."""
        # Mock sin resultados (código único)
        self.mock_db.fetch_one.return_value = None
        
        # Ejecutar
        resultado = self.manager.validar_codigo_unico('NUEVO001')
        
        # Verificar
        self.assertTrue(resultado)
    
    def test_validar_codigo_producto_duplicado(self):
        """Test de validación de código duplicado."""
        # Mock con resultado (código duplicado)
        self.mock_db.fetch_one.return_value = {'id': 1}
        
        # Ejecutar
        resultado = self.manager.validar_codigo_unico('DUPLICADO001')
        
        # Verificar
        self.assertFalse(resultado)
    
    @patch('qrcode.make')
    def test_generar_qr_exitoso(self, mock_qr):
        """Test de generación exitosa de código QR."""
        # Configurar mock
        mock_img = Mock()
        mock_qr.return_value = mock_img
        
        # Ejecutar
        with tempfile.TemporaryDirectory() as temp_dir:
            ruta_qr = os.path.join(temp_dir, 'test_qr.png')
            resultado = self.manager.generar_qr_producto('TEST001', ruta_qr)
            
            # Verificar
            self.assertTrue(resultado)
            mock_qr.assert_called_once_with('TEST001')
            mock_img.save.assert_called_once_with(ruta_qr)
    
    def test_buscar_productos_por_criterio(self):
        """Test de búsqueda de productos."""
        # Mock de resultados
        productos_mock = [
            {'id': 1, 'codigo': 'TEST001', 'descripcion': 'Producto 1'},
            {'id': 2, 'codigo': 'TEST002', 'descripcion': 'Producto 2'}
        ]
        self.mock_db.fetch_all.return_value = productos_mock
        
        # Ejecutar
        resultado = self.manager.buscar_productos('TEST')
        
        # Verificar
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado, productos_mock)
    
    def test_validacion_datos_producto_completa(self):
        """Test de validación completa de datos."""
        # Datos válidos
        datos_validos = {
            'codigo': 'TEST001',
            'descripcion': 'Producto válido',
            'precio': 100.50,
            'categoria': 'Categoria Test'
        }
        
        # Ejecutar
        resultado = self.manager._validar_datos_producto(datos_validos)
        
        # Verificar que no lance excepción
        self.assertTrue(resultado)
    
    def test_validacion_datos_producto_invalida(self):
        """Test de validación con datos inválidos."""
        # Datos inválidos (precio negativo)
        datos_invalidos = {
            'codigo': 'TEST001',
            'descripcion': 'Producto inválido',
            'precio': -10.0,
            'categoria': 'Test'
        }
        
        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError):
            self.manager._validar_datos_producto(datos_invalidos)
    
    def test_manejo_errores_base_datos(self):
        """Test de manejo de errores de base de datos."""
        # Configurar mock para lanzar excepción
        self.mock_db.execute_query.side_effect = Exception("Error de BD")
        
        # Datos de prueba
        datos_producto = {
            'codigo': 'ERROR001',
            'descripcion': 'Producto error',
            'precio': 100.50
        }
        
        # Ejecutar y verificar que maneja el error
        resultado = self.manager.agregar_producto(datos_producto)
        self.assertFalse(resultado)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        # Limpiar mocks y referencias
        self.mock_db = None
        self.mock_sanitizer = None
        self.manager = None


class TestProductosManagerIntegracion(unittest.TestCase):
    """Tests de integración para ProductosManager."""
    
    @patch('rexus.modules.inventario.submodules.productos_manager.DatabaseManager')
    @patch('rexus.modules.inventario.submodules.productos_manager.DataSanitizer')
    def test_flujo_completo_producto(self, mock_sanitizer_class, mock_db_class):
        """Test de flujo completo: crear, leer, actualizar, eliminar."""
        # Configurar mocks
        mock_db = Mock()
        mock_sanitizer = Mock()
        mock_db_class.return_value = mock_db
        mock_sanitizer_class.return_value = mock_sanitizer
        
        # Configurar comportamiento
        mock_sanitizer.sanitize_text.side_effect = lambda x: x
        mock_sanitizer.sanitize_number.side_effect = lambda x: x
        
        # Simular IDs incrementales
        mock_db.get_scalar.side_effect = [1, 2]
        mock_db.execute_query.return_value = True
        mock_db.fetch_one.side_effect = [
            None,  # Validación código único
            {'id': 1, 'codigo': 'INT001', 'descripcion': 'Producto integración'},  # Obtener producto
            {'id': 1, 'codigo': 'INT001', 'descripcion': 'Producto actualizado'}   # Producto actualizado
        ]
        
        # Crear manager
        manager = ProductosManager()
        
        # 1. Crear producto
        datos_producto = {
            'codigo': 'INT001',
            'descripcion': 'Producto integración',
            'precio': 200.00,
            'categoria': 'Integración'
        }
        
        resultado_crear = manager.agregar_producto(datos_producto)
        self.assertTrue(resultado_crear)
        
        # 2. Leer producto
        producto = manager.obtener_producto_por_id(1)
        self.assertIsNotNone(producto)
        self.assertEqual(producto['codigo'], 'INT001')
        
        # 3. Actualizar producto
        datos_actualizacion = {'descripcion': 'Producto actualizado'}
        resultado_actualizar = manager.actualizar_producto(1, datos_actualizacion)
        self.assertTrue(resultado_actualizar)
        
        # 4. Eliminar producto
        resultado_eliminar = manager.eliminar_producto(1)
        self.assertTrue(resultado_eliminar)


if __name__ == '__main__':
    # Configurar nivel de logging para tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
