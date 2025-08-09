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

Diálogo de Seguimiento de Entregas
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QLineEdit, QComboBox, QTextEdit, QLabel, QGroupBox, QDateEdit, 
    QTimeEdit, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QTime

from rexus.ui.components.base_components import (
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox, RexusGroupBox,
    RexusTable
)
from rexus.ui.standard_components import StandardComponents
from rexus.utils.xss_protection import XSSProtection
from rexus.utils.message_system import show_error


class DialogSeguimiento(QDialog):
    """Diálogo para seguimiento de entregas de compras."""

    def __init__(self, parent=None, orden_data=None):
        super().__init__(parent)
        self.orden_data = orden_data
        
        self.setWindowTitle("Seguimiento de Entrega")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        self.init_ui()
        
        if orden_data:
            self.cargar_datos_orden(orden_data)

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Información de la orden
        grupo_orden = self.crear_grupo_orden()
        layout.addWidget(grupo_orden)
        
        # Estado actual y nuevo estado
        grupo_estado = self.crear_grupo_estado()
        layout.addWidget(grupo_estado)
        
        # Detalles de la entrega
        grupo_entrega = self.crear_grupo_entrega()
        layout.addWidget(grupo_entrega)
        
        # Historial de seguimiento
        grupo_historial = self.crear_grupo_historial()
        layout.addWidget(grupo_historial)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def crear_grupo_orden(self):
        """Crea el grupo de información de la orden."""
        grupo = RexusGroupBox("📋 Información de la Orden")
        layout = QFormLayout(grupo)
        
        self.lbl_numero_orden = RexusLabel("N/A", "body")
        layout.addRow("Número de Orden:", self.lbl_numero_orden)
        
        self.lbl_proveedor = RexusLabel("N/A", "body")
        layout.addRow("Proveedor:", self.lbl_proveedor)
        
        self.lbl_fecha_pedido = RexusLabel("N/A", "body")
        layout.addRow("Fecha Pedido:", self.lbl_fecha_pedido)
        
        self.lbl_fecha_entrega_estimada = RexusLabel("N/A", "body")
        layout.addRow("Entrega Estimada:", self.lbl_fecha_entrega_estimada)
        
        self.lbl_total = RexusLabel("N/A", "body")
        layout.addRow("Total:", self.lbl_total)
        
        return grupo

    def crear_grupo_estado(self):
        """Crea el grupo de gestión de estado."""
        grupo = RexusGroupBox("📊 Estado de la Orden")
        layout = QFormLayout(grupo)
        
        self.lbl_estado_actual = RexusLabel("N/A", "body")
        layout.addRow("Estado Actual:", self.lbl_estado_actual)
        
        self.combo_nuevo_estado = RexusComboBox([
            "PENDIENTE",
            "CONFIRMADA", 
            "EN_PREPARACION",
            "ENVIADA",
            "EN_TRANSITO",
            "RECIBIDA",
            "CANCELADA",
            "DEVUELTA"
        ])
        layout.addRow("Nuevo Estado:", self.combo_nuevo_estado)
        
        # Motivo del cambio
        self.input_motivo = QTextEdit()
        self.input_motivo.setMaximumHeight(80)
        self.input_motivo.setPlaceholderText("Motivo del cambio de estado...")
        layout.addRow("Motivo:", self.input_motivo)
        
        return grupo

    def crear_grupo_entrega(self):
        """Crea el grupo de detalles de entrega."""
        grupo = RexusGroupBox("🚚 Detalles de Entrega")
        layout = QFormLayout(grupo)
        
        # Información de transporte
        self.input_transportista = RexusLineEdit("Nombre de la empresa...")
        layout.addRow("Transportista:", self.input_transportista)
        
        self.input_numero_guia = RexusLineEdit("Número de guía/tracking...")
        layout.addRow("Número de Guía:", self.input_numero_guia)
        
        # Fechas y horas de entrega
        fecha_layout = QHBoxLayout()
        self.date_entrega_real = QDateEdit()
        self.date_entrega_real.setDate(QDate.currentDate())
        self.date_entrega_real.setCalendarPopup(True)
        fecha_layout.addWidget(self.date_entrega_real)
        
        self.time_entrega_real = QTimeEdit()
        self.time_entrega_real.setTime(QTime.currentTime())
        fecha_layout.addWidget(self.time_entrega_real)
        
        fecha_widget = QWidget()
        fecha_widget.setLayout(fecha_layout)
        layout.addRow("Fecha/Hora Entrega:", fecha_widget)
        
        # Condiciones de entrega
        self.combo_condicion_entrega = RexusComboBox([
            "PERFECTA", "CON_OBSERVACIONES", "DAÑADA", "INCOMPLETA"
        ])
        layout.addRow("Condición:", self.combo_condicion_entrega)
        
        # Recibido por
        self.input_recibido_por = RexusLineEdit("Nombre de quien recibe...")
        layout.addRow("Recibido por:", self.input_recibido_por)
        
        # Checkbox para confirmar recepción
        self.check_confirmacion = QCheckBox("Confirmar recepción completa")
        layout.addRow("", self.check_confirmacion)
        
        # Observaciones de la entrega
        self.input_observaciones_entrega = QTextEdit()
        self.input_observaciones_entrega.setMaximumHeight(100)
        self.input_observaciones_entrega.setPlaceholderText(
            "Observaciones sobre la entrega, daños, faltantes, etc..."
        )
        layout.addRow("Observaciones:", self.input_observaciones_entrega)
        
        return grupo

    def crear_grupo_historial(self):
        """Crea el grupo de historial de seguimiento."""
        grupo = RexusGroupBox("📅 Historial de Seguimiento")
        layout = QVBoxLayout(grupo)
        
        # Tabla de historial
        self.tabla_historial = RexusTable()
        self.tabla_historial.setColumnCount(4)
        self.tabla_historial.setHorizontalHeaderLabels([
            "Fecha/Hora", "Estado", "Usuario", "Observaciones"
        ])
        
        # Configurar tabla
        header = self.tabla_historial.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Observaciones
        
        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_historial.setMaximumHeight(150)
        
        layout.addWidget(self.tabla_historial)
        
        return grupo

    def validar_y_aceptar(self):
        """Valida los datos y acepta el diálogo."""
        # Validaciones básicas
        nuevo_estado = self.combo_nuevo_estado.currentText()
        if not nuevo_estado:
            show_error(self, "Error de Validación", "Debe seleccionar un estado")
            return
        
        # Si el estado es RECIBIDA, validar datos de entrega
        if nuevo_estado == "RECIBIDA":
            if not self.input_recibido_por.text().strip():
                show_error(self, "Error de Validación", 
                          "Debe especificar quién recibe la orden")
                return
            
            if not self.check_confirmacion.isChecked():
                show_error(self, "Error de Validación", 
                          "Debe confirmar la recepción completa")
                return
        
        # Si hay número de guía, validar transportista
        if self.input_numero_guia.text().strip() and not self.input_transportista.text().strip():
            show_error(self, "Error de Validación", 
                      "Si hay número de guía debe especificar el transportista")
            return
        
        self.accept()

    def obtener_datos_seguimiento(self):
        """Obtiene los datos de seguimiento con sanitización."""
        return {
            "nuevo_estado": self.combo_nuevo_estado.currentText(),
            "motivo": XSSProtection.sanitize_text(self.input_motivo.toPlainText()),
            
            # Datos de entrega
            "transportista": XSSProtection.sanitize_text(self.input_transportista.text()),
            "numero_guia": XSSProtection.sanitize_text(self.input_numero_guia.text()),
            "fecha_entrega_real": self.date_entrega_real.date().toPython(),
            "hora_entrega_real": self.time_entrega_real.time().toPython(),
            "condicion_entrega": self.combo_condicion_entrega.currentText(),
            "recibido_por": XSSProtection.sanitize_text(self.input_recibido_por.text()),
            "confirmacion_recepcion": self.check_confirmacion.isChecked(),
            "observaciones_entrega": XSSProtection.sanitize_text(
                self.input_observaciones_entrega.toPlainText()
            ),
        }

    def cargar_datos_orden(self, datos):
        """Carga los datos de la orden en el diálogo."""
        # Información básica
        self.lbl_numero_orden.setText(str(datos.get("numero_orden", "N/A")))
        self.lbl_proveedor.setText(str(datos.get("proveedor", "N/A")))
        self.lbl_fecha_pedido.setText(str(datos.get("fecha_pedido", "N/A")))
        self.lbl_fecha_entrega_estimada.setText(str(datos.get("fecha_entrega_estimada", "N/A")))
        self.lbl_total.setText(f"${datos.get('total_final', 0):,.2f}")
        
        # Estado actual
        estado_actual = datos.get("estado", "PENDIENTE")
        self.lbl_estado_actual.setText(estado_actual)
        
        # Pre-seleccionar el próximo estado lógico
        siguiente_estado = self._obtener_siguiente_estado(estado_actual)
        if siguiente_estado:
            index = self.combo_nuevo_estado.findText(siguiente_estado)
            if index >= 0:
                self.combo_nuevo_estado.setCurrentIndex(index)

    def _obtener_siguiente_estado(self, estado_actual):
        """Obtiene el siguiente estado lógico basado en el estado actual."""
        flujo_estados = {
            "PENDIENTE": "CONFIRMADA",
            "CONFIRMADA": "EN_PREPARACION",
            "EN_PREPARACION": "ENVIADA", 
            "ENVIADA": "EN_TRANSITO",
            "EN_TRANSITO": "RECIBIDA"
        }
        return flujo_estados.get(estado_actual)

    def cargar_historial_seguimiento(self, historial):
        """Carga el historial de seguimiento en la tabla."""
        self.tabla_historial.setRowCount(len(historial))
        
        for row, evento in enumerate(historial):
            # Fecha/Hora
            fecha_hora = f"{evento.get('fecha', '')} {evento.get('hora', '')}"
            self.tabla_historial.setItem(row, 0, QTableWidgetItem(fecha_hora))
            
            # Estado
            self.tabla_historial.setItem(row, 1, QTableWidgetItem(evento.get('estado', '')))
            
            # Usuario
            self.tabla_historial.setItem(row, 2, QTableWidgetItem(evento.get('usuario', '')))
            
            # Observaciones
            self.tabla_historial.setItem(row, 3, QTableWidgetItem(evento.get('observaciones', '')))

    def actualizar_datos_entrega(self, datos_entrega):
        """Actualiza los campos de entrega con datos existentes."""
        if datos_entrega:
            self.input_transportista.setText(datos_entrega.get("transportista", ""))
            self.input_numero_guia.setText(datos_entrega.get("numero_guia", ""))
            
            if datos_entrega.get("fecha_entrega_real"):
                # Aquí convertirías la fecha desde string/datetime según el formato
                pass
            
            condicion = datos_entrega.get("condicion_entrega", "PERFECTA")
            index = self.combo_condicion_entrega.findText(condicion)
            if index >= 0:
                self.combo_condicion_entrega.setCurrentIndex(index)
            
            self.input_recibido_por.setText(datos_entrega.get("recibido_por", ""))
            self.check_confirmacion.setChecked(datos_entrega.get("confirmacion_recepcion", False))
            self.input_observaciones_entrega.setPlainText(
                datos_entrega.get("observaciones_entrega", "")
            )