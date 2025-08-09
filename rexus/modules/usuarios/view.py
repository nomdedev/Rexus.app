
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

Vista de Usuarios - Interfaz de gestión de usuarios y permisos
"""# XSS Protection Added
"""
Vista de Usuarios Modernizada

Interfaz moderna para la gestión de usuarios del sistema.
"""

import json
from datetime import datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QDateEdit,
    QTextEdit,
    QDialogButtonBox,
)

# Importar componentes del framework de estandarización UI
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusGroupBox,
    RexusFrame,
    RexusSpinBox,
    RexusColors,
    RexusFonts,
    RexusLayoutHelper
)
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.ui.templates.base_module_view import BaseModuleView

from rexus.modules.usuarios.improved_dialogs import (
    UsuarioDialogManager,
    UsuarioPasswordDialog,
    UsuarioPermisosDialog,
)
from rexus.utils.form_validators import FormValidator, FormValidatorManager
from rexus.utils.message_system import show_success, show_error, show_warning, ask_question
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import XSSProtection, FormProtector
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager


class UsuariosView(BaseModuleView):
    """Vista principal del módulo de usuarios."""
    
    # Señales
    solicitud_crear_usuario = pyqtSignal(dict)
    solicitud_actualizar_usuario = pyqtSignal(dict)
    solicitud_eliminar_usuario = pyqtSignal(str)
    
    def __init__(self):
        super().__init__("👥 Gestión de Usuarios")
        self.controller = None
        self.setup_usuarios_ui()
    
    def setup_usuarios_ui(self):
        """Configura la UI específica del módulo de usuarios."""
        # Configurar controles específicos
        self.setup_usuarios_controls()
        
        # Configurar tabla de usuarios
        self.setup_usuarios_table()
        
        # Aplicar tema del módulo
        self.apply_theme()
    
    def setup_usuarios_controls(self):
        """Configura los controles específicos del módulo de usuarios."""
        # Añadir controles al panel principal
        controls_layout = RexusLayoutHelper.create_horizontal_layout()
        
        # Botón Nuevo Usuario con componente Rexus
        self.btn_nuevo_usuario = RexusButton("👥 Nuevo Usuario", "primary")
        self.btn_nuevo_usuario.clicked.connect(self.nuevo_usuario)
        controls_layout.addWidget(self.btn_nuevo_usuario)
        
        # Campo de búsqueda con componente Rexus
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar usuario...")
        self.input_busqueda.returnPressed.connect(self.buscar_usuarios)
        controls_layout.addWidget(self.input_busqueda)
        
        # Botón buscar con componente Rexus
        self.btn_buscar = RexusButton("🔍 Buscar", "secondary")
        self.btn_buscar.clicked.connect(self.buscar_usuarios)
        controls_layout.addWidget(self.btn_buscar)
        
        # Botón actualizar con componente Rexus
        self.btn_actualizar = RexusButton("🔄 Actualizar", "secondary")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        controls_layout.addWidget(self.btn_actualizar)
        
        # Añadir controles al área principal
        self.add_to_main_content(controls_layout)
    
    def setup_usuarios_table(self):
        """Configura la tabla de usuarios con componentes Rexus."""
        # Crear tabla con componente Rexus
        self.tabla_usuarios = RexusTable()
        self.tabla_usuarios.setColumnCount(6)
        self.tabla_usuarios.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre", "Email", "Rol", "Estado"
        ])
        
        # Configurar encabezados
        header = self.tabla_usuarios.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        
        # Añadir tabla al contenido principal
        self.set_main_table(self.tabla_usuarios)
    
    def apply_theme(self):
        """Aplica el tema usando el sistema unificado de Rexus."""
        # Usar el sistema de temas de Rexus en lugar de CSS inline
        style_manager.apply_theme(self, "high_contrast")
        
        # Configuraciones específicas para el módulo de usuarios si es necesario
        self._apply_usuarios_specific_styling()

    def _apply_usuarios_specific_styling(self):
        """Aplica estilos específicos para el módulo de usuarios."""
        # Configuraciones específicas de estilos para usuarios
        # Por ejemplo, colores especiales para diferentes roles de usuario
        try:
            if hasattr(self, 'tabla_usuarios'):
                # Aplicar estilos específicos a la tabla de usuarios
                self.tabla_usuarios.setAlternatingRowColors(True)
                self.tabla_usuarios.setStyleSheet("""
                    QTableWidget::item:selected {
                        background-color: #4CAF50;
                        color: white;
                    }
                """)
        except Exception as e:
            print(f"[WARNING] Error aplicando estilos específicos de usuarios: {e}")
    
    def nuevo_usuario(self):
        """Abre el diálogo para crear un nuevo usuario."""
        dialogo = DialogoUsuario(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            if dialogo.validar_datos():
                datos = dialogo.obtener_datos()
                
                if self.controller:
                    try:
                        exito = self.controller.crear_usuario(datos)
                        if exito:
                            from rexus.utils.message_system import show_success
                            show_success(self, "Éxito", "Usuario creado exitosamente.")
                            self.actualizar_datos()
                        else:
                            from rexus.utils.message_system import show_error
                            show_error(self, "Error", "No se pudo crear el usuario.")
                    except Exception as e:
                        from rexus.utils.message_system import show_error
                        show_error(self, "Error", f"Error al crear usuario: {str(e)}")
                else:
                    from rexus.utils.message_system import show_warning
                    show_warning(self, "Advertencia", "No hay controlador disponible.")
    
    def buscar_usuarios(self):
        """Busca usuarios según el término ingresado."""
        termino = self.input_busqueda.text().strip()
        
        if not termino:
            # Si no hay término, mostrar todos los usuarios
            self.actualizar_datos()
            return
            
        if self.controller:
            try:
                # Buscar usuarios usando el controlador
                usuarios = self.controller.buscar_usuarios(termino)
                if usuarios is not None:
                    self.actualizar_tabla(usuarios)
                    self.lbl_info.setText(f"Encontrados {len(usuarios)} usuarios")
                else:
                    show_error(self, "Error", "Error al buscar usuarios")
            except Exception as e:
                show_error(self, "Error", f"Error en la búsqueda: {str(e)}")
        else:
            show_warning(self, "Sin Controlador", "No hay controlador disponible para realizar la búsqueda")
    
    def actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.controller.cargar_usuarios()
    
    def cargar_usuarios_en_tabla(self, usuarios):
        """Carga los usuarios en la tabla."""
        self.tabla_usuarios.setRowCount(len(usuarios))
        
        for row, usuario in enumerate(usuarios):
            self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(str(usuario.get("id", ""))))
            self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(str(usuario.get("username", ""))))
            self.tabla_usuarios.setItem(row, 2, QTableWidgetItem(str(usuario.get("nombre_completo", ""))))
            self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(str(usuario.get("email", ""))))
            self.tabla_usuarios.setItem(row, 4, QTableWidgetItem(str(usuario.get("rol", ""))))
            self.tabla_usuarios.setItem(row, 5, QTableWidgetItem(str(usuario.get("estado", ""))))
    

    def crear_controles_paginacion(self):
        """Crea los controles de paginación"""
        paginacion_layout = QHBoxLayout()
        
        # Etiqueta de información con componente Rexus
        self.info_label = RexusLabel("Mostrando 1-50 de 0 registros", "body")
        paginacion_layout.addWidget(self.info_label)
        
        paginacion_layout.addStretch()
        
        # Controles de navegación con componentes Rexus
        self.btn_primera = RexusButton("<<", "secondary")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)
        
        self.btn_anterior = RexusButton("<", "secondary")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)
        
        # Control de página actual con componentes Rexus
        self.pagina_actual_spin = RexusSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(RexusLabel("Página:", "body"))
        paginacion_layout.addWidget(self.pagina_actual_spin)
        
        self.total_paginas_label = RexusLabel("de 1", "body")
        paginacion_layout.addWidget(self.total_paginas_label)
        
        self.btn_siguiente = RexusButton(">", "secondary")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)
        
        self.btn_ultima = RexusButton(">>", "secondary")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)
        
        # Selector de registros por página con componentes Rexus
        paginacion_layout.addWidget(RexusLabel("Registros por página:", "body"))
        self.registros_por_pagina_combo = RexusComboBox()
        self.registros_por_pagina_combo.addItems(["25", "50", "100", "200"])
        self.registros_por_pagina_combo.setCurrentText("50")
        self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina)
        paginacion_layout.addWidget(self.registros_por_pagina_combo)
        
        return paginacion_layout
    
    def actualizar_controles_paginacion(self, pagina_actual, total_paginas, total_registros, registros_mostrados):
        """Actualiza los controles de paginación"""
        if hasattr(self, 'info_label'):
            inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} registros")
        
        if hasattr(self, 'pagina_actual_spin'):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)
        
        if hasattr(self, 'total_paginas_label'):
            self.total_paginas_label.setText(f"de {total_paginas}")
        
        # Habilitar/deshabilitar botones
        if hasattr(self, 'btn_primera'):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)
    
    def ir_a_pagina(self, pagina):
        """Va a una página específica"""
        if hasattr(self.controller, 'cargar_pagina'):
            self.controller.cargar_pagina(pagina)
    
    def pagina_anterior(self):
        """Va a la página anterior"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)
    
    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if hasattr(self, 'pagina_actual_spin'):
            pagina_actual = self.pagina_actual_spin.value()
            total_paginas = self.pagina_actual_spin.maximum()
            if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)
    
    def ultima_pagina(self):
        """Va a la última página"""
        if hasattr(self, 'pagina_actual_spin'):
            total_paginas = self.pagina_actual_spin.maximum()
            self.ir_a_pagina(total_paginas)
    
    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada"""
        self.ir_a_pagina(pagina)
    
    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página"""
        if hasattr(self.controller, 'cambiar_registros_por_pagina'):
            self.controller.cambiar_registros_por_pagina(int(registros))

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoUsuario(QDialog):
    """Diálogo para crear/editar usuarios."""
    
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.init_ui()
        
        if usuario:
            self.cargar_datos(usuario)
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nuevo Usuario" if not self.usuario else "Editar Usuario")
        self.setModal(True)
        self.resize(450, 500)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Información Personal
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Nombre de usuario único")
        form_layout.addRow("Usuario:", self.input_username)
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo")
        form_layout.addRow("Nombre:", self.input_nombre)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("email@ejemplo.com")
        form_layout.addRow("Email:", self.input_email)
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Contraseña")
        form_layout.addRow("Contraseña:", self.input_password)
        
        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm_password.setPlaceholderText("Confirmar contraseña")
        form_layout.addRow("Confirmar:", self.input_confirm_password)
        
        # Información del Sistema
        self.combo_role = QComboBox()
        self.combo_role.addItems(["Usuario", "Operador", "Supervisor", "Administrador", "Super Admin"])
        form_layout.addRow("Rol:", self.combo_role)
        
        self.combo_departamento = QComboBox()
        self.combo_departamento.addItems([
            "Administración", "Inventario", "Obras", "Mantenimiento", 
            "Compras", "Logística", "IT", "Recursos Humanos"
        ])
        form_layout.addRow("Departamento:", self.combo_departamento)
        
        # Estado y Configuración
        self.check_activo = QCheckBox("Usuario activo")
        self.check_activo.setChecked(True)
        form_layout.addRow("Estado:", self.check_activo)
        
        self.check_cambiar_password = QCheckBox("Debe cambiar contraseña en el próximo login")
        form_layout.addRow("Seguridad:", self.check_cambiar_password)
        
        self.input_fecha_caducidad = QDateEdit()
        self.input_fecha_caducidad.setCalendarPopup(True)
        from PyQt6.QtCore import QDate
        self.input_fecha_caducidad.setDate(QDate.currentDate().addDays(365))
        form_layout.addRow("Caducidad:", self.input_fecha_caducidad)
        
        # Observaciones
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales")
        self.input_observaciones.setMaximumHeight(80)
        form_layout.addRow("Observaciones:", self.input_observaciones)
        
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
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox {
                font-weight: bold;
                padding: 4px;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
    
    def cargar_datos(self, usuario):
        """Carga los datos de un usuario existente."""
        self.input_username.setText(usuario.get("username", ""))
        self.input_nombre.setText(usuario.get("nombre", ""))
        self.input_email.setText(usuario.get("email", ""))
        self.input_observaciones.setPlainText(usuario.get("observaciones", ""))
        
        # Cargar combos
        role = usuario.get("role", "Usuario")
        index = self.combo_role.findText(role)
        if index >= 0:
            self.combo_role.setCurrentIndex(index)
            
        departamento = usuario.get("departamento", "Administración")
        index = self.combo_departamento.findText(departamento)
        if index >= 0:
            self.combo_departamento.setCurrentIndex(index)
        
        self.check_activo.setChecked(usuario.get("activo", True))
        self.check_cambiar_password.setChecked(usuario.get("cambiar_password", False))
        
        # No cargar la contraseña por seguridad
        self.input_password.setPlaceholderText("Dejar vacío para no cambiar")
        self.input_confirm_password.setPlaceholderText("Dejar vacío para no cambiar")
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "username": self.input_username.text().strip(),
            "nombre": self.input_nombre.text().strip(),
            "email": self.input_email.text().strip(),
            "password": self.input_password.text(),
            "role": self.combo_role.currentText(),
            "departamento": self.combo_departamento.currentText(),
            "activo": self.check_activo.isChecked(),
            "cambiar_password": self.check_cambiar_password.isChecked(),
            "fecha_caducidad": self.input_fecha_caducidad.date().toString("yyyy-MM-dd"),
            "observaciones": self.input_observaciones.toPlainText().strip()
        }
    
    def validar_datos(self):
        """Valida los datos del formulario."""
        from rexus.utils.message_system import show_error
        datos = self.obtener_datos()
        
        if not datos["username"]:
            show_error(self, "Error de Validación", "El nombre de usuario es obligatorio.")
            return False
        
        if len(datos["username"]) < 3:
            show_error(self, "Error de Validación", "El nombre de usuario debe tener al menos 3 caracteres.")
            return False
        
        if not datos["nombre"]:
            show_error(self, "Error de Validación", "El nombre completo es obligatorio.")
            return False
        
        if not datos["email"]:
            show_error(self, "Error de Validación", "El email es obligatorio.")
            return False
        
        # Validar formato de email básico
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, datos["email"]):
            show_error(self, "Error de Validación", "El formato del email no es válido.")
            return False
        
        # Validar contraseña solo si se está creando un nuevo usuario o se ha ingresado una
        if not self.usuario or datos["password"]:
            if not datos["password"]:
                show_error(self, "Error de Validación", "La contraseña es obligatoria.")
                return False
            
            if len(datos["password"]) < 6:
                show_error(self, "Error de Validación", "La contraseña debe tener al menos 6 caracteres.")
                return False
            
            if datos["password"] != self.input_confirm_password.text():
                show_error(self, "Error de Validación", "Las contraseñas no coinciden.")
                return False
        
        return True
