#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests para HerrajesController - Versión robusta y compatible con CI/CD.
Arquitectura robusta con mocks, signals compatibles y sin QTest.
Todas las clases y métodos son mockeados para evitar dependencias del mundo real.
"""

# Agregar paths al sistema para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Simular imports críticos con mocks
sys.modules['PyQt6'] = Mock()
sys.modules['PyQt6.QtWidgets'] = Mock()
sys.modules['PyQt6.QtCore'] = Mock()
sys.modules['PyQt6.QtGui'] = Mock()

# Mocks para evitar imports reales problemáticos
with patch.dict('sys.modules', {
    'modules.usuarios.model': Mock(),
    'modules.auditoria.model': Mock(),
    'modules.obras.model': Mock(),
    'modules.contabilidad.model': Mock(),
    'core.logger': Mock(),
}):
class TestHerrajesControllerSetup(unittest.TestCase):
    """Tests para setup e inicialización del controlador."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        # Mock de QMessageBox para evitar errores de PyQt6
        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    def test_inicializacion_controlador(self):
        """Test que el controlador se inicializa correctamente."""
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertEqual(self.controller.view, self.mock_view)
        self.assertEqual(self.controller.usuario_actual, self.usuario_test)
        self.assertEqual(self.controller.usuarios_model, self.mock_usuarios_model)
        self.assertEqual(self.controller.db_connection, self.mock_db)
        self.assertIsNotNone(self.controller.auditoria_model)

    def test_inicializacion_sin_usuario(self):
        """Test inicialización sin usuario actual."""
        with patch('modules.herrajes.controller.QMessageBox'):
            controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=None
            )
        self.assertIsNone(controller.usuario_actual)


class TestHerrajesControllerAgregarMaterial(unittest.TestCase):
    """Tests para funcionalidad de agregar material."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        # Configurar view inputs
        self.mock_view.nombre_input.text.return_value = 'Material Test'
        self.mock_view.cantidad_input.text.return_value = '10'
        self.mock_view.proveedor_input.text.return_value = 'Proveedor Test'

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    @patch('modules.herrajes.controller.permiso_auditoria_herrajes')
    def test_agregar_material_exitoso(self, mock_decorador):
        """Test agregar material con datos válidos."""
        # Configurar decorador para que permita la acción
        mock_decorador.return_value = lambda func: func

        # Configurar mocks
        self.mock_model.verificar_material_existente.return_value = False

        # Ejecutar
        self.controller.agregar_material()

        # Verificar
        self.mock_model.verificar_material_existente.assert_called_once_with('Material Test')
        self.mock_model.agregar_material.assert_called_once_with(('Material Test', '10', 'Proveedor Test'))
        self.mock_view.label.setText.assert_called_with("Material agregado exitosamente.")

    @patch('modules.herrajes.controller.permiso_auditoria_herrajes')
    def test_agregar_material_existente(self, mock_decorador):
        """Test agregar material que ya existe."""
        # Configurar decorador para que permita la acción
        mock_decorador.return_value = lambda func: func

        # Configurar mocks
        self.mock_model.verificar_material_existente.return_value = True

        with patch('modules.herrajes.controller.QMessageBox.warning') as mock_warning:
            # Ejecutar
            self.controller.agregar_material()

            # Verificar
            mock_warning.assert_called_once()
            self.mock_model.agregar_material.assert_not_called()

    @patch('modules.herrajes.controller.permiso_auditoria_herrajes')
    def test_agregar_material_campos_vacios(self, mock_decorador):
        """Test agregar material con campos vacíos."""
        # Configurar decorador para que permita la acción
        mock_decorador.return_value = lambda func: func

        # Configurar view con campos vacíos
        self.mock_view.nombre_input.text.return_value = ''

        # Ejecutar
        self.controller.agregar_material()

        # Verificar
        self.mock_view.label.setText.assert_called_with("Por favor, complete todos los campos.")
        self.mock_model.agregar_material.assert_not_called()

    @patch('modules.herrajes.controller.permiso_auditoria_herrajes')
    def test_agregar_material_error_excepcion(self, mock_decorador):
        """Test manejo de excepción al agregar material."""
        # Configurar decorador para que permita la acción
        mock_decorador.return_value = lambda func: func

        # Configurar mocks
        self.mock_model.verificar_material_existente.return_value = False
        self.mock_model.agregar_material.side_effect = Exception("Error de base de datos")

        # Ejecutar
        self.controller.agregar_material()

        # Verificar
        self.mock_view.label.setText.assert_called_with("Error al agregar material: Error de base de datos")


class TestHerrajesControllerReservas(unittest.TestCase):
    """Tests para funcionalidad de reservas de herrajes."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    @patch('modules.obras.model.ObrasModel')
    def test_reservar_herraje_obra_existente(self, mock_obras_model_class):
        """Test reservar herraje para obra existente."""
        # Configurar mock del modelo de obras
        mock_obras_instance = Mock()
        mock_obras_instance.existe_obra_por_id.return_value = True
        mock_obras_model_class.return_value = mock_obras_instance

        # Configurar mock del modelo principal
        self.mock_model.reservar_herraje.return_value = True

        # Ejecutar
        resultado = self.controller.reservar_herraje(self.usuario_test, 1, 1, 5)

        # Verificar
        self.assertTrue(resultado)
        mock_obras_instance.existe_obra_por_id.assert_called_once_with(1)
        self.mock_model.reservar_herraje.assert_called_once_with(self.usuario_test, 1, 1, 5)

    @patch('modules.obras.model.ObrasModel')
    def test_reservar_herraje_obra_inexistente(self, mock_obras_model_class):
        """Test reservar herraje para obra inexistente."""
        # Configurar mock del modelo de obras
        mock_obras_instance = Mock()
        mock_obras_instance.existe_obra_por_id.return_value = False
        mock_obras_model_class.return_value = mock_obras_instance

        # Ejecutar
        resultado = self.controller.reservar_herraje(self.usuario_test, 999, 1, 5)

        # Verificar
        self.assertFalse(resultado)
        mock_obras_instance.existe_obra_por_id.assert_called_once_with(999)
        self.mock_model.reservar_herraje.assert_not_called()


