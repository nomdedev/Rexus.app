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
"""

"""
Módulo Herrajes - Versión simplificada funcional
Gestión de herrajes para el sistema Rexus
"""

import os
import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

# Importaciones PyQt6
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Importaciones del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from rexus.utils.contextual_error_system import (
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
    contextual_error_manager,
    show_database_error,
    show_validation_error,
)
from rexus.utils.keyboard_navigation import KeyboardNavigationMode, setup_crud_shortcuts
from rexus.utils.loading_manager import LoadingManager
from rexus.utils.smart_tooltips import TooltipManager, add_custom_tooltip


class HerrajesViewSimple(QWidget):
    """Vista simplificada para el módulo de herrajes con interfaz moderna pero sin StandardComponents."""

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.loading_manager = LoadingManager()

        # Inicializar sistema de tooltips inteligentes
        self.tooltip_manager = TooltipManager()

        # Variables de estado
        self.herrajes_data = []
        self.current_page = 1
        self.items_per_page = 50
        self.total_pages = 1

        # Filtros activos
        self.active_filters = {}

        self.init_ui()
        self.setup_shortcuts()
        self.setup_keyboard_navigation()
        self.setup_smart_tooltips()  # Configurar tooltips inteligentes
        self.cargar_datos_iniciales()

    def setup_keyboard_navigation(self):
        """Configura la navegación por teclado completa."""
        # Configurar navegación CRUD con métodos seguros
        crud_callbacks = {
            "new": self.nuevo_herraje,
            "edit": self.editar_herraje,
            "delete": self.eliminar_herraje,
            "save": self.actualizar_datos_navegacion,  # Usar método específico
            "cancel": lambda: self.tabla_herrajes.clearSelection(),  # Limpiar selección
        }

        self.nav_manager = setup_crud_shortcuts(self, crud_callbacks)
        self.nav_manager.set_mode(KeyboardNavigationMode.TABLE)

        # Configurar atajos adicionales específicos del módulo
        self.nav_manager.register_action(
            "buscar_general", self._focus_search_general, ["Ctrl+F"]
        )
        self.nav_manager.register_action(
            "filtrar_tipo", self._focus_tipo_filter, ["Ctrl+T"]
        )
        self.nav_manager.register_action(
            "filtrar_stock", self._focus_stock_filter, ["Ctrl+K"]
        )

    def setup_smart_tooltips(self):
        """Configura tooltips inteligentes para todos los campos."""
        # Aplicar tooltips automáticos a todo el widget
        self.tooltip_manager.apply_smart_tooltips(self)

        # Configurar tooltips personalizados para campos específicos
        field_help = {
            "descripcion": {
                "title": "Descripción del Herraje",
                "content": "Nombre descriptivo del herraje. Incluya marca, modelo y características principales.",
                "examples": [
                    "Bisagra piano 40mm",
                    "Cerradura Yale 3 puntos",
                    "Manija cromada moderna",
                ],
                "shortcuts": ["Tab: Siguiente campo", "Shift+Tab: Campo anterior"],
            },
            "tipo": {
                "title": "Tipo de Herraje",
                "content": "Categoría del herraje según su función principal.",
                "examples": [
                    "Bisagra",
                    "Cerradura",
                    "Manija",
                    "Corredera",
                    "Picaporte",
                ],
                "shortcuts": ["↑↓: Navegar opciones", "Enter: Seleccionar"],
            },
            "marca": {
                "title": "Marca del Herraje",
                "content": "Fabricante o marca comercial del herraje.",
                "examples": ["Yale", "Philips", "Dorma", "Häfele", "Blum"],
                "shortcuts": ["Ctrl+F: Buscar", "F2: Editar"],
            },
            "precio": {
                "title": "Precio Unitario",
                "content": "Precio de venta por unidad en pesos argentinos. Use formato decimal con punto.",
                "examples": ["125.50", "89.99", "2500.00"],
                "shortcuts": ["Ctrl+C: Copiar", "Ctrl+V: Pegar"],
            },
            "stock": {
                "title": "Stock Disponible",
                "content": "Cantidad disponible en inventario. Debe ser un número entero positivo.",
                "examples": ["50", "125", "8"],
                "shortcuts": ["Ctrl+K: Filtrar por stock", "F5: Actualizar"],
            },
        }

        # Aplicar tooltips personalizados cuando se crean los campos
        QTimer.singleShot(100, lambda: self._apply_custom_tooltips(field_help))

    def _apply_custom_tooltips(self, field_help):
        """Aplica tooltips personalizados a campos específicos."""
        for field_name, help_data in field_help.items():
            # Buscar el widget por nombre de objeto
            widget = self.findChild(QLineEdit, field_name)
            if not widget:
                widget = self.findChild(QComboBox, field_name)

            if widget:
                add_custom_tooltip(
                    widget,
                    help_data["content"],
                    help_data["title"],
                    help_data.get("examples", []),
                    help_data.get("shortcuts", []),
                )

    def _focus_search_general(self):
        """Enfoca el campo de búsqueda general."""
        if hasattr(self, "campo_busqueda"):
            self.campo_busqueda.setFocus()
            self.campo_busqueda.selectAll()

    def _focus_tipo_filter(self):
        """Enfoca el filtro de tipo."""
        if hasattr(self, "combo_tipo"):
            self.combo_tipo.setFocus()

    def _focus_stock_filter(self):
        """Enfoca el filtro de stock."""
        if hasattr(self, "combo_stock"):
            self.combo_stock.setFocus()

    def mostrar_ayuda_atajos(self):
        """Muestra la ayuda de atajos de teclado."""
        from rexus.utils.keyboard_help import KeyboardHelpWidget

        KeyboardHelpWidget.show_help(self, self.nav_manager)

    def actualizar_datos_navegacion(self):
        """Método auxiliar para actualizar datos desde navegación por teclado."""
        self.cargar_datos_iniciales()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título
        self.crear_titulo(layout)

        # Panel principal dividido
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel superior con controles
        panel_superior = self.crear_panel_superior()
        splitter.addWidget(panel_superior)

        # Panel inferior con tabla
        panel_tabla = self.crear_panel_tabla()
        splitter.addWidget(panel_tabla)

        splitter.setSizes([200, 600])
        layout.addWidget(splitter)

        # Panel de estado
        self.crear_panel_estado(layout)

        # Aplicar estilos
        self.aplicar_estilos()

    def crear_titulo(self, layout):
        """Crea el título del módulo."""
        titulo_frame = QFrame()
        titulo_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #4a90e2, stop:1 #357abd);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        titulo_layout = QHBoxLayout(titulo_frame)

        titulo_label = QLabel("🔧 Gestión de Herrajes")
        titulo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }
        """)
        titulo_layout.addWidget(titulo_label)
        titulo_layout.addStretch()

        layout.addWidget(titulo_frame)

    def crear_panel_superior(self):
        """Crea el panel superior con controles y estadísticas."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)

        # Panel de búsqueda y filtros
        grupo_busqueda = QGroupBox("🔍 Búsqueda y Filtros")
        layout_busqueda = QVBoxLayout(grupo_busqueda)

        # Búsqueda rápida
        busqueda_layout = QHBoxLayout()
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText(
            "Buscar por código, nombre o proveedor..."
        )
        self.campo_busqueda.textChanged.connect(self.buscar_herrajes)

        self.btn_limpiar_busqueda = QPushButton("Limpiar")
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)

        busqueda_layout.addWidget(QLabel("Buscar:"))
        busqueda_layout.addWidget(self.campo_busqueda)
        busqueda_layout.addWidget(self.btn_limpiar_busqueda)
        layout_busqueda.addLayout(busqueda_layout)

        # Filtros rápidos
        filtros_layout = QHBoxLayout()

        # Filtro por tipo
        filtros_layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(
            ["Todos", "Bisagras", "Cerraduras", "Manijas", "Rieles", "Otros"]
        )
        self.combo_tipo.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.combo_tipo)

        # Filtro por stock
        filtros_layout.addWidget(QLabel("Stock:"))
        self.combo_stock = QComboBox()
        self.combo_stock.addItems(["Todos", "Con stock", "Stock bajo", "Sin stock"])
        self.combo_stock.currentTextChanged.connect(self.aplicar_filtros)
        filtros_layout.addWidget(self.combo_stock)

        layout_busqueda.addLayout(filtros_layout)
        layout.addWidget(grupo_busqueda)

        # Panel de acciones
        grupo_acciones = QGroupBox("⚡ Acciones Rápidas")
        layout_acciones = QVBoxLayout(grupo_acciones)

        acciones_layout = QHBoxLayout()

        self.btn_nuevo = QPushButton("➕ Nuevo Herraje")
        self.btn_nuevo.clicked.connect(self.nuevo_herraje)

        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.clicked.connect(self.editar_herraje)
        self.btn_editar.setEnabled(False)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_herraje)
        self.btn_eliminar.setEnabled(False)

        self.btn_stock = QPushButton("📦 Ajustar Stock")
        self.btn_stock.clicked.connect(self.ajustar_stock)
        self.btn_stock.setEnabled(False)

        acciones_layout.addWidget(self.btn_nuevo)
        acciones_layout.addWidget(self.btn_editar)
        acciones_layout.addWidget(self.btn_eliminar)
        acciones_layout.addWidget(self.btn_stock)
        layout_acciones.addLayout(acciones_layout)

        # Acciones adicionales
        acciones2_layout = QHBoxLayout()

        self.btn_importar = QPushButton("📥 Importar")
        self.btn_importar.clicked.connect(self.importar_datos)

        self.btn_exportar = QPushButton("📤 Exportar")
        self.btn_exportar.clicked.connect(self.exportar_datos)

        self.btn_reporte = QPushButton("[CHART] Reportes")
        self.btn_reporte.clicked.connect(self.generar_reporte)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)

        acciones2_layout.addWidget(self.btn_importar)
        acciones2_layout.addWidget(self.btn_exportar)
        acciones2_layout.addWidget(self.btn_reporte)
        acciones2_layout.addWidget(self.btn_actualizar)
        layout_acciones.addLayout(acciones2_layout)

        layout.addWidget(grupo_acciones)

        # Panel de estadísticas
        grupo_stats = self.crear_panel_estadisticas()
        layout.addWidget(grupo_stats)

        return widget

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas."""
        grupo_stats = QGroupBox("📈 Estadísticas")
        layout_stats = QVBoxLayout(grupo_stats)

        # Labels de estadísticas
        self.label_total = QLabel("Total de herrajes: 0")
        self.label_activos = QLabel("Activos: 0")
        self.label_stock_bajo = QLabel("Stock bajo: 0")
        self.label_valor_total = QLabel("Valor total: $0.00")

        layout_stats.addWidget(self.label_total)
        layout_stats.addWidget(self.label_activos)
        layout_stats.addWidget(self.label_stock_bajo)
        layout_stats.addWidget(self.label_valor_total)

        return grupo_stats

    def crear_panel_tabla(self):
        """Crea el panel con la tabla de herrajes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Tabla
        self.tabla_herrajes = QTableWidget()
        self.configurar_tabla()
        self.tabla_herrajes.itemSelectionChanged.connect(self.seleccion_cambiada)
        layout.addWidget(self.tabla_herrajes)

        # Panel de paginación
        paginacion_layout = QHBoxLayout()

        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_primera.clicked.connect(lambda: self.ir_a_pagina(1))

        self.btn_anterior = QPushButton("⏪ Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)

        self.label_pagina = QLabel("Página 1 de 1")

        self.btn_siguiente = QPushButton("Siguiente ⏩")
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)

        self.btn_ultima = QPushButton("Última ⏭️")
        self.btn_ultima.clicked.connect(self.ir_a_ultima_pagina)

        paginacion_layout.addWidget(self.btn_primera)
        paginacion_layout.addWidget(self.btn_anterior)
        paginacion_layout.addStretch()
        paginacion_layout.addWidget(self.label_pagina)
        paginacion_layout.addStretch()
        paginacion_layout.addWidget(self.btn_siguiente)
        paginacion_layout.addWidget(self.btn_ultima)

        layout.addLayout(paginacion_layout)

        return widget

    def crear_panel_estado(self, layout):
        """Crea el panel de estado inferior."""
        estado_frame = QFrame()
        estado_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 5px;
            }
        """)
        estado_layout = QHBoxLayout(estado_frame)

        self.label_estado = QLabel("Listo")
        self.label_registros = QLabel("0 registros")
        self.label_ultima_actualizacion = QLabel("Última actualización: --")

        estado_layout.addWidget(self.label_estado)
        estado_layout.addStretch()
        estado_layout.addWidget(self.label_registros)
        estado_layout.addWidget(QLabel("|"))
        estado_layout.addWidget(self.label_ultima_actualizacion)

        layout.addWidget(estado_frame)

    def configurar_tabla(self):
        """Configura la tabla de herrajes."""
        columnas = [
            "Código",
            "Nombre",
            "Tipo",
            "Stock",
            "Precio Unit.",
            "Proveedor",
            "Estado",
            "Última Act.",
        ]

        self.tabla_herrajes.setColumnCount(len(columnas))
        self.tabla_herrajes.setHorizontalHeaderLabels(columnas)

        # Configurar encabezados
        header = self.tabla_herrajes.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Código
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Tipo
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Stock
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Precio
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Proveedor
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Estado
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Última Act.

        # Tamaños de columnas
        self.tabla_herrajes.setColumnWidth(0, 80)
        self.tabla_herrajes.setColumnWidth(2, 100)
        self.tabla_herrajes.setColumnWidth(3, 60)
        self.tabla_herrajes.setColumnWidth(4, 100)
        self.tabla_herrajes.setColumnWidth(6, 80)
        self.tabla_herrajes.setColumnWidth(7, 100)

        # Propiedades de la tabla
        self.tabla_herrajes.setAlternatingRowColors(True)
        self.tabla_herrajes.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_herrajes.setSortingEnabled(True)

    def aplicar_estilos(self):
        """Aplica estilos CSS al widget."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #6c757d;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            
            QPushButton {
                background-color: #007bff;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:disabled {
                background-color: #6c757d;
            }
            
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)

    def setup_shortcuts(self):
        """Configura atajos de teclado."""
        shortcuts = {
            "Ctrl+N": self.nuevo_herraje,
            "Ctrl+E": self.editar_herraje,
            "Delete": self.eliminar_herraje,
            "F5": self.actualizar_datos,
            "Ctrl+F": lambda: self.campo_busqueda.setFocus(),
            "Escape": self.limpiar_busqueda,
        }

        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales."""
        self.loading_manager.show_loading(self, "Cargando herrajes...")

        # Simular carga de datos
        QTimer.singleShot(1000, self._cargar_datos_demo)

    def _cargar_datos_demo(self):
        """Carga datos de demostración."""
        self.herrajes_data = [
            {
                "codigo": "BIS001",
                "nombre": "Bisagra Piano 1.5m",
                "tipo": "Bisagras",
                "stock": 25,
                "precio_unitario": 45.50,
                "proveedor": "Herrajes del Sur",
                "activo": True,
                "ultima_actualizacion": "2024-01-15",
            },
            {
                "codigo": "CER002",
                "nombre": "Cerradura Multipunto",
                "tipo": "Cerraduras",
                "stock": 8,
                "precio_unitario": 125.00,
                "proveedor": "Security Plus",
                "activo": True,
                "ultima_actualizacion": "2024-01-14",
            },
            {
                "codigo": "MAN003",
                "nombre": "Manija Aluminio Cromada",
                "tipo": "Manijas",
                "stock": 0,
                "precio_unitario": 32.75,
                "proveedor": "Aluminio SA",
                "activo": True,
                "ultima_actualizacion": "2024-01-10",
            },
        ]

        self.actualizar_tabla()
        self.actualizar_estadisticas()
        self.loading_manager.hide_loading(self)
        self.actualizar_estado("Datos cargados correctamente")

    def actualizar_tabla(self):
        """Actualiza la tabla con los datos filtrados."""
        datos_filtrados = self.aplicar_filtros_datos()

        # Calcular paginación
        total_items = len(datos_filtrados)
        self.total_pages = max(
            1, (total_items + self.items_per_page - 1) // self.items_per_page
        )

        # Obtener datos de la página actual
        inicio = (self.current_page - 1) * self.items_per_page
        fin = inicio + self.items_per_page
        datos_pagina = datos_filtrados[inicio:fin]

        # Llenar tabla
        self.tabla_herrajes.setRowCount(len(datos_pagina))

        for row, herraje in enumerate(datos_pagina):
            # Validar que el item no sea None antes de usar .text()
            items = [
                QTableWidgetItem(str(herraje.get("codigo", ""))),
                QTableWidgetItem(str(herraje.get("nombre", ""))),
                QTableWidgetItem(str(herraje.get("tipo", ""))),
                QTableWidgetItem(str(herraje.get("stock", 0))),
                QTableWidgetItem(f"${herraje.get('precio_unitario', 0):.2f}"),
                QTableWidgetItem(str(herraje.get("proveedor", ""))),
                QTableWidgetItem("Activo" if herraje.get("activo") else "Inactivo"),
                QTableWidgetItem(str(herraje.get("ultima_actualizacion", ""))),
            ]

            for col, item in enumerate(items):
                if item is not None:
                    self.tabla_herrajes.setItem(row, col, item)

                    # Colorear según stock
                    if col == 3:  # Columna stock
                        stock = herraje.get("stock", 0)
                        if stock == 0:
                            item.setBackground(Qt.GlobalColor.red)
                            item.setForeground(Qt.GlobalColor.white)
                        elif stock < 10:
                            item.setBackground(Qt.GlobalColor.yellow)

        # Actualizar paginación
        self.actualizar_paginacion()

    def aplicar_filtros_datos(self):
        """Aplica los filtros activos a los datos."""
        datos = self.herrajes_data.copy()

        # Filtro de búsqueda
        busqueda = self.campo_busqueda.text().lower()
        if busqueda:
            datos = [
                h
                for h in datos
                if (
                    busqueda in h.get("codigo", "").lower()
                    or busqueda in h.get("nombre", "").lower()
                    or busqueda in h.get("proveedor", "").lower()
                )
            ]

        # Filtro por tipo
        tipo = self.combo_tipo.currentText()
        if tipo and tipo != "Todos":
            datos = [h for h in datos if h.get("tipo") == tipo]

        # Filtro por stock
        stock_filter = self.combo_stock.currentText()
        if stock_filter == "Con stock":
            datos = [h for h in datos if h.get("stock", 0) > 0]
        elif stock_filter == "Stock bajo":
            datos = [h for h in datos if 0 < h.get("stock", 0) < 10]
        elif stock_filter == "Sin stock":
            datos = [h for h in datos if h.get("stock", 0) == 0]

        return datos

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas."""
        total = len(self.herrajes_data)
        activos = len([h for h in self.herrajes_data if h.get("activo")])
        stock_bajo = len([h for h in self.herrajes_data if 0 < h.get("stock", 0) < 10])
        valor_total = sum(
            h.get("precio_unitario", 0) * h.get("stock", 0) for h in self.herrajes_data
        )

        self.label_total.setText(f"Total de herrajes: {total}")
        self.label_activos.setText(f"Activos: {activos}")
        self.label_stock_bajo.setText(f"Stock bajo: {stock_bajo}")
        self.label_valor_total.setText(f"Valor total: ${valor_total:,.2f}")

    def actualizar_paginacion(self):
        """Actualiza los controles de paginación."""
        self.label_pagina.setText(f"Página {self.current_page} de {self.total_pages}")

        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado."""
        self.label_estado.setText(mensaje)
        self.label_registros.setText(f"{len(self.herrajes_data)} registros")
        self.label_ultima_actualizacion.setText(
            f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"
        )

    # Métodos de eventos
    def seleccion_cambiada(self):
        """Maneja el cambio de selección en la tabla."""
        hay_seleccion = len(self.tabla_herrajes.selectedItems()) > 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)
        self.btn_stock.setEnabled(hay_seleccion)

    def buscar_herrajes(self):
        """Busca herrajes según el texto ingresado."""
        self.current_page = 1
        self.actualizar_tabla()

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        self.current_page = 1
        self.actualizar_tabla()

    def limpiar_busqueda(self):
        """Limpia la búsqueda y filtros."""
        self.campo_busqueda.clear()
        self.combo_tipo.setCurrentIndex(0)
        self.combo_stock.setCurrentIndex(0)
        self.current_page = 1
        self.actualizar_tabla()

    # Métodos de paginación
    def ir_a_pagina(self, pagina):
        """Va a una página específica."""
        if 1 <= pagina <= self.total_pages:
            self.current_page = pagina
            self.actualizar_tabla()

    def pagina_anterior(self):
        """Va a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        """Va a la página siguiente."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.actualizar_tabla()

    def ir_a_ultima_pagina(self):
        """Va a la última página."""
        self.current_page = self.total_pages
        self.actualizar_tabla()

    # Métodos de acciones
    def nuevo_herraje(self):
        """Abre el diálogo para crear un nuevo herraje."""
        contextual_error_manager.show_error(
            "E7002",  # Error de lógica de negocio
            {
                "product_type": "Herraje",
                "price": "N/A",
                "min_price": "0",
                "max_price": "1000",
            },
            self,
            "herrajes",
        )

    def editar_herraje(self):
        """Edita el herraje seleccionado."""
        row = self.tabla_herrajes.currentRow()
        if row >= 0:
            # Verificar que los items existan antes de acceder
            codigo_item = self.tabla_herrajes.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                contextual_error_manager.show_error(
                    "E1001",  # Campo obligatorio vacío
                    {"field_name": f"código {codigo}"},
                    self,
                    "herrajes",
                )

    def eliminar_herraje(self):
        """Elimina el herraje seleccionado."""
        row = self.tabla_herrajes.currentRow()
        if row >= 0:
            codigo_item = self.tabla_herrajes.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                # Mostrar confirmación usando el sistema contextual
                contextual_error_manager.show_error(
                    "E2003",  # Registro no encontrado
                    {"record_id": codigo},
                    self,
                    "herrajes",
                )
        else:
            contextual_error_manager.show_error(
                "E1001",  # Campo obligatorio vacío
                {"field_name": "selección de herraje"},
                self,
                "herrajes",
            )

    def ajustar_stock(self):
        """Ajusta el stock del herraje seleccionado."""
        row = self.tabla_herrajes.currentRow()
        if row >= 0:
            codigo_item = self.tabla_herrajes.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                QMessageBox.information(
                    self, "Ajustar Stock", f"Ajustando stock de: {codigo}"
                )

    def importar_datos(self):
        """Importa datos desde archivo."""
        QMessageBox.information(
            self, "Importar", "Funcionalidad de importación en desarrollo"
        )

    def exportar_datos(self):
        """Exporta datos a archivo."""
        QMessageBox.information(
            self, "Exportar", "Funcionalidad de exportación en desarrollo"
        )

    def generar_reporte(self):
        """Genera reportes."""
        QMessageBox.information(
            self, "Reportes", "Funcionalidad de reportes en desarrollo"
        )

    def actualizar_datos(self):
        """Actualiza los datos desde la base de datos."""
        self.loading_manager.show_loading(self, "Actualizando datos...")
        QTimer.singleShot(
            1000,
            lambda: (
                self.loading_manager.hide_loading(self),
                self.actualizar_estado("Datos actualizados"),
            ),
        )


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    vista = HerrajesViewSimple()
    vista.show()
    sys.exit(app.exec())
