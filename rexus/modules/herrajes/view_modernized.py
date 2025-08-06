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

Vista de Herrajes Modernizada - Interfaz de gestión de herrajes
Migrado a StandardComponents con UX mejorada
"""

import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Importar componentes modernos
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.utils.loading_manager import LoadingManager
from rexus.utils.message_system import ask_question, show_error, show_warning
from rexus.utils.xss_protection import FormProtector


class HerrajesViewModernized(QWidget):
    """Vista modernizada del módulo de herrajes usando StandardComponents."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    herraje_seleccionado = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.loading_manager = LoadingManager()

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        self.init_ui()
        self.configurar_navegacion()

    def init_ui(self):
        """Inicializa la interfaz de usuario moderna."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título simple
        self.crear_titulo(layout)

        # Panel de control básico
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Panel de estadísticas básico
        stats_panel = self.crear_panel_estadisticas()
        layout.addWidget(stats_panel)

        # Tabla básica
        from PyQt6.QtWidgets import QTableWidget

        self.tabla_herrajes = QTableWidget()
        self.configurar_tabla()
        layout.addWidget(self.tabla_herrajes)

        # Aplicar estilos básicos
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #6c757d;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Búsqueda estandarizada
        search_group = StandardComponents.create_search_group()
        self.input_busqueda = search_group.findChild(QLineEdit)
        self.input_busqueda.setPlaceholderText(
            "🔍 Buscar herrajes por código, nombre o tipo..."
        )
        self.input_busqueda.setToolTip(
            "🔍 Buscar herrajes por código, nombre, tipo o proveedor"
        )
        layout.addWidget(search_group)

        # Filtro por categoría
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(
            [
                "📂 Todas las categorías",
                "🚪 Bisagras",
                "🔐 Cerraduras",
                "🎯 Manijas",
                "⚙️ Otros herrajes",
            ]
        )
        self.combo_categoria.setToolTip("📂 Filtrar herrajes por categoría")
        layout.addWidget(self.combo_categoria)

        # Botones de acción estandarizados
        button_group = StandardComponents.create_action_button_group(
            [
                ("➕ Nuevo", "primary", self.on_nuevo_herraje),
                ("✏️ Editar", "secondary", self.on_editar_herraje),
                ("🗑️ Eliminar", "danger", self.on_eliminar_herraje),
                ("🔄 Actualizar", "info", self.on_actualizar_datos),
            ]
        )
        layout.addWidget(button_group)

        # Conectar señales
        self.input_busqueda.textChanged.connect(self.on_buscar)
        self.combo_categoria.currentTextChanged.connect(self.on_filtrar_categoria)

    def crear_panel_estadisticas(self):
        """Crea panel de estadísticas usando StandardComponents."""
        return StandardComponents.create_stats_panel(
            [
                {
                    "icon": "🔧",
                    "title": "Total Herrajes",
                    "value": "0",
                    "color": "#6c757d",
                    "id": "total_herrajes",
                },
                {
                    "icon": "📦",
                    "title": "En Stock",
                    "value": "0",
                    "color": "#28a745",
                    "id": "en_stock",
                },
                {
                    "icon": "⚠️",
                    "title": "Stock Bajo",
                    "value": "0",
                    "color": "#ffc107",
                    "id": "stock_bajo",
                },
                {
                    "icon": "🚫",
                    "title": "Sin Stock",
                    "value": "0",
                    "color": "#dc3545",
                    "id": "sin_stock",
                },
            ]
        )

    def configurar_tabla(self):
        """Configura la tabla de herrajes con estilo moderno."""
        # Configurar columnas
        columnas = [
            "Código",
            "Nombre",
            "Tipo",
            "Stock",
            "Precio Unit.",
            "Proveedor",
            "Estado",
        ]

        StandardComponents.configure_table(
            self.tabla_herrajes, columnas, [100, 200, 120, 80, 100, 150, 80]
        )

        # Conectar señales
        self.tabla_herrajes.itemSelectionChanged.connect(self.on_seleccion_cambiada)
        self.tabla_herrajes.itemDoubleClicked.connect(self.on_editar_herraje)

    def configurar_navegacion(self):
        """Configura navegación por teclado y shortcuts."""
        # Tab order lógico
        widgets_tab_order = [
            self.input_busqueda,
            self.combo_categoria,
            self.tabla_herrajes,
        ]

        for i in range(len(widgets_tab_order) - 1):
            self.setTabOrder(widgets_tab_order[i], widgets_tab_order[i + 1])

        # Shortcuts globales
        StandardComponents.setup_shortcuts(
            self,
            {
                "Ctrl+N": self.on_nuevo_herraje,
                "F3": lambda: self.input_busqueda.setFocus(),
                "Ctrl+R": self.on_actualizar_datos,
                "Delete": self.on_eliminar_herraje,
                "Enter": self.on_editar_herraje,
            },
        )

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
        if self.controller:
            self.controller.mostrar_dialogo_herraje()

    def on_editar_herraje(self):
        """Maneja la edición de herraje seleccionado."""
        selected_items = self.tabla_herrajes.selectedItems()
        if not selected_items:
            show_warning(
                self,
                "Selección requerida",
                "Por favor seleccione un herraje para editar.",
            )
            return

        if self.controller:
            row = selected_items[0].row()
            herraje_data = self.obtener_datos_fila(row)
            self.controller.mostrar_dialogo_herraje(herraje_data)

    def on_eliminar_herraje(self):
        """Maneja la eliminación de herraje seleccionado."""
        selected_items = self.tabla_herrajes.selectedItems()
        if not selected_items:
            show_warning(
                self,
                "Selección requerida",
                "Por favor seleccione un herraje para eliminar.",
            )
            return

        row = selected_items[0].row()
        codigo = self.tabla_herrajes.item(row, 0).text()
        nombre = self.tabla_herrajes.item(row, 1).text()

        if ask_question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el herraje '{nombre}' (Código: {codigo})?",
        ):
            if self.controller:
                self.controller.eliminar_herraje(codigo)

    def on_actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.mostrar_loading("Actualizando datos...")
            self.controller.cargar_herrajes()

    def on_buscar(self, texto: str):
        """Maneja la búsqueda de herrajes."""
        if self.controller and len(texto) >= 2:  # Buscar con mínimo 2 caracteres
            self.controller.buscar_herrajes(texto, self.combo_categoria.currentText())

    def on_filtrar_categoria(self, categoria: str):
        """Maneja el filtro por categoría."""
        if self.controller:
            termino_busqueda = self.input_busqueda.text()
            self.controller.buscar_herrajes(termino_busqueda, categoria)

    def on_seleccion_cambiada(self):
        """Maneja el cambio de selección en la tabla."""
        selected_items = self.tabla_herrajes.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            herraje_data = self.obtener_datos_fila(row)
            self.herraje_seleccionado.emit(herraje_data)

    # === MÉTODOS DE DATOS ===

    def cargar_herrajes(self, herrajes: list):
        """Carga herrajes en la tabla con indicadores visuales."""
        try:
            self.tabla_herrajes.setRowCount(len(herrajes))

            for fila, herraje in enumerate(herrajes):
                # Código
                self.tabla_herrajes.setItem(
                    fila, 0, QTableWidgetItem(str(herraje.get("codigo", "")))
                )

                # Nombre
                self.tabla_herrajes.setItem(
                    fila, 1, QTableWidgetItem(str(herraje.get("nombre", "")))
                )

                # Tipo
                self.tabla_herrajes.setItem(
                    fila, 2, QTableWidgetItem(str(herraje.get("tipo", "")))
                )

                # Stock con colores
                stock = herraje.get("stock", 0)
                stock_item = QTableWidgetItem(str(stock))
                stock_item = StandardComponents.create_colored_cell(
                    str(stock), self.get_stock_color(stock)
                )
                self.tabla_herrajes.setItem(fila, 3, stock_item)

                # Precio
                precio = herraje.get("precio_unitario", 0.0)
                self.tabla_herrajes.setItem(
                    fila, 4, QTableWidgetItem(f"${precio:,.2f}")
                )

                # Proveedor
                self.tabla_herrajes.setItem(
                    fila, 5, QTableWidgetItem(str(herraje.get("proveedor", "")))
                )

                # Estado
                estado = "Activo" if herraje.get("activo", True) else "Inactivo"
                estado_item = StandardComponents.create_status_cell(estado)
                self.tabla_herrajes.setItem(fila, 6, estado_item)

            self.ocultar_loading()

        except Exception as e:
            self.error_ocurrido.emit(f"Error cargando herrajes: {str(e)}")
            show_error(
                self, "Error de datos", f"No se pudieron cargar los herrajes: {str(e)}"
            )

    def actualizar_estadisticas(self, stats: dict):
        """Actualiza el panel de estadísticas."""
        try:
            StandardComponents.update_stats_panel(
                self.children(),
                {
                    "total_herrajes": str(stats.get("total", 0)),
                    "en_stock": str(stats.get("en_stock", 0)),
                    "stock_bajo": str(stats.get("stock_bajo", 0)),
                    "sin_stock": str(stats.get("sin_stock", 0)),
                },
            )
        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}")

    def obtener_datos_fila(self, row: int) -> dict:
        """Obtiene los datos de una fila específica."""
        return {
            "codigo": self.tabla_herrajes.item(row, 0).text(),
            "nombre": self.tabla_herrajes.item(row, 1).text(),
            "tipo": self.tabla_herrajes.item(row, 2).text(),
            "stock": int(self.tabla_herrajes.item(row, 3).text()),
            "precio_unitario": float(
                self.tabla_herrajes.item(row, 4)
                .text()
                .replace("$", "")
                .replace(",", "")
            ),
            "proveedor": self.tabla_herrajes.item(row, 5).text(),
            "activo": self.tabla_herrajes.item(row, 6).text() == "Activo",
        }

    def get_stock_color(self, stock: int) -> str:
        """Retorna el color apropiado según el nivel de stock."""
        if stock == 0:
            return "#dc3545"  # Rojo
        elif stock <= 5:
            return "#ffc107"  # Amarillo
        else:
            return "#28a745"  # Verde

    def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja detección de contenido peligroso."""
        show_warning(
            self,
            "Contenido no permitido",
            f"Se detectó contenido potencialmente peligroso en {field_name}. "
            "Por favor revise su entrada.",
        )

        # Limpiar el campo
        if hasattr(self, "input_busqueda") and field_name == "busqueda":
            self.input_busqueda.clear()

    # === MÉTODOS DE EXPORTACIÓN ===

    def exportar_datos(self, formato: str = "excel"):
        """Exporta los datos de herrajes."""
        if self.controller:
            self.mostrar_loading(f"Exportando a {formato.upper()}...")
            self.controller.exportar_herrajes(formato)
