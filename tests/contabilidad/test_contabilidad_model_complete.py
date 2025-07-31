"""
Tests exhaustivos para ContabilidadModel - COBERTURA COMPLETA
Cubre todas las funcionalidades críticas del modelo de contabilidad.
"""

# Configurar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture
def mock_db_connection():
    """Fixture para mock de conexión a base de datos."""
    mock_db = Mock()
    mock_db.ejecutar_query = Mock()
    return mock_db


@pytest.fixture
def contabilidad_model(mock_db_connection):
    """Fixture para ContabilidadModel con DB mockeada."""
    return ContabilidadModel(mock_db_connection)


@pytest.fixture
def datos_recibo_sample():
    """Fixture con datos de recibo de prueba."""
    return {
        'fecha_emision': '2025-01-15',
        'obra_id': 1,
        'monto_total': 15000.50,
        'concepto': 'Pago por vidrios instalados',
        'destinatario': 'Empresa Constructora ABC',
        'usuario_emisor': 1,
        'estado': 'emitido',
        'archivo_pdf': ''
    }


@pytest.fixture
def datos_movimiento_sample():
    """Fixture con datos de movimiento contable de prueba."""
    return {
        'fecha': '2025-01-15',
        'tipo_movimiento': 'ingreso',
        'monto': 15000.50,
        'concepto': 'Pago recibido por instalación',
        'referencia_recibo': 'REC-001',
        'observaciones': 'Pago completo obra 123'
    }


class TestContabilidadModelInicializacion:
    """Tests para inicialización del modelo."""

    def test_init_con_db_connection(self, mock_db_connection):
        """Test inicialización correcta con conexión DB."""
        model = ContabilidadModel(mock_db_connection)

        assert model.db == mock_db_connection
        assert hasattr(model, 'db')

    def test_init_sin_db_connection(self):
        """Test inicialización sin conexión DB."""
        model = ContabilidadModel(None)

        assert model.db is None


