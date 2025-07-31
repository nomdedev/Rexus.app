"""
Tests completos para MantenimientoModel.
Cubre todas las funcionalidades, edge cases, validaciones y flujos de integración.
"""

# from rexus.modules.mantenimiento.model import MantenimientoModel # Movido a sección try/except
class TestMantenimientoModelComplete(unittest.TestCase):
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import unittest
from unittest.mock import MagicMock, Mock, call, patch

    def setUp(self):
        """Configuración para cada test."""
        self.mock_db = Mock()
        self.modelo = MantenimientoModel(self.mock_db)

        # Datos de prueba típicos
        self.datos_mantenimiento = (
            'vehiculo',  # tipo_objeto
            1,          # id_objeto
            'preventivo', # tipo_mantenimiento
            '2025-06-29', # fecha_realizacion
            'Juan Pérez', # realizado_por
            'Cambio de aceite', # observaciones
            'firma123'   # firma_digital
        )

        self.datos_checklist = (
            1,  # id_mantenimiento
            'Revisar aceite', # item
            'Completado', # estado
            'Aceite en buen estado' # observaciones
        )

    def tearDown(self):
        """Limpieza después de cada test."""
        self.mock_db.reset_mock()


class TestMantenimientoModelBasic(TestMantenimientoModelComplete):
    """Tests básicos de funcionamiento del modelo."""

    def test_init_mantenimiento_model(self):
        """Test inicialización del modelo."""
        # Arrange & Act
        modelo = MantenimientoModel(self.mock_db)

        # Assert
        self.assertEqual(modelo.db, self.mock_db)
        self.assertIsInstance(modelo, MantenimientoModel)

    def test_obtener_herramientas_success(self):
        """Test obtener herramientas exitoso."""
        # Arrange
        herramientas_mock = [
            {'id': 1, 'nombre': 'Taladro', 'estado': 'Activo'},
            {'id': 2, 'nombre': 'Martillo', 'estado': 'Mantenimiento'}
        ]
        self.mock_db.ejecutar_query.return_value = herramientas_mock

        # Act
        resultado = self.modelo.obtener_herramientas()

        # Assert
        self.assertEqual(resultado, herramientas_mock)
        self.mock_db.ejecutar_query.assert_called_once_with("SELECT * FROM herramientas")

    def test_obtener_vehiculos_success(self):
        """Test obtener vehículos exitoso."""
        # Arrange
        vehiculos_mock = [
            {'id': 1, 'placa': 'ABC-123', 'modelo': 'Ford Transit', 'estado': 'Activo'},
            {'id': 2, 'placa': 'XYZ-789', 'modelo': 'Chevrolet NPR', 'estado': 'Taller'}
        ]
        self.mock_db.ejecutar_query.return_value = vehiculos_mock

        # Act
        resultado = self.modelo.obtener_vehiculos()

        # Assert
        self.assertEqual(resultado, vehiculos_mock)
        self.mock_db.ejecutar_query.assert_called_once_with("SELECT * FROM vehiculos")

    def test_registrar_mantenimiento_success(self):
        """Test registro de mantenimiento exitoso."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        resultado = self.modelo.registrar_mantenimiento(self.datos_mantenimiento)

        # Assert
        self.assertTrue(resultado)
        expected_query = """
        INSERT INTO mantenimientos (tipo_objeto, id_objeto, tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.mock_db.ejecutar_query.assert_called_once()
        call_args = self.mock_db.ejecutar_query.call_args
        self.assertIn("INSERT INTO mantenimientos", call_args[0][0])
        self.assertEqual(call_args[0][1], self.datos_mantenimiento)

    def test_agregar_mantenimiento_alias(self):
        """Test alias agregar_mantenimiento funciona correctamente."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        resultado = self.modelo.agregar_mantenimiento(self.datos_mantenimiento)

        # Assert
        self.assertTrue(resultado)
        self.mock_db.ejecutar_query.assert_called_once()

    def test_obtener_mantenimientos_success(self):
        """Test obtener todos los mantenimientos exitoso."""
        # Arrange
        mantenimientos_mock = [
            {'id': 1, 'tipo_objeto': 'vehiculo', 'fecha_realizacion': '2025-06-29'},
            {'id': 2, 'tipo_objeto': 'herramienta', 'fecha_realizacion': '2025-06-28'}
        ]
        self.mock_db.ejecutar_query.return_value = mantenimientos_mock

        # Act
        resultado = self.modelo.obtener_mantenimientos()

        # Assert
        self.assertEqual(resultado, mantenimientos_mock)
        self.mock_db.ejecutar_query.assert_called_once_with("SELECT * FROM mantenimientos")

    def test_obtener_checklist_success(self):
        """Test obtener checklist por ID de mantenimiento."""
        # Arrange
        checklist_mock = [
            {'id': 1, 'item': 'Revisar aceite', 'estado': 'Completado'},
            {'id': 2, 'item': 'Revisar frenos', 'estado': 'Pendiente'}
        ]
        self.mock_db.ejecutar_query.return_value = checklist_mock
        id_mantenimiento = 1

        # Act
        resultado = self.modelo.obtener_checklist(id_mantenimiento)

        # Assert
        self.assertEqual(resultado, checklist_mock)
        self.mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM checklists_mantenimiento WHERE id_mantenimiento = ?",
            (id_mantenimiento,)
        )

    def test_agregar_checklist_item_success(self):
        """Test agregar item de checklist exitoso."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        self.modelo.agregar_checklist_item(self.datos_checklist)

        # Assert
        expected_query = """
        INSERT INTO checklists_mantenimiento (id_mantenimiento, item, estado, observaciones)
        VALUES (?, ?, ?, ?)
        """
        self.mock_db.ejecutar_query.assert_called_once()
        call_args = self.mock_db.ejecutar_query.call_args
        self.assertIn("INSERT INTO checklists_mantenimiento", call_args[0][0])
        self.assertEqual(call_args[0][1], self.datos_checklist)


class TestMantenimientoModelEdgeCases(TestMantenimientoModelComplete):
    """Tests de casos límite y errores."""

    def test_obtener_herramientas_empty_result(self):
        """Test obtener herramientas cuando no hay resultados."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []

        # Act
        resultado = self.modelo.obtener_herramientas()

        # Assert
        self.assertEqual(resultado, [])
        self.mock_db.ejecutar_query.assert_called_once()

    def test_obtener_vehiculos_none_result(self):
        """Test obtener vehículos cuando el resultado es None."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        resultado = self.modelo.obtener_vehiculos()

        # Assert
        self.assertIsNone(resultado)
        self.mock_db.ejecutar_query.assert_called_once()

    def test_registrar_mantenimiento_db_error(self):
        """Test registro de mantenimiento con error de base de datos."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = Exception("Error de BD")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.modelo.registrar_mantenimiento(self.datos_mantenimiento)

        self.assertIn("Error de BD", str(context.exception))
        self.mock_db.ejecutar_query.assert_called_once()

    def test_obtener_checklist_id_inexistente(self):
        """Test obtener checklist con ID inexistente."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []
        id_inexistente = 999

        # Act
        resultado = self.modelo.obtener_checklist(id_inexistente)

        # Assert
        self.assertEqual(resultado, [])
        self.mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM checklists_mantenimiento WHERE id_mantenimiento = ?",
            (id_inexistente,)
        )

    def test_agregar_checklist_item_datos_incompletos(self):
        """Test agregar item checklist con datos incompletos."""
        # Arrange
        datos_incompletos = (1, '', 'Completado')  # Item vacío
        self.mock_db.ejecutar_query.side_effect = Exception("Constraint violation")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.modelo.agregar_checklist_item(datos_incompletos)

        self.assertIn("Constraint violation", str(context.exception))

    def test_registrar_mantenimiento_datos_none(self):
        """Test registro con datos None."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = Exception("NULL constraint")

        # Act & Assert
        with self.assertRaises(Exception):
            self.modelo.registrar_mantenimiento(None)

    def test_obtener_checklist_parametro_none(self):
        """Test obtener checklist con parámetro None."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []

        # Act
        resultado = self.modelo.obtener_checklist(None)

        # Assert
        self.assertEqual(resultado, [])
        self.mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM checklists_mantenimiento WHERE id_mantenimiento = ?",
            (None,)
        )


