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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager

from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import FormProtector, XSSProtection


class HerrajesView(QWidget):
    """Vista principal del módulo de herrajes."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario con pestañas."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Crear sistema de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        # Pestaña de Gestión de Herrajes
        tab_gestion = self.crear_tab_gestion()
        self.tab_widget.addTab(tab_gestion, "🔧 Gestión")

        # Pestaña de Estadísticas
        tab_estadisticas = self.crear_tab_estadisticas()
        self.tab_widget.addTab(tab_estadisticas, "📊 Estadísticas")

        layout.addWidget(self.tab_widget)

        # Aplicar estilos modernos
        self.configurar_estilos()

        # Inicializar protección XSS
        self.init_xss_protection()

    def crear_tab_gestion(self):
        """Crea la pestaña de gestión de herrajes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Panel de integración con inventario
        integration_panel = self.crear_panel_integracion()
        layout.addWidget(integration_panel)

        # Tabla principal
        self.tabla_principal = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_principal)

        return tab

    def crear_tab_estadisticas(self):
        """Crea la pestaña de estadísticas de herrajes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        return tab

    def crear_panel_analisis_stock(self):
        """Crea el panel de análisis de stock."""
        panel = QGroupBox("📈 Análisis de Stock")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #6f42c1;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6f42c1;
            }
        """)

        layout = QVBoxLayout(panel)
        
        # Placeholder para análisis de stock
        placeholder = QLabel("📊 Análisis de stock próximamente")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #6c757d; font-size: 14px; padding: 20px;")
        layout.addWidget(placeholder)

        return panel

    def crear_panel_reportes_herrajes(self):
        """Crea el panel de reportes de herrajes."""
        panel = QGroupBox("📄 Reportes de Herrajes")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #20c997;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #20c997;
            }
        """)

        layout = QHBoxLayout(panel)
        
        # Botones de reportes
        btn_reporte_stock = QPushButton("📋 Herrajes por Stock")
        btn_reporte_stock.setStyleSheet("""
            QPushButton {
                background-color: #20c997;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ba085;
            }
        """)
        layout.addWidget(btn_reporte_stock)

        btn_reporte_categorias = QPushButton("📊 Por Categorías")
        btn_reporte_categorias.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8630a;
            }
        """)
        layout.addWidget(btn_reporte_categorias)

        btn_reporte_proveedores = QPushButton("🏭 Por Proveedores")
        btn_reporte_proveedores.setStyleSheet("""
            QPushButton {
                background-color: #6610f2;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #520dc2;
            }
        """)
        layout.addWidget(btn_reporte_proveedores)

        layout.addStretch()
        return panel

    # def crear_titulo(self, layout: QVBoxLayout):
