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

Vista de Vidrios - Interfaz de gestión de vidrios
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QWidget,
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QDoubleSpinBox,
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
    RexusColors,
    RexusFonts,
    RexusLayoutHelper
)

# Importar utilidades de sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager

from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector, XSSProtection


class VidriosView(BaseModuleView):
    """Vista principal del módulo de vidrios."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__("🪟 Gestión de Vidrios")
        self.controller = None
        self.form_protector = None
        self.setup_vidrios_ui()

    def setup_vidrios_ui(self):
        """Configura la UI específica del módulo de vidrios."""
        # Configurar controles específicos
        self.setup_vidrios_controls()
        
        # Panel de estadísticas
        stats_panel = self.crear_panel_estadisticas()
        self.add_to_main_content(stats_panel)

        # Tabla principal
        self.tabla_principal = RexusTable()
        self.configurar_tabla()
        self.set_main_table(self.tabla_principal)

        # Aplicar tema del módulo
        self.apply_theme()

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

    def setup_vidrios_controls(self):
        """Configura los controles específicos del módulo de vidrios."""
        # Añadir controles al panel principal
        controls_layout = RexusLayoutHelper.create_horizontal_layout()
        
        # Botón Nuevo Vidrio con componente Rexus
        self.btn_nuevo = RexusButton("➕ Nuevo Vidrio", "primary")
        self.btn_nuevo.setToolTip("➕ Crear un nuevo vidrio en el sistema")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        controls_layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda con componente Rexus
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar vidrio por tipo, medida o descripción...")
        self.input_busqueda.setToolTip("🔍 Buscar vidrios por tipo, dimensiones o características")
        self.input_busqueda.returnPressed.connect(self.buscar)
        controls_layout.addWidget(self.input_busqueda)

        # Filtro de tipo con componente Rexus
        self.combo_tipo = RexusComboBox()
        self.combo_tipo.addItems([
            "🪟 Todos los tipos",
            "🔲 Claro",
            "🌫️ Esmerilado",
            "🎨 Templado",
            "🛡️ Laminado",
            "🌈 Reflectivo",
            "📏 Doble Vidriado"
        ])
        self.combo_tipo.setToolTip("🪟 Filtrar vidrios por tipo")
        controls_layout.addWidget(self.combo_tipo)

        # Botón buscar con componente Rexus
        self.btn_buscar = RexusButton("🔍 Buscar", "secondary")
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_buscar.clicked.connect(self.buscar)
        controls_layout.addWidget(self.btn_buscar)

        # Botón actualizar con componente Rexus
        self.btn_actualizar = RexusButton("🔄 Actualizar", "secondary")
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de vidrios")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        controls_layout.addWidget(self.btn_actualizar)

        controls_layout.addStretch()
        
        # Botón editar con componente Rexus
        self.btn_editar = RexusButton("✏️ Editar", "warning")
        self.btn_editar.setToolTip("✏️ Editar vidrio seleccionado")
        self.btn_editar.setEnabled(False)
        controls_layout.addWidget(self.btn_editar)

        # Botón eliminar con componente Rexus
        self.btn_eliminar = RexusButton("🗑️ Eliminar", "danger")
        self.btn_eliminar.setToolTip("🗑️ Eliminar vidrio seleccionado")
        self.btn_eliminar.setEnabled(False)
        controls_layout.addWidget(self.btn_eliminar)
        
        # Añadir controles al área principal
        self.add_to_main_content(controls_layout)

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas de vidrios."""
        panel = RexusGroupBox("[CHART] Estadísticas de Vidrios")
        layout = RexusLayoutHelper.create_horizontal_layout()

        # Total vidrios
        self.lbl_total_vidrios = self.crear_stat_widget("🪟", "Total Vidrios", "0", "#17a2b8")
        layout.addWidget(self.lbl_total_vidrios)

        # Vidrios disponibles
        self.lbl_vidrios_disponibles = self.crear_stat_widget("[CHECK]", "Disponibles", "0", "#28a745")
        layout.addWidget(self.lbl_vidrios_disponibles)

        # En proceso
        self.lbl_vidrios_proceso = self.crear_stat_widget("⚙️", "En Proceso", "0", "#ffc107")
        layout.addWidget(self.lbl_vidrios_proceso)

        # Tipos únicos
        self.lbl_tipos_vidrios = self.crear_stat_widget("📂", "Tipos", "0", "#6c757d")
        layout.addWidget(self.lbl_tipos_vidrios)

        panel.setLayout(layout)
        return panel

    def crear_stat_widget(self, icono, titulo, valor, color):
        """Crea un widget de estadística individual."""
        widget = RexusFrame()
        
        layout = RexusLayoutHelper.create_vertical_layout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono y título
        header_layout = RexusLayoutHelper.create_horizontal_layout()
        
        icono_lbl = RexusLabel(icono, "heading")
        header_layout.addWidget(icono_lbl)
        
        titulo_lbl = RexusLabel(titulo, "caption")
        header_layout.addWidget(titulo_lbl)
        
        layout.addLayout(header_layout)

        # Valor
        valor_lbl = RexusLabel(valor, "heading")
        valor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(valor_lbl)

        # Guardar referencia al label del valor para actualizar
        setattr(widget, 'valor_label', valor_lbl)
        
        widget.setLayout(layout)
        return widget

    def configurar_tabla(self):
        """Configura la tabla principal con estilos modernos."""
        self.tabla_principal.setColumnCount(8)
        self.tabla_principal.setHorizontalHeaderLabels([
            "🆔 ID",
            "🪟 Tipo", 
            "📐 Dimensiones",
            "🎨 Color/Acabado",
            "📦 Stock",
            "💰 Precio m²",
            "[CHART] Estado",
            "⚡ Acciones"
        ])

        # Configurar tamaños de columnas
        header = self.tabla_principal.horizontalHeader()
        header.resizeSection(0, 60)   # ID
        header.resizeSection(1, 120)  # Tipo
        header.resizeSection(2, 140)  # Dimensiones
        header.resizeSection(3, 130)  # Color/Acabado
        header.resizeSection(4, 80)   # Stock
        header.resizeSection(5, 100)  # Precio m²
        header.resizeSection(6, 100)  # Estado
        header.setStretchLastSection(True)  # Acciones

        # Configuraciones visuales
        self.tabla_principal.setAlternatingRowColors(True)
        self.tabla_principal.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Los estilos se aplicarán por el tema unificado
        
        # Conectar señal de selección
        self.tabla_principal.itemSelectionChanged.connect(self.on_vidrio_seleccionado)

    def apply_theme(self):
        """Aplica el tema usando el sistema unificado de Rexus."""
        # Usar el sistema de temas de Rexus en lugar de CSS inline
        style_manager.apply_theme(self, "high_contrast")
        
        # Configuraciones específicas para el módulo de vidrios si es necesario
        self._apply_vidrios_specific_styling()
    
    def _apply_vidrios_specific_styling(self):
        """Aplica estilos específicos del módulo de vidrios."""
        # Los estilos ahora los maneja el sistema unificado de temas
        pass

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        # Estados de botones principales
        self.btn_nuevo.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)
        
        # Estados de botones de acción
        selected = self.tabla_principal.currentRow() >= 0
        self.btn_editar.setEnabled(not loading and selected)
        self.btn_eliminar.setEnabled(not loading and selected)
        
        # Cambiar textos durante loading
        if loading:
            self.btn_actualizar.setText("⏳ Actualizando...")
            self.btn_buscar.setText("🔍 Buscando...")
        else:
            self.btn_actualizar.setText("🔄 Actualizar")
            self.btn_buscar.setText("🔍 Buscar")

    def on_vidrio_seleccionado(self):
        """Maneja la selección de vidrios en la tabla."""
        hay_seleccion = self.tabla_principal.currentRow() >= 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas mostradas en el panel."""
        try:
            if hasattr(self.lbl_total_vidrios, 'valor_label'):
                self.lbl_total_vidrios.valor_label.setText(str(stats.get('total_vidrios', 0)))
            
            if hasattr(self.lbl_vidrios_disponibles, 'valor_label'):
                self.lbl_vidrios_disponibles.valor_label.setText(str(stats.get('vidrios_disponibles', 0)))
            
            if hasattr(self.lbl_vidrios_proceso, 'valor_label'):
                self.lbl_vidrios_proceso.valor_label.setText(str(stats.get('vidrios_proceso', 0)))
            
            if hasattr(self.lbl_tipos_vidrios, 'valor_label'):
                self.lbl_tipos_vidrios.valor_label.setText(str(stats.get('tipos_vidrios', 0)))
                
        except Exception as e:
            show_error(self, f"Error actualizando estadísticas: {e}")

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo vidrio."""
        dialog = NuevoVidrioDialog(self)
        if dialog.exec() == dialog.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                resultado = self.controller.crear_vidrio(datos)
                if resultado[0]:  # Éxito
                    show_success(self, "Vidrio Creado", resultado[1])
                    self.actualizar_datos()
                else:  # Error
                    show_error(self, "Error", resultado[1])

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

            # Botón de acciones con componente Rexus
            btn_editar = RexusButton("Editar", "warning")
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


