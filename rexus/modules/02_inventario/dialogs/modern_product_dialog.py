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
Diálogo moderno mejorado para productos de inventario
Incluye todos los campos de la base de datos con feedback visual avanzado
"""

import logging
import sys
from typing import Dict, Any
from PyQt6.QtWidgets import QCheckBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QPushButton, QFormLayout, QApplication, QMessageBox
from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)


class ModernProductDialog(QDialog):
    def __init__(self, product_data=None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.fields = {}
        self.setup_ui()
        if self.product_data:
            self.load_product_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Producto - Gestión de Inventario")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Producto activo
        activo_checkbox = QCheckBox("Producto activo")
        activo_checkbox.setChecked(True)
        self.add_field(
            "activo", "Activo", activo_checkbox,
            tooltip="Marcar si el producto está activo en el sistema"
        )
        
        form_layout.addRow("Estado:", activo_checkbox)
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        cancel_button = QPushButton("Cancelar")
        
        save_button.clicked.connect(self.validate_and_save)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def add_field(self, field_name, label, widget, tooltip=None):
        """Agrega un campo al formulario"""
        self.fields[field_name] = type('Field', (), {'widget': widget, 'validate': lambda: True})()
        if tooltip:
            widget.setToolTip(tooltip)
    
    def get_form_data(self):
        """Obtiene los datos del formulario"""
        data = {}
        for field_name, field in self.fields.items():
            widget = field.widget
            if hasattr(widget, 'isChecked'):
                data[field_name] = widget.isChecked()
            elif hasattr(widget, 'text'):
                data[field_name] = widget.text()
            elif hasattr(widget, 'value'):
                data[field_name] = widget.value()
            elif hasattr(widget, 'toPlainText'):
                data[field_name] = widget.toPlainText()
        return data
    
    def show_loading(self, message):
        """Muestra indicador de carga"""
        logger.info(f"Loading: {message}")
    
    def on_save_complete(self):
        """Callback cuando se completa el guardado"""
        logger.info("Producto guardado exitosamente")
        self.accept()

    def load_product_data(self):
        """Carga los datos del producto para edición"""
        if not self.product_data:
            return

        for key, field in self.fields.items():
            if key in self.product_data:
                value = self.product_data[key]
                widget = field.widget

                if hasattr(widget, 'setText'):
                    widget.setText(str(value) if value else "")
                elif hasattr(widget, 'setValue'):
                    widget.setValue(value if value is not None else 0)
                elif hasattr(widget, 'setCurrentText'):
                    widget.setCurrentText(str(value) if value else "")
                elif hasattr(widget, 'setChecked'):
                    widget.setChecked(bool(value))
                elif hasattr(widget, 'setPlainText'):
                    widget.setPlainText(str(value) if value else "")

    def get_product_data(self) -> Dict[str, Any]:
        """Obtiene los datos del producto del formulario"""
        return self.get_form_data()

    def validate_business_rules(self) -> tuple[bool, str]:
        """Valida reglas de negocio específicas"""
        data = self.get_form_data()

        # Validar que stock mínimo <= stock máximo
        if data.get("stock_minimo", 0) > data.get("stock_maximo", 0):
            return False, "El stock mínimo no puede ser mayor al stock máximo"

        # Validar que stock actual no exceda stock máximo
        if data.get("stock_actual", 0) > data.get("stock_maximo", 0):
            return False, "El stock actual no puede exceder el stock máximo"

        # Validar que precio unitario > costo unitario
        precio = data.get("precio_unitario", 0)
        costo = data.get("costo_unitario", 0)
        if costo > 0 and precio <= costo:
            return False, "El precio unitario debe ser mayor al costo unitario"

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
            QMessageBox.warning(self, "Error de Validación", error_message)
            return

        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando producto...")

        # Simular guardado (reemplazar con lógica real)
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == "__main__":
    """Test del diálogo moderno"""
    app = QApplication(sys.argv)

    # Test con producto nuevo
    dialog = ModernProductDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        data = dialog.get_product_data()
        logger.info("Datos del producto:")
        for key, value in data.items():
            logger.info(f"  {key}: {value}")

    app.exec()