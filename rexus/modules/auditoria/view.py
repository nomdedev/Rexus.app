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

Vista de Auditoria - Interfaz de auditoría
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QTextEdit,
    QDateTimeEdit,
    QDialogButtonBox,
)

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusFrame,
    RexusGroupBox,
    RexusLayoutHelper
)

from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import FormProtector, XSSProtection
from rexus.ui.templates.base_module_view import BaseModuleView


class AuditoriaView(BaseModuleView):
    """Vista principal del módulo de auditoria."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__(module_name="Auditoría")
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Tabla principal
        self.tabla_principal = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_principal)

        # Aplicar estilo
        self.aplicar_estilo()

        # Inicializar protección XSS
        self.init_xss_protection()

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, "input_busqueda"):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")

        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def crear_panel_control(self):
        """Crea el panel de control superior."""
        panel = RexusFrame()
        panel.setFrameStyle(RexusFrame.Shape.Box)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón Nuevo
        self.btn_nuevo = RexusButton("Nuevo")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Botón buscar
        self.btn_buscar = RexusButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar
        self.btn_actualizar = RexusButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

        return panel

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
            RexusTable.SelectionBehavior.SelectRows
        )

    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet("""
            QWidget {
            background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
            background-color: #e83e8c;
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
        """Abre el diálogo para crear un nuevo registro."""
        dialogo = DialogoAuditoria(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            if dialogo.validar_datos():
                datos = dialogo.obtener_datos()
                
                if self.controller:
                    try:
                        exito = self.controller.crear_registro_auditoria(datos)
                        if exito:
                            show_success(self, "Éxito", "Registro de auditoría creado exitosamente.")
                            self.actualizar_datos()
                        else:
                            show_error(self, "Error", "No se pudo crear el registro de auditoría.")
                    except Exception as e:
                        show_error(self, "Error", f"Error al crear registro: {str(e)}")
                else:
                    show_warning(self, "Advertencia", "No hay controlador disponible.")

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
            btn_editar = RexusButton("Editar")
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
    
    def actualizar_registros(self):
        """
        Actualiza los registros mostrados en la vista.
        Sobrescribe el método base para cargar datos específicos de auditoría.
        """
        try:
            if hasattr(self, 'controller') and self.controller:
                # Si tenemos controlador, delegar la carga de datos
                if hasattr(self.controller, '_cargar_datos_iniciales'):
                    self.controller._cargar_datos_iniciales()
                else:
                    print("[AUDITORÍA] Controlador sin método _cargar_datos_iniciales")
            else:
                # Sin controlador, cargar datos dummy o desde modelo directo
                print("[AUDITORÍA] Actualizando registros sin controlador")
                self.cargar_datos_en_tabla([])  # Datos vacíos por ahora
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error actualizando registros: {e}")
            self.mostrar_error(f"Error cargando registros: {e}")
    
    def cargar_registros_auditoría(self, registros):
        """
        Carga registros específicos de auditoría en la tabla.
        Método adicional para uso del controlador.
        
        Args:
            registros (list): Lista de registros de auditoría
        """
        try:
            self.cargar_datos_en_tabla(registros)
            print(f"[AUDITORÍA] {len(registros)} registros cargados en la tabla")
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error cargando registros de auditoría: {e}")
            self.mostrar_error(f"Error cargando registros: {e}")
    
    def actualizar_estadisticas(self, estadisticas):
        """
        Actualiza las estadísticas mostradas en la vista.
        
        Args:
            estadisticas (dict): Diccionario con estadísticas de auditoría
        """
        try:
            # Si hay un panel de estadísticas, actualizarlo
            if hasattr(self, 'label_estadisticas'):
                total = estadisticas.get('total', 0)
                criticos = estadisticas.get('criticos', 0)
                advertencias = estadisticas.get('advertencias', 0)
                
                texto = f"Total: {total} | Críticos: {criticos} | Advertencias: {advertencias}"
                self.label_estadisticas.setText(texto)
                print(f"[AUDITORÍA] Estadísticas actualizadas: {texto}")
            else:
                print(f"[AUDITORÍA] Estadísticas recibidas: {estadisticas}")
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error actualizando estadísticas: {e}")


class DialogoAuditoria(QDialog):
    """Diálogo para crear registros de auditoría manual."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nuevo Registro de Auditoría")
        self.setModal(True)
        self.resize(450, 400)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.input_modulo = RexusComboBox()
        self.input_modulo.addItems([
            "Sistema", "Usuarios", "Inventario", "Obras", "Herrajes", 
            "Vidrios", "Mantenimiento", "Configuración", "Auditoría",
            "Compras", "Pedidos", "Administración"
        ])
        form_layout.addRow("Módulo:", self.input_modulo)
        
        self.input_accion = RexusComboBox()
        self.input_accion.addItems([
            "CREAR", "LEER", "ACTUALIZAR", "ELIMINAR", "LOGIN", 
            "LOGOUT", "EXPORTAR", "IMPORTAR", "BACKUP", "CONFIGURAR"
        ])
        form_layout.addRow("Acción:", self.input_accion)
        
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción detallada de la acción realizada")
        self.input_descripcion.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.input_descripcion)
        
        self.input_tabla_afectada = RexusLineEdit()
        self.input_tabla_afectada.setPlaceholderText("Tabla o entidad afectada")
        form_layout.addRow("Tabla Afectada:", self.input_tabla_afectada)
        
        self.input_criticidad = RexusComboBox()
        self.input_criticidad.addItems(["BAJA", "MEDIA", "ALTA", "CRÍTICA"])
        self.input_criticidad.setCurrentText("MEDIA")
        form_layout.addRow("Criticidad:", self.input_criticidad)
        
        self.input_resultado = RexusComboBox()
        self.input_resultado.addItems(["EXITOSO", "FALLIDO", "PARCIAL"])
        self.input_resultado.setCurrentText("EXITOSO")
        form_layout.addRow("Resultado:", self.input_resultado)
        
        self.input_ip_origen = RexusLineEdit()
        self.input_ip_origen.setPlaceholderText("IP de origen (opcional)")
        form_layout.addRow("IP Origen:", self.input_ip_origen)
        
        self.input_detalles = QTextEdit()
        self.input_detalles.setPlaceholderText("Detalles adicionales o contexto")
        self.input_detalles.setMaximumHeight(80)
        form_layout.addRow("Detalles:", self.input_detalles)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Aplicar estilo
        self.aplicar_estilo()
    
    def aplicar_estilo(self):
        """Aplica estilo al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "modulo": self.input_modulo.currentText(),
            "accion": self.input_accion.currentText(),
            "descripcion": self.input_descripcion.toPlainText().strip(),
            "tabla_afectada": self.input_tabla_afectada.text().strip(),
            "nivel_criticidad": self.input_criticidad.currentText(),
            "resultado": self.input_resultado.currentText(),
            "ip_origen": self.input_ip_origen.text().strip(),
            "detalles": self.input_detalles.toPlainText().strip()
        }
    
    def validar_datos(self):
        """Valida los datos del formulario."""
        datos = self.obtener_datos()
        
        if not datos["descripcion"]:
            show_error(self, "Error de Validación", "La descripción es obligatoria.")
            return False
        
        if len(datos["descripcion"]) < 10:
            show_error(self, "Error de Validación", "La descripción debe tener al menos 10 caracteres.")
            return False
        
        return True

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
