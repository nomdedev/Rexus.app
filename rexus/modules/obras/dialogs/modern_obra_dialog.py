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
logger = logging.getLogger(__name__)

import sys
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
            tooltip="Email de contacto para la obra",
            validation_func=FormValidators.email_format
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
                elif hasattr(widget, 'setDate'):
                    if value:
                        from PyQt6.QtCore import QDate
                        if isinstance(value, str):
                            # Convertir string a QDate
                            try:
                                date_parts = value.split('-')
                                qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                                widget.setDate(qdate)
                            except (ValueError, IndexError) as e:
                                logger.info(f)
                                widget.setDate(QDate.currentDate())
                        else:
                            widget.setDate(value)

    def get_obra_data(self) -> Dict[str, Any]:
        """Obtiene los datos de la obra del formulario"""
        data = self.get_form_data()

        # Convertir QDate a string para fechas
        for key in ["fecha_inicio", "fecha_fin_estimada", "fecha_fin_real"]:
            if key in data and hasattr(data[key], 'toString'):
                data[key] = data[key].toString("yyyy-MM-dd")

        return data

    def validate_business_rules(self) -> tuple[bool, str]:
        """Valida reglas de negocio específicas para obras"""
        data = self.get_form_data()

        # Validar que fecha inicio <= fecha fin estimada
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin_est = data.get("fecha_fin_estimada")

        if fecha_inicio and fecha_fin_est:
            if hasattr(fecha_inicio, 'daysTo'):
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
            QMessageBox.warning(self, , error_message)
            return

        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando obra...")

        # Simular guardado (reemplazar con lógica real)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == :
    """Test del diálogo moderno de obras"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test con obra nueva
    dialog = ModernObraDialog()

    if dialog.exec() == dialog.DialogCode.Accepted:
        data = dialog.get_obra_data()
        logger.info()
        for key, value in data.items():
            logger.info(f"  {key}: {value}")

    app.exec()
