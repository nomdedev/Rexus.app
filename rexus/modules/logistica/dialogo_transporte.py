"""
MIT License

Copyright (c) 2024 Rexus.app

Diálogo para crear/editar transportes en el módulo de Logística
Implementación minimalista con el estilo visual del módulo
"""

import logging
from typing import Dict, Optional

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QDateEdit, QSpinBox, QWidget
)

from rexus.ui.components.base_components import (
    RexusButton, RexusLineEdit, RexusComboBox, RexusGroupBox
)
from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.message_system import show_error


class DialogoNuevoTransporte(QDialog):
    """Diálogo moderno y minimalista para crear/editar transportes."""

    def __init__(self, parent=None, transporte_id: Optional[str] = None):
        super().__init__(parent)
        self.transporte_id = transporte_id
        self.es_edicion = transporte_id is not None
        self.init_ui()
        self.configurar_validaciones()

        if self.es_edicion and self.transporte_id is not None:
            self.cargar_datos_transporte(self.transporte_id)

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Configuración básica de la ventana
        titulo = "Editar Transporte" if self.es_edicion else "Nuevo Transporte"
        self.setWindowTitle(titulo)
        self.setFixedSize(480, 620)
        self.setModal(True)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título del diálogo
        self.crear_titulo(layout, titulo)

        # Formulario principal
        self.crear_formulario(layout)

        # Botones de acción
        self.crear_botones(layout)

        # Aplicar estilos minimalistas
        self.aplicar_estilos()

    def crear_titulo(self, layout: QVBoxLayout, titulo: str):
        """Crea el título del diálogo."""
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0;
                border-bottom: 2px solid #e1e4e8;
                margin-bottom: 10px;
            }
        """)
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo_label)

    def crear_formulario(self, layout: QVBoxLayout):
        """Crea el formulario de datos."""
        # Grupo de información básica
        grupo_basico = RexusGroupBox("Información del Transporte")
        form_layout = QFormLayout(grupo_basico)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 20, 15, 15)

        # Campo Origen
        self.input_origen = RexusLineEdit()
        self.input_origen.setPlaceholderText("Dirección de origen...")
        form_layout.addRow("Origen:", self.input_origen)

        # Campo Destino
        self.input_destino = RexusLineEdit()
        self.input_destino.setPlaceholderText("Dirección de destino...")
        form_layout.addRow("Destino:", self.input_destino)

        # Campo Estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems([
            "Pendiente", "En tránsito", "Entregado", "Cancelado"
        ])
        form_layout.addRow("Estado:", self.combo_estado)

        # Campo Conductor
        self.input_conductor = RexusLineEdit()
        self.input_conductor.setPlaceholderText("Nombre del conductor...")
        form_layout.addRow("Conductor:", self.input_conductor)

        # Campo Fecha
        self.input_fecha = QDateEdit()
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Fecha:", self.input_fecha)

        layout.addWidget(grupo_basico)

        # Grupo de información adicional
        grupo_adicional = RexusGroupBox("Información Adicional")
        form_layout2 = QFormLayout(grupo_adicional)
        form_layout2.setSpacing(12)
        form_layout2.setContentsMargins(15, 20, 15, 15)

        # Campo Vehículo
        self.input_vehiculo = RexusLineEdit()
        self.input_vehiculo.setPlaceholderText("Modelo/patente del vehículo...")
        form_layout2.addRow("Vehículo:", self.input_vehiculo)

        # Campo Prioridad
        self.combo_prioridad = RexusComboBox()
        self.combo_prioridad.addItems(["Normal", "Alta", "Urgente"])
        form_layout2.addRow("Prioridad:", self.combo_prioridad)

        # Campo Costo Estimado
        self.input_costo = QSpinBox()
        self.input_costo.setRange(0, 999999)
        self.input_costo.setSuffix(" $")
        self.input_costo.setValue(0)
        form_layout2.addRow("Costo:", self.input_costo)

        # Campo Observaciones
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales...")
        self.input_observaciones.setMaximumHeight(80)
        form_layout2.addRow("Observaciones:", self.input_observaciones)

        layout.addWidget(grupo_adicional)

    def crear_botones(self, layout: QVBoxLayout):
        """Crea los botones de acción."""
        botones_widget = QWidget()
        botones_layout = QHBoxLayout(botones_widget)
        botones_layout.setContentsMargins(0, 10, 0, 0)

        # Botón Cancelar
        self.btn_cancelar = RexusButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e1e4e8;
                color: #586069;
                font-weight: 500;
                padding: 8px 20px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }
        """)
        botones_layout.addWidget(self.btn_cancelar)

        botones_layout.addStretch()

        # Botón Guardar
        texto_guardar = "Actualizar" if self.es_edicion else "Guardar"
        self.btn_guardar = RexusButton(texto_guardar)
        self.btn_guardar.clicked.connect(self.validar_y_guardar)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        botones_layout.addWidget(self.btn_guardar)

        layout.addWidget(botones_widget)

    def aplicar_estilos(self):
        """Aplica estilos minimalistas al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafbfc;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }

            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
                background-color: white;
                min-height: 20px;
            }

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
                border-color: #0366d6;
                outline: none;
            }

            QTextEdit {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
                background-color: white;
            }

            QTextEdit:focus {
                border-color: #0366d6;
                outline: none;
            }

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

            QLabel {
                color: #24292e;
                font-size: 11px;
                font-weight: 500;
            }
        """)

    def configurar_validaciones(self):
        """Configura las validaciones de los campos."""
        # Validaciones en tiempo real (opcional)
        self.input_origen.textChanged.connect(self.validar_campos)
        self.input_destino.textChanged.connect(self.validar_campos)
        self.input_conductor.textChanged.connect(self.validar_campos)

    def validar_campos(self):
        """Valida los campos en tiempo real y habilita/deshabilita el botón guardar."""
        origen_valido = len(self.input_origen.text().strip()) >= 3
        destino_valido = len(self.input_destino.text().strip()) >= 3
        conductor_valido = len(self.input_conductor.text().strip()) >= 2

        campos_validos = origen_valido and destino_valido and conductor_valido
        self.btn_guardar.setEnabled(campos_validos)

        # Feedback visual opcional
        if not campos_validos:
            self.btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #6c757d;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 4px;
                    border: 1px solid #e1e4e8;
                    min-width: 100px;
                }
            """)
        else:
            self.btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 4px;
                    border: none;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)

    def validar_y_guardar(self):
        """Valida los datos y procede con el guardado."""
        try:
            # Validar campos obligatorios
            errores = []

            if len(self.input_origen.text().strip()) < 3:
                errores.append("El origen debe tener al menos 3 caracteres")

            if len(self.input_destino.text().strip()) < 3:
                errores.append("El destino debe tener al menos 3 caracteres")

            if len(self.input_conductor.text().strip()) < 2:
                errores.append("El conductor debe tener al menos 2 caracteres")

            # Validar que origen y destino no sean iguales
            if self.input_origen.text().strip().lower() == self.input_destino.text().strip().lower():
                errores.append("El origen y destino no pueden ser iguales")

            # Mostrar errores si los hay
            if errores:
                mensaje_error = "Por favor corrija los siguientes errores:\n\n" + "\n".join(f"• {error}" for error in errores)
                show_error(self, "Errores de validación", mensaje_error)
                return

            # Si todo está bien, aceptar el diálogo
            self.accept()

        except Exception as e:
            logging.error(f"Error en validación del diálogo: {e}")
            show_error(self, "Error", f"Error inesperado durante la validación: {str(e)}")

    def obtener_datos(self) -> Dict:
        """Obtiene los datos del formulario."""
        try:
            datos = {
                'origen': sanitize_string(self.input_origen.text().strip()),
                'destino': sanitize_string(self.input_destino.text().strip()),
                'estado': self.combo_estado.currentText(),
                'conductor': sanitize_string(self.input_conductor.text().strip()),
                'fecha': self.input_fecha.date().toString('yyyy-MM-dd'),
                'vehiculo': sanitize_string(self.input_vehiculo.text().strip()) or "No especificado",
                'prioridad': self.combo_prioridad.currentText(),
                'costo': self.input_costo.value(),
                'observaciones': sanitize_string(self.input_observaciones.toPlainText().strip()) or "Sin observaciones"
            }

            # Agregar ID si es edición
            if self.es_edicion and self.transporte_id:
                datos['id'] = self.transporte_id

            logging.info(f"Datos del transporte {'editado' if self.es_edicion else 'creado'}: {datos}")
            return datos

        except Exception as e:
            logging.error(f"Error obteniendo datos del diálogo: {e}")
            return {}

    def cargar_datos_transporte(self, transporte_id: str):
        """Carga los datos de un transporte existente para edición."""
        try:
            # Aquí se cargarían los datos desde la base de datos
            # Por ahora, datos de ejemplo para testing
            datos_ejemplo = {
                'origen': 'Buenos Aires, Argentina',
                'destino': 'La Plata, Argentina',
                'estado': 'En tránsito',
                'conductor': 'Juan Pérez',
                'fecha': '2025-08-10',
                'vehiculo': 'Ford Transit ABC123',
                'prioridad': 'Normal',
                'costo': 15000,
                'observaciones': 'Entrega programada para la mañana'
            }

            # Cargar datos en los campos
            self.input_origen.setText(datos_ejemplo['origen'])
            self.input_destino.setText(datos_ejemplo['destino'])

            # Seleccionar estado
            index = self.combo_estado.findText(datos_ejemplo['estado'])
            if index >= 0:
                self.combo_estado.setCurrentIndex(index)

            self.input_conductor.setText(datos_ejemplo['conductor'])

            # Configurar fecha
            fecha = QDate.fromString(datos_ejemplo['fecha'], 'yyyy-MM-dd')
            if fecha.isValid():
                self.input_fecha.setDate(fecha)

            self.input_vehiculo.setText(datos_ejemplo['vehiculo'])

            # Seleccionar prioridad
            index_prioridad = self.combo_prioridad.findText(datos_ejemplo['prioridad'])
            if index_prioridad >= 0:
                self.combo_prioridad.setCurrentIndex(index_prioridad)

            self.input_costo.setValue(datos_ejemplo['costo'])
            self.input_observaciones.setPlainText(datos_ejemplo['observaciones'])

            logging.info(f"Datos cargados para edición del transporte {transporte_id}")

        except Exception as e:
            logging.error(f"Error cargando datos del transporte {transporte_id}: {e}")
            show_error(self, "Error", f"No se pudieron cargar los datos del transporte: {str(e)}")
