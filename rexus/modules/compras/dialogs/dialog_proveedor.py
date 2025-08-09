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

Diálogo de Gestión de Proveedores
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QLineEdit, QComboBox, QTextEdit, QLabel, QGroupBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt

from rexus.ui.components.base_components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox, RexusGroupBox
)
from rexus.ui.standard_components import StandardComponents
from rexus.utils.form_validators import FormValidator, FormValidatorManager
from rexus.utils.xss_protection import XSSProtection
from rexus.utils.message_system import show_error
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class DialogProveedor(QDialog):
    """Diálogo para crear/editar proveedores."""

    def __init__(self, parent=None, proveedor_data=None):
        super().__init__(parent)
        self.proveedor_data = proveedor_data
        self.validator_manager = FormValidatorManager()
        
        self.setWindowTitle("Nuevo Proveedor" if not proveedor_data else "Editar Proveedor")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.init_ui()
        self.configurar_validaciones()
        
        if proveedor_data:
            self.cargar_datos(proveedor_data)

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Crear pestañas
        tab_widget = QTabWidget()
        
        # Pestaña de información básica
        tab_basica = self.crear_tab_informacion_basica()
        tab_widget.addTab(tab_basica, "📋 Información Básica")
        
        # Pestaña de contacto
        tab_contacto = self.crear_tab_contacto()
        tab_widget.addTab(tab_contacto, "📞 Contacto")
        
        # Pestaña de detalles adicionales
        tab_detalles = self.crear_tab_detalles()
        tab_widget.addTab(tab_detalles, "[CHART] Detalles")
        
        layout.addWidget(tab_widget)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def crear_tab_informacion_basica(self):
        """Crea la pestaña de información básica."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información principal
        grupo_principal = RexusGroupBox("📋 Información Principal")
        form_layout = QFormLayout(grupo_principal)
        
        # Campos principales
        self.input_nombre = RexusLineEdit("Nombre del proveedor...")
        self.input_nombre.setObjectName("nombre")
        form_layout.addRow("* Nombre:", self.input_nombre)
        
        self.input_razon_social = RexusLineEdit("Razón social...")
        self.input_razon_social.setObjectName("razon_social")
        form_layout.addRow("Razón Social:", self.input_razon_social)
        
        self.input_ruc = RexusLineEdit("RUC o identificación fiscal...")
        self.input_ruc.setObjectName("ruc")
        form_layout.addRow("* RUC/DNI:", self.input_ruc)
        
        # Estado del proveedor
        self.combo_estado = RexusComboBox(["ACTIVO", "INACTIVO", "BLOQUEADO"])
        self.combo_estado.setObjectName("estado")
        form_layout.addRow("Estado:", self.combo_estado)
        
        # Categoría
        self.combo_categoria = RexusComboBox([
            "GENERAL", "FERRETERÍA", "VIDRIOS", "HERRAJES", 
            "MATERIALES", "SERVICIOS", "EQUIPOS"
        ])
        self.combo_categoria.setObjectName("categoria")
        form_layout.addRow("Categoría:", self.combo_categoria)
        
        layout.addWidget(grupo_principal)
        
        # Información fiscal
        grupo_fiscal = RexusGroupBox("💰 Información Fiscal")
        fiscal_layout = QFormLayout(grupo_fiscal)
        
        self.combo_condicion_iva = RexusComboBox([
            "RESPONSABLE_INSCRIPTO", "MONOTRIBUTO", "EXENTO", "CONSUMIDOR_FINAL"
        ])
        fiscal_layout.addRow("Condición IVA:", self.combo_condicion_iva)
        
        self.input_cuit = RexusLineEdit("CUIT...")
        fiscal_layout.addRow("CUIT:", self.input_cuit)
        
        layout.addWidget(grupo_fiscal)
        layout.addStretch()
        
        return widget

    def crear_tab_contacto(self):
        """Crea la pestaña de información de contacto."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información de contacto
        grupo_contacto = RexusGroupBox("📞 Información de Contacto")
        form_layout = QFormLayout(grupo_contacto)
        
        self.input_telefono = RexusLineEdit("Teléfono principal...")
        self.input_telefono.setObjectName("telefono")
        form_layout.addRow("* Teléfono:", self.input_telefono)
        
        self.input_telefono_secundario = RexusLineEdit("Teléfono secundario...")
        form_layout.addRow("Teléfono 2:", self.input_telefono_secundario)
        
        self.input_email = RexusLineEdit("email@proveedor.com")
        self.input_email.setObjectName("email")
        form_layout.addRow("* Email:", self.input_email)
        
        self.input_website = RexusLineEdit("https://www.proveedor.com")
        form_layout.addRow("Sitio Web:", self.input_website)
        
        layout.addWidget(grupo_contacto)
        
        # Dirección
        grupo_direccion = RexusGroupBox("📍 Dirección")
        direccion_layout = QFormLayout(grupo_direccion)
        
        self.input_direccion = QTextEdit()
        self.input_direccion.setMaximumHeight(80)
        self.input_direccion.setObjectName("direccion")
        direccion_layout.addRow("* Dirección:", self.input_direccion)
        
        # Dirección en una línea (para layouts horizontales)
        direccion_datos = QHBoxLayout()
        
        self.input_ciudad = RexusLineEdit("Ciudad...")
        direccion_datos.addWidget(QLabel("Ciudad:"))
        direccion_datos.addWidget(self.input_ciudad)
        
        self.input_provincia = RexusLineEdit("Provincia...")
        direccion_datos.addWidget(QLabel("Provincia:"))
        direccion_datos.addWidget(self.input_provincia)
        
        self.input_codigo_postal = RexusLineEdit("CP...")
        direccion_datos.addWidget(QLabel("CP:"))
        direccion_datos.addWidget(self.input_codigo_postal)
        
        direccion_widget = QWidget()
        direccion_widget.setLayout(direccion_datos)
        direccion_layout.addRow("Ubicación:", direccion_widget)
        
        layout.addWidget(grupo_direccion)
        layout.addStretch()
        
        return widget

    def crear_tab_detalles(self):
        """Crea la pestaña de detalles adicionales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Contacto principal
        grupo_contacto_principal = RexusGroupBox("👤 Contacto Principal")
        contacto_layout = QFormLayout(grupo_contacto_principal)
        
        self.input_contacto_nombre = RexusLineEdit("Nombre del contacto...")
        contacto_layout.addRow("Nombre:", self.input_contacto_nombre)
        
        self.input_contacto_cargo = RexusLineEdit("Cargo...")
        contacto_layout.addRow("Cargo:", self.input_contacto_cargo)
        
        self.input_contacto_telefono = RexusLineEdit("Teléfono directo...")
        contacto_layout.addRow("Teléfono:", self.input_contacto_telefono)
        
        self.input_contacto_email = RexusLineEdit("email@contacto.com")
        contacto_layout.addRow("Email:", self.input_contacto_email)
        
        layout.addWidget(grupo_contacto_principal)
        
        # Términos comerciales
        grupo_comercial = RexusGroupBox("💼 Términos Comerciales")
        comercial_layout = QFormLayout(grupo_comercial)
        
        self.combo_forma_pago = RexusComboBox([
            "CONTADO", "30_DIAS", "60_DIAS", "90_DIAS", "PERSONALIZADO"
        ])
        comercial_layout.addRow("Forma de Pago:", self.combo_forma_pago)
        
        self.combo_moneda = RexusComboBox(["ARS", "USD", "EUR"])
        comercial_layout.addRow("Moneda:", self.combo_moneda)
        
        self.input_descuento_maximo = RexusLineEdit("0.00")
        comercial_layout.addRow("Descuento Máximo %:", self.input_descuento_maximo)
        
        layout.addWidget(grupo_comercial)
        
        # Observaciones
        grupo_observaciones = RexusGroupBox("📝 Observaciones")
        obs_layout = QVBoxLayout(grupo_observaciones)
        
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setMaximumHeight(100)
        self.input_observaciones.setPlaceholderText(
            "Observaciones, notas especiales, condiciones particulares..."
        )
        self.input_observaciones.setObjectName("observaciones")
        obs_layout.addWidget(self.input_observaciones)
        
        layout.addWidget(grupo_observaciones)
        layout.addStretch()
        
        return widget

    def configurar_validaciones(self):
        """Configura las validaciones del formulario."""
        # Validaciones de campos obligatorios
        self.validator_manager.agregar_validacion(
            self.input_nombre,
            FormValidator.validar_campo_obligatorio,
            "Nombre del proveedor"
        )
        self.validator_manager.agregar_validacion(
            self.input_nombre,
            FormValidator.validar_longitud_texto,
            2, 100
        )
        
        self.validator_manager.agregar_validacion(
            self.input_ruc,
            FormValidator.validar_campo_obligatorio,
            "RUC/DNI"
        )
        self.validator_manager.agregar_validacion(
            self.input_ruc,
            FormValidator.validar_longitud_texto,
            8, 20
        )
        
        self.validator_manager.agregar_validacion(
            self.input_telefono,
            FormValidator.validar_campo_obligatorio,
            "Teléfono"
        )
        
        # Validación de email
        self.validator_manager.agregar_validacion(
            self.input_email,
            FormValidator.validar_email
        )
        
        # Validación de dirección
        self.validator_manager.agregar_validacion(
            self.input_direccion,
            FormValidator.validar_campo_obligatorio,
            "Dirección"
        )

    def validar_y_aceptar(self):
        """Valida los datos y acepta el diálogo."""
        # Validar formulario
        es_valido, errores = self.validator_manager.validar_formulario()
        
        if not es_valido:
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            show_error(
                self,
                "Errores de Validación",
                "Por favor corrige los siguientes errores:\n\n• " + "\n• ".join(mensajes_error)
            )
            return
        
        # Validaciones adicionales personalizadas
        if not self._validaciones_adicionales():
            return
        
        self.accept()

    def _validaciones_adicionales(self):
        """Validaciones adicionales específicas del negocio."""
        # Validar RUC/DNI único (solo para nuevos proveedores)
        if not self.proveedor_data:
            ruc = self.input_ruc.text().strip()
            if len(ruc) < 8:
                show_error(self, "Error de Validación", 
                          "El RUC/DNI debe tener al menos 8 caracteres")
                return False
        
        # Validar formato de email si está presente
        email = self.input_email.text().strip()
        if email and "@" not in email:
            show_error(self, "Error de Validación", 
                      "El formato del email no es válido")
            return False
        
        return True

    def obtener_datos(self):
        """Obtiene los datos del formulario con sanitización XSS."""
        return {
            # Información básica
            "nombre": XSSProtection.sanitize_text(self.input_nombre.text()),
            "razon_social": XSSProtection.sanitize_text(self.input_razon_social.text()),
            "ruc": XSSProtection.sanitize_text(self.input_ruc.text()),
            "estado": self.combo_estado.currentText(),
            "categoria": self.combo_categoria.currentText(),
            
            # Información fiscal
            "condicion_iva": self.combo_condicion_iva.currentText(),
            "cuit": XSSProtection.sanitize_text(self.input_cuit.text()),
            
            # Contacto
            "telefono": XSSProtection.sanitize_text(self.input_telefono.text()),
            "telefono_secundario": XSSProtection.sanitize_text(self.input_telefono_secundario.text()),
            "email": XSSProtection.sanitize_text(self.input_email.text()),
            "website": XSSProtection.sanitize_text(self.input_website.text()),
            
            # Dirección
            "direccion": XSSProtection.sanitize_text(self.input_direccion.toPlainText()),
            "ciudad": XSSProtection.sanitize_text(self.input_ciudad.text()),
            "provincia": XSSProtection.sanitize_text(self.input_provincia.text()),
            "codigo_postal": XSSProtection.sanitize_text(self.input_codigo_postal.text()),
            
            # Contacto principal
            "contacto_nombre": XSSProtection.sanitize_text(self.input_contacto_nombre.text()),
            "contacto_cargo": XSSProtection.sanitize_text(self.input_contacto_cargo.text()),
            "contacto_telefono": XSSProtection.sanitize_text(self.input_contacto_telefono.text()),
            "contacto_email": XSSProtection.sanitize_text(self.input_contacto_email.text()),
            
            # Términos comerciales
            "forma_pago": self.combo_forma_pago.currentText(),
            "moneda": self.combo_moneda.currentText(),
            "descuento_maximo": float(self.input_descuento_maximo.text() or "0"),
            
            # Observaciones
            "observaciones": XSSProtection.sanitize_text(self.input_observaciones.toPlainText()),
        }

    def cargar_datos(self, datos):
        """Carga datos existentes en el formulario."""
        # Información básica
        self.input_nombre.setText(datos.get("nombre", ""))
        self.input_razon_social.setText(datos.get("razon_social", ""))
        self.input_ruc.setText(datos.get("ruc", ""))
        
        estado = datos.get("estado", "ACTIVO")
        if estado in ["ACTIVO", "INACTIVO", "BLOQUEADO"]:
            self.combo_estado.setCurrentText(estado)
        
        categoria = datos.get("categoria", "GENERAL")
        index = self.combo_categoria.findText(categoria)
        if index >= 0:
            self.combo_categoria.setCurrentIndex(index)
        
        # Información fiscal
        self.input_cuit.setText(datos.get("cuit", ""))
        
        # Contacto
        self.input_telefono.setText(datos.get("telefono", ""))
        self.input_telefono_secundario.setText(datos.get("telefono_secundario", ""))
        self.input_email.setText(datos.get("email", ""))
        self.input_website.setText(datos.get("website", ""))
        
        # Dirección
        self.input_direccion.setPlainText(datos.get("direccion", ""))
        self.input_ciudad.setText(datos.get("ciudad", ""))
        self.input_provincia.setText(datos.get("provincia", ""))
        self.input_codigo_postal.setText(datos.get("codigo_postal", ""))
        
        # Contacto principal
        self.input_contacto_nombre.setText(datos.get("contacto_nombre", ""))
        self.input_contacto_cargo.setText(datos.get("contacto_cargo", ""))
        self.input_contacto_telefono.setText(datos.get("contacto_telefono", ""))
        self.input_contacto_email.setText(datos.get("contacto_email", ""))
        
        # Términos comerciales
        forma_pago = datos.get("forma_pago", "CONTADO")
        index = self.combo_forma_pago.findText(forma_pago)
        if index >= 0:
            self.combo_forma_pago.setCurrentIndex(index)
        
        moneda = datos.get("moneda", "ARS")
        index = self.combo_moneda.findText(moneda)
        if index >= 0:
            self.combo_moneda.setCurrentIndex(index)
        
        self.input_descuento_maximo.setText(str(datos.get("descuento_maximo", 0)))
        
        # Observaciones
        self.input_observaciones.setPlainText(datos.get("observaciones", ""))