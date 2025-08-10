"""
Diálogo para crear/editar entregas

Diálogo modular y reutilizable para la gestión de entregas.
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QDateEdit, QComboBox
)

from ..constants import ESTADOS_ENTREGA, UI_CONFIG
from ..styles import MAIN_STYLE
from ..widgets import LogisticaButton, FormBuilder, NotificationManager
from rexus.utils.form_validators import FormValidator, validacion_direccion


class DialogoNuevaEntrega(QDialog):
    """Diálogo para crear o editar entregas."""
    
    def __init__(self, parent=None, entrega_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        self.entrega_data = entrega_data
        self.is_editing = entrega_data is not None
        self.notification_manager = NotificationManager()
        
        # Configurar diálogo
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setWindowTitle("Editar Entrega" if self.is_editing else "Nueva Entrega")
        
        # Aplicar estilos
        self.setStyleSheet(MAIN_STYLE)
        
        # Inicializar UI
        self.setup_ui()
        self.setup_validations()
        
        # Cargar datos si estamos editando
        if self.is_editing:
            self.load_data()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt
        
        title = QLabel("✏️ Editar Entrega" if self.is_editing else "➕ Nueva Entrega")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #212529; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Formulario
        self.create_form(layout)
        
        # Botones
        self.create_buttons(layout)
    
    def create_form(self, parent_layout):
        """Crea el formulario de entrega."""
        # Configuración de campos
        fields_config = {
            "input_direccion": {
                "type": "line_edit",
                "label": "Dirección de Entrega",
                "placeholder": "Dirección completa de entrega",
                "width": UI_CONFIG["widget_widths"]["input_direccion"]
            },
            "input_contacto": {
                "type": "line_edit", 
                "label": "Contacto",
                "placeholder": "Nombre del contacto",
                "width": UI_CONFIG["widget_widths"]["input_contacto"]
            },
            "input_telefono": {
                "type": "line_edit",
                "label": "Teléfono",
                "placeholder": "Número de teléfono",
                "width": UI_CONFIG["widget_widths"]["input_contacto"]
            },
            "date_programada": {
                "type": "date_edit",
                "label": "Fecha Programada",
                "width": UI_CONFIG["widget_widths"]["date_programada"]
            },
            "combo_estado": {
                "type": "combo_box",
                "label": "Estado",
                "options": [estado for estado in ESTADOS_ENTREGA if estado != "Todos"],
                "width": UI_CONFIG["widget_widths"]["combo_estado"]
            },
            "text_observaciones": {
                "type": "text_edit",
                "label": "Observaciones",
                "placeholder": "Observaciones adicionales...",
                "height": UI_CONFIG["heights"]["text_observaciones"]
            }
        }
        
        # Crear formulario usando FormBuilder
        form_layout, self.form_widgets = FormBuilder.create_form_layout(fields_config)
        parent_layout.addLayout(form_layout)
    
    def create_buttons(self, parent_layout):
        """Crea los botones del diálogo."""
        buttons_layout = QHBoxLayout()
        
        # Botón cancelar
        btn_cancelar = LogisticaButton("Cancelar", "secondary", "", self)
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        buttons_layout.addStretch()
        
        # Botón guardar
        btn_text = "Actualizar" if self.is_editing else "Crear Entrega"
        btn_guardar = LogisticaButton(btn_text, "success", "💾", self)
        btn_guardar.clicked.connect(self.validar_y_aceptar)
        buttons_layout.addWidget(btn_guardar)
        
        parent_layout.addLayout(buttons_layout)
    
    def setup_validations(self):
        """Configura las validaciones del formulario."""
        self.validator = FormValidator()
        
        # Validación de dirección
        direccion_widget = self.form_widgets.get("input_direccion")
        if direccion_widget:
            direccion_widget.textChanged.connect(self.validate_direccion)
    
    def validate_direccion(self):
        """Valida la dirección ingresada."""
        direccion_widget = self.form_widgets.get("input_direccion")
        if direccion_widget:
            direccion = direccion_widget.text().strip()
            if direccion:
                is_valid = validacion_direccion(direccion)
                # Cambiar estilo según validación
                if is_valid:
                    direccion_widget.setStyleSheet("")
                else:
                    direccion_widget.setStyleSheet("border: 2px solid #dc3545;")
    
    def load_data(self):
        """Carga los datos de la entrega para edición."""
        if not self.entrega_data:
            return
        
        # Cargar dirección
        direccion_widget = self.form_widgets.get("input_direccion")
        if direccion_widget:
            direccion_widget.setText(self.entrega_data.get("direccion", ""))
        
        # Cargar contacto
        contacto_widget = self.form_widgets.get("input_contacto")
        if contacto_widget:
            contacto_text = self.entrega_data.get("contacto", "")
            # Extraer solo el nombre si tiene formato "Nombre - Teléfono"
            if " - " in contacto_text:
                contacto_text = contacto_text.split(" - ")[0]
            contacto_widget.setText(contacto_text)
        
        # Cargar teléfono
        telefono_widget = self.form_widgets.get("input_telefono")
        if telefono_widget:
            contacto_full = self.entrega_data.get("contacto", "")
            telefono = ""
            if " - " in contacto_full:
                telefono = contacto_full.split(" - ")[1]
            telefono_widget.setText(telefono)
        
        # Cargar fecha
        fecha_widget = self.form_widgets.get("date_programada")
        if fecha_widget:
            fecha_str = self.entrega_data.get("fecha_programada", "")
            if fecha_str:
                try:
                    from PyQt6.QtCore import QDate
                    fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
                    if fecha.isValid():
                        fecha_widget.setDate(fecha)
                except:
                    pass
        
        # Cargar estado
        estado_widget = self.form_widgets.get("combo_estado")
        if estado_widget:
            estado = self.entrega_data.get("estado", "Programada")
            index = estado_widget.findText(estado)
            if index >= 0:
                estado_widget.setCurrentIndex(index)
        
        # Cargar observaciones
        obs_widget = self.form_widgets.get("text_observaciones")
        if obs_widget:
            obs_widget.setPlainText(self.entrega_data.get("observaciones", ""))
    
    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar el diálogo."""
        # Validar campos requeridos
        direccion_widget = self.form_widgets.get("input_direccion")
        contacto_widget = self.form_widgets.get("input_contacto")
        
        if not direccion_widget or not direccion_widget.text().strip():
            self.notification_manager.show_error(
                self, "Validación", "La dirección es requerida"
            )
            return
        
        if not contacto_widget or not contacto_widget.text().strip():
            self.notification_manager.show_error(
                self, "Validación", "El contacto es requerido"
            )
            return
        
        # Validar dirección
        direccion = direccion_widget.text().strip()
        if not validacion_direccion(direccion):
            self.notification_manager.show_error(
                self, "Validación", "La dirección no tiene un formato válido"
            )
            return
        
        # Si llegamos aquí, todo está válido
        self.accept()
    
    def obtener_datos(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        data = {}
        
        # Obtener datos de cada widget
        for field_name, widget in self.form_widgets.items():
            clean_name = field_name.replace("input_", "").replace("combo_", "").replace("date_", "").replace("text_", "")
            
            if hasattr(widget, 'text'):
                data[clean_name] = widget.text().strip()
            elif hasattr(widget, 'currentText'):
                data[clean_name] = widget.currentText()
            elif hasattr(widget, 'date'):
                data[clean_name] = widget.date().toString("yyyy-MM-dd")
            elif hasattr(widget, 'toPlainText'):
                data[clean_name] = widget.toPlainText().strip()
        
        # Combinar contacto y teléfono
        contacto = data.get("contacto", "")
        telefono = data.get("telefono", "")
        if contacto and telefono:
            data["contacto"] = f"{contacto} - {telefono}"
        elif contacto:
            data["contacto"] = contacto
        
        # Remover teléfono separado ya que se combina con contacto
        if "telefono" in data:
            del data["telefono"]
        
        return data