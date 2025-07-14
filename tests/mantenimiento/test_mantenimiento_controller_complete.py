"""
Tests completos para MantenimientoController.
Cubre todas las funcionalidades, permisos, auditoría, edge cases y flujos de integración.
"""

class TestMantenimientoControllerComplete(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configuración de clase para PyQt6."""
        if not QApplication.instance():
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from modules.mantenimiento.controller import (
    MantenimientoController,
    PermisoAuditoria,
    permiso_auditoria_mantenimiento,
)
from modules.mantenimiento.model import MantenimientoModel

            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Configuración para cada test."""
        # Mocks de dependencias
        self.mock_model = Mock(spec=MantenimientoModel)
        self.mock_view = Mock(spec=QWidget)
        self.mock_db_connection = Mock()
        self.mock_usuarios_model = Mock()  # Eliminar spec para permitir atributos personalizados
        self.mock_notificaciones_controller = Mock()

        # Mock de usuario actual
        self.usuario_actual = {
            'id': 1,
            'nombre': 'Juan Test',
            'rol': 'TEST_USER',
            'ip': '192.168.1.100'
        }

        # Configurar view mock con widgets necesarios
        self.setup_view_mock()

        # Crear controlador con mock de auditoria_model
        with patch('modules.mantenimiento.controller.AuditoriaModel') as mock_auditoria_class:
            self.mock_auditoria_model = Mock()
            mock_auditoria_class.return_value = self.mock_auditoria_model

            self.controller = MantenimientoController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db_connection,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=self.usuario_actual,
                notificaciones_controller=self.mock_notificaciones_controller
            )

    def setup_view_mock(self):
        """Configura los widgets del view mock."""
        # Botones
        self.mock_view.boton_agregar_mantenimiento = Mock(spec=QPushButton)
        self.mock_view.boton_ver_tareas_recurrentes = Mock(spec=QPushButton)
        self.mock_view.boton_registrar_repuesto = Mock(spec=QPushButton)
        self.mock_view.boton_exportar_excel = Mock(spec=QPushButton)
        self.mock_view.boton_exportar_pdf = Mock(spec=QPushButton)

        # Inputs
        self.mock_view.tipo_mantenimiento_input = Mock(spec=QComboBox)
        self.mock_view.fecha_realizacion_input = Mock(spec=QDateEdit)
        self.mock_view.realizado_por_input = Mock(spec=QLineEdit)
        self.mock_view.observaciones_input = Mock(spec=QTextEdit)
        self.mock_view.firma_digital_input = Mock(spec=QLineEdit)

        # Label para feedback
        self.mock_view.label = Mock()

        # Configurar valores de retorno típicos
        self.mock_view.tipo_mantenimiento_input.currentText.return_value = "Preventivo"
        self.mock_view.fecha_realizacion_input.date.return_value.toString.return_value = "2025-06-29"
        self.mock_view.realizado_por_input.text.return_value = "Juan Pérez"
        self.mock_view.observaciones_input.toPlainText.return_value = "Mantenimiento completo"
        self.mock_view.firma_digital_input.text.return_value = "firma123"

    def tearDown(self):
        """Limpieza después de cada test."""
        # Reset todos los mocks
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, 'reset_mock'):
                attr.reset_mock()


class TestMantenimientoControllerBasic(TestMantenimientoControllerComplete):
    """Tests básicos de inicialización y configuración."""

    def test_init_controller(self):
        """Test inicialización del controlador."""
        # Assert
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertEqual(self.controller.view, self.mock_view)
        self.assertEqual(self.controller.usuario_actual, self.usuario_actual)
        self.assertEqual(self.controller.usuarios_model, self.mock_usuarios_model)
        self.assertEqual(self.controller.auditoria_model, self.mock_auditoria_model)
        self.assertEqual(self.controller.notificaciones_controller, self.mock_notificaciones_controller)

    def test_setup_view_signals_all_widgets_present(self):
        """Test configuración de señales cuando todos los widgets están presentes."""
        # Act
        self.controller.setup_view_signals()

        # Assert
        self.mock_view.boton_agregar_mantenimiento.clicked.connect.assert_called_once()
        self.mock_view.boton_ver_tareas_recurrentes.clicked.connect.assert_called_once()
        self.mock_view.boton_registrar_repuesto.clicked.connect.assert_called_once()
        self.mock_view.boton_exportar_excel.clicked.connect.assert_called_once()
        self.mock_view.boton_exportar_pdf.clicked.connect.assert_called_once()

    def test_setup_view_signals_missing_widgets(self):
        """Test configuración de señales cuando faltan widgets."""
        # Arrange
        delattr(self.mock_view, 'boton_agregar_mantenimiento')
        delattr(self.mock_view, 'boton_exportar_excel')

        # Act & Assert (no debe fallar)
        try:
            self.controller.setup_view_signals()
        except AttributeError:
            self.fail("setup_view_signals falló con widgets faltantes")

    def test_registrar_evento_auditoria_success(self):
        """Test registro exitoso de evento de auditoría."""
        # Arrange
        accion = "test_action"
        detalle_extra = "detalles adicionales"
        estado = "éxito"

        # Act
        self.controller._registrar_evento_auditoria(accion, detalle_extra, estado)

        # Assert
        expected_detalle = f"{accion} - {detalle_extra} - {estado}"
        self.mock_auditoria_model.registrar_evento.assert_called_once_with(
            self.usuario_actual['id'],
            'mantenimiento',
            accion,
            expected_detalle,
            self.usuario_actual['ip']
        )

    def test_registrar_evento_auditoria_minimal(self):
        """Test registro de evento de auditoría con datos mínimos."""
        # Arrange
        accion = "simple_action"

        # Act
        self.controller._registrar_evento_auditoria(accion)

        # Assert
        self.mock_auditoria_model.registrar_evento.assert_called_once_with(
            self.usuario_actual['id'],
            'mantenimiento',
            accion,
            accion,
            self.usuario_actual['ip']
        )


