"""
Tests exhaustivos para HerrajesView.

Cobertura:
- Inicialización de la vista
- Componentes de la UI (tablas, botones, filtros)
- Banner de feedback visual
- Funcionalidades de filtrado
- Exportación de datos
- Interacciones con tabs
- Manejo de eventos y señales
- Edge cases y validaciones
- Accesibilidad y feedback visual
- Integración con controladores
"""

# Asegurar que QApplication existe para tests de PyQt6
if not QApplication.instance():
    app = QApplication([])

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# from rexus.modules.herrajes.view import HerrajesView # Movido a sección try/except, FeedbackBanner


import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from PyQt6.QtWidgets import QApplication, QWidget


class TestFeedbackBanner(unittest.TestCase):
    """Tests para el componente FeedbackBanner."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.banner = FeedbackBanner()

    def test_init_feedback_banner(self):
        """Test inicialización del banner de feedback."""
        self.assertIsNotNone(self.banner)
        self.assertEqual(self.banner.objectName(), "feedback_banner")
        self.assertFalse(self.banner.isVisible())
        self.assertEqual(self.banner.accessibleName(), "Feedback visual tipo banner")

    def test_show_feedback_info(self):
        """Test mostrar feedback de tipo info."""
        mensaje = "Información de prueba"
        self.banner.show_feedback(mensaje, "info", 1000)

        self.assertTrue(self.banner.isVisible())
        self.assertEqual(self.banner.text_label.text(), mensaje)
        self.assertEqual(self.banner.accessibleDescription(), mensaje)

    def test_show_feedback_exito(self):
        """Test mostrar feedback de tipo éxito."""
        mensaje = "Operación exitosa"
        self.banner.show_feedback(mensaje, "exito", 1000)

        self.assertTrue(self.banner.isVisible())
        self.assertEqual(self.banner.text_label.text(), mensaje)

    def test_show_feedback_error(self):
        """Test mostrar feedback de tipo error."""
        mensaje = "Error en la operación"
        self.banner.show_feedback(mensaje, "error", 1000)

        self.assertTrue(self.banner.isVisible())
        self.assertEqual(self.banner.text_label.text(), mensaje)

    def test_show_feedback_advertencia(self):
        """Test mostrar feedback de tipo advertencia."""
        mensaje = "Advertencia importante"
        self.banner.show_feedback(mensaje, "advertencia", 1000)

        self.assertTrue(self.banner.isVisible())
        self.assertEqual(self.banner.text_label.text(), mensaje)

    def test_hide_feedback(self):
        """Test ocultar feedback."""
        self.banner.show_feedback("Test", "info", 1000)
        self.assertTrue(self.banner.isVisible())

        self.banner.hide()
        self.assertFalse(self.banner.isVisible())
        self.assertEqual(self.banner.accessibleDescription(), "")

    def test_close_button_functionality(self):
        """Test funcionalidad del botón cerrar."""
        self.banner.show_feedback("Test", "info", 5000)
        self.assertTrue(self.banner.isVisible())

        # Simular click en botón cerrar
        self.banner.close_btn.click()
        self.assertFalse(self.banner.isVisible())


class TestHerrajesViewBasic(unittest.TestCase):
    """Tests básicos de HerrajesView."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

    def test_init_herrajes_view_basic(self):
        """Test inicialización básica de HerrajesView."""
        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

            self.assertEqual(view.objectName(), "HerrajesView")
            self.assertEqual(view.db_connection, self.mock_db)
            self.assertEqual(view.usuario_actual, self.usuario_test)
            self.assertEqual(view.controller, self.mock_controller)
            self.assertIsNotNone(view.boton_agregar)

    def test_init_herrajes_view_without_controller(self):
        """Test inicialización sin controlador."""
        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=None,
            )

            self.assertIsNone(view.controller)
            self.assertIsNotNone(view.boton_agregar)

    def test_components_initialization(self):
        """Test inicialización de componentes principales."""
        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

            # Verificar componentes principales
            self.assertIsNotNone(view.feedback_banner)
            self.assertIsNotNone(view.label_titulo)
            self.assertIsNotNone(view.tabs)
            self.assertIsNotNone(view.tabla_herrajes)
            self.assertIsNotNone(view.tabla_pedidos)

            # Verificar tabs
            self.assertEqual(view.tabs.count(), 2)
            self.assertEqual(view.tabs.tabText(0), "Herrajes")
            self.assertEqual(view.tabs.tabText(1), "Pedidos de Herrajes")


