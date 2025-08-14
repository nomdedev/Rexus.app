"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Diálogos mejorados para Pedidos usando utilidades nuevas - Rexus.app v2.0.0

Implementa diálogos CRUD modernos usando las utilidades dialog_utils.py
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel
from PyQt6.QtGui import QFont
from datetime import date, timedelta

from rexus.utils.dialog_utils import CrudDialogManager, create_standard_form_config, BaseFormDialog
from rexus.utils.validation_utils import FormValidationManager, AdvancedValidator


class PedidoDialogManager:
    """Gestor de diálogos para el módulo de pedidos."""

    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller
        self.crud_manager = CrudDialogManager(parent_widget, controller)
        self.validator = self._create_pedido_validator()

    def _create_pedido_validator(self) -> FormValidationManager:
        """Crea un validador específico para pedidos."""
        manager = FormValidationManager()

        # Validadores de campos
        manager.add_field_validator("numero_pedido", manager.create_required_validator("Número de pedido"))
        manager.add_field_validator("cliente", manager.create_required_validator("Cliente"))
        manager.add_field_validator("tipo_pedido", manager.create_required_validator("Tipo de pedido"))
        manager.add_field_validator("fecha_entrega_solicitada", lambda v: AdvancedValidator.validate_future_date(v, "Fecha de entrega") if v else AdvancedValidator.ValidationResult(True))
        manager.add_field_validator("direccion_entrega", manager.create_required_validator("Dirección de entrega"))
        manager.add_field_validator("telefono_contacto", lambda v: AdvancedValidator.validate_phone(v) if v else AdvancedValidator.ValidationResult(True))

        return manager

    def get_form_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del formulario de pedido."""
        return create_standard_form_config(
            title="Gestión de Pedido",
            item_name="pedido",
            groups=[
                {
                    'title': 'Información del Pedido',
                    'fields': [
                        {
                            'name': 'numero_pedido',
                            'label': 'Número de Pedido',
                            'type': 'text',
                            'required': True,
                            'default': self._generar_numero_pedido()
                        },
                        {
                            'name': 'tipo_pedido',
                            'label': 'Tipo de Pedido',
                            'type': 'combo',
                            'options': ['MATERIAL', 'HERRAMIENTA', 'SERVICIO', 'VIDRIO', 'HERRAJE', 'MIXTO'],
                            'required': True,
                            'default': 'MATERIAL'
                        },
                        {
                            'name': 'prioridad',
                            'label': 'Prioridad',
                            'type': 'combo',
                            'options': ['BAJA', 'NORMAL', 'ALTA', 'URGENTE'],
                            'required': True,
                            'default': 'NORMAL'
                        },
                        {
                            'name': 'estado',
                            'label': 'Estado',
                            'type': 'combo',
                            'options': ['BORRADOR', 'PENDIENTE', 'APROBADO', 'EN_PREPARACION', 'LISTO_ENTREGA', 'EN_TRANSITO', 'ENTREGADO', 'CANCELADO', 'FACTURADO'],
                            'required': True,
                            'default': 'BORRADOR'
                        }
                    ]
                },
                {
                    'title': 'Cliente y Obra',
                    'fields': [
                        {
                            'name': 'cliente',
                            'label': 'Cliente',
                            'type': 'text',
                            'required': True
                        },
                        {
                            'name': 'obra_codigo',
                            'label': 'Código de Obra',
                            'type': 'combo',
                            'options': ['OBR-2024-001', 'OBR-2024-002', 'OBR-2024-003'],  # Se llenará dinámicamente
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Fechas',
                    'fields': [
                        {
                            'name': 'fecha_pedido',
                            'label': 'Fecha del Pedido',
                            'type': 'date',
                            'required': True,
                            'default': date.today()
                        },
                        {
                            'name': 'fecha_entrega_solicitada',
                            'label': 'Fecha Entrega Solicitada',
                            'type': 'date',
                            'required': False,
                            'default': date.today() + timedelta(days=7)
                        }
                    ]
                },
                {
                    'title': 'Entrega',
                    'fields': [
                        {
                            'name': 'direccion_entrega',
                            'label': 'Dirección de Entrega',
                            'type': 'textarea',
                            'height': 60,
                            'required': True
                        },
                        {
                            'name': 'responsable_entrega',
                            'label': 'Responsable de Entrega',
                            'type': 'text',
                            'required': False
                        },
                        {
                            'name': 'telefono_contacto',
                            'label': 'Teléfono de Contacto',
                            'type': 'text',
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Totales',
                    'fields': [
                        {
                            'name': 'subtotal',
                            'label': 'Subtotal',
                            'type': 'float',
                            'required': False,
                            'min': 0.0,
                            'max': 999999.99,
                            'decimals': 2,
                            'default': 0.0
                        },
                        {
                            'name': 'descuento',
                            'label': 'Descuento',
                            'type': 'float',
                            'required': False,
                            'min': 0.0,
                            'max': 999999.99,
                            'decimals': 2,
                            'default': 0.0
                        },
                        {
                            'name': 'impuestos',
                            'label': 'Impuestos',
                            'type': 'float',
                            'required': False,
                            'min': 0.0,
                            'max': 999999.99,
                            'decimals': 2,
                            'default': 0.0
                        }
                    ]
                },
                {
                    'title': 'Observaciones',
                    'fields': [
                        {
                            'name': 'observaciones',
                            'label': 'Observaciones',
                            'type': 'textarea',
                            'height': 80,
                            'required': False
                        }
                    ]
                }
            ],
            size=(800, 750)
        )

    def show_create_dialog(self) -> bool:
        """Muestra el diálogo para crear un nuevo pedido."""
        config = self.get_form_config()
        config['title'] = "Crear Nuevo Pedido"

        def create_callback(data: Dict[str, Any]) -> bool:
            # Validar datos antes de crear
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False

            # Calcular total
            data['total'] = data.get('subtotal',
0) - data.get('descuento',
                0) + data.get('impuestos',
                0)

            # Crear pedido a través del controlador
            if self.controller:
                return self.controller.crear_pedido(data)
            return False

        return self.crud_manager.show_create_dialog(config, create_callback)

    def show_edit_dialog(self, pedido_data: Dict[str, Any]) -> bool:
        """Muestra el diálogo para editar un pedido existente."""
        config = self.get_form_config()
        config['title'] = f"Editar Pedido: {pedido_data.get('numero_pedido', '')}"

        # Preparar datos actuales para el formulario
        current_data = self._prepare_form_data(pedido_data)

        def update_callback(data: Dict[str, Any]) -> bool:
            # Validar datos
            is_valid, errors = self.validator.validate_form(data)
            if not is_valid:
                from rexus.utils.message_system import show_error
                show_error(self.parent, "Errores de Validación", "\n• ".join(errors))
                return False

            # Calcular total
            data['total'] = data.get('subtotal',
0) - data.get('descuento',
                0) + data.get('impuestos',
                0)

            # Actualizar pedido a través del controlador
            if self.controller:
                return self.controller.actualizar_pedido(pedido_data.get('id'), data)
            return False

        return self.crud_manager.show_edit_dialog(config, current_data, update_callback)

    def confirm_and_delete(self, pedido_data: Dict[str, Any]) -> bool:
        """Confirma y elimina un pedido."""
        numero_pedido = pedido_data.get('numero_pedido', 'Pedido')
        pedido_id = pedido_data.get('id')

        def delete_callback() -> bool:
            if self.controller:
                return self.controller.eliminar_pedido(pedido_id)
            return False

        return self.crud_manager.confirm_and_delete(numero_pedido, "pedido", delete_callback)

    def _prepare_form_data(self,
pedido_data: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Prepara los datos del pedido para el formulario."""
        form_data = {}

        # Mapear campos directos
        direct_fields = [
            'numero_pedido', 'tipo_pedido', 'prioridad', 'estado', 'cliente',
            'obra_codigo', 'direccion_entrega', 'responsable_entrega',
            'telefono_contacto', 'observaciones'
        ]

        for field in direct_fields:
            form_data[field] = pedido_data.get(field, '')

        # Campos numéricos
        form_data['subtotal'] = pedido_data.get('subtotal', 0.0)
        form_data['descuento'] = pedido_data.get('descuento', 0.0)
        form_data['impuestos'] = pedido_data.get('impuestos', 0.0)

        # Fechas
        fecha_pedido = pedido_data.get('fecha_pedido')
        if fecha_pedido:
            if isinstance(fecha_pedido, str):
                try:
                    from datetime import datetime
                    form_data['fecha_pedido'] = datetime.strptime(fecha_pedido, '%Y-%m-%d').date()
                except ValueError:
                    form_data['fecha_pedido'] = date.today()
            else:
                form_data['fecha_pedido'] = fecha_pedido
        else:
            form_data['fecha_pedido'] = date.today()

        fecha_entrega = pedido_data.get('fecha_entrega_solicitada')
        if fecha_entrega:
            if isinstance(fecha_entrega, str):
                try:
                    from datetime import datetime
                    form_data['fecha_entrega_solicitada'] = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
                except ValueError:
                    form_data['fecha_entrega_solicitada'] = date.today() + timedelta(days=7)
            else:
                form_data['fecha_entrega_solicitada'] = fecha_entrega

        return form_data

    def _generar_numero_pedido(self) -> str:
        """Genera un número de pedido automático."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        return f"PED-{timestamp}"


class PedidoDetalleDialog:
    """Diálogo especializado para gestionar el detalle de productos de un pedido."""

    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller

    def show_detalle_dialog(self, pedido_data: Dict[str, Any]) -> bool:
        """Muestra diálogo para gestionar los productos del pedido."""
        dialog = BaseFormDialog(
            self.parent,
            f"Detalle del Pedido - {pedido_data.get('numero_pedido', '')}",
            (900, 600)
        )

        # Crear layout personalizado para el detalle
        main_widget = dialog.scroll_widget
        layout = QVBoxLayout()

        # Información del pedido
        info_label = QLabel(f"Pedido: {pedido_data.get('numero_pedido', '')} - {pedido_data.get('cliente', '')}")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)

        # Tabla de productos
        productos_table = QTableWidget()
        productos_table.setColumnCount(6)
        productos_table.setHorizontalHeaderLabels([
            "Código", "Descripción", "Cantidad", "Precio Unit.", "Total", "Acciones"
        ])

        # Configurar tabla
        header = productos_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        productos_table.setMinimumHeight(300)
        layout.addWidget(productos_table)

        # Botones para gestión de productos
        botones_layout = QHBoxLayout()

        btn_agregar = QPushButton("➕ Agregar Producto")
        btn_agregar.clicked.connect(lambda: self._agregar_producto_dialog(productos_table))

        btn_quitar = QPushButton("➖ Quitar Producto")
        btn_quitar.clicked.connect(lambda: self._quitar_producto_seleccionado(productos_table))

        btn_buscar = QPushButton("[SEARCH] Buscar en Inventario")
        btn_buscar.clicked.connect(lambda: self._buscar_en_inventario_dialog(productos_table))

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_quitar)
        botones_layout.addWidget(btn_buscar)
        botones_layout.addStretch()

        layout.addLayout(botones_layout)

        # Totales
        totales_layout = QHBoxLayout()
        totales_layout.addStretch()

        self.label_subtotal = QLabel("Subtotal: $0.00")
        self.label_descuento = QLabel("Descuento: $0.00")
        self.label_impuestos = QLabel("Impuestos: $0.00")
        self.label_total = QLabel("Total: $0.00")

        self.label_total.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        totales_layout.addWidget(self.label_subtotal)
        totales_layout.addWidget(self.label_descuento)
        totales_layout.addWidget(self.label_impuestos)
        totales_layout.addWidget(self.label_total)

        layout.addLayout(totales_layout)

        main_widget.setLayout(layout)

        # Cargar productos existentes
        self._cargar_productos_existentes(productos_table, pedido_data.get('id'))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Guardar cambios en el detalle
            productos = self._obtener_productos_tabla(productos_table)

            if self.controller:
                success = self.controller.actualizar_detalle_pedido(
                    pedido_data.get('id'),
                    productos
                )

                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Detalle Actualizado",
                        f"El detalle del pedido {pedido_data.get('numero_pedido')} ha sido actualizado."
                    )
                    return True

        return False

    def _agregar_producto_dialog(self, tabla):
        """Muestra diálogo para agregar un producto manualmente."""
        # Implementar diálogo simple para agregar producto

    def _quitar_producto_seleccionado(self, tabla):
        """Quita el producto seleccionado de la tabla."""
        current_row = tabla.currentRow()
        if current_row >= 0:
            tabla.removeRow(current_row)
            self._recalcular_totales(tabla)

    def _buscar_en_inventario_dialog(self, tabla):
        """Muestra diálogo para buscar productos en el inventario."""
        # Implementar búsqueda en inventario

    def _cargar_productos_existentes(self, tabla, pedido_id):
        """Carga los productos existentes del pedido."""
        if not self.controller or not pedido_id:
            return

        productos = self.controller.obtener_detalle_pedido(pedido_id)
        tabla.setRowCount(len(productos))

        for row, producto in enumerate(productos):
            tabla.setItem(row,
0,
                QTableWidgetItem(str(producto.get('codigo_producto',
                ''))))
            tabla.setItem(row,
1,
                QTableWidgetItem(str(producto.get('descripcion',
                ''))))
            tabla.setItem(row,
2,
                QTableWidgetItem(str(producto.get('cantidad',
                ''))))
            tabla.setItem(row,
3,
                QTableWidgetItem(f"${producto.get('precio_unitario',
                0):.2f}"))
            tabla.setItem(row,
4,
                QTableWidgetItem(f"${producto.get('total_linea',
                0):.2f}"))

            # Botón de acción
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.clicked.connect(lambda checked, r=row: self._quitar_producto_seleccionado(tabla))
            tabla.setCellWidget(row, 5, btn_eliminar)

        self._recalcular_totales(tabla)

    def _recalcular_totales(self, tabla):
        """Recalcula los totales basado en los productos de la tabla."""
        subtotal = 0.0

        for row in range(tabla.rowCount()):
            total_item = tabla.item(row, 4)
            if total_item:
                try:
                    total_linea = float(total_item.text().replace('$', ''))
                    subtotal += total_linea
                except ValueError:
                    pass

        descuento = 0.0  # Podría venir de un campo editable
        impuestos = subtotal * 0.19  # IVA 19%
        total = subtotal - descuento + impuestos

        if hasattr(self, 'label_subtotal'):
            from rexus.utils.format_utils import currency_formatter
            self.label_subtotal.setText(f"Subtotal: {currency_formatter.format_amount(subtotal)}")
            self.label_descuento.setText(f"Descuento: {currency_formatter.format_amount(descuento)}")
            self.label_impuestos.setText(f"Impuestos: {currency_formatter.format_amount(impuestos)}")
            self.label_total.setText(f"Total: {currency_formatter.format_amount(total)}")

    def _obtener_productos_tabla(self, tabla) -> List[Dict[str, Any]]:
        """Obtiene la lista de productos desde la tabla."""
        productos = []

        for row in range(tabla.rowCount()):
            codigo = tabla.item(row, 0).text() if tabla.item(row, 0) else ""
            descripcion = tabla.item(row, 1).text() if tabla.item(row, 1) else ""
            cantidad = tabla.item(row, 2).text() if tabla.item(row, 2) else "0"
            precio = tabla.item(row,
3).text().replace('$',
                '') if tabla.item(row,
                3) else "0"

            try:
                cantidad_float = float(cantidad)
                precio_float = float(precio)

                producto = {
                    'codigo_producto': codigo,
                    'descripcion': descripcion,
                    'cantidad': cantidad_float,
                    'precio_unitario': precio_float,
                    'total_linea': cantidad_float * precio_float
                }
                productos.append(producto)
            except ValueError:
                continue

        return productos


class PedidoEstadoDialog:
    """Diálogo especializado para cambiar el estado de pedidos."""

    def __init__(self, parent_widget: QWidget, controller=None):
        self.parent = parent_widget
        self.controller = controller

    def show_cambiar_estado_dialog(self, pedido_data: Dict[str, Any]) -> bool:
        """Muestra diálogo para cambiar el estado del pedido."""
        estado_config = {
            'title': f'Cambiar Estado - {pedido_data.get("numero_pedido", "Pedido")}',
            'size': (400, 300),
            'groups': [
                {
                    'title': 'Estado Actual',
                    'fields': [
                        {
                            'name': 'estado_actual',
                            'label': 'Estado Actual',
                            'type': 'text',
                            'default': pedido_data.get('estado', ''),
                            'required': False
                        }
                    ]
                },
                {
                    'title': 'Nuevo Estado',
                    'fields': [
                        {
                            'name': 'nuevo_estado',
                            'label': 'Nuevo Estado',
                            'type': 'combo',
                            'options': ['BORRADOR', 'PENDIENTE', 'APROBADO', 'EN_PREPARACION', 'LISTO_ENTREGA', 'EN_TRANSITO', 'ENTREGADO', 'CANCELADO', 'FACTURADO'],
                            'required': True
                        },
                        {
                            'name': 'motivo_cambio',
                            'label': 'Motivo del Cambio',
                            'type': 'textarea',
                            'height': 60,
                            'required': False
                        }
                    ]
                }
            ]
        }

        dialog = BaseFormDialog(
            self.parent,
            estado_config['title'],
            estado_config['size']
        )

        # Agregar campos
        for group in estado_config['groups']:
            dialog.add_form_group(group['title'], group['fields'])

        # Deshabilitar el campo de estado actual
        if 'estado_actual' in dialog.form_fields:
            dialog.form_fields['estado_actual']['widget'].setEnabled(False)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            estado_data = dialog.get_form_data()

            # Cambiar estado a través del controlador
            if self.controller:
                success = self.controller.cambiar_estado_pedido(
                    pedido_data.get('id'),
                    estado_data.get('nuevo_estado'),
                    estado_data.get('motivo_cambio', '')
                )

                if success:
                    from rexus.utils.message_system import show_success
                    show_success(
                        self.parent,
                        "Estado Cambiado",
                        f"El estado del pedido {pedido_data.get('numero_pedido')} ha sido cambiado a {estado_data.get('nuevo_estado')}."
                    )
                    return True
                else:
                    from rexus.utils.message_system import show_error
                    show_error(
                        self.parent,
                        "Error al Cambiar Estado",
                        "No se pudo cambiar el estado del pedido."
                    )

        return False"