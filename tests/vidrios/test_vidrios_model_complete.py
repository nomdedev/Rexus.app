"""
Tests exhaustivos para VidriosModel.

Cobertura:
- Inicialización del modelo
- CRUD de vidrios por obra (crear, obtener, actualizar)
- Asignación y devolución de vidrios
- Consultas de obras y estados
- Manejo de pedidos
- Edge cases y validaciones
- Integración con base de datos
- Auditoría y logging
"""

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestVidriosModelInit(unittest.TestCase):
    """Tests para la inicialización del modelo."""

    def test_init_with_db_connection(self):
        """Test inicialización con conexión de BD válida."""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from rexus.modules.vidrios.model import VidriosModel

        mock_db = Mock()
        model = VidriosModel(mock_db)

        self.assertEqual(model.db, mock_db)
        self.assertEqual(model.CANTIDAD_INVALIDA_MSG, "Cantidad inválida")

    def test_init_with_none_db(self):
        """Test inicialización con conexión None."""
        model = VidriosModel(None)
        self.assertIsNone(model.db)


class TestVidriosModelObtener(unittest.TestCase):
    """Tests para obtención de datos."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_obtener_vidrios_exitoso(self):
        """Test obtener todos los vidrios exitosamente."""
        datos_esperados = [
            (1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo"),
            (2, 2, "Vidrio", 150, 100, "Azul", "Proveedor B", "2025-01-20", "Urgente", 3, "Reservado")
"""
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_vidrios()

        self.assertEqual(resultado, datos_esperados)
        self.mock_db.ejecutar_query.assert_called_once_with("SELECT * FROM vidrios_por_obra")

    def test_obtener_vidrios_vacio(self):
        """Test obtener vidrios cuando no hay datos."""
        self.mock_db.ejecutar_query.return_value = []

        resultado = self.model.obtener_vidrios()

        self.assertEqual(resultado, [])
        self.mock_db.ejecutar_query.assert_called_once()

    def test_obtener_obras_con_estado_pedido_exitoso(self):
        """Test obtener obras con estado de pedido."""
        datos_esperados = [
            (1, "Obra A", "Cliente 1", "2025-02-01", "Con pedido"),
            (2, "Obra B", "Cliente 2", "2025-02-15", "Sin pedido")
        ]
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_obras_con_estado_pedido()

        self.assertEqual(resultado, datos_esperados)
        expected_query = '''
        SELECT o.id, o.nombre, o.cliente, o.fecha_entrega,
               CASE WHEN EXISTS (SELECT 1 FROM vidrios_por_obra vpo WHERE vpo.obra_id = o.id) THEN 'Con pedido' ELSE 'Sin pedido' END as estado_pedido
        FROM obras o
        '''
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query)

    def test_obtener_pedidos_por_usuario_exitoso(self):
        """Test obtener pedidos por usuario."""
        datos_esperados = [
            (1, "Obra A", "Cliente 1", "Cristal", 100, 80, "Transparente", 5, "Activo", 1),
            (2, "Obra B", "Cliente 2", "Vidrio", 150, 100, "Azul", 3, "Reservado", 2)
        ]
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_pedidos_por_usuario()

        self.assertEqual(resultado, datos_esperados)
        expected_query = '''
        SELECT vpo.obra_id, o.nombre, o.cliente, vpo.tipo, vpo.ancho, vpo.alto, vpo.color, vpo.cantidad_reservada, vpo.estado, vpo.id
        FROM vidrios_por_obra vpo
        JOIN obras o ON o.id = vpo.obra_id
        ORDER BY vpo.id DESC
        '''
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query)

    def test_obtener_pedidos_por_usuario_con_parametro(self):
        """Test obtener pedidos por usuario específico."""
        datos_esperados = [(1, "Obra A", "Cliente 1", "Cristal", 100, 80, "Transparente", 5, "Activo", 1)]
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_pedidos_por_usuario(usuario_id=123)

        self.assertEqual(resultado, datos_esperados)
        # El método actual ignora el usuario_id, pero el test verifica que no falle