class TestHerrajesViewTablas(unittest.TestCase):
    """Tests para las tablas de HerrajesView."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_tabla_herrajes_properties(self):
        """Test propiedades de la tabla de herrajes."""
        tabla = self.view.tabla_herrajes

        self.assertEqual(tabla.objectName(), "tabla_herrajes")
        self.assertEqual(tabla.accessibleName(), "Tabla de herrajes")
        self.assertEqual(tabla.columnCount(), len(self.view.herrajes_headers))
        self.assertTrue(tabla.alternatingRowColors())
        self.assertEqual(tabla.selectionBehavior(), tabla.SelectionBehavior.SelectRows)

    def test_tabla_pedidos_properties(self):
        """Test propiedades de la tabla de pedidos."""
        tabla = self.view.tabla_pedidos

        self.assertEqual(tabla.objectName(), "tabla_pedidos_herrajes")
        self.assertEqual(tabla.accessibleName(), "Tabla de pedidos de herrajes")
        self.assertEqual(tabla.columnCount(), len(self.view.pedidos_headers))
        self.assertTrue(tabla.alternatingRowColors())
        self.assertEqual(tabla.selectionBehavior(), tabla.SelectionBehavior.SelectRows)

    def test_headers_content(self):
        """Test contenido de headers de tablas."""
        # Headers de herrajes
        expected_herrajes = [
            "ID",
            "Nombre",
            "Cantidad",
            "Proveedor",
            "Ubicación",
            "Stock mínimo",
        ]
        self.assertEqual(self.view.herrajes_headers, expected_herrajes)

        # Headers de pedidos
        expected_pedidos = [
            "ID Pedido",
            "Fecha",
            "Solicitante",
            "Herrajes",
            "Cantidad",
            "Estado",
            "Observaciones",
        ]
        self.assertEqual(self.view.pedidos_headers, expected_pedidos)


class TestHerrajesViewFeedback(unittest.TestCase):
    """Tests para el sistema de feedback visual."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_mostrar_feedback_info(self):
        """Test mostrar feedback de información."""
        mensaje = "Información de prueba"
        self.view.mostrar_feedback(mensaje, "info", 1000)

        self.assertTrue(self.view.feedback_banner.isVisible())
        self.assertEqual(self.view.feedback_banner.text_label.text(), mensaje)

    def test_mostrar_mensaje_alias(self):
        """Test alias mostrar_mensaje."""
        mensaje = "Mensaje de prueba"
        self.view.mostrar_mensaje(mensaje, "exito", 1000)

        self.assertTrue(self.view.feedback_banner.isVisible())
        self.assertEqual(self.view.feedback_banner.text_label.text(), mensaje)

    def test_ocultar_feedback(self):
        """Test ocultar feedback."""
        self.view.mostrar_feedback("Test", "info", 1000)
        self.assertTrue(self.view.feedback_banner.isVisible())

        self.view.ocultar_feedback()
        self.assertFalse(self.view.feedback_banner.isVisible())

    @patch("modules.herrajes.view.QDialog")
    @patch("modules.herrajes.view.QProgressBar")
    def test_mostrar_feedback_carga(self, mock_progress, mock_dialog):
        """Test mostrar feedback de carga."""
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance
        mock_progress_instance = Mock()
        mock_progress.return_value = mock_progress_instance

        resultado = self.view.mostrar_feedback_carga("Cargando datos...", 0, 100)

        mock_dialog.assert_called_once()
        mock_dialog_instance.setModal.assert_called_once_with(True)
        mock_dialog_instance.show.assert_called_once()

    def test_ocultar_feedback_carga_sin_dialog(self):
        """Test ocultar feedback de carga sin dialog activo."""
        # No debe lanzar excepción
        self.view.ocultar_feedback_carga()

    def test_ocultar_feedback_carga_con_dialog(self):
        """Test ocultar feedback de carga con dialog activo."""
        mock_dialog = Mock()
        self.view.dialog_carga = mock_dialog

        self.view.ocultar_feedback_carga()

        mock_dialog.accept.assert_called_once()
        self.assertIsNone(self.view.dialog_carga)