class TestContabilidadModelReportes:
    """Tests para funcionalidades de reportes."""

    def test_obtener_reportes_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener reportes exitosamente."""
        # Arrange
        reportes_mock = [
            (1, 'Reporte Mensual', '2025-01-15', 25000.00),
            (2, 'Balance Trimestral', '2025-01-10', 75000.00)
        ]
        mock_db_connection.ejecutar_query.return_value = reportes_mock

        # Act
        resultado = contabilidad_model.obtener_reportes()

        # Assert
        assert resultado == reportes_mock
        mock_db_connection.ejecutar_query.assert_called_once_with("SELECT * FROM reportes")

    def test_obtener_reportes_vacio(self, contabilidad_model, mock_db_connection):
        """Test obtener reportes cuando no hay datos."""
        # Arrange
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.obtener_reportes()

        # Assert
        assert resultado == []
        mock_db_connection.ejecutar_query.assert_called_once()

    def test_agregar_reporte_exito(self, contabilidad_model, mock_db_connection):
        """Test agregar reporte exitosamente."""
        # Arrange
        datos_reporte = ('Reporte Test', '2025-01-15', 50000.00)

        # Act
        contabilidad_model.agregar_reporte(datos_reporte)

        # Assert
        expected_query = "INSERT INTO reportes (titulo, fecha, total) VALUES (?, ?, ?)"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, datos_reporte)

    def test_agregar_reporte_error_db(self, contabilidad_model, mock_db_connection):
        """Test agregar reporte con error de DB."""
        # Arrange
        mock_db_connection.ejecutar_query.side_effect = Exception("Error de conexión")
        datos_reporte = ('Reporte Test', '2025-01-15', 50000.00)

        # Act & Assert
        with pytest.raises(Exception, match="Error de conexión"):
            contabilidad_model.agregar_reporte(datos_reporte)


class TestContabilidadModelRecibos:
    """Tests para funcionalidades de recibos."""

    def test_obtener_recibos_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener recibos exitosamente."""
        # Arrange
        recibos_mock = [
            (1, '2025-01-15', 1, 15000.50, 'Pago vidrios', 'Empresa ABC', 'hash123', 1, 'emitido', ''),
            (2, '2025-01-14', 2, 8500.00, 'Pago herrajes', 'Empresa XYZ', 'hash456', 1, 'emitido', '')
        ]
        mock_db_connection.ejecutar_query.return_value = recibos_mock

        # Act
        resultado = contabilidad_model.obtener_recibos()

        # Assert
        assert resultado == recibos_mock
        mock_db_connection.ejecutar_query.assert_called_once_with("SELECT * FROM recibos")

    def test_agregar_recibo_exito(self, contabilidad_model, mock_db_connection, datos_recibo_sample):
        """Test agregar recibo exitosamente."""
        # Arrange
        datos = (
            datos_recibo_sample['fecha_emision'],
            datos_recibo_sample['obra_id'],
            datos_recibo_sample['monto_total'],
            datos_recibo_sample['concepto'],
            datos_recibo_sample['destinatario'],
            'firma_hash',
            datos_recibo_sample['usuario_emisor'],
            datos_recibo_sample['estado'],
            datos_recibo_sample['archivo_pdf']
        )

        # Act
        contabilidad_model.agregar_recibo(datos)

        # Assert
        expected_query = """
        INSERT INTO recibos (fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital, usuario_emisor, estado, archivo_pdf)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, datos)

    def test_anular_recibo_exito(self, contabilidad_model, mock_db_connection):
        """Test anular recibo exitosamente."""
        # Arrange
        id_recibo = 123

        # Act
        contabilidad_model.anular_recibo(id_recibo)

        # Assert
        expected_query = "UPDATE recibos SET estado = 'anulado' WHERE id = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (id_recibo,))

    def test_generar_recibo_exito(self, contabilidad_model, mock_db_connection):
        """Test generar recibo exitosamente."""
        # Arrange
        obra_id, monto_total, concepto, destinatario = 1, 15000.50, 'Pago test', 'Cliente Test'

        # Act
        contabilidad_model.generar_recibo(obra_id, monto_total, concepto, destinatario)

        # Assert
        expected_query = "INSERT INTO recibos (obra_id, monto_total, concepto, destinatario) VALUES (?, ?, ?, ?)"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (obra_id, monto_total, concepto, destinatario))


class TestContabilidadModelMovimientosContables:
    """Tests para movimientos contables."""

    def test_obtener_movimientos_contables_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener movimientos contables exitosamente."""
        # Arrange
        movimientos_mock = [
            (1, '2025-01-15', 'ingreso', 15000.50, 'Pago cliente', 'REC-001', 'Pago completo'),
            (2, '2025-01-14', 'egreso', -2500.00, 'Compra materiales', '', 'Gastos obra')
        ]
        mock_db_connection.ejecutar_query.return_value = movimientos_mock

        # Act
        resultado = contabilidad_model.obtener_movimientos_contables()

        # Assert
        assert resultado == movimientos_mock
        mock_db_connection.ejecutar_query.assert_called_once_with("SELECT * FROM movimientos_contables")

    def test_agregar_movimiento_contable_exito(self, contabilidad_model, mock_db_connection, datos_movimiento_sample):
        """Test agregar movimiento contable exitosamente."""
        # Arrange
        datos = (
            datos_movimiento_sample['fecha'],
            datos_movimiento_sample['tipo_movimiento'],
            datos_movimiento_sample['monto'],
            datos_movimiento_sample['concepto'],
            datos_movimiento_sample['referencia_recibo'],
            datos_movimiento_sample['observaciones']
        )

        # Act
        contabilidad_model.agregar_movimiento_contable(datos)

        # Assert
        expected_query = """
        INSERT INTO movimientos_contables (fecha, tipo_movimiento, monto, concepto, referencia_recibo, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, datos)

    def test_obtener_balance_por_fechas(self, contabilidad_model, mock_db_connection):
        """Test obtener balance por rango de fechas."""
        # Arrange
        fecha_inicio = '2025-01-01'
        fecha_fin = '2025-01-31'
        balance_mock = [
            (1, '2025-01-15', 'ingreso', 15000.50, 'Pago cliente', 'REC-001', ''),
            (2, '2025-01-20', 'egreso', -3000.00, 'Compra materiales', '', '')
        ]
        mock_db_connection.ejecutar_query.return_value = balance_mock

        # Act
        resultado = contabilidad_model.obtener_balance(fecha_inicio, fecha_fin)

        # Assert
        assert resultado == balance_mock
        expected_query = "SELECT * FROM movimientos_contables WHERE fecha BETWEEN ? AND ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (fecha_inicio, fecha_fin))


class TestContabilidadModelExportacion:
    """Tests para funcionalidades de exportación."""

    @patch('pandas.Timestamp.now')
    @patch('pandas.DataFrame.to_excel')
    def test_exportar_balance_excel_exito(self, mock_to_excel, mock_timestamp, contabilidad_model):
        """Test exportar balance a Excel exitosamente."""
        # Arrange
        mock_timestamp.return_value.strftime.return_value = "20250115_143000"
        datos_balance = [
            ['2025-01-15', 'ingreso', 15000.50, 'Pago cliente', 'REC-001', ''],
            ['2025-01-14', 'egreso', -2500.00, 'Compra materiales', '', 'Gastos']
        ]

        # Act
        resultado = contabilidad_model.exportar_balance('excel', datos_balance)

        # Assert
        assert "balance_contable_20250115_143000.xlsx" in resultado
        assert "Balance exportado a Excel" in resultado
        mock_to_excel.assert_called_once_with('balance_contable_20250115_143000.xlsx', index=False)

    @patch('pandas.Timestamp.now')
    @patch('fpdf.FPDF.output')
    @patch('fpdf.FPDF.add_page')
    @patch('fpdf.FPDF.set_font')
    @patch('fpdf.FPDF.cell')
    def test_exportar_balance_pdf_exito(self, mock_cell, mock_set_font, mock_add_page, mock_output, mock_timestamp, contabilidad_model):
        """Test exportar balance a PDF exitosamente."""
        # Arrange
        mock_timestamp.return_value.strftime.return_value = "20250115_143000"
        datos_balance = [
            ['2025-01-15', 'ingreso', 15000.50, 'Pago cliente', 'REC-001', ''],
            ['2025-01-14', 'egreso', -2500.00, 'Compra materiales', '', 'Gastos']
        ]

        # Act
        resultado = contabilidad_model.exportar_balance('pdf', datos_balance)

        # Assert
        assert "balance_contable_20250115_143000.pdf" in resultado
        assert "Balance exportado a PDF" in resultado
        mock_add_page.assert_called_once()
        mock_output.assert_called_once_with('balance_contable_20250115_143000.pdf')

    def test_exportar_balance_sin_datos(self, contabilidad_model):
        """Test exportar balance sin datos."""
        # Act
        resultado = contabilidad_model.exportar_balance('excel', [])

        # Assert
        assert resultado == "No hay datos de balance para exportar."

    def test_exportar_balance_formato_invalido(self, contabilidad_model):
        """Test exportar balance con formato inválido."""
        # Arrange
        datos_balance = [['2025-01-15', 'ingreso', 15000.50, 'Test', '', '']]

        # Act
        resultado = contabilidad_model.exportar_balance('xml', datos_balance)

        # Assert
        assert resultado == "Formato no soportado. Use 'excel' o 'pdf'."

    @patch('pandas.DataFrame.to_excel')
    def test_exportar_balance_excel_error(self, mock_to_excel, contabilidad_model):
        """Test exportar balance a Excel con error."""
        # Arrange
        mock_to_excel.side_effect = Exception("Error de escritura")
        datos_balance = [['2025-01-15', 'ingreso', 15000.50, 'Test', '', '']]

        # Act
        resultado = contabilidad_model.exportar_balance('excel', datos_balance)

        # Assert
        assert "Error al exportar a Excel: Error de escritura" in resultado
        mock_to_excel.assert_called_once()
        assert "Error al exportar a Excel: Error de escritura" in resultado


class TestContabilidadModelPDFRecibos:
    """Tests para generación de PDFs de recibos."""

    @patch('fpdf.FPDF.output')
    @patch('fpdf.FPDF.add_page')
    @patch('fpdf.FPDF.set_font')
    @patch('fpdf.FPDF.cell')
    def test_generar_recibo_pdf_exito(self, mock_cell, mock_set_font, mock_add_page, mock_output, contabilidad_model, mock_db_connection):
        """Test generar PDF de recibo exitosamente."""
        # Arrange
        id_recibo = 123
        datos_recibo = [('2025-01-15', 1, 15000.50, 'Pago vidrios', 'Cliente ABC', 'hash123')]
        mock_db_connection.ejecutar_query.return_value = datos_recibo

        # Act
        resultado = contabilidad_model.generar_recibo_pdf(id_recibo)

        # Assert
        assert f"Recibo exportado como recibo_{id_recibo}.pdf." == resultado
        mock_add_page.assert_called_once()
        mock_output.assert_called_once_with(f"recibo_{id_recibo}.pdf")

    def test_generar_recibo_pdf_no_encontrado(self, contabilidad_model, mock_db_connection):
        """Test generar PDF de recibo no encontrado."""
        # Arrange
        id_recibo = 999
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.generar_recibo_pdf(id_recibo)

        # Assert
        assert resultado == "Recibo no encontrado."


class TestContabilidadModelFirmaDigital:
    """Tests para funcionalidades de firma digital."""

    def test_generar_firma_digital_exito(self, contabilidad_model):
        """Test generar firma digital exitosamente."""
        # Arrange
        datos_recibo = ['2025-01-15', 1, 15000.50, 'Pago test', 'Cliente Test']
        datos_concatenados = "|".join(map(str, datos_recibo))
        firma_esperada = hashlib.sha256(datos_concatenados.encode()).hexdigest()

        # Act
        resultado = contabilidad_model.generar_firma_digital(datos_recibo)

        # Assert
        assert resultado == firma_esperada
        assert isinstance(resultado, str)
        assert len(resultado) == 64  # SHA256 produces 64 character hex string

    def test_generar_firma_digital_datos_vacios(self, contabilidad_model):
        """Test generar firma digital con datos vacíos."""
        # Arrange
        datos_recibo = []

        # Act
        resultado = contabilidad_model.generar_firma_digital(datos_recibo)

        # Assert
        assert isinstance(resultado, str)
        assert len(resultado) == 64

    def test_verificar_firma_digital_valida(self, contabilidad_model, mock_db_connection):
        """Test verificar firma digital válida."""
        # Arrange
        id_recibo = 123
        datos_recibo = ['2025-01-15', 1, 15000.50, 'Pago test', 'Cliente Test']
        firma_correcta = hashlib.sha256("|".join(map(str, datos_recibo)).encode()).hexdigest()
        datos_db = datos_recibo + [firma_correcta]
        mock_db_connection.ejecutar_query.return_value = [datos_db]

        # Act
        resultado = contabilidad_model.verificar_firma_digital(id_recibo)

        # Assert
        assert resultado is True

    def test_verificar_firma_digital_invalida(self, contabilidad_model, mock_db_connection):
        """Test verificar firma digital inválida."""
        # Arrange
        id_recibo = 123
        datos_recibo = ['2025-01-15', 1, 15000.50, 'Pago test', 'Cliente Test']
        firma_incorrecta = "firma_incorrecta"
        datos_db = datos_recibo + [firma_incorrecta]
        mock_db_connection.ejecutar_query.return_value = [datos_db]

        # Act
        resultado = contabilidad_model.verificar_firma_digital(id_recibo)

        # Assert
        assert resultado is False

    def test_verificar_firma_digital_recibo_no_encontrado(self, contabilidad_model, mock_db_connection):
        """Test verificar firma digital de recibo no encontrado."""
        # Arrange
        id_recibo = 999
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.verificar_firma_digital(id_recibo)

        # Assert
        assert resultado == "Recibo no encontrado."


class TestContabilidadModelPagosPedidos:
    """Tests para funcionalidades de pagos por pedidos."""

    def test_registrar_pago_pedido_exito(self, contabilidad_model, mock_db_connection):
        """Test registrar pago por pedido exitosamente."""
        # Arrange
        datos_pago = (123, 'inventario', 1, 15000.50, '2025-01-15', 1, 'pagado', 'COMP-001', 'Pago completo')

        # Act
        contabilidad_model.registrar_pago_pedido(*datos_pago)

        # Assert
        expected_query = '''
        INSERT INTO pagos_pedidos (tipo_pedido, modulo, obra_id, monto_total, fecha_pago, usuario_id, estado, numero_comprobante, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, datos_pago)

    def test_actualizar_estado_pago_exito(self, contabilidad_model, mock_db_connection):
        """Test actualizar estado de pago exitosamente."""
        # Arrange
        id_pago = 456
        nuevo_estado = 'cancelado'

        # Act
        contabilidad_model.actualizar_estado_pago(id_pago, nuevo_estado)

        # Assert
        expected_query = "UPDATE pagos_pedidos SET estado = ? WHERE id = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (nuevo_estado, id_pago))

    def test_obtener_pagos_por_pedido_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener pagos por pedido exitosamente."""
        # Arrange
        id_pedido = 123
        modulo = 'inventario'
        pagos_mock = [(1, 123, 'inventario', 1, 15000.50, '2025-01-15', 1, 'pagado', 'COMP-001', '')]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_pagos_por_pedido(id_pedido, modulo)

        # Assert
        assert resultado == pagos_mock
        expected_query = "SELECT * FROM pagos_pedidos WHERE tipo_pedido = ? AND modulo = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (id_pedido, modulo))

    def test_obtener_pagos_por_obra_con_modulo(self, contabilidad_model, mock_db_connection):
        """Test obtener pagos por obra con módulo específico."""
        # Arrange
        obra_id = 1
        modulo = 'vidrios'
        pagos_mock = [(1, 123, 'vidrios', 1, 8500.00, '2025-01-15', 1, 'pagado', 'COMP-002', '')]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_pagos_por_obra(obra_id, modulo)

        # Assert
        assert resultado == pagos_mock
        expected_query = "SELECT * FROM pagos_pedidos WHERE obra_id = ? AND modulo = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (obra_id, modulo))

    def test_obtener_pagos_por_obra_sin_modulo(self, contabilidad_model, mock_db_connection):
        """Test obtener pagos por obra sin módulo específico."""
        # Arrange
        obra_id = 1
        pagos_mock = [
            (1, 123, 'inventario', 1, 15000.50, '2025-01-15', 1, 'pagado', 'COMP-001', ''),
            (2, 124, 'vidrios', 1, 8500.00, '2025-01-16', 1, 'pagado', 'COMP-002', '')
        ]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_pagos_por_obra(obra_id)

        # Assert
        assert resultado == pagos_mock
        expected_query = "SELECT * FROM pagos_pedidos WHERE obra_id = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (obra_id,))

    def test_obtener_estado_pago_pedido_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener estado de pago por pedido exitosamente."""
        # Arrange
        id_pedido = 123
        modulo = 'herrajes'
        mock_db_connection.ejecutar_query.return_value = [('pagado',)]

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido(id_pedido, modulo)

        # Assert
        assert resultado == 'pagado'

    def test_obtener_estado_pago_pedido_no_encontrado(self, contabilidad_model, mock_db_connection):
        """Test obtener estado de pago cuando no existe."""
        # Arrange
        id_pedido = 999
        modulo = 'inventario'
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido(id_pedido, modulo)

        # Assert
        assert resultado is None

    def test_obtener_pagos_por_usuario_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener pagos por usuario exitosamente."""
        # Arrange
        usuario = 1
        pagos_mock = [
            (1, 123, 'inventario', 1, 15000.50, '2025-01-15', 1, 'pagado', 'COMP-001', ''),
            (2, 124, 'vidrios', 2, 8500.00, '2025-01-16', 1, 'pendiente', '', '')
        ]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_pagos_por_usuario(usuario)

        # Assert
        assert resultado == pagos_mock
        expected_query = "SELECT * FROM pagos_pedidos WHERE usuario = ?"
        mock_db_connection.ejecutar_query.assert_called_once_with(expected_query, (usuario,))

    def test_obtener_estado_pago_pedido_por_obra_exito(self, contabilidad_model, mock_db_connection):
        """Test obtener estado de pago por obra exitosamente."""
        # Arrange
        obra_id = 1
        modulo = 'inventario'
        pagos_mock = [(1, 123, 'inventario', 1, 15000.50, '2025-01-15', 'pagado', 'COMP-001', '')]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido_por_obra(obra_id, modulo)

        # Assert
        assert resultado == 'pagado'

    def test_obtener_estado_pago_pedido_por_obra_sin_pagos(self, contabilidad_model, mock_db_connection):
        """Test obtener estado de pago por obra sin pagos."""
        # Arrange
        obra_id = 999
        modulo = 'inventario'
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido_por_obra(obra_id, modulo)

        # Assert
        assert resultado == 'pendiente'

    def test_obtener_estado_pago_pedido_por_obra_error(self, contabilidad_model, mock_db_connection):
        """Test obtener estado de pago por obra con error."""
        # Arrange
        obra_id = 1
        modulo = 'inventario'
        mock_db_connection.ejecutar_query.side_effect = Exception("Error de conexión")

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido_por_obra(obra_id, modulo)

        # Assert
        assert resultado == 'error'


