# -*- coding: utf-8 -*-
"""
Tests unitarios para el modelo de Vidrios
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.modules.vidrios.model import VidriosModel


class TestVidriosModel(unittest.TestCase):
    """Tests para el modelo de vidrios."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(db_connection=self.mock_db)

    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self.model, 'db_connection'):
            self.model.db_connection = None

    def test_init_model(self):
        """Test de inicialización del modelo."""
        model = VidriosModel()
        self.assertIsNotNone(model)
        
        # Con conexión
        mock_db = Mock()
        model_with_db = VidriosModel(db_connection=mock_db)
        self.assertEqual(model_with_db.db_connection, mock_db)

    @patch('rexus.modules.vidrios.model.data_sanitizer')
    def test_crear_vidrio(self, mock_sanitizer):
        """Test de creación de vidrio."""
        # Mock sanitizer
        if mock_sanitizer:
            mock_sanitizer.sanitize_dict.return_value = {
                'tipo': 'Laminado',
                'espesor': 6.0,
                'ancho': 1200,
                'alto': 800,
                'obra_id': 1
            }
        
        # Mock cursor
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        self.mock_db.commit.return_value = None
        
        datos = {
            'tipo': 'Laminado',
            'espesor': 6.0,
            'ancho': 1200,
            'alto': 800,
            'obra_id': 1
        }
        
        result = self.model.crear_vidrio(datos)
        
        # Verificar que se llamó a los métodos esperados
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_crear_vidrio_sin_db(self):
        """Test de creación sin conexión a BD."""
        model_sin_db = VidriosModel(db_connection=None)
        
        datos = {
            'tipo': 'Laminado',
            'espesor': 6.0
        }
        
        result = model_sin_db.crear_vidrio(datos)
        self.assertFalse(result)

    def test_obtener_vidrios(self):
        """Test de obtención de vidrios."""
        # Mock cursor y resultados
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular datos de respuesta
        mock_cursor.fetchall.return_value = [
            (1, 'Laminado', 6.0, 1200, 800, 1, 'Obra 1', 'Activo'),
            (2, 'Templado', 8.0, 1500, 1000, 2, 'Obra 2', 'Activo')
        ]
        
        mock_cursor.description = [
            ('id',), ('tipo',), ('espesor',), ('ancho',), ('alto',), 
            ('obra_id',), ('obra_nombre',), ('estado',)
        ]
        
        result = self.model.obtener_vidrios()
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_obtener_vidrio_por_id(self):
        """Test de obtención de vidrio por ID."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular respuesta
        mock_cursor.fetchone.return_value = (
            1, 'Laminado', 6.0, 1200, 800, 1, 'Obra Test', 'Activo'
        )
        
        mock_cursor.description = [
            ('id',), ('tipo',), ('espesor',), ('ancho',), ('alto',), 
            ('obra_id',), ('obra_nombre',), ('estado',)
        ]
        
        result = self.model.obtener_vidrio_por_id(1)
        
        self.assertIsNotNone(result)
        mock_cursor.execute.assert_called()

    def test_actualizar_vidrio(self):
        """Test de actualización de vidrio."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        datos = {
            'tipo': 'Templado',
            'espesor': 8.0,
            'ancho': 1500
        }
        
        result = self.model.actualizar_vidrio(1, datos)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_eliminar_vidrio(self):
        """Test de eliminación de vidrio."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = self.model.eliminar_vidrio(1)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_obtener_vidrios_por_obra(self):
        """Test de obtención de vidrios por obra."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            (1, 'Laminado', 6.0, 1200, 800, 1, 'Obra Test', 'Activo')
        ]
        
        result = self.model.obtener_vidrios_por_obra(1)
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_calcular_area_vidrio(self):
        """Test de cálculo de área."""
        # Test con valores válidos
        area = self.model.calcular_area_vidrio(1200, 800)
        self.assertEqual(area, 0.96)  # 1.2 * 0.8 metros cuadrados
        
        # Test con valores inválidos
        area = self.model.calcular_area_vidrio(0, 800)
        self.assertEqual(area, 0)

    def test_obtener_tipos_vidrio(self):
        """Test de obtención de tipos de vidrio."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            ('Laminado',), ('Templado',), ('Común',), ('Insulado',)
        ]
        
        result = self.model.obtener_tipos_vidrio()
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_validar_datos_vidrio(self):
        """Test de validación de datos."""
        # Datos válidos
        datos_validos = {
            'tipo': 'Laminado',
            'espesor': 6.0,
            'ancho': 1200,
            'alto': 800
        }
        
        result = self.model.validar_datos_vidrio(datos_validos)
        self.assertTrue(result)
        
        # Datos inválidos - sin tipo
        datos_invalidos = {
            'espesor': 6.0,
            'ancho': 1200,
            'alto': 800
        }
        
        result = self.model.validar_datos_vidrio(datos_invalidos)
        self.assertFalse(result)

    def test_obtener_estadisticas(self):
        """Test de obtención de estadísticas."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular respuesta de estadísticas
        mock_cursor.fetchone.return_value = (25, 125.5, 8.5, 2.5)
        
        result = self.model.obtener_estadisticas()
        
        self.assertIsInstance(result, dict)
        self.assertIn('total_vidrios', result)
        mock_cursor.execute.assert_called()

    def test_manejo_errores_db(self):
        """Test de manejo de errores de base de datos."""
        # Simular error de BD
        self.mock_db.cursor.side_effect = Exception("Database error")
        
        datos = {
            'tipo': 'Laminado',
            'espesor': 6.0
        }
        
        result = self.model.crear_vidrio(datos)
        self.assertFalse(result)

    @patch('rexus.modules.vidrios.model.data_sanitizer')
    def test_sanitizacion_datos(self, mock_sanitizer):
        """Test de sanitización de datos."""
        if mock_sanitizer:
            mock_sanitizer.sanitize_dict.return_value = {
                'tipo': 'Safe Type',
                'observaciones': 'Safe Notes'
            }
        
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        datos = {
            'tipo': '<script>alert("xss")</script>',
            'observaciones': 'DROP TABLE vidrios;'
        }
        
        self.model.crear_vidrio(datos)
        
        # Verificar que se usaron datos sanitizados
        mock_cursor.execute.assert_called()


if __name__ == '__main__':
    unittest.main()