"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice sh        # Estados de botones principales
        self.btn_nuevo_herraje.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)e included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Vista de Herrajes - Interfaz de gestión de herrajes
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpinBox,
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
    RexusTabWidget,
    RexusColors,
    RexusFonts,
    RexusLayoutHelper
)
from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager

from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector, XSSProtection


class HerrajesView(BaseModuleView):
    """Vista principal del módulo de herrajes."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    # Constantes para mensajes de error
    MSG_SIN_CONTROLADOR = "Sin controlador"
    MSG_NO_CONTROLADOR_DISPONIBLE = "No hay controlador disponible"
    MSG_NO_CONTROLADOR_SINCRONIZACION = "No hay controlador disponible para la sincronización"

    def __init__(self):
        super().__init__("🔧 Gestión de Herrajes")
        self.controller = None
        self.form_protector = None
        self.setup_herrajes_ui()

    def setup_herrajes_ui(self):
        """Configura la UI específica del módulo de herrajes."""
        # Configurar controles específicos
        self.setup_herrajes_controls()
        
        # Crear sistema de pestañas usando RexusTabWidget
        self.tab_widget = RexusTabWidget()

        # Pestaña de Gestión de Herrajes
        tab_gestion = self.crear_tab_gestion()
        self.tab_widget.addTab(tab_gestion, "🔧 Gestión")

        # Pestaña de Estadísticas
        tab_estadisticas = self.crear_tab_estadisticas()
        self.tab_widget.addTab(tab_estadisticas, "📊 Estadísticas")

        self.add_to_main_content(self.tab_widget)

        # Aplicar tema del módulo
        self.apply_theme()

        # Inicializar protección XSS
        self.init_xss_protection()

    def setup_herrajes_controls(self):
        """Configura los controles específicos del módulo de herrajes."""
        # Los controles principales se configurarán dentro de las pestañas
        pass
    
    def crear_tab_gestion(self):
        """Crea la pestaña de gestión de herrajes."""
        tab = RexusFrame()
        layout = RexusLayoutHelper.create_vertical_layout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Panel de integración con inventario
        integration_panel = self.crear_panel_integracion()
        layout.addWidget(integration_panel)

        # Tabla principal
        self.tabla_principal = RexusTable()
        self.configurar_tabla()
        layout.addWidget(self.tabla_principal)

        tab.setLayout(layout)
        return tab

    def crear_tab_estadisticas(self):
        """Crea la pestaña de estadísticas de herrajes."""
        tab = RexusFrame()
        layout = RexusLayoutHelper.create_vertical_layout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Panel de estadísticas principales
        stats_panel = self.crear_panel_estadisticas()
        layout.addWidget(stats_panel)

        # Panel de análisis de stock
        stock_panel = self.crear_panel_analisis_stock()
        layout.addWidget(stock_panel)

        # Panel de reportes de herrajes
        reportes_panel = self.crear_panel_reportes_herrajes()
        layout.addWidget(reportes_panel)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def crear_panel_analisis_stock(self):
        """Crea el panel de análisis de stock."""
        panel = RexusGroupBox("📈 Análisis de Stock")
        layout = RexusLayoutHelper.create_vertical_layout()
        
        # Placeholder para análisis de stock
        placeholder = RexusLabel("📊 Análisis de stock próximamente", "body")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        panel.setLayout(layout)
        return panel

    def crear_panel_reportes_herrajes(self):
        """Crea el panel de reportes de herrajes."""
        panel = RexusGroupBox("📄 Reportes de Herrajes")
        layout = RexusLayoutHelper.create_horizontal_layout()
        
        # Botones de reportes con componentes Rexus
        btn_reporte_stock = RexusButton("📋 Herrajes por Stock", "primary")
        layout.addWidget(btn_reporte_stock)

        btn_reporte_categorias = RexusButton("📊 Por Categorías", "secondary")
        layout.addWidget(btn_reporte_categorias)

        btn_reporte_proveedores = RexusButton("🏭 Por Proveedores", "secondary")
        layout.addWidget(btn_reporte_proveedores)
        layout.addStretch()
        panel.setLayout(layout)
        return panel


        # Aplicar tema del módulo
        try:
            style_manager.apply_module_theme(self)
        except Exception as e:
            print(f"[HERRAJES] Error aplicando tema: {e}")
            # Aplicar estilos de alto contraste como fallback
            self.apply_high_contrast_style()

    def apply_high_contrast_style(self):
        """Aplicar estilos de alto contraste para mejor legibilidad."""
        # Los estilos de alto contraste ahora se manejan a través del sistema unificado de temas
        style_manager.apply_theme(self, "high_contrast")

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
        """Crea el panel de control superior con botones modernos."""
        panel = RexusGroupBox("🎛️ Panel de Control")
        layout = RexusLayoutHelper.create_horizontal_layout()

        # Botón Nuevo Herraje con componente Rexus
        self.btn_nuevo = RexusButton("➕ Nuevo Herraje", "primary")
        self.btn_nuevo.setToolTip("➕ Crear un nuevo herraje en el sistema")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda usando componente Rexus
        self.input_busqueda = RexusLineEdit("🔍 Buscar herraje por nombre o descripción...")
        self.input_busqueda.setToolTip("🔍 Buscar herrajes por nombre, descripción o tipo")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Filtro de tipo usando componente Rexus
        self.combo_tipo = RexusComboBox([
            "🔩 Todos los tipos",
            "⚙️ Tornillería",
            "🔗 Cadenas",
            "🚪 Bisagras", 
            "🔐 Cerraduras",
            "🔧 Herramientas",
            "📏 Medición"
        ])
        self.combo_tipo.setToolTip("🔩 Filtrar herrajes por tipo")
        layout.addWidget(self.combo_tipo)

        # Botón buscar usando componente Rexus
        self.btn_buscar = RexusButton("🔍 Buscar", "primary")
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar usando componente Rexus
        self.btn_actualizar = RexusButton("🔄 Actualizar", "success")
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de herrajes")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

        # Separador y botones de acción
        layout.addStretch()
        
        # Botón editar usando componente Rexus
        self.btn_editar = RexusButton("✏️ Editar", "warning")
        self.btn_editar.setToolTip("✏️ Editar herraje seleccionado")
        self.btn_editar.setEnabled(False)
        layout.addWidget(self.btn_editar)

        # Botón eliminar usando componente Rexus
        self.btn_eliminar = RexusButton("🗑️ Eliminar", "danger")
        self.btn_eliminar.setToolTip("🗑️ Eliminar herraje seleccionado")
        self.btn_eliminar.setEnabled(False)
        layout.addWidget(self.btn_eliminar)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas de herrajes."""
        panel = RexusGroupBox("📊 Estadísticas de Herrajes")

        layout = RexusLayoutHelper.create_horizontal_layout()

        # Total herrajes
        self.lbl_total_herrajes = self.crear_stat_widget("🔩", "Total Herrajes", "0", "#17a2b8")
        layout.addWidget(self.lbl_total_herrajes)

        # Herrajes activos
        self.lbl_herrajes_activos = self.crear_stat_widget("✅", "Activos", "0", "#28a745")
        layout.addWidget(self.lbl_herrajes_activos)

        # Herrajes inactivos
        self.lbl_herrajes_inactivos = self.crear_stat_widget("⏸️", "Inactivos", "0", "#ffc107")
        layout.addWidget(self.lbl_herrajes_inactivos)

        # Tipos disponibles
        self.lbl_tipos_disponibles = self.crear_stat_widget("📂", "Tipos", "0", "#6c757d")
        layout.addWidget(self.lbl_tipos_disponibles)

        return panel

    def crear_stat_widget(self, icono, titulo, valor, color):
        """Crea un widget de estadística individual."""
        widget = RexusFrame()
        
        layout = RexusLayoutHelper.create_vertical_layout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono y título
        header_layout = RexusLayoutHelper.create_horizontal_layout()
        
        icono_lbl = RexusLabel(icono, "subtitle")
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
        
        return widget

    def configurar_tabla(self):
        """Configura la tabla principal con estilos modernos."""
        self.tabla_principal.setColumnCount(7)
        self.tabla_principal.setHorizontalHeaderLabels([
            "🆔 ID",
            "🔧 Nombre", 
            "📝 Descripción",
            "📂 Tipo",
            "📊 Estado",
            "📅 Última Actualización",
            "⚡ Acciones"
        ])

        # Configurar tamaños de columnas
        header = self.tabla_principal.horizontalHeader()
        header.resizeSection(0, 60)   # ID
        header.resizeSection(1, 150)  # Nombre
        header.resizeSection(2, 200)  # Descripción
        header.resizeSection(3, 120)  # Tipo
        header.resizeSection(4, 100)  # Estado
        header.resizeSection(5, 140)  # Última Actualización
        header.setStretchLastSection(True)  # Acciones

        # Configuraciones visuales
        self.tabla_principal.setAlternatingRowColors(True)
        self.tabla_principal.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Conectar señal de selección
        self.tabla_principal.itemSelectionChanged.connect(self.on_herraje_seleccionado)

    def apply_theme(self):
        """Aplica el tema usando el sistema unificado de Rexus."""
        # Usar el sistema de temas de Rexus en lugar de CSS inline
        style_manager.apply_theme(self, "high_contrast")
        
        # Configuraciones específicas para el módulo de herrajes si es necesario
        self._apply_herrajes_specific_styling()
    
    def _apply_herrajes_specific_styling(self):
        """Aplica estilos específicos del módulo de herrajes."""
        # Los estilos ahora los maneja el sistema unificado de temas
        pass
    

    def aplicar_estilo_basico(self):
        """Aplica estilos básicos como fallback."""
        # Los estilos básicos ahora se manejan a través del sistema unificado de temas
        style_manager.apply_theme(self, "default")

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

    def on_herraje_seleccionado(self):
        """Maneja la selección de herrajes en la tabla."""
        hay_seleccion = self.tabla_principal.currentRow() >= 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)
        
        # Habilitar/deshabilitar botones de integración
        if hasattr(self, 'btn_transferir_inventario'):
            self.btn_transferir_inventario.setEnabled(hay_seleccion)
        if hasattr(self, 'btn_crear_reserva'):
            self.btn_crear_reserva.setEnabled(hay_seleccion)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas mostradas en el panel."""
        try:
            # Buscar los labels de valor dentro de cada widget de estadística
            if hasattr(self, 'lbl_total_herrajes'):
                valor_labels = self.lbl_total_herrajes.findChildren(RexusLabel)
                if len(valor_labels) >= 2:  # Segundo label es el valor
                    valor_labels[1].setText(str(stats.get("total_herrajes", 0)))

            if hasattr(self, 'lbl_herrajes_activos'):
                valor_labels = self.lbl_herrajes_activos.findChildren(RexusLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("herrajes_activos", 0)))

            if hasattr(self, 'lbl_herrajes_inactivos'):
                valor_labels = self.lbl_herrajes_inactivos.findChildren(RexusLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("herrajes_inactivos", 0)))

            if hasattr(self, 'lbl_tipos_disponibles'):
                valor_labels = self.lbl_tipos_disponibles.findChildren(RexusLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("tipos_disponibles", 0)))

        except Exception as e:
            show_error(self, "Error de Estadísticas", f"Error actualizando estadísticas: {e}")

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo herraje."""
        dialog = NuevoHerrajeDialog(self)
        if dialog.exec() == dialog.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                resultado = self.controller.crear_herraje(datos)
                if resultado[0]:  # Éxito
                    show_success(self, "Herraje Creado", resultado[1])
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

            # Botón de acciones usando componente Rexus
            btn_editar = RexusButton("Editar", "warning")
            self.tabla_principal.setCellWidget(row, 4, btn_editar)

    def crear_panel_integracion(self):
        """Crea el panel de integración con inventario."""
        panel = RexusGroupBox("🔗 Integración con Inventario")

        layout = RexusLayoutHelper.create_horizontal_layout()

        # Botón sincronizar con inventario usando componente Rexus
        self.btn_sincronizar_inventario = RexusButton("🔄 Sincronizar con Inventario", "success")
        self.btn_sincronizar_inventario.setToolTip("🔄 Sincroniza herrajes con el inventario general")
        self.btn_sincronizar_inventario.clicked.connect(self.sincronizar_inventario)
        layout.addWidget(self.btn_sincronizar_inventario)

        # Botón resumen de integración usando componente Rexus
        self.btn_resumen_integracion = RexusButton("📊 Resumen Integración", "info")
        self.btn_resumen_integracion.setToolTip("📊 Muestra resumen del estado de integración")
        self.btn_resumen_integracion.clicked.connect(self.mostrar_resumen_integracion)
        layout.addWidget(self.btn_resumen_integracion)

        # Botón transferir a inventario usando componente Rexus
        self.btn_transferir_inventario = RexusButton("📦 Transferir a Inventario", "secondary")
        self.btn_transferir_inventario.setToolTip("📦 Transfiere herraje seleccionado al inventario general")
        self.btn_transferir_inventario.setEnabled(False)
        self.btn_transferir_inventario.clicked.connect(self.transferir_a_inventario)
        layout.addWidget(self.btn_transferir_inventario)

        # Botón crear reserva usando componente Rexus
        self.btn_crear_reserva = RexusButton("📝 Crear Reserva", "warning")
        self.btn_crear_reserva.setToolTip("📝 Crear reserva del herraje para una obra")
        self.btn_crear_reserva.setEnabled(False)
        self.btn_crear_reserva.clicked.connect(self.crear_reserva_obra)
        layout.addWidget(self.btn_crear_reserva)

        return panel

    def sincronizar_inventario(self):
        """Sincroniza herrajes con el inventario general."""
        if hasattr(self, "controller") and self.controller:
            self.controller.sincronizar_con_inventario()
        else:
            show_warning(self, self.MSG_SIN_CONTROLADOR, self.MSG_NO_CONTROLADOR_SINCRONIZACION)

    def mostrar_resumen_integracion(self):
        """Muestra el resumen de integración."""
        if hasattr(self, "controller") and self.controller:
            self.controller.mostrar_resumen_integracion()
        else:
            show_warning(self, "Sin controlador", "No hay controlador disponible")

    def transferir_a_inventario(self):
        """Transfiere herraje seleccionado al inventario."""
        if not hasattr(self, "controller") or not self.controller:
            show_warning(self, "Sin controlador", "No hay controlador disponible")
            return
            
        # Obtener herraje seleccionado
        fila_seleccionada = self.tabla_principal.currentRow()
        if fila_seleccionada < 0:
            show_warning(self, "Sin selección", "Debe seleccionar un herraje para transferir")
            return
            
        # Obtener ID del herraje (asumiendo que está en la primera columna)
        id_item = self.tabla_principal.item(fila_seleccionada, 0)
        if not id_item:
            show_error(self, "Error", "No se pudo obtener el ID del herraje seleccionado")
            return
            
        try:
            herraje_id = int(id_item.text())
            
            # Solicitar cantidad al usuario usando StandardComponents
            cantidad, ok = StandardComponents.get_integer_input(
                self, 
                "Cantidad a Transferir", 
                "Ingrese la cantidad a transferir:",
                value=1, min=1, max=9999
            )
            
            if ok and cantidad > 0:
                self.controller.transferir_a_inventario(herraje_id, cantidad)
                
        except ValueError:
            show_error(self, "Error", "ID de herraje inválido")

    def crear_reserva_obra(self):
        """Crea una reserva del herraje para una obra."""
        if not hasattr(self, "controller") or not self.controller:
            show_warning(self, "Sin controlador", "No hay controlador disponible")
            return
            
        # Obtener herraje seleccionado
        fila_seleccionada = self.tabla_principal.currentRow()
        if fila_seleccionada < 0:
            show_warning(self, "Sin selección", "Debe seleccionar un herraje para crear reserva")
            return
            
        # Obtener ID del herraje
        id_item = self.tabla_principal.item(fila_seleccionada, 0)
        if not id_item:
            show_error(self, "Error", "No se pudo obtener el ID del herraje seleccionado")
            return
            
        try:
            herraje_id = int(id_item.text())
            
            # Solicitar datos de la reserva usando StandardComponents
            
            # Solicitar ID de obra
            obra_id, ok_obra = StandardComponents.get_integer_input(
                self,
                "ID de Obra",
                "Ingrese el ID de la obra:",
                value=1, min=1, max=9999
            )
            
            if not ok_obra:
                return
                
            # Solicitar cantidad
            cantidad, ok_cantidad = StandardComponents.get_integer_input(
                self,
                "Cantidad a Reservar",
                "Ingrese la cantidad a reservar:",
                value=1, min=1, max=9999
            )
            
            if not ok_cantidad:
                return
                
            # Solicitar observaciones
            observaciones, ok_obs = StandardComponents.get_text_input(
                self,
                "Observaciones",
                "Observaciones (opcional):"
            )
            
            if ok_cantidad and cantidad > 0:
                self.controller.crear_reserva_para_obra(
                    herraje_id, obra_id, cantidad, observaciones if ok_obs else ""
                )
                
        except ValueError:
            show_error(self, "Error", "ID de herraje inválido")

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


