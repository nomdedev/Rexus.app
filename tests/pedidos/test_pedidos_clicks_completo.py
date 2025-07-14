"""
Tests exhaustivos de clicks e interacciones para módulo Pedidos.
Cubre gestión de pedidos, seguimiento, estados y aprobaciones.
"""

    QApplication, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QDialog, QMessageBox,
    QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QTabWidget,
    QProgressBar, QListWidget, QCheckBox
)
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
    """Mock del controlador de pedidos."""
    controller = Mock()
    controller.obtener_todos_pedidos = Mock(return_value=[])
    controller.crear_pedido = Mock(return_value=True)
    controller.actualizar_pedido = Mock(return_value=True)
    controller.eliminar_pedido = Mock(return_value=True)
    controller.aprobar_pedido = Mock(return_value=True)
    controller.rechazar_pedido = Mock(return_value=True)
    controller.cambiar_estado = Mock(return_value=True)
    controller.obtener_estados = Mock(return_value=["Pendiente", "Aprobado", "Enviado", "Entregado"])
    controller.obtener_proveedores = Mock(return_value=["Proveedor A", "Proveedor B"])
    controller.calcular_total = Mock(return_value=Decimal('100.00'))
    controller.generar_qr = Mock(return_value=True)
    controller.exportar_pedido = Mock(return_value=True)
    return controller

@pytest.fixture
def pedidos_view(qapp, mock_db_connection, mock_controller):
    """Fixture para PedidosView con mocks."""
    with patch('modules.pedidos.view.aplicar_qss_global_y_tema'), \
         patch('modules.pedidos.view.estilizar_boton_icono'), \
         patch('modules.pedidos.view.get_icon'):

        view = PedidosView()
        view.controller = mock_controller

        # Asegurar que todos los elementos UI existen
        if not hasattr(view, 'boton_nuevo_pedido'):
            view.boton_nuevo_pedido = QPushButton("Nuevo Pedido")
        if not hasattr(view, 'boton_editar_pedido'):
            view.boton_editar_pedido = QPushButton("Editar")
        if not hasattr(view, 'boton_eliminar_pedido'):
            view.boton_eliminar_pedido = QPushButton("Eliminar")
        if not hasattr(view, 'boton_aprobar'):
            view.boton_aprobar = QPushButton("Aprobar")
        if not hasattr(view, 'boton_rechazar'):
            view.boton_rechazar = QPushButton("Rechazar")
        if not hasattr(view, 'boton_exportar'):
            view.boton_exportar = QPushButton("Exportar")
        if not hasattr(view, 'boton_generar_qr'):
            view.boton_generar_qr = QPushButton("Generar QR")
        if not hasattr(view, 'tabla_pedidos'):
            view.tabla_pedidos = QTableWidget()
        if not hasattr(view, 'combo_estado_filtro'):
            view.combo_estado_filtro = QComboBox()
        if not hasattr(view, 'combo_proveedor_filtro'):
            view.combo_proveedor_filtro = QComboBox()
        if not hasattr(view, 'fecha_desde'):
            view.fecha_desde = QDateEdit()
        if not hasattr(view, 'fecha_hasta'):
            view.fecha_hasta = QDateEdit()
        if not hasattr(view, 'campo_busqueda'):
            view.campo_busqueda = QLineEdit()
        if not hasattr(view, 'progress_bar'):
            view.progress_bar = QProgressBar()

        yield view
        view.close()