class TestHerrajesViewFiltros(unittest.TestCase):
    """Tests para el sistema de filtros."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_filtros_initialization(self):
        """Test inicialización de filtros."""
        # Verificar existencia de filtros
        self.assertIsNotNone(self.view.filtro_estado)
        self.assertIsNotNone(self.view.filtro_obra)
        self.assertIsNotNone(self.view.filtro_usuario)
        self.assertIsNotNone(self.view.filtro_tipo_herraje)
        self.assertIsNotNone(self.view.filtro_fecha_inicio)
        self.assertIsNotNone(self.view.filtro_fecha_fin)
        self.assertIsNotNone(self.view.filtro_stock_bajo)
        self.assertIsNotNone(self.view.filtro_busqueda)

    def test_filtros_default_values(self):
        """Test valores por defecto de filtros."""
        self.assertEqual(self.view.filtro_estado.currentText(), "Todos")
        self.assertEqual(self.view.filtro_obra.currentText(), "Todas las obras")
        self.assertEqual(self.view.filtro_usuario.currentText(), "Todos los usuarios")
        self.assertEqual(self.view.filtro_tipo_herraje.currentText(), "Todos los tipos")
        self.assertEqual(self.view.filtro_stock_bajo.currentText(), "Stock: Todos")

    def test_filtros_placeholders(self):
        """Test placeholders de filtros de texto."""
        self.assertEqual(
            self.view.filtro_fecha_inicio.placeholderText(), "Fecha desde (AAAA-MM-DD)"
        )
        self.assertEqual(
            self.view.filtro_fecha_fin.placeholderText(), "Fecha hasta (AAAA-MM-DD)"
        )
        self.assertEqual(
            self.view.filtro_busqueda.placeholderText(),
            "Buscar por obra, usuario, herraje, observaciones...",
        )

    def test_filtros_tooltips(self):
        """Test tooltips de filtros."""
        self.assertEqual(
            self.view.filtro_estado.toolTip(), "Filtrar por estado del pedido"
        )
        self.assertEqual(
            self.view.filtro_fecha_inicio.toolTip(), "Filtrar desde fecha (inclusive)"
        )
        self.assertEqual(
            self.view.filtro_fecha_fin.toolTip(), "Filtrar hasta fecha (inclusive)"
        )
        self.assertEqual(
            self.view.filtro_busqueda.toolTip(),
            "Búsqueda rápida en pedidos de herrajes",
        )


class TestHerrajesViewSenales(unittest.TestCase):
    """Tests para las señales de HerrajesView."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_signals_existence(self):
        """Test existencia de señales principales."""
        # Verificar que las señales existen
        self.assertTrue(hasattr(self.view, "nuevo_herraje_signal"))
        self.assertTrue(hasattr(self.view, "exportar_excel_signal"))
        self.assertTrue(hasattr(self.view, "buscar_signal"))
        self.assertTrue(hasattr(self.view, "ajustar_stock_signal"))
        self.assertTrue(hasattr(self.view, "generar_qr_signal"))
        self.assertTrue(hasattr(self.view, "nuevo_pedido_signal"))
        self.assertTrue(hasattr(self.view, "actualizar_signal"))


class TestHerrajesViewBotones(unittest.TestCase):
    """Tests para los botones de HerrajesView."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_boton_agregar_properties(self):
        """Test propiedades del botón agregar."""
        boton = self.view.boton_agregar

        self.assertIsNotNone(boton)
        self.assertEqual(boton.toolTip(), "Agregar nuevo herraje")
        self.assertEqual(boton.accessibleName(), "Botón agregar nuevo herraje")

    def test_boton_agregar_signal_connection(self):
        """Test conexión de señal del botón agregar."""
        # Mock para capturar la señal
        signal_mock = Mock()
        self.view.nuevo_herraje_signal.connect(signal_mock)

        # Simular click
        self.view.boton_agregar.click()

        # Verificar que se emitió la señal
        signal_mock.assert_called_once()


class TestHerrajesViewConfiguracion(unittest.TestCase):
    """Tests para funcionalidades de configuración."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_config_path_initialization(self):
        """Test inicialización del path de configuración."""
        self.assertTrue(self.view.config_path.endswith("config_herrajes_columns.json"))

    def test_columnas_visibles_default(self):
        """Test columnas visibles por defecto."""
        expected_columns = {
            "ID": True,
            "Nombre": True,
            "Cantidad": True,
            "Proveedor": True,
            "Ubicación": True,
            "Stock mínimo": True,
        }
        self.assertEqual(self.view.columnas_visibles, expected_columns)

    @patch("modules.herrajes.view.os.path.exists")
    @patch("modules.herrajes.view.open")
    @patch("modules.herrajes.view.json.load")
    def test_cargar_config_columnas_success(
        self, mock_json_load, mock_open, mock_exists
    ):
        """Test cargar configuración de columnas exitosamente."""
        # Arrange
        mock_exists.return_value = True
        mock_config = {"ID": False, "Nombre": True}
        mock_json_load.return_value = mock_config

        # Act
        resultado = self.view.cargar_config_columnas()

        # Assert
        self.assertEqual(resultado, mock_config)
        mock_exists.assert_called_once()
        mock_open.assert_called_once()

    @patch("modules.herrajes.view.os.path.exists")
    def test_cargar_config_columnas_file_not_exists(self, mock_exists):
        """Test cargar configuración cuando el archivo no existe."""
        # Arrange
        mock_exists.return_value = False

        # Act
        resultado = self.view.cargar_config_columnas()

        # Assert
        self.assertIsNone(resultado)

    @patch("modules.herrajes.view.os.path.exists")
    @patch("modules.herrajes.view.open")
    @patch("modules.herrajes.view.log_error")
    def test_cargar_config_columnas_error(self, mock_log_error, mock_open, mock_exists):
        """Test cargar configuración con error."""
        # Arrange
        mock_exists.return_value = True
        mock_open.side_effect = Exception("Error de lectura")

        # Act
        resultado = self.view.cargar_config_columnas()

        # Assert
        self.assertIsNone(resultado)
        mock_log_error.assert_called_once()


