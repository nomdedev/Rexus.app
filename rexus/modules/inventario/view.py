# -*- coding: utf-8 -*-
"""
Vista de Inventario Refactorizada - Rexus.app
Vista funcional con pestañas organizadas para gestión de inventario
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QLabel, QGroupBox, QFrame, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QTextEdit,
    QSplitter, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon
from rexus.ui.templates.base_module_view import BaseModuleView

class InventarioView(BaseModuleView):
    """Vista refactorizada del módulo de inventario con funcionalidad real."""
    
    # Señales
    producto_agregado = pyqtSignal(dict)
    producto_editado = pyqtSignal(int, dict)
    producto_eliminado = pyqtSignal(int)
    movimiento_registrado = pyqtSignal(dict)
    material_reservado = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__("📦 Gestión de Inventario", parent)
        self.productos = []
        self.obras = []
        self.movimientos = []
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz principal."""
        # Widget de pestañas principal
        self.tabs = QTabWidget()
        
        # Pestaña 1: Materiales (tabla principal)
        self.tab_materiales = self.crear_tab_materiales()
        self.tabs.addTab(self.tab_materiales, "📦 Materiales")
        
        # Pestaña 2: Reservas por Obras
        self.tab_reservas = self.crear_tab_reservas()
        self.tabs.addTab(self.tab_reservas, "🏢 Reservas por Obras")
        
        # Pestaña 3: Movimientos (Entradas/Salidas)
        self.tab_movimientos = self.crear_tab_movimientos()
        self.tabs.addTab(self.tab_movimientos, "📊 Movimientos")
        
        # Pestaña 4: Reportes
        self.tab_reportes = self.crear_tab_reportes()
        self.tabs.addTab(self.tab_reportes, "📋 Reportes")
        
        self.add_to_main_content(self.tabs)
        self.apply_theme()
    
    def crear_tab_materiales(self):
        """Crea la pestaña principal de materiales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Barra de herramientas
        toolbar = self.crear_toolbar_materiales()
        layout.addWidget(toolbar)
        
        # Filtros
        filtros = self.crear_filtros_materiales()
        layout.addWidget(filtros)
        
        # Tabla de materiales
        self.tabla_materiales = self.crear_tabla_materiales()
        layout.addWidget(self.tabla_materiales)
        
        # Información de resumen
        resumen = self.crear_resumen_materiales()
        layout.addWidget(resumen)
        
        return widget
    
    def crear_toolbar_materiales(self):
        """Crea la barra de herramientas de materiales."""
        toolbar = QFrame()
        layout = QHBoxLayout(toolbar)
        
        # Botones principales
        self.btn_agregar_material = QPushButton("➕ Agregar Material")
        self.btn_agregar_material.setStyleSheet("""
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
        """)
        
        self.btn_editar_material = QPushButton("✏️ Editar")
        self.btn_eliminar_material = QPushButton("🗑️ Eliminar")
        self.btn_importar = QPushButton("📥 Importar")
        self.btn_exportar = QPushButton("📤 Exportar")
        
        # Configurar estilos de botones
        for btn in [self.btn_editar_material, self.btn_eliminar_material, 
                   self.btn_importar, self.btn_exportar]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
        
        layout.addWidget(self.btn_agregar_material)
        layout.addWidget(self.btn_editar_material)
        layout.addWidget(self.btn_eliminar_material)
        layout.addStretch()
        layout.addWidget(self.btn_importar)
        layout.addWidget(self.btn_exportar)
        
        return toolbar
    
    def crear_filtros_materiales(self):
        """Crea los filtros para la tabla de materiales."""
        filtros_frame = QFrame()
        layout = QHBoxLayout(filtros_frame)
        
        # Búsqueda por nombre
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar materiales...")
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.buscar_input)
        
        # Filtro por categoría
        self.filtro_categoria = QComboBox()
        self.filtro_categoria.addItems(["Todas las categorías", "Vidrios", "Herrajes", "Perfiles", "Accesorios"])
        layout.addWidget(QLabel("Categoría:"))
        layout.addWidget(self.filtro_categoria)
        
        # Filtro por stock
        self.filtro_stock = QComboBox()
        self.filtro_stock.addItems(["Todos", "Stock disponible", "Stock bajo", "Sin stock"])
        layout.addWidget(QLabel("Stock:"))
        layout.addWidget(self.filtro_stock)
        
        layout.addStretch()
        
        return filtros_frame
    
    def crear_tabla_materiales(self):
        """Crea la tabla principal de materiales."""
        tabla = QTableWidget()
        
        # Definir columnas
        columnas = [
            "ID", "Código", "Nombre", "Descripción", "Categoría", 
            "Stock Actual", "Stock Mínimo", "Unidad", "Precio Unit.", 
            "Valor Total", "Ubicación", "Estado"
        ]
        
        tabla.setColumnCount(len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        
        # Configurar tabla
        tabla.setAlternatingRowColors(True)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setSortingEnabled(True)
        
        # Ajustar columnas
        header = tabla.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Descripción
        
        # Ocultar ID
        tabla.hideColumn(0)
        
        # Estilos
        tabla.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2196f3;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        return tabla
    
    def crear_resumen_materiales(self):
        """Crea el panel de resumen de materiales."""
        resumen = QFrame()
        layout = QHBoxLayout(resumen)
        
        # Estadísticas
        self.lbl_total_materiales = QLabel("Total: 0")
        self.lbl_valor_total = QLabel("Valor: $0")
        self.lbl_stock_bajo = QLabel("Stock bajo: 0")
        self.lbl_sin_stock = QLabel("Sin stock: 0")
        
        # Estilos para las estadísticas
        for lbl in [self.lbl_total_materiales, self.lbl_valor_total, 
                   self.lbl_stock_bajo, self.lbl_sin_stock]:
            lbl.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    padding: 8px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        
        layout.addWidget(self.lbl_total_materiales)
        layout.addWidget(self.lbl_valor_total)
        layout.addWidget(self.lbl_stock_bajo)
        layout.addWidget(self.lbl_sin_stock)
        layout.addStretch()
        
        return resumen
    
    def crear_tab_reservas(self):
        """Crea la pestaña de reservas por obras."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Splitter para dividir obras y detalles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Lista de obras
        panel_obras = self.crear_panel_obras()
        splitter.addWidget(panel_obras)
        
        # Panel derecho: Materiales reservados
        panel_reservas = self.crear_panel_reservas()
        splitter.addWidget(panel_reservas)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        return widget
    
    def crear_panel_obras(self):
        """Crea el panel de lista de obras."""
        panel = QGroupBox("🏢 Obras Activas")
        layout = QVBoxLayout(panel)
        
        # Tabla de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(4)
        self.tabla_obras.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Estado"])
        self.tabla_obras.hideColumn(0)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.tabla_obras)
        
        return panel
    
    def crear_panel_reservas(self):
        """Crea el panel de materiales reservados."""
        panel = QGroupBox("📦 Materiales Reservados")
        layout = QVBoxLayout(panel)
        
        # Botones de acción
        botones = QHBoxLayout()
        self.btn_reservar_material = QPushButton("➕ Reservar Material")
        self.btn_liberar_reserva = QPushButton("🔓 Liberar Reserva")
        self.btn_usar_material = QPushButton("✅ Usar Material")
        
        botones.addWidget(self.btn_reservar_material)
        botones.addWidget(self.btn_liberar_reserva)
        botones.addWidget(self.btn_usar_material)
        botones.addStretch()
        
        layout.addLayout(botones)
        
        # Tabla de reservas
        self.tabla_reservas = QTableWidget()
        self.tabla_reservas.setColumnCount(6)
        self.tabla_reservas.setHorizontalHeaderLabels([
            "Material", "Código", "Cantidad Reservada", "Cantidad Usada", 
            "Fecha Reserva", "Estado"
        ])
        self.tabla_reservas.setAlternatingRowColors(True)
        
        layout.addWidget(self.tabla_reservas)
        
        return panel
    
    def crear_tab_movimientos(self):
        """Crea la pestaña de movimientos (entradas/salidas)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Botones para registrar movimientos
        botones = QHBoxLayout()
        self.btn_entrada_material = QPushButton("📥 Registrar Entrada")
        self.btn_salida_material = QPushButton("📤 Registrar Salida")
        self.btn_ajuste_inventario = QPushButton("⚖️ Ajuste de Inventario")
        
        # Estilos para botones de movimiento
        self.btn_entrada_material.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        
        self.btn_salida_material.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        
        self.btn_ajuste_inventario.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e0a800; }
        """)
        
        botones.addWidget(self.btn_entrada_material)
        botones.addWidget(self.btn_salida_material)
        botones.addWidget(self.btn_ajuste_inventario)
        botones.addStretch()
        
        layout.addLayout(botones)
        
        # Filtros de fecha
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Período:"))
        
        self.filtro_periodo = QComboBox()
        self.filtro_periodo.addItems(["Hoy", "Esta semana", "Este mes", "Últimos 3 meses", "Todo"])
        filtros.addWidget(self.filtro_periodo)
        
        filtros.addWidget(QLabel("Tipo:"))
        self.filtro_tipo_movimiento = QComboBox()
        self.filtro_tipo_movimiento.addItems(["Todos", "Entradas", "Salidas", "Ajustes"])
        filtros.addWidget(self.filtro_tipo_movimiento)
        
        filtros.addStretch()
        layout.addLayout(filtros)
        
        # Tabla de movimientos
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(8)
        self.tabla_movimientos.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Material", "Cantidad", "Motivo", 
            "Usuario", "Obra/Destino", "Observaciones"
        ])
        self.tabla_movimientos.setAlternatingRowColors(True)
        self.tabla_movimientos.setSortingEnabled(True)
        
        layout.addWidget(self.tabla_movimientos)
        
        return widget
    
    def crear_tab_reportes(self):
        """Crea la pestaña de reportes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grid de reportes disponibles
        reportes_grid = QGridLayout()
        
        # Reportes de stock
        self.btn_reporte_stock = QPushButton("📊 Reporte de Stock")
        self.btn_reporte_stock_bajo = QPushButton("⚠️ Stock Bajo")
        self.btn_reporte_valorizado = QPushButton("💰 Inventario Valorizado")
        
        # Reportes de movimientos
        self.btn_reporte_movimientos = QPushButton("📋 Movimientos")
        self.btn_reporte_kardex = QPushButton("📈 Kardex")
        self.btn_reporte_consumos = QPushButton("🏗️ Consumos por Obra")
        
        # Configurar estilos de reportes
        for btn in [self.btn_reporte_stock, self.btn_reporte_stock_bajo, 
                   self.btn_reporte_valorizado, self.btn_reporte_movimientos, 
                   self.btn_reporte_kardex, self.btn_reporte_consumos]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    padding: 20px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            btn.setMinimumHeight(80)
        
        # Organizar en grid
        reportes_grid.addWidget(self.btn_reporte_stock, 0, 0)
        reportes_grid.addWidget(self.btn_reporte_stock_bajo, 0, 1)
        reportes_grid.addWidget(self.btn_reporte_valorizado, 0, 2)
        reportes_grid.addWidget(self.btn_reporte_movimientos, 1, 0)
        reportes_grid.addWidget(self.btn_reporte_kardex, 1, 1)
        reportes_grid.addWidget(self.btn_reporte_consumos, 1, 2)
        
        layout.addLayout(reportes_grid)
        layout.addStretch()
        
        return widget
    
    def apply_theme(self):
        """Aplica el tema visual al módulo."""
        self.setStyleSheet("""
            InventarioView {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #0056b3;
                color: white;
            }
        """)
    
    def cargar_datos_materiales(self, materiales):
        """Carga los datos en la tabla de materiales."""
        self.productos = materiales
        self.tabla_materiales.setRowCount(len(materiales))
        
        for row, material in enumerate(materiales):
            # ID (oculto)
            self.tabla_materiales.setItem(row, 0, QTableWidgetItem(str(material.get('id', ''))))
            
            # Código
            self.tabla_materiales.setItem(row, 1, QTableWidgetItem(material.get('codigo', '')))
            
            # Nombre
            self.tabla_materiales.setItem(row, 2, QTableWidgetItem(material.get('nombre', '')))
            
            # Descripción
            self.tabla_materiales.setItem(row, 3, QTableWidgetItem(material.get('descripcion', '')))
            
            # Categoría
            self.tabla_materiales.setItem(row, 4, QTableWidgetItem(material.get('categoria', '')))
            
            # Stock Actual
            stock_actual = material.get('stock_actual', 0)
            item_stock = QTableWidgetItem(str(stock_actual))
            if stock_actual <= material.get('stock_minimo', 0):
                item_stock.setBackground(QColor('#ffebee'))  # Rojo claro para stock bajo
            self.tabla_materiales.setItem(row, 5, item_stock)
            
            # Stock Mínimo
            self.tabla_materiales.setItem(row, 6, QTableWidgetItem(str(material.get('stock_minimo', 0))))
            
            # Unidad
            self.tabla_materiales.setItem(row, 7, QTableWidgetItem(material.get('unidad', '')))
            
            # Precio Unitario
            precio = material.get('precio_unitario', 0)
            self.tabla_materiales.setItem(row, 8, QTableWidgetItem(f"${precio:,.2f}"))
            
            # Valor Total
            valor_total = stock_actual * precio
            self.tabla_materiales.setItem(row, 9, QTableWidgetItem(f"${valor_total:,.2f}"))
            
            # Ubicación
            self.tabla_materiales.setItem(row, 10, QTableWidgetItem(material.get('ubicacion', '')))
            
            # Estado
            estado = 'Activo' if material.get('activo', True) else 'Inactivo'
            self.tabla_materiales.setItem(row, 11, QTableWidgetItem(estado))
        
        self.actualizar_resumen_materiales()
    
    def actualizar_resumen_materiales(self):
        """Actualiza las estadísticas del resumen."""
        if not self.productos:
            return
        
        total_materiales = len(self.productos)
        valor_total = sum(p.get('stock_actual', 0) * p.get('precio_unitario', 0) for p in self.productos)
        stock_bajo = sum(1 for p in self.productos if p.get('stock_actual', 0) <= p.get('stock_minimo', 0))
        sin_stock = sum(1 for p in self.productos if p.get('stock_actual', 0) == 0)
        
        self.lbl_total_materiales.setText(f"Total: {total_materiales}")
        self.lbl_valor_total.setText(f"Valor: ${valor_total:,.2f}")
        self.lbl_stock_bajo.setText(f"Stock bajo: {stock_bajo}")
        self.lbl_sin_stock.setText(f"Sin stock: {sin_stock}")
        
        # Cambiar colores según alertas
        if stock_bajo > 0:
            self.lbl_stock_bajo.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    color: #856404;
                    padding: 8px;
                    border: 1px solid #ffeaa7;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        
        if sin_stock > 0:
            self.lbl_sin_stock.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 8px;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)