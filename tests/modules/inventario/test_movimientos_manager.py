"""
Tests unitarios para MovimientosManager del módulo inventario.
Valida funcionalidad de movimientos de stock y auditoría.
"""

import unittest
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Configurar path antes de imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rexus.modules.inventario.submodules.movimientos_manager import MovimientosManager


class TestMovimientosManager(unittest.TestCase):
    """Test suite para MovimientosManager."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Mock de dependencias
        self.mock_db = Mock()
        self.mock_sanitizer = Mock()
        
        # Configurar mocks
        self.mock_sanitizer.sanitize_text.return_value = "texto_limpio"
        self.mock_sanitizer.sanitize_number.return_value = 10
        
        # Crear instancia del manager
        with patch('rexus.modules.inventario.submodules.movimientos_manager.DatabaseManager', return_value=self.mock_db), \
             patch('rexus.modules.inventario.submodules.movimientos_manager.DataSanitizer', return_value=self.mock_sanitizer):
            self.manager = MovimientosManager()
    
    def test_inicializacion(self):
        """Test de inicialización correcta del manager."""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.db)
        self.assertIsNotNone(self.manager.sanitizer)
    
    def test_registrar_entrada_exitosa(self):
        """Test de registro exitoso de entrada de stock."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        self.mock_db.get_scalar.return_value = 1
        
        # Datos de entrada
        datos_entrada = {
            'producto_id': 1,
            'cantidad': 50,
            'motivo': 'Compra',
            'observaciones': 'Entrada inicial'
        }
        
        # Ejecutar
        resultado = self.manager.registrar_entrada(datos_entrada)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_registrar_salida_exitosa(self):
        """Test de registro exitoso de salida de stock."""
        # Configurar mock - stock suficiente
        self.mock_db.get_scalar.return_value = 100  # Stock actual
        self.mock_db.execute_query.return_value = True
        
        # Datos de salida
        datos_salida = {
            'producto_id': 1,
            'cantidad': 25,
            'motivo': 'Venta',
            'observaciones': 'Venta cliente'
        }
        
        # Ejecutar
        resultado = self.manager.registrar_salida(datos_salida)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_registrar_salida_stock_insuficiente(self):
        """Test de validación de stock insuficiente."""
        # Configurar mock - stock insuficiente
        self.mock_db.get_scalar.return_value = 10  # Stock actual menor
        
        # Datos de salida que exceden stock
        datos_salida = {
            'producto_id': 1,
            'cantidad': 25,
            'motivo': 'Venta'
        }
        
        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError):
            self.manager.registrar_salida(datos_salida)
    
    def test_obtener_stock_actual(self):
        """Test de obtención de stock actual."""
        # Mock de stock
        self.mock_db.get_scalar.return_value = 150
        
        # Ejecutar
        stock = self.manager.obtener_stock_actual(1)
        
        # Verificar
        self.assertEqual(stock, 150)
        self.mock_db.get_scalar.assert_called_once()
    
    def test_obtener_historial_movimientos(self):
        """Test de obtención de historial de movimientos."""
        # Mock de historial
        movimientos_mock = [
            {
                'id': 1,
                'tipo': 'ENTRADA',
                'cantidad': 50,
                'fecha': datetime.now(),
                'motivo': 'Compra'
            },
            {
                'id': 2,
                'tipo': 'SALIDA',
                'cantidad': 25,
                'fecha': datetime.now(),
                'motivo': 'Venta'
            }
        ]
        self.mock_db.fetch_all.return_value = movimientos_mock
        
        # Ejecutar
        historial = self.manager.obtener_historial_movimientos(1)
        
        # Verificar
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0]['tipo'], 'ENTRADA')
        self.assertEqual(historial[1]['tipo'], 'SALIDA')
    
    def test_calcular_stock_desde_movimientos(self):
        """Test de cálculo de stock desde movimientos."""
        # Mock de movimientos para cálculo
        movimientos_calculo = [
            {'tipo': 'ENTRADA', 'cantidad': 100},
            {'tipo': 'ENTRADA', 'cantidad': 50},
            {'tipo': 'SALIDA', 'cantidad': 30},
            {'tipo': 'SALIDA', 'cantidad': 20}
        ]
        self.mock_db.fetch_all.return_value = movimientos_calculo
        
        # Ejecutar
        stock_calculado = self.manager.calcular_stock_desde_movimientos(1)
        
        # Verificar (100 + 50 - 30 - 20 = 100)
        self.assertEqual(stock_calculado, 100)
    
    def test_validar_movimiento_datos_validos(self):
        """Test de validación con datos válidos."""
        datos_validos = {
            'producto_id': 1,
            'cantidad': 25,
            'motivo': 'Transferencia'
        }
        
        # Ejecutar (no debe lanzar excepción)
        resultado = self.manager._validar_datos_movimiento(datos_validos)
        self.assertTrue(resultado)
    
    def test_validar_movimiento_datos_invalidos(self):
        """Test de validación con datos inválidos."""
        # Cantidad negativa
        datos_invalidos = {
            'producto_id': 1,
            'cantidad': -5,
            'motivo': 'Test'
        }
        
        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError):
            self.manager._validar_datos_movimiento(datos_invalidos)
    
    def test_obtener_productos_bajo_stock(self):
        """Test de obtención de productos con stock bajo."""
        # Mock de productos bajo stock
        productos_bajo_stock = [
            {'id': 1, 'codigo': 'PROD001', 'stock_actual': 5, 'stock_minimo': 10},
            {'id': 2, 'codigo': 'PROD002', 'stock_actual': 2, 'stock_minimo': 15}
        ]
        self.mock_db.fetch_all.return_value = productos_bajo_stock
        
        # Ejecutar
        resultado = self.manager.obtener_productos_bajo_stock()
        
        # Verificar
        self.assertEqual(len(resultado), 2)
        self.assertTrue(all(p['stock_actual'] < p['stock_minimo'] for p in resultado))
    
    def test_crear_auditoria_movimiento(self):
        """Test de creación de auditoría para movimiento."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        
        # Datos de auditoría
        datos_auditoria = {
            'movimiento_id': 1,
            'usuario': 'test_user',
            'accion': 'REGISTRO_ENTRADA',
            'detalles': 'Entrada de mercancía'
        }
        
        # Ejecutar
        resultado = self.manager.crear_auditoria_movimiento(datos_auditoria)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_obtener_resumen_movimientos_periodo(self):
        """Test de obtención de resumen por período."""
        # Mock de resumen
        resumen_mock = {
            'total_entradas': 5,
            'total_salidas': 3,
            'cantidad_entrada': 250,
            'cantidad_salida': 150,
            'saldo_neto': 100
        }
        self.mock_db.fetch_one.return_value = resumen_mock
        
        # Ejecutar
        fecha_inicio = '2025-01-01'
        fecha_fin = '2025-01-31'
        resumen = self.manager.obtener_resumen_movimientos_periodo(fecha_inicio, fecha_fin)
        
        # Verificar
        self.assertEqual(resumen['total_entradas'], 5)
        self.assertEqual(resumen['saldo_neto'], 100)
    
    def test_ajustar_stock_directo(self):
        """Test de ajuste directo de stock."""
        # Configurar mock
        self.mock_db.execute_query.return_value = True
        self.mock_db.get_scalar.return_value = 1
        
        # Datos de ajuste
        datos_ajuste = {
            'producto_id': 1,
            'stock_nuevo': 75,
            'motivo': 'Inventario físico',
            'usuario': 'admin'
        }
        
        # Ejecutar
        resultado = self.manager.ajustar_stock_directo(datos_ajuste)
        
        # Verificar
        self.assertTrue(resultado)
        self.mock_db.execute_query.assert_called()
    
    def test_manejo_errores_base_datos(self):
        """Test de manejo de errores de base de datos."""
        # Configurar mock para error
        self.mock_db.execute_query.side_effect = Exception("Error BD")
        
        datos_entrada = {
            'producto_id': 1,
            'cantidad': 10,
            'motivo': 'Test error'
        }
        
        # Ejecutar y verificar manejo de error
        resultado = self.manager.registrar_entrada(datos_entrada)
        self.assertFalse(resultado)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        self.mock_db = None
        self.mock_sanitizer = None
        self.manager = None


class TestMovimientosManagerIntegracion(unittest.TestCase):
    """Tests de integración para MovimientosManager."""
    
    @patch('rexus.modules.inventario.submodules.movimientos_manager.DatabaseManager')
    @patch('rexus.modules.inventario.submodules.movimientos_manager.DataSanitizer')
    def test_flujo_completo_movimientos(self, mock_sanitizer_class, mock_db_class):
        """Test de flujo completo de movimientos."""
        # Configurar mocks
        mock_db = Mock()
        mock_sanitizer = Mock()
        mock_db_class.return_value = mock_db
        mock_sanitizer_class.return_value = mock_sanitizer
        
        mock_sanitizer.sanitize_text.side_effect = lambda x: x
        mock_sanitizer.sanitize_number.side_effect = lambda x: x
        
        # Simular comportamiento secuencial
        mock_db.execute_query.return_value = True
        mock_db.get_scalar.side_effect = [
            0,    # Stock inicial
            50,   # Stock después de entrada
            25    # Stock después de salida
        ]
        
        manager = MovimientosManager()
        
        # 1. Registrar entrada
        entrada = {
            'producto_id': 1,
            'cantidad': 50,
            'motivo': 'Compra inicial'
        }
        resultado_entrada = manager.registrar_entrada(entrada)
        self.assertTrue(resultado_entrada)
        
        # 2. Verificar stock
        stock_actual = manager.obtener_stock_actual(1)
        self.assertEqual(stock_actual, 50)
        
        # 3. Registrar salida
        salida = {
            'producto_id': 1,
            'cantidad': 25,
            'motivo': 'Venta'
        }
        resultado_salida = manager.registrar_salida(salida)
        self.assertTrue(resultado_salida)
        
        # 4. Verificar stock final
        stock_final = manager.obtener_stock_actual(1)
        self.assertEqual(stock_final, 25)


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