class NuevoVidrioDialog(QDialog):
    """Diálogo para crear un nuevo vidrio."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Vidrio")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setupUI()
        
    def setupUI(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título
        titulo = RexusLabel("Crear Nuevo Vidrio", "title")
        layout.addWidget(titulo)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos obligatorios
        self.codigo_input = RexusLineEdit()
        self.codigo_input.setPlaceholderText("Ej: V001, VID-001")
        self.codigo_input.setMaxLength(20)
        form_layout.addRow("Código*:", self.codigo_input)
        
        self.descripcion_input = RexusLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción del vidrio")
        self.descripcion_input.setMaxLength(200)
        form_layout.addRow("Descripción*:", self.descripcion_input)
        
        self.tipo_input = RexusComboBox()
        self.tipo_input.addItems([
            "Templado",
            "Laminado", 
            "Doble Acristalamiento",
            "Flotado",
            "Reflectivo",
            "Bajo Emisivo",
            "Acústico",
            "Seguridad"
        ])
        self.tipo_input.setEditable(True)
        form_layout.addRow("Tipo*:", self.tipo_input)
        
        self.proveedor_input = RexusComboBox()
        self.proveedor_input.addItems([
            "Guardian Glass",
            "Pilkington",
            "Vitro",
            "Saint-Gobain",
            "AGC Glass",
            "Otro"
        ])
        self.proveedor_input.setEditable(True)
        form_layout.addRow("Proveedor*:", self.proveedor_input)
        
        # Campos opcionales
        self.espesor_input = QDoubleSpinBox()
        self.espesor_input.setRange(0.1, 50.0)
        self.espesor_input.setSuffix(" mm")
        self.espesor_input.setDecimals(1)
        self.espesor_input.setValue(6.0)
        form_layout.addRow("Espesor:", self.espesor_input)
        
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.0, 99999.99)
        self.precio_input.setPrefix("$ ")
        self.precio_input.setSuffix(" /m²")
        self.precio_input.setDecimals(2)
        form_layout.addRow("Precio por m²:", self.precio_input)
        
        self.color_input = RexusComboBox()
        self.color_input.addItems([
            "Transparente",
            "Bronce",
            "Gris",
            "Verde",
            "Azul",
            "Negro",
            "Blanco",
            "Otro"
        ])
        self.color_input.setEditable(True)
        form_layout.addRow("Color:", self.color_input)
        
        self.tratamiento_input = RexusLineEdit()
        self.tratamiento_input.setPlaceholderText("Ej: Templado, Laminado, etc.")
        self.tratamiento_input.setMaxLength(100)
        form_layout.addRow("Tratamiento:", self.tratamiento_input)
        
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
        
        self.btn_crear = RexusButton("Crear Vidrio", "primary")
        self.btn_crear.clicked.connect(self.validar_y_aceptar)
        botones_layout.addWidget(self.btn_crear)
        
        layout.addLayout(botones_layout)
        
    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar."""
        # Validar campos obligatorios
        if not self.codigo_input.text().strip():
            show_error(self, "Error", "El código es obligatorio")
            self.codigo_input.setFocus()
            return
            
        if not self.descripcion_input.text().strip():
            show_error(self, "Error", "La descripción es obligatoria")
            self.descripcion_input.setFocus()
            return
            
        if not self.tipo_input.currentText().strip():
            show_error(self, "Error", "El tipo es obligatorio")
            self.tipo_input.setFocus()
            return
            
        if not self.proveedor_input.currentText().strip():
            show_error(self, "Error", "El proveedor es obligatorio")
            self.proveedor_input.setFocus()
            return
            
        self.accept()
        
    def obtener_datos(self):
        """Retorna los datos del formulario."""
        return {
            "codigo": self.codigo_input.text().strip(),
            "descripcion": self.descripcion_input.text().strip(),
            "tipo": self.tipo_input.currentText().strip(),
            "proveedor": self.proveedor_input.currentText().strip(),
            "espesor": self.espesor_input.value(),
            "precio_m2": self.precio_input.value(),
            "color": self.color_input.currentText().strip() or "Transparente",
            "tratamiento": self.tratamiento_input.text().strip() or "",
        }
