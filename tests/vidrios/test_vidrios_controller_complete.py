"""
Tests exhaustivos para VidriosController.

Cobertura:
- Inicialización del controlador
- Métodos de actualización y refresco
- Manejo de pedidos y obras
- Validaciones cruzadas
- Integración con auditoría
- Manejo de estados
- Edge cases y validaciones
- Feedback visual y logging
"""

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestVidriosControllerInit(unittest.TestCase):
    """Tests para la inicialización del controlador."""

    def test_init_with_all_parameters(self):
        """Test inicialización con todos los parámetros."""
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from modules.vidrios.controller import VidriosController

        mock_model = Mock()
        mock_view = Mock()
        mock_db = Mock()
        mock_usuario = Mock()
        mock_usuario.username = "test_user"
        mock_usuario.id = 123

        with patch('modules.vidrios.controller.AuditoriaModel') as mock_auditoria:
            controller = VidriosController(mock_model, mock_view, mock_db, mock_usuario)

            self.assertEqual(controller.model, mock_model)
            self.assertEqual(controller.view, mock_view)
            self.assertEqual(controller.usuario_actual, mock_usuario)
            mock_auditoria.assert_called_once_with(mock_db)
            self.assertIsNotNone(controller.auditoria_model)

    def test_init_without_usuario(self):
        """Test inicialización sin usuario."""
        mock_model = Mock()
        mock_view = Mock()
        mock_db = Mock()

        with patch('modules.vidrios.controller.AuditoriaModel'):
            controller = VidriosController(mock_model, mock_view, mock_db)

            self.assertEqual(controller.model, mock_model)
            self.assertEqual(controller.view, mock_view)
            self.assertIsNone(controller.usuario_actual)


