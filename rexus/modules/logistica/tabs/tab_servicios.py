"""
Pestaña de Servicios para el módulo de Logística

Maneja la interfaz y lógica específica de la generación de servicios.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QDate, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout

from .base_tab import BaseTab
from ..constants import TIPOS_SERVICIO, ICONS, UI_CONFIG
from ..widgets import (
    LogisticaButton, LogisticaTable, LogisticaGroupBox, 
    FormBuilder
)


class TabServicios(BaseTab):
    """Pestaña para generación de servicios."""
    
    # Señales específicas de servicios
    servicio_generado = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        self.servicios_data = []
        super().__init__("Servicios", ICONS["tabs"]["servicios"], parent)
    
    def init_ui(self):
        """Inicializa la interfaz de la pestaña de servicios."""
        # Panel de creación de servicios
        self.create_service_form()
        
        # Tabla de servicios generados
        self.create_services_table()
    
    def create_service_form(self):
        """Crea el formulario para generar servicios."""
        crear_group = LogisticaGroupBox("📋 Generar Nuevo Servicio", self)
        
        # Configuración de campos del formulario
        fields_config = {
            "combo_tipo_servicio": {
                "type": "combo_box",
                "label": "Tipo de Servicio",
                "options": TIPOS_SERVICIO,
                "width": UI_CONFIG["widget_widths"]["combo_tipo_servicio"]
            },
            "input_cliente": {
                "type": "line_edit",
                "label": "Cliente/Destino",
                "placeholder": "Nombre del cliente o destino",
                "width": UI_CONFIG["widget_widths"]["input_cliente"]
            },
            "input_direccion": {
                "type": "line_edit",
                "label": "Dirección",
                "placeholder": "Dirección completa de entrega",
                "width": UI_CONFIG["widget_widths"]["input_direccion"]
            },
            "date_programada": {
                "type": "date_edit",
                "label": "Fecha Programada",
                "width": UI_CONFIG["widget_widths"]["date_programada"]
            },
            "input_hora": {
                "type": "line_edit",
                "label": "Hora",
                "placeholder": "HH:MM",
                "width": UI_CONFIG["widget_widths"]["input_hora"]
            },
            "input_contacto": {
                "type": "line_edit",
                "label": "Contacto",
                "placeholder": "Teléfono de contacto",
                "width": UI_CONFIG["widget_widths"]["input_contacto"]
            },
            "text_observaciones": {
                "type": "text_edit",
                "label": "Observaciones",
                "placeholder": "Observaciones adicionales del servicio",
                "height": UI_CONFIG["heights"]["text_observaciones"]
            }
        }
        
        # Crear formulario usando FormBuilder
        form_layout, self.form_widgets = FormBuilder.create_form_layout(fields_config)
        crear_group.add_layout(form_layout)
        
        # Panel de botones
        self.create_form_buttons(crear_group)
        
        self.main_layout.addWidget(crear_group)
    
    def create_form_buttons(self, parent_group):
        """Crea los botones del formulario."""
        botones_layout = QHBoxLayout()
        
        # Botón generar servicio
        self.btn_generar = LogisticaButton(
            "Generar Servicio", "success", ICONS["buttons"]["generar_servicio"], self
        )
        self.btn_generar.clicked.connect(self.generar_servicio)
        botones_layout.addWidget(self.btn_generar)
        
        # Botón limpiar formulario
        self.btn_limpiar = LogisticaButton(
            "Limpiar Formulario", "secondary", ICONS["buttons"]["limpiar"], self
        )
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        botones_layout.addWidget(self.btn_limpiar)
        
        botones_layout.addStretch()
        parent_group.add_layout(botones_layout)
    
    def create_services_table(self):
        """Crea la tabla de servicios generados."""
        servicios_group = LogisticaGroupBox("🚛 Servicios Programados", self)
        
        headers = ["Tipo", "Cliente", "Dirección", "Fecha", "Estado", "Acciones"]
        self.tabla_servicios = LogisticaTable(headers, self)
        
        servicios_group.add_widget(self.tabla_servicios)
        self.main_layout.addWidget(servicios_group)
    
    def generar_servicio(self):
        """Genera un nuevo servicio con los datos del formulario."""
        # Validar datos
        is_valid, error_msg = self.validate_form_data()
        if not is_valid:
            self.show_error(error_msg, "Datos inválidos")
            return
        
        # Recopilar datos del formulario
        servicio_data = self.get_form_data()
        
        # Agregar a la tabla
        self.agregar_servicio_tabla(servicio_data)
        
        # Emitir señal
        self.servicio_generado.emit(servicio_data)
        
        # Mostrar confirmación
        cliente = servicio_data.get("cliente", "cliente")
        self.show_success(f"Servicio creado para {cliente}")
        
        # Limpiar formulario
        self.limpiar_formulario()
    
    def validate_form_data(self) -> tuple[bool, str]:
        """Valida los datos del formulario."""
        # Validar campos requeridos
        required_fields = ["input_cliente", "input_direccion", "input_contacto"]
        
        for field_name in required_fields:
            widget = self.form_widgets.get(field_name)
            if widget and hasattr(widget, 'text') and not widget.text().strip():
                field_label = field_name.replace("input_", "").replace("_", " ").title()
                return False, f"El campo '{field_label}' es requerido"
        
        # Validar formato de hora si está presente
        hora_widget = self.form_widgets.get("input_hora")
        if hora_widget and hora_widget.text().strip():
            hora_text = hora_widget.text().strip()
            if not self.validate_time_format(hora_text):
                return False, "Formato de hora inválido. Use HH:MM"
        
        return True, ""
    
    def validate_time_format(self, time_str: str) -> bool:
        """Valida el formato de hora HH:MM."""
        try:
            if ":" not in time_str:
                return False
            
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except ValueError:
            return False
    
    def get_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario."""
        data = {}
        
        # Obtener datos de cada widget
        for field_name, widget in self.form_widgets.items():
            if hasattr(widget, 'text'):
                data[field_name.replace("input_", "").replace("combo_", "")] = widget.text()
            elif hasattr(widget, 'currentText'):
                data[field_name.replace("combo_", "")] = widget.currentText()
            elif hasattr(widget, 'date'):
                data[field_name.replace("date_", "")] = widget.date().toString("yyyy-MM-dd")
            elif hasattr(widget, 'toPlainText'):
                data[field_name.replace("text_", "")] = widget.toPlainText()
        
        # Agregar datos adicionales
        data["estado"] = "Programado"
        data["fecha_creacion"] = QDate.currentDate().toString("yyyy-MM-dd")
        
        return data
    
    def agregar_servicio_tabla(self, servicio: Dict[str, Any]):
        """Agrega un servicio a la tabla."""
        self.servicios_data.append(servicio)
        
        row = self.tabla_servicios.rowCount()
        self.tabla_servicios.setRowCount(row + 1)
        
        # Llenar celdas
        self.tabla_servicios.setItem(row, 0, self.create_table_item(servicio.get("tipo_servicio", "")))
        self.tabla_servicios.setItem(row, 1, self.create_table_item(servicio.get("cliente", "")))
        self.tabla_servicios.setItem(row, 2, self.create_table_item(servicio.get("direccion", "")))
        
        fecha_programada = servicio.get("programada", "")
        hora = servicio.get("hora", "")
        fecha_completa = f"{fecha_programada} {hora}".strip()
        self.tabla_servicios.setItem(row, 3, self.create_table_item(fecha_completa))
        
        self.tabla_servicios.setItem(row, 4, self.create_table_item(servicio.get("estado", "")))
        self.tabla_servicios.setItem(row, 5, self.create_table_item("Ver Detalles"))
    
    def create_table_item(self, text: str):
        """Crea un item de tabla."""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        for field_name, widget in self.form_widgets.items():
            if hasattr(widget, 'setText'):
                widget.setText("")
            elif hasattr(widget, 'setCurrentIndex'):
                widget.setCurrentIndex(0)
            elif hasattr(widget, 'setDate'):
                widget.setDate(QDate.currentDate())
            elif hasattr(widget, 'setPlainText'):
                widget.setPlainText("")
        
        self.show_success("Formulario limpiado correctamente")
    
    def cargar_servicios_en_tabla(self, servicios: List[Dict[str, Any]]):
        """Carga servicios en la tabla (compatibilidad)."""
        self.servicios_data = servicios
        self.tabla_servicios.setRowCount(len(servicios))
        
        for row, servicio in enumerate(servicios):
            self.agregar_servicio_tabla(servicio)
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna los datos actuales de servicios."""
        return {
            "servicios": self.servicios_data,
            "form_data": self.get_form_data() if hasattr(self, 'form_widgets') else {}
        }
    
    def clear(self):
        """Limpia el formulario y los datos."""
        self.limpiar_formulario()
        self.servicios_data.clear()
        self.tabla_servicios.setRowCount(0)