class NuevoHerrajeDialog(QDialog):
    """Diálogo para crear un nuevo herraje."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Herraje")
        self.setModal(True)
        self.setFixedSize(500, 650)
        self.setupUI()
        
    def setupUI(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título
        titulo = RexusLabel("Crear Nuevo Herraje", "title")
        layout.addWidget(titulo)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos obligatorios
        self.codigo_input = RexusLineEdit()
        self.codigo_input.setPlaceholderText("Ej: H001, HER-001")
        self.codigo_input.setMaxLength(20)
        form_layout.addRow("Código*:", self.codigo_input)
        
        self.descripcion_input = RexusLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción del herraje")
        self.descripcion_input.setMaxLength(200)
        form_layout.addRow("Descripción*:", self.descripcion_input)
        
        self.proveedor_input = RexusComboBox()
        self.proveedor_input.addItems([
            "Kawneer",
            "Schüco",
            "Reynaers",
            "Technal",
            "Cortizo",
            "ALUCOIL",
            "Otro"
        ])
        self.proveedor_input.setEditable(True)
        form_layout.addRow("Proveedor*:", self.proveedor_input)
        
        # Categoría y tipo
        self.categoria_input = RexusLineEdit()
        self.categoria_input.setPlaceholderText("Ej: Bisagras, Cerraduras, etc.")
        self.categoria_input.setMaxLength(100)
        form_layout.addRow("Categoría:", self.categoria_input)
        
        self.tipo_input = RexusComboBox()
        self.tipo_input.addItems([
            "BISAGRA",
            "CERRADURA", 
            "MANILLA",
            "PESTILLO",
            "GUÍA",
            "RODAMIENTO",
            "TORNILLERÍA",
            "SELLADO",
            "OTRO"
        ])
        self.tipo_input.setEditable(True)
        form_layout.addRow("Tipo:", self.tipo_input)
        
        # Stock
        self.stock_actual_input = QSpinBox()
        self.stock_actual_input.setRange(0, 99999)
        self.stock_actual_input.setValue(0)
        form_layout.addRow("Stock Actual:", self.stock_actual_input)
        
        self.stock_minimo_input = QSpinBox()
        self.stock_minimo_input.setRange(0, 99999)
        self.stock_minimo_input.setValue(1)
        form_layout.addRow("Stock Mínimo:", self.stock_minimo_input)
        
        # Precios
        self.precio_unitario_input = QDoubleSpinBox()
        self.precio_unitario_input.setRange(0.0, 99999.99)
        self.precio_unitario_input.setPrefix("$ ")
        self.precio_unitario_input.setDecimals(2)
        form_layout.addRow("Precio Unitario:", self.precio_unitario_input)
        
        self.precio_compra_input = QDoubleSpinBox()
        self.precio_compra_input.setRange(0.0, 99999.99)
        self.precio_compra_input.setPrefix("$ ")
        self.precio_compra_input.setDecimals(2)
        form_layout.addRow("Precio Compra:", self.precio_compra_input)
        
        # Ubicación
        self.ubicacion_input = RexusLineEdit()
        self.ubicacion_input.setPlaceholderText("Ej: Almacén A-1, Estante 3")
        self.ubicacion_input.setMaxLength(100)
        form_layout.addRow("Ubicación:", self.ubicacion_input)
        
        # Observaciones
        self.observaciones_input = RexusLineEdit()
        self.observaciones_input.setPlaceholderText("Notas adicionales del herraje")
        self.observaciones_input.setMaxLength(500)
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        layout.addLayout(form_layout)
        
        # Nota de campos obligatorios
        nota = RexusLabel("* Campos obligatorios", "caption")
        layout.addWidget(nota)
        
        layout.addStretch()
        
        # Botones
        botones_layout = QHBoxLayout()
        
        self.btn_cancelar = RexusButton("Cancelar", "secondary")
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_cancelar)
        
        botones_layout.addStretch()
        
        self.btn_crear = RexusButton("Crear Herraje", "primary")
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
            "proveedor": self.proveedor_input.currentText().strip(),
            "categoria": self.categoria_input.text().strip() or "",
            "tipo": self.tipo_input.currentText().strip() or "OTRO",
            "stock_actual": self.stock_actual_input.value(),
            "stock_minimo": self.stock_minimo_input.value(),
            "precio_unitario": self.precio_unitario_input.value(),
            "precio_compra": self.precio_compra_input.value(),
            "ubicacion": self.ubicacion_input.text().strip() or "",
            "observaciones": self.observaciones_input.text().strip() or "",
        }
