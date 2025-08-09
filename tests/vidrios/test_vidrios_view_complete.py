"""
Tests exhaustivos para la Vista de Vidrios.
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

@pytest.fixture
def app():
    """Fixture para QApplication."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
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
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QWidget

from rexus.modules.vidrios.view import VidriosView


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
    with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
         patch('modules.vidrios.view.estilizar_boton_icono'), \
         patch('modules.vidrios.view.cargar_modo_tema', return_value='light'), \
         patch('modules.vidrios.view.event_bus') as mock_event_bus, \
         patch('modules.vidrios.view.QIcon'):

        mock_event_bus.obra_agregada = Mock()
        mock_event_bus.obra_agregada.connect = Mock()

        view = VidriosView(
            usuario_actual="test_user",
            headers_dinamicos=["id_obra", "tipo", "ancho", "alto", "color"],
            controller=mock_controller
        )
        yield view
        view.close()


class TestVidriosViewInicializacion:
    """Tests para la inicialización de la vista."""

    def test_init_basico(self, app):
        """Test inicialización básica sin controlador."""
        with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
             patch('modules.vidrios.view.estilizar_boton_icono'), \
             patch('modules.vidrios.view.cargar_modo_tema', return_value='light'), \
             patch('modules.vidrios.view.event_bus') as mock_event_bus, \
             patch('modules.vidrios.view.QIcon'):

            mock_event_bus.obra_agregada = Mock()
            mock_event_bus.obra_agregada.connect = Mock()

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

        with patch('modules.vidrios.view.aplicar_qss_global_y_tema'), \
             patch('modules.vidrios.view.estilizar_boton_icono'), \
             patch('modules.vidrios.view.cargar_modo_tema', return_value='dark'), \
             patch('modules.vidrios.view.event_bus') as mock_event_bus, \
             patch('modules.vidrios.view.QIcon'):

            mock_event_bus.obra_agregada = Mock()
            mock_event_bus.obra_agregada.connect = Mock()

            view = VidriosView(
                usuario_actual="custom_user",
                headers_dinamicos=headers_custom,
                controller=mock_controller
            )

            assert view.usuario_actual == "custom_user"
            assert view.controller == mock_controller
            assert view.vidrios_headers == headers_custom
            view.close()

    def test_init_header_componentes(self, vidrios_view):
        """Test componentes del header."""
        assert hasattr(vidrios_view, 'label_titulo')
        assert hasattr(vidrios_view, 'boton_agregar_vidrios_obra')
        assert vidrios_view.label_titulo.text() == "Gestión de Vidrios"
        assert vidrios_view.boton_agregar_vidrios_obra.objectName() == "boton_agregar_vidrios_obra"

    def test_init_tabs_estructura(self, vidrios_view):
        """Test estructura de pestañas."""
        assert vidrios_view.tabs.count() == 3
        assert hasattr(vidrios_view, 'tab_obras')
        assert hasattr(vidrios_view, 'tab_pedidos_usuario')
        assert hasattr(vidrios_view, 'tab_pedidos')

    def test_init_feedback_componentes(self, vidrios_view):
        """Test componentes de feedback."""
        assert hasattr(vidrios_view, 'label_feedback')
        assert hasattr(vidrios_view, '_feedback_timer')
        assert not vidrios_view.label_feedback.isVisible()

    def test_init_botones_principales(self, vidrios_view):
        """Test botones principales."""
        assert hasattr(vidrios_view, 'boton_buscar')
        assert hasattr(vidrios_view, 'boton_exportar_excel')
        assert vidrios_view.boton_buscar.objectName() == "boton_buscar_vidrios"
        assert vidrios_view.boton_exportar_excel.objectName() == "boton_exportar_excel_vidrios"