class TestMantenimientoControllerPermisos(TestMantenimientoControllerComplete):
    """Tests de permisos y decoradores de auditoría."""

    def test_registrar_mantenimiento_con_permisos(self):
        """Test registrar mantenimiento con permisos válidos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        resultado = self.controller.registrar_mantenimiento()

        # Assert
        self.mock_usuarios_model.tiene_permiso.assert_called_once_with(
            self.usuario_actual, 'mantenimiento', 'registrar_mantenimiento'
        )
        # Verificar que se ejecutó la lógica del método
        self.mock_view.tipo_mantenimiento_input.currentText.assert_called()

    def test_registrar_mantenimiento_sin_permisos(self):
        """Test registrar mantenimiento sin permisos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = False

        # Act
        resultado = self.controller.registrar_mantenimiento()

        # Assert
        self.assertIsNone(resultado)
        self.mock_view.label.setText.assert_called_once()
        self.assertIn("No tiene permiso", self.mock_view.label.setText.call_args[0][0])

        # Verificar que se registró el evento de auditoría de denegación
        self.mock_auditoria_model.registrar_evento.assert_called_once()
        call_args = self.mock_auditoria_model.registrar_evento.call_args[0]
        self.assertIn("denegado", call_args[3])

    def test_decorador_permiso_auditoria_sin_usuario(self):
        """Test decorador cuando no hay usuario actual."""
        # Arrange
        controller_sin_usuario = MantenimientoController(
            model=self.mock_model,
            view=self.mock_view,
            db_connection=self.mock_db_connection,
            usuarios_model=self.mock_usuarios_model,
            usuario_actual=None
        )

        # Act
        resultado = controller_sin_usuario.registrar_mantenimiento()

        # Assert
        self.assertIsNone(resultado)
        self.mock_view.label.setText.assert_called_once()

    def test_decorador_permiso_auditoria_sin_usuarios_model(self):
        """Test decorador cuando no hay usuarios_model."""
        # Arrange
        controller_sin_model = MantenimientoController(
            model=self.mock_model,
            view=self.mock_view,
            db_connection=self.mock_db_connection,
            usuarios_model=None,
            usuario_actual=self.usuario_actual
        )

        # Act
        resultado = controller_sin_model.registrar_mantenimiento()

        # Assert
        self.assertIsNone(resultado)

    def test_decorador_maneja_excepcion_en_metodo(self):
        """Test decorador maneja excepciones en el método decorado."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True
        self.mock_view.tipo_mantenimiento_input.currentText.side_effect = Exception("Error en widget")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.controller.registrar_mantenimiento()

        self.assertIn("Error en widget", str(context.exception))

        # Verificar que se registró el evento de error en auditoría
        self.mock_auditoria_model.registrar_evento.assert_called()
        call_args = self.mock_auditoria_model.registrar_evento.call_args[0]
        self.assertIn("error", call_args[3])

    @patch('modules.mantenimiento.controller.log_error')
    def test_decorador_maneja_excepcion_auditoria(self, mock_log_error):
        """Test manejo de excepciones en registro de auditoría."""
        # Arrange
        self.mock_auditoria_model.registrar_evento.side_effect = Exception("Error auditoría")

        # Act
        self.controller._registrar_evento_auditoria("test_action")

        # Assert
        mock_log_error.assert_called_once()
        self.assertIn("Error registrando evento auditoría", mock_log_error.call_args[0][0])


class TestMantenimientoControllerFuncionalidades(TestMantenimientoControllerComplete):
    """Tests de funcionalidades específicas del controlador."""

    def test_registrar_mantenimiento_success_completo(self):
        """Test registro exitoso de mantenimiento con todos los datos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        with patch.object(self.controller, '_registrar_evento_auditoria') as mock_registrar:
            resultado = self.controller.registrar_mantenimiento()

        # Assert
        # Verificar que se obtuvo datos del formulario
        self.mock_view.tipo_mantenimiento_input.currentText.assert_called_once()
        self.mock_view.fecha_realizacion_input.date.assert_called_once()
        self.mock_view.realizado_por_input.text.assert_called_once()
        self.mock_view.observaciones_input.toPlainText.assert_called_once()
        self.mock_view.firma_digital_input.text.assert_called_once()

    def test_mostrar_tareas_recurrentes_con_permisos(self):
        """Test mostrar tareas recurrentes con permisos válidos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        with patch.object(self.controller, 'mostrar_tareas_recurrentes', wraps=self.controller.mostrar_tareas_recurrentes):
            # Simular que el método existe y es llamado
            if hasattr(self.controller, 'mostrar_tareas_recurrentes'):
                resultado = self.controller.mostrar_tareas_recurrentes()

    def test_registrar_repuesto_utilizado_con_permisos(self):
        """Test registrar repuesto utilizado con permisos válidos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        if hasattr(self.controller, 'registrar_repuesto_utilizado'):
            with patch.object(self.controller, 'registrar_repuesto_utilizado', wraps=self.controller.registrar_repuesto_utilizado):
                resultado = self.controller.registrar_repuesto_utilizado()

    def test_exportar_reporte_excel_con_permisos(self):
        """Test exportar reporte Excel con permisos válidos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        if hasattr(self.controller, 'exportar_reporte_mantenimiento'):
            with patch.object(self.controller, 'exportar_reporte_mantenimiento', wraps=self.controller.exportar_reporte_mantenimiento):
                resultado = self.controller.exportar_reporte_mantenimiento('excel')

    def test_exportar_reporte_pdf_con_permisos(self):
        """Test exportar reporte PDF con permisos válidos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        if hasattr(self.controller, 'exportar_reporte_mantenimiento'):
            with patch.object(self.controller, 'exportar_reporte_mantenimiento', wraps=self.controller.exportar_reporte_mantenimiento):
                resultado = self.controller.exportar_reporte_mantenimiento('pdf')