class TestContabilidadModelEdgeCases:
    """Tests para edge cases y casos extremos."""

    def test_exportar_balance_datos_none(self, contabilidad_model):
        """Test exportar balance con datos None."""
        # Act
        resultado = contabilidad_model.exportar_balance('excel', None)

        # Assert
        assert resultado == "No hay datos de balance para exportar."

    def test_generar_firma_digital_con_unicode(self, contabilidad_model):
        """Test generar firma digital con caracteres Unicode."""
        # Arrange
        datos_recibo = ['2025-01-15', 1, 15000.50, 'Pago ñoño & Asociados 💰', 'Cliente Tëst']

        # Act
        resultado = contabilidad_model.generar_firma_digital(datos_recibo)

        # Assert
        assert isinstance(resultado, str)
        assert len(resultado) == 64

    def test_agregar_recibo_datos_invalidos(self, contabilidad_model, mock_db_connection):
        """Test agregar recibo con datos inválidos."""
        # Arrange
        datos_invalidos = (None, '', -1000, '', '', '', '', '', '')
        mock_db_connection.ejecutar_query.side_effect = Exception("Constraint violation")

        # Act & Assert
        with pytest.raises(Exception, match="Constraint violation"):
            contabilidad_model.agregar_recibo(datos_invalidos)

    def test_registrar_pago_pedido_montos_extremos(self, contabilidad_model, mock_db_connection):
        """Test registrar pago con montos extremos."""
        # Arrange
        monto_extremo = 999999999999.99
        datos_pago = (123, 'inventario', 1, monto_extremo, '2025-01-15', 1, 'pagado', 'COMP-001', '')

        # Act
        contabilidad_model.registrar_pago_pedido(*datos_pago)

        # Assert
        mock_db_connection.ejecutar_query.assert_called_once()

    def test_obtener_balance_fechas_invalidas(self, contabilidad_model, mock_db_connection):
        """Test obtener balance con fechas inválidas."""
        # Arrange
        fecha_inicio = '2025-12-31'  # Fecha mayor que fecha fin
        fecha_fin = '2025-01-01'
        mock_db_connection.ejecutar_query.return_value = []

        # Act
        resultado = contabilidad_model.obtener_balance(fecha_inicio, fecha_fin)

        # Assert
        assert resultado == []

    def test_db_connection_none_error_handling(self):
        """Test manejo de errores cuando db_connection es None."""
        # Arrange
        model = ContabilidadModel(None)

        # Act & Assert
        with pytest.raises(AttributeError):
            model.obtener_reportes()


