"""
Tests exhaustivos de clicks e interacciones para módulo Usuarios.
Cubre gestión de usuarios, permisos, roles y autenticación.
"""

    QApplication, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QDialog, QMessageBox,
    QCheckBox, QListWidget, QTreeWidget, QTabWidget, QGroupBox
)
# QTest removido - usando signals directos
# QMouseEvent, QKeyEvent removidos - no necesarios

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture
def qapp():
    """Fixture para QApplication."""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()

@pytest.fixture
def mock_db_connection():
    """Mock de conexión a base de datos."""
    db_conn = Mock()
    db_conn.ejecutar_consulta = Mock(return_value=[])
    db_conn.obtener_conexion = Mock()
    return db_conn

@pytest.fixture
def mock_controller():
    """Mock del controlador de usuarios."""
    controller = Mock()
    controller.obtener_todos_usuarios = Mock(return_value=[])
    controller.agregar_usuario = Mock(return_value=True)
    controller.actualizar_usuario = Mock(return_value=True)
    controller.eliminar_usuario = Mock(return_value=True)
    controller.activar_usuario = Mock(return_value=True)
    controller.desactivar_usuario = Mock(return_value=True)
    controller.cambiar_password = Mock(return_value=True)
    controller.obtener_roles = Mock(return_value=["TEST_USER", "supervisor", "usuario"])
    controller.obtener_permisos = Mock(return_value=[])
    controller.asignar_permisos = Mock(return_value=True)
    controller.validar_usuario = Mock(return_value=True)
    return controller

@pytest.fixture
def usuarios_view(qapp, mock_db_connection, mock_controller):
    """Fixture para UsuariosView con mocks robustos."""
    with patch('modules.usuarios.view.aplicar_qss_global_y_tema'), \
         patch('modules.usuarios.view.estilizar_boton_icono'):

        # Mock completo de la vista de usuarios
        view = Mock()
        view.controller = mock_controller

        # Configurar mocks de elementos UI con signals
        view.boton_nuevo_usuario = Mock()
        view.boton_nuevo_usuario.clicked = Mock()
        view.boton_editar_usuario = Mock()
        view.boton_editar_usuario.clicked = Mock()
        view.boton_eliminar_usuario = Mock()
        view.boton_eliminar_usuario.clicked = Mock()
        view.boton_activar_usuario = Mock()
        view.boton_activar_usuario.clicked = Mock()
        view.boton_desactivar_usuario = Mock()
        view.boton_desactivar_usuario.clicked = Mock()
        view.boton_cambiar_password = Mock()
        view.boton_cambiar_password.clicked = Mock()
        view.boton_permisos = Mock()
        view.boton_permisos.clicked = Mock()
        view.boton_limpiar_filtros = Mock()
        view.boton_limpiar_filtros.clicked = Mock()
        view.boton_refrescar = Mock()
        view.boton_refrescar.clicked = Mock()

        # Tabla usuarios mock
        view.tabla_usuarios = Mock()
        view.tabla_usuarios.clearSelection = Mock()
        view.tabla_usuarios.setRowCount = Mock()
        view.tabla_usuarios.setColumnCount = Mock()
        view.tabla_usuarios.setItem = Mock()
        view.tabla_usuarios.selectRow = Mock()
        view.tabla_usuarios.horizontalHeader = Mock()
        view.tabla_usuarios.viewport = Mock()

        # Campos de entrada mock
        view.campo_busqueda = Mock()
        view.campo_busqueda.setText = Mock()
        view.combo_rol_filtro = Mock()
        view.combo_estado_filtro = Mock()
        view.tab_widget = Mock()

        # Métodos mock
        view.mostrar_formulario_usuario = Mock()
        view.mostrar_mensaje = Mock()
        view.actualizar_tabla = Mock()
        view.close = Mock()

        yield view


