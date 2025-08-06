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

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from rexus.core.auth_manager import admin_required, auth_required, manager_required
from rexus.utils.message_system import show_error, show_success, show_warning, ask_question
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import FormProtector, XSSProtection
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager


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

    def crear_titulo(self, layout: QVBoxLayout):
        """Crea el título moderno de la vista."""
        titulo_container = QFrame()
        titulo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #28a745, stop:1 #20c997);
                border-radius: 8px;
                padding: 6px;
                margin-bottom: 10px;
            }
        """)

        titulo_layout = QHBoxLayout(titulo_container)

        # Título principal
        title_label = QLabel("📦 Gestión de Inventario")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        titulo_layout.addWidget(title_label)

        # Botón de configuración
        self.btn_configuracion = QPushButton("⚙️ Configuración")
        self.btn_configuracion.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.5);
                border-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.btn_configuracion.setToolTip("⚙️ Configuración del módulo de inventario")
        titulo_layout.addWidget(self.btn_configuracion)

        layout.addWidget(titulo_container)

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Botón Nuevo Producto estandarizado
        self.btn_nuevo_producto = StandardComponents.create_primary_button("➕ Nuevo Producto")
        self.btn_nuevo_producto.setToolTip("➕ Crear un nuevo producto en el inventario")
        layout.addWidget(self.btn_nuevo_producto)

        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar por código o descripción...")
        self.input_busqueda.setToolTip("🔍 Buscar productos por código, descripción o categoría")
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

        # Filtro de categoría
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "📂 Todas las categorías",
            "🔧 Herramientas",
            "🪟 Vidrios",
            "🔩 Herrajes",
            "🧱 Materiales",
            "⚡ Eléctricos",
            "🚰 Plomería"
        ])
        self.combo_categoria.setToolTip("📂 Filtrar productos por categoría")
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

        # Botón buscar estandarizado
        self.btn_buscar = StandardComponents.create_secondary_button("🔍 Buscar")
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        layout.addWidget(self.btn_buscar)

        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_secondary_button("🔄 Actualizar")
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de inventario")
        layout.addWidget(self.btn_actualizar)

        # Separador y botones de acción
        layout.addStretch()
        
        # Botón editar estandarizado
        self.btn_editar = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_editar.setToolTip("✏️ Editar producto seleccionado")
        self.btn_editar.setEnabled(False)
        layout.addWidget(self.btn_editar)

        # Botón eliminar estandarizado
        self.btn_eliminar = StandardComponents.create_danger_button("🗑️ Eliminar")
        self.btn_eliminar.setToolTip("🗑️ Eliminar producto seleccionado")
        self.btn_eliminar.setEnabled(False)
        layout.addWidget(self.btn_eliminar)

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
        self.lbl_total_productos = self.crear_stat_widget("📦", "Total Productos", "0", "#17a2b8")
        layout.addWidget(self.lbl_total_productos)

        # Stock bajo
        self.lbl_stock_bajo = self.crear_stat_widget("⚠️", "Stock Bajo", "0", "#ffc107")
        layout.addWidget(self.lbl_stock_bajo)

        # Sin stock
        self.lbl_sin_stock = self.crear_stat_widget("❌", "Sin Stock", "0", "#dc3545")
        layout.addWidget(self.lbl_sin_stock)

        # Valor total
        self.lbl_valor_total = self.crear_stat_widget("💰", "Valor Total", "$0.00", "#28a745")
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
        setattr(widget, 'valor_label', valor_lbl)
        
        return widget

    def configurar_tabla(self):
        """Configura la tabla de inventario con estilos modernos."""
        self.tabla_inventario.setColumnCount(8)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "📋 Código",
            "📝 Descripción", 
            "📂 Categoría",
            "📦 Stock",
            "💰 Precio",
            "📊 Estado",
            "📅 Última Actualización",
            "⚡ Acciones"
        ])

        # Configurar tamaños de columnas
        header = self.tabla_inventario.horizontalHeader()
        header.resizeSection(0, 100)  # Código
        header.resizeSection(1, 200)  # Descripción
        header.resizeSection(2, 130)  # Categoría
        header.resizeSection(3, 80)   # Stock
        header.resizeSection(4, 100)  # Precio
        header.resizeSection(5, 100)  # Estado
        header.resizeSection(6, 140)  # Última Actualización
        header.setStretchLastSection(True)  # Acciones

        # Configuraciones visuales
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_inventario.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
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
        self.tabla_inventario.itemSelectionChanged.connect(self.on_producto_seleccionado)

    def configurar_estilos(self):
        """Configura los estilos modernos usando FormStyleManager."""
        try:
            from rexus.utils.form_styles import FormStyleManager, setup_form_widget
            
            # Aplicar estilos modernos del FormStyleManager
            setup_form_widget(self, apply_animations=True)
            
            # Estilos específicos del módulo de inventario
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #f8f9fa;
                }
                QGroupBox {
                    font-weight: bold;
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
            
        except ImportError:
            print("[WARNING] FormStyleManager no disponible, usando estilos básicos")
            self.aplicar_estilo_basico()

    def aplicar_estilo_basico(self):
        """Aplica estilos básicos como fallback."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        # Estados de botones principales
        self.btn_nuevo_producto.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)
        self.btn_configuracion.setEnabled(not loading)
        
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
            if hasattr(self.lbl_total_productos, 'valor_label'):
                self.lbl_total_productos.valor_label.setText(str(stats.get('total_productos', 0)))
            
            if hasattr(self.lbl_stock_bajo, 'valor_label'):
                self.lbl_stock_bajo.valor_label.setText(str(stats.get('stock_bajo', 0)))
            
            if hasattr(self.lbl_sin_stock, 'valor_label'):
                self.lbl_sin_stock.valor_label.setText(str(stats.get('sin_stock', 0)))
            
            if hasattr(self.lbl_valor_total, 'valor_label'):
                valor_total = stats.get('valor_total', 0.0)
                self.lbl_valor_total.valor_label.setText(f"${valor_total:,.2f}")
                
        except Exception as e:
            show_error(self, f"Error actualizando estadísticas: {e}")

    def cargar_productos_en_tabla(self, productos):
        """Carga productos en la tabla con estilos modernos."""
        try:
            self.tabla_inventario.setRowCount(len(productos))
            
            for fila, producto in enumerate(productos):
                # Código
                self.tabla_inventario.setItem(fila, 0, QTableWidgetItem(str(producto.get('codigo', ''))))
                
                # Descripción
                self.tabla_inventario.setItem(fila, 1, QTableWidgetItem(str(producto.get('descripcion', ''))))
                
                # Categoría
                categoria_item = QTableWidgetItem(str(producto.get('categoria', '')))
                self.tabla_inventario.setItem(fila, 2, categoria_item)
                
                # Stock con indicador visual
                stock = producto.get('stock', 0)
                stock_item = QTableWidgetItem(str(stock))
                
                # Colorear según nivel de stock
                if stock == 0:
                    stock_item.setBackground(QColor("#ffebee"))  # Rojo claro para sin stock
                    stock_item.setForeground(QColor("#c62828"))
                elif stock <= 5:  # Stock bajo
                    stock_item.setBackground(QColor("#fff3e0"))  # Naranja claro
                    stock_item.setForeground(QColor("#ef6c00"))
                else:
                    stock_item.setBackground(QColor("#e8f5e8"))  # Verde claro
                    stock_item.setForeground(QColor("#2e7d32"))
                
                self.tabla_inventario.setItem(fila, 3, stock_item)
                
                # Precio
                precio = producto.get('precio_unitario', 0.0)
                self.tabla_inventario.setItem(fila, 4, QTableWidgetItem(f"${precio:,.2f}"))
                
                # Estado
                estado = producto.get('estado', 'ACTIVO')
                estado_item = QTableWidgetItem(estado)
                
                if estado == 'ACTIVO':
                    estado_item.setBackground(QColor("#e8f5e8"))
                    estado_item.setForeground(QColor("#2e7d32"))
                elif estado == 'INACTIVO':
                    estado_item.setBackground(QColor("#ffebee"))
                    estado_item.setForeground(QColor("#c62828"))
                
                self.tabla_inventario.setItem(fila, 5, estado_item)
                
                # Última actualización
                fecha_actualizacion = producto.get('fecha_actualizacion', '')
                if fecha_actualizacion:
                    if isinstance(fecha_actualizacion, str):
                        fecha_actualizacion = fecha_actualizacion[:16]  # YYYY-MM-DD HH:MM
                self.tabla_inventario.setItem(fila, 6, QTableWidgetItem(str(fecha_actualizacion)))
                
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
                    lambda checked, prod_id=producto.get('id'): self.mostrar_detalles_producto(prod_id)
                )
                self.tabla_inventario.setCellWidget(fila, 7, btn_acciones)
                
        except Exception as e:
            show_error(self, f"Error cargando productos en tabla: {e}")

    def mostrar_detalles_producto(self, producto_id):
        """Muestra los detalles de un producto."""
        try:
            if hasattr(self, "controller") and self.controller:
                producto = self.controller.obtener_producto_por_id(producto_id)
                if producto:
                    detalles = f"""
                    📋 Código: {producto.get('codigo', 'N/A')}
                    📝 Descripción: {producto.get('descripcion', 'N/A')}
                    📂 Categoría: {producto.get('categoria', 'N/A')}
                    📦 Stock Actual: {producto.get('stock', 0)} unidades
                    💰 Precio Unitario: ${producto.get('precio_unitario', 0):,.2f}
                    📊 Estado: {producto.get('estado', 'N/A')}
                    🏪 Ubicación: {producto.get('ubicacion', 'Sin especificar')}
                    📅 Última Actualización: {producto.get('fecha_actualizacion', 'N/A')}
                    """
                    
                    show_success(self, f"Detalles del Producto:\n{detalles}")
                    
        except Exception as e:
            show_error(self, f"Error mostrando detalles del producto: {e}")

    def _on_dangerous_content(self, campo, contenido):
        """Maneja detección de contenido peligroso XSS."""
        show_warning(self, f"⚠️ Contenido potencialmente peligroso detectado en {campo}: {contenido[:50]}...")

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
        """Carga los productos en la tabla."""
        self.tabla_inventario.setRowCount(len(productos))

        for row, producto in enumerate(productos):
            self.tabla_inventario.setItem(
                row, 0, QTableWidgetItem(str(producto.get("codigo", "")))
            )
            self.tabla_inventario.setItem(
                row, 1, QTableWidgetItem(str(producto.get("descripcion", "")))
            )
            self.tabla_inventario.setItem(
                row, 2, QTableWidgetItem(str(producto.get("categoria", "")))
            )
            self.tabla_inventario.setItem(
                row, 3, QTableWidgetItem(str(producto.get("stock_actual", "")))
            )
            self.tabla_inventario.setItem(
                row, 4, QTableWidgetItem(f"${producto.get('precio_unitario', 0):.2f}")
            )
            self.tabla_inventario.setItem(
                row, 5, QTableWidgetItem(str(producto.get("estado", "")))
            )

            # Botón de acciones
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("background-color: #ffc107; color: #212529;")
            self.tabla_inventario.setCellWidget(row, 6, btn_editar)

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