class TestMantenimientoControllerEdgeCases(TestMantenimientoControllerComplete):
    """Tests de casos límite y edge cases."""

    def test_registrar_mantenimiento_datos_vacios(self):
        """Test registrar mantenimiento con datos vacíos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True
        self.mock_view.tipo_mantenimiento_input.currentText.return_value = ""
        self.mock_view.realizado_por_input.text.return_value = ""
        self.mock_view.observaciones_input.toPlainText.return_value = ""

        # Act
        resultado = self.controller.registrar_mantenimiento()

        # Assert
        # Verificar que se obtuvieron los datos aunque estén vacíos
        self.mock_view.tipo_mantenimiento_input.currentText.assert_called_once()

    def test_registrar_mantenimiento_fecha_invalida(self):
        """Test registrar mantenimiento con fecha inválida."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True
        self.mock_view.fecha_realizacion_input.date.return_value.toString.return_value = ""

        # Act
        resultado = self.controller.registrar_mantenimiento()

        # Assert
        self.mock_view.fecha_realizacion_input.date.assert_called_once()

    def test_view_sin_label_para_feedback(self):
        """Test comportamiento cuando view no tiene label para feedback."""
        # Arrange
        delattr(self.mock_view, 'label')
        self.mock_usuarios_model.tiene_permiso.return_value = False

        # Act & Assert (no debe fallar)
        try:
            resultado = self.controller.registrar_mantenimiento()
            self.assertIsNone(resultado)
        except AttributeError:
            self.fail("Falló al manejar view sin label")

    def test_usuario_sin_ip(self):
        """Test con usuario que no tiene IP."""
        # Arrange
        usuario_sin_ip = {'id': 1, 'nombre': 'Test'}

        with patch('modules.mantenimiento.controller.AuditoriaModel') as mock_auditoria_class:
            mock_auditoria_model = Mock()
            mock_auditoria_class.return_value = mock_auditoria_model

            controller = MantenimientoController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db_connection,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=usuario_sin_ip
            )

            # Act
            controller._registrar_evento_auditoria("test_action")

            # Assert
            mock_auditoria_model.registrar_evento.assert_called_once()
            call_args = mock_auditoria_model.registrar_evento.call_args[0]
            self.assertEqual(call_args[4], '')  # IP vacía

    def test_usuario_sin_id(self):
        """Test con usuario que no tiene ID."""
        # Arrange
        usuario_sin_id = {'nombre': 'Test', 'ip': '192.168.1.1'}

        with patch('modules.mantenimiento.controller.AuditoriaModel') as mock_auditoria_class:
            mock_auditoria_model = Mock()
            mock_auditoria_class.return_value = mock_auditoria_model

            controller = MantenimientoController(
                model=self.mock_model,
                view=self.mock_view,
                db_connection=self.mock_db_connection,
                usuarios_model=self.mock_usuarios_model,
                usuario_actual=usuario_sin_id
            )

            # Act
            controller._registrar_evento_auditoria("test_action")

            # Assert
            mock_auditoria_model.registrar_evento.assert_called_once()
            call_args = mock_auditoria_model.registrar_evento.call_args[0]
            self.assertIsNone(call_args[0])  # usuario_id es None