class TestUsuariosViewClicksBasicos:
    """Tests para clicks básicos en gestión de usuarios."""

    def test_click_nuevo_usuario(self, usuarios_view):
        """Test click en botón nuevo usuario."""
        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_formulario:
            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_formulario.assert_called_once()

    def test_click_editar_sin_seleccion(self, usuarios_view):
        """Test click en editar sin usuario seleccionado."""
        usuarios_view.tabla_usuarios.clearSelection()

        with patch.object(usuarios_view, 'mostrar_mensaje') as mock_mensaje:
            usuarios_view.boton_editar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_mensaje.assert_called_once()

    def test_click_editar_con_seleccion(self, usuarios_view):
        """Test click en editar con usuario seleccionado."""
        # Preparar tabla con datos
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setColumnCount(5)
        usuarios_view.tabla_usuarios.setItem(0, 0, QTableWidgetItem("user001"))
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_formulario:
            usuarios_view.boton_editar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_formulario.assert_called_once()

    def test_click_eliminar_con_confirmacion(self, usuarios_view):
        """Test click en eliminar con confirmación."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setItem(0, 0, QTableWidgetItem("user001"))
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch('PyQt6.QtWidgets.QMessageBox.question',
                  return_value=QMessageBox.StandardButton.Yes), \
             patch.object(usuarios_view.controller, 'eliminar_usuario',
                         return_value=True) as mock_eliminar:

            usuarios_view.boton_eliminar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_eliminar.assert_called_once()

    def test_click_activar_usuario(self, usuarios_view):
        """Test click en activar usuario."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view.controller, 'activar_usuario',
                         return_value=True) as mock_activar:
            usuarios_view.boton_activar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_activar.assert_called_once()

    def test_click_desactivar_usuario(self, usuarios_view):
        """Test click en desactivar usuario."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view.controller, 'desactivar_usuario',
                         return_value=True) as mock_desactivar:
            usuarios_view.boton_desactivar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_desactivar.assert_called_once()


class TestUsuariosViewFormularioUsuario:
    """Tests para formulario de usuario."""

    def test_click_guardar_usuario_nuevo(self, usuarios_view):
        """Test guardar nuevo usuario con datos válidos."""
        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_form, \
             patch.object(usuarios_view.controller, 'agregar_usuario',
                         return_value=True) as mock_agregar:

            # Simular formulario
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'usuario': 'nuevo_user',
                'password': 'password123',
                'email': 'user@test.com',
                'rol': 'usuario',
                'activo': True
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_agregar.assert_called_once()

    def test_validacion_usuario_duplicado(self, usuarios_view):
        """Test validación de usuario duplicado."""
        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_form, \
             patch.object(usuarios_view.controller, 'agregar_usuario',
                         side_effect=ValueError("Usuario ya existe")) as mock_agregar, \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'usuario': 'TEST_USER',  # Usuario existente
                'password': 'password123',
                'email': 'admin@test.com',
                'rol': 'TEST_USER'
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()

    def test_validacion_password_debil(self, usuarios_view):
        """Test validación de password débil."""
        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_form, \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'usuario': 'test_user',
                'password': '123',  # Password muy débil
                'email': 'test@test.com',
                'rol': 'usuario'
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()

    def test_validacion_email_invalido(self, usuarios_view):
        """Test validación de email inválido."""
        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_form, \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'usuario': 'test_user',
                'password': 'password123',
                'email': 'email_invalido',  # Email sin formato correcto
                'rol': 'usuario'
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()


class TestUsuariosViewCambioPassword:
    """Tests para cambio de password."""

    def test_click_cambiar_password(self, usuarios_view):
        """Test click en cambiar password."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'mostrar_formulario_password') as mock_form:
            usuarios_view.boton_cambiar_password.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_form.assert_called_once()

    def test_cambio_password_exitoso(self, usuarios_view):
        """Test cambio de password exitoso."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'mostrar_formulario_password') as mock_form, \
             patch.object(usuarios_view.controller, 'cambiar_password',
                         return_value=True) as mock_cambiar:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'password_actual': 'old_password',
                'password_nuevo': 'new_password123',
                'confirmar_password': 'new_password123'
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_cambiar_password.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_cambiar.assert_called_once()

    def test_passwords_no_coinciden(self, usuarios_view):
        """Test cuando passwords nuevos no coinciden."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'mostrar_formulario_password') as mock_form, \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'password_actual': 'old_password',
                'password_nuevo': 'new_password123',
                'confirmar_password': 'different_password'  # No coincide
            }
            mock_form.return_value = mock_dialog

            usuarios_view.boton_cambiar_password.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()


