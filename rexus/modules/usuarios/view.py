
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
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
,
    QSpinBox,
    QLabel)

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


class UsuariosView(QWidget):
    """Vista principal del módulo de usuarios."""
    
    # Señales
    solicitud_crear_usuario = pyqtSignal(dict)
    solicitud_actualizar_usuario = pyqtSignal(dict)
    solicitud_eliminar_usuario = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.controller = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Título estandarizado
        StandardComponents.create_title("👥 Gestión de Usuarios", layout)
        
        # Panel de control estandarizado
        control_panel = StandardComponents.create_control_panel()
        self.setup_control_panel(control_panel)
        layout.addWidget(control_panel)
        
        # Tabla estandarizada
        self.tabla_usuarios = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_usuarios)
        
        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)
    
    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)
        
        # Botón Nuevo Usuario estandarizado
        self.btn_nuevo_usuario = StandardComponents.create_primary_button("👥 Nuevo Usuario")
        self.btn_nuevo_usuario.clicked.connect(self.nuevo_usuario)
        layout.addWidget(self.btn_nuevo_usuario)
        
        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar usuario...")
        self.input_busqueda.returnPressed.connect(self.buscar_usuarios)
        layout.addWidget(self.input_busqueda)
        
        # Botón buscar estandarizado
        self.btn_buscar = StandardComponents.create_secondary_button("🔍 Buscar")
        self.btn_buscar.clicked.connect(self.buscar_usuarios)
        layout.addWidget(self.btn_buscar)
        
        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_secondary_button("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)
    
    def configurar_tabla(self):
        """Configura la tabla de usuarios."""
        self.tabla_usuarios.setColumnCount(6)
        self.tabla_usuarios.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre", "Email", "Rol", "Estado"
        ])
        
        # Configurar encabezados
        header = self.tabla_usuarios.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLineEdit {
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
        
        # Etiqueta de información
        self.info_label = QLabel("Mostrando 1-50 de 0 registros")
        paginacion_layout.addWidget(self.info_label)
        
        paginacion_layout.addStretch()
        
        # Controles de navegación
        self.btn_primera = QPushButton("<<")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
        paginacion_layout.addWidget(self.btn_primera)
        
        self.btn_anterior = QPushButton("<")
        self.btn_anterior.setMaximumWidth(30)
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)
        
        # Control de página actual
        self.pagina_actual_spin = QSpinBox()
        self.pagina_actual_spin.setMinimum(1)
        self.pagina_actual_spin.setMaximum(1)
        self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
        self.pagina_actual_spin.setMaximumWidth(60)
        paginacion_layout.addWidget(QLabel("Página:"))
        paginacion_layout.addWidget(self.pagina_actual_spin)
        
        self.total_paginas_label = QLabel("de 1")
        paginacion_layout.addWidget(self.total_paginas_label)
        
        self.btn_siguiente = QPushButton(">")
        self.btn_siguiente.setMaximumWidth(30)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)
        
        self.btn_ultima = QPushButton(">>")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima)
        
        # Selector de registros por página
        paginacion_layout.addWidget(QLabel("Registros por página:"))
        self.registros_por_pagina_combo = QComboBox()
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