class TestVidriosModelAgregar(unittest.TestCase):
    """Tests para agregar vidrios."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_agregar_vidrio_exitoso(self):
        """Test agregar vidrio exitosamente."""
        datos = (1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")

        self.model.agregar_vidrio(datos)

        expected_query = """
        INSERT INTO vidrios_por_obra (obra_id, tipo, ancho, alto, color, proveedor, fecha_entrega, observaciones, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, datos)

    def test_agregar_vidrio_datos_minimos(self):
        """Test agregar vidrio con datos mínimos."""
        datos = (2, "Vidrio", 50, 40, "Azul", "Proveedor B", None, None, 1, "Pendiente")

        self.model.agregar_vidrio(datos)

        self.mock_db.ejecutar_query.assert_called_once()
        args = self.mock_db.ejecutar_query.call_args[0]
        self.assertEqual(args[1], datos)

    def test_guardar_pedido_vidrios_exitoso(self):
        """Test guardar pedido de vidrios."""
        datos = (3, "Cristal", 120, 90, "Verde", "Proveedor C", "2025-02-01", "Urgente", 2, "Activo")

        self.model.guardar_pedido_vidrios(datos)

        # Debe llamar a agregar_vidrio internamente
        expected_query = """
        INSERT INTO vidrios_por_obra (obra_id, tipo, ancho, alto, color, proveedor, fecha_entrega, observaciones, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, datos)


class TestVidriosModelAsignar(unittest.TestCase):
    """Tests para asignación de vidrios."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_asignar_a_obra_exitoso(self):
        """Test asignar vidrio a obra exitosamente."""
        datos = (1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Asignado")

        resultado = self.model.asignar_a_obra(datos)

        self.assertTrue(resultado)
        expected_query = """
        INSERT INTO vidrios_por_obra (obra_id, tipo, ancho, alto, color, proveedor, fecha_entrega, observaciones, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, datos)

    def test_asignar_a_obra_datos_completos(self):
        """Test asignar vidrio con todos los datos."""
        datos = (2, "Vidrio templado", 200, 150, "Negro", "Proveedor Premium", "2025-03-01", "Material especial", 10, "Reservado")

        resultado = self.model.asignar_a_obra(datos)

        self.assertTrue(resultado)
        self.mock_db.ejecutar_query.assert_called_once()


class TestVidriosModelDevolver(unittest.TestCase):
    """Tests para devolución de vidrios."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_devolver_vidrio_exitoso_sin_usuario(self):
        """Test devolver vidrio sin usuario."""
        resultado = self.model.devolver_vidrio(obra_id=1, tipo="Cristal", cantidad=3)

        self.assertTrue(resultado)
        expected_query = """
        UPDATE vidrios_por_obra SET cantidad_reservada = cantidad_reservada + ?, estado = 'Devuelto' WHERE obra_id = ? AND tipo = ?
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (3, 1, "Cristal"))

    def test_devolver_vidrio_exitoso_con_usuario(self):
        """Test devolver vidrio con usuario para auditoría."""
        self.model.devolver_vidrio(obra_id=2, tipo="Vidrio", cantidad=5, usuario_id=123)

        expected_calls = [
            call("""
        UPDATE vidrios_por_obra SET cantidad_reservada = cantidad_reservada + ?, estado = 'Devuelto' WHERE obra_id = ? AND tipo = ?
        """, (5, 2, "Vidrio")),
            call("INSERT INTO auditorias_sistema (usuario_id, modulo, accion) VALUES (?, ?, ?)",
                 (123, "Vidrios", "Devolvió 5 del vidrio tipo Vidrio de la obra 2"))
        ]
        self.mock_db.ejecutar_query.assert_has_calls(expected_calls)

    def test_devolver_vidrio_auditoria_falla_no_afecta_operacion(self):
        """Test que fallo en auditoría no afecte la operación principal."""
        # Configurar para que la auditoría falle
        self.mock_db.ejecutar_query.side_effect = [None, Exception("Error auditoría")]

        # La operación debe completarse exitosamente
        resultado = self.model.devolver_vidrio(obra_id=1, tipo="Cristal", cantidad=2, usuario_id=456)

        self.assertTrue(resultado)
        # Verificar que se intentó la auditoría pero falló silenciosamente
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 2)

    def test_devolver_vidrio_cantidad_cero(self):
        """Test devolver cantidad cero."""
        resultado = self.model.devolver_vidrio(obra_id=1, tipo="Cristal", cantidad=0)

        self.assertTrue(resultado)
        expected_query = """
        UPDATE vidrios_por_obra SET cantidad_reservada = cantidad_reservada + ?, estado = 'Devuelto' WHERE obra_id = ? AND tipo = ?
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (0, 1, "Cristal"))


