"""
Tests completos para HerrajesModel.
Cubre todas las funcionalidades, edge cases, validaciones y flujos de integración.
"""

# from rexus.modules.herrajes.model import HerrajesModel # Movido a sección try/except
class TestHerrajesModelComplete(unittest.TestCase):
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import unittest
from unittest.mock import MagicMock, Mock, call, patch

    def setUp(self):
        """Configuración para cada test."""
        # Crear mock de base de datos
        self.mock_db = Mock()
        self.mock_db.ejecutar_query = Mock()

        # Mock del context manager de transacciones
        self.mock_transaction = Mock()
        self.mock_transaction.__enter__ = Mock(return_value=self.mock_transaction)
        self.mock_transaction.__exit__ = Mock(return_value=None)
        self.mock_db.transaction = Mock(return_value=self.mock_transaction)

        # Crear modelo con mock
        self.modelo = HerrajesModel(self.mock_db)

        # Datos de prueba típicos
        self.datos_material = {
            'codigo': 'HERR-001',
            'descripcion': 'Bisagra estándar 3"',
            'cantidad': 100,
            'ubicacion': 'Estante A-1',
            'observaciones': 'Material nuevo'
        }

        self.usuario_test = 'test_user'
        self.id_obra_test = 1
        self.id_herraje_test = 1

    def tearDown(self):
        """Limpieza después de cada test."""
        self.mock_db.reset_mock()


class TestHerrajesModelBasic(TestHerrajesModelComplete):
    """Tests básicos de funcionamiento del modelo."""

    def test_init_herrajes_model(self):
        """Test inicialización del modelo."""
        # Act
        modelo = HerrajesModel(self.mock_db)

        # Assert
        self.assertEqual(modelo.db, self.mock_db)
        self.assertIsInstance(modelo, HerrajesModel)

    def test_init_without_db_uses_default(self):
        """Test inicialización sin DB usa conexión por defecto."""
        # Act
        with patch('modules.herrajes.model.InventarioDatabaseConnection') as mock_db_class:
            mock_db_instance = Mock()
            mock_db_class.return_value = mock_db_instance

            modelo = HerrajesModel()

            # Assert
            mock_db_class.assert_called_once()
            self.assertEqual(modelo.db, mock_db_instance)

    def test_crear_tabla_materiales_success(self):
        """Test crear tabla materiales exitoso."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        self.modelo.crear_tabla_materiales()

        # Assert
        self.mock_db.ejecutar_query.assert_called_once()
        call_args = self.mock_db.ejecutar_query.call_args[0][0]
        self.assertIn("CREATE TABLE materiales", call_args)
        self.assertIn("id INT IDENTITY(1,1) PRIMARY KEY", call_args)

    def test_agregar_material_success(self):
        """Test agregar material exitoso."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        self.modelo.agregar_material(
            self.datos_material['codigo'],
            self.datos_material['descripcion'],
            self.datos_material['cantidad'],
            self.datos_material['ubicacion'],
            self.datos_material['observaciones']
        )

        # Assert
        self.mock_db.ejecutar_query.assert_called_once()
        call_args = self.mock_db.ejecutar_query.call_args
        self.assertIn("INSERT INTO materiales", call_args[0][0])
        self.assertEqual(call_args[0][1], (
            self.datos_material['codigo'],
            self.datos_material['descripcion'],
            self.datos_material['cantidad'],
            self.datos_material['ubicacion'],
            self.datos_material['observaciones']
        ))

    def test_obtener_materiales_success(self):
        """Test obtener materiales exitoso."""
        # Arrange
        materiales_mock = [
            {'id': 1, 'codigo': 'HERR-001', 'descripcion': 'Bisagra', 'cantidad': 100},
            {'id': 2, 'codigo': 'HERR-002', 'descripcion': 'Tornillo', 'cantidad': 500}
        ]
        self.mock_db.ejecutar_query.return_value = materiales_mock

        # Act
        resultado = self.modelo.obtener_materiales()

        # Assert
        self.assertEqual(resultado, materiales_mock)
        self.mock_db.ejecutar_query.assert_called_once_with("SELECT * FROM materiales;")

    def test_actualizar_material_success(self):
        """Test actualizar material exitoso."""
        # Arrange
        id_material = 1
        self.mock_db.ejecutar_query.return_value = None

        # Act
        self.modelo.actualizar_material(
            id_material,
            self.datos_material['codigo'],
            self.datos_material['descripcion'],
            self.datos_material['cantidad'],
            self.datos_material['ubicacion'],
            self.datos_material['observaciones']
        )

        # Assert
        self.mock_db.ejecutar_query.assert_called_once()
        call_args = self.mock_db.ejecutar_query.call_args
        self.assertIn("UPDATE materiales", call_args[0][0])
        self.assertEqual(call_args[0][1], (
            self.datos_material['codigo'],
            self.datos_material['descripcion'],
            self.datos_material['cantidad'],
            self.datos_material['ubicacion'],
            self.datos_material['observaciones'],
            id_material
        ))

    def test_eliminar_material_success(self):
        """Test eliminar material exitoso."""
        # Arrange
        id_material = 1
        self.mock_db.ejecutar_query.return_value = None

        # Act
        self.modelo.eliminar_material(id_material)

        # Assert
        self.mock_db.ejecutar_query.assert_called_once_with(
            "DELETE FROM materiales WHERE id = ?;", (id_material,)
        )


