"""
Tests exhaustivos para la Vista de Vidrios - VERSIÓN CORREGIDA.
Cobertura completa de inicialización, eventos, formularios, tablas, feedback,
exportación, QR, configuración de columnas, y edge cases.
"""

# Configurar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock global antes de importar
sys.modules['qrcode'] = Mock()
sys.modules['reportlab'] = Mock()
sys.modules['reportlab.pdfgen'] = Mock()
sys.modules['reportlab.lib'] = Mock()
sys.modules['reportlab.lib.pagesizes'] = Mock()
sys.modules['reportlab.pdfgen.canvas'] = Mock()

# Patch de event_bus antes del import de VidriosView
with patch('modules.vidrios.view.event_bus') as mock_event_bus:
    mock_event_bus.obra_agregada = Mock()
    mock_event_bus.obra_agregada.connect = Mock()
@pytest.fixture
def app():
    """Fixture para QApplication."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_controller():
    """Fixture para controlador mock."""
    controller = Mock()
    controller.cargar_resumen_obras = Mock()
    controller.cargar_pedidos_usuario = Mock()
    controller.actualizar_estado_pedido = Mock()
    controller.guardar_pedido_vidrios = Mock()
    controller.mostrar_detalle_pedido = Mock()
    return controller


@pytest.fixture
def vidrios_view(app, mock_controller):
    """Fixture para VidriosView con controlador mock."""
    def real_qicon(*args, **kwargs):
        return QIcon()
    with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
         patch('modules.vidrios.view.estilizar_boton_icono'), \
         patch('utils.theme_manager.cargar_modo_tema', return_value='light'), \
         patch('modules.vidrios.view.QIcon', side_effect=real_qicon):
        view = VidriosView(
            usuario_actual="test_user",
            headers_dinamicos=["id_obra", "tipo", "ancho", "alto", "color"],
            controller=mock_controller
"""
        yield view
        view.close()


class TestVidriosViewInicializacion:
    """Tests para la inicialización de la vista."""

    def test_init_basico(self, app):
        """Test inicialización básica sin controlador."""
        def real_qicon(*args, **kwargs):
            return QIcon()
        with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
             patch('modules.vidrios.view.estilizar_boton_icono'), \
             patch('utils.theme_manager.cargar_modo_tema', return_value='light'), \
             patch('modules.vidrios.view.QIcon', side_effect=real_qicon):

            view = VidriosView()

            assert view.usuario_actual == "default"
            assert view.controller is None
            assert hasattr(view, 'main_layout')
            assert hasattr(view, 'tabs')
            assert hasattr(view, 'tabla_obras')
            assert hasattr(view, 'tabla_pedidos_usuario')
            assert hasattr(view, 'tabla_pedido')
            view.close()

    def test_init_con_parametros(self, app, mock_controller):
        """Test inicialización con parámetros personalizados."""
        headers_custom = ["id", "tipo", "cantidad"]
        def real_qicon(*args, **kwargs):
            return QIcon()
        with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
             patch('modules.vidrios.view.estilizar_boton_icono'), \
             patch('utils.theme_manager.cargar_modo_tema', return_value='dark'), \
             patch('modules.vidrios.view.QIcon', side_effect=real_qicon):

            view = VidriosView(
                usuario_actual="custom_user",
                headers_dinamicos=headers_custom,
                controller=mock_controller
            )

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import json
import os
import sys
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest
from rexus.modules.vidrios.view import VidriosView
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QWidget

            assert view.usuario_actual == "custom_user"
            assert view.controller == mock_controller
            assert view.vidrios_headers == headers_custom
            view.close()

    def test_init_event_bus_conexion(self, app, mock_controller):
        """Test que event_bus se conecta correctamente."""
        with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
             patch('modules.vidrios.view.estilizar_boton_icono'), \
             patch('utils.theme_manager.cargar_modo_tema', return_value='light'), \
             patch('modules.vidrios.view.QIcon'):

            mock_signal = Mock()
            mock_event_bus.obra_agregada = mock_signal

            view = VidriosView(controller=mock_controller)

            # Verificar que se conectó al event bus
            mock_signal.connect.assert_called_once()
            view.close()

    def test_init_componentes_ui(self, vidrios_view):
        """Test que todos los componentes UI se inicializan."""
        view = vidrios_view

        # Verificar elementos principales
        assert hasattr(view, 'tabs')
        assert hasattr(view, 'tabla_obras')
        assert hasattr(view, 'tabla_pedidos_usuario')
        assert hasattr(view, 'tabla_pedido')

        # Verificar botones principales
        assert hasattr(view, 'boton_buscar')
        assert hasattr(view, 'boton_nuevo_pedido')
        assert hasattr(view, 'boton_exportar')
        assert hasattr(view, 'boton_mostrar_qr')

        # Verificar inputs de búsqueda
        assert hasattr(view, 'input_buscar_obra')
        assert hasattr(view, 'input_buscar_pedido')