class TestVidriosModelEstados(unittest.TestCase):
    """Tests para manejo de estados."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_actualizar_estado_pedido_exitoso(self):
        """Test actualizar estado de pedido."""
        self.model.actualizar_estado_pedido(obra_id=1, nuevo_estado="Completado")

        expected_query = """
        UPDATE vidrios_por_obra SET estado = ? WHERE obra_id = ?
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, ("Completado", 1))

    def test_obtener_estado_pedido_por_obra_exitoso(self):
        """Test obtener estado de pedido por obra."""
        self.mock_db.ejecutar_query.return_value = [("Activo",)]

        estado = self.model.obtener_estado_pedido_por_obra(obra_id=1)

        self.assertEqual(estado, "Activo")
        expected_query = "SELECT TOP 1 estado FROM vidrios_por_obra WHERE obra_id = ? ORDER BY id DESC"
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (1,))

    def test_obtener_estado_pedido_por_obra_sin_resultados(self):
        """Test obtener estado cuando no hay resultados."""
        self.mock_db.ejecutar_query.return_value = []

        estado = self.model.obtener_estado_pedido_por_obra(obra_id=999)

        self.assertEqual(estado, "pendiente")

    def test_obtener_estado_pedido_por_obra_resultado_vacio(self):
        """Test obtener estado con resultado None."""
        self.mock_db.ejecutar_query.return_value = None

        estado = self.model.obtener_estado_pedido_por_obra(obra_id=999)

        self.assertEqual(estado, "pendiente")

    def test_obtener_estado_pedido_por_obra_error(self):
        """Test obtener estado con error en BD."""
        self.mock_db.ejecutar_query.side_effect = Exception("Error de BD")

        estado = self.model.obtener_estado_pedido_por_obra(obra_id=1)

        self.assertTrue(estado.startswith("Error:"))
        self.assertIn("Error de BD", estado)


class TestVidriosModelDetalles(unittest.TestCase):
    """Tests para obtención de detalles."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_obtener_detalle_pedido_exitoso(self):
        """Test obtener detalle de pedido exitosamente."""
        datos_esperados = [("Cristal", 100, 80, "Transparente", 5, "Activo", 1, "Proveedor A", "2025-01-15", "Sin observaciones")]
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_detalle_pedido(obra_id=1, tipo="Cristal")

        self.assertEqual(resultado, datos_esperados)
        expected_query = '''
        SELECT tipo, ancho, alto, color, cantidad_reservada, estado, id, proveedor, fecha_entrega, observaciones
        FROM vidrios_por_obra
        WHERE obra_id = ? AND tipo = ?
        '''
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (1, "Cristal"))

    def test_obtener_detalle_pedido_sin_resultados(self):
        """Test obtener detalle cuando no hay resultados."""
        self.mock_db.ejecutar_query.return_value = []

        resultado = self.model.obtener_detalle_pedido(obra_id=999, tipo="Inexistente")

        self.assertEqual(resultado, [])

    def test_obtener_pedidos_por_obra_exitoso(self):
        """Test obtener pedidos por obra exitosamente."""
        datos_esperados = [
            (1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo"),
            (2, 1, "Vidrio", 150, 100, "Azul", "Proveedor B", "2025-01-20", "Urgente", 3, "Reservado")
        ]
        self.mock_db.ejecutar_query.return_value = datos_esperados

        resultado = self.model.obtener_pedidos_por_obra(obra_id=1)

        self.assertEqual(resultado, datos_esperados)
        expected_query = "SELECT * FROM vidrios_por_obra WHERE obra_id = ? ORDER BY id DESC"
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (1,))

    def test_obtener_pedidos_por_obra_sin_resultados(self):
        """Test obtener pedidos por obra sin resultados."""
        self.mock_db.ejecutar_query.return_value = None

        resultado = self.model.obtener_pedidos_por_obra(obra_id=999)

        self.assertEqual(resultado, [])

    def test_obtener_pedidos_por_obra_error(self):
        """Test obtener pedidos por obra con error."""
        self.mock_db.ejecutar_query.side_effect = Exception("Error de consulta")

        resultado = self.model.obtener_pedidos_por_obra(obra_id=1)

        self.assertTrue(isinstance(resultado, str))
        self.assertTrue(resultado.startswith("Error:"))


class TestVidriosModelEdgeCases(unittest.TestCase):
    """Tests para casos edge y validaciones."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_agregar_vidrio_con_datos_none(self):
        """Test agregar vidrio con algunos datos None."""
        datos = (1, "Cristal", 100, 80, None, None, None, None, 0, "Pendiente")

        self.model.agregar_vidrio(datos)

        self.mock_db.ejecutar_query.assert_called_once()

    def test_devolver_vidrio_obra_inexistente(self):
        """Test devolver vidrio de obra inexistente."""
        resultado = self.model.devolver_vidrio(obra_id=9999, tipo="Cristal", cantidad=1)

        self.assertTrue(resultado)  # El método siempre retorna True

    def test_actualizar_estado_pedido_estado_vacio(self):
        """Test actualizar estado con string vacío."""
        self.model.actualizar_estado_pedido(obra_id=1, nuevo_estado="")

        expected_query = """
        UPDATE vidrios_por_obra SET estado = ? WHERE obra_id = ?
        """
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, ("", 1))

    def test_obtener_detalle_pedido_tipo_especial(self):
        """Test obtener detalle con tipo que contiene caracteres especiales."""
        self.mock_db.ejecutar_query.return_value = []

        resultado = self.model.obtener_detalle_pedido(obra_id=1, tipo="Vidrio & Cristal 100%")

        self.assertEqual(resultado, [])
        expected_query = '''
        SELECT tipo, ancho, alto, color, cantidad_reservada, estado, id, proveedor, fecha_entrega, observaciones
        FROM vidrios_por_obra
        WHERE obra_id = ? AND tipo = ?
        '''
        self.mock_db.ejecutar_query.assert_called_once_with(expected_query, (1, "Vidrio & Cristal 100%"))