class TestVidriosControllerActualizacion(unittest.TestCase):
    """Tests para métodos de actualización."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = Mock()
        self.mock_usuario.username = "test_user"
        self.mock_usuario.id = 123

        with patch('modules.vidrios.controller.AuditoriaModel'):
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    @patch('modules.vidrios.controller.Logger')
    def test_actualizar_por_obra_exitoso(self, mock_logger):
        """Test actualizar por obra exitosamente."""
        datos_obra = {"nombre": "Obra Test", "id": 1}
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Mock del método refrescar_vidrios
        with patch.object(self.controller, 'refrescar_vidrios') as mock_refrescar:
            self.controller.actualizar_por_obra(datos_obra)

            mock_refrescar.assert_called_once()
            self.mock_view.mostrar_mensaje.assert_called_once_with(
                "Vidrios actualizados automáticamente por la obra 'Obra Test'.", tipo='info'
            )

        # Verificar logging
        mock_logger_instance.info.assert_any_call(
            "[LOG ACCIÓN] Ejecutando acción 'actualizar_por_obra' en módulo 'vidrios' por usuario: test_user"
        )
        mock_logger_instance.info.assert_any_call(
            "[LOG ACCIÓN] Acción 'actualizar_por_obra' en módulo 'vidrios' finalizada con éxito."
        )

    @patch('modules.vidrios.controller.Logger')
    def test_actualizar_por_obra_sin_nombre(self, mock_logger):
        """Test actualizar por obra sin nombre."""
        datos_obra = {"id": 1}
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        with patch.object(self.controller, 'refrescar_vidrios'):
            self.controller.actualizar_por_obra(datos_obra)

            self.mock_view.mostrar_mensaje.assert_called_once_with(
                "Vidrios actualizados automáticamente por la obra ''.", tipo='info'
            )

    @patch('modules.vidrios.controller.Logger')
    def test_refrescar_vidrios_exitoso(self, mock_logger):
        """Test refrescar vidrios exitosamente."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Configurar datos de prueba
        vidrios_data = [
            (1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo"),
            (2, 2, "Vidrio", 150, 100, "Azul", "Proveedor B", "2025-01-20", "Urgente", 3, "Reservado")
        ]
        self.mock_model.obtener_vidrios.return_value = vidrios_data

        # Configurar headers y tabla
        self.mock_view.vidrios_headers = ["ID", "Obra", "Tipo", "Ancho", "Alto", "Color", "Proveedor", "Fecha", "Obs", "Cantidad", "Estado"]
        self.mock_view.tabla_vidrios = Mock()

        self.controller.refrescar_vidrios()

        # Verificar llamadas
        self.mock_model.obtener_vidrios.assert_called_once()
        self.mock_view.tabla_vidrios.setRowCount.assert_called_once_with(2)

        # Verificar logging
        mock_logger_instance.info.assert_any_call(
            "[LOG ACCIÓN] Ejecutando acción 'refrescar_vidrios' en módulo 'vidrios' por usuario: test_user"
        )
        mock_logger_instance.info.assert_any_call(
            "[LOG ACCIÓN] Acción 'refrescar_vidrios' en módulo 'vidrios' finalizada con éxito."
        )

    @patch('modules.vidrios.controller.Logger')
    def test_refrescar_vidrios_error(self, mock_logger):
        """Test refrescar vidrios con error."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Configurar error en modelo
        self.mock_model.obtener_vidrios.side_effect = Exception("Error de BD")

        self.controller.refrescar_vidrios()

        # Verificar manejo de error
        mock_logger_instance.error.assert_called_once_with(
            "[LOG ACCIÓN] Error en acción 'refrescar_vidrios' en módulo 'vidrios': Error de BD"
        )
        self.mock_view.mostrar_mensaje.assert_called_once_with(
            "Error al refrescar vidrios: Error de BD", tipo='error'
        )

    @patch('modules.vidrios.controller.Logger')
    def test_refrescar_vidrios_sin_tabla(self, mock_logger):
        """Test refrescar vidrios sin tabla en vista."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        vidrios_data = [(1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")]
        self.mock_model.obtener_vidrios.return_value = vidrios_data

        # Vista sin tabla_vidrios
        delattr(self.mock_view, 'tabla_vidrios')

        # No debe lanzar excepción
        self.controller.refrescar_vidrios()

        self.mock_model.obtener_vidrios.assert_called_once()