class TestVidriosViewEventosTablas:
    """Tests para eventos de tablas."""

    def test_on_obra_seleccionada(self, vidrios_view):
        """Test selección de obra."""
        view = vidrios_view

        # Mock de datos de obra
        obra_data = {
            'id_obra': 1,
            'nombre': 'Obra Test',
            'cliente': 'Cliente Test'
        }

        with patch.object(view, 'obtener_datos_fila_seleccionada', return_value=obra_data), \
             patch.object(view, 'cargar_detalles_obra') as mock_cargar:

            view.on_obra_seleccionada()
            mock_cargar.assert_called_once_with(obra_data)

    def test_on_pedido_seleccionado(self, vidrios_view):
        """Test selección de pedido."""
        view = vidrios_view

        pedido_data = {
            'id_pedido': 1,
            'fecha': '2024-01-01',
            'estado': 'pendiente'
        }

        with patch.object(view, 'obtener_datos_fila_seleccionada', return_value=pedido_data), \
             patch.object(view, 'cargar_detalle_pedido') as mock_cargar:

            view.on_pedido_seleccionado()
            mock_cargar.assert_called_once_with(pedido_data)

    def test_on_item_pedido_doble_click(self, vidrios_view):
        """Test doble click en item de pedido."""
        view = vidrios_view

        item_data = {
            'id_item': 1,
            'tipo': 'vidrio_simple',
            'cantidad': 5
        }

        with patch.object(view, 'obtener_datos_fila_seleccionada', return_value=item_data), \
             patch.object(view, 'editar_item_pedido') as mock_editar:

            view.on_item_pedido_doble_click()
            mock_editar.assert_called_once_with(item_data)

    def test_cambio_tab_obras(self, vidrios_view):
        """Test cambio a tab de obras."""
        view = vidrios_view

        with patch.object(view.controller, 'cargar_resumen_obras') as mock_cargar:
            view.cambio_tab(0)  # Tab de obras
            mock_cargar.assert_called_once()

    def test_cambio_tab_pedidos(self, vidrios_view):
        """Test cambio a tab de pedidos."""
        view = vidrios_view

        with patch.object(view.controller, 'cargar_pedidos_usuario') as mock_cargar:
            view.cambio_tab(1)  # Tab de pedidos
            mock_cargar.assert_called_once_with("test_user")