class TestHerrajesControllerPedidos(unittest.TestCase):
    """Tests para funcionalidad de pedidos."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    def test_obtener_pedidos_por_obra_exitoso(self):
        """Test obtener pedidos por obra exitosamente."""
        # Configurar mock
        pedidos_mock = [
            (1, 'Material 1', 10, 'Pendiente'),
            (2, 'Material 2', 5, 'Completado')
        ]
        self.mock_model.obtener_pedidos_por_obra.return_value = pedidos_mock

        # Ejecutar
        pedidos = self.controller.obtener_pedidos_por_obra(1)

        # Verificar
        self.assertEqual(pedidos, pedidos_mock)
        self.mock_model.obtener_pedidos_por_obra.assert_called_once_with(1)

    def test_obtener_pedidos_por_obra_error(self):
        """Test manejo de error al obtener pedidos."""
        # Configurar mock para lanzar excepción
        self.mock_model.obtener_pedidos_por_obra.side_effect = Exception("Error de BD")

        # Ejecutar
        pedidos = self.controller.obtener_pedidos_por_obra(1)

        # Verificar
        self.assertEqual(pedidos, [])

    def test_obtener_estado_pedidos_por_obra_exitoso(self):
        """Test obtener estado de pedidos exitosamente."""
        # Configurar mock
        self.mock_model.obtener_estado_pedido_por_obra.return_value = 'Completado'

        # Ejecutar
        estado = self.controller.obtener_estado_pedidos_por_obra(1)

        # Verificar
        self.assertEqual(estado, 'Completado')
        self.mock_model.obtener_estado_pedido_por_obra.assert_called_once_with(1)

    def test_obtener_estado_pedidos_por_obra_error(self):
        """Test manejo de error al obtener estado."""
        # Configurar mock para lanzar excepción
        self.mock_model.obtener_estado_pedido_por_obra.side_effect = Exception("Error de BD")

        # Ejecutar
        estado = self.controller.obtener_estado_pedidos_por_obra(1)

        # Verificar
        self.assertEqual(estado, 'error')

    def test_refrescar_pedidos_exitoso(self):
        """Test refrescar pedidos exitosamente."""
        # Configurar mocks
        pedidos_mock = [(1, 'Material 1', 10)]
        self.mock_model.obtener_pedidos.return_value = pedidos_mock

        # Resetear el mock para evitar llamadas previas del setUp
        self.mock_model.obtener_pedidos.reset_mock()

        # Ejecutar
        self.controller.refrescar_pedidos()

        # Verificar
        self.mock_model.obtener_pedidos.assert_called_once()

    def test_refrescar_pedidos_error(self):
        """Test manejo de error al refrescar pedidos."""
        # Resetear el mock para evitar llamadas previas del setUp
        self.mock_model.obtener_pedidos.reset_mock()

        # Configurar mock para lanzar excepción
        self.mock_model.obtener_pedidos.side_effect = Exception("Error de BD")

        # Ejecutar (no debe lanzar excepción)
        self.controller.refrescar_pedidos()

        # Verificar que se intentó obtener pedidos
        self.mock_model.obtener_pedidos.assert_called_once()


class TestHerrajesControllerValidacion(unittest.TestCase):
    """Tests para funcionalidades de validación."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    def test_validar_obra_existente_exitoso(self):
        """Test validación de obra existente."""
        # Configurar mock
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = {'id': 1, 'nombre': 'Obra Test'}

        # Ejecutar
        resultado = self.controller.validar_obra_existente(1, mock_obras_model)

        # Verificar
        self.assertTrue(resultado)
        mock_obras_model.obtener_obra_por_id.assert_called_once_with(1)

    def test_validar_obra_existente_no_existe(self):
        """Test validación de obra inexistente."""
        # Configurar mock
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = None

        # Ejecutar
        resultado = self.controller.validar_obra_existente(1, mock_obras_model)

        # Verificar
        self.assertFalse(resultado)

    def test_validar_obra_existente_id_nulo(self):
        """Test validación con ID nulo."""
        # Configurar mock
        mock_obras_model = Mock()

        # Ejecutar
        resultado = self.controller.validar_obra_existente(None, mock_obras_model)

        # Verificar
        self.assertFalse(resultado)
        mock_obras_model.obtener_obra_por_id.assert_not_called()

    def test_validar_obra_existente_error_excepcion(self):
        """Test manejo de excepción en validación."""
        # Configurar mock
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.side_effect = Exception("Error de BD")

        # Ejecutar
        resultado = self.controller.validar_obra_existente(1, mock_obras_model)

        # Verificar
        self.assertFalse(resultado)

    def test_guardar_pedido_herrajes_obra_valida(self):
        """Test guardar pedido con obra válida."""
        # Configurar datos y mocks
        datos = {'id_obra': 1, 'material': 'Test', 'cantidad': 10}
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = {'id': 1}

        # Ejecutar
        self.controller.guardar_pedido_herrajes(datos, mock_obras_model)

        # Verificar
        self.mock_model.guardar_pedido_herrajes.assert_called_once_with(datos)

    def test_guardar_pedido_herrajes_obra_invalida(self):
        """Test guardar pedido con obra inválida."""
        # Configurar datos y mocks
        datos = {'id_obra': 999, 'material': 'Test', 'cantidad': 10}
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = None

        # Ejecutar
        self.controller.guardar_pedido_herrajes(datos, mock_obras_model)

        # Verificar que no se guardó el pedido
        self.mock_model.guardar_pedido_herrajes.assert_not_called()


