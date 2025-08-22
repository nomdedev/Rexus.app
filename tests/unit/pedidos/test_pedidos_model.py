# -*- coding: utf-8 -*-
"""
Tests unitarios para el modelo de Pedidos
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.modules.pedidos.model import PedidosModel


class TestPedidosModel(unittest.TestCase):
    """Tests para el modelo de pedidos."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = PedidosModel(db_connection=self.mock_db)

    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self.model, 'db_connection'):
            self.model.db_connection = None

    def test_init_model(self):
        """Test de inicialización del modelo."""
        model = PedidosModel()
        self.assertIsNotNone(model)
        
        # Con conexión
        mock_db = Mock()
        model_with_db = PedidosModel(db_connection=mock_db)
        self.assertEqual(model_with_db.db_connection, mock_db)

    @patch('rexus.modules.pedidos.model.unified_sanitizer')
    def test_crear_pedido(self, mock_sanitizer):
        """Test de creación de pedido."""
        # Mock sanitizer
        mock_sanitizer.sanitize_dict.return_value = {
            'numero_pedido': 'PED-001',
            'cliente': 'Test Cliente',
            'estado': 'PENDIENTE',
            'productos': []
        }
        
        # Mock cursor
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        self.mock_db.commit.return_value = None
        
        datos = {
            'numero_pedido': 'PED-001',
            'cliente': 'Test Cliente',
            'estado': 'PENDIENTE'
        }
        
        result = self.model.crear_pedido(datos)
        
        # Verificar que se llamó a los métodos esperados
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_crear_pedido_sin_db(self):
        """Test de creación sin conexión a BD."""
        model_sin_db = PedidosModel(db_connection=None)
        
        datos = {
            'numero_pedido': 'PED-001',
            'cliente': 'Test Cliente'
        }
        
        result = model_sin_db.crear_pedido(datos)
        self.assertFalse(result)

    def test_obtener_pedidos(self):
        """Test de obtención de pedidos."""
        # Mock cursor y resultados
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular datos de respuesta
        mock_cursor.fetchall.return_value = [
            (1, 'PED-001', 'Cliente 1', 'PENDIENTE', '2025-08-22', 1000.0),
            (2, 'PED-002', 'Cliente 2', 'APROBADO', '2025-08-22', 2000.0)
        ]
        
        mock_cursor.description = [
            ('id',), ('numero_pedido',), ('cliente',), ('estado',), 
            ('fecha_creacion',), ('total',)
        ]
        
        result = self.model.obtener_pedidos()
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_obtener_pedido_por_id(self):
        """Test de obtención de pedido por ID."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular respuesta
        mock_cursor.fetchone.return_value = (
            1, 'PED-001', 'Cliente Test', 'PENDIENTE', '2025-08-22', 1000.0
        )
        
        mock_cursor.description = [
            ('id',), ('numero_pedido',), ('cliente',), ('estado',), 
            ('fecha_creacion',), ('total',)
        ]
        
        result = self.model.obtener_pedido_por_id(1)
        
        self.assertIsNotNone(result)
        mock_cursor.execute.assert_called()

    def test_actualizar_pedido(self):
        """Test de actualización de pedido."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        datos = {
            'cliente': 'Cliente Actualizado',
            'estado': 'APROBADO'
        }
        
        result = self.model.actualizar_pedido(1, datos)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_eliminar_pedido(self):
        """Test de eliminación de pedido."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = self.model.eliminar_pedido(1)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_cambiar_estado_pedido(self):
        """Test de cambio de estado."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = self.model.cambiar_estado_pedido(1, 'APROBADO')
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_obtener_estadisticas(self):
        """Test de obtención de estadísticas."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular respuesta de estadísticas
        mock_cursor.fetchone.return_value = (10, 5, 3, 2, 50000.0)
        
        result = self.model.obtener_estadisticas()
        
        self.assertIsInstance(result, dict)
        mock_cursor.execute.assert_called()

    def test_validar_datos_pedido(self):
        """Test de validación de datos."""
        # Datos válidos
        datos_validos = {
            'numero_pedido': 'PED-001',
            'cliente': 'Cliente Test',
            'estado': 'PENDIENTE'
        }
        
        result = self.model.validar_datos_pedido(datos_validos)
        self.assertTrue(result)
        
        # Datos inválidos - sin número de pedido
        datos_invalidos = {
            'cliente': 'Cliente Test',
            'estado': 'PENDIENTE'
        }
        
        result = self.model.validar_datos_pedido(datos_invalidos)
        self.assertFalse(result)

    def test_obtener_pedidos_por_estado(self):
        """Test de obtención de pedidos por estado."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            (1, 'PED-001', 'Cliente 1', 'PENDIENTE', '2025-08-22', 1000.0)
        ]
        
        result = self.model.obtener_pedidos_por_estado('PENDIENTE')
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_manejo_errores_db(self):
        """Test de manejo de errores de base de datos."""
        # Simular error de BD
        self.mock_db.cursor.side_effect = Exception("Database error")
        
        datos = {
            'numero_pedido': 'PED-001',
            'cliente': 'Cliente Test'
        }
        
        result = self.model.crear_pedido(datos)
        self.assertFalse(result)

    @patch('rexus.modules.pedidos.model.unified_sanitizer')
    def test_sanitizacion_datos(self, mock_sanitizer):
        """Test de sanitización de datos."""
        mock_sanitizer.sanitize_dict.return_value = {
            'numero_pedido': 'PED-001',
            'cliente': 'Safe Cliente'
        }
        
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        datos = {
            'numero_pedido': 'PED-001',
            'cliente': '<script>alert("xss")</script>'
        }
        
        self.model.crear_pedido(datos)
        
        # Verificar que se usaron datos sanitizados
        mock_cursor.execute.assert_called()


if __name__ == '__main__':
    unittest.main()