class TestVidriosViewConfiguracionColumnas:
    """Tests para configuración de columnas."""

    def test_cargar_config_columnas_archivo_existente(self, vidrios_view):
        """Test cargar configuración desde archivo existente."""
        config_data = {"id_obra": True, "tipo": False, "ancho": True}

        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):

            config = vidrios_view.cargar_config_columnas()
            assert config == config_data

    def test_cargar_config_columnas_archivo_no_existe(self, vidrios_view):
        """Test cargar configuración cuando no existe archivo."""
        with patch('os.path.exists', return_value=False):
            config = vidrios_view.cargar_config_columnas()

            # Debe devolver config por defecto
            for header in vidrios_view.vidrios_headers:
                assert config[header] is True

    def test_cargar_config_columnas_error_archivo(self, vidrios_view):
        """Test manejo de error al cargar configuración."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=Exception("Error de archivo")), \
             patch.object(vidrios_view, 'show') as mock_show:  # Para evitar mostrar QMessageBox

            config = vidrios_view.cargar_config_columnas()

            # Debe devolver config por defecto
            for header in vidrios_view.vidrios_headers:
                assert config[header] is True

    def test_guardar_config_columnas_exitoso(self, vidrios_view):
        """Test guardar configuración exitosamente."""
        vidrios_view.columnas_visibles = {"id_obra": True, "tipo": False}

        with patch('builtins.open', mock_open()) as mock_file:
            vidrios_view.guardar_config_columnas()

            mock_file.assert_called_once()
            handle = mock_file()
            written_data = ''.join(call[0][0] for call in handle.write.call_args_list)
            assert '"id_obra": true' in written_data
            assert '"tipo": false' in written_data

    def test_guardar_config_columnas_error(self, vidrios_view):
        """Test manejo de error al guardar configuración."""
        with patch('builtins.open', side_effect=Exception("Error de escritura")), \
             patch.object(vidrios_view, 'show'):  # Para evitar mostrar QMessageBox

            # No debe lanzar excepción
            vidrios_view.guardar_config_columnas()

    def test_aplicar_columnas_visibles(self, vidrios_view):
        """Test aplicar visibilidad de columnas."""
        tabla = vidrios_view.tabla_obras
        headers = ["col1", "col2", "col3"]
        columnas_visibles = {"col1": True, "col2": False, "col3": True}

        # Configurar tabla mock
        tabla.setColumnCount(3)
        tabla.setColumnHidden = Mock()

        vidrios_view.aplicar_columnas_visibles(tabla, headers, columnas_visibles)

        # Verificar calls
        expected_calls = [
            call(0, False),  # col1: visible
            call(1, True),   # col2: oculta
            call(2, False)   # col3: visible
        ]
        tabla.setColumnHidden.assert_has_calls(expected_calls)

    def test_get_tabla_activa_obras(self, vidrios_view):
        """Test obtener tabla activa - pestaña obras."""
        vidrios_view.tabs.setCurrentIndex(0)
        tabla = vidrios_view.get_tabla_activa()
        assert tabla == vidrios_view.tabla_obras

    def test_get_tabla_activa_pedidos_usuario(self, vidrios_view):
        """Test obtener tabla activa - pestaña pedidos usuario."""
        vidrios_view.tabs.setCurrentIndex(1)
        tabla = vidrios_view.get_tabla_activa()
        assert tabla == vidrios_view.tabla_pedidos_usuario

    def test_get_tabla_activa_invalida(self, vidrios_view):
        """Test obtener tabla activa - índice inválido."""
        vidrios_view.tabs.setCurrentIndex(99)
        tabla = vidrios_view.get_tabla_activa()
        assert tabla is None


class TestVidriosViewMenuColumnas:
    """Tests para menús de columnas."""

    def test_mostrar_menu_columnas(self, vidrios_view):
        """Test mostrar menú de configuración de columnas."""
        tabla = vidrios_view.tabla_obras
        headers = ["col1", "col2"]
        columnas_visibles = {"col1": True, "col2": False}
        pos = QPoint(10, 10)

        with patch('modules.vidrios.view.QMenu') as mock_menu_class, \
             patch('modules.vidrios.view.QAction') as mock_action_class:

            mock_menu = Mock()
            mock_menu_class.return_value = mock_menu
            mock_action = Mock()
            mock_action_class.return_value = mock_action

            vidrios_view.mostrar_menu_columnas(pos, tabla, headers, columnas_visibles)

            # Verificar que se creó el menú y acciones
            mock_menu_class.assert_called_once()
            assert mock_action_class.call_count == 2
            mock_menu.exec.assert_called_once()

    def test_toggle_columna(self, vidrios_view):
        """Test alternar visibilidad de columna."""
        tabla = Mock()
        idx = 1
        header = "test_header"
        columnas_visibles = {"test_header": True}

        with patch.object(vidrios_view, 'guardar_config_columnas') as mock_guardar:
            vidrios_view.toggle_columna(tabla, idx, header, columnas_visibles, False)

            assert columnas_visibles[header] is False
            tabla.setColumnHidden.assert_called_once_with(idx, True)
            mock_guardar.assert_called_once()

    def test_auto_ajustar_columna(self, vidrios_view):
        """Test auto ajustar ancho de columna."""
        tabla = Mock()
        idx = 2

        vidrios_view.auto_ajustar_columna(idx, tabla)
        tabla.resizeColumnToContents.assert_called_once_with(idx)

    def test_auto_ajustar_columna_tabla_none(self, vidrios_view):
        """Test auto ajustar columna con tabla None."""
        with patch.object(vidrios_view, 'get_tabla_activa', return_value=None):
            # No debe lanzar excepción
            vidrios_view.auto_ajustar_columna(1)


class TestVidriosViewFeedback:
    """Tests para sistema de feedback."""

    def test_mostrar_feedback_info(self, vidrios_view):
        """Test mostrar feedback de información."""
        mensaje = "Test mensaje info"

        with patch.object(vidrios_view, '_feedback_timer', Mock()):
            vidrios_view.mostrar_feedback(mensaje, tipo="info")

            assert vidrios_view.label_feedback.isVisible()
            assert "ℹ️ Test mensaje info" in vidrios_view.label_feedback.text()

    def test_mostrar_feedback_exito(self, vidrios_view):
        """Test mostrar feedback de éxito."""
        mensaje = "Operación exitosa"

        vidrios_view.mostrar_feedback(mensaje, tipo="exito")

        assert vidrios_view.label_feedback.isVisible()
        assert "[CHECK] Operación exitosa" in vidrios_view.label_feedback.text()

    def test_mostrar_feedback_advertencia(self, vidrios_view):
        """Test mostrar feedback de advertencia."""
        mensaje = "Advertencia importante"

        vidrios_view.mostrar_feedback(mensaje, tipo="advertencia")

        assert vidrios_view.label_feedback.isVisible()
        assert "[WARN] Advertencia importante" in vidrios_view.label_feedback.text()

    def test_mostrar_feedback_error(self, vidrios_view):
        """Test mostrar feedback de error."""
        mensaje = "Error crítico"

        vidrios_view.mostrar_feedback(mensaje, tipo="error")

        assert vidrios_view.label_feedback.isVisible()
        assert "[ERROR] Error crítico" in vidrios_view.label_feedback.text()

    def test_mostrar_feedback_timer_configurado(self, vidrios_view):
        """Test configuración de timer de feedback."""
        with patch('modules.vidrios.view.QTimer') as mock_timer_class:
            mock_timer = Mock()
            mock_timer_class.return_value = mock_timer

            vidrios_view.mostrar_feedback("Test")

            mock_timer.setSingleShot.assert_called_once_with(True)
            mock_timer.start.assert_called_once_with(4000)

    def test_ocultar_feedback(self, vidrios_view):
        """Test ocultar feedback."""
        # Mostrar feedback primero
        vidrios_view.mostrar_feedback("Test")
        assert vidrios_view.label_feedback.isVisible()

        # Ocultar feedback
        vidrios_view.ocultar_feedback()

        assert not vidrios_view.label_feedback.isVisible()
        assert vidrios_view.label_feedback.text() == ""

    def test_mostrar_feedback_carga(self, vidrios_view):
        """Test mostrar feedback de carga."""
        with patch('modules.vidrios.view.QDialog') as mock_dialog_class, \
             patch('modules.vidrios.view.QProgressBar') as mock_progress_class:

            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog
            mock_progress = Mock()
            mock_progress_class.return_value = mock_progress

            result = vidrios_view.mostrar_feedback_carga("Cargando datos...", 0, 100)

            assert result == mock_progress
            mock_dialog.setModal.assert_called_once_with(True)
            mock_dialog.show.assert_called_once()

    def test_ocultar_feedback_carga(self, vidrios_view):
        """Test ocultar feedback de carga."""
        mock_dialog = Mock()
        vidrios_view.dialog_carga = mock_dialog

        vidrios_view.ocultar_feedback_carga()

        mock_dialog.accept.assert_called_once()
        assert vidrios_view.dialog_carga is None


class TestVidriosViewTabsEventos:
    """Tests para eventos de pestañas."""

    def test_on_tab_changed_obras(self, vidrios_view):
        """Test cambio a pestaña de obras."""
        vidrios_view._on_tab_changed(0)

        # Verificar que se llama al controlador
        vidrios_view.controller.cargar_resumen_obras.assert_called()

    def test_on_tab_changed_pedidos_usuario(self, vidrios_view):
        """Test cambio a pestaña de pedidos usuario."""
        vidrios_view._on_tab_changed(1)

        # Verificar que se llama al controlador
        vidrios_view.controller.cargar_pedidos_usuario.assert_called_with("test_user")

    def test_on_tab_changed_sin_tabs(self, vidrios_view):
        """Test cambio de tab sin tabs definidos."""
        vidrios_view.tabs = None

        # No debe lanzar excepción
        vidrios_view._on_tab_changed(0)

    def test_is_tab_obras(self, vidrios_view):
        """Test identificar pestaña de obras."""
        assert vidrios_view._is_tab_obras(vidrios_view.tab_obras)
        assert not vidrios_view._is_tab_obras(vidrios_view.tab_pedidos_usuario)

    def test_is_tab_pedidos_usuario(self, vidrios_view):
        """Test identificar pestaña de pedidos usuario."""
        assert vidrios_view._is_tab_pedidos_usuario(vidrios_view.tab_pedidos_usuario)
        assert not vidrios_view._is_tab_pedidos_usuario(vidrios_view.tab_obras)

    def test_is_tab_pedidos(self, vidrios_view):
        """Test identificar pestaña de pedidos."""
        assert vidrios_view._is_tab_pedidos(vidrios_view.tab_pedidos)
        assert not vidrios_view._is_tab_pedidos(vidrios_view.tab_obras)


class TestVidriosViewTablas:
    """Tests para operaciones de tablas."""

    def test_mostrar_resumen_obras(self, vidrios_view):
        """Test mostrar resumen de obras en tabla."""
        obras = [
            [1, "Obra A", "Cliente 1", "2024-01-15", "Pendiente"],
            [2, "Obra B", "Cliente 2", "2024-01-20", "Enviado"]
        ]

        vidrios_view.mostrar_resumen_obras(obras)

        assert vidrios_view.tabla_obras.rowCount() == 2
        assert vidrios_view.tabla_obras.columnCount() == 6

        # Verificar datos primera fila
        assert vidrios_view.tabla_obras.item(0, 0).text() == "1"
        assert vidrios_view.tabla_obras.item(0, 1).text() == "Obra A"
        assert vidrios_view.tabla_obras.item(0, 4).text() == "Pendiente"

    def test_mostrar_resumen_obras_datos_none(self, vidrios_view):
        """Test mostrar resumen con datos None."""
        obras = [
            [1, None, "Cliente 1", None, "Pendiente"]
        ]

        vidrios_view.mostrar_resumen_obras(obras)

        assert vidrios_view.tabla_obras.item(0, 1).text() == ""
        assert vidrios_view.tabla_obras.item(0, 3).text() == ""

    def test_mostrar_pedidos_usuario(self, vidrios_view):
        """Test mostrar pedidos de usuario."""
        pedidos = [
            [1, 1, "test_user", "Vidrio A", 100, 200, "Azul", 5, "Pendiente", "2024-01-15"],
            [2, 2, "test_user", "Vidrio B", 150, 250, "Verde", 3, "Enviado", "2024-01-16"]
        ]

        vidrios_view.mostrar_pedidos_usuario(pedidos)

        assert vidrios_view.tabla_pedido.rowCount() == 2
        assert vidrios_view.tabla_pedido.columnCount() == 8

    def test_actualizar_tabla_pedido(self, vidrios_view):
        """Test actualizar tabla de pedido."""
        # Agregar algunas filas primero
        vidrios_view.tabla_pedido.setRowCount(3)

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view.actualizar_tabla_pedido()

            assert vidrios_view.tabla_pedido.rowCount() == 0
            mock_feedback.assert_called_with("Tabla de pedido de vidrios actualizada.", tipo="info")

    def test_get_safe_item_valido(self, vidrios_view):
        """Test obtener item de tabla de forma segura - posición válida."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(3)
        tabla.setItem(1, 2, Mock())

        item = vidrios_view.get_safe_item(tabla, 1, 2)
        assert item is not None

    def test_get_safe_item_invalido(self, vidrios_view):
        """Test obtener item de tabla de forma segura - posición inválida."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(3)

        # Posiciones fuera de rango
        assert vidrios_view.get_safe_item(tabla, 5, 1) is None
        assert vidrios_view.get_safe_item(tabla, 1, 10) is None
        assert vidrios_view.get_safe_item(tabla, -1, 1) is None

    def test_get_safe_item_tabla_none(self, vidrios_view):
        """Test obtener item con tabla None."""
        assert vidrios_view.get_safe_item(None, 0, 0) is None

    def test_get_safe_selected_items(self, vidrios_view):
        """Test obtener items seleccionados de forma segura."""
        tabla = vidrios_view.tabla_obras
        tabla.selectedItems = Mock(return_value=["item1", "item2"])

        items = vidrios_view.get_safe_selected_items(tabla)
        assert items == ["item1", "item2"]

    def test_get_safe_selected_items_tabla_none(self, vidrios_view):
        """Test obtener items seleccionados con tabla None."""
        items = vidrios_view.get_safe_selected_items(None)
        assert items == []

    def test_get_safe_column_count(self, vidrios_view):
        """Test obtener número de columnas de forma segura."""
        tabla = vidrios_view.tabla_obras
        tabla.setColumnCount(5)

        count = vidrios_view.get_safe_column_count(tabla)
        assert count == 5

    def test_get_safe_column_count_tabla_none(self, vidrios_view):
        """Test obtener número de columnas con tabla None."""
        count = vidrios_view.get_safe_column_count(None)
        assert count == 0

    def test_get_safe_row_count(self, vidrios_view):
        """Test obtener número de filas de forma segura."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(10)

        count = vidrios_view.get_safe_row_count(tabla)
        assert count == 10

    def test_get_safe_row_count_tabla_none(self, vidrios_view):
        """Test obtener número de filas con tabla None."""
        count = vidrios_view.get_safe_row_count(None)
        assert count == 0

    def test_set_safe_background(self, vidrios_view):
        """Test establecer color de fondo de forma segura."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(2)

        # Mock item
        mock_item = Mock()
        tabla.setItem(1, 1, mock_item)

        color = QColor(255, 0, 0)
        vidrios_view.set_safe_background(tabla, 1, 1, color)

        mock_item.setBackground.assert_called_once_with(color)

    def test_set_safe_background_item_none(self, vidrios_view):
        """Test establecer color de fondo cuando item es None."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(2)

        color = QColor(255, 0, 0)
        # No debe lanzar excepción
        vidrios_view.set_safe_background(tabla, 1, 1, color)


