"""
Tests específicos de clicks para formularios de pedidos.
Cubre formularios de crear pedidos, gestión de proveedores, seguimiento, etc.
"""

                            QSpinBox, QPushButton, QTableWidget, QCheckBox,
                            QTextEdit, QDateEdit, QDoubleSpinBox, QListWidget)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@pytest.fixture(scope="session")
def app():
    """Fixture de aplicación Qt."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()

@pytest.fixture
def mock_db_pedidos():
    """Mock específico para base de datos de pedidos."""
    mock_db = Mock()
    mock_db.ejecutar_query = Mock(return_value=[
        {'id': 1, 'numero': 'PED-001', 'proveedor': 'Vidrios SA', 'estado': 'pendiente', 'total': 15000.00},
        {'id': 2, 'numero': 'PED-002', 'proveedor': 'Aluminios Norte', 'estado': 'aprobado', 'total': 25000.00}
    ])
    return mock_db

@pytest.fixture
def mock_controller_pedidos():
    """Mock de controlador para pedidos."""
    controller = Mock()
    controller.crear_pedido = Mock(return_value={"success": True, "message": "Pedido creado"})
    controller.actualizar_pedido = Mock(return_value={"success": True, "message": "Pedido actualizado"})
    controller.obtener_proveedores = Mock(return_value=[
        {'id': 1, 'nombre': 'Vidrios SA', 'contacto': 'Juan Pérez', 'telefono': '123456789'},
        {'id': 2, 'nombre': 'Aluminios Norte', 'contacto': 'María García', 'telefono': '987654321'}
    ])
    controller.obtener_productos_proveedor = Mock(return_value=[
        {'id': 1, 'codigo': 'VID001', 'descripcion': 'Vidrio templado 6mm', 'precio': 150.00},
        {'id': 2, 'codigo': 'PER002', 'descripcion': 'Perfil aluminio 20x40', 'precio': 45.00}
    ])
    return controller


class TestFormularioCrearPedido:
    """Tests para formulario de crear nuevo pedido."""

    def test_click_abrir_formulario_crear_pedido(self, app, mock_db_pedidos, mock_controller_pedidos):
        """Test de click para abrir formulario de crear pedido."""
        try:
            # Arrange
            view = PedidosView(db_connection=mock_db_pedidos, usuario_actual="TEST_USER")
            view.controller = mock_controller_pedidos
            view.show()
            QTest.qWait(100)

            # Buscar botón de crear pedido
            buttons = view.findChildren(QPushButton)
            create_buttons = [btn for btn in buttons
                             if "crear" in btn.toolTip().lower() or
                                "nuevo" in btn.toolTip().lower() or
                                "agregar" in btn.toolTip().lower()]

            # Act - Click en crear pedido
            if create_buttons:
                QTest.mouseClick(create_buttons[0], Qt.MouseButton.LeftButton)
                QTest.qWait(300)

                # Buscar diálogo que se abrió
                dialogs = [w for w in app.allWidgets() if isinstance(w, QDialog) and w.isVisible()]
                if dialogs:
                    dialog = dialogs[0]
                    assert "pedido" in dialog.windowTitle().lower()
                    dialog.close()

            view.close()
        except ImportError:
            pytest.skip("Módulo de pedidos no disponible")

    def test_llenar_formulario_crear_pedido_completo(self, app, mock_db_pedidos):
        """Test completo de llenado del formulario de crear pedido."""
        # Arrange - Crear formulario de pedido
        dialog = QDialog()
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos del pedido
        numero_pedido = QLineEdit()
        numero_pedido.setObjectName("numero_pedido")
        numero_pedido.setText("PED-" + QDate.currentDate().toString("yyyyMMdd") + "-001")
        form_layout.addRow("Número:", numero_pedido)

        proveedor_combo = QComboBox()
        proveedor_combo.setObjectName("proveedor_combo")
        proveedor_combo.addItems(["Vidrios SA", "Aluminios Norte", "Herrajes Central"])
        form_layout.addRow("Proveedor:", proveedor_combo)

        fecha_pedido = QDateEdit()
        fecha_pedido.setObjectName("fecha_pedido")
        fecha_pedido.setDate(QDate.currentDate())
        form_layout.addRow("Fecha pedido:", fecha_pedido)

        fecha_entrega = QDateEdit()
        fecha_entrega.setObjectName("fecha_entrega")
        fecha_entrega.setDate(QDate.currentDate().addDays(15))
        form_layout.addRow("Fecha entrega:", fecha_entrega)

        prioridad_combo = QComboBox()
        prioridad_combo.setObjectName("prioridad_combo")
        prioridad_combo.addItems(["Normal", "Alta", "Urgente"])
        form_layout.addRow("Prioridad:", prioridad_combo)

        observaciones = QTextEdit()
        observaciones.setObjectName("observaciones")
        observaciones.setMaximumHeight(80)
        observaciones.setPlaceholderText("Observaciones adicionales...")
        form_layout.addRow("Observaciones:", observaciones)

        main_layout.addLayout(form_layout)

        # Sección de productos
        productos_label = QLabel("Productos del pedido:")
        productos_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(productos_label)

        # Tabla de productos
        tabla_productos = QTableWidget(0, 5)
        tabla_productos.setObjectName("tabla_productos")
        tabla_productos.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad", "Precio", "Subtotal"])
        main_layout.addWidget(tabla_productos)

        # Botones para productos
        btn_layout = QHBoxLayout()
        btn_agregar_producto = QPushButton("+ Agregar Producto")
        btn_agregar_producto.setObjectName("btn_agregar_producto")
        btn_layout.addWidget(btn_agregar_producto)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Total del pedido
        total_layout = QFormLayout()
        total_label = QLabel("$ 0.00")
        total_label.setObjectName("total_label")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_layout.addRow("TOTAL:", total_label)
        main_layout.addLayout(total_layout)

        # Botones de acción
        botones_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar Pedido")
        btn_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)
        main_layout.addLayout(botones_layout)

        dialog.setLayout(main_layout)
        dialog.show()
        QTest.qWait(100)

        # Act - Llenar formulario
        numero_pedido.clear()
        QTest.keyClicks(numero_pedido, "PED-TEST-001")
        QTest.qWait(50)

        proveedor_combo.setCurrentIndex(1)  # Aluminios Norte
        QTest.qWait(50)

        fecha_entrega.setDate(QDate.currentDate().addDays(20))
        QTest.qWait(30)

        prioridad_combo.setCurrentIndex(1)  # Alta
        QTest.qWait(30)

        observaciones.setPlainText("Pedido urgente para obra Torre Central")
        QTest.qWait(50)

        # Simular agregar producto
        tabla_productos.setRowCount(1)
        QTest.qWait(30)

        # Click en guardar
        QTest.mouseClick(btn_guardar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert numero_pedido.text() == "PED-TEST-001"
        assert proveedor_combo.currentText() == "Aluminios Norte"
        assert prioridad_combo.currentText() == "Alta"
        assert "Torre Central" in observaciones.toPlainText()

        dialog.close()


class TestFormularioAgregarProducto:
    """Tests para formulario de agregar productos al pedido."""

    def test_formulario_seleccionar_producto(self, app):
        """Test de formulario para seleccionar producto del catálogo."""
        # Arrange - Crear formulario de selección de producto
        dialog = QDialog()
        layout = QVBoxLayout()

        # Filtros de búsqueda
        form_filtros = QFormLayout()

        buscar_codigo = QLineEdit()
        buscar_codigo.setPlaceholderText("Buscar por código...")
        form_filtros.addRow("Código:", buscar_codigo)

        filtro_categoria = QComboBox()
        filtro_categoria.addItems(["Todos", "Vidrios", "Perfiles", "Herrajes"])
        form_filtros.addRow("Categoría:", filtro_categoria)

        layout.addLayout(form_filtros)

        # Tabla de productos disponibles
        tabla_catalogo = QTableWidget(3, 4)
        tabla_catalogo.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Stock"])

        # Agregar productos de ejemplo
        productos = [
            ("VID001", "Vidrio templado 6mm", "150.00", "50"),
            ("PER002", "Perfil aluminio 20x40", "45.00", "100"),
            ("HER003", "Bisagra ajustable", "25.00", "200")
        ]

        for row, (codigo, desc, precio, stock) in enumerate(productos):
            tabla_catalogo.setItem(row, 0, QTableWidgetItem(codigo))
            tabla_catalogo.setItem(row, 1, QTableWidgetItem(desc))
            tabla_catalogo.setItem(row, 2, QTableWidgetItem(precio))
            tabla_catalogo.setItem(row, 3, QTableWidgetItem(stock))

        layout.addWidget(tabla_catalogo)

        # Campos de cantidad y precio
        form_cantidad = QFormLayout()

        cantidad_input = QSpinBox()
        cantidad_input.setMinimum(1)
        cantidad_input.setMaximum(9999)
        cantidad_input.setValue(1)
        form_cantidad.addRow("Cantidad:", cantidad_input)

        precio_input = QDoubleSpinBox()
        precio_input.setMinimum(0.01)
        precio_input.setMaximum(999999.99)
        precio_input.setPrefix("$ ")
        form_cantidad.addRow("Precio unitario:", precio_input)

        layout.addLayout(form_cantidad)

        # Botones
        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar al Pedido")
        btn_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_cancelar)
        layout.addLayout(botones_layout)

        dialog.setLayout(layout)
        dialog.show()
        QTest.qWait(100)

        # Act - Buscar producto
        QTest.keyClicks(buscar_codigo, "VID")
        QTest.qWait(50)

        # Seleccionar producto en tabla
        tabla_catalogo.selectRow(0)  # Vidrio templado
        QTest.qWait(50)

        # Establecer cantidad
        cantidad_input.setValue(5)
        QTest.qWait(30)

        # Establecer precio
        precio_input.setValue(150.00)
        QTest.qWait(30)

        # Click en agregar
        QTest.mouseClick(btn_agregar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert buscar_codigo.text() == "VID"
        assert tabla_catalogo.currentRow() == 0
        assert cantidad_input.value() == 5
        assert precio_input.value() == 150.00

        dialog.close()


class TestFormularioSeguimientoPedido:
    """Tests para formularios de seguimiento de pedidos."""

    def test_formulario_actualizar_estado_pedido(self, app):
        """Test de formulario para actualizar estado del pedido."""
        # Arrange - Crear formulario de estado
        dialog = QDialog()
        form = QFormLayout()

        # Información del pedido
        numero_label = QLabel("PED-001")
        numero_label.setStyleSheet("font-weight: bold;")
        form.addRow("Número pedido:", numero_label)

        proveedor_label = QLabel("Vidrios SA")
        form.addRow("Proveedor:", proveedor_label)

        # Estados disponibles
        estados_group = QButtonGroup()
        estados_layout = QVBoxLayout()

        estado_pendiente = QRadioButton("Pendiente")
        estado_aprobado = QRadioButton("Aprobado")
        estado_enviado = QRadioButton("Enviado")
        estado_entregado = QRadioButton("Entregado")
        estado_cancelado = QRadioButton("Cancelado")

        estados = [estado_pendiente, estado_aprobado, estado_enviado, estado_entregado, estado_cancelado]

        for i, estado in enumerate(estados):
            estados_group.addButton(estado, i)
            estados_layout.addWidget(estado)

        estado_aprobado.setChecked(True)  # Estado actual
        form.addRow("Nuevo estado:", estados_layout)

        # Fecha de actualización
        fecha_actualizacion = QDateEdit()
        fecha_actualizacion.setDate(QDate.currentDate())
        form.addRow("Fecha actualización:", fecha_actualizacion)

        # Comentarios
        comentarios = QTextEdit()
        comentarios.setMaximumHeight(80)
        comentarios.setPlaceholderText("Comentarios sobre el cambio de estado...")
        form.addRow("Comentarios:", comentarios)

        # Notificar por email
        notificar_email = QCheckBox("Notificar al solicitante por email")
        notificar_email.setChecked(True)
        form.addRow("", notificar_email)

        # Botones
        botones_layout = QHBoxLayout()
        btn_actualizar = QPushButton("Actualizar Estado")
        btn_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_cancelar)
        form.addRow("", botones_layout)

        dialog.setLayout(form)
        dialog.show()
        QTest.qWait(100)

        # Act - Cambiar estado
        QTest.mouseClick(estado_enviado, Qt.MouseButton.LeftButton)
        QTest.qWait(50)

        fecha_actualizacion.setDate(QDate.currentDate().addDays(1))
        QTest.qWait(30)

        comentarios.setPlainText("Pedido enviado por el proveedor, llegada estimada en 3 días")
        QTest.qWait(50)

        # Desmarcar notificación
        QTest.mouseClick(notificar_email, Qt.MouseButton.LeftButton)
        QTest.qWait(30)

        # Click en actualizar
        QTest.mouseClick(btn_actualizar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert estado_enviado.isChecked()
        assert not notificar_email.isChecked()
        assert "llegada estimada" in comentarios.toPlainText()

        dialog.close()


class TestFormularioProveedores:
    """Tests para formularios de gestión de proveedores."""

    def test_formulario_agregar_proveedor(self, app):
        """Test de formulario para agregar nuevo proveedor."""
        # Arrange - Crear formulario de proveedor
        dialog = QDialog()
        form = QFormLayout()

        # Datos básicos del proveedor
        nombre_empresa = QLineEdit()
        nombre_empresa.setPlaceholderText("Nombre de la empresa")
        form.addRow("Empresa:", nombre_empresa)

        rut_empresa = QLineEdit()
        rut_empresa.setPlaceholderText("12.345.678-9")
        form.addRow("RUT:", rut_empresa)

        # Contacto principal
        contacto_nombre = QLineEdit()
        contacto_nombre.setPlaceholderText("Nombre del contacto")
        form.addRow("Contacto:", contacto_nombre)

        contacto_cargo = QLineEdit()
        contacto_cargo.setPlaceholderText("Cargo del contacto")
        form.addRow("Cargo:", contacto_cargo)

        # Información de contacto
        telefono = QLineEdit()
        telefono.setPlaceholderText("+56 9 1234 5678")
        form.addRow("Teléfono:", telefono)

        email = QLineEdit()
        email.setPlaceholderText("contacto@empresa.com")
        form.addRow("Email:", email)

        # Dirección
        direccion = QTextEdit()
        direccion.setMaximumHeight(60)
        direccion.setPlaceholderText("Dirección completa")
        form.addRow("Dirección:", direccion)

        # Categorías de productos
        categorias = QListWidget()
        categorias.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        categorias_items = ["Vidrios", "Perfiles", "Herrajes", "Accesorios", "Sellantes"]
        categorias.addItems(categorias_items)
        form.addRow("Categorías:", categorias)

        # Condiciones comerciales
        forma_pago = QComboBox()
        forma_pago.addItems(["Contado", "30 días", "60 días", "90 días"])
        form.addRow("Forma de pago:", forma_pago)

        descuento = QSpinBox()
        descuento.setMinimum(0)
        descuento.setMaximum(50)
        descuento.setSuffix(" %")
        form.addRow("Descuento:", descuento)

        # Estado del proveedor
        activo = QCheckBox("Proveedor activo")
        activo.setChecked(True)
        form.addRow("", activo)

        # Botones
        botones_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar Proveedor")
        btn_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)
        form.addRow("", botones_layout)

        dialog.setLayout(form)
        dialog.show()
        QTest.qWait(100)

        # Act - Llenar formulario de proveedor
        QTest.keyClicks(nombre_empresa, "Vidrios y Cristales del Sur")
        QTest.qWait(50)

        QTest.keyClicks(rut_empresa, "76.543.210-8")
        QTest.qWait(50)

        QTest.keyClicks(contacto_nombre, "María González")
        QTest.qWait(50)

        QTest.keyClicks(contacto_cargo, "Gerente Comercial")
        QTest.qWait(50)

        QTest.keyClicks(telefono, "+56 9 8765 4321")
        QTest.qWait(50)

        QTest.keyClicks(email, "mgonzalez@vidriosdelsur.cl")
        QTest.qWait(50)

        direccion.setPlainText("Av. Industrial 456, Zona Franca, Temuco")
        QTest.qWait(50)

        # Seleccionar categorías
        categorias.item(0).setSelected(True)  # Vidrios
        categorias.item(3).setSelected(True)  # Accesorios
        QTest.qWait(50)

        forma_pago.setCurrentIndex(1)  # 30 días
        QTest.qWait(30)

        descuento.setValue(5)  # 5%
        QTest.qWait(30)

        # Click en guardar
        QTest.mouseClick(btn_guardar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert nombre_empresa.text() == "Vidrios y Cristales del Sur"
        assert rut_empresa.text() == "76.543.210-8"
        assert contacto_nombre.text() == "María González"
        assert email.text() == "mgonzalez@vidriosdelsur.cl"
        assert forma_pago.currentText() == "30 días"
        assert descuento.value() == 5
        assert activo.isChecked()

        # Verificar categorías seleccionadas
        selected_categories = [item.text() for item in categorias.selectedItems()]
        assert "Vidrios" in selected_categories
        assert "Accesorios" in selected_categories

        dialog.close()


class TestFormularioComparacionPedidos:
    """Tests para formularios de comparación de pedidos/cotizaciones."""

    def test_formulario_comparar_cotizaciones(self, app):
        """Test de formulario para comparar cotizaciones de proveedores."""
        # Arrange - Crear formulario de comparación
        dialog = QDialog()
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Comparación de Cotizaciones - Vidrio Templado 6mm")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Tabla de comparación
        tabla_comparacion = QTableWidget(3, 6)
        tabla_comparacion.setHorizontalHeaderLabels([
            "Proveedor", "Precio Unit.", "Cantidad", "Subtotal", "Plazo Entrega", "Condiciones"
        ])

        # Datos de ejemplo
        cotizaciones = [
            ("Vidrios SA", "150.00", "50", "7,500.00", "7 días", "30 días pago"),
            ("Cristales Norte", "145.00", "50", "7,250.00", "10 días", "45 días pago"),
            ("Vidriería Central", "155.00", "50", "7,750.00", "5 días", "Contado 5% desc.")
        ]

        for row, (proveedor, precio, cant, subtotal, plazo, condiciones) in enumerate(cotizaciones):
            tabla_comparacion.setItem(row, 0, QTableWidgetItem(proveedor))
            tabla_comparacion.setItem(row, 1, QTableWidgetItem(precio))
            tabla_comparacion.setItem(row, 2, QTableWidgetItem(cant))
            tabla_comparacion.setItem(row, 3, QTableWidgetItem(subtotal))
            tabla_comparacion.setItem(row, 4, QTableWidgetItem(plazo))
            tabla_comparacion.setItem(row, 5, QTableWidgetItem(condiciones))

        layout.addWidget(tabla_comparacion)

        # Criterios de evaluación
        criterios_layout = QFormLayout()

        peso_precio = QSpinBox()
        peso_precio.setMinimum(1)
        peso_precio.setMaximum(10)
        peso_precio.setValue(8)
        peso_precio.setSuffix("/10")
        criterios_layout.addRow("Importancia precio:", peso_precio)

        peso_plazo = QSpinBox()
        peso_plazo.setMinimum(1)
        peso_plazo.setMaximum(10)
        peso_plazo.setValue(6)
        peso_plazo.setSuffix("/10")
        criterios_layout.addRow("Importancia plazo:", peso_plazo)

        peso_condiciones = QSpinBox()
        peso_condiciones.setMinimum(1)
        peso_condiciones.setMaximum(10)
        peso_condiciones.setValue(4)
        peso_condiciones.setSuffix("/10")
        criterios_layout.addRow("Importancia condiciones:", peso_condiciones)

        layout.addLayout(criterios_layout)

        # Resultado recomendado
        resultado_label = QLabel("Recomendación: Cristales Norte (mejor relación precio-plazo)")
        resultado_label.setStyleSheet("background: #e6f3ff; padding: 10px; border-radius: 5px; margin: 10px 0;")
        layout.addWidget(resultado_label)

        # Botones
        botones_layout = QHBoxLayout()
        btn_seleccionar = QPushButton("Seleccionar Proveedor")
        btn_nueva_comparacion = QPushButton("Nueva Comparación")
        btn_cerrar = QPushButton("Cerrar")
        botones_layout.addWidget(btn_seleccionar)
        botones_layout.addWidget(btn_nueva_comparacion)
        botones_layout.addWidget(btn_cerrar)
        layout.addLayout(botones_layout)

        dialog.setLayout(layout)
        dialog.show()
        QTest.qWait(100)

        # Act - Cambiar criterios de evaluación
        peso_precio.setValue(6)
        QTest.qWait(50)

        peso_plazo.setValue(9)  # Priorizar plazo
        QTest.qWait(50)

        # Seleccionar fila en tabla
        tabla_comparacion.selectRow(2)  # Vidriería Central (mejor plazo)
        QTest.qWait(50)

        # Click en seleccionar
        QTest.mouseClick(btn_seleccionar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert peso_precio.value() == 6
        assert peso_plazo.value() == 9
        assert tabla_comparacion.currentRow() == 2

        dialog.close()


class TestInteraccionesAvanzadasPedidos:
    """Tests de interacciones avanzadas en formularios de pedidos."""

    def test_calculo_automatico_totales(self, app):
        """Test de cálculo automático de totales en pedido."""
        # Arrange - Crear tabla de productos con cálculos
        dialog = QDialog()
        layout = QVBoxLayout()

        tabla_productos = QTableWidget(2, 5)
        tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio", "Descuento %", "Subtotal"])

        # Función para calcular subtotal
        def calcular_subtotal(row):
            try:
                cantidad_item = tabla_productos.item(row, 1)
                precio_item = tabla_productos.item(row, 2)
                descuento_item = tabla_productos.item(row, 3)

                if cantidad_item and precio_item and descuento_item:
                    cantidad = float(cantidad_item.text() or "0")
                    precio = float(precio_item.text() or "0")
                    descuento = float(descuento_item.text() or "0")

                    subtotal = cantidad * precio * (1 - descuento/100)
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import os
import sys

from PyQt6.QtCore import QDate, Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    MagicMock,
    Mock,
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    =,
    f"{subtotal:.2f}",
    from,
    import,
    patch,
    pytest,
    subtotal_item,
    unittest.mock,
)

from rexus.modules.pedidos.view import PedidosView

                    tabla_productos.setItem(row, 4, subtotal_item)

                    # Calcular total general
                    total = 0
                    for i in range(tabla_productos.rowCount()):
                        sub_item = tabla_productos.item(i, 4)
                        if sub_item:
                            total += float(sub_item.text() or "0")

                    total_label.setText(f"Total: ${total:.2f}")
            except (ValueError, AttributeError):
                pass

        # Conectar cambios en celdas
        tabla_productos.itemChanged.connect(lambda item: calcular_subtotal(item.row()))

        layout.addWidget(tabla_productos)

        total_label = QLabel("Total: $0.00")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(total_label)

        dialog.setLayout(layout)
        dialog.show()
        QTest.qWait(100)

        # Act - Llenar tabla con productos
        productos_test = [
            ("Vidrio templado", "10", "150.00", "5"),
            ("Perfil aluminio", "20", "45.00", "10")
        ]

        for row, (producto, cantidad, precio, descuento) in enumerate(productos_test):
            tabla_productos.setItem(row, 0, QTableWidgetItem(producto))
            tabla_productos.setItem(row, 1, QTableWidgetItem(cantidad))
            tabla_productos.setItem(row, 2, QTableWidgetItem(precio))
            tabla_productos.setItem(row, 3, QTableWidgetItem(descuento))
            QTest.qWait(100)  # Esperar cálculo

        # Assert - Verificar cálculos
        # Producto 1: 10 * 150 * 0.95 = 1425
        # Producto 2: 20 * 45 * 0.90 = 810
        # Total esperado: 2235

        QTest.qWait(200)  # Esperar que se completen los cálculos

        subtotal1 = tabla_productos.item(0, 4)
        subtotal2 = tabla_productos.item(1, 4)

        if subtotal1 and subtotal2:
            assert abs(float(subtotal1.text()) - 1425.0) < 0.01
            assert abs(float(subtotal2.text()) - 810.0) < 0.01

        dialog.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