class TestVidriosModelIntegration(unittest.TestCase):
    """Tests de integración para VidriosModel."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.model = VidriosModel(self.mock_db)

    def test_flujo_completo_agregar_asignar_devolver(self):
        """Test flujo completo: agregar, asignar y devolver vidrio."""
        # 1. Agregar vidrio
        datos_agregar = (1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")
        self.model.agregar_vidrio(datos_agregar)

        # 2. Asignar a obra
        datos_asignar = (2, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 3, "Asignado")
        resultado_asignar = self.model.asignar_a_obra(datos_asignar)

        # 3. Devolver vidrios
        resultado_devolver = self.model.devolver_vidrio(obra_id=2, tipo="Cristal", cantidad=1, usuario_id=123)

        self.assertTrue(resultado_asignar)
        self.assertTrue(resultado_devolver)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 4)  # 2 inserts + 1 update + 1 auditoría

    def test_flujo_consultas_relacionadas(self):
        """Test flujo de consultas relacionadas."""
        # Configurar datos de prueba
        self.mock_db.ejecutar_query.side_effect = [
            # obtener_obras_con_estado_pedido
            [(1, "Obra A", "Cliente 1", "2025-02-01", "Con pedido")],
            # obtener_pedidos_por_obra
            [(1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")],
            # obtener_estado_pedido_por_obra
            [("Activo",)],
            # obtener_detalle_pedido
            [("Cristal", 100, 80, "Transparente", 5, "Activo", 1, "Proveedor A", "2025-01-15", "Sin observaciones")]
        ]

        # Ejecutar consultas
        obras = self.model.obtener_obras_con_estado_pedido()
        pedidos = self.model.obtener_pedidos_por_obra(obra_id=1)
        estado = self.model.obtener_estado_pedido_por_obra(obra_id=1)
        detalle = self.model.obtener_detalle_pedido(obra_id=1, tipo="Cristal")

        # Verificar resultados
        self.assertEqual(len(obras), 1)
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(estado, "Activo")
        self.assertEqual(len(detalle), 1)
        self.assertEqual(self.mock_db.ejecutar_query.call_count, 4)


if __name__ == '__main__':
    unittest.main()
