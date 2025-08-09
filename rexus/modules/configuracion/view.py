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

Vista de Configuracion - Interfaz de configuración
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QDialogButtonBox,
)

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusGroupBox,
    RexusFrame,
    RexusLayoutHelper
)

from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import XSSProtection, FormProtector
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class ConfiguracionView(QWidget):
    """Vista principal del módulo de configuracion."""
    
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
            if hasattr(self, 'input_busqueda'):
                self.form_protector.protect_field(self.input_busqueda, 'busqueda')
                
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
        self.tabla_principal.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Estado", "Acciones"
        ])
        
        # Configurar encabezados
        header = self.tabla_principal.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        
        self.tabla_principal.setAlternatingRowColors(True)
        self.tabla_principal.setSelectionBehavior(RexusTable.SelectionBehavior.SelectRows)
    
    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet(f"""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #495057;
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
        dialogo = DialogoConfiguracion(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            if dialogo.validar_datos():
                datos = dialogo.obtener_datos()
                
                if self.controller:
                    # Intentar crear la configuración a través del controlador
                    try:
                        exito = self.controller.crear_configuracion(datos)
                        if exito:
                            show_success(self, "Éxito", "Configuración creada exitosamente.")
                            self.actualizar_datos()
                        else:
                            show_error(self, "Error", "No se pudo crear la configuración.")
                    except Exception as e:
                        show_error(self, "Error", f"Error al crear configuración: {str(e)}")
                else:
                    show_warning(self, "Advertencia", "No hay controlador disponible.")
            else:
                # La validación ya mostró el error, no hacer nada
                pass
    
    def buscar(self):
        """Busca registros según los criterios especificados."""
        if self.controller:
            filtros = {'busqueda': self.input_busqueda.text()}
            self.controller.buscar(filtros)
    
    def actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.controller.cargar_datos()
    
    def cargar_datos_en_tabla(self, datos):
        """Carga los datos en la tabla."""
        self.tabla_principal.setRowCount(len(datos))
        
        for row, registro in enumerate(datos):
            self.tabla_principal.setItem(row, 0, QTableWidgetItem(str(registro.get("id", ""))))
            self.tabla_principal.setItem(row, 1, QTableWidgetItem(str(registro.get("nombre", ""))))
            self.tabla_principal.setItem(row, 2, QTableWidgetItem(str(registro.get("descripcion", ""))))
            self.tabla_principal.setItem(row, 3, QTableWidgetItem(str(registro.get("estado", ""))))
            
            # Botón de acciones
            btn_editar = RexusButton("Editar")
            btn_editar.setStyleSheet("background-color: #ffc107; color: #212529;")
            self.tabla_principal.setCellWidget(row, 4, btn_editar)
    
    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, 'form_protector') and self.form_protector:
            return self.form_protector.get_sanitized_data()
        else:
            # Fallback manual
            datos = {}
            if hasattr(self, 'input_busqueda'):
                datos['busqueda'] = XSSProtection.sanitize_text(self.input_busqueda.text())
            return datos
    
    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoConfiguracion(QDialog):
    """Diálogo para crear/editar configuraciones."""
    
    def __init__(self, parent=None, configuracion=None):
        super().__init__(parent)
        self.configuracion = configuracion
        self.init_ui()
        
        if configuracion:
            self.cargar_datos(configuracion)
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nueva Configuración" if not self.configuracion else "Editar Configuración")
        self.setModal(True)
        self.resize(400, 350)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.input_clave = RexusLineEdit()
        self.input_clave.setPlaceholderText("Clave de configuración")
        form_layout.addRow("Clave:", self.input_clave)
        
        self.input_valor = RexusLineEdit()
        self.input_valor.setPlaceholderText("Valor de configuración")
        form_layout.addRow("Valor:", self.input_valor)
        
        self.combo_tipo = RexusComboBox()
        self.combo_tipo.addItems(["Texto", "Número", "Booleano", "JSON"])
        form_layout.addRow("Tipo:", self.combo_tipo)
        
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción de la configuración")
        self.input_descripcion.setMaximumHeight(80)
        form_layout.addRow("Descripción:", self.input_descripcion)
        
        self.combo_categoria = RexusComboBox()
        self.combo_categoria.addItems(["Sistema", "Usuario", "Base de Datos", "Interfaz", "Seguridad"])
        form_layout.addRow("Categoría:", self.combo_categoria)
        
        self.check_activo = QCheckBox("Configuración activa")
        self.check_activo.setChecked(True)
        form_layout.addRow("Estado:", self.check_activo)
        
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
            QCheckBox {
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
    
    def cargar_datos(self, configuracion):
        """Carga los datos de una configuración existente."""
        self.input_clave.setText(configuracion.get("clave", ""))
        self.input_valor.setText(configuracion.get("valor", ""))
        self.input_descripcion.setPlainText(configuracion.get("descripcion", ""))
        
        # Cargar tipo
        tipo = configuracion.get("tipo", "Texto")
        index = self.combo_tipo.findText(tipo)
        if index >= 0:
            self.combo_tipo.setCurrentIndex(index)
        
        # Cargar categoría
        categoria = configuracion.get("categoria", "Sistema")
        index = self.combo_categoria.findText(categoria)
        if index >= 0:
            self.combo_categoria.setCurrentIndex(index)
        
        self.check_activo.setChecked(configuracion.get("activo", True))
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "clave": self.input_clave.text().strip(),
            "valor": self.input_valor.text().strip(),
            "tipo": self.combo_tipo.currentText(),
            "descripcion": self.input_descripcion.toPlainText().strip(),
            "categoria": self.combo_categoria.currentText(),
            "activo": self.check_activo.isChecked()
        }
    
    def validar_datos(self):
        """Valida los datos del formulario."""
        datos = self.obtener_datos()
        
        if not datos["clave"]:
            show_error(self, "Error de Validación", "La clave es obligatoria.")
            return False
        
        if not datos["valor"]:
            show_error(self, "Error de Validación", "El valor es obligatorio.")
            return False
        
        # Validar formato según tipo
        if datos["tipo"] == "Número":
            try:
                float(datos["valor"])
            except ValueError:
                show_error(self, "Error de Validación", "El valor debe ser un número válido.")
                return False
        
        elif datos["tipo"] == "Booleano":
            if datos["valor"].lower() not in ["true", "false", "1", "0", "si", "no"]:
                show_error(self, "Error de Validación", "El valor booleano debe ser: true/false, 1/0, si/no.")
                return False
        
        elif datos["tipo"] == "JSON":
            try:
                import json
                json.loads(datos["valor"])
            except json.JSONDecodeError:
                show_error(self, "Error de Validación", "El valor debe ser un JSON válido.")
                return False
        
        return True