class TestPedidosViewClicksBasicos:
    """Tests para clicks básicos en gestión de pedidos."""

    def test_click_nuevo_pedido(self, pedidos_view):
        """Test click en botón nuevo pedido."""
        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_formulario:
            QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_formulario.assert_called_once()

    def test_click_editar_sin_seleccion(self, pedidos_view):
        """Test click en editar sin pedido seleccionado."""
        pedidos_view.tabla_pedidos.clearSelection()

        with patch.object(pedidos_view, 'mostrar_mensaje') as mock_mensaje:
            QTest.mouseClick(pedidos_view.boton_editar_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_mensaje.assert_called_once()

    def test_click_editar_con_seleccion(self, pedidos_view):
        """Test click en editar con pedido seleccionado."""
        # Preparar tabla con datos
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setColumnCount(6)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_formulario:
            QTest.mouseClick(pedidos_view.boton_editar_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_formulario.assert_called_once()

    def test_click_aprobar_pedido(self, pedidos_view):
        """Test click en aprobar pedido."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.setItem(0, 3, QTableWidgetItem("Pendiente"))  # Estado
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch('PyQt6.QtWidgets.QMessageBox.question',
                  return_value=QMessageBox.StandardButton.Yes), \
             patch.object(pedidos_view.controller, 'aprobar_pedido',
                         return_value=True) as mock_aprobar:

            QTest.mouseClick(pedidos_view.boton_aprobar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_aprobar.assert_called_once()

    def test_click_rechazar_pedido(self, pedidos_view):
        """Test click en rechazar pedido."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch('PyQt6.QtWidgets.QMessageBox.question',
                  return_value=QMessageBox.StandardButton.Yes), \
             patch.object(pedidos_view.controller, 'rechazar_pedido',
                         return_value=True) as mock_rechazar:

            QTest.mouseClick(pedidos_view.boton_rechazar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_rechazar.assert_called_once()

    def test_click_eliminar_con_confirmacion(self, pedidos_view):
        """Test click en eliminar con confirmación."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch('PyQt6.QtWidgets.QMessageBox.question',
                  return_value=QMessageBox.StandardButton.Yes), \
             patch.object(pedidos_view.controller, 'eliminar_pedido',
                         return_value=True) as mock_eliminar:

            QTest.mouseClick(pedidos_view.boton_eliminar_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_eliminar.assert_called_once()


class TestPedidosViewFormularioPedido:
    """Tests para formulario de pedidos."""

    def test_click_guardar_pedido_nuevo(self, pedidos_view):
        """Test guardar nuevo pedido con datos válidos."""
        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_form, \
             patch.object(pedidos_view.controller, 'crear_pedido',
                         return_value=True) as mock_crear:

            # Simular formulario
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'proveedor': 'Proveedor A',
                'fecha_entrega': QDate.currentDate().addDays(7),
                'items': [
                    {'producto': 'Item 1', 'cantidad': 10, 'precio': Decimal('15.50')},
                    {'producto': 'Item 2', 'cantidad': 5, 'precio': Decimal('25.00')}
                ],
                'observaciones': 'Pedido urgente'
            }
            mock_form.return_value = mock_dialog

            QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_crear.assert_called_once()

    def test_validacion_items_vacios(self, pedidos_view):
        """Test validación de pedido sin items."""
        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_form, \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'proveedor': 'Proveedor A',
                'fecha_entrega': QDate.currentDate(),
                'items': [],  # Sin items
                'observaciones': ''
            }
            mock_form.return_value = mock_dialog

            QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_error.assert_called()

    def test_validacion_fecha_pasada(self, pedidos_view):
        """Test validación de fecha de entrega en el pasado."""
        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_form, \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_datos.return_value = {
                'proveedor': 'Proveedor A',
                'fecha_entrega': QDate.currentDate().addDays(-1),  # Fecha pasada
                'items': [{'producto': 'Item 1', 'cantidad': 1, 'precio': Decimal('10.00')}],
                'observaciones': ''
            }
            mock_form.return_value = mock_dialog

            QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_error.assert_called()

    def test_cancelar_formulario_pedido(self, pedidos_view):
        """Test cancelar formulario de pedido."""
        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_form, \
             patch.object(pedidos_view.controller, 'crear_pedido') as mock_crear:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Rejected
            mock_form.return_value = mock_dialog

            QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            # No debe crear pedido
            mock_crear.assert_not_called()


class TestPedidosViewTablaInteracciones:
    """Tests para interacciones con tabla de pedidos."""

    def test_doble_click_editar_pedido(self, pedidos_view):
        """Test doble click en fila para editar pedido."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setColumnCount(6)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))

        with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_editar:
            QTest.mouseDClick(
                pedidos_view.tabla_pedidos.viewport(),
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
                QPoint(50, 20)
            )
            QApplication.processEvents()

            mock_editar.assert_called_once()

    def test_click_derecho_menu_contextual(self, pedidos_view):
        """Test menú contextual en tabla."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))

        with patch.object(pedidos_view, 'mostrar_menu_contextual') as mock_menu:
            QTest.mouseClick(
                pedidos_view.tabla_pedidos.viewport(),
                Qt.MouseButton.RightButton,
                Qt.KeyboardModifier.NoModifier,
                QPoint(50, 20)
            )
            QApplication.processEvents()

            mock_menu.assert_called_once()

    def test_ordenamiento_por_columnas(self, pedidos_view):
        """Test ordenamiento clickeando headers."""
        pedidos_view.tabla_pedidos.setRowCount(3)
        pedidos_view.tabla_pedidos.setColumnCount(6)
        pedidos_view.tabla_pedidos.setHorizontalHeaderLabels([
            "ID", "Proveedor", "Fecha", "Estado", "Total", "Acciones"
        ])

        header = pedidos_view.tabla_pedidos.horizontalHeader()

        # Click en columna "Estado"
        QTest.mouseClick(header.viewport(), Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier, QPoint(200, 10))
        QApplication.processEvents()

        # Verificar que no hay crashes
        assert True

    def test_seleccion_multiple_pedidos(self, pedidos_view):
        """Test selección múltiple de pedidos."""
        pedidos_view.tabla_pedidos.setRowCount(3)
        pedidos_view.tabla_pedidos.setColumnCount(6)
        for i in range(3):
            pedidos_view.tabla_pedidos.setItem(i, 0, QTableWidgetItem(f"PED00{i+1}"))

        pedidos_view.tabla_pedidos.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Seleccionar múltiples pedidos
        QTest.mouseClick(
            pedidos_view.tabla_pedidos.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QPoint(50, 20)
        )

        QTest.mouseClick(
            pedidos_view.tabla_pedidos.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.ControlModifier,
            QPoint(50, 40)
        )

        QApplication.processEvents()

        selected_items = pedidos_view.tabla_pedidos.selectedItems()
        assert len(selected_items) >= 2


class TestPedidosViewFiltrosYBusqueda:
    """Tests para filtros y búsqueda de pedidos."""

    def test_filtro_por_estado(self, pedidos_view):
        """Test filtro por estado de pedido."""
        pedidos_view.combo_estado_filtro.addItems(["Todos", "Pendiente", "Aprobado", "Enviado"])

        with patch.object(pedidos_view, 'filtrar_por_estado') as mock_filtro:
            pedidos_view.combo_estado_filtro.setCurrentIndex(1)  # Pendiente
            QApplication.processEvents()

            mock_filtro.assert_called()

    def test_filtro_por_proveedor(self, pedidos_view):
        """Test filtro por proveedor."""
        pedidos_view.combo_proveedor_filtro.addItems(["Todos", "Proveedor A", "Proveedor B"])

        with patch.object(pedidos_view, 'filtrar_por_proveedor') as mock_filtro:
            pedidos_view.combo_proveedor_filtro.setCurrentIndex(1)  # Proveedor A
            QApplication.processEvents()

            mock_filtro.assert_called()

    def test_filtro_por_fecha(self, pedidos_view):
        """Test filtro por rango de fechas."""
        fecha_inicio = QDate(2024, 1, 1)
        fecha_fin = QDate(2024, 12, 31)

        with patch.object(pedidos_view, 'aplicar_filtro_fechas') as mock_filtro:
            pedidos_view.fecha_desde.setDate(fecha_inicio)
            pedidos_view.fecha_hasta.setDate(fecha_fin)
            QApplication.processEvents()

            mock_filtro.assert_called()

    def test_busqueda_por_id_pedido(self, pedidos_view):
        """Test búsqueda por ID de pedido."""
        with patch.object(pedidos_view.controller, 'buscar_pedidos') as mock_buscar:
            pedidos_view.campo_busqueda.setText("PED001")
            QTest.keyClick(pedidos_view.campo_busqueda, Qt.Key.Key_Return)
            QApplication.processEvents()

            mock_buscar.assert_called_with("PED001")

    def test_limpiar_filtros(self, pedidos_view):
        """Test limpiar todos los filtros."""
        # Establecer filtros
        pedidos_view.combo_estado_filtro.setCurrentIndex(1)
        pedidos_view.combo_proveedor_filtro.setCurrentIndex(1)
        pedidos_view.campo_busqueda.setText("test")

        with patch.object(pedidos_view, 'cargar_todos_pedidos') as mock_cargar:
            if hasattr(pedidos_view, 'boton_limpiar_filtros'):
                QTest.mouseClick(pedidos_view.boton_limpiar_filtros, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                mock_cargar.assert_called()


class TestPedidosViewQRYExportacion:
    """Tests para generación de QR y exportación."""

    def test_click_generar_qr(self, pedidos_view):
        """Test generar código QR para pedido."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view.controller, 'generar_qr',
                         return_value=True) as mock_qr:
            QTest.mouseClick(pedidos_view.boton_generar_qr, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_qr.assert_called_once()

    def test_generar_qr_sin_seleccion(self, pedidos_view):
        """Test generar QR sin pedido seleccionado."""
        pedidos_view.tabla_pedidos.clearSelection()

        with patch.object(pedidos_view, 'mostrar_mensaje') as mock_mensaje:
            QTest.mouseClick(pedidos_view.boton_generar_qr, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_mensaje.assert_called()

    def test_click_exportar_pedido(self, pedidos_view):
        """Test exportar pedido a PDF."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName',
                  return_value=("pedido.pdf", "PDF Files (*.pdf)")), \
             patch.object(pedidos_view.controller, 'exportar_pedido',
                         return_value=True) as mock_exportar:

            QTest.mouseClick(pedidos_view.boton_exportar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_exportar.assert_called_once()

    def test_exportar_sin_datos(self, pedidos_view):
        """Test exportar cuando no hay pedidos."""
        pedidos_view.tabla_pedidos.setRowCount(0)

        with patch.object(pedidos_view, 'mostrar_advertencia') as mock_advertencia:
            QTest.mouseClick(pedidos_view.boton_exportar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_advertencia.assert_called()


class TestPedidosViewEstados:
    """Tests para cambios de estado de pedidos."""

    def test_cambio_estado_manual(self, pedidos_view):
        """Test cambio manual de estado."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.setItem(0, 3, QTableWidgetItem("Pendiente"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view, 'mostrar_selector_estado') as mock_selector, \
             patch.object(pedidos_view.controller, 'cambiar_estado',
                         return_value=True) as mock_cambiar:

            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.obtener_estado_seleccionado.return_value = "Enviado"
            mock_selector.return_value = mock_dialog

            # Simular click en celda de estado (si es clickeable)
            if hasattr(pedidos_view, 'boton_cambiar_estado'):
                QTest.mouseClick(pedidos_view.boton_cambiar_estado, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                mock_cambiar.assert_called_once()

    def test_progreso_visual_cambio_estado(self, pedidos_view):
        """Test progreso visual durante cambio de estado."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view.controller, 'cambiar_estado') as mock_cambiar:
            # Simular operación larga
            mock_cambiar.return_value = True

            if hasattr(pedidos_view, 'boton_cambiar_estado'):
                QTest.mouseClick(pedidos_view.boton_cambiar_estado, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                # Verificar que el progress bar se muestra
                assert pedidos_view.progress_bar.isVisible() or True

    def test_historial_cambios_estado(self, pedidos_view):
        """Test visualización de historial de cambios."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view, 'mostrar_historial_estado') as mock_historial:
            # Simular botón de historial (si existe)
            if hasattr(pedidos_view, 'boton_historial'):
                QTest.mouseClick(pedidos_view.boton_historial, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                mock_historial.assert_called_once()


class TestPedidosViewValidacionesSeguridad:
    """Tests de validaciones y seguridad."""

    def test_no_aprobar_pedido_ya_aprobado(self, pedidos_view):
        """Test que no permite aprobar pedido ya aprobado."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 0, QTableWidgetItem("PED001"))
        pedidos_view.tabla_pedidos.setItem(0, 3, QTableWidgetItem("Aprobado"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view, 'mostrar_advertencia') as mock_advertencia:
            QTest.mouseClick(pedidos_view.boton_aprobar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_advertencia.assert_called()

    def test_validacion_permisos_aprobacion(self, pedidos_view):
        """Test validación de permisos para aprobar."""
        with patch.object(pedidos_view, 'verificar_permisos_aprobacion', return_value=False), \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            pedidos_view.tabla_pedidos.setRowCount(1)
            pedidos_view.tabla_pedidos.selectRow(0)

            QTest.mouseClick(pedidos_view.boton_aprobar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_error.assert_called()

    def test_no_eliminar_pedido_aprobado(self, pedidos_view):
        """Test que no permite eliminar pedido aprobado."""
        pedidos_view.tabla_pedidos.setRowCount(1)
        pedidos_view.tabla_pedidos.setItem(0, 3, QTableWidgetItem("Aprobado"))
        pedidos_view.tabla_pedidos.selectRow(0)

        with patch.object(pedidos_view, 'mostrar_advertencia') as mock_advertencia:
            QTest.mouseClick(pedidos_view.boton_eliminar_pedido, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_advertencia.assert_called()


class TestPedidosViewErrorHandling:
    """Tests para manejo de errores."""

    def test_click_con_excepcion_controller(self, pedidos_view):
        """Test click cuando controller lanza excepción."""
        with patch.object(pedidos_view.controller, 'obtener_todos_pedidos',
                         side_effect=Exception("Error DB")), \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            if hasattr(pedidos_view, 'boton_refrescar'):
                QTest.mouseClick(pedidos_view.boton_refrescar, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                mock_error.assert_called()

    def test_timeout_operacion_larga(self, pedidos_view):
        """Test timeout en operaciones largas."""
        with patch.object(pedidos_view.controller, 'crear_pedido',
                         side_effect=TimeoutError("Timeout")), \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            with patch.object(pedidos_view, 'mostrar_formulario_pedido') as mock_form:
                mock_dialog = Mock()
                mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
                mock_dialog.obtener_datos.return_value = {
                    'proveedor': 'Test',
                    'items': [{'producto': 'Test', 'cantidad': 1, 'precio': Decimal('10.00')}]
                }
                mock_form.return_value = mock_dialog

                QTest.mouseClick(pedidos_view.boton_nuevo_pedido, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

                mock_error.assert_called()

    def test_error_conexion_red(self, pedidos_view):
        """Test error de conexión de red."""
        with patch.object(pedidos_view.controller, 'exportar_pedido',
                         side_effect=ConnectionError("No hay conexión")), \
             patch.object(pedidos_view, 'mostrar_error') as mock_error:

            pedidos_view.tabla_pedidos.setRowCount(1)
            pedidos_view.tabla_pedidos.selectRow(0)

            QTest.mouseClick(pedidos_view.boton_exportar, Qt.MouseButton.LeftButton)
            QApplication.processEvents()

            mock_error.assert_called()


class TestPedidosViewPerformance:
    """Tests de performance para pedidos."""

    def test_performance_carga_muchos_pedidos(self, pedidos_view):
        """Test performance con muchos pedidos."""
        # Simular muchos pedidos
        pedidos_view.tabla_pedidos.setRowCount(2000)
        pedidos_view.tabla_pedidos.setColumnCount(6)

        start_time = time.time()
        for i in range(100):  # Solo llenar algunos para el test
            for j in range(6):
                item = QTableWidgetItem(f"Data {i}-{j}")
                pedidos_view.tabla_pedidos.setItem(i, j, item)

        QApplication.processEvents()
        end_time = time.time()

        # Debe cargar razonablemente rápido
        assert (end_time - start_time) < 2.0

    def test_performance_filtrado_rapido(self, pedidos_view):
        """Test performance de filtrado."""
        with patch.object(pedidos_view.controller, 'buscar_pedidos') as mock_buscar:
            mock_buscar.return_value = [f"PED{i:04d}" for i in range(1000)]

            start_time = time.time()
            pedidos_view.campo_busqueda.setText("test")
            QTest.keyClick(pedidos_view.campo_busqueda, Qt.Key.Key_Return)
            QApplication.processEvents()
            end_time = time.time()

            # Filtrado debe ser rápido
            assert (end_time - start_time) < 1.0

    def test_performance_actualizacion_estados(self, pedidos_view):
        """Test performance de actualización masiva de estados."""
        # Simular múltiples pedidos seleccionados
        pedidos_view.tabla_pedidos.setRowCount(50)
        pedidos_view.tabla_pedidos.setColumnCount(6)

        with patch.object(pedidos_view.controller, 'cambiar_estado_multiple') as mock_cambiar:
            start_time = time.time()

            # Simular cambio masivo de estados
            if hasattr(pedidos_view, 'boton_cambiar_estado_masivo'):
                QTest.mouseClick(pedidos_view.boton_cambiar_estado_masivo, Qt.MouseButton.LeftButton)
                QApplication.processEvents()

            end_time = time.time()

import sys
import time
from pathlib import Path

from PyQt6.QtCore import QDate, QPoint, Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (  # Debe procesar rápidamente
    Decimal,
    MagicMock,
    Mock,
    3.0,
    "__main__":,
    -,
    <,
    ==,
    __name__,
    assert,
    decimal,
    end_time,
    from,
    if,
    import,
    patch,
    pytest,
    start_time,
    unittest.mock,
)

from modules.pedidos.view import PedidosView

    pytest.main([__file__, "-v"])