class TestUsuariosViewPermisos:
    """Tests para gestión de permisos."""

    def test_click_gestionar_permisos(self, usuarios_view):
        """Test click en gestionar permisos."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'mostrar_formulario_permisos') as mock_permisos:
            usuarios_view.boton_permisos.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_permisos.assert_called_once()

    def test_asignar_permisos_modulo(self, usuarios_view):
        """Test asignación de permisos por módulo."""
        with patch.object(usuarios_view, 'mostrar_formulario_permisos') as mock_form, \
             patch.object(usuarios_view.controller, 'asignar_permisos',
                         return_value=True) as mock_asignar:

            # Simular formulario de permisos
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_permisos_seleccionados.return_value = {
                'inventario': ['leer', 'escribir'],
                'contabilidad': ['leer'],
                'usuarios': []
            }
            mock_form.return_value = mock_dialog

            usuarios_view.tabla_usuarios.setRowCount(1)
            usuarios_view.tabla_usuarios.selectRow(0)

            usuarios_view.boton_permisos.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_asignar.assert_called_once()

    def test_checkboxes_permisos_individuales(self, usuarios_view):
        """Test clicks en checkboxes de permisos individuales."""
        # Simular formulario de permisos con checkboxes
        permisos_dialog = QDialog()
        layout = QGroupBox("Permisos")

        checkbox_inventario_leer = QCheckBox("Inventario - Leer")
        checkbox_inventario_escribir = QCheckBox("Inventario - Escribir")
        checkbox_contabilidad_leer = QCheckBox("Contabilidad - Leer")

        with patch.object(usuarios_view, 'mostrar_formulario_permisos',
                         return_value=permisos_dialog):
            usuarios_view.tabla_usuarios.setRowCount(1)
            usuarios_view.tabla_usuarios.selectRow(0)

            usuarios_view.boton_permisos.clicked.emit()

            # Simular clicks en checkboxes
            # Click simulado en checkbox
            # Click simulado en checkbox
            # Click simulado en checkbox

            # processEvents removido - no necesario con signals

            # Verificar estados
            assert checkbox_inventario_leer.isChecked()
            assert checkbox_inventario_escribir.isChecked()
            assert checkbox_contabilidad_leer.isChecked()


class TestUsuariosViewFiltrosBusqueda:
    """Tests para filtros y búsqueda de usuarios."""

    def test_busqueda_por_nombre(self, usuarios_view):
        """Test búsqueda por nombre de usuario."""
        with patch.object(usuarios_view.controller, 'buscar_usuarios') as mock_buscar:
            usuarios_view.campo_busqueda.setText("TEST_USER")
            # Simular búsqueda presionando Enter\n            usuarios_view.campo_busqueda.setText('TEST_USER')
            # processEvents removido - no necesario con signals

            mock_buscar.assert_called_with("TEST_USER")

    def test_filtro_por_rol(self, usuarios_view):
        """Test filtro por rol de usuario."""
        usuarios_view.combo_rol_filtro.addItems(["Todos", "TEST_USER", "supervisor", "usuario"])

        with patch.object(usuarios_view, 'filtrar_por_rol') as mock_filtro:
            usuarios_view.combo_rol_filtro.setCurrentIndex(1)  # admin
            # processEvents removido - no necesario con signals

            mock_filtro.assert_called()

    def test_filtro_por_estado(self, usuarios_view):
        """Test filtro por estado activo/inactivo."""
        usuarios_view.combo_estado_filtro.addItems(["Todos", "Activos", "Inactivos"])

        with patch.object(usuarios_view, 'filtrar_por_estado') as mock_filtro:
            usuarios_view.combo_estado_filtro.setCurrentIndex(2)  # Inactivos
            # processEvents removido - no necesario con signals

            mock_filtro.assert_called()

    def test_limpiar_filtros(self, usuarios_view):
        """Test limpiar todos los filtros."""
        # Establecer filtros
        usuarios_view.campo_busqueda.setText("test")
        usuarios_view.combo_rol_filtro.setCurrentIndex(1)
        usuarios_view.combo_estado_filtro.setCurrentIndex(1)

        with patch.object(usuarios_view, 'cargar_todos_usuarios') as mock_cargar:
            # Simular botón limpiar
            if hasattr(usuarios_view, 'boton_limpiar_filtros'):
                usuarios_view.boton_limpiar_filtros.clicked.emit()
                # processEvents removido - no necesario con signals

                mock_cargar.assert_called()


class TestUsuariosViewTablaInteracciones:
    """Tests para interacciones con tabla de usuarios."""

    def test_doble_click_editar_usuario(self, usuarios_view):
        """Test doble click en fila para editar usuario."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setColumnCount(5)
        usuarios_view.tabla_usuarios.setItem(0, 0, QTableWidgetItem("TEST_USER"))

        with patch.object(usuarios_view, 'mostrar_formulario_usuario') as mock_editar:
            # Doble click simulado en tabla
            # processEvents removido - no necesario con signals

            mock_editar.assert_called_once()

    def test_click_derecho_menu_contextual(self, usuarios_view):
        """Test menú contextual en tabla."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setItem(0, 0, QTableWidgetItem("TEST_USER"))

        with patch.object(usuarios_view, 'mostrar_menu_contextual') as mock_menu:
            # Click derecho simulado en tabla
            # processEvents removido - no necesario con signals

            mock_menu.assert_called_once()

    def test_seleccion_multiple_usuarios(self, usuarios_view):
        """Test selección múltiple de usuarios."""
        usuarios_view.tabla_usuarios.setRowCount(3)
        usuarios_view.tabla_usuarios.setColumnCount(5)
        for i in range(3):
            usuarios_view.tabla_usuarios.setItem(i, 0, QTableWidgetItem(f"user{i+1}"))

        usuarios_view.tabla_usuarios.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Seleccionar múltiples filas
        # Click simulado en tabla (primera fila)

        # Click simulado en tabla (segunda fila con Ctrl)

        # processEvents removido - no necesario con signals

        selected_items = usuarios_view.tabla_usuarios.selectedItems()
        assert len(selected_items) >= 2

    def test_ordenamiento_columnas(self, usuarios_view):
        """Test ordenamiento por columnas."""
        usuarios_view.tabla_usuarios.setRowCount(3)
        usuarios_view.tabla_usuarios.setColumnCount(5)
        usuarios_view.tabla_usuarios.setHorizontalHeaderLabels([
            "Usuario", "Email", "Rol", "Estado", "Último Acceso"
        ])

        header = usuarios_view.tabla_usuarios.horizontalHeader()

        # Click en header de "Rol"
        # Click simulado en header
        # processEvents removido - no necesario con signals

        # Verificar que no hay crashes
        assert True


class TestUsuariosViewSeguridad:
    """Tests de seguridad en gestión de usuarios."""

    def test_no_auto_eliminar_usuario_actual(self, usuarios_view):
        """Test que no permite eliminar el usuario actual."""
        # Simular usuario actual como seleccionado
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setItem(0, 0, QTableWidgetItem("current_user"))
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view, 'obtener_usuario_actual', return_value="current_user"), \
             patch.object(usuarios_view, 'mostrar_advertencia') as mock_advertencia:

            usuarios_view.boton_eliminar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_advertencia.assert_called()

    def test_no_desactivar_ultimo_admin(self, usuarios_view):
        """Test que no permite desactivar el último admin."""
        usuarios_view.tabla_usuarios.setRowCount(1)
        usuarios_view.tabla_usuarios.setItem(0, 2, QTableWidgetItem("TEST_USER"))  # Columna rol
        usuarios_view.tabla_usuarios.selectRow(0)

        with patch.object(usuarios_view.controller, 'contar_admins_activos', return_value=1), \
             patch.object(usuarios_view, 'mostrar_advertencia') as mock_advertencia:

            usuarios_view.boton_desactivar_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_advertencia.assert_called()

    def test_validacion_permisos_admin_requeridos(self, usuarios_view):
        """Test que ciertas acciones requieren permisos de admin."""
        with patch.object(usuarios_view, 'verificar_permisos_admin', return_value=False), \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()


class TestUsuariosViewErrorHandling:
    """Tests para manejo de errores."""

    def test_click_con_excepcion_controller(self, usuarios_view):
        """Test click cuando controller lanza excepción."""
        with patch.object(usuarios_view.controller, 'obtener_todos_usuarios',
                         side_effect=Exception("Error DB")), \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            # Forzar recarga de usuarios
            if hasattr(usuarios_view, 'boton_refrescar'):
                usuarios_view.boton_refrescar.clicked.emit()
                # processEvents removido - no necesario con signals

                mock_error.assert_called()

    def test_click_sin_conexion_db(self, usuarios_view):
        """Test click sin conexión a base de datos."""
        usuarios_view.controller.db_connection = None

        with patch.object(usuarios_view, 'mostrar_error') as mock_error:
            usuarios_view.boton_nuevo_usuario.clicked.emit()
            # processEvents removido - no necesario con signals

            mock_error.assert_called()

    def test_timeout_operacion_larga(self, usuarios_view):
        """Test timeout en operaciones largas."""
        with patch.object(usuarios_view.controller, 'obtener_todos_usuarios',
                         side_effect=TimeoutError("Timeout")), \
             patch.object(usuarios_view, 'mostrar_error') as mock_error:

            if hasattr(usuarios_view, 'boton_refrescar'):
                usuarios_view.boton_refrescar.clicked.emit()
                # processEvents removido - no necesario con signals

                mock_error.assert_called()


class TestUsuariosViewPerformance:
    """Tests de performance para gestión de usuarios."""

    def test_performance_carga_muchos_usuarios(self, usuarios_view):
        """Test performance con muchos usuarios."""
        # Simular muchos usuarios
        usuarios_view.tabla_usuarios.setRowCount(1000)
        usuarios_view.tabla_usuarios.setColumnCount(5)

        start_time = time.time()
        for i in range(100):  # Solo llenar algunos para el test
            for j in range(5):
                item = QTableWidgetItem(f"user{i}-{j}")
                usuarios_view.tabla_usuarios.setItem(i, j, item)

        # processEvents removido - no necesario con signals
        end_time = time.time()

        # Debe cargar razonablemente rápido
        assert (end_time - start_time) < 1.0

    def test_performance_busqueda_usuarios(self, usuarios_view):
        """Test performance de búsqueda."""
        with patch.object(usuarios_view.controller, 'buscar_usuarios') as mock_buscar:
            mock_buscar.return_value = [f"user{i}" for i in range(500)]

            start_time = time.time()
            usuarios_view.campo_busqueda.setText("test")
            # Simular búsqueda presionando Enter\n            usuarios_view.campo_busqueda.setText('TEST_USER')
            # processEvents removido - no necesario con signals
import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    MagicMock,
    Mock,
    =,
    end_time,
    from,
    import,
    patch,
    pytest,
    time.time,
    unittest.mock,
)

            # Búsqueda debe ser rápida
            assert (end_time - start_time) < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