class TestVidriosControllerPedidos(unittest.TestCase):
    """Tests para manejo de pedidos."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = Mock()
        self.mock_usuario.username = "test_user"
        self.mock_usuario.id = 123

        with patch('modules.vidrios.controller.AuditoriaModel') as mock_auditoria:
            self.mock_auditoria_model = Mock()
            mock_auditoria.return_value = self.mock_auditoria_model
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    def test_cargar_resumen_obras(self):
        """Test cargar resumen de obras."""
        obras_data = [
            (1, "Obra A", "Cliente 1", "2025-02-01", "Con pedido"),
            (2, "Obra B", "Cliente 2", "2025-02-15", "Sin pedido")
        ]
        self.mock_model.obtener_obras_con_estado_pedido.return_value = obras_data

        self.controller.cargar_resumen_obras()

        self.mock_model.obtener_obras_con_estado_pedido.assert_called_once()
        self.mock_view.mostrar_resumen_obras.assert_called_once_with(obras_data)

    def test_cargar_pedidos_usuario(self):
        """Test cargar pedidos por usuario."""
        usuario = "test_user"
        pedidos_data = [
            (1, "Obra A", "Cliente 1", "Cristal", 100, 80, "Transparente", 5, "Activo", 1)
        ]
        self.mock_model.obtener_pedidos_por_usuario.return_value = pedidos_data

        self.controller.cargar_pedidos_usuario(usuario)

        self.mock_model.obtener_pedidos_por_usuario.assert_called_once_with(usuario)
        self.mock_view.mostrar_pedidos_usuario.assert_called_once_with(pedidos_data)

    def test_mostrar_detalle_pedido(self):
        """Test mostrar detalle de pedido."""
        id_obra = 1
        tipo = "Cristal"
        detalle_data = [("Cristal", 100, 80, "Transparente", 5, "Activo", 1, "Proveedor A", "2025-01-15", "Sin observaciones")]
        self.mock_model.obtener_detalle_pedido.return_value = detalle_data

        self.controller.mostrar_detalle_pedido(id_obra, tipo)

        self.mock_model.obtener_detalle_pedido.assert_called_once_with(id_obra, tipo)
        self.mock_view.mostrar_detalle_pedido.assert_called_once_with(detalle_data)

    def test_actualizar_estado_pedido(self):
        """Test actualizar estado de pedido."""
        id_obra = 1
        nuevo_estado = "Completado"

        with patch.object(self.controller, 'cargar_resumen_obras') as mock_cargar:
            self.controller.actualizar_estado_pedido(id_obra, nuevo_estado)

            self.mock_model.actualizar_estado_pedido.assert_called_once_with(id_obra, nuevo_estado)
            self.mock_auditoria_model.registrar_evento.assert_called_once_with(
                usuario_id=123,
                modulo="Vidrios",
                tipo_evento="Actualizar estado pedido",
                detalle="Actualizó estado de pedido de obra 1 a Completado",
                ip_origen="127.0.0.1"
            )
            mock_cargar.assert_called_once()


class TestVidriosControllerValidaciones(unittest.TestCase):
    """Tests para validaciones."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = Mock()

        with patch('modules.vidrios.controller.AuditoriaModel'):
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    @patch('modules.vidrios.controller.Logger')
    def test_validar_obra_existente_exitoso(self, mock_logger):
        """Test validar obra existente exitosamente."""
        id_obra = 1
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = {"id": 1, "nombre": "Obra Test"}

        resultado = self.controller.validar_obra_existente(id_obra, mock_obras_model)

        self.assertTrue(resultado)
        mock_obras_model.obtener_obra_por_id.assert_called_once_with(id_obra)

    @patch('modules.vidrios.controller.Logger')
    def test_validar_obra_existente_no_existe(self, mock_logger):
        """Test validar obra que no existe."""
        id_obra = 999
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.return_value = None

        resultado = self.controller.validar_obra_existente(id_obra, mock_obras_model)

        self.assertFalse(resultado)

    @patch('modules.vidrios.controller.Logger')
    def test_validar_obra_existente_id_vacio(self, mock_logger):
        """Test validar obra con ID vacío."""
        mock_obras_model = Mock()

        resultado = self.controller.validar_obra_existente(None, mock_obras_model)
        self.assertFalse(resultado)

        resultado = self.controller.validar_obra_existente("", mock_obras_model)
        self.assertFalse(resultado)

    @patch('modules.vidrios.controller.Logger')
    def test_validar_obra_existente_error(self, mock_logger):
        """Test validar obra con error."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        id_obra = 1
        mock_obras_model = Mock()
        mock_obras_model.obtener_obra_por_id.side_effect = Exception("Error de BD")

        resultado = self.controller.validar_obra_existente(id_obra, mock_obras_model)

        self.assertFalse(resultado)
        mock_logger_instance.error.assert_called_once_with(
            "[ERROR] No se pudo validar existencia de obra: Error de BD"
        )


class TestVidriosControllerGuardarPedido(unittest.TestCase):
    """Tests para guardar pedidos."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = "test_user"

        with patch('modules.vidrios.controller.AuditoriaModel') as mock_auditoria:
            self.mock_auditoria_model = Mock()
            mock_auditoria.return_value = self.mock_auditoria_model
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    def test_guardar_pedido_vidrios_sin_validacion(self):
        """Test guardar pedido sin validación de obra."""
        datos = {"id_obra": 1, "tipo": "Cristal", "cantidad": 5}

        with patch.object(self.controller, 'cargar_pedidos_usuario') as mock_cargar:
            self.controller.guardar_pedido_vidrios(datos)

            self.mock_model.guardar_pedido_vidrios.assert_called_once_with(datos)
            self.mock_auditoria_model.registrar_evento.assert_called_once_with(
                usuario_id=self.mock_usuario,
                modulo="Vidrios",
                tipo_evento="Guardar pedido vidrios",
                detalle=f"Guardó pedido de vidrios: {datos}",
                ip_origen="127.0.0.1"
            )
            mock_cargar.assert_called_once_with(self.mock_usuario)

    def test_guardar_pedido_vidrios_con_validacion_exitosa(self):
        """Test guardar pedido con validación exitosa."""
        datos = {"id_obra": 1, "tipo": "Cristal", "cantidad": 5}
        mock_obras_model = Mock()

        with patch.object(self.controller, 'validar_obra_existente', return_value=True) as mock_validar:
            with patch.object(self.controller, 'cargar_pedidos_usuario') as mock_cargar:
                self.controller.guardar_pedido_vidrios(datos, mock_obras_model)

                mock_validar.assert_called_once_with(1, mock_obras_model)
                self.mock_model.guardar_pedido_vidrios.assert_called_once_with(datos)
                mock_cargar.assert_called_once_with(self.mock_usuario)

    def test_guardar_pedido_vidrios_con_validacion_fallida(self):
        """Test guardar pedido con validación fallida."""
        datos = {"id_obra": 999, "tipo": "Cristal", "cantidad": 5}
        mock_obras_model = Mock()

        with patch.object(self.controller, 'validar_obra_existente', return_value=False) as mock_validar:
            self.controller.guardar_pedido_vidrios(datos, mock_obras_model)

            mock_validar.assert_called_once_with(999, mock_obras_model)
            self.mock_model.guardar_pedido_vidrios.assert_not_called()
            self.mock_view.mostrar_mensaje.assert_called_once_with(
                "No se puede registrar el pedido: la obra 999 no existe.", tipo='error'
            )

    def test_guardar_pedido_vidrios_datos_tupla(self):
        """Test guardar pedido con datos como tupla."""
        datos = (1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")

        with patch.object(self.controller, 'cargar_pedidos_usuario'):
            self.controller.guardar_pedido_vidrios(datos)

            self.mock_model.guardar_pedido_vidrios.assert_called_once_with(datos)


class TestVidriosControllerReservas(unittest.TestCase):
    """Tests para reservas de vidrios."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = "test_user"

        with patch('modules.vidrios.controller.AuditoriaModel') as mock_auditoria:
            self.mock_auditoria_model = Mock()
            mock_auditoria.return_value = self.mock_auditoria_model
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    @patch('modules.obras.model.ObrasModel')
    def test_reservar_vidrio_obra_existe(self, mock_obras_model_class):
        """Test reservar vidrio cuando la obra existe."""
        mock_obras_model = Mock()
        mock_obras_model.existe_obra_por_id.return_value = True
        mock_obras_model_class.return_value = mock_obras_model

        self.mock_model.reservar_vidrio.return_value = True

        resultado = self.controller.reservar_vidrio("test_user", 1, 1, 5)

        mock_obras_model_class.assert_called_once_with(self.mock_model.db)
        mock_obras_model.existe_obra_por_id.assert_called_once_with(1)
        self.mock_model.reservar_vidrio.assert_called_once_with("test_user", 1, 1, 5)
        self.assertTrue(resultado)

    @patch('modules.obras.model.ObrasModel')
    def test_reservar_vidrio_obra_no_existe(self, mock_obras_model_class):
        """Test reservar vidrio cuando la obra no existe."""
        mock_obras_model = Mock()
        mock_obras_model.existe_obra_por_id.return_value = False
        mock_obras_model_class.return_value = mock_obras_model

        resultado = self.controller.reservar_vidrio("test_user", 999, 1, 5)

        mock_obras_model.existe_obra_por_id.assert_called_once_with(999)
        self.mock_model.reservar_vidrio.assert_not_called()
        self.mock_view.mostrar_mensaje.assert_called_once_with(
            "No existe una obra con ese ID. No se puede reservar vidrio.", tipo='error'
        )
        self.mock_auditoria_model.registrar_evento.assert_called_once_with(
            "test_user", "Vidrios", "reserva_vidrio", "Intento de reserva a obra inexistente: 999", "error"
        )
        self.assertFalse(resultado)


class TestVidriosControllerEstados(unittest.TestCase):
    """Tests para obtención de estados."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()

        with patch('modules.vidrios.controller.AuditoriaModel'):
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db)

    @patch('modules.vidrios.controller.Logger')
    def test_obtener_estado_pedidos_por_obra_exitoso(self, mock_logger):
        """Test obtener estado de pedidos exitosamente."""
        self.mock_model.obtener_estado_pedido_por_obra.return_value = "Activo"

        resultado = self.controller.obtener_estado_pedidos_por_obra(1)

        self.assertEqual(resultado, "Activo")
        self.mock_model.obtener_estado_pedido_por_obra.assert_called_once_with(1)

    @patch('modules.vidrios.controller.Logger')
    def test_obtener_estado_pedidos_por_obra_error(self, mock_logger):
        """Test obtener estado de pedidos con error."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        self.mock_model.obtener_estado_pedido_por_obra.side_effect = Exception("Error de BD")

        resultado = self.controller.obtener_estado_pedidos_por_obra(1)

        self.assertEqual(resultado, "error")
        mock_logger_instance.error.assert_called_once_with(
            "[ERROR] Error al obtener estado de pedidos de vidrios para obra 1: Error de BD"
        )

    @patch('modules.vidrios.controller.Logger')
    def test_obtener_pedidos_por_obra_exitoso(self, mock_logger):
        """Test obtener pedidos por obra exitosamente."""
        pedidos_data = [(1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")]
        self.mock_model.obtener_pedidos_por_obra.return_value = pedidos_data

        resultado = self.controller.obtener_pedidos_por_obra(1)

        self.assertEqual(resultado, pedidos_data)
        self.mock_model.obtener_pedidos_por_obra.assert_called_once_with(1)

    @patch('modules.vidrios.controller.Logger')
    def test_obtener_pedidos_por_obra_error(self, mock_logger):
        """Test obtener pedidos por obra con error."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        self.mock_model.obtener_pedidos_por_obra.side_effect = Exception("Error de BD")

        resultado = self.controller.obtener_pedidos_por_obra(1)

        self.assertEqual(resultado, [])
        mock_logger_instance.error.assert_called_once_with(
            "[ERROR] Error al obtener pedidos de vidrios para obra 1: Error de BD"
        )