class TestVidriosViewFormularios:
    """Tests para formularios de la vista."""

    def test_abrir_dialogo_nuevo_pedido(self, vidrios_view):
        """Test apertura de diálogo para nuevo pedido."""
        view = vidrios_view

        with patch('modules.vidrios.view.QDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog_class.return_value = mock_dialog

            with patch.object(view, 'crear_formulario_pedido') as mock_crear_form, \
                 patch.object(view, 'procesar_nuevo_pedido') as mock_procesar:

                view.abrir_dialogo_nuevo_pedido()

                mock_crear_form.assert_called_once()
                mock_procesar.assert_called_once()

    def test_crear_formulario_pedido(self, vidrios_view):
        """Test creación de formulario de pedido."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFormLayout') as mock_layout:
            mock_dialog = Mock()

            view.crear_formulario_pedido(mock_dialog)

            # Verificar que se creó el layout
            mock_layout.assert_called_once()

    def test_procesar_nuevo_pedido_valido(self, vidrios_view):
        """Test procesamiento de nuevo pedido válido."""
        view = vidrios_view

        mock_dialog = Mock()

        # Mock de inputs con datos válidos
        view.input_cliente = Mock()
        view.input_cliente.text.return_value = "Cliente Test"
        view.input_fecha_entrega = Mock()
        view.input_fecha_entrega.date.return_value.toString.return_value = "2024-12-31"

        with patch.object(view.controller, 'guardar_pedido_vidrios') as mock_guardar, \
             patch.object(view, 'mostrar_mensaje_exito') as mock_exito:

            mock_guardar.return_value = True

            view.procesar_nuevo_pedido(mock_dialog)

            mock_guardar.assert_called_once()
            mock_exito.assert_called_once()

    def test_procesar_nuevo_pedido_invalido(self, vidrios_view):
        """Test procesamiento de nuevo pedido con datos inválidos."""
        view = vidrios_view

        mock_dialog = Mock()

        # Mock de inputs con datos inválidos
        view.input_cliente = Mock()
        view.input_cliente.text.return_value = ""  # Cliente vacío

        with patch.object(view, 'mostrar_mensaje_error') as mock_error:

            view.procesar_nuevo_pedido(mock_dialog)

            mock_error.assert_called_once()

    def test_validar_formulario_pedido_correcto(self, vidrios_view):
        """Test validación exitosa de formulario."""
        view = vidrios_view

        # Mock de inputs válidos
        view.input_cliente = Mock()
        view.input_cliente.text.return_value = "Cliente Valid"
        view.input_fecha_entrega = Mock()
        view.input_fecha_entrega.date.return_value.toString.return_value = "2024-12-31"

        resultado = view.validar_formulario_pedido()
        assert resultado is True

    def test_validar_formulario_pedido_incorrecto(self, vidrios_view):
        """Test validación fallida de formulario."""
        view = vidrios_view

        # Mock de inputs inválidos
        view.input_cliente = Mock()
        view.input_cliente.text.return_value = ""  # Cliente vacío

        resultado = view.validar_formulario_pedido()
        assert resultado is False


class TestVidriosViewBusqueda:
    """Tests para funcionalidad de búsqueda."""

    def test_buscar_obras(self, vidrios_view):
        """Test búsqueda de obras."""
        view = vidrios_view

        view.input_buscar_obra.setText("test obra")

        with patch.object(view.controller, 'buscar_obras') as mock_buscar, \
             patch.object(view, 'actualizar_tabla_obras') as mock_actualizar:

            mock_buscar.return_value = [{'id': 1, 'nombre': 'Test Obra'}]

            view.buscar_obras()

            mock_buscar.assert_called_once_with("test obra")
            mock_actualizar.assert_called_once()

    def test_buscar_pedidos(self, vidrios_view):
        """Test búsqueda de pedidos."""
        view = vidrios_view

        view.input_buscar_pedido.setText("test pedido")

        with patch.object(view.controller, 'buscar_pedidos') as mock_buscar, \
             patch.object(view, 'actualizar_tabla_pedidos') as mock_actualizar:

            mock_buscar.return_value = [{'id': 1, 'cliente': 'Test Client'}]

            view.buscar_pedidos()

            mock_buscar.assert_called_once_with("test pedido")
            mock_actualizar.assert_called_once()

    def test_limpiar_busqueda_obras(self, vidrios_view):
        """Test limpieza de búsqueda de obras."""
        view = vidrios_view

        view.input_buscar_obra.setText("texto busqueda")

        with patch.object(view.controller, 'cargar_resumen_obras') as mock_cargar:
            view.limpiar_busqueda_obras()

            assert view.input_buscar_obra.text() == ""
            mock_cargar.assert_called_once()

    def test_limpiar_busqueda_pedidos(self, vidrios_view):
        """Test limpieza de búsqueda de pedidos."""
        view = vidrios_view

        view.input_buscar_pedido.setText("texto busqueda")

        with patch.object(view.controller, 'cargar_pedidos_usuario') as mock_cargar:
            view.limpiar_busqueda_pedidos()

            assert view.input_buscar_pedido.text() == ""
            mock_cargar.assert_called_once_with("test_user")


class TestVidriosViewTablas:
    """Tests para manejo de tablas."""

    def test_actualizar_tabla_obras(self, vidrios_view):
        """Test actualización de tabla de obras."""
        view = vidrios_view

        datos = [
            {'id_obra': 1, 'nombre': 'Obra 1', 'cliente': 'Cliente 1'},
            {'id_obra': 2, 'nombre': 'Obra 2', 'cliente': 'Cliente 2'}
        ]

        view.actualizar_tabla_obras(datos)

        assert view.tabla_obras.rowCount() == 2

    def test_actualizar_tabla_pedidos(self, vidrios_view):
        """Test actualización de tabla de pedidos."""
        view = vidrios_view

        datos = [
            {'id_pedido': 1, 'cliente': 'Cliente 1', 'estado': 'pendiente'},
            {'id_pedido': 2, 'cliente': 'Cliente 2', 'estado': 'completado'}
        ]

        view.actualizar_tabla_pedidos(datos)

        assert view.tabla_pedidos_usuario.rowCount() == 2

    def test_actualizar_tabla_detalle_pedido(self, vidrios_view):
        """Test actualización de tabla de detalle de pedido."""
        view = vidrios_view

        datos = [
            {'id_item': 1, 'tipo': 'vidrio_simple', 'cantidad': 5},
            {'id_item': 2, 'tipo': 'vidrio_doble', 'cantidad': 3}
        ]

        view.actualizar_tabla_detalle_pedido(datos)

        assert view.tabla_pedido.rowCount() == 2

    def test_obtener_datos_fila_seleccionada(self, vidrios_view):
        """Test obtención de datos de fila seleccionada."""
        view = vidrios_view

        # Simular tabla con datos
        tabla = view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(3)

        # Mock de selección
        with patch.object(tabla, 'currentRow', return_value=0), \
             patch.object(tabla, 'item') as mock_item:

            mock_item.return_value.text.return_value = "test_value"

            resultado = view.obtener_datos_fila_seleccionada(tabla)

            assert isinstance(resultado, dict)

    def test_limpiar_tabla(self, vidrios_view):
        """Test limpieza de tabla."""
        view = vidrios_view

        tabla = view.tabla_obras
        tabla.setRowCount(5)

        view.limpiar_tabla(tabla)

        assert tabla.rowCount() == 0


class TestVidriosViewFeedback:
    """Tests para sistema de feedback."""

    def test_mostrar_mensaje_exito(self, vidrios_view):
        """Test mostrar mensaje de éxito."""
        view = vidrios_view

        with patch('modules.vidrios.view.QMessageBox') as mock_msgbox:
            view.mostrar_mensaje_exito("Operación exitosa")

            mock_msgbox.information.assert_called_once()

    def test_mostrar_mensaje_error(self, vidrios_view):
        """Test mostrar mensaje de error."""
        view = vidrios_view

        with patch('modules.vidrios.view.QMessageBox') as mock_msgbox:
            view.mostrar_mensaje_error("Error en operación")

            mock_msgbox.critical.assert_called_once()

    def test_mostrar_mensaje_advertencia(self, vidrios_view):
        """Test mostrar mensaje de advertencia."""
        view = vidrios_view

        with patch('modules.vidrios.view.QMessageBox') as mock_msgbox:
            view.mostrar_mensaje_advertencia("Advertencia importante")

            mock_msgbox.warning.assert_called_once()

    def test_confirmar_accion(self, vidrios_view):
        """Test confirmación de acción."""
        view = vidrios_view

        with patch('modules.vidrios.view.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = QMessageBox.StandardButton.Yes

            resultado = view.confirmar_accion("¿Confirmar acción?")

            assert resultado is True
            mock_msgbox.question.assert_called_once()

    def test_mostrar_progreso(self, vidrios_view):
        """Test mostrar barra de progreso."""
        view = vidrios_view

        with patch('modules.vidrios.view.QProgressDialog') as mock_progress:
            mock_dialog = Mock()
            mock_progress.return_value = mock_dialog

            view.mostrar_progreso("Procesando...", 100)

            mock_progress.assert_called_once()


class TestVidriosViewExportacion:
    """Tests para funcionalidad de exportación."""

    def test_exportar_a_excel(self, vidrios_view):
        """Test exportación a Excel."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog, \
             patch('pandas.DataFrame') as mock_df:

            mock_dialog.getSaveFileName.return_value = ("test.xlsx", "Excel files")
            mock_df_instance = Mock()
            mock_df.return_value = mock_df_instance

            datos = [{'col1': 'val1', 'col2': 'val2'}]

            view.exportar_a_excel(datos)

            mock_df_instance.to_excel.assert_called_once_with("test.xlsx", index=False)

    def test_exportar_a_pdf(self, vidrios_view):
        """Test exportación a PDF."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog, \
             patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:

            mock_dialog.getSaveFileName.return_value = ("test.pdf", "PDF files")
            mock_canvas_instance = Mock()
            mock_canvas.return_value = mock_canvas_instance

            datos = [{'col1': 'val1', 'col2': 'val2'}]

            view.exportar_a_pdf(datos)

            mock_canvas_instance.save.assert_called_once()

    def test_exportar_seleccion_tabla(self, vidrios_view):
        """Test exportación de selección de tabla."""
        view = vidrios_view

        tabla = view.tabla_obras
        tabla.setRowCount(3)
        tabla.setColumnCount(2)

        with patch.object(tabla, 'selectedRanges') as mock_ranges, \
             patch.object(view, 'exportar_a_excel') as mock_export:

            # Mock de rango seleccionado
            mock_range = Mock()
            mock_range.topRow.return_value = 0
            mock_range.bottomRow.return_value = 1
            mock_ranges.return_value = [mock_range]

            view.exportar_seleccion_tabla(tabla)

            mock_export.assert_called_once()


class TestVidriosViewQR:
    """Tests para funcionalidad de códigos QR."""

    def test_generar_qr_obra(self, vidrios_view):
        """Test generación de QR para obra."""
        view = vidrios_view

        obra_data = {'id_obra': 1, 'nombre': 'Obra Test'}

        with patch('qrcode.QRCode') as mock_qr_class:
            mock_qr = Mock()
            mock_img = Mock()
            mock_qr.make_image.return_value = mock_img
            mock_qr_class.return_value = mock_qr

            qr_image = view.generar_qr_obra(obra_data)

            assert qr_image == mock_img
            mock_qr.add_data.assert_called_once()

    def test_mostrar_qr_dialog(self, vidrios_view):
        """Test mostrar diálogo de QR."""
        view = vidrios_view

        with patch('modules.vidrios.view.QDialog') as mock_dialog_class, \
             patch('modules.vidrios.view.QLabel') as mock_label, \
             patch.object(view, 'generar_qr_obra') as mock_generar:

            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog
            mock_generar.return_value = Mock()

            obra_data = {'id_obra': 1, 'nombre': 'Obra Test'}

            view.mostrar_qr_dialog(obra_data)

            mock_dialog.exec.assert_called_once()

    def test_guardar_qr_imagen(self, vidrios_view):
        """Test guardar imagen QR."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog:
            mock_dialog.getSaveFileName.return_value = ("test_qr.png", "PNG files")

            mock_qr_image = Mock()

            view.guardar_qr_imagen(mock_qr_image)

            mock_qr_image.save.assert_called_once_with("test_qr.png")


class TestVidriosViewConfiguracion:
    """Tests para configuración de la vista."""

    def test_configurar_columnas_tabla(self, vidrios_view):
        """Test configuración de columnas de tabla."""
        view = vidrios_view

        tabla = view.tabla_obras
        columnas = ["ID", "Nombre", "Cliente", "Estado"]

        view.configurar_columnas_tabla(tabla, columnas)

        assert tabla.columnCount() == len(columnas)

    def test_mostrar_menu_columnas(self, vidrios_view):
        """Test mostrar menú de configuración de columnas."""
        view = vidrios_view

        with patch('modules.vidrios.view.QMenu') as mock_menu_class, \
             patch('modules.vidrios.view.QAction') as mock_action_class:

            mock_menu = Mock()
            mock_menu_class.return_value = mock_menu

            tabla = view.tabla_obras
            punto = QPoint(10, 10)

            view.mostrar_menu_columnas(tabla, punto)

            mock_menu.exec.assert_called_once()

    def test_toggle_columna_visibilidad(self, vidrios_view):
        """Test toggle de visibilidad de columna."""
        view = vidrios_view

        tabla = view.tabla_obras
        tabla.setColumnCount(3)

        # Hacer columna invisible
        view.toggle_columna_visibilidad(tabla, 1, False)
        assert tabla.isColumnHidden(1) is True

        # Hacer columna visible
        view.toggle_columna_visibilidad(tabla, 1, True)
        assert tabla.isColumnHidden(1) is False

    def test_guardar_configuracion_columnas(self, vidrios_view):
        """Test guardar configuración de columnas."""
        view = vidrios_view

        config = {
            'columnas_visibles': [0, 1, 3],
            'orden_columnas': ['id', 'nombre', 'estado']
        }

        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_json_dump:

            view.guardar_configuracion_columnas("tabla_obras", config)

            mock_file.assert_called_once()
            mock_json_dump.assert_called_once()

    def test_cargar_configuracion_columnas(self, vidrios_view):
        """Test cargar configuración de columnas."""
        view = vidrios_view

        config_data = '{"columnas_visibles": [0, 1, 3], "orden_columnas": ["id", "nombre", "estado"]}'

        with patch('builtins.open', mock_open(read_data=config_data)), \
             patch('json.load') as mock_json_load:

            mock_json_load.return_value = json.loads(config_data)

            resultado = view.cargar_configuracion_columnas("tabla_obras")

            assert 'columnas_visibles' in resultado
            assert 'orden_columnas' in resultado


class TestVidriosViewEdgeCases:
    """Tests para casos edge y manejo de errores."""

    def test_error_conexion_bd(self, vidrios_view):
        """Test manejo de error de conexión a BD."""
        view = vidrios_view

        with patch.object(view.controller, 'cargar_resumen_obras') as mock_cargar, \
             patch.object(view, 'mostrar_mensaje_error') as mock_error:

            mock_cargar.side_effect = Exception("Error de conexión")

            view.cambio_tab(0)  # Tab de obras

            mock_error.assert_called_once()

    def test_datos_vacios_tabla(self, vidrios_view):
        """Test manejo de datos vacíos en tabla."""
        view = vidrios_view

        datos_vacios = []

        view.actualizar_tabla_obras(datos_vacios)

        assert view.tabla_obras.rowCount() == 0

    def test_seleccion_vacia_tabla(self, vidrios_view):
        """Test manejo de selección vacía en tabla."""
        view = vidrios_view

        tabla = view.tabla_obras

        with patch.object(tabla, 'currentRow', return_value=-1), \
             patch.object(view, 'mostrar_mensaje_advertencia') as mock_warning:

            view.on_obra_seleccionada()

            mock_warning.assert_called_once()

    def test_archivo_no_encontrado_exportacion(self, vidrios_view):
        """Test manejo de archivo no encontrado en exportación."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog, \
             patch.object(view, 'mostrar_mensaje_error') as mock_error:

            mock_dialog.getSaveFileName.return_value = ("", "")  # Usuario cancela

            datos = [{'col1': 'val1'}]
            view.exportar_a_excel(datos)

            # No debe llamar a mostrar error si usuario cancela
            mock_error.assert_not_called()

    def test_datos_invalidos_formulario(self, vidrios_view):
        """Test manejo de datos inválidos en formulario."""
        view = vidrios_view

        # Mock de inputs con datos problemáticos
        view.input_cliente = Mock()
        view.input_cliente.text.return_value = "   "  # Solo espacios

        with patch.object(view, 'mostrar_mensaje_error') as mock_error:

            resultado = view.validar_formulario_pedido()

            assert resultado is False

    def test_timeout_operacion_larga(self, vidrios_view):
        """Test manejo de timeout en operación larga."""
        view = vidrios_view

        with patch.object(view.controller, 'guardar_pedido_vidrios') as mock_guardar, \
             patch.object(view, 'mostrar_mensaje_error') as mock_error:

            mock_guardar.side_effect = TimeoutError("Operación timeout")

            mock_dialog = Mock()
            view.input_cliente = Mock()
            view.input_cliente.text.return_value = "Cliente Test"
            view.input_fecha_entrega = Mock()
            view.input_fecha_entrega.date.return_value.toString.return_value = "2024-12-31"

            view.procesar_nuevo_pedido(mock_dialog)

            mock_error.assert_called_once()

    def test_memoria_insuficiente_exportacion(self, vidrios_view):
        """Test manejo de memoria insuficiente en exportación."""
        view = vidrios_view

        with patch('pandas.DataFrame') as mock_df, \
             patch.object(view, 'mostrar_mensaje_error') as mock_error:

            mock_df.side_effect = MemoryError("Memoria insuficiente")

            datos_grandes = [{'col1': f'val{i}'} for i in range(1000000)]  # Datos grandes

            view.exportar_a_excel(datos_grandes)

            mock_error.assert_called_once()

    def test_permisos_archivo_exportacion(self, vidrios_view):
        """Test manejo de permisos insuficientes en exportación."""
        view = vidrios_view

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog, \
             patch('pandas.DataFrame') as mock_df, \
             patch.object(view, 'mostrar_mensaje_error') as mock_error:

            mock_dialog.getSaveFileName.return_value = ("readonly.xlsx", "Excel files")
            mock_df_instance = Mock()
            mock_df.return_value = mock_df_instance
            mock_df_instance.to_excel.side_effect = PermissionError("Sin permisos")

            datos = [{'col1': 'val1'}]

            view.exportar_a_excel(datos)

            mock_error.assert_called_once()


class TestVidriosViewIntegracion:
    """Tests de integración y flujos completos."""

    def test_flujo_completo_nuevo_pedido(self, vidrios_view):
        """Test flujo completo de creación de nuevo pedido."""
        view = vidrios_view

        # Simular apertura de diálogo
        with patch('modules.vidrios.view.QDialog') as mock_dialog_class, \
             patch.object(view, 'crear_formulario_pedido') as mock_crear_form, \
             patch.object(view, 'validar_formulario_pedido', return_value=True) as mock_validar, \
             patch.object(view.controller, 'guardar_pedido_vidrios', return_value=True) as mock_guardar, \
             patch.object(view, 'mostrar_mensaje_exito') as mock_exito, \
             patch.object(view.controller, 'cargar_pedidos_usuario') as mock_reload:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog_class.return_value = mock_dialog

            # Mock de inputs
            view.input_cliente = Mock()
            view.input_cliente.text.return_value = "Cliente Test"
            view.input_fecha_entrega = Mock()
            view.input_fecha_entrega.date.return_value.toString.return_value = "2024-12-31"

            # Ejecutar flujo
            view.abrir_dialogo_nuevo_pedido()

            # Verificar secuencia
            mock_crear_form.assert_called_once()
            mock_validar.assert_called_once()
            mock_guardar.assert_called_once()
            mock_exito.assert_called_once()
            mock_reload.assert_called_once()

    def test_flujo_busqueda_y_seleccion(self, vidrios_view):
        """Test flujo de búsqueda y selección de obra."""
        view = vidrios_view

        # Datos de búsqueda
        obras_resultado = [
            {'id_obra': 1, 'nombre': 'Obra Test', 'cliente': 'Cliente Test'}
        ]

        with patch.object(view.controller, 'buscar_obras', return_value=obras_resultado) as mock_buscar, \
             patch.object(view, 'actualizar_tabla_obras') as mock_actualizar, \
             patch.object(view, 'obtener_datos_fila_seleccionada', return_value=obras_resultado[0]) as mock_obtener, \
             patch.object(view, 'cargar_detalles_obra') as mock_cargar_detalles:

            # Ejecutar búsqueda
            view.input_buscar_obra.setText("Test")
            view.buscar_obras()

            # Ejecutar selección
            view.on_obra_seleccionada()

            # Verificar flujo
            mock_buscar.assert_called_once_with("Test")
            mock_actualizar.assert_called_once_with(obras_resultado)
            mock_obtener.assert_called_once()
            mock_cargar_detalles.assert_called_once_with(obras_resultado[0])

    def test_flujo_exportacion_completa(self, vidrios_view):
        """Test flujo completo de exportación."""
        view = vidrios_view

        # Datos para exportar
        datos_tabla = [
            {'id': 1, 'nombre': 'Item 1', 'valor': 100},
            {'id': 2, 'nombre': 'Item 2', 'valor': 200}
        ]

        with patch('modules.vidrios.view.QFileDialog') as mock_dialog, \
             patch('pandas.DataFrame') as mock_df, \
             patch.object(view, 'mostrar_mensaje_exito') as mock_exito:

            mock_dialog.getSaveFileName.return_value = ("export.xlsx", "Excel files")
            mock_df_instance = Mock()
            mock_df.return_value = mock_df_instance

            # Ejecutar exportación
            view.exportar_a_excel(datos_tabla)

            # Verificar flujo
            mock_df.assert_called_once_with(datos_tabla)
            mock_df_instance.to_excel.assert_called_once_with("export.xlsx", index=False)
            mock_exito.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
