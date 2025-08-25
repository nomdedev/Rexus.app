"""
MIT License

Copyright (c) 2024 Rexus.app

Vista Principal de Herrajes - Interfaz moderna de gestión de herrajes
Versión simplificada con componentes básicos de PyQt6
"""

import logging
from typing import Dict, List

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
QComboBox,
QGroupBox,
QHBoxLayout,
QLabel,
QLineEdit,
QTableWidget,
QTableWidgetItem,
QVBoxLayout,
QWidget,
QPushButton,
QHeaderView
)

# Importar componentes básicos
from rexus.ui.components.base_components import RexusColors
from rexus.utils.loading_manager import LoadingManager
from rexus.utils.message_system import ask_question, show_error, show_warning
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin
from rexus.modules.herrajes.constants import HerrajesConstants


class HerrajesView(QWidget, ModuleExportMixin):
    """Vista principal del módulo de herrajes con UI/UX modernizada."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    herraje_seleccionado = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.loading_manager = LoadingManager()

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        # Referencias a widgets importantes
        self.tabla_herrajes = None
        self.input_busqueda = None
        self.combo_categoria = None
        self.stats_labels = {}

        self.init_ui()
        self.aplicar_estilos()

def setup_ui(self):
        """Método de compatibilidad para setup_ui."""
self.init_ui()

def refresh_data(self):
        """Actualiza los datos mostrados en la vista."""
try:
        if self.controller and hasattr(self.controller, 'cargar_herrajes'):
                self.controller.cargar_herrajes()
else:
                self._cargar_datos_demo()
except Exception as e:
        self.show_error(f"Error actualizando datos: {e}")

def show_error(self, mensaje, titulo="Error"):
        """
Muestra un mensaje de error al usuario.

Args:
        mensaje (str): Mensaje de error
