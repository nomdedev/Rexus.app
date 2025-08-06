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

Vista de Pedidos - Interfaz de gestión de pedidos
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
,
    QSpinBox,
    QLabel)

from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import XSSProtection, FormProtector


class PedidosView(QWidget):
    """Vista principal del módulo de pedidos."""
    
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
        
        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)
        
        # Tabla principal
        self.tabla_principal = QTableWidget()
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
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.Box)
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
        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)
        
        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)
        
        # Botón buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)
        
        # Botón actualizar
        self.btn_actualizar = QPushButton("Actualizar")
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
        self.tabla_principal.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet(f"""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #fd7e14;
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
        show_warning(self, "Función en desarrollo", "Diálogo en desarrollo")
    
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
            btn_editar = QPushButton("Editar")
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