class TestVidriosViewFormularios:
    """Tests para formularios y diálogos."""

    def test_create_form_layout(self, vidrios_view):
        """Test crear layout de formulario."""
        form_layout = vidrios_view.create_form_layout()

        assert hasattr(vidrios_view, 'tipo_input')
        assert hasattr(vidrios_view, 'ancho_input')
        assert hasattr(vidrios_view, 'alto_input')
        assert hasattr(vidrios_view, 'cantidad_input')
        assert hasattr(vidrios_view, 'proveedor_input')
        assert hasattr(vidrios_view, 'fecha_entrega_input')
        assert form_layout is not None

    def test_create_table(self, vidrios_view):
        """Test crear tabla."""
        tabla = vidrios_view.create_table()

        assert tabla.columnCount() == len(vidrios_view.vidrios_headers)

    def test_validar_campos_formulario_validos(self, vidrios_view):
        """Test validar campos de formulario - campos válidos."""
        # Crear formulario primero
        vidrios_view.create_form_layout()

        # Llenar campos
        vidrios_view.tipo_input.setText("Vidrio templado")
        vidrios_view.ancho_input.setText("100")
        vidrios_view.alto_input.setText("200")
        vidrios_view.cantidad_input.setText("5")
        vidrios_view.proveedor_input.setText("Proveedor ABC")

        assert vidrios_view.validar_campos_formulario() is True

    def test_validar_campos_formulario_campos_vacios(self, vidrios_view):
        """Test validar campos de formulario - campos vacíos."""
        # Crear formulario primero
        vidrios_view.create_form_layout()

        # Dejar algunos campos vacíos
        vidrios_view.tipo_input.setText("")
        vidrios_view.ancho_input.setText("100")
        vidrios_view.alto_input.setText("")
        vidrios_view.cantidad_input.setText("5")
        vidrios_view.proveedor_input.setText("Proveedor ABC")

        assert vidrios_view.validar_campos_formulario() is False

    def test_mostrar_formulario_vidrios_obra(self, vidrios_view):
        """Test mostrar formulario para agregar vidrios a obra."""
        with patch('modules.vidrios.view.QDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog

            vidrios_view.mostrar_formulario_vidrios_obra()

            mock_dialog.setWindowTitle.assert_called_with("Agregar Vidrios a Obra")
            mock_dialog.exec.assert_called_once()

    def test_guardar_vidrios_obra_campos_validos(self, vidrios_view):
        """Test guardar vidrios a obra con campos válidos."""
        # Crear formulario primero
        vidrios_view.create_form_layout()

        # Llenar campos
        vidrios_view.tipo_input.setText("Vidrio templado")
        vidrios_view.ancho_input.setText("100")
        vidrios_view.alto_input.setText("200")
        vidrios_view.cantidad_input.setText("5")
        vidrios_view.proveedor_input.setText("Proveedor ABC")

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view.guardar_vidrios_obra("1", "Vidrio templado", "100", "200", "5")

            mock_feedback.assert_called_with("Vidrios agregados a la obra correctamente.", tipo="exito")

    def test_guardar_vidrios_obra_campos_invalidos(self, vidrios_view):
        """Test guardar vidrios a obra con campos inválidos."""
        # Crear formulario primero
        vidrios_view.create_form_layout()

        # Dejar campos vacíos
        vidrios_view.tipo_input.setText("")

        with patch.object(vidrios_view, 'show'):  # Para evitar mostrar QMessageBox
            vidrios_view.guardar_vidrios_obra("1", "", "100", "200", "5")


class TestVidriosViewPedidos:
    """Tests para gestión de pedidos."""

    def test_iniciar_pedido_para_obra_sin_seleccion(self, vidrios_view):
        """Test iniciar pedido sin obra seleccionada."""
        vidrios_view.tabla_obras.setCurrentRow(-1)

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._iniciar_pedido_para_obra()

            mock_feedback.assert_called_with("Seleccione una obra para iniciar pedido.", tipo="error")

    def test_iniciar_pedido_para_obra_con_seleccion(self, vidrios_view):
        """Test iniciar pedido con obra seleccionada."""
        # Configurar tabla
        vidrios_view.tabla_obras.setRowCount(1)
        vidrios_view.tabla_obras.setColumnCount(2)

        # Mock item con ID de obra
        mock_item = Mock()
        mock_item.text.return_value = "123"
        vidrios_view.tabla_obras.setItem(0, 0, mock_item)
        vidrios_view.tabla_obras.setCurrentRow(0)

        vidrios_view._iniciar_pedido_para_obra()

        # Verificar que cambia a pestaña de pedidos
        assert vidrios_view.tabs.currentIndex() == 1
        assert "123" in vidrios_view.label_formulario.text()

    def test_guardar_pedido_vidrios_sin_controlador(self, vidrios_view):
        """Test guardar pedido sin controlador."""
        vidrios_view.controller = None

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._guardar_pedido_vidrios()

            mock_feedback.assert_called_with("Error: El controlador no está disponible para guardar el pedido.", tipo="error")

    def test_guardar_pedido_vidrios_con_datos(self, vidrios_view):
        """Test guardar pedido con datos válidos."""
        # Configurar tabla de pedido
        vidrios_view.tabla_pedido.setRowCount(2)
        vidrios_view.tabla_pedido.setColumnCount(3)

        # Mock items
        for row in range(2):
            for col in range(3):
                mock_item = Mock()
                mock_item.text.return_value = f"dato_{row}_{col}"
                vidrios_view.tabla_pedido.setItem(row, col, mock_item)

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._guardar_pedido_vidrios()

            # Verificar que se llama al controlador
            vidrios_view.controller.guardar_pedido_vidrios.assert_called_once()
            vidrios_view.controller.cargar_pedidos_usuario.assert_called_with("test_user")
            mock_feedback.assert_called_with("Pedido de vidrios guardado correctamente.", tipo="exito")

    def test_editar_estado_pedido_sin_controlador(self, vidrios_view):
        """Test editar estado de pedido sin controlador."""
        vidrios_view.controller = None

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._editar_estado_pedido(0)

            mock_feedback.assert_called_with("Error: controlador no inicializado o método no disponible.", tipo="error")

    def test_editar_estado_pedido_con_datos(self, vidrios_view):
        """Test editar estado de pedido con datos válidos."""
        # Configurar tabla
        vidrios_view.tabla_obras.setRowCount(1)
        vidrios_view.tabla_obras.setColumnCount(5)

        # Mock items
        mock_item_id = Mock()
        mock_item_id.text.return_value = "123"
        mock_item_estado = Mock()
        mock_item_estado.text.return_value = "Pendiente"

        vidrios_view.tabla_obras.setItem(0, 0, mock_item_id)
        vidrios_view.tabla_obras.setItem(0, 4, mock_item_estado)

        with patch('modules.vidrios.view.QInputDialog') as mock_input:
            mock_input.getText.return_value = ("Enviado", True)

            vidrios_view._editar_estado_pedido(0)

            vidrios_view.controller.actualizar_estado_pedido.assert_called_with("123", "Enviado")

    def test_ver_detalle_pedido_sin_controlador(self, vidrios_view):
        """Test ver detalle de pedido sin controlador."""
        vidrios_view.controller = None

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._ver_detalle_pedido(0)

            mock_feedback.assert_called_with("Error: El controlador no está disponible para mostrar el detalle del pedido.", tipo="error")

    def test_mostrar_detalle_pedido(self, vidrios_view):
        """Test mostrar detalle de pedido en diálogo."""
        detalle = [
            ["Vidrio templado", "100", "200", "Azul", "5", "Pendiente", "2024-01-15", "Proveedor ABC", "2024-01-30", "Sin observaciones"]
        ]

        with patch('modules.vidrios.view.QDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog

            vidrios_view.mostrar_detalle_pedido(detalle)

            mock_dialog.setWindowTitle.assert_called_with("Detalle del pedido de vidrios")
            mock_dialog.exec.assert_called_once()


class TestVidriosViewExportacion:
    """Tests para funcionalidades de exportación."""

    def test_exportar_tabla_a_excel_sin_tabla(self, vidrios_view):
        """Test exportar a Excel sin tabla activa."""
        with patch.object(vidrios_view, 'get_tabla_activa', return_value=None), \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            vidrios_view.exportar_tabla_a_excel()

            mock_feedback.assert_called_with("No hay tabla activa para exportar.", tipo="error")

    def test_exportar_tabla_a_excel_cancelado_por_usuario(self, vidrios_view):
        """Test exportar a Excel cancelado por usuario."""
        tabla = vidrios_view.tabla_obras

        with patch('modules.vidrios.view.QMessageBox') as mock_msg, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            mock_msg.question.return_value = mock_msg.StandardButton.No

            vidrios_view.exportar_tabla_a_excel(tabla)

            mock_feedback.assert_called_with("Exportación cancelada por el usuario.", tipo="advertencia")

    def test_exportar_tabla_a_excel_sin_archivo(self, vidrios_view):
        """Test exportar a Excel sin seleccionar archivo."""
        tabla = vidrios_view.tabla_obras

        with patch('modules.vidrios.view.QMessageBox') as mock_msg, \
             patch('modules.vidrios.view.QFileDialog') as mock_file_dialog, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            mock_msg.question.return_value = mock_msg.StandardButton.Yes
            mock_file_dialog.getSaveFileName.return_value = ("", "")

            vidrios_view.exportar_tabla_a_excel(tabla)

            mock_feedback.assert_called_with("Exportación cancelada.", tipo="advertencia")

    def test_exportar_tabla_a_excel_exitoso(self, vidrios_view):
        """Test exportar a Excel exitosamente."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(2)
        tabla.setColumnCount(3)

        # Mock headers
        headers = ["Col1", "Col2", "Col3"]
        for i, header in enumerate(headers):
            mock_header_item = Mock()
            mock_header_item.text.return_value = header
            tabla.setHorizontalHeaderItem(i, mock_header_item)

        # Mock items
        for row in range(2):
            for col in range(3):
                mock_item = Mock()
                mock_item.text.return_value = f"data_{row}_{col}"
                tabla.setItem(row, col, mock_item)

        with patch('modules.vidrios.view.QMessageBox') as mock_msg, \
             patch('modules.vidrios.view.QFileDialog') as mock_file_dialog, \
             patch('modules.vidrios.view.pd') as mock_pd, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            mock_msg.question.return_value = mock_msg.StandardButton.Yes
            mock_file_dialog.getSaveFileName.return_value = ("test.xlsx", "")

            mock_df = Mock()
            mock_pd.DataFrame.return_value = mock_df

            vidrios_view.exportar_tabla_a_excel(tabla)

            # Verificar que se crea DataFrame y se exporta
            mock_pd.DataFrame.assert_called_once()
            mock_df.to_excel.assert_called_with("test.xlsx", index=False)
            mock_feedback.assert_called_with("Datos exportados correctamente a test.xlsx", tipo="exito")

    def test_exportar_tabla_a_excel_error(self, vidrios_view):
        """Test exportar a Excel con error."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(1)
        tabla.setColumnCount(1)

        with patch('modules.vidrios.view.QMessageBox') as mock_msg, \
             patch('modules.vidrios.view.QFileDialog') as mock_file_dialog, \
             patch('modules.vidrios.view.pd') as mock_pd, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            mock_msg.question.return_value = mock_msg.StandardButton.Yes
            mock_file_dialog.getSaveFileName.return_value = ("test.xlsx", "")

            mock_df = Mock()
            mock_df.to_excel.side_effect = Exception("Error de escritura")
            mock_pd.DataFrame.return_value = mock_df

            vidrios_view.exportar_tabla_a_excel(tabla)

            mock_feedback.assert_called_with("No se pudo exportar: Error de escritura", tipo="error")


class TestVidriosViewQR:
    """Tests para funcionalidad QR."""

    def test_mostrar_qr_item_seleccionado_sin_seleccion(self, vidrios_view):
        """Test mostrar QR sin item seleccionado."""
        tabla = vidrios_view.tabla_obras
        tabla.selectedItems = Mock(return_value=[])

        # No debe hacer nada
        vidrios_view.mostrar_qr_item_seleccionado(tabla)

    def test_mostrar_qr_item_seleccionado_sin_codigo(self, vidrios_view):
        """Test mostrar QR sin código válido."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(1)
        tabla.setColumnCount(1)

        # Mock item seleccionado pero sin código
        mock_selected_item = Mock()
        mock_selected_item.row.return_value = 0
        tabla.selectedItems = Mock(return_value=[mock_selected_item])

        mock_codigo_item = Mock()
        mock_codigo_item.text.return_value = ""
        tabla.setItem(0, 0, mock_codigo_item)

        with patch.object(vidrios_view, 'show'):  # Para evitar mostrar QMessageBox
            vidrios_view.mostrar_qr_item_seleccionado(tabla)

    def test_mostrar_qr_item_seleccionado_exitoso(self, vidrios_view):
        """Test mostrar QR exitosamente."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(1)
        tabla.setColumnCount(1)

        # Mock item seleccionado
        mock_selected_item = Mock()
        mock_selected_item.row.return_value = 0
        tabla.selectedItems = Mock(return_value=[mock_selected_item])

        # Mock item con código
        mock_codigo_item = Mock()
        mock_codigo_item.text.return_value = "VIDRIO123"
        tabla.setItem(0, 0, mock_codigo_item)

        with patch('modules.vidrios.view.qrcode') as mock_qrcode, \
             patch('modules.vidrios.view.tempfile') as mock_tempfile, \
             patch('modules.vidrios.view.QPixmap') as mock_pixmap, \
             patch('modules.vidrios.view.QDialog') as mock_dialog_class:

            # Mock QR generation
            mock_qr = Mock()
            mock_img = Mock()
            mock_qrcode.QRCode.return_value = mock_qr
            mock_qr.make_image.return_value = mock_img

            # Mock temp file
            mock_temp = Mock()
            mock_temp.name = "temp_qr.png"
            mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value = mock_temp

            # Mock dialog
            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog

            vidrios_view.mostrar_qr_item_seleccionado(tabla)

            # Verificar que se genera QR y se muestra diálogo
            mock_qr.add_data.assert_called_with("VIDRIO123")
            mock_qr.make.assert_called_with(fit=True)
            mock_dialog.exec.assert_called_once()

    def test_mostrar_qr_error_generacion(self, vidrios_view):
        """Test mostrar QR con error en generación."""
        tabla = vidrios_view.tabla_obras
        tabla.setRowCount(1)
        tabla.setColumnCount(1)

        # Mock item seleccionado
        mock_selected_item = Mock()
        mock_selected_item.row.return_value = 0
        tabla.selectedItems = Mock(return_value=[mock_selected_item])

        # Mock item con código
        mock_codigo_item = Mock()
        mock_codigo_item.text.return_value = "VIDRIO123"
        tabla.setItem(0, 0, mock_codigo_item)

        with patch('modules.vidrios.view.qrcode') as mock_qrcode, \
             patch.object(vidrios_view, 'show'):  # Para evitar mostrar QMessageBox

            # Simular error en generación QR
            mock_qrcode.QRCode.side_effect = Exception("Error QR")

            vidrios_view.mostrar_qr_item_seleccionado(tabla)


class TestVidriosViewEventBus:
    """Tests para integración con Event Bus."""

    def test_actualizar_por_obra(self, vidrios_view):
        """Test actualizar vista por nueva obra."""
        datos_obra = {"id": 1, "nombre": "Obra Test", "cliente": "Cliente Test"}

        with patch.object(vidrios_view, 'refrescar_por_obra') as mock_refrescar, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            vidrios_view.actualizar_por_obra(datos_obra)

            mock_refrescar.assert_called_once_with(datos_obra)
            mock_feedback.assert_called_with("Nueva obra agregada: Obra Test (vidrios actualizados)", tipo="info")

    def test_refrescar_por_obra(self, vidrios_view):
        """Test refrescar tabla de obras."""
        datos_obra = {"id": 1, "nombre": "Obra Test"}

        # Agregar filas a la tabla primero
        vidrios_view.tabla_obras.setRowCount(5)

        vidrios_view.refrescar_por_obra(datos_obra)

        assert vidrios_view.tabla_obras.rowCount() == 0


class TestVidriosViewEventosTabla:
    """Tests para eventos específicos de tablas."""

    def test_editar_estado_pedido_evento(self, vidrios_view):
        """Test evento de editar estado de pedido."""
        # Configurar tabla
        vidrios_view.tabla_obras.setRowCount(1)
        vidrios_view.tabla_obras.setColumnCount(5)

        # Mock item
        mock_item = Mock()
        mock_item.text.return_value = "Pendiente"
        vidrios_view.tabla_obras.setItem(0, 0, mock_item)

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view.editar_estado_pedido(0, 0)

            # Verificar que se actualiza el estado
            assert vidrios_view.PEDIDO_ENVIADO in mock_item.setText.call_args[0]
            mock_feedback.assert_called()

    def test_actualizar_detalle_pedido(self, vidrios_view):
        """Test actualizar detalle de pedido."""
        # Configurar tabla
        vidrios_view.tabla_obras.setRowCount(1)
        vidrios_view.tabla_obras.setColumnCount(2)
        vidrios_view.tabla_obras.setCurrentRow(0)

        # Mock item
        mock_item = Mock()
        mock_item.text.return_value = "PEDIDO123"
        vidrios_view.tabla_obras.setItem(0, 0, mock_item)

        vidrios_view.actualizar_detalle_pedido()

        assert vidrios_view.codigo_pedido_actual == "PEDIDO123"

    def test_editar_detalle_pedido(self, vidrios_view):
        """Test editar detalle de pedido."""
        # Configurar tabla
        vidrios_view.tabla_obras.setRowCount(1)
        vidrios_view.tabla_obras.setColumnCount(2)

        # Mock item
        mock_item = Mock()
        mock_item.text.return_value = "Valor actual"
        vidrios_view.tabla_obras.setItem(0, 1, mock_item)

        with patch('modules.vidrios.view.QInputDialog') as mock_input, \
             patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:

            mock_input.getText.return_value = ("Nuevo valor", True)

            vidrios_view.editar_detalle_pedido(0, 1)

            mock_item.setText.assert_called_with("Nuevo valor")
            mock_feedback.assert_called_with("Detalle de pedido actualizado.", tipo="exito")

    def test_on_tabla_obras_cell_clicked(self, vidrios_view):
        """Test evento click en celda de tabla obras."""
        with patch.object(vidrios_view, '_editar_estado_pedido') as mock_editar:
            vidrios_view._on_tabla_obras_cell_clicked(1, 4)
            mock_editar.assert_called_once_with(1)

    def test_on_tabla_pedido_cell_clicked(self, vidrios_view):
        """Test evento click en celda de tabla pedido."""
        with patch.object(vidrios_view, '_ver_detalle_pedido') as mock_ver:
            vidrios_view._on_tabla_pedido_cell_clicked(2, 4)
            mock_ver.assert_called_once_with(2)


class TestVidriosViewIntegracion:
    """Tests de integración y edge cases."""

    def test_inicializar_vinculos_controlador(self, vidrios_view):
        """Test inicializar vínculos con controlador."""
        nuevo_controller = Mock()

        with patch.object(vidrios_view, '_on_tab_changed') as mock_tab_changed:
            vidrios_view.inicializar_vinculos_controlador(nuevo_controller)

            assert vidrios_view.controller == nuevo_controller
            mock_tab_changed.assert_called_with(0)

    def test_conectar_botones_principales(self, vidrios_view):
        """Test conexión de botones principales."""
        # Verificar que el botón de exportar está conectado
        assert vidrios_view.boton_exportar_excel.receivers(vidrios_view.boton_exportar_excel.clicked) > 0

    def test_init_controller_data_sin_controlador(self, vidrios_view):
        """Test inicialización de datos sin controlador."""
        vidrios_view.controller = None

        with patch.object(vidrios_view, 'mostrar_feedback') as mock_feedback:
            vidrios_view._init_controller_data()

            mock_feedback.assert_called_with("Error: controlador no inicializado.", tipo="error")

    def test_abrir_dialogo_estandar(self, vidrios_view):
        """Test abrir diálogo estándar."""
        mock_widget = Mock()

        with patch('modules.vidrios.view.QDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog_class.return_value = mock_dialog

            vidrios_view._abrir_dialogo_estandar("Título Test", mock_widget)

            mock_dialog.setWindowTitle.assert_called_with("Título Test")
            mock_dialog.exec.assert_called_once()

    def test_edge_case_tabla_sin_header(self, vidrios_view):
        """Test edge case con tabla sin header."""
        # Simular tabla sin header
        tabla = Mock()
        tabla.horizontalHeader.return_value = None

        result = vidrios_view.get_safe_horizontal_header(tabla)
        assert result is None

    def test_edge_case_feedback_sin_label(self, vidrios_view):
        """Test edge case mostrar feedback sin label."""
        # Eliminar label de feedback
        vidrios_view.label_feedback = None

        # No debe lanzar excepción
        vidrios_view.mostrar_feedback("Test")

    def test_edge_case_tabs_currentWidget_none(self, vidrios_view):
        """Test edge case cuando currentWidget es None."""
        vidrios_view.tabs.currentWidget = Mock(return_value=None)

        # No debe lanzar excepción
        vidrios_view._on_tab_changed(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