class TestHerrajesModelReservas(TestHerrajesModelComplete):
    """Tests específicos de reservas de herrajes."""

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_reservar_herraje_success_sin_reserva_previa(self, mock_auditoria_db_class):
        """Test reservar herraje exitoso sin reserva previa."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        cantidad_reservar = 10
        stock_actual = 20

        # Simular respuestas de la BD
        self.mock_db.ejecutar_query.side_effect = [
            [(stock_actual,)],  # Consulta stock actual
            None,               # UPDATE stock
            [],                 # No reserva previa (res vacío)
            None,               # INSERT nueva reserva
            None                # INSERT movimiento
        ]

        # Act
        resultado = self.modelo.reservar_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_reservar
        )

        # Assert
        self.assertTrue(resultado)

        # Verificar llamadas a la BD principal
        expected_calls = [
            call("SELECT stock_actual FROM herrajes WHERE id_herraje = ?", (self.id_herraje_test,)),
            call("UPDATE herrajes SET stock_actual = stock_actual - ? WHERE id_herraje = ?", (cantidad_reservar, self.id_herraje_test)),
            call("SELECT cantidad_reservada FROM herrajes_por_obra WHERE id_obra=? AND id_herraje=?", (self.id_obra_test, self.id_herraje_test)),
            call("INSERT INTO herrajes_por_obra (id_obra, id_herraje, cantidad_reservada, estado) VALUES (?, ?, ?, 'Reservado')", (self.id_obra_test, self.id_herraje_test, cantidad_reservar)),
            call("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Egreso', ?, CURRENT_TIMESTAMP, ?)", (self.id_herraje_test, cantidad_reservar, self.usuario_test))
        ]

        self.mock_db.ejecutar_query.assert_has_calls(expected_calls)

        # Verificar auditoría
        mock_auditoria_db.ejecutar_query.assert_called()

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_reservar_herraje_success_con_reserva_previa(self, mock_auditoria_db_class):
        """Test reservar herraje exitoso con reserva previa existente."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        cantidad_reservar = 5
        stock_actual = 15
        cantidad_previa = 3

        self.mock_db.ejecutar_query.side_effect = [
            [(stock_actual,)],      # Consulta stock actual
            None,                   # UPDATE stock
            [(cantidad_previa,)],   # Reserva previa existente
            None,                   # UPDATE reserva existente
            None                    # INSERT movimiento
        ]

        # Act
        resultado = self.modelo.reservar_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_reservar
        )

        # Assert
        self.assertTrue(resultado)

        # Verificar que se actualizó la reserva existente
        expected_update_call = call(
            "UPDATE herrajes_por_obra SET cantidad_reservada=?, estado='Reservado' WHERE id_obra=? AND id_herraje=?",
            (cantidad_previa + cantidad_reservar, self.id_obra_test, self.id_herraje_test)
        )
        self.assertIn(expected_update_call, self.mock_db.ejecutar_query.call_args_list)

    def test_reservar_herraje_cantidad_invalida_none(self):
        """Test reservar herraje con cantidad None."""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, None)

        self.assertIn("Cantidad inválida", str(context.exception))

    def test_reservar_herraje_cantidad_invalida_cero(self):
        """Test reservar herraje con cantidad cero."""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 0)

        self.assertIn("Cantidad inválida", str(context.exception))

    def test_reservar_herraje_cantidad_invalida_negativa(self):
        """Test reservar herraje con cantidad negativa."""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, -5)

        self.assertIn("Cantidad inválida", str(context.exception))

    def test_reservar_herraje_no_encontrado(self):
        """Test reservar herraje que no existe."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []  # No se encuentra herraje

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 10)

        self.assertIn("Herraje no encontrado", str(context.exception))

    def test_reservar_herraje_stock_insuficiente(self):
        """Test reservar herraje con stock insuficiente."""
        # Arrange
        stock_actual = 5
        cantidad_reservar = 10
        self.mock_db.ejecutar_query.return_value = [(stock_actual,)]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_reservar)

        self.assertIn("Stock insuficiente", str(context.exception))

    def test_reservar_herraje_stock_none(self):
        """Test reservar herraje cuando stock es None."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = [(None,)]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 10)

        self.assertIn("Herraje no encontrado", str(context.exception))