class TestContabilidadModelIntegracion:
    """Tests de integración con otros módulos."""

    def test_integracion_obras_pagos(self, contabilidad_model, mock_db_connection):
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import hashlib
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from rexus.modules.contabilidad.model import ContabilidadModel

        """Test integración con módulo de obras para pagos."""
        # Arrange
        obra_id = 1
        modulo = 'inventario'
        pagos_mock = [(1, 123, 'inventario', 1, 15000.50, '2025-01-15', 'pagado', 'COMP-001', '')]
        mock_db_connection.ejecutar_query.return_value = pagos_mock

        # Act
        resultado = contabilidad_model.obtener_estado_pago_pedido_por_obra(obra_id, modulo)

        # Assert
        assert resultado == 'pagado'

    def test_integracion_auditoria_estructura_datos(self, contabilidad_model, mock_db_connection):
        """Test que la estructura de datos es compatible con auditoría."""
        # Arrange
        datos_pago = (123, 'inventario', 1, 15000.50, '2025-01-15', 1, 'pagado', 'COMP-001', 'Test auditoría')

        # Act
        contabilidad_model.registrar_pago_pedido(*datos_pago)

        # Assert
        # Verificar que se llamó con datos estructurados para auditoría
        call_args = mock_db_connection.ejecutar_query.call_args[0]
        assert len(call_args) == 2  # Query y datos
        assert len(call_args[1]) == 9  # 9 campos para registro completo

    def test_verificacion_integridad_datos_firma(self, contabilidad_model):
        """Test verificación de integridad de datos para firma digital."""
        # Arrange
        datos_originales = ['2025-01-15', 1, 15000.50, 'Concepto original', 'Cliente Test']
        datos_modificados = ['2025-01-15', 1, 15000.50, 'Concepto modificado', 'Cliente Test']

        # Act
        firma_original = contabilidad_model.generar_firma_digital(datos_originales)
        firma_modificada = contabilidad_model.generar_firma_digital(datos_modificados)

        # Assert
        assert firma_original != firma_modificada  # Las firmas deben ser diferentes


