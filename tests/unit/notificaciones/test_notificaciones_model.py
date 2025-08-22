# -*- coding: utf-8 -*-
"""
Tests unitarios para el modelo de Notificaciones
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.modules.notificaciones.model import NotificacionesModel, TipoNotificacion


class TestNotificacionesModel(unittest.TestCase):
    """Tests para el modelo de notificaciones."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = NotificacionesModel(db_connection=self.mock_db)

    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self.model, 'db_connection'):
            self.model.db_connection = None

    def test_init_model(self):
        """Test de inicialización del modelo."""
        model = NotificacionesModel()
        self.assertIsNotNone(model)
        
        # Con conexión
        mock_db = Mock()
        model_with_db = NotificacionesModel(db_connection=mock_db)
        self.assertEqual(model_with_db.db_connection, mock_db)

    def test_tipo_notificacion_enum(self):
        """Test de enum TipoNotificacion."""
        self.assertEqual(TipoNotificacion.INFO.value, "info")
        self.assertEqual(TipoNotificacion.WARNING.value, "warning")
        self.assertEqual(TipoNotificacion.ERROR.value, "error")
        self.assertEqual(TipoNotificacion.SUCCESS.value, "success")

    @patch('rexus.modules.notificaciones.model.unified_sanitizer')
    def test_crear_notificacion(self, mock_sanitizer):
        """Test de creación de notificación."""
        # Mock sanitizer
        mock_sanitizer.sanitize_dict.return_value = {
            'titulo': 'Test Notification',
            'mensaje': 'Test message',
            'tipo': 'info',
            'usuario_id': 1
        }
        
        # Mock cursor
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        self.mock_db.commit.return_value = None
        
        datos = {
            'titulo': 'Test Notification',
            'mensaje': 'Test message',
            'tipo': 'info',
            'usuario_id': 1
        }
        
        result = self.model.crear_notificacion(datos)
        
        # Verificar que se llamó a los métodos esperados
        mock_sanitizer.sanitize_dict.assert_called_once()
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_crear_notificacion_sin_db(self):
        """Test de creación sin conexión a BD."""
        model_sin_db = NotificacionesModel(db_connection=None)
        
        datos = {
            'titulo': 'Test',
            'mensaje': 'Test message',
            'tipo': 'info'
        }
        
        result = model_sin_db.crear_notificacion(datos)
        self.assertFalse(result)

    @patch('rexus.modules.notificaciones.model.unified_sanitizer')
    def test_obtener_notificaciones(self, mock_sanitizer):
        """Test de obtención de notificaciones."""
        # Mock cursor y resultados
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular datos de respuesta
        mock_cursor.fetchall.return_value = [
            (1, 'Título 1', 'Mensaje 1', 'info', '2025-08-22', 1, False),
            (2, 'Título 2', 'Mensaje 2', 'warning', '2025-08-22', 1, True)
        ]
        
        mock_cursor.description = [
            ('id',), ('titulo',), ('mensaje',), ('tipo',), 
            ('fecha_creacion',), ('usuario_id',), ('leida',)
        ]
        
        result = self.model.obtener_notificaciones(usuario_id=1)
        
        self.assertIsInstance(result, list)
        mock_cursor.execute.assert_called()

    def test_marcar_como_leida(self):
        """Test de marcar notificación como leída."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = self.model.marcar_como_leida(1)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_eliminar_notificacion(self):
        """Test de eliminación de notificación."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        result = self.model.eliminar_notificacion(1)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        self.mock_db.commit.assert_called_once()

    def test_obtener_estadisticas(self):
        """Test de obtención de estadísticas."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        # Simular respuesta de estadísticas
        mock_cursor.fetchone.return_value = (10, 5, 3, 2)
        
        result = self.model.obtener_estadisticas(usuario_id=1)
        
        self.assertIsInstance(result, dict)
        self.assertIn('total', result)
        mock_cursor.execute.assert_called()

    def test_validar_datos_notificacion(self):
        """Test de validación de datos."""
        # Datos válidos
        datos_validos = {
            'titulo': 'Test',
            'mensaje': 'Test message',
            'tipo': 'info'
        }
        
        result = self.model.validar_datos_notificacion(datos_validos)
        self.assertTrue(result)
        
        # Datos inválidos - sin título
        datos_invalidos = {
            'mensaje': 'Test message',
            'tipo': 'info'
        }
        
        result = self.model.validar_datos_notificacion(datos_invalidos)
        self.assertFalse(result)

    @patch('rexus.modules.notificaciones.model.unified_sanitizer')
    def test_sanitizacion_datos(self, mock_sanitizer):
        """Test de sanitización de datos."""
        mock_sanitizer.sanitize_dict.return_value = {
            'titulo': 'Safe Title',
            'mensaje': 'Safe Message'
        }
        
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        datos = {
            'titulo': '<script>alert("xss")</script>',
            'mensaje': 'DROP TABLE notifications;'
        }
        
        self.model.crear_notificacion(datos)
        
        # Verificar que se llamó al sanitizer
        mock_sanitizer.sanitize_dict.assert_called_once()

    def test_manejo_errores_db(self):
        """Test de manejo de errores de base de datos."""
        # Simular error de BD
        self.mock_db.cursor.side_effect = Exception("Database error")
        
        datos = {
            'titulo': 'Test',
            'mensaje': 'Test message',
            'tipo': 'info'
        }
        
        result = self.model.crear_notificacion(datos)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()