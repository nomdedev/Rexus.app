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

Vista de Pedidos - Interfaz de gestión de pedidos
"""

import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QTextEdit,
    QDateEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
)

from rexus.ui.components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox
)

from rexus.ui.standard_components import StandardComponents

from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.utils.xss_protection import XSSProtection, FormProtector


class PedidosView(QWidget):
    """Vista principal del módulo de pedidos."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Tabla principal
        self.tabla_principal = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_principal)

        # Aplicar estilo
        self.aplicar_estilo()

        # Inicializar protección XSS
        self.init_xss_protection()

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, 'input_busqueda'):
                self.form_protector.protect_field(self.input_busqueda, 'busqueda')

        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def crear_panel_control(self):
        """Crea el panel de control superior."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)

        layout = QHBoxLayout(panel)

        # Botón Nuevo
        self.btn_nuevo = RexusButton("Nuevo")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Botón buscar
        self.btn_buscar = RexusButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar
        self.btn_actualizar = RexusButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

        return panel

    def configurar_tabla(self):
        """Configura la tabla principal."""
        self.tabla_principal.setColumnCount(5)
        self.tabla_principal.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Estado", "Acciones"
        ])

        # Configurar encabezados
        header = self.tabla_principal.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.tabla_principal.setAlternatingRowColors(True)
        self.tabla_principal.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def aplicar_estilo(self):
        """Aplica estilos minimalistas y modernos a toda la interfaz."""
        self.setStyleSheet("""
            /* Estilo general del widget */
            QWidget {
                background-color: #fafbfc;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }

            /* Pestañas minimalistas */
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: white;
                margin-top: 2px;
            }

            QTabBar::tab {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-bottom: none;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                color: #586069;
                min-width: 80px;
                height: 24px;
                max-height: 24px;
            }

            QTabBar::tab:selected {
                background-color: white;
                color: #24292e;
                font-weight: 500;
                border-bottom: 2px solid #0366d6;
            }

            QTabBar::tab:hover:!selected {
                background-color: #e1e4e8;
                color: #24292e;
            }

            /* Tablas compactas */
            QTableWidget {
                gridline-color: #e1e4e8;
                selection-background-color: #f1f8ff;
                selection-color: #24292e;
                alternate-background-color: #f6f8fa;
                font-size: 11px;
                border: 1px solid #e1e4e8;
                border-radius: 4px;
            }

            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }

            QHeaderView::section {
                background-color: #f6f8fa;
                color: #586069;
                font-weight: 600;
                font-size: 10px;
                border: none;
                border-right: 1px solid #e1e4e8;
                border-bottom: 1px solid #e1e4e8;
                padding: 6px 8px;
            }

            /* GroupBox minimalista */
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                color: #24292e;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #24292e;
            }

            /* Botones minimalistas */
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 20px;
            }

            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }

            QPushButton:pressed {
                background-color: #d0d7de;
            }

            /* Campos de entrada compactos */
            QLineEdit, QComboBox {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: white;
                min-height: 18px;
            }

            QLineEdit:focus, QComboBox:focus {
                border-color: #0366d6;
                outline: none;
            }

            /* Labels compactos */
            QLabel {
                color: #24292e;
                font-size: 11px;
            }

            /* Scroll bars minimalistas */
            QScrollBar:vertical {
                width: 12px;
                background-color: #f6f8fa;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #d0d7de;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #bbb;
            }
        """)

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo registro."""
        dialogo = DialogoPedido(self)

        if dialogo.exec() == QDialog.DialogCode.Accepted:
            if dialogo.validar_datos():
                datos = dialogo.obtener_datos()

                if self.controller:
                    try:
                        exito = self.controller.crear_pedido(datos)
                        if exito:
                            show_success(self, "Éxito", "Pedido creado exitosamente.")
                            self.actualizar_datos()
                        else:
                            show_error(self, "Error", "No se pudo crear el pedido.")
                    except Exception as e:
                        show_error(self, "Error", f"Error al crear pedido: {str(e)}")
                else:
                    show_warning(self, "Advertencia", "No hay controlador disponible.")

    def buscar(self):
        """Busca registros según los criterios especificados."""
        if self.controller:
            filtros = {'busqueda': self.input_busqueda.text()}
            self.controller.buscar(filtros)

    def editar_pedido(self, pedido_id):
        """Abre el diálogo para editar un pedido existente."""
        if not self.controller:
            show_warning(self, "Advertencia", "No hay controlador disponible.")
            return

        try:
            # Obtener datos del pedido
            pedido_data = self.controller.obtener_pedido_por_id(pedido_id)
            if not pedido_data:
                show_error(self, "Error", "No se pudo obtener la información del pedido.")
                return

            # Abrir diálogo de edición
            dialogo = DialogoPedido(self, pedido_data)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                if dialogo.validar_datos():
                    datos = dialogo.obtener_datos()
                    datos['id'] = pedido_id  # Agregar ID para la actualización

                    exito = self.controller.actualizar_pedido(datos)
                    if exito:
                        show_success(self, "Éxito", "Pedido actualizado exitosamente.")
                        self.actualizar_datos()
                    else:
                        show_error(self, "Error", "No se pudo actualizar el pedido.")

        except Exception as e:
            show_error(self, "Error", f"Error al editar pedido: {str(e)}")

    def eliminar_pedido(self, pedido_id):
        """Elimina un pedido después de confirmar con el usuario."""
        if not self.controller:
            show_warning(self, "Advertencia", "No hay controlador disponible.")
            return

        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # Confirmación del usuario
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                "¿Está seguro de que desea eliminar este pedido?\n\nEsta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                exito = self.controller.eliminar_pedido(pedido_id)
                if exito:
                    show_success(self, "Éxito", "Pedido eliminado exitosamente.")
                    self.actualizar_datos()
                else:
                    show_error(self, "Error", "No se pudo eliminar el pedido.")

        except Exception as e:
            show_error(self, "Error", f"Error al eliminar pedido: {str(e)}")

    def actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.controller.cargar_datos()

    def cargar_datos_en_tabla(self, datos):
        """Carga los datos en la tabla."""
        self.tabla_principal.setRowCount(len(datos))

        for row, registro in enumerate(datos):
            self.tabla_principal.setItem(row,
0,
                QTableWidgetItem(str(registro.get("id",
                ""))))
            self.tabla_principal.setItem(row,
1,
                QTableWidgetItem(str(registro.get("nombre",
                ""))))
            self.tabla_principal.setItem(row,
2,
                QTableWidgetItem(str(registro.get("descripcion",
                ""))))
            self.tabla_principal.setItem(row,
3,
                QTableWidgetItem(str(registro.get("estado",
                ""))))

            # Botón de acciones
            btn_editar = RexusButton("Editar")
            btn_editar.clicked.connect(lambda checked, pedido_id=registro.get("id"): self.editar_pedido(pedido_id))
            
            btn_eliminar = RexusButton("Eliminar")
            btn_eliminar.clicked.connect(lambda checked, pedido_id=registro.get("id"): self.eliminar_pedido(pedido_id))
            btn_eliminar.setStyleSheet("QPushButton { background-color: #dc2626; color: white; }")
            
            # Contenedor para los botones
            from PyQt6.QtWidgets import QHBoxLayout, QWidget
            botones_widget = QWidget()
            botones_layout = QHBoxLayout(botones_widget)
            botones_layout.setContentsMargins(5, 2, 5, 2)
            botones_layout.addWidget(btn_editar)
            botones_layout.addWidget(btn_eliminar)
            
            self.tabla_principal.setCellWidget(row, 4, botones_widget)

    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, 'form_protector') and self.form_protector:
            return self.form_protector.get_sanitized_data()
        else:
            # Fallback manual
            datos = {}
            if hasattr(self, 'input_busqueda'):
                datos['busqueda'] = XSSProtection.sanitize_text(self.input_busqueda.text())
            return datos


    def crear_controles_paginacion(self):
        """Crea los controles de paginación"""
        paginacion_layout = QHBoxLayout()

        # Etiqueta de información
        self.info_label = RexusLabel("Mostrando 1-50 de 0 registros")
        paginacion_layout.addWidget(self.info_label)

        paginacion_layout.addStretch()

        # Controles de navegación
        self.btn_primera = RexusButton("<<")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)

        self.btn_anterior = RexusButton("<")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)

        # Control de página actual
        self.pagina_actual_spin = QSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(RexusLabel("Página:"))
        paginacion_layout.addWidget(self.pagina_actual_spin)

        self.total_paginas_label = RexusLabel("de 1")
        paginacion_layout.addWidget(self.total_paginas_label)

        self.btn_siguiente = RexusButton(">")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)

        self.btn_ultima = RexusButton(">>")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)

        # Selector de registros por página
        paginacion_layout.addWidget(RexusLabel("Registros por página:"))
        self.registros_por_pagina_combo = RexusComboBox()
        self.registros_por_pagina_combo.addItems(["25", "50", "100", "200"])
        self.registros_por_pagina_combo.setCurrentText("50")
        self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        paginacion_layout.addWidget(self.registros_por_pagina_combo)

        return paginacion_layout

    def actualizar_controles_paginacion(self,
pagina_actual,
        total_paginas,
        total_registros,
        registros_mostrados):
        """Actualiza los controles de paginación"""
        if hasattr(self, 'info_label'):
            inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} registros")

        if hasattr(self, 'pagina_actual_spin'):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)

        if hasattr(self, 'total_paginas_label'):
            self.total_paginas_label.setText(f"de {total_paginas}")

        # Habilitar/deshabilitar botones
        if hasattr(self, 'btn_primera'):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)

    def ir_a_pagina(self, pagina):
        """Va a una página específica"""
        if hasattr(self.controller, 'cargar_pagina'):
            self.controller.cargar_pagina(pagina)

    def pagina_anterior(self):
        """Va a la página anterior"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)

    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            total_paginas = self.pagina_actual_spin.maximum()
            if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)

    def ultima_pagina(self):
        """Va a la última página"""
        if hasattr(self, 'pagina_actual_spin'):
            total_paginas = self.pagina_actual_spin.maximum()
            self.ir_a_pagina(total_paginas)

    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada"""
        self.ir_a_pagina(pagina)

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página"""
        if hasattr(self.controller, 'cambiar_registros_por_pagina'):
            self.controller.cambiar_registros_por_pagina(int(registros))

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoPedido(QDialog):
    """Diálogo para crear/editar pedidos."""

    def __init__(self, parent=None, pedido=None):
        super().__init__(parent)
        self.pedido = pedido
        self.init_ui()

        if pedido:
            self.cargar_datos(pedido)

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nuevo Pedido" if not self.pedido else "Editar Pedido")
        self.setModal(True)
        self.resize(500, 450)

        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Información del Cliente
        self.input_cliente = RexusLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente")
        form_layout.addRow("Cliente:", self.input_cliente)

        self.input_contacto = RexusLineEdit()
        self.input_contacto.setPlaceholderText("Teléfono o email")
        form_layout.addRow("Contacto:", self.input_contacto)

        # Información del Pedido
        self.combo_tipo = RexusComboBox()
        self.combo_tipo.addItems(["Obra Nueva",
"Reparación",
            "Mantenimiento",
            "Emergencia"])
        form_layout.addRow("Tipo:", self.combo_tipo)

        self.combo_prioridad = RexusComboBox()
        self.combo_prioridad.addItems(["Baja", "Normal", "Alta", "Urgente"])
        self.combo_prioridad.setCurrentText("Normal")
        form_layout.addRow("Prioridad:", self.combo_prioridad)

        self.input_fecha_entrega = QDateEdit()
        self.input_fecha_entrega.setCalendarPopup(True)
        from PyQt6.QtCore import QDate
        self.input_fecha_entrega.setDate(QDate.currentDate().addDays(7))
        form_layout.addRow("Fecha Entrega:", self.input_fecha_entrega)

        # Descripción
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción detallada del pedido")
        self.input_descripcion.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.input_descripcion)

        # Ubicación y Dirección
        self.input_direccion = QTextEdit()
        self.input_direccion.setPlaceholderText("Dirección de entrega")
        self.input_direccion.setMaximumHeight(60)
        form_layout.addRow("Dirección:", self.input_direccion)

        # Información Comercial
        self.input_presupuesto = QDoubleSpinBox()
        self.input_presupuesto.setMaximum(999999.99)
        self.input_presupuesto.setSuffix(" €")
        form_layout.addRow("Presupuesto:", self.input_presupuesto)

        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["Pendiente",
"En Proceso",
            "Listo",
            "Entregado",
            "Cancelado"])
        form_layout.addRow("Estado:", self.combo_estado)

        # Observaciones
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales")
        self.input_observaciones.setMaximumHeight(60)
        form_layout.addRow("Observaciones:", self.input_observaciones)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Aplicar estilo
        self.aplicar_estilo()

    def aplicar_estilo(self):
        """Estilos manejados por el style_manager de Rexus."""

    def cargar_datos(self, pedido):
        """Carga los datos de un pedido existente."""
        self.input_cliente.setText(pedido.get("cliente", ""))
        self.input_contacto.setText(pedido.get("contacto", ""))
        self.input_descripcion.setPlainText(pedido.get("descripcion", ""))
        self.input_direccion.setPlainText(pedido.get("direccion", ""))
        self.input_observaciones.setPlainText(pedido.get("observaciones", ""))
        self.input_presupuesto.setValue(pedido.get("presupuesto", 0.0))

        # Cargar combos
        tipo = pedido.get("tipo", "Obra Nueva")
        index = self.combo_tipo.findText(tipo)
        if index >= 0:
            self.combo_tipo.setCurrentIndex(index)

        prioridad = pedido.get("prioridad", "Normal")
        index = self.combo_prioridad.findText(prioridad)
        if index >= 0:
            self.combo_prioridad.setCurrentIndex(index)

        estado = pedido.get("estado", "Pendiente")
        index = self.combo_estado.findText(estado)
        if index >= 0:
            self.combo_estado.setCurrentIndex(index)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "cliente": self.input_cliente.text().strip(),
            "contacto": self.input_contacto.text().strip(),
            "tipo": self.combo_tipo.currentText(),
            "prioridad": self.combo_prioridad.currentText(),
            "fecha_entrega": self.input_fecha_entrega.date().toString("yyyy-MM-dd"),
            "descripcion": self.input_descripcion.toPlainText().strip(),
            "direccion": self.input_direccion.toPlainText().strip(),
            "presupuesto": self.input_presupuesto.value(),
            "estado": self.combo_estado.currentText(),
            "observaciones": self.input_observaciones.toPlainText().strip()
        }

    def validar_datos(self):
        """Valida los datos del formulario."""
        datos = self.obtener_datos()

        if not datos["cliente"]:
            show_error(self, "Error de Validación", "El nombre del cliente es obligatorio.")
            return False

        if not datos["descripcion"]:
            show_error(self, "Error de Validación", "La descripción del pedido es obligatoria.")
            return False

        if len(datos["descripcion"]) < 10:
            show_error(self, "Error de Validación", "La descripción debe tener al menos 10 caracteres.")
            return False

        if datos["presupuesto"] <= 0:
            show_error(self, "Error de Validación", "El presupuesto debe ser mayor a 0.")
            return False

        return True