class TestHerrajesControllerPagos(unittest.TestCase):
    """Tests para funcionalidades de pagos."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_exitoso(self, mock_contabilidad_model_class):
        """Test registrar pago de pedido exitosamente."""
        # Configurar mocks
        mock_contabilidad_instance = Mock()
        mock_contabilidad_model_class.return_value = mock_contabilidad_instance

        pedidos_mock = [(1, 'Material 1', 10, 'Pendiente')]
        self.mock_model.obtener_pedidos_por_obra.return_value = pedidos_mock

        # Ejecutar
        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=1,
            monto=1000.0,
            fecha='2024-01-01',
            usuario=self.usuario_test
        )

        # Verificar
        self.assertTrue(resultado)
        mock_contabilidad_instance.registrar_pago_pedido.assert_called_once()

    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_sin_pedidos(self, mock_contabilidad_model_class):
        """Test registrar pago sin pedidos existentes."""
        # Configurar mocks
        mock_contabilidad_instance = Mock()
        mock_contabilidad_model_class.return_value = mock_contabilidad_instance

        self.mock_model.obtener_pedidos_por_obra.return_value = []

        # Ejecutar
        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=1,
            monto=1000.0,
            fecha='2024-01-01',
            usuario=self.usuario_test
        )

        # Verificar
        self.assertFalse(resultado)
        mock_contabilidad_instance.registrar_pago_pedido.assert_not_called()

    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_error(self, mock_contabilidad_model_class):
        """Test manejo de error al registrar pago."""
        # Configurar mocks
        mock_contabilidad_instance = Mock()
        mock_contabilidad_instance.registrar_pago_pedido.side_effect = Exception("Error de BD")
        mock_contabilidad_model_class.return_value = mock_contabilidad_instance

        pedidos_mock = [(1, 'Material 1', 10, 'Pendiente')]
        self.mock_model.obtener_pedidos_por_obra.return_value = pedidos_mock

        # Ejecutar
        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=1,
            monto=1000.0,
            fecha='2024-01-01',
            usuario=self.usuario_test
        )

        # Verificar
        self.assertFalse(resultado)


class TestHerrajesControllerAuditoria(unittest.TestCase):
    """Tests para funcionalidades de auditoría."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    def test_registrar_evento_auditoria_exitoso(self):
        """Test registrar evento de auditoría exitosamente."""
        # Configurar mock
        mock_auditoria = Mock()
        self.controller.auditoria_model = mock_auditoria

        # Ejecutar
        self.controller._registrar_evento_auditoria("test_action", "detalle test", "exito")

        # Verificar
        mock_auditoria.registrar_evento.assert_called_once_with(
            1, 'herrajes', 'test_action', 'test_action - detalle test - exito', '127.0.0.1'
        )

    def test_registrar_evento_auditoria_error(self):
        """Test manejo de error en auditoría."""
        # Configurar mock
        mock_auditoria = Mock()
        mock_auditoria.registrar_evento.side_effect = Exception("Error auditoría")
        self.controller.auditoria_model = mock_auditoria

        # Ejecutar (no debe lanzar excepción)
        self.controller._registrar_evento_auditoria("test_action")

        # Verificar que se intentó registrar
        mock_auditoria.registrar_evento.assert_called_once()

    def test_registrar_evento_auditoria_sin_usuario(self):
        """Test registrar evento sin usuario actual."""
        # Configurar controlador sin usuario
        self.controller.usuario_actual = None
        mock_auditoria = Mock()
        self.controller.auditoria_model = mock_auditoria

        # Ejecutar
        self.controller._registrar_evento_auditoria("test_action")

        # Verificar
        mock_auditoria.registrar_evento.assert_called_once_with(
            None, 'herrajes', 'test_action', 'test_action', ''
        )


