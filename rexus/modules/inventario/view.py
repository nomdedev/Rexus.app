# 🔒 Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control

# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check

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

Vista de Inventario

Interfaz de usuario moderna para la gestión del inventario con sistema de reservas.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.xss_protection import FormProtector

# Importar sistemas de mejora UI/UX
try:
    from rexus.ui.contextual_error_system import contextual_error_system
    from rexus.ui.keyboard_navigation import keyboard_navigation
    from rexus.ui.smart_tooltips import smart_tooltips

    ENHANCED_UI_AVAILABLE = True
except ImportError:
    ENHANCED_UI_AVAILABLE = False


class InventarioView(QWidget):
    """Vista principal del módulo de inventario."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título estandarizado
        StandardComponents.create_title("📦 Gestión de Inventario", layout)

        # Panel de control estandarizado
        control_panel = StandardComponents.create_control_panel()
        self.setup_control_panel(control_panel)
        layout.addWidget(control_panel)

        # Panel de estadísticas
        stats_panel = self.crear_panel_estadisticas()
        layout.addWidget(stats_panel)

        # Tabla estandarizada
        self.tabla_inventario = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_inventario)

        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)

        # Integrar smart tooltips si está disponible
        if ENHANCED_UI_AVAILABLE:
            self._integrate_smart_tooltips()
            self._setup_keyboard_navigation()
        else:
            self._setup_basic_tooltips()
            self._setup_basic_navigation()

    def _integrate_smart_tooltips(self):
        """Integra tooltips inteligentes en todos los controles."""
        try:
            # Tooltips contextuales para controles principales
            smart_tooltips.add_contextual_tooltip(
                self.btn_nuevo_producto,
                "Crear Producto",
                "Abre el formulario para registrar un nuevo producto en el inventario. Se solicitará código, descripción, categoría, precio y stock inicial.",
                "💡 Tip: Use códigos únicos para evitar duplicados",
            )

            smart_tooltips.add_contextual_tooltip(
                self.input_busqueda,
                "Búsqueda Inteligente",
                "Busque productos por código, descripción o categoría. Soporte para búsqueda parcial y filtros avanzados.",
                "🔍 Ejemplos: 'VID001', 'cristal', 'herrajes'",
            )

            smart_tooltips.add_contextual_tooltip(
                self.combo_categoria,
                "Filtro de Categoría",
                "Filtre productos por categoría específica para una búsqueda más rápida y organizada.",
                "📂 Use 'Todas' para ver inventario completo",
            )

        except Exception as e:
            print(f"[WARNING] Error integrando smart tooltips: {e}")
            self._setup_basic_tooltips()

    def _setup_basic_tooltips(self):
        """Configura tooltips básicos como fallback."""
        self.btn_nuevo_producto.setToolTip(
            "➕ Crear un nuevo producto en el inventario"
        )
        self.input_busqueda.setToolTip(
            "🔍 Buscar productos por código, descripción o categoría"
        )
        self.combo_categoria.setToolTip("📂 Filtrar productos por categoría")
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de inventario")
        self.btn_editar.setToolTip("✏️ Editar producto seleccionado")
        self.btn_eliminar.setToolTip("🗑️ Eliminar producto seleccionado")

    def _setup_keyboard_navigation(self):
        """Configura navegación por teclado avanzada."""
        try:
            keyboard_navigation.setup_tab_order(
                self,
                [
                    self.btn_nuevo_producto,
                    self.input_busqueda,
                    self.combo_categoria,
                    self.btn_buscar,
                    self.btn_actualizar,
                    self.tabla_inventario,
                    self.btn_editar,
                    self.btn_eliminar,
                ],
            )
        except Exception as e:
            print(f"[WARNING] Error configurando navegación por teclado: {e}")
            self._setup_basic_navigation()

    def _setup_basic_navigation(self):
        """Configura navegación básica por teclado."""
        # Configuración básica de tab order
        self.setTabOrder(self.btn_nuevo_producto, self.input_busqueda)
        self.setTabOrder(self.input_busqueda, self.combo_categoria)
        self.setTabOrder(self.combo_categoria, self.btn_buscar)
        self.setTabOrder(self.btn_buscar, self.btn_actualizar)
        self.setTabOrder(self.btn_actualizar, self.tabla_inventario)
        self.setTabOrder(self.tabla_inventario, self.btn_editar)
        self.setTabOrder(self.btn_editar, self.btn_eliminar)

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Botón Nuevo Producto estandarizado
        self.btn_nuevo_producto = StandardComponents.create_primary_button(
            "➕ Nuevo Producto"
        )
        layout.addWidget(self.btn_nuevo_producto)

        # Campo de búsqueda con tooltip mejorado
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar por código o descripción...")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #28a745;
            }
        """)
        layout.addWidget(self.input_busqueda)

        # Filtro de categoría con tooltips
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(
            [
                "📂 Todas las categorías",
                "🔧 Herramientas",
                "🪟 Vidrios",
                "🔩 Herrajes",
                "🧱 Materiales",
                "⚡ Eléctricos",
                "🚰 Plomería",
            ]
        )
        self.combo_categoria.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 180px;
            }
            QComboBox:focus {
                border-color: #28a745;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 12px;
                height: 12px;
            }
        """)
        layout.addWidget(self.combo_categoria)

        # Botones estandarizados
        self.btn_buscar = StandardComponents.create_secondary_button("🔍 Buscar")
        layout.addWidget(self.btn_buscar)

        self.btn_actualizar = StandardComponents.create_secondary_button(
            "🔄 Actualizar"
        )
        layout.addWidget(self.btn_actualizar)

        # Separador y botones de acción
        layout.addStretch()

        self.btn_editar = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_editar.setEnabled(False)
        layout.addWidget(self.btn_editar)

        self.btn_eliminar = StandardComponents.create_danger_button("🗑️ Eliminar")
        self.btn_eliminar.setEnabled(False)
        layout.addWidget(self.btn_eliminar)

        # Botones adicionales que el controlador requiere
        self.btn_limpiar = StandardComponents.create_secondary_button("🧹 Limpiar")
        layout.addWidget(self.btn_limpiar)

        self.btn_movimiento = StandardComponents.create_primary_button("📦 Movimiento")
        layout.addWidget(self.btn_movimiento)

        self.btn_exportar = StandardComponents.create_secondary_button("📤 Exportar")
        layout.addWidget(self.btn_exportar)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas del inventario."""
        panel = QGroupBox("📊 Estadísticas de Inventario")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #17a2b8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #17a2b8;
            }
        """)

        layout = QHBoxLayout(panel)

        # Total productos
        self.lbl_total_productos = self.crear_stat_widget(
            "📦", "Total Productos", "0", "#17a2b8"
        )
        layout.addWidget(self.lbl_total_productos)

        # Stock bajo
        self.lbl_stock_bajo = self.crear_stat_widget("⚠️", "Stock Bajo", "0", "#ffc107")
        layout.addWidget(self.lbl_stock_bajo)

        # Sin stock
        self.lbl_sin_stock = self.crear_stat_widget("❌", "Sin Stock", "0", "#dc3545")
        layout.addWidget(self.lbl_sin_stock)

        # Valor total
        self.lbl_valor_total = self.crear_stat_widget(
            "💰", "Valor Total", "$0.00", "#28a745"
        )
        layout.addWidget(self.lbl_valor_total)

        return panel

    def crear_stat_widget(self, icono, titulo, valor, color):
        """Crea un widget de estadística individual."""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8f9fa;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono y título
        header_layout = QHBoxLayout()

        icono_lbl = QLabel(icono)
        icono_lbl.setStyleSheet(f"font-size: 18px; color: {color};")
        header_layout.addWidget(icono_lbl)

        titulo_lbl = QLabel(titulo)
        titulo_lbl.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
        header_layout.addWidget(titulo_lbl)

        layout.addLayout(header_layout)

        # Valor
        valor_lbl = QLabel(valor)
        valor_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        valor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(valor_lbl)

        # Guardar referencia al label del valor para actualizar
        setattr(widget, "valor_label", valor_lbl)

        return widget

    def configurar_tabla(self):
        """Configura la tabla de inventario con estilos modernos."""
        self.tabla_inventario.setColumnCount(8)
        self.tabla_inventario.setHorizontalHeaderLabels(
            [
                "📋 Código",
                "📝 Descripción",
                "📂 Categoría",
                "📦 Stock",
                "💰 Precio",
                "📊 Estado",
                "📅 Última Actualización",
                "⚡ Acciones",
            ]
        )

        # Configurar tamaños de columnas
        header = self.tabla_inventario.horizontalHeader()
        if header:  # Verificar que header existe
            header.resizeSection(0, 100)  # Código
            header.resizeSection(1, 200)  # Descripción
            header.resizeSection(2, 130)  # Categoría
            header.resizeSection(3, 80)  # Stock
            header.resizeSection(4, 100)  # Precio
            header.resizeSection(5, 100)  # Estado
            header.resizeSection(6, 140)  # Última Actualización
            header.setStretchLastSection(True)  # Acciones

        # Configuraciones visuales
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_inventario.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Estilos de tabla modernos
        self.tabla_inventario.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #0066cc;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
        """)

        # Conectar señal de selección
        self.tabla_inventario.itemSelectionChanged.connect(
            self.on_producto_seleccionado
        )

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        # Estados de botones principales
        self.btn_nuevo_producto.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)

        # Estados de botones de acción
        selected = self.tabla_inventario.currentRow() >= 0
        self.btn_editar.setEnabled(not loading and selected)
        self.btn_eliminar.setEnabled(not loading and selected)

        # Cambiar textos durante loading
        if loading:
            self.btn_actualizar.setText("⏳ Actualizando...")
            self.btn_buscar.setText("🔍 Buscando...")
        else:
            self.btn_actualizar.setText("🔄 Actualizar")
            self.btn_buscar.setText("🔍 Buscar")

    def on_producto_seleccionado(self):
        """Maneja la selección de productos en la tabla."""
        hay_seleccion = self.tabla_inventario.currentRow() >= 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas mostradas en el panel."""
        try:
            if hasattr(self.lbl_total_productos, "valor_label"):
                self.lbl_total_productos.valor_label.setText(
                    str(stats.get("total_productos", 0))
                )

            if hasattr(self.lbl_stock_bajo, "valor_label"):
                self.lbl_stock_bajo.valor_label.setText(str(stats.get("stock_bajo", 0)))

            if hasattr(self.lbl_sin_stock, "valor_label"):
                self.lbl_sin_stock.valor_label.setText(str(stats.get("sin_stock", 0)))

            if hasattr(self.lbl_valor_total, "valor_label"):
                valor_total = stats.get("valor_total", 0.0)
                self.lbl_valor_total.valor_label.setText(f"${valor_total:,.2f}")

        except Exception as e:
            show_error(
                self, "Error de Estadísticas", f"Error actualizando estadísticas: {e}"
            )

    def cargar_productos_en_tabla(self, productos):
        """Carga productos en la tabla con estilos modernos."""
        try:
            self.tabla_inventario.setRowCount(len(productos))

            for fila, producto in enumerate(productos):
                # Código
                self.tabla_inventario.setItem(
                    fila, 0, QTableWidgetItem(str(producto.get("codigo", "")))
                )

                # Descripción
                self.tabla_inventario.setItem(
                    fila, 1, QTableWidgetItem(str(producto.get("descripcion", "")))
                )

                # Categoría
                categoria_item = QTableWidgetItem(str(producto.get("categoria", "")))
                self.tabla_inventario.setItem(fila, 2, categoria_item)

                # Stock con indicador visual
                stock = producto.get("stock", 0)
                stock_item = QTableWidgetItem(str(stock))

                # Colorear según nivel de stock
                if stock == 0:
                    stock_item.setBackground(
                        QColor("#ffebee")
                    )  # Rojo claro para sin stock
                    stock_item.setForeground(QColor("#c62828"))
                elif stock <= 5:  # Stock bajo
                    stock_item.setBackground(QColor("#fff3e0"))  # Naranja claro
                    stock_item.setForeground(QColor("#ef6c00"))
                else:
                    stock_item.setBackground(QColor("#e8f5e8"))  # Verde claro
                    stock_item.setForeground(QColor("#2e7d32"))

                self.tabla_inventario.setItem(fila, 3, stock_item)

                # Precio
                precio = producto.get("precio_unitario", 0.0)
                self.tabla_inventario.setItem(
                    fila, 4, QTableWidgetItem(f"${precio:,.2f}")
                )

                # Estado
                estado = producto.get("estado", "ACTIVO")
                estado_item = QTableWidgetItem(estado)

                if estado == "ACTIVO":
                    estado_item.setBackground(QColor("#e8f5e8"))
                    estado_item.setForeground(QColor("#2e7d32"))
                elif estado == "INACTIVO":
                    estado_item.setBackground(QColor("#ffebee"))
                    estado_item.setForeground(QColor("#c62828"))

                self.tabla_inventario.setItem(fila, 5, estado_item)

                # Última actualización
                fecha_actualizacion = producto.get("fecha_actualizacion", "")
                if fecha_actualizacion:
                    if isinstance(fecha_actualizacion, str):
                        fecha_actualizacion = fecha_actualizacion[
                            :16
                        ]  # YYYY-MM-DD HH:MM
                self.tabla_inventario.setItem(
                    fila, 6, QTableWidgetItem(str(fecha_actualizacion))
                )

                # Botón de acciones
                btn_acciones = QPushButton("👁️ Ver Detalles")
                btn_acciones.setStyleSheet("""
                    QPushButton {
                        background-color: #17a2b8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #138496;
                    }
                """)
                btn_acciones.clicked.connect(
                    lambda checked,
                    prod_id=producto.get("id"): self.mostrar_detalles_producto(prod_id)
                )
                self.tabla_inventario.setCellWidget(fila, 7, btn_acciones)

        except Exception as e:
            show_error(
                self, "Error de Tabla", f"Error cargando productos en tabla: {e}"
            )

    def mostrar_detalles_producto(self, producto_id):
        """Muestra los detalles de un producto."""
        try:
            if hasattr(self, "controller") and self.controller:
                producto = self.controller.obtener_producto_por_id(producto_id)
                if producto:
                    detalles = f"""
                    📋 Código: {producto.get("codigo", "N/A")}
                    📝 Descripción: {producto.get("descripcion", "N/A")}
                    📂 Categoría: {producto.get("categoria", "N/A")}
                    📦 Stock Actual: {producto.get("stock", 0)} unidades
                    💰 Precio Unitario: ${producto.get("precio_unitario", 0):,.2f}
                    📊 Estado: {producto.get("estado", "N/A")}
                    🏪 Ubicación: {producto.get("ubicacion", "Sin especificar")}
                    📅 Última Actualización: {producto.get("fecha_actualizacion", "N/A")}
                    """

                    show_success(self, "Detalles del Producto", f"{detalles}")

        except Exception as e:
            show_error(
                self, "Error de Producto", f"Error mostrando detalles del producto: {e}"
            )

    def _on_dangerous_content(self, campo, contenido):
        """Maneja detección de contenido peligroso XSS."""
        show_warning(
            self,
            "Contenido Peligroso",
            f"⚠️ Contenido potencialmente peligroso detectado en {campo}: {contenido[:50]}...",
        )

    def obtener_producto_seleccionado(self):
        """Obtiene los datos del producto seleccionado."""
        fila_seleccionada = self.tabla_inventario.currentRow()
        if fila_seleccionada >= 0:
            codigo_item = self.tabla_inventario.item(fila_seleccionada, 0)
            if codigo_item and hasattr(self, "controller") and self.controller:
                codigo = codigo_item.text()
                return self.controller.obtener_producto_por_codigo(codigo)
        return None

    def cargar_inventario_en_tabla(self, productos):
        """Método alternativo para cargar productos en la tabla."""
        self.cargar_productos_en_tabla(productos)

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
        self.registros_por_pagina_combo.currentTextChanged.connect(
            self.cambiar_registros_por_pagina
        )
        paginacion_layout.addWidget(self.registros_por_pagina_combo)

        return paginacion_layout

    def actualizar_controles_paginacion(
        self, pagina_actual, total_paginas, total_registros, registros_mostrados
    ):
        """Actualiza los controles de paginación"""
        if hasattr(self, "info_label"):
            inicio = (
                (pagina_actual - 1) * int(self.registros_por_pagina_combo.currentText())
            ) + 1
            fin = min(inicio + registros_mostrados - 1, total_registros)
            self.info_label.setText(
                f"Mostrando {inicio}-{fin} de {total_registros} registros"
            )

        if hasattr(self, "pagina_actual_spin"):
            self.pagina_actual_spin.blockSignals(True)
            self.pagina_actual_spin.setValue(pagina_actual)
            self.pagina_actual_spin.setMaximum(max(1, total_paginas))
            self.pagina_actual_spin.blockSignals(False)

        if hasattr(self, "total_paginas_label"):
            self.total_paginas_label.setText(f"de {total_paginas}")

        # Habilitar/deshabilitar botones
        if hasattr(self, "btn_primera"):
            self.btn_primera.setEnabled(pagina_actual > 1)
            self.btn_anterior.setEnabled(pagina_actual > 1)
            self.btn_siguiente.setEnabled(pagina_actual < total_paginas)
            self.btn_ultima.setEnabled(pagina_actual < total_paginas)

    def ir_a_pagina(self, pagina):
        """Va a una página específica"""
        if (
            hasattr(self, "controller")
            and self.controller
            and hasattr(self.controller, "cargar_pagina")
        ):
            self.controller.cargar_pagina(pagina)

    def pagina_anterior(self):
        """Va a la página anterior"""
        if hasattr(self, "pagina_actual_spin"):
            pagina_actual = self.pagina_actual_spin.value()
            if pagina_actual > 1:
                self.ir_a_pagina(pagina_actual - 1)

    def pagina_siguiente(self):
        """Va a la página siguiente"""
        if hasattr(self, "pagina_actual_spin"):
            pagina_actual = self.pagina_actual_spin.value()
            total_paginas = self.pagina_actual_spin.maximum()
            if pagina_actual < total_paginas:
                self.ir_a_pagina(pagina_actual + 1)

    def ultima_pagina(self):
        """Va a la última página"""
        if hasattr(self, "pagina_actual_spin"):
            total_paginas = self.pagina_actual_spin.maximum()
            self.ir_a_pagina(total_paginas)

    def cambiar_pagina(self, pagina):
        """Cambia a la página seleccionada"""
        self.ir_a_pagina(pagina)

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página"""
        if (
            hasattr(self, "controller")
            and self.controller
            and hasattr(self.controller, "cambiar_registros_por_pagina")
        ):
            self.controller.cambiar_registros_por_pagina(int(registros))

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller

    def actualizar_tabla(self, productos):
        """Actualiza la tabla con lista de productos."""
        if not hasattr(self, "tabla_inventario") or not self.tabla_inventario:
            print("❌ tabla_inventario no disponible")
            return

        try:
            self.tabla_inventario.setRowCount(len(productos))

            for row, producto in enumerate(productos):
                if isinstance(producto, dict):
                    # Columnas: Código, Descripción, Categoría, Stock, Precio
                    codigo = str(producto.get("codigo", f"PROD{row + 1}"))
                    descripcion = str(
                        producto.get("descripcion", f"Producto {row + 1}")
                    )
                    categoria = str(producto.get("categoria", "General"))
                    stock = str(producto.get("stock", 0))
                    precio = str(producto.get("precio", 0.0))

                    from PyQt6.QtWidgets import QTableWidgetItem

                    self.tabla_inventario.setItem(row, 0, QTableWidgetItem(codigo))
                    self.tabla_inventario.setItem(row, 1, QTableWidgetItem(descripcion))
                    self.tabla_inventario.setItem(row, 2, QTableWidgetItem(categoria))
                    self.tabla_inventario.setItem(row, 3, QTableWidgetItem(stock))
                    self.tabla_inventario.setItem(row, 4, QTableWidgetItem(precio))

            print(f"✅ Tabla actualizada con {len(productos)} productos")

        except Exception as e:
            print(f"❌ Error actualizando tabla: {e}")
            import traceback

            traceback.print_exc()

    def mostrar_productos(self, productos):
        """Alias para actualizar_tabla."""
        self.actualizar_tabla(productos)

    def cargar_datos(self, datos):
        """Otro alias para actualizar_tabla."""
        self.actualizar_tabla(datos)
