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

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
)

from rexus.utils.message_system import show_warning, show_error, show_success
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusColors,
)

# Importar utilidades de sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from rexus.utils.xss_protection import FormProtector, XSSProtection
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager


class MantenimientoView(QWidget):
    """Vista principal del módulo de mantenimiento."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Panel de control estandarizado
        control_panel = StandardComponents.create_control_panel()
        self.setup_control_panel(control_panel)
        layout.addWidget(control_panel)

        # Tabla estandarizada
        self.tabla_principal = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_principal)

        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)

        # Aplicar estilos después de crear la interfaz
        self.aplicar_estilos()

        # Inicializar protección XSS
        self.init_xss_protection()

    def aplicar_estilos(self):
        """Aplica estilos minimalistas y modernos a toda la interfaz."""
        self.setStyleSheet("""
            /* Estilo general del widget */
            QWidget {
                background-color: #fafbfc;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            /* Pestañas minimalistas */
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: white;
                margin-top: 2px;
            }
            
            QTabBar::tab {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 11px;
                color: #586069;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #24292e;
                font-weight: 500;
                border-bottom: 2px solid #0366d6;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e1e4e8;
                color: #24292e;
            }
            
            /* Tablas compactas */
            QTableWidget {
                gridline-color: #e1e4e8;
                selection-background-color: #f1f8ff;
                selection-color: #24292e;
                alternate-background-color: #f6f8fa;
                font-size: 11px;
                border: 1px solid #e1e4e8;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            
            QHeaderView::section {
                background-color: #f6f8fa;
                color: #586069;
                font-weight: 600;
                font-size: 10px;
                border: none;
                border-right: 1px solid #e1e4e8;
                border-bottom: 1px solid #e1e4e8;
                padding: 6px 8px;
            }
            
            /* GroupBox minimalista */
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
            
            /* Botones minimalistas */
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }
            
            QPushButton:pressed {
                background-color: #d0d7de;
            }
            
            /* Campos de entrada compactos */
            QLineEdit, QComboBox {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: white;
                min-height: 18px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #0366d6;
                outline: none;
            }
            
            /* Labels compactos */
            QLabel {
                color: #24292e;
                font-size: 11px;
            }
            
            /* Scroll bars minimalistas */
            QScrollBar:vertical {
                width: 12px;
                background-color: #f6f8fa;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #d0d7de;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #bbb;
            }
        """)

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, "input_busqueda"):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")

        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Botón Nuevo estandarizado
        self.btn_nuevo = StandardComponents.create_primary_button("🔧 Nuevo Mantenimiento")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Botón buscar estandarizado
        self.btn_buscar = StandardComponents.create_secondary_button("🔍 Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_secondary_button("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

    def configurar_tabla(self):
        """Configura la tabla principal."""
        self.tabla_principal.setColumnCount(5)
        self.tabla_principal.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Descripción", "Estado", "Acciones"]
        )

        # Configurar encabezados
        header = self.tabla_principal.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.tabla_principal.setAlternatingRowColors(True)
        self.tabla_principal.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet("""
            QWidget {
            background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
            background-color: #6f42c1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
            opacity: 0.8;
            }
            QLineEdit, QComboBox {
            border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QTableWidget {
            background-color: white;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo mantenimiento."""
        dialog = NuevoMantenimientoDialog(self)
        if dialog.exec() == dialog.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                resultado = self.controller.crear_mantenimiento(datos)
                if resultado:  # Éxito (devuelve ID)
                    show_success(self, "Mantenimiento Creado", f"Mantenimiento creado con ID: {resultado}")
                    self.actualizar_datos()
                else:  # Error
                    show_error(self, "Error", "No se pudo crear el mantenimiento")

    def buscar(self):
        """Busca registros según los criterios especificados."""
        if self.controller:
            filtros = {"busqueda": self.input_busqueda.text()}
            self.controller.buscar(filtros)

    def actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.controller.cargar_datos()

    def cargar_datos_en_tabla(self, datos):
        """Carga los datos en la tabla."""
        self.tabla_principal.setRowCount(len(datos))

        for row, registro in enumerate(datos):
            self.tabla_principal.setItem(
                row, 0, QTableWidgetItem(str(registro.get("id", "")))
            )
            self.tabla_principal.setItem(
                row, 1, QTableWidgetItem(str(registro.get("nombre", "")))
            )
            self.tabla_principal.setItem(
                row, 2, QTableWidgetItem(str(registro.get("descripcion", "")))
            )
            self.tabla_principal.setItem(
                row, 3, QTableWidgetItem(str(registro.get("estado", "")))
            )

            # Botón de acciones
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("background-color: #ffc107; color: #212529;")
            self.tabla_principal.setCellWidget(row, 4, btn_editar)

    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, "form_protector") and self.form_protector:
            return self.form_protector.get_sanitized_data()
        else:
            # Fallback manual
            datos = {}
            if hasattr(self, "input_busqueda"):
                datos["busqueda"] = XSSProtection.sanitize_text(
                    self.input_busqueda.text()
                )
            return datos

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class NuevoMantenimientoDialog(QDialog):
    """Diálogo para crear un nuevo mantenimiento."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Mantenimiento")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setupUI()
        
    def setupUI(self):
        """Configura la interfaz del diálogo."""
        from PyQt6.QtCore import QDate
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = RexusLabel("Crear Nuevo Mantenimiento", "title")
        layout.addWidget(titulo)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Equipo ID (obligatorio)
        self.equipo_id_input = QSpinBox()
        self.equipo_id_input.setRange(1, 999999)
        self.equipo_id_input.setValue(1)
        form_layout.addRow("ID del Equipo*:", self.equipo_id_input)
        
        # Tipo de mantenimiento
        self.tipo_input = RexusComboBox()
        self.tipo_input.addItems([
            "PREVENTIVO",
            "CORRECTIVO",
            "PREDICTIVO",
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
