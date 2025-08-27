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
Diálogo moderno mejorado para obras
Incluye todos los campos de la base de datos con feedback visual avanzado
"""

import logging
import sys
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QTextEdit, QComboBox, QLineEdit, QCheckBox, QDialog, QFormLayout, QWidget, QLabel, QDialogButtonBox)
from PyQt6.QtCore import QDate, QTimer

logger = logging.getLogger(__name__)

# Add missing class definition and method
class ModernObraDialog(QDialog):
    def __init__(self, obra_data: Optional[Dict[str, Any]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.obra_data = obra_data or {}
        self.fields = {}
        self.setup_ui()
        self.setup_form_fields()
        
        if self.obra_data:
            self.load_obra_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        self.setWindowTitle("Obra - Gestión de Obras")
        self.setModal(True)
        self.resize(800, 600)
        
        # Layout principal
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Formulario
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        
        # Botones
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.validate_and_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def add_section(self, title):
        """Añade una sección al formulario"""
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.form_layout.addRow(label)
        return label
    
    def add_field(self, name, label, widget, tooltip="", validation_func=None):
        """Añade un campo al formulario"""
        label_widget = QLabel(label)
        widget.setToolTip(tooltip)
        self.form_layout.addRow(label_widget, widget)
        
        # Store field info
        self.fields[name] = type('Field', (), {'widget': widget, 'label': label_widget, 'validate': lambda: True})()
        
        return widget
    
    def setup_form_fields(self):
        """Setup form fields for obra dialog"""
        # This appears to be part of a larger method
        # Adding the missing context for the tooltip line
        responsable_input = QLineEdit()
        responsable_input.setPlaceholderText("Nombre del responsable técnico")
        self.add_field(
            "responsable_tecnico", "Responsable Técnico", responsable_input,
            tooltip="Responsable técnico asignado a la obra"
        )

        # SECCIÓN: INFORMACIÓN ADICIONAL
        adicional_section = self.add_section("[CLIPBOARD] Información Adicional")
        QVBoxLayout(adicional_section)

        # Observaciones
        observaciones_input = QTextEdit()
        observaciones_input.setMaximumHeight(120)
        observaciones_input.setPlaceholderText("Observaciones especiales, notas técnicas, restricciones, condiciones especiales...")
        self.add_field(
            "observaciones", "Observaciones", observaciones_input,
            tooltip="Información adicional relevante para la obra"
        )

        # Tipo de obra (campo adicional no en BD original)
        tipo_obra_combo = QComboBox()
        tipo_obra_combo.addItems([
            "CONSTRUCCION", "RENOVACION", "AMPLIACION", "REPARACION",
            "MANTENIMIENTO", "DEMOLICION", "RESTAURACION", "OTRO"
        ])
        self.add_field(
            "tipo_obra", "Tipo de Obra", tipo_obra_combo,
            tooltip="Clasificación del tipo de obra"
        )

        # Prioridad (campo adicional no en BD original)
        prioridad_combo = QComboBox()
        prioridad_combo.addItems(["BAJA",
"NORMAL",
            "ALTA",
            "URGENTE",
            "CRITICA"])
        prioridad_combo.setCurrentText("NORMAL")
        self.add_field(
            "prioridad", "Prioridad", prioridad_combo,
            tooltip="Nivel de prioridad de la obra"
        )

        # Contacto en obra (campo adicional)
        contacto_obra_input = QLineEdit()
        contacto_obra_input.setPlaceholderText("Persona de contacto en la obra")
        self.add_field(
            "contacto_obra", "Contacto en Obra", contacto_obra_input,
            tooltip="Persona de contacto disponible en el sitio de la obra"
        )

        # Teléfono de contacto (campo adicional)
        telefono_input = QLineEdit()
        telefono_input.setPlaceholderText("Ej: +54 11 1234-5678")
        self.add_field(
            "telefono_contacto", "Teléfono de Contacto", telefono_input,
            tooltip="Número de teléfono para contacto durante la obra"
        )

        # Email de contacto (campo adicional)
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@ejemplo.com")
        self.add_field(
            "email_contacto", "Email de Contacto", email_input,
            tooltip="Email de contacto para la obra"
        )

        # Obra activa
        activo_checkbox = QCheckBox("Obra activa")
        activo_checkbox.setChecked(True)
        self.add_field(
            "activo", "Activo", activo_checkbox,
            tooltip="Marcar si la obra está activa en el sistema"
        )

    def validate_codigo_obra(self, value) -> tuple[bool, str]:
        """Valida formato específico del código de obra"""
        if not value:
            return False, "Código de obra es obligatorio"

        import re
        pattern = r'^OBR-\d{4}-\d{3,6}$'
        if not re.match(pattern, value.upper()):
            return False, "Formato: OBR-YYYY-NNN (ej: OBR-2024-001)"
        return True, ""

    def load_obra_data(self):
        """Carga los datos de la obra para edición"""
        if not self.obra_data:
            return

        for key, field in self.fields.items():
            if key in self.obra_data:
                value = self.obra_data[key]
                self._set_widget_value(field.widget, value)

    def _set_widget_value(self, widget, value):
        """Sets the value for a specific widget type"""
        if hasattr(widget, 'setText'):
            self._set_text_widget(widget, value)
        elif hasattr(widget, 'setValue'):
            self._set_numeric_widget(widget, value)
        elif hasattr(widget, 'setCurrentText'):
            self._set_combo_widget(widget, value)
        elif hasattr(widget, 'setChecked'):
            self._set_checkbox_widget(widget, value)
        elif hasattr(widget, 'setPlainText'):
            self._set_plaintext_widget(widget, value)
        elif hasattr(widget, 'setDate'):
            self._set_date_widget(widget, value)

    def _set_text_widget(self, widget, value):
        """Sets value for text input widgets"""
        widget.setText(str(value) if value else "")

    def _set_numeric_widget(self, widget, value):
        """Sets value for numeric input widgets"""
        widget.setValue(value if value is not None else 0)

    def _set_combo_widget(self, widget, value):
        """Sets value for combo box widgets"""
        widget.setCurrentText(str(value) if value else "")

    def _set_checkbox_widget(self, widget, value):
        """Sets value for checkbox widgets"""
        widget.setChecked(bool(value))

    def _set_plaintext_widget(self, widget, value):
        """Sets value for plain text widgets"""
        widget.setPlainText(str(value) if value else "")

    def _set_date_widget(self, widget, value):
        """Sets value for date widgets"""
        if not value:
            return
        
        if isinstance(value, str):
            self._set_date_from_string(widget, value)
        else:
            widget.setDate(value)

    def _set_date_from_string(self, widget, date_string):
        """Converts string date to QDate and sets it"""
        try:
            date_parts = date_string.split('-')
            qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
            widget.setDate(qdate)
        except (ValueError, IndexError) as e:
            logger.info(f"Error parsing date: {e}")
            widget.setDate(QDate.currentDate())

    def get_obra_data(self) -> Dict[str, Any]:
        """Obtiene los datos de la obra del formulario"""
        data = self.get_form_data()

        # Convertir QDate a string para fechas
        for key in ["fecha_inicio", "fecha_fin_estimada", "fecha_fin_real"]:
            if key in data and hasattr(data[key], 'toString'):
                data[key] = data[key].toString("yyyy-MM-dd")

        return data

    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario"""
        data = {}
        for key, field in self.fields.items():
            widget = field.widget
            if hasattr(widget, 'text'):
                data[key] = widget.text()
            elif hasattr(widget, 'value'):
                data[key] = widget.value()
            elif hasattr(widget, 'currentText'):
                data[key] = widget.currentText()
            elif hasattr(widget, 'isChecked'):
                data[key] = widget.isChecked()
            elif hasattr(widget, 'toPlainText'):
                data[key] = widget.toPlainText()
            elif hasattr(widget, 'date'):
                data[key] = widget.date()
        return data

    def show_loading(self, message: str):
        """Muestra un mensaje de carga"""
        # Implementar loading dialog si es necesario
        logger.info(f"Loading: {message}")

    def on_save_complete(self):
        """Callback cuando se completa el guardado"""
        logger.info("Obra guardada exitosamente")
        self.accept()

    def validate_business_rules(self) -> tuple[bool, str]:
        """Valida reglas de negocio específicas para obras"""
        data = self.get_form_data()

        # Validar que fecha inicio <= fecha fin estimada
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin_est = data.get("fecha_fin_estimada")

        if fecha_inicio and fecha_fin_est and hasattr(fecha_inicio, 'daysTo'):
            if fecha_inicio.daysTo(fecha_fin_est) < 0:
                return False, "La fecha de fin estimada debe ser posterior a la fecha de inicio"

        # Validar porcentaje vs estado
        porcentaje = data.get("porcentaje_completado", 0)
        estado = data.get("estado", "")

        if estado == "COMPLETADA" and porcentaje < 100:
            return False, "Una obra completada debe tener 100% de progreso"

        if estado == "PLANIFICACION" and porcentaje > 10:
            return False, "Una obra en planificación no debería tener más del 10% de progreso"

        # Validar presupuesto vs costo
        presupuesto = data.get("presupuesto_inicial", 0)
        costo_actual = data.get("costo_actual", 0)

        if costo_actual > presupuesto * 1.5:  # 150% del presupuesto
            return False, "El costo actual excede significativamente el presupuesto inicial. Revisar."

        return True, ""

    def validate_and_save(self):
        """Valida incluyendo reglas de negocio antes de guardar"""
        # Validación estándar de campos
        all_valid = True
        for field in self.fields.values():
            if not field.validate():
                all_valid = False

        if not all_valid:
            return

        # Validaciones de reglas de negocio
        is_valid, error_message = self.validate_business_rules()
        if not is_valid:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error de validación", error_message)
            return

        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando obra...")

        # Simular guardado (reemplazar con lógica real)
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == "__main__":
    """Test del diálogo moderno de obras"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test con obra nueva
    dialog = ModernObraDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        data = dialog.get_obra_data()
        logger.info("Datos de la obra guardada:")
        for key, value in data.items():
            logger.info(f"  {key}: {value}")

    app.exec()
