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

Vista de Mantenimiento - Interfaz de mantenimiento
"""

import logging

                        "EMERGENCIA",
            "INSPECCION"
        ])
        form_layout.addRow("Tipo*:", self.tipo_input)

        # Descripción (obligatorio)
        self.descripcion_input = RexusLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción del mantenimiento")
        self.descripcion_input.setMaxLength(500)
        form_layout.addRow("Descripción*:", self.descripcion_input)

        # Fecha programada
        self.fecha_programada_input = QDateEdit()
        self.fecha_programada_input.setDate(QDate.currentDate())
        self.fecha_programada_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Programada:", self.fecha_programada_input)

        # Estado
        self.estado_input = RexusComboBox()
        self.estado_input.addItems([
            "PROGRAMADO",
            "EN_PROGRESO",
            "COMPLETADO",
            "CANCELADO",
            "PENDIENTE"
        ])
        form_layout.addRow("Estado:", self.estado_input)

        # Costo estimado
        self.costo_estimado_input = QDoubleSpinBox()
        self.costo_estimado_input.setRange(0.0, 999999.99)
        self.costo_estimado_input.setPrefix("$ ")
        self.costo_estimado_input.setDecimals(2)
        form_layout.addRow("Costo Estimado:", self.costo_estimado_input)

        # Responsable
        self.responsable_input = RexusLineEdit()
        self.responsable_input.setPlaceholderText("Nombre del responsable")
        self.responsable_input.setMaxLength(100)
        form_layout.addRow("Responsable:", self.responsable_input)

        # Observaciones
        self.observaciones_input = RexusLineEdit()
        self.observaciones_input.setPlaceholderText("Observaciones adicionales")
        self.observaciones_input.setMaxLength(500)
        form_layout.addRow("Observaciones:", self.observaciones_input)

        layout.addLayout(form_layout)

        # Nota de campos obligatorios
        nota = RexusLabel("* Campos obligatorios", "caption")
        nota.setStyleSheet(f"color: {RexusColors.TEXT_SECONDARY}; font-style: italic;")
        layout.addWidget(nota)

        layout.addStretch()

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_cancelar = RexusButton("Cancelar", "secondary")
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_cancelar)

        botones_layout.addStretch()

        self.btn_crear = RexusButton("Crear Mantenimiento", "primary")
        self.btn_crear.clicked.connect(self.validar_y_aceptar)
        botones_layout.addWidget(self.btn_crear)

        layout.addLayout(botones_layout)

    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar."""
        # Validar campos obligatorios
        if self.equipo_id_input.value() <= 0:
            show_error(self, "Error", "Debe especificar un ID de equipo válido")
            self.equipo_id_input.setFocus()
            return

        if not self.descripcion_input.text().strip():
            show_error(self, "Error", "La descripción es obligatoria")
            self.descripcion_input.setFocus()
            return

        self.accept()

    def obtener_datos(self):
        """Retorna los datos del formulario."""
        return {
            "equipo_id": self.equipo_id_input.value(),
            "tipo": self.tipo_input.currentText(),
            "descripcion": self.descripcion_input.text().strip(),
            "fecha_programada": self.fecha_programada_input.date().toString("yyyy-MM-dd"),
            "estado": self.estado_input.currentText(),
            "costo_estimado": self.costo_estimado_input.value(),
            "responsable": self.responsable_input.text().strip() or "",
            "observaciones": self.observaciones_input.text().strip() or "",
        }

    # === MÉTODOS PARA BOTONES CORREGIDOS ===

    def ejecutar_accion_preventivo(self, row):
        """Ejecuta acción para mantenimiento preventivo."""
        show_success(self, "Acción Ejecutada", f"Procesando acción para fila {row + 1}")

    def ver_detalle_repuesto(self, row):
        """Ver detalle de repuesto."""
        show_success(self, "Ver Repuesto", f"Mostrando detalle del repuesto en fila {row + 1}")

    def ver_detalle_equipo(self, row):
        """Ver detalle de equipo."""
        show_success(self, "Ver Equipo", f"Mostrando detalle del equipo en fila {row + 1}")

    def ver_detalle(self, row):
        """Ver detalle general."""
        show_success(self, "Ver Detalle", f"Mostrando detalle para fila {row + 1}")

    # === MÉTODOS DE PAGINACIÓN ===