class TestVidriosControllerPagos(unittest.TestCase):
    """Tests para validación y registro de pagos."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()
        self.mock_usuario = Mock()
        self.mock_usuario.id = 123

        with patch('modules.vidrios.controller.AuditoriaModel') as mock_auditoria:
            self.mock_auditoria_model = Mock()
            mock_auditoria.return_value = self.mock_auditoria_model
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, self.mock_usuario)

    @patch('modules.vidrios.controller.Logger')
    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_exitoso(self, mock_contabilidad_class, mock_logger):
        """Test validar y registrar pago exitosamente."""
        mock_contabilidad = Mock()
        mock_contabilidad_class.return_value = mock_contabilidad

        # Configurar pedidos existentes
        pedidos_data = [(1, 1, "Cristal", 100, 80, "Transparente", "Proveedor A", "2025-01-15", "Sin observaciones", 5, "Activo")]
        self.mock_model.obtener_pedidos_por_obra.return_value = pedidos_data

        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=1, monto=1500.0, fecha="2025-01-20", usuario="test_user"
        )

        self.assertTrue(resultado)
        mock_contabilidad_class.assert_called_once_with(self.mock_model.db)
        mock_contabilidad.registrar_pago_pedido.assert_called_once_with(
            id_pedido=1,
            modulo='vidrios',
            obra_id=1,
            monto=1500.0,
            fecha="2025-01-20",
            usuario="test_user",
            estado='pagado'
        )
        self.mock_auditoria_model.registrar_evento.assert_called_once_with(
            usuario_id=123,
            modulo="Vidrios",
            tipo_evento="Registrar pago pedido",
            detalle="Registró pago de 1500.0 para pedido de vidrios de obra 1",
            ip_origen="127.0.0.1"
        )
        self.mock_view.mostrar_mensaje.assert_called_once_with(
            "Pago de vidrios registrado correctamente para obra 1.", tipo='exito'
        )

    @patch('modules.vidrios.controller.Logger')
    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_sin_pedidos(self, mock_contabilidad_class, mock_logger):
        """Test validar y registrar pago sin pedidos."""
        # Sin pedidos para la obra
        self.mock_model.obtener_pedidos_por_obra.return_value = []

        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=999, monto=1500.0, fecha="2025-01-20", usuario="test_user"
        )

        self.assertFalse(resultado)
        mock_contabilidad_class.assert_called_once_with(self.mock_model.db)
        # Pero no debe llamar a registrar_pago_pedido
        mock_contabilidad = mock_contabilidad_class.return_value
        mock_contabilidad.registrar_pago_pedido.assert_not_called()
        self.mock_view.mostrar_mensaje.assert_called_once_with(
            "No se encontraron pedidos de vidrios para la obra 999.", tipo='error'
        )

    @patch('modules.vidrios.controller.Logger')
    @patch('modules.contabilidad.model.ContabilidadModel')
    def test_validar_y_registrar_pago_pedido_error(self, mock_contabilidad_class, mock_logger):
        """Test validar y registrar pago con error."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Error en contabilidad
        mock_contabilidad_class.side_effect = Exception("Error de contabilidad")

        resultado = self.controller.validar_y_registrar_pago_pedido(
            id_obra=1, monto=1500.0, fecha="2025-01-20", usuario="test_user"
        )

        self.assertFalse(resultado)
        mock_logger_instance.error.assert_called_once_with(
            "[ERROR] Error al registrar pago de pedido de vidrios: Error de contabilidad"
        )
        self.mock_view.mostrar_mensaje.assert_called_once_with(
            "Error al registrar pago: Error de contabilidad", tipo='error'
        )


class TestVidriosControllerEdgeCases(unittest.TestCase):
    """Tests para casos edge y validaciones."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.mock_db = Mock()

        with patch('modules.vidrios.controller.AuditoriaModel'):
            self.controller = VidriosController(self.mock_model, self.mock_view, self.mock_db)

    def test_usuario_sin_atributos(self):
        """Test con usuario sin atributos username o id."""
        usuario_simple = "string_user"

        with patch('modules.vidrios.controller.AuditoriaModel'):
            controller = VidriosController(self.mock_model, self.mock_view, self.mock_db, usuario_simple)

        # Debe manejar graciosamente la falta de atributos
        self.assertEqual(controller.usuario_actual, usuario_simple)

    def test_view_sin_metodos(self):
        """Test con vista sin métodos esperados."""
        view_limitada = Mock()
        delattr(view_limitada, 'mostrar_mensaje')

        with patch('modules.vidrios.controller.AuditoriaModel'):
            controller = VidriosController(self.mock_model, view_limitada, self.mock_db)

        # No debe fallar al intentar mostrar mensaje
        datos_obra = {"nombre": "Obra Test"}
        controller.actualizar_por_obra(datos_obra)  # No debe lanzar excepción


if __name__ == '__main__':
    unittest.main()
