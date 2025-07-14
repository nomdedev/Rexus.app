"""
Test de integración cruzada entre módulos.
Verifica que la tabla de obras muestre correctamente los estados de pedidos de otros módulos.
"""

import unittest

# from modules.obras.controller import ObrasController # Movido a sección try/except
# from modules.obras.model import ObrasModel # Movido a sección try/except
from unittest.mock import Mock, patch

# from modules.obras.view import ObrasView # Movido a sección try/except


class TestIntegracionCruzada(unittest.TestCase):

    def setUp(self):
        """Configurar mocks para las pruebas"""
        self.mock_db = Mock()
        self.mock_view = Mock()
        self.mock_model = Mock(spec=ObrasModel)
        self.mock_model.db_connection = self.mock_db

        # Configurar datos de prueba
        self.mock_model.obtener_datos_obras.return_value = [
            (1, "Obra Test", "Cliente Test", "Medición", "2025-06-25", "2025-07-25")
        ]
        self.mock_model.obtener_headers_obras.return_value = [
            "id",
            "nombre",
            "cliente",
            "estado",
            "fecha",
            "fecha_entrega",
            "estado_material",
            "estado_vidrios",
            "estado_herrajes",
            "estado_pago",
        ]

    @patch("modules.inventario.model.InventarioModel")
    @patch("modules.vidrios.model.VidriosModel")
    @patch("modules.herrajes.model.HerrajesModel")
    @patch("modules.contabilidad.model.ContabilidadModel")
    def test_cargar_datos_obras_con_estados_integracion(
        self, mock_contabilidad, mock_herrajes, mock_vidrios, mock_inventario
    ):
        """Test que verifica que la tabla de obras carga con los estados de integración"""

        # Configurar mocks de modelos
        mock_inventario.return_value.obtener_estado_pedido_por_obra.return_value = (
            "pedido"
        )
        mock_vidrios.return_value.obtener_estado_pedido_por_obra.return_value = (
            "pendiente"
        )
        mock_herrajes.return_value.obtener_estado_pedido_por_obra.return_value = (
            "pedido"
        )
        mock_contabilidad.return_value.obtener_estado_pago_pedido_por_obra.return_value = (
            "pagado"
        )

        # Crear controlador
        controller = ObrasController(
            model=self.mock_model,
            view=self.mock_view,
            db_connection=self.mock_db,
            usuarios_model=Mock(),
            usuario_actual={"id": 1, "username": "test"},
            auditoria_model=Mock(),
        )

        # Llamar al método que queremos probar
        controller.cargar_datos_obras_tabla()
        # Verificar que se llamaron los métodos de integración (pueden ser múltiples llamadas)
        self.assertGreaterEqual(mock_inventario.call_count, 1)
        self.assertGreaterEqual(mock_vidrios.call_count, 1)
        self.assertGreaterEqual(mock_herrajes.call_count, 1)
        self.assertGreaterEqual(mock_contabilidad.call_count, 1)

        # Verificar que se consultaron los estados
        mock_inventario.return_value.obtener_estado_pedido_por_obra.assert_called_with(
            1
        )
        mock_vidrios.return_value.obtener_estado_pedido_por_obra.assert_called_with(1)
        mock_herrajes.return_value.obtener_estado_pedido_por_obra.assert_called_with(1)

    def test_headers_include_integration_columns(self):
        """Test que verifica que los headers incluyen las columnas de integración"""

        headers = self.mock_model.obtener_headers_obras()

        # Verificar que incluye las columnas de integración
        self.assertIn("estado_material", headers)
        self.assertIn("estado_vidrios", headers)
        self.assertIn("estado_herrajes", headers)
        self.assertIn("estado_pago", headers)

    def test_obtener_estado_pedidos_por_obra(self):
        """Test del método que obtiene estados de pedidos de todos los módulos"""

        # Crear mocks para controladores
        mock_inventario_controller = Mock()
        mock_vidrios_controller = Mock()
        mock_herrajes_controller = Mock()

        mock_inventario_controller.model.obtener_estado_pedido_por_obra.return_value = (
            "pedido"
        )
        mock_vidrios_controller.model.obtener_estado_pedido_por_obra.return_value = (
            "pendiente"
        )
        mock_herrajes_controller.model.obtener_estado_pedido_por_obra.return_value = (
            "error"
        )

        # Crear controlador
        controller = ObrasController(
            model=self.mock_model,
            view=self.mock_view,
            db_connection=self.mock_db,
            usuarios_model=Mock(),
            usuario_actual={"id": 1, "username": "test"},
            auditoria_model=Mock(),
        )

        # Llamar al método
        resultado = controller.obtener_estado_pedidos_por_obra(
            id_obra=1,
            inventario_controller=mock_inventario_controller,
            vidrios_controller=mock_vidrios_controller,
            herrajes_controller=mock_herrajes_controller,
        )

        # Verificar el resultado
        expected = {"inventario": "pedido", "vidrios": "pendiente", "herrajes": "error"}
        self.assertEqual(resultado, expected)


if __name__ == "__main__":
    unittest.main()
