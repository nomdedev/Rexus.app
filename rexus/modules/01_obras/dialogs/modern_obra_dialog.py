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

import sys
from typing import Optional, Dict, Any
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QCheckBox, QVBoxLayout
)

# Importar componentes modernos con manejo de errores
try:
    from rexus.utils.modern_form_components import ModernFormDialog, FormValidators
except ImportError:
    print("[WARNING] Modern form components not available, using basic dialog")
    from PyQt6.QtWidgets import QDialog as ModernFormDialog

    class FormValidators:
        @staticmethod
        def code_format(value):
            return bool(value.strip() if hasattr(value, 'strip') else value)

        @staticmethod
        def required_field(value):
            return bool(value.strip() if hasattr(value, 'strip') else value)

        @staticmethod
        def numeric_range(value, min_val=None, max_val=None):
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    return False
                if max_val is not None and num > max_val:
                    return False
                return True
            except (ValueError, TypeError):
                return False

        @staticmethod
        def email_format(value):
            return '@' in str(value) if value else False



class ModernObraDialog(ModernFormDialog):
    """Diálogo moderno para crear/editar obras"""

    def __init__(self, parent=None, obra_data: Optional[Dict] = None):
        self.obra_data = obra_data
        self.is_editing = obra_data is not None

        title = "Editar Obra" if self.is_editing else "Nueva Obra"
        super().__init__(title, parent)

        self.setup_form_fields()

        if self.is_editing:
            self.load_obra_data()

    def setup_form_fields(self):
        """Configura todos los campos del formulario"""

        # SECCIÓN: INFORMACIÓN BÁSICA
        basic_section = self.add_section("🏗️ Información Básica")
        QVBoxLayout(basic_section)

        # Código de obra
        codigo_input = QLineEdit()
        codigo_input.setPlaceholderText("Ej: OBR-2024-001")
        self.add_field(
            "codigo_obra", "Código de Obra", codigo_input,
            required=True,
            tooltip="Código único para identificar la obra (formato: OBR-YYYY-NNN)",
            validation_func=lambda x: self.validate_codigo_obra(x)
        )

        # Nombre de la obra
        nombre_input = QLineEdit()
        nombre_input.setPlaceholderText("Nombre descriptivo de la obra")
        self.add_field(
            "nombre", "Nombre de la Obra", nombre_input,
            required=True,
            tooltip="Nombre claro y descriptivo de la obra",
            validation_func=FormValidators.required_field
        )

        # Descripción
        descripcion_input = QTextEdit()
        descripcion_input.setMaximumHeight(100)
        descripcion_input.setPlaceholderText("Descripción detallada de la obra, alcance, características...")
        self.add_field(
            "descripcion", "Descripción", descripcion_input,
            tooltip="Descripción detallada del proyecto"
        )

        # Cliente ID (combo con clientes existentes)
        cliente_combo = QComboBox()
        cliente_combo.setEditable(True)
        cliente_combo.addItems([
            "Cliente 1 - Juan Pérez",
            "Cliente 2 - María García",
            "Cliente 3 - Empresa ABC S.A.",
            "Cliente 4 - Constructora XYZ"
        ])
        self.add_field(
            "cliente_id", "Cliente", cliente_combo,
            required=True,
            tooltip="Seleccionar cliente existente o crear nuevo"
        )

        # SECCIÓN: FECHAS Y CRONOGRAMA
        fechas_section = self.add_section("📅 Cronograma")
        QVBoxLayout(fechas_section)

        # Fecha de inicio
        fecha_inicio_input = QDateEdit()
        fecha_inicio_input.setDate(QDate.currentDate())
        fecha_inicio_input.setCalendarPopup(True)
        self.add_field(
            "fecha_inicio", "Fecha de Inicio", fecha_inicio_input,
            required=True,
            tooltip="Fecha planificada de inicio de la obra"
        )

        # Fecha fin estimada
        fecha_fin_estimada_input = QDateEdit()
        fecha_fin_estimada_input.setDate(QDate.currentDate().addMonths(3))
        fecha_fin_estimada_input.setCalendarPopup(True)
        self.add_field(
            "fecha_fin_estimada", "Fecha Fin Estimada", fecha_fin_estimada_input,
            required=True,
            tooltip="Fecha estimada de finalización de la obra"
        )

        # Fecha fin real
        fecha_fin_real_input = QDateEdit()
        fecha_fin_real_input.setCalendarPopup(True)
        fecha_fin_real_input.setEnabled(False)  # Se habilita cuando la obra esté terminada
        self.add_field(
            "fecha_fin_real", "Fecha Fin Real", fecha_fin_real_input,
            tooltip="Fecha real de finalización (se completa al finalizar la obra)"
        )

        # SECCIÓN: ESTADO Y PROGRESO
        estado_section = self.add_section("[CHART] Estado y Progreso")
        QVBoxLayout(estado_section)

        # Etapa actual
        etapa_combo = QComboBox()
        etapa_combo.addItems([
            "PLANIFICACION", "DISEÑO", "PERMISOS", "PREPARACION_SITIO",
            "CIMENTACION", "ESTRUCTURA", "CERRAMIENTOS", "INSTALACIONES",
            "ACABADOS", "REVISION", "ENTREGA", "COMPLETADA"
        ])
        self.add_field(
            "etapa_actual", "Etapa Actual", etapa_combo,
            required=True,
            tooltip="Etapa actual en la que se encuentra la obra"
        )

        # Estado de la obra
        estado_combo = QComboBox()
        estado_combo.addItems([
            "PLANIFICACION", "EN_PROCESO", "PAUSADA", "COMPLETADA",
            "CANCELADA", "EN_REVISION", "ENTREGADA"
        ])
        self.add_field(
            "estado", "Estado", estado_combo,
            required=True,
            tooltip="Estado general de la obra"
        )

        # Porcentaje completado
        porcentaje_input = QSpinBox()
        porcentaje_input.setRange(0, 100)
        porcentaje_input.setSuffix(" %")
        self.add_field(
            "porcentaje_completado", "Porcentaje Completado", porcentaje_input,
            tooltip="Porcentaje de avance de la obra (0-100%)"
        )

        # SECCIÓN: ASPECTOS FINANCIEROS
        financiero_section = self.add_section("[MONEY] Aspectos Financieros")
        QVBoxLayout(financiero_section)

        # Presupuesto inicial
        presupuesto_inicial_input = QDoubleSpinBox()
        presupuesto_inicial_input.setRange(0.00, 999999999.99)
        presupuesto_inicial_input.setDecimals(2)
        presupuesto_inicial_input.setPrefix("$ ")
        self.add_field(
            "presupuesto_inicial", "Presupuesto Inicial", presupuesto_inicial_input,
            required=True,
            tooltip="Presupuesto inicial acordado con el cliente",
            validation_func=lambda x: FormValidators.numeric_range(x, 0.01)
        )

        # Costo actual
        costo_actual_input = QDoubleSpinBox()
        costo_actual_input.setRange(0.00, 999999999.99)
        costo_actual_input.setDecimals(2)
        costo_actual_input.setPrefix("$ ")
        self.add_field(
            "costo_actual", "Costo Actual", costo_actual_input,
            tooltip="Costo acumulado hasta la fecha"
        )

        # Margen estimado
        margen_estimado_input = QDoubleSpinBox()
        margen_estimado_input.setRange(-999999.99, 999999999.99)
        margen_estimado_input.setDecimals(2)
        margen_estimado_input.setPrefix("$ ")
        self.add_field(
            "margen_estimado", "Margen Estimado", margen_estimado_input,
            tooltip="Margen de ganancia estimado (puede ser negativo si hay pérdidas)"
        )

        # SECCIÓN: UBICACIÓN Y RESPONSABLES
        ubicacion_section = self.add_section("📍 Ubicación y Responsables")
        QVBoxLayout(ubicacion_section)

        # Ubicación/Dirección
        ubicacion_input = QTextEdit()
        ubicacion_input.setMaximumHeight(80)
        ubicacion_input.setPlaceholderText("Dirección completa de la obra, referencias, coordenadas...")
        self.add_field(
            "ubicacion", "Ubicación", ubicacion_input,
            required=True,
            tooltip="Dirección completa donde se realizará la obra",
            validation_func=FormValidators.required_field
        )

        # Responsable de obra
        responsable_combo = QComboBox()
        responsable_combo.setEditable(True)
        responsable_combo.addItems([
            "Ing. Carlos Rodríguez",
            "Arq. Ana Martínez",
            "Ing. Luis González",
            "Arq. Patricia López"
        ])
        self.add_field(
            "responsable_obra", "Responsable de Obra", responsable_combo,
            required=True,
            tooltip="Responsable técnico asignado a la obra"
        )

        # SECCIÓN: INFORMACIÓN ADICIONAL
        adicional_section = self.add_section("📋 Información Adicional")
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
                                print(f"[WARNING OBRA_DIALOG] Invalid date format '{value}': {e}")
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
            QMessageBox.warning(self, "Error de Validación", error_message)
            return

        # Mostrar loading y proceder con guardado
        self.show_loading("Guardando obra...")

        # Simular guardado (reemplazar con lógica real)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.on_save_complete)


if __name__ == "__main__":
    """Test del diálogo moderno de obras"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test con obra nueva
    dialog = ModernObraDialog()

    if dialog.exec() == dialog.DialogCode.Accepted:
        data = dialog.get_obra_data()
        print("Datos de la obra:")
        for key, value in data.items():
            print(f"  {key}: {value}")

    app.exec()