class TestContabilidadModelPerformance:
    """Tests de rendimiento y límites."""

    @patch('pandas.DataFrame.to_excel')
    def test_exportar_balance_datos_masivos(self, mock_to_excel, contabilidad_model):
        """Test exportar balance con datos masivos."""
        # Arrange
        datos_masivos = []
        for i in range(10000):
            datos_masivos.append([
                f'2025-01-{(i % 28) + 1:02d}',
                'ingreso' if i % 2 == 0 else 'egreso',
                (i * 100.50),
                f'Concepto {i}',
                f'REF-{i:05d}',
                f'Observación {i}'
            ])

        # Act
        resultado = contabilidad_model.exportar_balance('excel', datos_masivos)

        # Assert
        assert "Balance exportado a Excel" in resultado
        mock_to_excel.assert_called_once()

    def test_generar_firmas_multiples_performance(self, contabilidad_model):
        """Test generar múltiples firmas digitales."""
        # Arrange
        datos_base = ['2025-01-15', 1, 15000.50, 'Concepto base', 'Cliente Test']

        # Act
        firmas = []
        for i in range(1000):
            datos_modificados = datos_base.copy()
            datos_modificados[3] = f'Concepto {i}'
            firma = contabilidad_model.generar_firma_digital(datos_modificados)
            firmas.append(firma)

        # Assert
        assert len(firmas) == 1000
        assert len(set(firmas)) == 1000  # Todas las firmas deben ser únicas


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