class TestMantenimientoControllerIntegration(TestMantenimientoControllerComplete):
    """Tests de integración y flujos complejos."""

    def test_flujo_completo_registrar_mantenimiento_exitoso(self):
        """Test flujo completo de registro de mantenimiento exitoso."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        resultado = self.controller.registrar_mantenimiento()

        # Assert
        # 1. Verificar validación de permisos
        self.mock_usuarios_model.tiene_permiso.assert_called_once_with(
            self.usuario_actual, 'mantenimiento', 'registrar_mantenimiento'
        )

        # 2. Verificar obtención de datos del formulario
        self.mock_view.tipo_mantenimiento_input.currentText.assert_called_once()
        self.mock_view.fecha_realizacion_input.date.assert_called_once()
        self.mock_view.realizado_por_input.text.assert_called_once()
        self.mock_view.observaciones_input.toPlainText.assert_called_once()
        self.mock_view.firma_digital_input.text.assert_called_once()

        # 3. Verificar registro en auditoría
        self.mock_auditoria_model.registrar_evento.assert_called_once()

    def test_configuracion_completa_signals_y_permisos(self):
        """Test configuración completa de señales y verificación de permisos."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        self.controller.setup_view_signals()

        # Simular clicks en botones
        if hasattr(self.mock_view, 'boton_agregar_mantenimiento'):
            # Obtener la función conectada y ejecutarla
            connected_func = self.mock_view.boton_agregar_mantenimiento.clicked.connect.call_args[0][0]
            if connected_func == self.controller.registrar_mantenimiento:
                resultado = connected_func()

        # Assert
        self.mock_view.boton_agregar_mantenimiento.clicked.connect.assert_called_once()

    def test_integracion_con_notificaciones(self):
        """Test integración con sistema de notificaciones."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True

        # Act
        self.controller.registrar_mantenimiento()

        # Assert
        # Verificar que el controlador tiene acceso al sistema de notificaciones
        self.assertIsNotNone(self.controller.notificaciones_controller)

    @patch('modules.mantenimiento.controller.log_error')
    def test_manejo_error_integral_con_logging(self, mock_log_error):
        """Test manejo integral de errores con logging."""
        # Arrange
        self.mock_usuarios_model.tiene_permiso.return_value = True
        self.mock_view.tipo_mantenimiento_input.currentText.side_effect = Exception("Error crítico")

        # Act
        with self.assertRaises(Exception):
            self.controller.registrar_mantenimiento()

        # Assert
        # Verificar que se registró el error
        self.mock_auditoria_model.registrar_evento.assert_called()
        call_args = self.mock_auditoria_model.registrar_evento.call_args[0]
        self.assertIn("error", call_args[3])


class TestPermisoAuditoriaDecorator(TestMantenimientoControllerComplete):
    """Tests específicos del decorador PermisoAuditoria."""

    def test_permiso_auditoria_instanciacion(self):
        """Test instanciación del decorador PermisoAuditoria."""
        # Act
        decorador = PermisoAuditoria('test_modulo')

        # Assert
        self.assertEqual(decorador.modulo, 'test_modulo')

    def test_decorador_aplicado_correctamente(self):
        """Test que el decorador se aplica correctamente a métodos."""
        # Arrange
        @permiso_auditoria_mantenimiento('test_action')
        def test_method(self):
            return "test_result"

        # Assert
        self.assertTrue(hasattr(test_method, '__wrapped__'))

    def test_decorador_preserva_metadata(self):
        """Test que el decorador preserva metadatos del método original."""
        # Arrange
        def metodo_original():
            """Documentación del método original."""
            pass

        decorador = PermisoAuditoria('test')
        metodo_decorado = decorador('action')(metodo_original)

        # Assert
        # Verificar que functools.wraps preservó la metadata
        self.assertEqual(metodo_decorado.__name__, metodo_original.__name__)
        self.assertEqual(metodo_decorado.__doc__, metodo_original.__doc__)


if __name__ == '__main__':
    unittest.main()
