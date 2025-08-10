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

Vista Principal de Herrajes - Interfaz moderna de gestión de herrajes
Migrado a StandardComponents con UX mejorada y soporte para temas
"""

import logging
from typing import Optional, Dict, List

from PyQt6.QtCore import pyqtSignal, Qt
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
)

# Importar componentes modernos
from rexus.ui.components.base_components import RexusColors
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.utils.loading_manager import LoadingManager
from rexus.utils.message_system import ask_question, show_error, show_warning
from rexus.utils.xss_protection import FormProtector
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class HerrajesView(QWidget):
    """Vista principal del módulo de herrajes con UI/UX modernizada."""

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

        # Referencias a widgets importantes
        self.tabla_herrajes = None
        self.input_busqueda = None
        self.combo_categoria = None
        self.stats_panel = None

        self.init_ui()
        self.configurar_navegacion()
        self.aplicar_tema()

    def init_ui(self):
        """Inicializa la interfaz de usuario moderna."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Título del módulo
        self.crear_titulo(layout)

        # Panel de control con búsqueda y filtros
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Panel de estadísticas
        self.stats_panel = self.crear_panel_estadisticas()
        layout.addWidget(self.stats_panel)

        # Tabla de herrajes
        self.crear_tabla_herrajes(layout)

    def crear_titulo(self, layout: QVBoxLayout):
        """Crea el título del módulo."""
        title_widget = StandardComponents.create_module_header(
            "🔧 Gestión de Herrajes",
            "Administración de herrajes, stock y proveedores"
        )
        layout.addWidget(title_widget)

    def crear_panel_control(self) -> QGroupBox:
        """Crea el panel de control con búsqueda y acciones."""
        grupo = QGroupBox("Panel de Control")
        layout = QVBoxLayout(grupo)
        layout.setSpacing(10)

        # Fila superior: Búsqueda y filtros
        fila_busqueda = QHBoxLayout()
        
        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar herrajes por código, nombre o tipo...")
        self.input_busqueda.setToolTip("Buscar herrajes por código, nombre, tipo o proveedor")
        self.input_busqueda.setMinimumHeight(35)
        fila_busqueda.addWidget(self.input_busqueda, 2)

        # Filtro por categoría
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "📂 Todas las categorías",
            "🚪 Bisagras",
            "🔐 Cerraduras", 
            "🎯 Manijas",
            "⚙️ Otros herrajes"
        ])
        self.combo_categoria.setMinimumHeight(35)
        self.combo_categoria.setToolTip("Filtrar herrajes por categoría")
        fila_busqueda.addWidget(self.combo_categoria, 1)

        layout.addLayout(fila_busqueda)

        # Fila inferior: Botones de acción
        botones_layout = QHBoxLayout()
        
        # Crear botones usando StandardComponents
        botones = [
            ("➕ Nuevo Herraje", "primary", self.on_nuevo_herraje),
            ("✏️ Editar", "secondary", self.on_editar_herraje),
            ("🗑️ Eliminar", "danger", self.on_eliminar_herraje),
            ("🔄 Actualizar", "info", self.on_actualizar_datos),
            ("[CHART] Exportar", "success", self.on_exportar_datos)
        ]

        for texto, estilo, funcion in botones:
            boton = StandardComponents.create_button(texto, estilo)
            boton.clicked.connect(funcion)
            botones_layout.addWidget(boton)

        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Conectar señales
        self.input_busqueda.textChanged.connect(self.on_buscar)
        self.combo_categoria.currentTextChanged.connect(self.on_filtrar_categoria)

        return grupo

    def crear_panel_estadisticas(self) -> QWidget:
        """Crea panel de estadísticas usando StandardComponents."""
        return StandardComponents.create_stats_panel([
            {
                "icon": "🔧",
                "title": "Total Herrajes",
                "value": "0",
                "color": RexusColors.PRIMARY,
                "id": "total_herrajes"
            },
            {
                "icon": "📦", 
                "title": "En Stock",
                "value": "0",
                "color": RexusColors.SUCCESS,
                "id": "en_stock"
            },
            {
                "icon": "[WARN]",
                "title": "Stock Bajo", 
                "value": "0",
                "color": RexusColors.WARNING,
                "id": "stock_bajo"
            },
            {
                "icon": "🚫",
                "title": "Sin Stock",
                "value": "0", 
                "color": RexusColors.DANGER,
                "id": "sin_stock"
            }
        ])

    def crear_tabla_herrajes(self, layout: QVBoxLayout):
        """Crea y configura la tabla de herrajes."""
        # Grupo contenedor
        grupo_tabla = QGroupBox("Lista de Herrajes")
        tabla_layout = QVBoxLayout(grupo_tabla)

        # Crear tabla
        self.tabla_herrajes = QTableWidget()
        self.configurar_tabla()
        tabla_layout.addWidget(self.tabla_herrajes)

        layout.addWidget(grupo_tabla)

    def configurar_tabla(self):
        """Configura la tabla de herrajes con estilo moderno."""
        if not self.tabla_herrajes:
            return

        # Configurar columnas
        columnas = [
            "Código",
            "Nombre", 
            "Tipo",
            "Stock",
            "Precio Unit.",
            "Proveedor",
            "Estado"
        ]

        StandardComponents.configure_table(
            self.tabla_herrajes, 
            columnas,
            [100, 200, 120, 80, 100, 150, 80]
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
            self.tabla_herrajes
        ]

        for i in range(len(widgets_tab_order) - 1):
            if widgets_tab_order[i] and widgets_tab_order[i + 1]:
                self.setTabOrder(widgets_tab_order[i], widgets_tab_order[i + 1])

        # Shortcuts globales
        StandardComponents.setup_shortcuts(self, {
            "Ctrl+N": self.on_nuevo_herraje,
            "F3": lambda: self.input_busqueda.setFocus() if self.input_busqueda else None,
            "Ctrl+R": self.on_actualizar_datos,
            "Delete": self.on_eliminar_herraje,
            "Enter": self.on_editar_herraje
        })

    def aplicar_tema(self):
        """Aplica el tema actual al widget."""
        try:
            # Obtener colores del tema actual
            bg_color = RexusColors.BACKGROUND
            text_color = RexusColors.TEXT_PRIMARY
            border_color = RexusColors.BORDER_LIGHT

            # Aplicar estilos responsive al tema
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 15px;
                    background-color: {bg_color};
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 8px;
                    color: {RexusColors.PRIMARY};
                    font-size: 14px;
                }}

                QLineEdit {{
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    background-color: {RexusColors.SURFACE};
                }}

                QLineEdit:focus {{
                    border: 2px solid {RexusColors.PRIMARY};
                }}

                QComboBox {{
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    background-color: {RexusColors.SURFACE};
                }}

                QTableWidget {{
                    gridline-color: {border_color};
                    background-color: {RexusColors.SURFACE};
                    alternate-background-color: {RexusColors.BACKGROUND};
                    selection-background-color: {RexusColors.PRIMARY};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                }}

                QHeaderView::section {{
                    background-color: {RexusColors.PRIMARY};
                    color: white;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)

            logging.info("Tema aplicado correctamente al módulo Herrajes")

        except Exception as e:
            logging.error(f"Error aplicando tema en Herrajes: {e}")

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
        else:
            show_warning(self, "Sin controlador", "El controlador no está disponible.")

    def on_editar_herraje(self):
        """Maneja la edición de herraje seleccionado."""
        if not self.tabla_herrajes:
            return

        selected_items = self.tabla_herrajes.selectedItems()
        if not selected_items:
            show_warning(
                self,
                "Selección requerida",
                "Por favor seleccione un herraje para editar."
            )
            return

        if self.controller:
            row = selected_items[0].row()
            herraje_data = self.obtener_datos_fila(row)
            self.controller.mostrar_dialogo_herraje(herraje_data)
        else:
            show_warning(self, "Sin controlador", "El controlador no está disponible.")

    def on_eliminar_herraje(self):
        """Maneja la eliminación de herraje seleccionado."""
        if not self.tabla_herrajes:
            return

        selected_items = self.tabla_herrajes.selectedItems()
        if not selected_items:
            show_warning(
                self,
                "Selección requerida", 
                "Por favor seleccione un herraje para eliminar."
            )
            return

        row = selected_items[0].row()
        codigo = self.tabla_herrajes.item(row, 0).text()
        nombre = self.tabla_herrajes.item(row, 1).text()

        if ask_question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el herraje '{nombre}' (Código: {codigo})?"
        ):
            if self.controller:
                self.controller.eliminar_herraje(codigo)
            else:
                show_warning(self, "Sin controlador", "El controlador no está disponible.")

    def on_actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.mostrar_loading("Actualizando datos...")
            self.controller.cargar_herrajes()
        else:
            show_warning(self, "Sin controlador", "El controlador no está disponible.")

    def on_exportar_datos(self):
        """Exporta los datos de herrajes."""
        if self.controller:
            self.mostrar_loading("Exportando datos...")
            self.controller.exportar_herrajes("excel")
        else:
            show_warning(self, "Sin controlador", "El controlador no está disponible.")

    def on_buscar(self, texto: str):
        """Maneja la búsqueda de herrajes."""
        if self.controller and len(texto) >= 2:  # Buscar con mínimo 2 caracteres
            categoria = self.combo_categoria.currentText() if self.combo_categoria else ""
            self.controller.buscar_herrajes(texto, categoria)

    def on_filtrar_categoria(self, categoria: str):
        """Maneja el filtro por categoría."""
        if self.controller:
            termino_busqueda = self.input_busqueda.text() if self.input_busqueda else ""
            self.controller.buscar_herrajes(termino_busqueda, categoria)

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
                stock = int(herraje.get("stock", 0))
                stock_item = QTableWidgetItem(str(stock))
                
                # Aplicar color según nivel de stock
                if stock == 0:
                    stock_item.setBackground(Qt.GlobalColor.red)
                elif stock <= 5:
                    stock_item.setBackground(Qt.GlobalColor.yellow)
                else:
                    stock_item.setBackground(Qt.GlobalColor.green)
                    
                self.tabla_herrajes.setItem(fila, 3, stock_item)

                # Precio
                precio = float(herraje.get("precio_unitario", 0.0))
                self.tabla_herrajes.setItem(
                    fila, 4, QTableWidgetItem(f"${precio:,.2f}")
                )

                # Proveedor
                self.tabla_herrajes.setItem(
                    fila, 5, QTableWidgetItem(str(herraje.get("proveedor", "")))
                )

                # Estado
                estado = "Activo" if herraje.get("activo", True) else "Inactivo"
                estado_item = QTableWidgetItem(estado)
                if estado == "Activo":
                    estado_item.setBackground(Qt.GlobalColor.green)
                else:
                    estado_item.setBackground(Qt.GlobalColor.gray)
                self.tabla_herrajes.setItem(fila, 6, estado_item)

            self.ocultar_loading()

        except Exception as e:
            self.error_ocurrido.emit(f"Error cargando herrajes: {str(e)}")
            show_error(
                self, 
                "Error de datos", 
                f"No se pudieron cargar los herrajes: {str(e)}"
            )

    def actualizar_estadisticas(self, stats: Dict):
        """Actualiza el panel de estadísticas."""
        try:
            if self.stats_panel:
                StandardComponents.update_stats_panel(
                    self.stats_panel,
                    {
                        "total_herrajes": str(stats.get("total", 0)),
                        "en_stock": str(stats.get("en_stock", 0)),
                        "stock_bajo": str(stats.get("stock_bajo", 0)),
                        "sin_stock": str(stats.get("sin_stock", 0))
                    }
                )
        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}")

    def obtener_datos_fila(self, row: int) -> Dict:
        """Obtiene los datos de una fila específica."""
        if not self.tabla_herrajes or row < 0:
            return {}

        try:
            return {
                "codigo": self.tabla_herrajes.item(row, 0).text() if self.tabla_herrajes.item(row, 0) else "",
                "nombre": self.tabla_herrajes.item(row, 1).text() if self.tabla_herrajes.item(row, 1) else "",
                "tipo": self.tabla_herrajes.item(row, 2).text() if self.tabla_herrajes.item(row, 2) else "",
                "stock": int(self.tabla_herrajes.item(row, 3).text()) if self.tabla_herrajes.item(row, 3) else 0,
                "precio_unitario": float(
                    self.tabla_herrajes.item(row, 4).text().replace("$", "").replace(",", "")
                ) if self.tabla_herrajes.item(row, 4) else 0.0,
                "proveedor": self.tabla_herrajes.item(row, 5).text() if self.tabla_herrajes.item(row, 5) else "",
                "activo": self.tabla_herrajes.item(row, 6).text() == "Activo" if self.tabla_herrajes.item(row, 6) else True
            }
        except Exception as e:
            logging.error(f"Error obteniendo datos de fila {row}: {e}")
            return {}

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
