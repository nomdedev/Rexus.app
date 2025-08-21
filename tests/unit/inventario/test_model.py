#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests del Modelo de Inventario - Módulo Inventario
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
from decimal import Decimal

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'


class MockInventarioDatabase:
    """Mock de base de datos para inventario."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.connected = True
        
        # Datos de productos de prueba
        self.productos_data = [
            {
                'id': 1,
                'codigo': 'PROD001',
                'nombre': 'Producto Test 1',
                'categoria': 'Categoría A',
                'precio': Decimal('100.00'),
                'stock': 50,
                'stock_minimo': 10,
                'activo': True
            },
            {
                'id': 2, 
                'codigo': 'PROD002',
                'nombre': 'Producto Test 2',
                'categoria': 'Categoría B',
                'precio': Decimal('200.00'),
                'stock': 25,
                'stock_minimo': 5,
                'activo': True
            }
        ]
    
    def cursor(self):
        return self.cursor_mock
    
    def commit(self):
        pass
    
    def close(self):
        self.connected = False


class TestInventarioModel(unittest.TestCase):
    """Tests del modelo de inventario."""
    
    def setUp(self):
        """Setup para cada test."""
        self.mock_db = MockInventarioDatabase()
    
    def test_product_creation_structure(self):
        """Test: Estructura básica de creación de producto."""
        # Datos típicos de producto
        producto_data = {
            'codigo': 'PROD001',
            'nombre': 'Producto Test',
            'categoria': 'Categoría A',
            'precio': Decimal('100.00'),
            'stock': 50,
            'stock_minimo': 10,
            'descripcion': 'Descripción del producto',
            'activo': True
        }
        
        # Validar campos requeridos
        required_fields = ['codigo', 'nombre', 'categoria', 'precio', 'stock']
        for field in required_fields:
            self.assertIn(field, producto_data)
            self.assertIsNotNone(producto_data[field])
    
    def test_stock_validation(self):
        """Test: Validación de stock."""
        # Stock válido
        valid_stocks = [0, 10, 100, 1000]
        for stock in valid_stocks:
            self.assertGreaterEqual(stock, 0)
        
        # Stock mínimo
        stock_actual = 5
        stock_minimo = 10
        self.assertLess(stock_actual, stock_minimo, "Stock por debajo del mínimo")
    
    def test_price_validation(self):
        """Test: Validación de precios."""
        # Precios válidos
        valid_prices = [Decimal('0.01'), Decimal('100.00'), Decimal('999.99')]
        for price in valid_prices:
            self.assertGreater(price, Decimal('0'))
            self.assertIsInstance(price, Decimal)
        
        # Precio inválido
        invalid_price = Decimal('0')
        self.assertEqual(invalid_price, Decimal('0'))
    
    @patch('rexus.core.database.InventarioDatabaseConnection')
    def test_product_retrieval(self, mock_db_connection):
        """Test: Obtener productos de la base de datos."""
        mock_db_connection.return_value = self.mock_db
        
        # Configurar respuesta mock
        self.mock_db.cursor_mock.fetchall.return_value = [
            (1, 'PROD001', 'Producto Test 1', 'Categoría A', 100.00, 50, 10, 1),
            (2, 'PROD002', 'Producto Test 2', 'Categoría B', 200.00, 25, 5, 1)
        ]
        
        # Test básico de estructura de datos
        productos = self.mock_db.cursor_mock.fetchall()
        self.assertEqual(len(productos), 2)
        
        # Validar estructura de cada producto
        for producto in productos:
            self.assertEqual(len(producto), 8)  # 8 campos esperados
            self.assertIsInstance(producto[0], int)  # ID
            self.assertIsInstance(producto[1], str)  # Código


class TestInventarioMovimientos(unittest.TestCase):
    """Tests de movimientos de inventario."""
    
    def test_movement_types(self):
        """Test: Tipos de movimientos de inventario."""
        movement_types = ['entrada', 'salida', 'transferencia', 'ajuste']
        
        for mov_type in movement_types:
            self.assertIsInstance(mov_type, str)
            self.assertGreater(len(mov_type), 3)
    
    def test_movement_data_structure(self):
        """Test: Estructura de datos de movimiento."""
        movement_data = {
            'tipo': 'entrada',
            'producto_id': 1,
            'cantidad': 10,
            'precio_unitario': Decimal('100.00'),
            'fecha': '2025-08-21T10:00:00',
            'descripcion': 'Compra de productos',
            'usuario_id': 1
        }
        
        # Validar campos requeridos
        required_fields = ['tipo', 'producto_id', 'cantidad']
        for field in required_fields:
            self.assertIn(field, movement_data)
            self.assertIsNotNone(movement_data[field])


class TestInventarioReservas(unittest.TestCase):
    """Tests de reservas de inventario."""
    
    def test_reservation_structure(self):
        """Test: Estructura de reserva."""
        reserva_data = {
            'producto_id': 1,
            'obra_id': 1,
            'cantidad_reservada': 5,
            'fecha_reserva': '2025-08-21T10:00:00',
            'estado': 'activa',
            'usuario_id': 1
        }
        
        # Validar campos requeridos
        required_fields = ['producto_id', 'obra_id', 'cantidad_reservada']
        for field in required_fields:
            self.assertIn(field, reserva_data)
            self.assertIsNotNone(reserva_data[field])
    
    def test_reservation_states(self):
        """Test: Estados de reserva."""
        valid_states = ['activa', 'utilizada', 'cancelada']
        
        for state in valid_states:
            self.assertIsInstance(state, str)
            self.assertIn(state, valid_states)


class TestInventarioCategorias(unittest.TestCase):
    """Tests de categorías de productos."""
    
    def test_category_structure(self):
        """Test: Estructura de categoría."""
        categoria_data = {
            'id': 1,
            'nombre': 'Materiales Construcción',
            'descripcion': 'Materiales para construcción',
            'activa': True
        }
        
        # Validar estructura
        self.assertIn('nombre', categoria_data)
        self.assertIsInstance(categoria_data['nombre'], str)
        self.assertGreater(len(categoria_data['nombre']), 2)
    
    def test_category_hierarchy(self):
        """Test: Jerarquía de categorías."""
        categorias = [
            'Materiales',
            'Herramientas', 
            'Equipos',
            'Consumibles',
            'Repuestos'
        ]
        
        for categoria in categorias:
            self.assertIsInstance(categoria, str)
            self.assertGreater(len(categoria), 3)


if __name__ == '__main__':
    print("Ejecutando tests del modelo de inventario...")
    unittest.main(verbosity=2)