class TestHerrajesControllerValidacionesEspeciales(unittest.TestCase):
    """Tests para validaciones especiales y casos edge."""

    def setUp(self):
        """Configuración para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuarios_model = Mock()
        self.usuario_test = {
            'id': 1,
            'username': 'test_user',
            'ip': '127.0.0.1'
        }

        with patch('modules.herrajes.controller.QMessageBox'):
            self.controller = HerrajesController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_test
            )

    def test_guardar_pedido_herrajes_sin_validacion_obras(self):
        """Test guardar pedido sin modelo de obras (compatibilidad)."""
        # Configurar datos
        datos = {'material': 'Test', 'cantidad': 10}

        # Ejecutar
        self.controller.guardar_pedido_herrajes(datos, obras_model=None)

        # Verificar que se guardó sin validación
        self.mock_model.guardar_pedido_herrajes.assert_called_once_with(datos)

    def test_guardar_pedido_herrajes_error_interno(self):
        """Test manejo de error interno al guardar pedido."""
        # Configurar datos y mocks
        datos = {'id_obra': 1, 'material': 'Test', 'cantidad': 10}
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = {'id': 1}
        self.mock_model.guardar_pedido_herrajes.side_effect = Exception("Error de BD")

        # Ejecutar (debe manejar la excepción internamente)
        with self.assertRaises(Exception):
            self.controller.guardar_pedido_herrajes(datos, mock_obras_model)


if __name__ == '__main__':
    # Configurar logging para tests
    logging.basicConfig(level=logging.WARNING)

    # Ejecutar tests
    unittest.main(verbosity=2)

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from rexus.modules.herrajes.controller import HerrajesController, PermisoAuditoria
