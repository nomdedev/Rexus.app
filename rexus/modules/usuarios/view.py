
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
    
    def nuevo_usuario(self):
        """Abre el diálogo para crear un nuevo usuario."""
        # TODO: Implementar diálogo
        show_warning(self, "Función en desarrollo", "Diálogo de nuevo usuario en desarrollo")
    
    def buscar_usuarios(self):
        """Busca usuarios según el término ingresado."""
        termino = self.input_busqueda.text()
        # TODO: Implementar búsqueda
        print(f"Buscando usuarios: {termino}")
    
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