titulo (str): Título del diálogo
"""
try:
        show_error(self, titulo, mensaje)
except ImportError as e:
        # Fallback usando QMessageBox si show_error no está disponible
logger.warning("show_error no disponible, usando fallback: %s", e)
from PyQt6.QtWidgets import QMessageBox
msg = QMessageBox()
msg.setIcon(QMessageBox.Icon.Critical)
msg.setWindowTitle(titulo)
msg.setText(mensaje)
msg.exec()

def _cargar_datos_demo(self):
        """Carga datos demo cuando no hay controlador."""
datos_demo = [
{
'id': 1,
'codigo': 'H001',
'nombre': 'Bisagra Piano',
'categoria': 'Bisagras',
'stock_actual': 50,
'precio_unitario': 15.75
},
{
'id': 2,
'codigo': 'H002', 
'nombre': 'Manija Moderna',
'categoria': 'Manijas',
'stock_actual': 25,
'precio_unitario': 32.50
}
]
self.actualizar_tabla_herrajes(datos_demo)

def init_ui(self):
        """Inicializa la interfaz de usuario con pestañas (QTabWidget)."""
main_layout = QVBoxLayout(self)
main_layout.setSpacing(10)
main_layout.setContentsMargins(10, 10, 10, 10)

from PyQt6.QtWidgets import QTabWidget
self.tabs = QTabWidget()
self.tabs.setTabPosition(QTabWidget.TabPosition.North)
self.tabs.setMovable(False)

# --- Pestaña Inventario ---
tab_inventario = QWidget()
inventario_layout = QVBoxLayout(tab_inventario)
inventario_layout.setSpacing(10)
inventario_layout.setContentsMargins(10, 10, 10, 10)
control_panel = self.crear_panel_control()
inventario_layout.addWidget(control_panel)
# Remover panel de estadísticas de aquí - solo en pestaña Estadísticas
self.crear_tabla_herrajes(inventario_layout)
self.tab_inventario = tab_inventario
self.tabs.addTab(tab_inventario, )

# --- Pestaña Asignación a Obra ---
tab_asignacion = QWidget()
asignacion_layout = QVBoxLayout(tab_asignacion)
asignacion_layout.setSpacing(10)
asignacion_layout.setContentsMargins(10, 10, 10, 10)

# Panel de selección de obra
obra_panel = QGroupBox("Seleccionar Obra")
obra_layout = QHBoxLayout(obra_panel)

self.combo_obras = QComboBox()
self.combo_obras.setPlaceholderText("Seleccione una obra...")
self.combo_obras.setMinimumHeight(35)
obra_layout.addWidget(QLabel("Obra:"))
obra_layout.addWidget(self.combo_obras, 2)

self.btn_cargar_obra = QPushButton("Cargar Herrajes")
self.btn_cargar_obra.setMinimumHeight(35)
self.btn_cargar_obra.clicked.connect(self.on_cargar_herrajes_obra)
obra_layout.addWidget(self.btn_cargar_obra)

asignacion_layout.addWidget(obra_panel)

# Tabla de herrajes asignados a la obra
self.tabla_herrajes_obra = QTableWidget()
self.configurar_tabla_obra()
asignacion_layout.addWidget(self.tabla_herrajes_obra)

self.tabs.addTab(tab_asignacion, "Asignación a Obra")

# --- Pestaña Proveedores ---
tab_proveedores = QWidget()
proveedores_layout = QVBoxLayout(tab_proveedores)
proveedores_layout.setSpacing(10)
proveedores_layout.setContentsMargins(10, 10, 10, 10)

# Panel de gestión de proveedores
proveedor_panel = QGroupBox("Gestión de Proveedores")
proveedor_layout = QVBoxLayout(proveedor_panel)

# Lista de proveedores
self.lista_proveedores = QTableWidget()
self.lista_proveedores.setColumnCount(3)
self.lista_proveedores.setHorizontalHeaderLabels(["Proveedor", "Contacto", "Herrajes Suministrados"])

# Aplicar estilos mejorados para tabla de proveedores
self.lista_proveedores.setStyleSheet("""
QTableWidget {
gridline-color: #666666;
background-color: #f8f9fa;
alternate-background-color: #e9ecef;
selection-background-color: #007bff;
selection-color: white;
border: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item {
padding: 8px;
border-bottom: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item:hover {
background-color: #e3f2fd;
}
QTableWidget::item:selected {
background-color: #007bff;
color: white;
}
QHeaderView::section {
background-color: #495057;
color: white;
padding: 8px;
border: 1px solid #343a40;
font-weight: bold;
}
""")
self.lista_proveedores.setAlternatingRowColors(True)
self.lista_proveedores.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

proveedor_layout.addWidget(self.lista_proveedores)

proveedores_layout.addWidget(proveedor_panel)
self.tabs.addTab(tab_proveedores, "Proveedores")

# --- Pestaña Estadísticas ---
tab_estadisticas = QWidget()
estadisticas_layout = QVBoxLayout(tab_estadisticas)
estadisticas_layout.setSpacing(10)
estadisticas_layout.setContentsMargins(10, 10, 10, 10)
stats_panel2 = self.crear_panel_estadisticas()
estadisticas_layout.addWidget(stats_panel2)
self.tabs.addTab(tab_estadisticas, "Estadísticas")

main_layout.addWidget(self.tabs)

# Aplicar estilos después de crear la interfaz
self.aplicar_estilos()

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

# Eliminar método crear_titulo (ya no se usa)

def crear_panel_control(self) -> QGroupBox:
        """Crea el panel de control con búsqueda y acciones."""
grupo = QGroupBox("Panel de Control")
layout = QVBoxLayout(grupo)
layout.setSpacing(10)

# Fila superior: Búsqueda y filtros
fila_busqueda = QHBoxLayout()

# Campo de búsqueda
self.input_busqueda = QLineEdit()
self.input_busqueda.setPlaceholderText("[SEARCH] Buscar herrajes por código, nombre o tipo...")
self.input_busqueda.setToolTip("Buscar herrajes por código, nombre, tipo o proveedor")
self.input_busqueda.setMinimumHeight(35)
fila_busqueda.addWidget(self.input_busqueda, 2)

# Filtro por categoría
self.combo_categoria = QComboBox()
self.combo_categoria.addItems([
"📂 Todas las categorías",
"🚪 Bisagras",
"🔐 Cerraduras",
"[TARGET] Manijas",
"[SETTINGS] Otros herrajes"
])
self.combo_categoria.setMinimumHeight(35)
self.combo_categoria.setToolTip("Filtrar herrajes por categoría")
fila_busqueda.addWidget(self.combo_categoria, 1)

layout.addLayout(fila_busqueda)

# Fila inferior: Botones de acción
botones_layout = QHBoxLayout()

# Crear botones básicos
self.btn_nuevo = self.crear_boton("➕ Nuevo Herraje", "primary")
self.btn_editar = self.crear_boton("✏️ Editar", "secondary")
self.btn_eliminar = self.crear_boton("🗑️ Eliminar", "danger")
self.btn_actualizar = self.crear_boton("🔄 Actualizar", "info")
# Conectar botones
self.btn_nuevo.clicked.connect(self.on_nuevo_herraje)
self.btn_editar.clicked.connect(self.on_editar_herraje)
self.btn_eliminar.clicked.connect(self.on_eliminar_herraje)
self.btn_actualizar.clicked.connect(self.on_actualizar_datos)

botones_layout.addWidget(self.btn_nuevo)
botones_layout.addWidget(self.btn_editar)
botones_layout.addWidget(self.btn_eliminar)
botones_layout.addWidget(self.btn_actualizar)

# Agregar botón de exportación estándar
self.add_export_button(botones_layout, "📄 Exportar Herrajes")
botones_layout.addStretch()

layout.addLayout(botones_layout)

# Conectar señales de búsqueda
self.input_busqueda.textChanged.connect(self.on_buscar)
self.combo_categoria.currentTextChanged.connect(self.on_filtrar_categoria)

return grupo

def crear_boton(self, texto: str, estilo: str) -> QPushButton:
        """Crea un botón con estilo específico."""
boton = QPushButton(texto)
boton.setMinimumHeight(30)

# Aplicar estilos según el tipo
if estilo == "primary":
        boton.setStyleSheet(f"""
QPushButton {{
background-color: {RexusColors.PRIMARY};
color: white;
border: none;
border-radius: 4px;
padding: 5px 15px;
font-weight: bold;
}}
QPushButton:hover {{
background-color: #0056b3;
}}
""")
elif estilo == "danger":
        boton.setStyleSheet(f"""
QPushButton {{
background-color: #dc3545;
color: white;
border: none;
border-radius: 4px;
padding: 5px 15px;
font-weight: bold;
}}
QPushButton:hover {{
background-color: #c82333;
}}
""")
elif estilo == "success":
        boton.setStyleSheet(f"""
QPushButton {{
background-color: #28a745;
color: white;
border: none;
border-radius: 4px;
padding: 5px 15px;
font-weight: bold;
}}
QPushButton:hover {{
background-color: #218838;
}}
""")
elif estilo == "info":
        boton.setStyleSheet(f"""
QPushButton {{
background-color: #17a2b8;
color: white;
border: none;
border-radius: 4px;
padding: 5px 15px;
font-weight: bold;
}}
QPushButton:hover {{
background-color: #138496;
}}
""")
else:  # secondary
boton.setStyleSheet(f"""
QPushButton {{
background-color: {RexusColors.SECONDARY};
color: white;
border: none;
border-radius: 4px;
padding: 5px 15px;
font-weight: bold;
}}
QPushButton:hover {{
background-color: #5a6268;
}}
""")

return boton

def crear_panel_estadisticas(self) -> QGroupBox:
        """Crea panel de estadísticas."""
grupo = QGroupBox("Estadísticas")
layout = QHBoxLayout(grupo)

# Crear estadísticas básicas
stats = [
("[TOOL]",
"Total Herrajes",
"total_herrajes",
RexusColors.PRIMARY),
("[PACKAGE]", "En Stock", "en_stock", "#28a745"),
("[WARN]", "Stock Bajo", "stock_bajo", "#ffc107"),
("🚫", "Sin Stock", "sin_stock", "#dc3545")
]

for icon, title, key, color in stats:
        stat_widget = self.crear_stat_widget(icon, title, "0", color)
self.stats_labels[key] = stat_widget.findChild(QLabel, "value_label")
layout.addWidget(stat_widget)

return grupo

def crear_stat_widget(self,
icon: str,
title: str,
value: str,
color: str) -> QWidget:
        """Crea un widget de estadística individual."""
widget = QWidget()
layout = QVBoxLayout(widget)
layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Icono y valor
icon_label = QLabel(f"{icon} {value}")
icon_label.setObjectName("value_label")
icon_label.setStyleSheet(f"""
QLabel {{
font-size: 24px;
font-weight: bold;
color: {color};
margin: 5px;
}}
""")
icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Título
title_label = QLabel(title)
title_label.setStyleSheet(f"""
QLabel {{
font-size: 12px;
color: {RexusColors.TEXT_SECONDARY};
margin: 2px;
}}
""")
title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

layout.addWidget(icon_label)
layout.addWidget(title_label)

widget.setStyleSheet(f"""
QWidget {{
border: 1px solid {RexusColors.BORDER_LIGHT};
border-radius: 6px;
background-color: {RexusColors.SURFACE};
margin: 2px;
padding: 10px;
}}
""")

return widget

def crear_tabla_herrajes(self, layout: QVBoxLayout):
        """Crea y configura la tabla de herrajes."""
# Grupo contenedor
grupo_tabla = QGroupBox("Lista de Herrajes")
tabla_layout = QVBoxLayout(grupo_tabla)

# Crear tabla
self.tabla_herrajes = QTableWidget()
self.configurar_tabla()
tabla_layout.addWidget(self.tabla_herrajes)

# Controles de paginación
paginacion_panel = self.crear_controles_paginacion()
tabla_layout.addWidget(paginacion_panel)

# Asignar referencia para exportación
self.tabla_principal = self.tabla_herrajes

layout.addWidget(grupo_tabla)

def configurar_tabla(self):
        """Configura la tabla de herrajes con estilo moderno y robusto."""
if not self.tabla_herrajes:
        return

columnas = [
"Código",
"Nombre",
"Tipo",
"Stock",
"Precio Unit.",
"Proveedor",
"Estado"
]
self.tabla_herrajes.setColumnCount(len(columnas))
self.tabla_herrajes.setHorizontalHeaderLabels(columnas)

# Configurar ancho de columnas solo si el header existe
header = self.tabla_herrajes.horizontalHeader()
if header is not None:
        try:
                header.setStretchLastSection(True)
header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
except Exception as e:
                logging.warning(f"No se pudo configurar el header de la tabla: {e}")

# Establecer anchos específicos
self.tabla_herrajes.setColumnWidth(0, 100)  # Código
self.tabla_herrajes.setColumnWidth(2, 120)  # Tipo
self.tabla_herrajes.setColumnWidth(3, 80)   # Stock
self.tabla_herrajes.setColumnWidth(4, 100)  # Precio

# Configurar comportamiento
self.tabla_herrajes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
self.tabla_herrajes.setAlternatingRowColors(True)
self.tabla_herrajes.setSortingEnabled(True)

# Aplicar estilos mejorados para mejor contraste
self.tabla_herrajes.setStyleSheet("""
QTableWidget {
gridline-color: #666666;
background-color: #f8f9fa;
alternate-background-color: #e9ecef;
selection-background-color: #007bff;
selection-color: white;
border: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item {
padding: 8px;
border-bottom: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item:hover {
background-color: #e3f2fd;
}
QTableWidget::item:selected {
background-color: #007bff;
color: white;
}
QHeaderView::section {
background-color: #495057;
color: white;
padding: 8px;
border: 1px solid #343a40;
font-weight: bold;
}
""")

# Conectar señales
self.tabla_herrajes.itemSelectionChanged.connect(self.on_seleccion_cambiada)
self.tabla_herrajes.itemDoubleClicked.connect(self.on_editar_herraje)

def configurar_tabla_obra(self):
        """Configura la tabla de herrajes por obra."""
if not self.tabla_herrajes_obra:
        return

columnas = ["Código", "Nombre", "Cantidad Requerida", "Cantidad Instalada", "Estado"]
self.tabla_herrajes_obra.setColumnCount(len(columnas))
self.tabla_herrajes_obra.setHorizontalHeaderLabels(columnas)

# Configurar comportamiento
self.tabla_herrajes_obra.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
self.tabla_herrajes_obra.setAlternatingRowColors(True)
self.tabla_herrajes_obra.setSortingEnabled(True)

# Aplicar estilos mejorados para mejor contraste
self.tabla_herrajes_obra.setStyleSheet("""
QTableWidget {
gridline-color: #666666;
background-color: #f8f9fa;
alternate-background-color: #e9ecef;
selection-background-color: #007bff;
selection-color: white;
border: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item {
padding: 8px;
border-bottom: 1px solid #dee2e6;
color: #212529;
}
QTableWidget::item:hover {
background-color: #e3f2fd;
}
QTableWidget::item:selected {
background-color: #007bff;
color: white;
}
QHeaderView::section {
background-color: #495057;
color: white;
padding: 8px;
border: 1px solid #343a40;
font-weight: bold;
}
""")

def showEvent(self, a0):
        """Carga los datos de herrajes al mostrar la vista."""
super().showEvent(a0)
if hasattr(self, 'controller') and self.controller:
        self.controller.cargar_datos_iniciales()

# El método on_actualizar_datos ya existe, no duplicar

# === MÉTODOS DE CONTROL ===

def aplicar_estilos_adicionales(self):
        """Aplica estilos adicionales si es necesario."""

# === MÉTODOS DE CONTROL ===

def set_controller(self, controller):
        """Establece el controlador."""
self.controller = controller

def mostrar_loading(self, mensaje: str = "Cargando herrajes..."):
        """Muestra indicador de carga."""
self.loading_manager.show_loading(self, mensaje)

def ocultar_loading(self):
        """Oculta indicador de carga."""
self.loading_manager.hide_loading()

# === SLOTS DE EVENTOS ===

def on_nuevo_herraje(self):
        """Maneja la creación de nuevo herraje."""
try:
        if self.controller and \
hasattr(self.controller, 'mostrar_dialogo_herraje'):
                self.controller.mostrar_dialogo_herraje()
else:
                show_warning(self, HerrajesConstants.FUNCIONALIDAD_NO_DISPONIBLE,
HerrajesConstants.MENSAJE_CREACION_PENDIENTE)
except Exception as e:
        logging.error(f"Error al abrir diálogo de nuevo herraje: {e}")
show_error(self, "Error", f"No se pudo abrir el formulario: {e}")

def on_editar_herraje(self):
        """Maneja la edición de herraje seleccionado."""
try:
        if not self.tabla_herrajes:
                return

selected_items = self.tabla_herrajes.selectedItems()
if not selected_items:
                show_warning(self, HerrajesConstants.SELECCION_REQUERIDA,
HerrajesConstants.SELECCIONAR_HERRAJE_EDITAR)
return

if self.controller and \
hasattr(self.controller, 'mostrar_dialogo_herraje'):
                row = selected_items[0].row()
herraje_data = self.obtener_datos_fila(row)
if herraje_data:
                self.controller.mostrar_dialogo_herraje(herraje_data)
else:
                show_warning(self, "Error", "No se pudieron obtener los datos del herraje.")
else:
                show_warning(self, HerrajesConstants.FUNCIONALIDAD_NO_DISPONIBLE,
HerrajesConstants.MENSAJE_EDICION_PENDIENTE)
except Exception as e:
        logging.error(f"Error al editar herraje: {e}")
show_error(self, "Error", f"No se pudo editar el herraje: {e}")

def on_eliminar_herraje(self):
        """Maneja la eliminación de herraje seleccionado."""
try:
        if not self.tabla_herrajes:
                return

selected_items = self.tabla_herrajes.selectedItems()
if not selected_items:
                show_warning(self, HerrajesConstants.SELECCION_REQUERIDA,
HerrajesConstants.SELECCIONAR_HERRAJE_ELIMINAR)
return

row = selected_items[0].row()
codigo_item = self.tabla_herrajes.item(row, 0)
nombre_item = self.tabla_herrajes.item(row, 1)

if not codigo_item or not nombre_item:
                show_warning(self, "Error", "No se pueden obtener los datos del herraje.")
return

codigo = codigo_item.text()
nombre = nombre_item.text()

if ask_question(self, "Confirmar eliminación",
f"¿Está seguro que desea eliminar el herraje '{nombre}' (Código: {codigo})?"):
                if self.controller and \
hasattr(self.controller, 'eliminar_herraje'):
                success = self.controller.eliminar_herraje(codigo)
if success:
                        self.on_actualizar_datos()  # Recargar tabla
else:
                show_warning(self, HerrajesConstants.FUNCIONALIDAD_NO_DISPONIBLE,
HerrajesConstants.MENSAJE_ELIMINACION_PENDIENTE)
except Exception as e:
        logging.error(f"Error al eliminar herraje: {e}")
show_error(self, "Error", f"No se pudo eliminar el herraje: {e}")

def on_actualizar_datos(self):
        """Actualiza los datos de la tabla."""
try:
        if self.controller and \
hasattr(self.controller, 'cargar_herrajes'):
                self.mostrar_loading("Actualizando datos...")
self.controller.cargar_herrajes()
self.ocultar_loading()
elif self.controller and \
hasattr(self.controller, 'cargar_datos_iniciales'):
                self.mostrar_loading("Actualizando datos...")
self.controller.cargar_datos_iniciales()
self.ocultar_loading()
else:
                show_warning(self, "Sin controlador", "No se puede actualizar sin controlador.")
except Exception as e:
        logging.error(f"Error al actualizar datos: {e}")
show_error(self, "Error", f"No se pudieron actualizar los datos: {e}")
self.ocultar_loading()

def on_exportar_datos(self):
        """Exporta los datos de herrajes."""
try:
        if self.controller and \
hasattr(self.controller, 'exportar_herrajes'):
                self.mostrar_loading("Exportando datos...")
self.controller.exportar_herrajes("excel")
self.ocultar_loading()
else:
                show_warning(self, HerrajesConstants.FUNCIONALIDAD_NO_DISPONIBLE,
HerrajesConstants.MENSAJE_EXPORTACION_PENDIENTE)
except Exception as e:
        logging.error(f"Error al exportar datos: {e}")
show_error(self, "Error", f"No se pudieron exportar los datos: {e}")
self.ocultar_loading()

def on_buscar(self, texto: str):
        """Maneja la búsqueda de herrajes con debounce."""
texto_limpio = texto.strip()

if not texto_limpio:
        self._cargar_todos_herrajes()
return

if len(texto_limpio) >= 2:
        self._ejecutar_busqueda(texto_limpio)

def _cargar_todos_herrajes(self):
        """Carga todos los herrajes cuando no hay filtro."""
if self.controller and hasattr(self.controller, 'cargar_herrajes'):
        self.controller.cargar_herrajes()

def _ejecutar_busqueda(self, texto: str):
        """Ejecuta la búsqueda con el controlador o localmente."""
try:
        if self._tiene_controlador_busqueda():
                self._buscar_con_controlador(texto)
else:
                self._filtrar_tabla_local(texto)
except Exception as e:
        logging.error(f"Error en búsqueda: {e}")

def _tiene_controlador_busqueda(self) -> bool:
        """Verifica si el controlador tiene capacidad de búsqueda."""
return (self.controller and 
hasattr(self.controller, 'buscar_herrajes'))

def _buscar_con_controlador(self, texto: str):
        """Realiza búsqueda usando el controlador."""
categoria = self._obtener_categoria_filtro()
self.controller.buscar_herrajes(texto, categoria)

def _obtener_categoria_filtro(self) -> str:
        """Obtiene la categoría seleccionada para filtrado."""
if not self.combo_categoria:
        return ""

categoria = self.combo_categoria.currentText()
# Limpiar categoria si es "Todas las categorías"
return "" if categoria.startswith("📂") else categoria

def on_filtrar_categoria(self, categoria: str):
        """Maneja el filtro por categoría."""
try:
        if self.controller and \
hasattr(self.controller, 'buscar_herrajes'):
                termino_busqueda = self.input_busqueda.text().strip() if self.input_busqueda else ""
# Limpiar categoria si es "Todas las categorías"
if categoria.startswith("📂"):
                categoria = ""
self.controller.buscar_herrajes(termino_busqueda, categoria)
else:
                # Filtrado local si no hay controlador
self._filtrar_tabla_local_por_categoria(categoria)
except Exception as e:
        logging.error(f"Error en filtrado por categoría: {e}")

def _filtrar_tabla_local(self, termino: str):
        """Filtra la tabla localmente por término de búsqueda."""
if not self.tabla_herrajes:
        return

termino_lower = termino.lower()
for row in range(self.tabla_herrajes.rowCount()):
        mostrar_fila = False

# Buscar en todas las columnas relevantes
for col in range(min(6, self.tabla_herrajes.columnCount())):  # Hasta la columna de proveedor
item = self.tabla_herrajes.item(row, col)
if item and termino_lower in item.text().lower():
                mostrar_fila = True
break

self.tabla_herrajes.setRowHidden(row, not mostrar_fila)

def _filtrar_tabla_local_por_categoria(self, categoria: str):
        """Filtra la tabla localmente por categoría."""
if not self.tabla_herrajes:
        return

if categoria.startswith("📂"):
        # Mostrar todas las filas si es "Todas las categorías"
for row in range(self.tabla_herrajes.rowCount()):
                self.tabla_herrajes.setRowHidden(row, False)
return

# Extraer la categoría real del texto con emoji
categoria_real = categoria.split(" ", 1)[1] if " " in categoria else categoria

for row in range(self.tabla_herrajes.rowCount()):
        tipo_item = self.tabla_herrajes.item(row, 2)  # Columna "Tipo"
if tipo_item:
                mostrar = categoria_real.lower() in tipo_item.text().lower()
self.tabla_herrajes.setRowHidden(row, not mostrar)
else:
                self.tabla_herrajes.setRowHidden(row, True)

def on_cargar_herrajes_obra(self):
        """Carga los herrajes asignados a la obra seleccionada."""
if not self.combo_obras or not self.controller:
        show_warning(self, "Error", "No se puede cargar la información de la obra.")
return

obra_text = self.combo_obras.currentText()
if not obra_text or obra_text == "Seleccione una obra...":
        show_warning(self, HerrajesConstants.SELECCION_REQUERIDA, HerrajesConstants.SELECCIONAR_OBRA)
return

# Extraer ID de obra del texto (formato: "ID - Nombre")
try:
        obra_id = int(obra_text.split(" - ")[0])
if hasattr(self.controller, 'cargar_herrajes_obra'):
                self.mostrar_loading("Cargando herrajes de obra...")
herrajes_obra = self.controller.cargar_herrajes_obra(obra_id)
self.cargar_herrajes_en_tabla_obra(herrajes_obra)
self.ocultar_loading()
else:
                show_warning(self, HerrajesConstants.FUNCIONALIDAD_NO_DISPONIBLE,
HerrajesConstants.MENSAJE_CARGA_OBRA_PENDIENTE)
except (ValueError, IndexError):
        show_warning(self, "Error", "Formato de obra no válido.")

def cargar_herrajes_en_tabla_obra(self, herrajes: List[Dict]):
        """Carga herrajes en la tabla de obra."""
if not self.tabla_herrajes_obra:
        return

try:
        self.tabla_herrajes_obra.setRowCount(len(herrajes))

for fila, herraje in enumerate(herrajes):
                # Código
self.tabla_herrajes_obra.setItem(fila,
0,
QTableWidgetItem(str(herraje.get("codigo",
""))))

# Nombre
self.tabla_herrajes_obra.setItem(fila,
1,
QTableWidgetItem(str(herraje.get("nombre",
""))))

# Cantidad requerida
cant_req = int(herraje.get("cantidad_requerida", 0))
self.tabla_herrajes_obra.setItem(fila, 2, QTableWidgetItem(str(cant_req)))

# Cantidad instalada
cant_inst = int(herraje.get("cantidad_instalada", 0))
self.tabla_herrajes_obra.setItem(fila, 3, QTableWidgetItem(str(cant_inst)))

# Estado con mejor contraste
if cant_inst >= cant_req:
                estado = "Completo"
bg_color = QColor(34, 139, 34)  # Verde bosque
text_color = QColor(255, 255, 255)  # Blanco
elif cant_inst > 0:
                estado = "Parcial"
bg_color = QColor(255, 165, 0)  # Naranja
text_color = QColor(0, 0, 0)  # Negro
else:
                estado = "Pendiente"
bg_color = QColor(180, 30, 30)  # Rojo oscuro
text_color = QColor(255, 255, 255)  # Blanco

estado_item = QTableWidgetItem(estado)
estado_item.setBackground(bg_color)
estado_item.setForeground(text_color)
self.tabla_herrajes_obra.setItem(fila, 4, estado_item)

except Exception as e:
        logging.error(f"Error cargando herrajes en tabla de obra: {e}")
show_error(self, "Error", f"No se pudieron cargar los herrajes de la obra: {e}")

def cargar_proveedores(self):
        """Carga la lista de proveedores."""
if not self.controller or not hasattr(self.controller, 'obtener_proveedores'):
        return

try:
        proveedores = self.controller.obtener_proveedores()
self.lista_proveedores.setRowCount(len(proveedores))

for fila, proveedor in enumerate(proveedores):
                self.lista_proveedores.setItem(fila,
0,
QTableWidgetItem(str(proveedor.get("nombre",
""))))
self.lista_proveedores.setItem(fila,
1,
QTableWidgetItem(str(proveedor.get("contacto",
""))))
self.lista_proveedores.setItem(fila,
2,
QTableWidgetItem(str(proveedor.get("herrajes_count",
0))))

except Exception as e:
        logging.error(f"Error cargando proveedores: {e}")

def on_seleccion_cambiada(self):
        """Maneja el cambio de selección en la tabla."""
if not self.tabla_herrajes:
        return

selected_items = self.tabla_herrajes.selectedItems()
if selected_items:
        row = selected_items[0].row()
herraje_data = self.obtener_datos_fila(row)
self.herraje_seleccionado.emit(herraje_data)

# === MÉTODOS DE DATOS ===

def cargar_herrajes(self, herrajes: List[Dict]):
        """Carga herrajes en la tabla con indicadores visuales."""
if not self.tabla_herrajes:
        return

try:
        self.tabla_herrajes.setRowCount(len(herrajes))

for fila, herraje in enumerate(herrajes):
                # Código
codigo = str(herraje.get("codigo", ""))
self.tabla_herrajes.setItem(fila, 0, QTableWidgetItem(codigo))

# Nombre
nombre = str(herraje.get("nombre", ""))
self.tabla_herrajes.setItem(fila, 1, QTableWidgetItem(nombre))

# Tipo
tipo = str(herraje.get("tipo", herraje.get("categoria", "")))
self.tabla_herrajes.setItem(fila, 2, QTableWidgetItem(tipo))

# Stock con colores de alto contraste
stock = int(herraje.get("stock_actual", herraje.get("stock", 0)))
stock_item = QTableWidgetItem(str(stock))

# Aplicar colores con mejor contraste
if stock == 0:
                # Rojo fuerte con texto blanco
stock_item.setBackground(QColor(180, 30, 30))  # Rojo oscuro
stock_item.setForeground(QColor(255, 255, 255))  # Blanco
elif stock <= 5:
                # Amarillo/naranja con texto negro
stock_item.setBackground(QColor(255, 165, 0))  # Naranja
stock_item.setForeground(QColor(0, 0, 0))  # Negro
else:
                # Verde con texto blanco
stock_item.setBackground(QColor(34, 139, 34))  # Verde bosque
stock_item.setForeground(QColor(255, 255, 255))  # Blanco

self.tabla_herrajes.setItem(fila, 3, stock_item)

# Precio
precio = float(herraje.get("precio_unitario", 0.0))
self.tabla_herrajes.setItem(fila, 4, QTableWidgetItem(f"${precio:,.2f}"))

# Proveedor
proveedor = str(herraje.get("proveedor", ""))
self.tabla_herrajes.setItem(fila, 5, QTableWidgetItem(proveedor))

# Estado con colores de alto contraste
activo = herraje.get("activo", 1)
estado = "Activo" if activo else "Inactivo"
estado_item = QTableWidgetItem(estado)
if activo:
                # Verde con texto blanco
estado_item.setBackground(QColor(34, 139, 34))  # Verde bosque
estado_item.setForeground(QColor(255, 255, 255))  # Blanco
else:
                # Gris con texto blanco
estado_item.setBackground(QColor(105, 105, 105))  # Gris oscuro
estado_item.setForeground(QColor(255, 255, 255))  # Blanco
self.tabla_herrajes.setItem(fila, 6, estado_item)

self.ocultar_loading()

except Exception as e:
        self.error_ocurrido.emit(f"Error cargando herrajes: {str(e)}")
show_error(
self,
"Error de datos",
f"No se pudieron cargar los herrajes: {str(e)}"
)
self.ocultar_loading()

def actualizar_estadisticas(self, stats: Dict):
        """Actualiza el panel de estadísticas."""
try:
        # Actualizar cada estadística
for key, value in stats.items():
                if key in self.stats_labels and self.stats_labels[key]:
                # Obtener el ícono del texto actual
current_text = self.stats_labels[key].text()
icon = current_text.split()[0] if current_text else "[CHART]"
self.stats_labels[key].setText(f"{icon} {value}")

except Exception as e:
        logging.error(f"Error actualizando estadísticas: {e}")

def obtener_datos_fila(self, row: int) -> Dict:
        """Obtiene los datos de una fila específica de forma robusta."""
if not self._es_fila_valida(row):
        return {}

try:
        return self._extraer_datos_fila(row)
except Exception as e:
        logging.error(f"Error obteniendo datos de fila {row}: {e}")
return {}

def _es_fila_valida(self, row: int) -> bool:
        """Verifica si la fila es válida para extracción de datos."""
return self.tabla_herrajes is not None and row >= 0

def _extraer_datos_fila(self, row: int) -> Dict:
        """Extrae los datos de una fila específica."""
columnas = ["codigo", "nombre", "tipo", "stock", "precio_unitario", "proveedor", "activo"]
data = {}

for col, key in enumerate(columnas):
        item = self.tabla_herrajes.item(row, col)
if item is not None:
                data[key] = self._convertir_valor_columna(key, item.text())

return data

def _convertir_valor_columna(self, key: str, text: str):
        """Convierte el valor de una columna al tipo apropiado."""
converters = {
"stock": self._convertir_a_entero,
"precio_unitario": self._convertir_a_precio,
"activo": lambda t: t == "Activo"
}

converter = converters.get(key, lambda t: t)
return converter(text)

def _convertir_a_entero(self, text: str) -> int:
        """Convierte texto a entero de forma segura."""
try:
        return int(text)
except (ValueError, TypeError) as e:
        logger.warning(f"Error convirtiendo stock a entero: {e}")
return 0

def _convertir_a_precio(self, text: str) -> float:
        """Convierte texto a precio de forma segura."""
try:
        precio_limpio = text.replace("$", "").replace(",", "")
return float(precio_limpio)
except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error convirtiendo precio a float: {e}")
return 0.0

# Método on_seleccion_cambiada ya existe más abajo, no duplicar

def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja detección de contenido peligroso."""
show_warning(
self,
"Contenido no permitido",
f"Se detectó contenido potencialmente peligroso en {field_name}. "
"Por favor revise su entrada."
)

# Limpiar el campo
if hasattr(self, "input_busqueda") and field_name == "busqueda" and self.input_busqueda:
        self.input_busqueda.clear()

# === MÉTODOS PÚBLICOS PARA COMPATIBILIDAD ===

def exportar_datos(self, formato: str = "excel"):
        """Exporta los datos de herrajes."""
if self.controller:
        self.mostrar_loading(f"Exportando a {formato.upper()}...")
self.controller.exportar_herrajes(formato)
else:
        show_warning(self, "Sin controlador", "El controlador no está disponible.")

def limpiar_datos(self):
        """Limpia todos los datos de la vista."""
if self.tabla_herrajes:
        self.tabla_herrajes.setRowCount(0)

if self.input_busqueda:
        self.input_busqueda.clear()

if self.combo_categoria:
        self.combo_categoria.setCurrentIndex(0)

def obtener_herrajes_seleccionados(self) -> List[Dict]:
        """Obtiene los herrajes actualmente seleccionados."""
if not self.tabla_herrajes:
        return []

selected_rows = set()
for item in self.tabla_herrajes.selectedItems():
        selected_rows.add(item.row())

return [self.obtener_datos_fila(row) for row in selected_rows]

# === MÉTODOS DE PAGINACIÓN ===

def crear_controles_paginacion(self) -> QWidget:
        """Crea los controles de paginación."""
from PyQt6.QtWidgets import QFrame, QSpinBox

panel = QFrame()
panel.setStyleSheet("""
QFrame {
background: #f8fafc;
border: 1px solid #e2e8f0;
border-radius: 6px;
max-height: 40px;
}
""")

layout = QHBoxLayout(panel)
layout.setContentsMargins(12, 4, 12, 4)
layout.setSpacing(8)

# Información de registros
self.info_label = QLabel("Mostrando 1-50 de 0 herrajes")
self.info_label.setStyleSheet("QLabel { color: #6b7280; font-size: 11px; }")
layout.addWidget(self.info_label)

layout.addStretch()

# Botones de navegación
self.btn_primera = QPushButton("⏮")
self.btn_primera.setMaximumWidth(30)
self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))
layout.addWidget(self.btn_primera)

self.btn_anterior = QPushButton("⏪")
self.btn_anterior.setMaximumWidth(30)
self.btn_anterior.clicked.connect(self.pagina_anterior)
layout.addWidget(self.btn_anterior)

# Control de página actual
self.pagina_actual_spin = QSpinBox()
self.pagina_actual_spin.setMinimum(1)
self.pagina_actual_spin.setMaximum(1)
self.pagina_actual_spin.valueChanged.connect(self.cambiar_pagina)
self.pagina_actual_spin.setMaximumWidth(60)
self.pagina_actual_spin.setStyleSheet("""
QSpinBox {
padding: 4px;
border: 1px solid #d1d5db;
border-radius: 4px;
font-size: 11px;
}
""")
layout.addWidget(QLabel("Pág."))
layout.addWidget(self.pagina_actual_spin)

self.total_paginas_label = QLabel("de 1")
self.total_paginas_label.setStyleSheet("QLabel { color: #6b7280; font-size: 11px; }")
layout.addWidget(self.total_paginas_label)

self.btn_siguiente = QPushButton("⏩")
self.btn_siguiente.setMaximumWidth(30)
self.btn_siguiente.clicked.connect(self.pagina_siguiente)
layout.addWidget(self.btn_siguiente)

self.btn_ultima = QPushButton("⏭")
self.btn_ultima.setMaximumWidth(30)
self.btn_ultima.clicked.connect(self.ultima_pagina)
layout.addWidget(self.btn_ultima)

# Selector de registros por página
layout.addWidget(QLabel("Items:"))
self.registros_por_pagina_combo = QComboBox()
self.registros_por_pagina_combo.addItems(["25", "50", "100", "200"])
self.registros_por_pagina_combo.setCurrentText("50")
self.registros_por_pagina_combo.currentTextChanged.connect(self.cambiar_registros_por_pagina)
self.registros_por_pagina_combo.setMaximumWidth(70)
self.registros_por_pagina_combo.setStyleSheet("""
QComboBox {
padding: 4px;
border: 1px solid #d1d5db;
border-radius: 4px;
font-size: 11px;
}
""")
layout.addWidget(self.registros_por_pagina_combo)

return panel

def actualizar_controles_paginacion(self, pagina_actual, total_paginas, total_registros, registros_mostrados):
        """Actualiza los controles de paginación."""
if hasattr(self, 'info_label'):
        inicio = ((pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())) + 1
fin = min(inicio + registros_mostrados - 1, total_registros)
self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} herrajes")

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
        """Va a una página específica."""
if hasattr(self.controller, 'cargar_pagina'):
        self.controller.cargar_pagina(pagina)

def pagina_anterior(self):
        """Va a la página anterior."""
if hasattr(self, 'pagina_actual_spin'):
        pagina_actual = self.pagina_actual_spin.value()
if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)

def pagina_siguiente(self):
        """Va a la página siguiente."""
if hasattr(self, 'pagina_actual_spin'):
        pagina_actual = self.pagina_actual_spin.value()
total_paginas = self.pagina_actual_spin.maximum()
if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)

def ultima_pagina(self):
        """Va a la última página."""
if hasattr(self, 'pagina_actual_spin'):
        total_paginas = self.pagina_actual_spin.maximum()
self.ir_a_pagina(total_paginas)

def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada."""
self.ir_a_pagina(pagina)

def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página."""
if hasattr(self.controller, 'cambiar_registros_por_pagina'):
        self.controller.cambiar_registros_por_pagina(int(registros))

def cargar_datos_en_tabla(self, datos):
        """Carga datos en la tabla de herrajes para paginación."""
self.cargar_herrajes(datos)  # Reutilizar el método existente