#         """Crea el título moderno de la vista."""
#         titulo_container = QFrame()
#         titulo_container.setStyleSheet("""
#             QFrame {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                                            stop:0 #6c757d, stop:1 #495057);
#                 border-radius: 8px;
#                 padding: 6px;
#                 margin-bottom: 10px;
#             }
#         """)
# 
#         titulo_layout = QHBoxLayout(titulo_container)
# 
#         # Título principal
#         title_label = QLabel("🔧 Gestión de Herrajes")
#         title_label.setStyleSheet("""
#             QLabel {
#                 font-size: 16px;
#                 font-weight: bold;
#                 color: white;
#                 background: transparent;
#                 padding: 0;
#                 margin: 0;
#             }
#         """)
#         titulo_layout.addWidget(title_label)

        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)

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
        panel = QGroupBox("🎛️ Panel de Control")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
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
                color: #6c757d;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón Nuevo Herraje
        self.btn_nuevo = QPushButton("➕ Nuevo Herraje")
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 130px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_nuevo.setToolTip("➕ Crear un nuevo herraje en el sistema")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar herraje por nombre o descripción...")
        self.input_busqueda.setToolTip("🔍 Buscar herrajes por nombre, descripción o tipo")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #6c757d;
            }
        """)
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Filtro de tipo
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "🔩 Todos los tipos",
            "⚙️ Tornillería",
            "🔗 Cadenas",
            "🚪 Bisagras", 
            "🔐 Cerraduras",
            "🔧 Herramientas",
            "📏 Medición"
        ])
        self.combo_tipo.setToolTip("🔩 Filtrar herrajes por tipo")
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 160px;
            }
            QComboBox:focus {
                border-color: #6c757d;
            }
        """)
        layout.addWidget(self.combo_tipo)

        # Botón buscar
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar
        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de herrajes")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

        # Separador y botones de acción
        layout.addStretch()
        
        # Botón editar
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ffcd39;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_editar.setToolTip("✏️ Editar herraje seleccionado")
        self.btn_editar.setEnabled(False)
        layout.addWidget(self.btn_editar)

        # Botón eliminar
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_eliminar.setToolTip("🗑️ Eliminar herraje seleccionado")
        self.btn_eliminar.setEnabled(False)
        layout.addWidget(self.btn_eliminar)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas de herrajes."""
        panel = QGroupBox("📊 Estadísticas de Herrajes")
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
        self.tabla_principal.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Estilos de tabla modernos
        self.tabla_principal.setStyleSheet("""
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
        self.tabla_principal.itemSelectionChanged.connect(self.on_herraje_seleccionado)

    def configurar_estilos(self):
        """Configura los estilos modernos usando FormStyleManager."""
        try:
            from rexus.utils.form_styles import FormStyleManager, setup_form_widget
            
            # Aplicar estilos modernos del FormStyleManager
            setup_form_widget(self, apply_animations=True)
            
            # Estilos específicos del módulo de herrajes
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
        """Aplica estilos básicos como fallback (sin sintaxis incorrecta)."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
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
                valor_labels = self.lbl_total_herrajes.findChildren(QLabel)
                if len(valor_labels) >= 2:  # Segundo label es el valor
                    valor_labels[1].setText(str(stats.get("total_herrajes", 0)))

            if hasattr(self, 'lbl_herrajes_activos'):
                valor_labels = self.lbl_herrajes_activos.findChildren(QLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("herrajes_activos", 0)))

            if hasattr(self, 'lbl_herrajes_inactivos'):
                valor_labels = self.lbl_herrajes_inactivos.findChildren(QLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("herrajes_inactivos", 0)))

            if hasattr(self, 'lbl_tipos_disponibles'):
                valor_labels = self.lbl_tipos_disponibles.findChildren(QLabel)
                if len(valor_labels) >= 2:
                    valor_labels[1].setText(str(stats.get("tipos_disponibles", 0)))

        except Exception as e:
            show_error(self, "Error de Estadísticas", f"Error actualizando estadísticas: {e}")

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo registro."""
        show_warning(self, "Función en desarrollo", "Diálogo en desarrollo")

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

            # Botón de acciones
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("background-color: #ffc107; color: #212529;")
            self.tabla_principal.setCellWidget(row, 4, btn_editar)

    def crear_panel_integracion(self):
        """Crea el panel de integración con inventario."""
        panel = QGroupBox("🔗 Integración con Inventario")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28a745;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón sincronizar con inventario
        self.btn_sincronizar_inventario = QPushButton("🔄 Sincronizar con Inventario")
        self.btn_sincronizar_inventario.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_sincronizar_inventario.setToolTip("🔄 Sincroniza herrajes con el inventario general")
        self.btn_sincronizar_inventario.clicked.connect(self.sincronizar_inventario)
        layout.addWidget(self.btn_sincronizar_inventario)

        # Botón resumen de integración
        self.btn_resumen_integracion = QPushButton("📊 Resumen Integración")
        self.btn_resumen_integracion.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_resumen_integracion.setToolTip("📊 Muestra resumen del estado de integración")
        self.btn_resumen_integracion.clicked.connect(self.mostrar_resumen_integracion)
        layout.addWidget(self.btn_resumen_integracion)

        # Botón transferir a inventario
        self.btn_transferir_inventario = QPushButton("📦 Transferir a Inventario")
        self.btn_transferir_inventario.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #5a36a3;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_transferir_inventario.setToolTip("📦 Transfiere herraje seleccionado al inventario general")
        self.btn_transferir_inventario.setEnabled(False)
        self.btn_transferir_inventario.clicked.connect(self.transferir_a_inventario)
        layout.addWidget(self.btn_transferir_inventario)

        # Botón crear reserva
        self.btn_crear_reserva = QPushButton("📝 Crear Reserva")
        self.btn_crear_reserva.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e8690b;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
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
            show_warning(self, "Sin controlador", "No hay controlador disponible para la sincronización")

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
            
            # Solicitar cantidad al usuario
            from PyQt6.QtWidgets import QInputDialog
            cantidad, ok = QInputDialog.getInt(
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
            
            # Solicitar datos de la reserva
            from PyQt6.QtWidgets import QInputDialog
            
            # Solicitar ID de obra
            obra_id, ok_obra = QInputDialog.getInt(
                self,
                "ID de Obra",
                "Ingrese el ID de la obra:",
                value=1, min=1, max=9999
            )
            
            if not ok_obra:
                return
                
            # Solicitar cantidad
            cantidad, ok_cantidad = QInputDialog.getInt(
                self,
                "Cantidad a Reservar",
                "Ingrese la cantidad a reservar:",
                value=1, min=1, max=9999
            )
            
            if not ok_cantidad:
                return
                
            # Solicitar observaciones
            observaciones, ok_obs = QInputDialog.getText(
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