class TestHerrajesModelDevoluciones(TestHerrajesModelComplete):
    """Tests específicos de devoluciones de herrajes."""

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_devolver_herraje_success_parcial(self, mock_auditoria_db_class):
        """Test devolver herraje parcial exitoso."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        cantidad_devolver = 3
        cantidad_reservada = 10

        self.mock_db.ejecutar_query.side_effect = [
            None,                       # UPDATE stock (incremento)
            [(cantidad_reservada,)],    # Consulta reserva actual
            None,                       # UPDATE reserva (queda cantidad)
            None                        # INSERT movimiento
        ]

        # Act
        resultado = self.modelo.devolver_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_devolver
        )

        # Assert
        self.assertTrue(resultado)

        # Verificar llamadas
        expected_calls = [
            call("UPDATE herrajes SET stock_actual = stock_actual + ? WHERE id_herraje = ?", (cantidad_devolver, self.id_herraje_test)),
            call("SELECT cantidad_reservada FROM herrajes_por_obra WHERE id_obra=? AND id_herraje=?", (self.id_obra_test, self.id_herraje_test)),
            call("UPDATE herrajes_por_obra SET cantidad_reservada=?, estado='Reservado' WHERE id_obra=? AND id_herraje=?", (cantidad_reservada - cantidad_devolver, self.id_obra_test, self.id_herraje_test)),
            call("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, CURRENT_TIMESTAMP, ?)", (self.id_herraje_test, cantidad_devolver, self.usuario_test))
        ]

        self.mock_db.ejecutar_query.assert_has_calls(expected_calls)

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_devolver_herraje_success_total(self, mock_auditoria_db_class):
        """Test devolver herraje total exitoso."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        cantidad_devolver = 10
        cantidad_reservada = 10

        self.mock_db.ejecutar_query.side_effect = [
            None,                       # UPDATE stock
            [(cantidad_reservada,)],    # Consulta reserva actual
            None,                       # UPDATE reserva (liberar)
            None                        # INSERT movimiento
        ]

        # Act
        resultado = self.modelo.devolver_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_devolver
        )

        # Assert
        self.assertTrue(resultado)

        # Verificar que se liberó la reserva
        expected_liberar_call = call(
            "UPDATE herrajes_por_obra SET cantidad_reservada=0, estado='Liberado' WHERE id_obra=? AND id_herraje=?",
            (self.id_obra_test, self.id_herraje_test)
        )
        self.assertIn(expected_liberar_call, self.mock_db.ejecutar_query.call_args_list)

    def test_devolver_herraje_cantidad_invalida(self):
        """Test devolver herraje con cantidad inválida."""
        # Act & Assert casos
        for cantidad_invalida in [None, 0, -5]:
            with self.subTest(cantidad=cantidad_invalida):
                with self.assertRaises(ValueError) as context:
                    self.modelo.devolver_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_invalida)

                self.assertIn("Cantidad inválida", str(context.exception))

    def test_devolver_herraje_sin_reserva_previa(self):
        """Test devolver herraje sin reserva previa."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = [
            None,   # UPDATE stock
            []      # No hay reserva previa
        ]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.devolver_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 5)

        self.assertIn("No hay reserva previa", str(context.exception))

    def test_devolver_herraje_reserva_cero(self):
        """Test devolver herraje con reserva en cero."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = [
            None,       # UPDATE stock
            [(0,)]      # Reserva en cero
        ]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.devolver_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 5)

        self.assertIn("No hay reserva previa", str(context.exception))

    def test_devolver_herraje_mas_de_lo_reservado(self):
        """Test devolver más cantidad de la reservada."""
        # Arrange
        cantidad_reservada = 5
        cantidad_devolver = 10

        self.mock_db.ejecutar_query.side_effect = [
            None,                       # UPDATE stock
            [(cantidad_reservada,)]     # Consulta reserva actual
        ]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.devolver_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_devolver)

        self.assertIn("No se puede devolver más de lo reservado", str(context.exception))


