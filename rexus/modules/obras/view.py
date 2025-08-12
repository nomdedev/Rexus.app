"""
MIT License

Copyright (c) 2024 Rexus.app

Vista de Obras Modernizada - Sistema de pestañas integrado
Migración de vista alternada cronograma/tabla a pestañas unificadas
"""

import datetime
from typing import Any, Dict, Optional, List

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox, QTextEdit,
    QDialog, QDialogButtonBox, QGridLayout, QProgressBar, QScrollArea,
    QSplitter, QDateEdit, QCheckBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QFont, QColor

from rexus.ui.standard_components import StandardComponents
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric
from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin

# Importar la vista cronograma existente para integrarla
try:
    from .cronograma_view import CronogramaObrasView
except ImportError:
    CronogramaObrasView = None


class ObrasModernView(QWidget, ModuleExportMixin):
    """Vista modernizada del módulo de obras con pestañas integradas."""
    
    # Señales para comunicación con controlador
    obra_agregada = pyqtSignal(dict)
    obra_editada = pyqtSignal(dict)
    obra_eliminada = pyqtSignal(int)
    solicitud_actualizar = pyqtSignal()
    solicitud_buscar = pyqtSignal(dict)
    solicitud_exportar = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.form_protector = FormProtector()
        self.setup_ui()
        self.cargar_datos_ejemplo()
    
    def setup_ui(self):
        """Configura la interfaz principal con pestañas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header del módulo
        header = self.crear_header_modulo()
        layout.addWidget(header)
        
        # Widget de pestañas principal
        self.tab_widget = QTabWidget()
        self.configurar_pestanas()
        
        # Crear pestañas
        self.crear_pestana_obras()
        self.crear_pestana_cronograma()
        self.crear_pestana_presupuestos()
        self.crear_pestana_estadisticas()
        
        layout.addWidget(self.tab_widget)
    
    def crear_header_modulo(self) -> QFrame:
        """Crea el header principal del módulo."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1e40af, stop:1 #3b82f6);
                border: none;
                border-radius: 8px;
                min-height: 50px;
                max-height: 50px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Título
        titulo = QLabel("🏗️ Gestión de Obras")
        titulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Botones de acción rápida
        btn_actualizar = QPushButton("🔄")
        btn_exportar = QPushButton("📊")
        btn_nueva_obra = QPushButton("➕")
        
        for btn in [btn_actualizar, btn_exportar, btn_nueva_obra]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
            """)
        
        btn_actualizar.clicked.connect(self.actualizar_datos)
        btn_exportar.clicked.connect(lambda: self.exportar_datos('excel'))
        btn_nueva_obra.clicked.connect(self.mostrar_dialogo_nueva_obra)
        
        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(btn_actualizar)
        layout.addWidget(btn_exportar)
        layout.addWidget(btn_nueva_obra)
        
        return header
    
    def configurar_pestanas(self):
        """Configura el estilo y comportamiento de las pestañas."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)
        
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                top: -1px;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #374151;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: 500;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1e40af;
                border-color: #3b82f6;
                border-bottom: 2px solid white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
                color: #1e40af;
            }
        """)
    
    def crear_pestana_obras(self):
        """Crea la pestaña principal de gestión de obras."""
        tab_obras = QWidget()
        layout = QVBoxLayout(tab_obras)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Panel de control compacto
        control_panel = self.crear_panel_control_obras()
        layout.addWidget(control_panel)
        
        # Tabla de obras
        self.tabla_obras = StandardComponents.create_standard_table()
        self.configurar_tabla_obras()
        layout.addWidget(self.tabla_obras)
        
        # Asignar referencia para exportación
        self.tabla_principal = self.tabla_obras
        
        # Panel de acciones
        acciones_panel = self.crear_panel_acciones_obras()
        layout.addWidget(acciones_panel)
        
        self.tab_widget.addTab(tab_obras, "🏗️ Obras")
    
    def crear_panel_control_obras(self) -> QFrame:
        """Crea el panel de control para la pestaña de obras."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Fila de búsqueda y filtros
        busqueda_layout = QHBoxLayout()
        busqueda_layout.setSpacing(8)
        
        # Búsqueda
        busqueda_layout.addWidget(QLabel("🔍 Buscar:"))
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por código, nombre, cliente...")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        busqueda_layout.addWidget(self.input_busqueda)
        
        # Filtro por estado
        busqueda_layout.addWidget(QLabel("Estado:"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todos", "Planificación", "En Curso", "Pausada", "Finalizada", "Cancelada"
        ])
        self.combo_estado.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
                min-width: 120px;
            }
        """)
        busqueda_layout.addWidget(self.combo_estado)
        
        # Filtro por tipo
        busqueda_layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Residencial", "Comercial", "Industrial", "Público"])
        self.combo_tipo.setStyleSheet(self.combo_estado.styleSheet())
        busqueda_layout.addWidget(self.combo_tipo)
        
        # Botón buscar
        btn_buscar = StandardComponents.create_primary_button("🔍 Buscar")
        btn_buscar.clicked.connect(self.buscar_obras)
        busqueda_layout.addWidget(btn_buscar)
        
        busqueda_layout.addStretch()
        
        layout.addLayout(busqueda_layout)
        
        return panel
    
    def configurar_tabla_obras(self):
        """Configura la tabla principal de obras."""
        headers = [
            "ID", "Código", "Nombre", "Cliente", "Estado", "Tipo", 
            "Inicio", "Fin", "Progreso", "Presupuesto", "Acciones"
        ]
        
        self.tabla_obras.setColumnCount(len(headers))
        self.tabla_obras.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos compactos
        anchos = [40, 80, 150, 120, 80, 80, 70, 70, 80, 100, 80]
        for i, ancho in enumerate(anchos):
            self.tabla_obras.setColumnWidth(i, ancho)
        
        # Configuraciones adicionales
        self.tabla_obras.setAlternatingRowColors(False)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setSortingEnabled(True)
        
        # Header compacto
        header = self.tabla_obras.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(40)
        header.setDefaultSectionSize(80)
    
    def crear_panel_acciones_obras(self) -> QFrame:
        """Crea el panel de acciones para obras."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                max-height: 60px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Botones de acción
        self.btn_nueva_obra = StandardComponents.create_primary_button("➕ Nueva Obra")
        self.btn_editar_obra = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_eliminar_obra = StandardComponents.create_danger_button("🗑️ Eliminar")
        self.btn_duplicar_obra = StandardComponents.create_info_button("📋 Duplicar")
        
        # Conectar eventos
        self.btn_nueva_obra.clicked.connect(self.mostrar_dialogo_nueva_obra)
        self.btn_editar_obra.clicked.connect(self.editar_obra_seleccionada)
        self.btn_eliminar_obra.clicked.connect(self.eliminar_obra_seleccionada)
        
        layout.addWidget(self.btn_nueva_obra)
        layout.addWidget(self.btn_editar_obra)
        layout.addWidget(self.btn_eliminar_obra)
        layout.addWidget(self.btn_duplicar_obra)
        
        # Agregar botón de exportación
        self.add_export_button(layout, "📄 Exportar Obras")
        
        layout.addStretch()
        
        # Botones de exportación
        btn_export_excel = StandardComponents.create_success_button("📊 Excel")
        btn_export_pdf = StandardComponents.create_info_button("📄 PDF")
        
        btn_export_excel.clicked.connect(lambda: self.exportar_datos('excel'))
        btn_export_pdf.clicked.connect(lambda: self.exportar_datos('pdf'))
        
        layout.addWidget(btn_export_excel)
        layout.addWidget(btn_export_pdf)
        
        return panel
    
    def crear_pestana_cronograma(self):
        """Crea la pestaña de cronograma integrado."""
        tab_cronograma = QWidget()
        layout = QVBoxLayout(tab_cronograma)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Panel de control del cronograma
        control_cronograma = self.crear_panel_control_cronograma()
        layout.addWidget(control_cronograma)
        
        # Área principal del cronograma
        if CronogramaObrasView is not None:
            self.cronograma_widget = CronogramaObrasView()
            layout.addWidget(self.cronograma_widget)
        else:
            # Fallback si no está disponible el cronograma
            fallback = self.crear_cronograma_fallback()
            layout.addWidget(fallback)
        
        self.tab_widget.addTab(tab_cronograma, "📅 Cronograma")
    
    def crear_panel_control_cronograma(self) -> QFrame:
        """Panel de control para el cronograma."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                max-height: 60px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Controles de vista temporal
        layout.addWidget(QLabel("Vista:"))
        self.combo_vista_cronograma = QComboBox()
        self.combo_vista_cronograma.addItems(["Semanal", "Mensual", "Trimestral", "Anual"])
        self.combo_vista_cronograma.setCurrentText("Mensual")
        layout.addWidget(self.combo_vista_cronograma)
        
        layout.addWidget(QLabel("Año:"))
        self.combo_año = QComboBox()
        año_actual = datetime.datetime.now().year
        for año in range(año_actual - 2, año_actual + 3):
            self.combo_año.addItem(str(año))
        self.combo_año.setCurrentText(str(año_actual))
        layout.addWidget(self.combo_año)
        
        btn_actualizar_cronograma = StandardComponents.create_primary_button("🔄 Actualizar")
        btn_actualizar_cronograma.clicked.connect(self.actualizar_cronograma)
        layout.addWidget(btn_actualizar_cronograma)
        
        layout.addStretch()
        
        # Botones de navegación temporal
        btn_anterior = StandardComponents.create_secondary_button("◀")
        btn_hoy = StandardComponents.create_info_button("Hoy")
        btn_siguiente = StandardComponents.create_secondary_button("▶")
        
        layout.addWidget(btn_anterior)
        layout.addWidget(btn_hoy)
        layout.addWidget(btn_siguiente)
        
        return panel
    
    def crear_cronograma_fallback(self) -> QWidget:
        """Crea un fallback cuando no hay cronograma disponible."""
        fallback = QFrame()
        fallback.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8fafc, stop: 1 #e2e8f0);
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(fallback)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ícono grande
        icon_label = QLabel("📅")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                background: transparent;
                border: none;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto principal
        main_text = QLabel("Cronograma de Obras")
        main_text.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #374151;
                background: transparent;
                border: none;
            }
        """)
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto secundario
        sub_text = QLabel("Vista temporal de obras con fechas de inicio y fin")
        sub_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6b7280;
                background: transparent;
                border: none;
            }
        """)
        sub_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Lista de obras simplificada
        obras_list = StandardComponents.create_standard_table()
        obras_list.setColumnCount(4)
        obras_list.setHorizontalHeaderLabels(["Obra", "Inicio", "Fin", "Estado"])
        obras_list.setMaximumHeight(200)
        
        layout.addWidget(icon_label)
        layout.addWidget(main_text)
        layout.addWidget(sub_text)
        layout.addSpacing(20)
        layout.addWidget(obras_list)
        
        return fallback
    
    def crear_pestana_presupuestos(self):
        """Crea la pestaña de gestión de presupuestos."""
        tab_presupuestos = QWidget()
        layout = QVBoxLayout(tab_presupuestos)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Splitter para dividir la vista
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Lista de obras
        lista_obras = self.crear_widget_lista_obras_presupuestos()
        splitter.addWidget(lista_obras)
        
        # Panel derecho - Detalle del presupuesto
        detalle_presupuesto = self.crear_widget_detalle_presupuesto()
        splitter.addWidget(detalle_presupuesto)
        
        # Proporción 40-60
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.tab_widget.addTab(tab_presupuestos, "💰 Presupuestos")
    
    def crear_widget_lista_obras_presupuestos(self) -> QWidget:
        """Lista de obras para gestión de presupuestos."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_label = QLabel("🏗️ Obras para Presupuestar")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1e293b;
                padding: 8px 0px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(header_label)
        
        # Lista de obras
        self.lista_presupuestos = StandardComponents.create_standard_table()
        self.configurar_lista_presupuestos()
        layout.addWidget(self.lista_presupuestos)
        
        return widget
    
    def configurar_lista_presupuestos(self):
        """Configura la lista para presupuestos."""
        headers = ["Código", "Obra", "Estado Presup."]
        self.lista_presupuestos.setColumnCount(len(headers))
        self.lista_presupuestos.setHorizontalHeaderLabels(headers)
        
        # Anchos ajustados
        self.lista_presupuestos.setColumnWidth(0, 80)
        self.lista_presupuestos.setColumnWidth(1, 180)
        self.lista_presupuestos.setColumnWidth(2, 120)
        
        # Eventos de selección
        self.lista_presupuestos.itemSelectionChanged.connect(self.actualizar_detalle_presupuesto)
    
    def crear_widget_detalle_presupuesto(self) -> QWidget:
        """Crea el widget de detalle del presupuesto."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        self.presupuesto_header = QLabel("💰 Seleccionar una obra para ver presupuesto")
        self.presupuesto_header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #374151;
                padding: 8px 0px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(self.presupuesto_header)
        
        # Área de contenido scrolleable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Contenido del presupuesto
        self.contenido_presupuesto = QWidget()
        self.layout_presupuesto = QVBoxLayout(self.contenido_presupuesto)
        
        # Placeholder inicial
        placeholder = QLabel("Seleccione una obra de la lista para ver y editar su presupuesto detallado.")
        placeholder.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-style: italic;
                text-align: center;
                padding: 40px 20px;
            }
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setWordWrap(True)
        
        self.layout_presupuesto.addWidget(placeholder)
        self.layout_presupuesto.addStretch()
        
        scroll_area.setWidget(self.contenido_presupuesto)
        layout.addWidget(scroll_area)
        
        return widget
    
    def crear_pestana_estadisticas(self):
        """Crea la pestaña de estadísticas y reportes."""
        tab_stats = QWidget()
        layout = QVBoxLayout(tab_stats)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Grid de widgets de estadísticas
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)
        
        # Widgets de estadísticas
        widgets_stats = [
            self.crear_widget_resumen_obras(),
            self.crear_widget_obras_por_estado(),
            self.crear_widget_presupuestos_mes(),
            self.crear_widget_cronograma_resumen()
        ]
        
        # Distribuir en grid 2x2
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for widget, pos in zip(widgets_stats, positions):
            stats_layout.addWidget(widget, pos[0], pos[1])
        
        layout.addLayout(stats_layout)
        self.tab_widget.addTab(tab_stats, "📊 Estadísticas")
    
    def crear_widget_resumen_obras(self) -> QWidget:
        """Widget de resumen de obras."""
        return self._crear_widget_estadistica(
            "🏗️ Resumen de Obras",
            [
                ("Total Obras", "47", "#3b82f6"),
                ("En Curso", "23", "#10b981"),
                ("Pausadas", "3", "#f59e0b"),
                ("Finalizadas", "21", "#6b7280")
            ]
        )
    
    def crear_widget_obras_por_estado(self) -> QWidget:
        """Widget de obras por estado."""
        return self._crear_widget_estadistica(
            "📈 Por Estado",
            [
                ("Planificación", "12", "#8b5cf6"),
                ("En Progreso", "23", "#10b981"),
                ("Pendientes", "8", "#f59e0b"),
                ("Entregadas", "18", "#3b82f6")
            ]
        )
    
    def crear_widget_presupuestos_mes(self) -> QWidget:
        """Widget de presupuestos del mes."""
        return self._crear_widget_estadistica(
            "💰 Presupuestos Mes",
            [
                ("Aprobados", "$2.847.500", "#10b981"),
                ("Pendientes", "$1.234.800", "#f59e0b"),
                ("En Revisión", "$892.400", "#8b5cf6"),
                ("Rechazados", "$245.100", "#ef4444")
            ]
        )
    
    def crear_widget_cronograma_resumen(self) -> QWidget:
        """Widget de resumen de cronograma."""
        return self._crear_widget_estadistica(
            "📅 Cronograma",
            [
                ("A Tiempo", "28", "#10b981"),
                ("Retrasadas", "8", "#ef4444"),
                ("Adelantadas", "5", "#3b82f6"),
                ("Sin Programar", "6", "#6b7280")
            ]
        )
    
    def _crear_widget_estadistica(self, titulo: str, datos: List[tuple]) -> QWidget:
        """Crea un widget de estadística con título y datos."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #374151;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 4px;
            }
        """)
        layout.addWidget(titulo_label)
        
        # Datos
        for label, value, color in datos:
            item_layout = QHBoxLayout()
            
            # Indicador de color
            indicator = QLabel("●")
            indicator.setStyleSheet(f"QLabel {{ color: {color}; font-size: 16px; }}")
            
            # Etiqueta
            label_widget = QLabel(label)
            label_widget.setStyleSheet("QLabel { color: #6b7280; font-size: 11px; }")
            
            # Valor
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
            
            item_layout.addWidget(indicator)
            item_layout.addWidget(label_widget)
            item_layout.addStretch()
            item_layout.addWidget(value_widget)
            
            layout.addLayout(item_layout)
        
        return widget
    
    # === MÉTODOS DE EVENTOS ===
    
    def buscar_obras(self):
        """Ejecuta búsqueda de obras."""
        filtros = {
            'busqueda': self.input_busqueda.text(),
            'estado': self.combo_estado.currentText(),
            'tipo': self.combo_tipo.currentText()
        }
        self.solicitud_buscar.emit(filtros)
        
    def mostrar_dialogo_nueva_obra(self):
        """Muestra el diálogo para crear nueva obra."""
        dialogo = DialogoObraModerna(self, modo='nueva')
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            self.obra_agregada.emit(datos)
    
    def editar_obra_seleccionada(self):
        """Edita la obra seleccionada."""
        row = self.tabla_obras.currentRow()
        if row >= 0:
            id_item = self.tabla_obras.item(row, 0)
            if id_item:
                obra_id = int(id_item.text())
                dialogo = DialogoObraModerna(self, modo='editar')
                if dialogo.exec() == QDialog.DialogCode.Accepted:
                    datos = dialogo.obtener_datos()
                    self.obra_editada.emit({'id': obra_id, 'datos': datos})
    
    def eliminar_obra_seleccionada(self):
        """Elimina la obra seleccionada."""
        row = self.tabla_obras.currentRow()
        if row >= 0:
            id_item = self.tabla_obras.item(row, 0)
            if id_item:
                obra_id = int(id_item.text())
                from PyQt6.QtWidgets import QMessageBox
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    f"¿Está seguro de eliminar la obra ID {obra_id}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    self.obra_eliminada.emit(obra_id)
    
    def actualizar_cronograma(self):
        """Actualiza los datos del cronograma."""
        if hasattr(self, 'cronograma_widget'):
            # Aquí deberías cargar datos reales del controlador
            pass
    
    def actualizar_detalle_presupuesto(self):
        """Actualiza los detalles del presupuesto seleccionado."""
        row = self.lista_presupuestos.currentRow()
        if row >= 0:
            codigo_item = self.lista_presupuestos.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                self.presupuesto_header.setText(f"💰 Presupuesto: {codigo}")
                self._mostrar_detalle_presupuesto_ejemplo(codigo)
    
    def _mostrar_detalle_presupuesto_ejemplo(self, codigo: str):
        """Muestra detalles de ejemplo para el presupuesto."""
        # Limpiar layout anterior
        while self.layout_presupuesto.count():
            child = self.layout_presupuesto.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Crear tabla de items del presupuesto
        tabla_items = StandardComponents.create_standard_table()
        tabla_items.setColumnCount(5)
        tabla_items.setHorizontalHeaderLabels(["Item", "Descripción", "Cantidad", "Precio Unit.", "Total"])
        tabla_items.setMaximumHeight(300)
        
        # Datos de ejemplo
        items_ejemplo = [
            ["1", "Materiales básicos", "100", "$1.200", "$120.000"],
            ["2", "Mano de obra", "80", "$2.500", "$200.000"],
            ["3", "Equipos", "15", "$5.000", "$75.000"],
            ["4", "Transportes", "10", "$3.200", "$32.000"]
        ]
        
        tabla_items.setRowCount(len(items_ejemplo))
        for row, data in enumerate(items_ejemplo):
            for col, value in enumerate(data):
                tabla_items.setItem(row, col, QTableWidgetItem(value))
        
        # Panel de totales
        totales_frame = QFrame()
        totales_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        totales_layout = QVBoxLayout(totales_frame)
        totales_layout.addWidget(QLabel("Subtotal: $427.000"))
        totales_layout.addWidget(QLabel("IVA (21%): $89.670"))
        
        total_label = QLabel("TOTAL: $516.670")
        total_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #10b981;
                border-top: 1px solid #e2e8f0;
                padding-top: 4px;
            }
        """)
        totales_layout.addWidget(total_label)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        btn_editar_presupuesto = StandardComponents.create_primary_button("✏️ Editar")
        btn_generar_pdf = StandardComponents.create_info_button("📄 PDF")
        btn_aprobar = StandardComponents.create_success_button("✅ Aprobar")
        
        botones_layout.addWidget(btn_editar_presupuesto)
        botones_layout.addWidget(btn_generar_pdf)
        botones_layout.addWidget(btn_aprobar)
        botones_layout.addStretch()
        
        self.layout_presupuesto.addWidget(tabla_items)
        self.layout_presupuesto.addWidget(totales_frame)
        self.layout_presupuesto.addLayout(botones_layout)
        self.layout_presupuesto.addStretch()
    
    def actualizar_datos(self):
        """Actualiza todos los datos del módulo."""
        self.solicitud_actualizar.emit()
    
    def exportar_datos(self, formato='excel'):
        """Exporta datos en el formato especificado."""
        self.solicitud_exportar.emit(formato)
    
    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para desarrollo."""
        # Datos de ejemplo para la tabla de obras
        datos_obras = [
            ["1", "OB-001", "Casa Familiar", "García S.A.", "En Curso", "Residencial", "01/08", "30/12", "65%", "$1.200.000", "Ver"],
            ["2", "OB-002", "Edificio Comercial", "Beta Corp", "Planificación", "Comercial", "15/09", "15/03", "10%", "$8.500.000", "Ver"],
            ["3", "OB-003", "Ampliación Oficinas", "Gamma Ltd", "Finalizada", "Comercial", "01/03", "30/06", "100%", "$750.000", "Ver"],
            ["4", "OB-004", "Complejo Industrial", "Delta Inc", "Pausada", "Industrial", "01/07", "31/12", "40%", "$15.000.000", "Ver"],
        ]
        
        self.tabla_obras.setRowCount(len(datos_obras))
        for row, data in enumerate(datos_obras):
            for col, value in enumerate(data):
                if col == 10:  # Columna Acciones
                    btn = QPushButton(value)
                    btn.setStyleSheet("""
                        QPushButton {
                            background: #3b82f6;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 8px;
                            font-size: 10px;
                        }
                        QPushButton:hover {
                            background: #2563eb;
                        }
                    """)
                    self.tabla_obras.setCellWidget(row, col, btn)
                else:
                    item = QTableWidgetItem(str(value))
                    
                    # Colorear según estado
                    if col == 4:  # Columna Estado
                        if value == "En Curso":
                            item.setBackground(QColor("#dcfce7"))
                        elif value == "Pausada":
                            item.setBackground(QColor("#fef3c7"))
                        elif value == "Finalizada":
                            item.setBackground(QColor("#e0e7ff"))
                        elif value == "Planificación":
                            item.setBackground(QColor("#f3e8ff"))
                    
                    self.tabla_obras.setItem(row, col, item)
        
        # Datos para lista de presupuestos
        if hasattr(self, 'lista_presupuestos'):
            datos_presupuestos = [
                ["OB-001", "Casa Familiar", "Aprobado"],
                ["OB-002", "Edificio Comercial", "Pendiente"],
                ["OB-003", "Ampliación Oficinas", "Completado"],
                ["OB-004", "Complejo Industrial", "En Revisión"]
            ]
            
            self.lista_presupuestos.setRowCount(len(datos_presupuestos))
            for row, data in enumerate(datos_presupuestos):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(value)
                    if col == 2:  # Columna Estado Presupuesto
                        if value == "Aprobado":
                            item.setBackground(QColor("#dcfce7"))
                        elif value == "Pendiente":
                            item.setBackground(QColor("#fef3c7"))
                        elif value == "En Revisión":
                            item.setBackground(QColor("#f3e8ff"))
                    self.lista_presupuestos.setItem(row, col, item)


class DialogoObraModerna(QDialog):
    """Diálogo moderno para crear/editar obras."""
    
    def __init__(self, parent=None, modo='nueva'):
        super().__init__(parent)
        self.modo = modo
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        titulo = "Nueva Obra" if self.modo == 'nueva' else "Editar Obra"
        self.setWindowTitle(titulo)
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Formulario principal
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.codigo_edit = QLineEdit()
        self.nombre_edit = QLineEdit()
        self.cliente_edit = QLineEdit()
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Residencial", "Comercial", "Industrial", "Público"])
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Planificación", "En Curso", "Pausada", "Finalizada", "Cancelada"])
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate().addDays(90))
        self.fecha_fin.setCalendarPopup(True)
        
        self.presupuesto_spin = QDoubleSpinBox()
        self.presupuesto_spin.setRange(0.0, 99999999.99)
        self.presupuesto_spin.setPrefix("$ ")
        
        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setMaximumHeight(100)
        
        # Agregar campos al formulario
        form_layout.addRow("Código:", self.codigo_edit)
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Cliente:", self.cliente_edit)
        form_layout.addRow("Tipo:", self.tipo_combo)
        form_layout.addRow("Estado:", self.estado_combo)
        form_layout.addRow("Fecha Inicio:", self.fecha_inicio)
        form_layout.addRow("Fecha Fin:", self.fecha_fin)
        form_layout.addRow("Presupuesto:", self.presupuesto_spin)
        form_layout.addRow("Descripción:", self.descripcion_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def obtener_datos(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        return {
            'codigo': sanitize_string(self.codigo_edit.text()),
            'nombre': sanitize_string(self.nombre_edit.text()),
            'cliente': sanitize_string(self.cliente_edit.text()),
            'tipo': self.tipo_combo.currentText(),
            'estado': self.estado_combo.currentText(),
            'fecha_inicio': self.fecha_inicio.date().toString('yyyy-MM-dd'),
            'fecha_fin': self.fecha_fin.date().toString('yyyy-MM-dd'),
            'presupuesto': self.presupuesto_spin.value(),
            'descripcion': sanitize_string(self.descripcion_edit.toPlainText())
        }


# Alias para compatibilidad con importaciones existentes
ObrasView = ObrasModernView