class TestHerrajesViewEdgeCases(unittest.TestCase):
    """Tests para casos edge y validaciones."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

    def test_init_with_none_values(self):
        """Test inicialización con valores None."""
        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            view = HerrajesView(
                db_connection=None, usuario_actual=None, controller=None
            )

            self.assertIsNone(view.db_connection)
            self.assertIsNone(view.usuario_actual)
            self.assertIsNone(view.controller)
            self.assertIsNotNone(view.boton_agregar)

    def test_init_with_default_usuario(self):
        """Test inicialización con usuario por defecto."""
        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            view = HerrajesView(db_connection=self.mock_db)

            self.assertEqual(view.usuario_actual, "default")

    @patch("utils.theme_manager.cargar_modo_tema")
    def test_tema_loading_error(self, mock_tema):
        """Test manejo de error al cargar tema."""
        mock_tema.side_effect = Exception("Error al cargar tema")

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"):
            # No debe lanzar excepción
            view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

            self.assertIsNotNone(view)


class TestHerrajesViewIntegration(unittest.TestCase):
    """Tests de integración para HerrajesView."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.usuario_test = "test_user"
        self.mock_controller = Mock()

        with patch("modules.herrajes.view.aplicar_qss_global_y_tema"), patch(
            "modules.herrajes.view.cargar_modo_tema"
        ) as mock_tema:
            mock_tema.return_value = "light"

            self.view = HerrajesView(
                db_connection=self.mock_db,
                usuario_actual=self.usuario_test,
                controller=self.mock_controller,
            )

    def test_controller_integration(self):
        """Test integración con controlador."""
        # Verificar que el controlador tiene el método refrescar_pedidos
        if hasattr(self.mock_controller, "refrescar_pedidos"):
            self.mock_controller.refrescar_pedidos.assert_called()

    def test_complete_ui_structure(self):
        """Test estructura completa de la UI."""
        # Verificar que todos los componentes principales están presentes
        components = [
            "feedback_banner",
            "label_titulo",
            "tabs",
            "tabla_herrajes",
            "tabla_pedidos",
            "filtro_estado",
            "filtro_obra",
            "filtro_usuario",
            "filtro_tipo_herraje",
            "filtro_fecha_inicio",
            "filtro_fecha_fin",
            "filtro_stock_bajo",
            "filtro_busqueda",
        ]

        for component in components:
            self.assertTrue(
                hasattr(self.view, component), f"Falta componente: {component}"
            )
            self.assertIsNotNone(
                getattr(self.view, component), f"Componente nulo: {component}"
            )

    def test_accessibility_attributes(self):
        """Test atributos de accesibilidad."""
        # Verificar atributos de accesibilidad en componentes principales
        self.assertEqual(
            self.view.feedback_banner.accessibleName(), "Feedback visual tipo banner"
        )
        self.assertEqual(
            self.view.label_titulo.accessibleName(), "Título de módulo Herrajes"
        )
        self.assertEqual(self.view.tabla_herrajes.accessibleName(), "Tabla de herrajes")
        self.assertEqual(
            self.view.tabla_pedidos.accessibleName(), "Tabla de pedidos de herrajes"
        )


if __name__ == "__main__":
    unittest.main()