class TestHerrajesModelAjusteStock(TestHerrajesModelComplete):
    """Tests específicos de ajuste de stock."""

    def test_ajustar_stock_herraje_cantidad_negativa(self):
        """Test ajustar stock con cantidad negativa."""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.ajustar_stock_herraje(self.usuario_test, self.id_herraje_test, -10)

        self.assertIn("Cantidad inválida", str(context.exception))

    def test_ajustar_stock_herraje_no_encontrado(self):
        """Test ajustar stock de herraje no encontrado."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.ajustar_stock_herraje(self.usuario_test, self.id_herraje_test, 50)

        self.assertIn("Herraje no encontrado", str(context.exception))

    def test_ajustar_stock_herraje_stock_none(self):
        """Test ajustar stock cuando stock actual es None."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = [(None,)]

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.modelo.ajustar_stock_herraje(self.usuario_test, self.id_herraje_test, 50)

        self.assertIn("Herraje no encontrado", str(context.exception))


class TestHerrajesModelEdgeCases(TestHerrajesModelComplete):
    """Tests de casos límite y errores."""

    def test_obtener_materiales_empty_result(self):
        """Test obtener materiales cuando no hay resultados."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = []

        # Act
        resultado = self.modelo.obtener_materiales()

        # Assert
        self.assertEqual(resultado, [])

    def test_obtener_materiales_none_result(self):
        """Test obtener materiales cuando el resultado es None."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None

        # Act
        resultado = self.modelo.obtener_materiales()

        # Assert
        self.assertIsNone(resultado)

    def test_agregar_material_error_db(self):
        """Test agregar material con error de base de datos."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = Exception("Error de BD")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.modelo.agregar_material("TEST", "Test", 1, "Test", "Test")

        self.assertIn("Error de BD", str(context.exception))

    def test_actualizar_material_id_inexistente(self):
        """Test actualizar material con ID inexistente."""
        # Arrange
        self.mock_db.ejecutar_query.side_effect = Exception("No rows affected")

        # Act & Assert
        with self.assertRaises(Exception):
            self.modelo.actualizar_material(9999, "TEST", "Test", 1, "Test", "Test")

    def test_eliminar_material_id_inexistente(self):
        """Test eliminar material con ID inexistente."""
        # Arrange
        self.mock_db.ejecutar_query.return_value = None  # No error, pero no afecta filas

        # Act
        # No debería lanzar excepción, pero tampoco afectar registros
        self.modelo.eliminar_material(9999)

        # Assert
        self.mock_db.ejecutar_query.assert_called_once_with(
            "DELETE FROM materiales WHERE id = ?;", (9999,)
        )

    def test_constantes_clase_definidas(self):
        """Test que las constantes de clase están correctamente definidas."""
        # Assert
        self.assertEqual(HerrajesModel.CANTIDAD_INVALIDA_MSG, "Cantidad inválida")
        self.assertIn("INSERT INTO auditorias_sistema", HerrajesModel.AUDITORIA_INSERT_QUERY)


class TestHerrajesModelIntegration(TestHerrajesModelComplete):
    """Tests de integración y flujos complejos."""

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_flujo_completo_reserva_devolucion(self, mock_auditoria_db_class):
        """Test flujo completo: reservar y luego devolver herraje."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        cantidad_inicial = 20
        cantidad_reservar = 10
        cantidad_devolver = 5

        # Simulación de reserva
        self.mock_db.ejecutar_query.side_effect = [
            # Reserva
            [(cantidad_inicial,)],          # Stock inicial
            None,                           # UPDATE stock (reserva)
            [],                             # No reserva previa
            None,                           # INSERT nueva reserva
            None,                           # INSERT movimiento egreso
            # Devolución
            None,                           # UPDATE stock (devolución)
            [(cantidad_reservar,)],         # Consulta reserva actual
            None,                           # UPDATE reserva (parcial)
            None                            # INSERT movimiento ingreso
        ]

        # Act
        # 1. Reservar
        resultado_reserva = self.modelo.reservar_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_reservar
        )

        # 2. Devolver parcialmente
        resultado_devolucion = self.modelo.devolver_herraje(
            self.usuario_test, self.id_obra_test, self.id_herraje_test, cantidad_devolver
        )

        # Assert
        self.assertTrue(resultado_reserva)
        self.assertTrue(resultado_devolucion)

        # Verificar que se llamaron ambos flujos (ajustando el número real de llamadas)
        self.assertGreaterEqual(self.mock_db.ejecutar_query.call_count, 8)

        # Verificar auditoría para ambas operaciones
        self.assertEqual(mock_auditoria_db.ejecutar_query.call_count, 4)  # 2 por reserva + 2 por devolución

    def test_flujo_materiales_crud_completo(self):
        """Test flujo CRUD completo de materiales."""
        # Arrange
        material_id = 1

        self.mock_db.ejecutar_query.side_effect = [
            None,                           # CREATE TABLE
            None,                           # INSERT material
            [{'id': material_id, 'codigo': 'HERR-001'}],  # SELECT materiales
            None,                           # UPDATE material
            None                            # DELETE material
        ]

        # Act
        # 1. Crear tabla
        self.modelo.crear_tabla_materiales()

        # 2. Agregar material
        self.modelo.agregar_material(
            self.datos_material['codigo'],
            self.datos_material['descripcion'],
            self.datos_material['cantidad'],
            self.datos_material['ubicacion'],
            self.datos_material['observaciones']
        )

        # 3. Obtener materiales
        materiales = self.modelo.obtener_materiales()

        # 4. Actualizar material
        self.modelo.actualizar_material(
            material_id,
            "HERR-001-UPD",
            "Descripción actualizada",
            150,
            "Estante B-2",
            "Material actualizado"
        )

        # 5. Eliminar material
        self.modelo.eliminar_material(material_id)

        # Assert
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 5)
        self.assertEqual(len(materiales), 1)

    def test_multiples_reservas_misma_obra(self):
        """Test múltiples reservas de diferentes herrajes para la misma obra."""
        # Arrange
        with patch('modules.herrajes.model.AuditoriaDatabaseConnection'):
            herrajes_ids = [1, 2, 3]
            cantidades = [5, 10, 15]

            # Configurar respuestas para cada herraje
            side_effects = []
            for i, (herraje_id, cantidad) in enumerate(zip(herrajes_ids, cantidades)):
                side_effects.extend([
                    [(50,)],    # Stock suficiente
                    None,       # UPDATE stock
                    [],         # No reserva previa
                    None,       # INSERT reserva
                    None        # INSERT movimiento
                ])

            self.mock_db.ejecutar_query.side_effect = side_effects

            # Act
            resultados = []
            for herraje_id, cantidad in zip(herrajes_ids, cantidades):
                resultado = self.modelo.reservar_herraje(
                    self.usuario_test, self.id_obra_test, herraje_id, cantidad
                )
                resultados.append(resultado)

            # Assert
            self.assertTrue(all(resultados))
            self.assertEqual(self.mock_db.ejecutar_query.call_count, 15)  # 5 calls por herraje

    @patch('modules.herrajes.model.AuditoriaDatabaseConnection')
    def test_transacciones_utilizadas_correctamente(self, mock_auditoria_db_class):
        """Test que las transacciones se usan correctamente en operaciones críticas."""
        # Arrange
        mock_auditoria_db = Mock()
        mock_auditoria_db_class.return_value = mock_auditoria_db

        self.mock_db.ejecutar_query.side_effect = [
            [(20,)],    # Stock inicial
            None,       # UPDATE stock
            [],         # No reserva previa
            None,       # INSERT reserva
            None        # INSERT movimiento
        ]

        # Act
        self.modelo.reservar_herraje(self.usuario_test, self.id_obra_test, self.id_herraje_test, 10)

        # Assert
        # Verificar que se usó transacción
        self.mock_db.transaction.assert_called_once_with(timeout=30, retries=2)
        self.mock_transaction.__enter__.assert_called_once()
        self.mock_transaction.__exit__.assert_called_once()


if __name__ == '__main__':
    unittest.main()
