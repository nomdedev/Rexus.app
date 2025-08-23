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
DiÃ¡logo moderno mejorado para productos de inventario
Incluye todos los campos de la base de datos con feedback visual avanzado
"""


import logging
logger = logging.getLogger(__name__)

import sys
                        tooltip="Estado actual del producto"
        )

        # Producto activo
        activo_checkbox = QCheckBox("Producto activo")
        activo_checkbox.setChecked(True)
        self.add_field(
            "activo", "Activo", activo_checkbox,
            tooltip="Marcar si el producto estÃ¡ activo en el sistema"
        )

    def load_product_data(self):
        """Carga los datos del producto para ediciÃ³n"""
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
        """Valida reglas de negocio especÃ­ficas"""
        data = self.get_form_data()

        # Validar que stock mÃ­nimo <= stock mÃ¡ximo
        if data.get("stock_minimo", 0) > data.get("stock_maximo", 0):
            return False, "El stock mÃ­nimo no puede ser mayor al stock mÃ¡ximo"

        # Validar que stock actual no exceda stock mÃ¡ximo
        if data.get("stock_actual", 0) > data.get("stock_maximo", 0):
            return False, "El stock actual no puede exceder el stock mÃ¡ximo"

        # Validar que precio unitario > costo unitario
        precio = data.get("precio_unitario", 0)
        costo = data.get("costo_unitario", 0)
        if costo > 0 and precio <= costo:
            return False, "El precio unitario debe ser mayor al costo unitario"

        return True, ""

    def validate_and_save(self):
        """Valida incluyendo reglas de negocio antes de guardar"""
        # ValidaciÃ³n estÃ¡ndar de campos
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
            QMessageBox.warning(self, , error_message)
            return

        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando producto...")

        # Simular guardado (reemplazar con lÃ³gica real)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == :
    """Test del diÃ¡logo moderno"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test con producto nuevo
    dialog = ModernProductDialog()

    if dialog.exec() == dialog.DialogCode.Accepted:
        data = dialog.get_product_data()
        logger.info()
        for key, value in data.items():
            logger.info(f"  {key}: {value}")

    app.exec()