class TestMantenimientoModelIntegration(TestMantenimientoModelComplete):
    """Tests de integración y flujos complejos."""

    def test_flujo_completo_mantenimiento_con_checklist(self):
        """Test flujo completo: registrar mantenimiento y agregar items checklist."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = [
            None,  # Registro mantenimiento
            [{'id': 1, 'tipo_objeto': 'vehiculo'}],  # Obtener mantenimientos
            None,  # Agregar item 1
            None,  # Agregar item 2
            [  # Obtener checklist
                {'id': 1, 'item': 'Revisar aceite', 'estado': 'Completado'},
                {'id': 2, 'item': 'Revisar frenos', 'estado': 'Completado'}
            ]
        ]

        # Act
        # 1. Registrar mantenimiento
        resultado_registro = self.modelo.registrar_mantenimiento(self.datos_mantenimiento)

        # 2. Verificar registro
        mantenimientos = self.modelo.obtener_mantenimientos()

        # 3. Agregar items checklist
        item1 = (1, 'Revisar aceite', 'Completado', 'OK')
        item2 = (1, 'Revisar frenos', 'Completado', 'OK')
        self.modelo.agregar_checklist_item(item1)
        self.modelo.agregar_checklist_item(item2)

        # 4. Verificar checklist
        checklist = self.modelo.obtener_checklist(1)

        # Assert
        self.assertTrue(resultado_registro)
        self.assertEqual(len(mantenimientos), 1)
        self.assertEqual(len(checklist), 2)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 5)

    def test_multiples_mantenimientos_mismo_objeto(self):
        """Test registrar múltiples mantenimientos para el mismo objeto."""
        # Arrange
        mantenimiento1 = ('vehiculo', 1, 'preventivo', '2025-06-29', 'Juan', 'Cambio aceite', 'firma1')
        mantenimiento2 = ('vehiculo', 1, 'correctivo', '2025-07-15', 'María', 'Reparar frenos', 'firma2')

        self.mock_db.ejecutar_query.side_effect = [None, None]  # Ambos registros exitosos

        # Act
        resultado1 = self.modelo.registrar_mantenimiento(mantenimiento1)
        resultado2 = self.modelo.registrar_mantenimiento(mantenimiento2)

        # Assert
        self.assertTrue(resultado1)
        self.assertTrue(resultado2)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 2)

    def test_obtener_datos_relacionados_herramientas_vehiculos(self):
        """Test obtener herramientas y vehículos para formularios."""
        # Arrange
        herramientas_mock = [{'id': 1, 'nombre': 'Taladro'}]
        vehiculos_mock = [{'id': 1, 'placa': 'ABC-123'}]

        self.mock_db.ejecutar_query.side_effect = [herramientas_mock, vehiculos_mock]

        # Act
        herramientas = self.modelo.obtener_herramientas()
        vehiculos = self.modelo.obtener_vehiculos()

        # Assert
        self.assertEqual(herramientas, herramientas_mock)
        self.assertEqual(vehiculos, vehiculos_mock)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 2)

    @patch('modules.mantenimiento.model.pd')
    def test_integracion_con_pandas_preparacion_datos(self, mock_pd):
        """Test preparación de datos para exportación con pandas."""
        # Arrange
        mantenimientos_data = [
            {'id': 1, 'tipo_objeto': 'vehiculo', 'fecha_realizacion': '2025-06-29'},
            {'id': 2, 'tipo_objeto': 'herramienta', 'fecha_realizacion': '2025-06-28'}
        ]
        self.mock_db.ejecutar_query.return_value = mantenimientos_data
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df

        # Act
        mantenimientos = self.modelo.obtener_mantenimientos()
        # Simular creación de DataFrame usando el pandas mockeado
        if mantenimientos:
            df = mock_pd.DataFrame(mantenimientos)

        # Assert
        self.assertEqual(mantenimientos, mantenimientos_data)
        # Verificar que pandas fue mockeado correctamente
        mock_pd.DataFrame.assert_called_once_with(mantenimientos_data)
        self.assertEqual(df, mock_df)

    def test_validacion_integridad_datos_mantenimiento(self):
        """Test validación de integridad de datos en registros."""
        # Arrange
        datos_completos = ('vehiculo', 1, 'preventivo', '2025-06-29', 'Juan', 'OK', 'firma')
        datos_minimos = ('herramienta', 2, 'correctivo', '2025-06-30', 'María', '', '')

        self.mock_db.ejecutar_query.side_effect = [None, None]

        # Act
        resultado1 = self.modelo.registrar_mantenimiento(datos_completos)
        resultado2 = self.modelo.registrar_mantenimiento(datos_minimos)

        # Assert
        self.assertTrue(resultado1)
        self.assertTrue(resultado2)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 2)


class TestMantenimientoModelErrorHandling(TestMantenimientoModelComplete):
    """Tests específicos de manejo de errores."""

    def test_db_connection_none(self):
        """Test comportamiento con conexión de BD None."""
        # Arrange & Act
        modelo = MantenimientoModel(None)

        # Assert
        self.assertIsNone(modelo.db)

        # Verificar que falla al intentar usar métodos
        with self.assertRaises(AttributeError):
            modelo.obtener_herramientas()

    def test_ejecutar_query_exception_handling(self):
        """Test manejo de excepciones en ejecutar_query."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = Exception("Connection lost")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.modelo.obtener_herramientas()

        self.assertIn("Connection lost", str(context.exception))

    def test_timeout_database_operations(self):
        """Test comportamiento con timeout en operaciones de BD."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = TimeoutError("Database timeout")

        # Act & Assert
        with self.assertRaises(TimeoutError):
            self.modelo.obtener_mantenimientos()

    def test_sql_injection_protection(self):
        """Test protección contra inyección SQL usando parámetros."""
        # Arrange
        id_malicioso = "1; DROP TABLE mantenimientos; --"
        self.mock_db.ejecutar_query.return_value = []

        # Act
        resultado = self.modelo.obtener_checklist(id_malicioso)

        # Assert
        self.assertEqual(resultado, [])
        # Verificar que se usa query parametrizada
        call_args = self.mock_db.ejecutar_query.call_args
        self.assertIn("?", call_args[0][0])  # Query con placeholder
        self.assertEqual(call_args[0][1], (id_malicioso,))  # Parámetro separado


if __name__ == '__main__':
    unittest.main()
