"""
MIT License

Copyright (c) 2024 Rexus.app

Vista de Obras Modernizada - Sistema de pestañas integrado
Migración de vista alternada cronograma/tabla a pestañas unificadas
"""


import logging
logger = logging.getLogger(__name__)

import datetime
from typing import Any, Dict, List

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidgetItem, QFormLayout,
    QDoubleSpinBox, QTextEdit, QDialog, QDialogButtonBox, QGridLayout,
    QScrollArea, QSplitter, QDateEdit
)
from PyQt6.QtGui import QColor

from rexus.ui.standard_components import StandardComponents
from rexus.ui.components.base_components import RexusLabel
from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.message_system import show_error, show_warning, show_success
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin

# Importar componentes mejorados
from .components.optimized_table_widget import EnhancedTableContainer

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
        # Cargar obras en la tabla después de la configuración inicial
        self.cargar_obras_en_tabla()

    def setup_ui(self):
        """Configura la interfaz principal con pestañas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Widget de pestañas principal (sin header azul)
        self.tab_widget = QTabWidget()
        self.configurar_pestanas()

        # Crear pestañas
        self.crear_pestana_obras()
        self.crear_pestana_cronograma()
        self.crear_pestana_presupuestos()
        self.crear_pestana_estadisticas()

        layout.addWidget(self.tab_widget)


    def configurar_pestanas(self):
        """Configura el estilo y comportamiento de las pestañas."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)

        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #374151;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                margin-right: 2px;
                font-weight: 500;
                min-width: 80px;
                min-height: 24px;
                max-height: 24px;
                font-size: 12px;
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
        from PyQt6.QtWidgets import QTableWidget
        self.tabla_obras = QTableWidget()
        self.configurar_tabla_obras()
        layout.addWidget(self.tabla_obras)

        # Asignar referencia para exportación
        self.tabla_principal = self.tabla_obras

        # Controles de paginación
        paginacion_panel = self.crear_controles_paginacion()
        layout.addWidget(paginacion_panel)

        # Panel de acciones
        acciones_panel = self.crear_panel_acciones_obras()
        layout.addWidget(acciones_panel)

        self.tab_widget.addTab(tab_obras, )

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
        busqueda_layout.addWidget(QLabel("[SEARCH] Buscar:"))
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por código, nombre, cliente...")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                padding: 3px 6px;
                border: 1px solid #d1d5db;
                border-radius: 3px;
                font-size: 9px;
                min-height: 16px;
                max-height: 18px;
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
                padding: 3px 6px;
                border: 1px solid #d1d5db;
                border-radius: 3px;
                font-size: 9px;
                min-width: 80px;
                max-width: 100px;
                min-height: 16px;
                max-height: 18px;
            }
        """)
        busqueda_layout.addWidget(self.combo_estado)

        # Filtro por tipo
        busqueda_layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos",
"Residencial",
            "Comercial",
            "Industrial",
            "Público"])
        self.combo_tipo.setStyleSheet(self.combo_estado.styleSheet())
        busqueda_layout.addWidget(self.combo_tipo)

        # Botón buscar - extra compacto
        btn_buscar = StandardComponents.create_primary_button("[SEARCH] Buscar")
        btn_buscar.setStyleSheet("""
            QPushButton {
                background: #f8fafc;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                color: #374151;
                font-weight: 500;
                font-size: 9px;
                padding: 2px 6px;
                min-height: 18px;
                max-height: 20px;
                min-width: 50px;
                max-width: 70px;
            }
            QPushButton:hover {
                background: #e5e7eb;
                border: 1px solid #9ca3af;
            }
        """)
        btn_buscar.clicked.connect(self.buscar_obras)
        busqueda_layout.addWidget(btn_buscar)

        busqueda_layout.addStretch()

        layout.addLayout(busqueda_layout)

        return panel

    def configurar_tabla_obras(self):
        """Configura la tabla principal de obras."""
        # Configurar columnas
        self.tabla_obras.setColumnCount(10)
        self.tabla_obras.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Cliente", "Estado", "Tipo", 
            "Fecha Inicio", "Fecha Fin", "Progreso", "Presupuesto"
        ])
        
        # Configurar propiedades
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSelectionBehavior(self.tabla_obras.SelectionBehavior.SelectRows)
        self.tabla_obras.setSortingEnabled(True)

        logger.info("[OBRAS] Tabla configurada correctamente")

    def cargar_obras_en_tabla(self, obras_data=None):
        """Carga las obras en la tabla principal usando componente optimizado."""
        try:
            # Si no se proporcionan datos, solicitar al controlador
            if obras_data is None:
                if self.controller:
                    self.controller.cargar_obras()
                    return
                else:
                    # Cargar datos de ejemplo para desarrollo/testing
                    obras_data = self.obtener_datos_obras_ejemplo()

            if not obras_data:
                show_warning(self, "Información", "No hay obras para mostrar")
                return

            # Usar el componente optimizado para cargar datos
            def update_progress(progress):
                if hasattr(self.tabla_obras_container, 'update_status'):
                    if progress < 100:
                        self.tabla_obras_container.update_status(f"Cargando datos... {progress}%")
                    else:
                        self.tabla_obras_container.update_status(f"{len(obras_data)} obras cargadas")

            # Cargar datos en la tabla optimizada
            self.tabla_obras.load_data(obras_data, update_progress)

            logger.info(f"[OBRAS] Cargadas {len(obras_data)} obras en tabla optimizada")

            # Poblar la tabla
            for row, obra in enumerate(obras_data):
                try:
                    # ID
                    id_item = QTableWidgetItem(str(obra.get('id', '')))
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_obras.setItem(row, 0, id_item)

                    # Código
                    codigo_item = QTableWidgetItem(str(obra.get('codigo', '')))
                    self.tabla_obras.setItem(row, 1, codigo_item)

                    # Nombre
                    nombre_item = QTableWidgetItem(str(obra.get('nombre', '')))
                    self.tabla_obras.setItem(row, 2, nombre_item)

                    # Cliente
                    cliente_item = QTableWidgetItem(str(obra.get('cliente', '')))
                    self.tabla_obras.setItem(row, 3, cliente_item)

                    # Estado con color
                    estado = str(obra.get('estado', ''))
                    estado_item = QTableWidgetItem(estado)
                    estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Colorear según estado
                    if estado.lower() in ['en curso', 'en progreso', 'activa']:
                        estado_item.setBackground(QColor("#dcfce7"))  # Verde claro
                    elif estado.lower() in ['pausada', 'pendiente']:
                        estado_item.setBackground(QColor("#fef3c7"))  # Amarillo
                    elif estado.lower() in ['finalizada', 'completada']:
                        estado_item.setBackground(QColor("#e0e7ff"))  # Azul claro
                    elif estado.lower() in ['planificación', 'planificacion']:
                        estado_item.setBackground(QColor("#f3e8ff"))  # Púrpura claro

                    self.tabla_obras.setItem(row, 4, estado_item)

                    # Tipo
                    tipo_item = QTableWidgetItem(str(obra.get('tipo', '')))
                    self.tabla_obras.setItem(row, 5, tipo_item)

                    # Fecha inicio
                    inicio_item = QTableWidgetItem(str(obra.get('fecha_inicio', '')))
                    inicio_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_obras.setItem(row, 6, inicio_item)

                    # Fecha fin
                    fin_item = QTableWidgetItem(str(obra.get('fecha_fin', '')))
                    fin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_obras.setItem(row, 7, fin_item)

                    # Progreso
                    progreso = obra.get('progreso', 0)
                    progreso_item = QTableWidgetItem(f"{progreso}%")
                    progreso_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_obras.setItem(row, 8, progreso_item)

                    # Presupuesto
                    presupuesto = obra.get('presupuesto', 0)
                    presupuesto_item = QTableWidgetItem(f"${presupuesto:,.0f}")
                    presupuesto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                    self.tabla_obras.setItem(row, 9, presupuesto_item)

                    # Botón de acciones
                    btn_acciones = QPushButton("Ver")
                    btn_acciones.setStyleSheet("""
                        QPushButton {
                            background: #3b82f6;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 2px 6px;
                            font-size: 8px;
                            min-width: 35px;
                            max-width: 50px;
                            min-height: 16px;
                            max-height: 18px;
                        }
                        QPushButton:hover {
                            background: #2563eb;
                        }
                    """)
                    btn_acciones.clicked.connect(
                        lambda checked, obra_id=obra.get('id'): self.ver_detalle_obra(obra_id)
                    )
                    self.tabla_obras.setCellWidget(row, 10, btn_acciones)

                except Exception as e:
                    logger.info(f"Error cargando fila {row}: {str(e)}")
                    continue

            logger.info(f"Cargadas {len(obras_data)} obras en la tabla")

        except Exception as e:
            show_error(self, "Error", f"Error cargando obras en tabla: {str(e)}")

    def obtener_datos_obras_ejemplo(self):
        """Datos de ejemplo para desarrollo y testing."""
        import datetime
        datetime.date.today()

        return [
            {
                'id': 1,
                'codigo': 'OB-001',
                'nombre': 'Casa Familiar Los Robles',
                'cliente': 'García S.A.',
                'estado': 'En Curso',
                'tipo': 'Residencial',
                'fecha_inicio': '2024-08-01',
                'fecha_fin': '2024-12-30',
                'progreso': 65,
                'presupuesto': 1200000
            },
            {
                'id': 2,
                'codigo': 'OB-002',
                'nombre': 'Edificio Comercial Centro',
                'cliente': 'Beta Corp',
                'estado': 'Planificación',
                'tipo': 'Comercial',
                'fecha_inicio': '2024-09-15',
                'fecha_fin': '2025-03-15',
                'progreso': 10,
                'presupuesto': 8500000
            },
            {
                'id': 3,
                'codigo': 'OB-003',
                'nombre': 'Ampliación Oficinas',
                'cliente': 'Gamma Ltd',
                'estado': 'Finalizada',
                'tipo': 'Comercial',
                'fecha_inicio': '2024-03-01',
                'fecha_fin': '2024-06-30',
                'progreso': 100,
                'presupuesto': 750000
            },
            {
                'id': 4,
                'codigo': 'OB-004',
                'nombre': 'Complejo Industrial Norte',
                'cliente': 'Delta Inc',
                'estado': 'Pausada',
                'tipo': 'Industrial',
                'fecha_inicio': '2024-07-01',
                'fecha_fin': '2024-12-31',
                'progreso': 40,
                'presupuesto': 15000000
            }
        ]

    def ver_detalle_obra(self, obra_id):
        """Muestra el detalle de una obra específica."""
        try:
            if self.controller and \
                hasattr(self.controller, 'mostrar_detalle_obra'):
                self.controller.mostrar_detalle_obra(obra_id)
            else:
                show_warning(self, "En desarrollo", f"Funcionalidad de detalle para obra {obra_id} en desarrollo")
        except Exception as e:
            show_error(self, "Error", f"Error mostrando detalle: {str(e)}")

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
        self.btn_duplicar_obra = StandardComponents.create_info_button("[CLIPBOARD] Duplicar")

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

        # Botones movidos desde el header - más pequeños
        btn_actualizar_small = StandardComponents.create_primary_button("🔄 Actualizar")
        btn_estadisticas_small = StandardComponents.create_info_button("[CHART] Estadísticas")
        btn_nueva_obra_small = StandardComponents.create_success_button("➕ Nueva Obra")

        # Estilo compacto para botones pequeños
        for btn in [btn_actualizar_small, btn_estadisticas_small, btn_nueva_obra_small]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    color: #374151;
                    font-weight: 500;
                    font-size: 9px;
                    padding: 2px 6px;
                    min-height: 18px;
                    max-height: 20px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background: #e5e7eb;
                    border: 1px solid #9ca3af;
                }
                QPushButton:pressed {
                    background: #d1d5db;
                }
            """)

        # Conectar eventos
        btn_actualizar_small.clicked.connect(self.actualizar_datos)
        btn_estadisticas_small.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        btn_nueva_obra_small.clicked.connect(self.mostrar_dialogo_nueva_obra)

        # Añadir los botones pequeños
        layout.addWidget(btn_actualizar_small)
        layout.addWidget(btn_estadisticas_small)
        layout.addWidget(btn_nueva_obra_small)

        layout.addStretch()

        # Botones de exportación - extra pequeños
        btn_export_excel = StandardComponents.create_success_button("[CHART] Excel")
        btn_export_pdf = StandardComponents.create_info_button("📄 PDF")

        # Aplicar estilo extra compacto a botones de exportación
        for btn in [btn_export_excel, btn_export_pdf]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    color: #374151;
                    font-weight: 500;
                    font-size: 9px;
                    padding: 2px 6px;
                    min-height: 18px;
                    max-height: 20px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background: #e5e7eb;
                    border: 1px solid #9ca3af;
                }
                QPushButton:pressed {
                    background: #d1d5db;
                }
            """)

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

            # Cargar datos iniciales en el cronograma
            self.actualizar_cronograma()
        else:
            # Usar fallback temporalmente
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

        # Panel de filtros mejorado
        filtros_frame = QFrame()
        filtros_layout = QHBoxLayout(filtros_frame)

        # Vista temporal
        vista_label = RexusLabel("🗓️ Vista:", "subtitle")
        filtros_layout.addWidget(vista_label)

        self.combo_vista_cronograma = QComboBox()
        self.combo_vista_cronograma.addItems(["📅 Semanal",
"📆 Mensual",
            "🗓️ Trimestral",
            "[CHART] Anual"])
        self.combo_vista_cronograma.setCurrentText("📆 Mensual")
        self.combo_vista_cronograma.setStyleSheet("""
            QComboBox {
                min-width: 80px;
                max-width: 100px;
                padding: 2px 4px;
                font-size: 10px;
                border: 1px solid #d1d5db;
                border-radius: 3px;
                background: white;
            }
        """)
        filtros_layout.addWidget(self.combo_vista_cronograma)

        # Separador visual
        separador1 = QFrame()
        separador1.setFrameShape(QFrame.Shape.VLine)
        separador1.setStyleSheet("color: #e2e8f0;")
        filtros_layout.addWidget(separador1)

        # Año
        año_label = RexusLabel("📅 Año:", "subtitle")
        filtros_layout.addWidget(año_label)

        self.combo_año = QComboBox()
        año_actual = datetime.datetime.now().year
        for año in range(año_actual - 2, año_actual + 5):
            self.combo_año.addItem(str(año))
        self.combo_año.setCurrentText(str(año_actual))
        self.combo_año.setStyleSheet("min-width: 70px; padding: 4px;")
        filtros_layout.addWidget(self.combo_año)

        # Estado de obras
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.Shape.VLine)
        separador2.setStyleSheet("color: #e2e8f0;")
        filtros_layout.addWidget(separador2)

        estado_label = RexusLabel("[CONSTRUCTION] Estado:", "subtitle")
        filtros_layout.addWidget(estado_label)

        self.combo_estado_cronograma = QComboBox()
        self.combo_estado_cronograma.addItems([
            "[SEARCH] Todas",
            "🟢 En Progreso",
            "🟡 Pendientes",
            "🔴 Retrasadas",
            "[OK] Finalizadas"
        ])
        self.combo_estado_cronograma.setStyleSheet("min-width: 120px; padding: 4px;")
        filtros_layout.addWidget(self.combo_estado_cronograma)

        layout.addWidget(filtros_frame)

        # Panel de acciones mejorado
        acciones_frame = QFrame()
        acciones_layout = QHBoxLayout(acciones_frame)

        btn_actualizar_cronograma = StandardComponents.create_primary_button("🔄 Actualizar")
        btn_exportar_cronograma = StandardComponents.create_info_button("[CHART] Exportar")
        btn_imprimir_cronograma = StandardComponents.create_secondary_button("🖨️ Imprimir")

        btn_actualizar_cronograma.clicked.connect(self.actualizar_cronograma)
        btn_exportar_cronograma.clicked.connect(lambda: self.exportar_cronograma())
        btn_imprimir_cronograma.clicked.connect(lambda: self.imprimir_cronograma())

        acciones_layout.addWidget(btn_actualizar_cronograma)
        acciones_layout.addWidget(btn_exportar_cronograma)
        acciones_layout.addWidget(btn_imprimir_cronograma)
        acciones_layout.addStretch()

        # Navegación temporal mejorada
        navegacion_label = RexusLabel("🔄 Navegación:", "subtitle")
        acciones_layout.addWidget(navegacion_label)

        btn_anterior = StandardComponents.create_secondary_button("◀ Anterior")
        btn_hoy = StandardComponents.create_info_button("📍 Hoy")
        btn_siguiente = StandardComponents.create_secondary_button("Siguiente ▶")

        for btn in [btn_anterior, btn_hoy, btn_siguiente]:
            btn.setMaximumWidth(100)

        btn_anterior.clicked.connect(self.ir_periodo_anterior)
        btn_hoy.clicked.connect(self.ir_a_hoy)
        btn_siguiente.clicked.connect(self.ir_periodo_siguiente)

        acciones_layout.addWidget(btn_anterior)
        acciones_layout.addWidget(btn_hoy)
        acciones_layout.addWidget(btn_siguiente)

        layout.addWidget(acciones_frame)

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
        icon_label = RexusLabel("📅", "title")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                background: transparent;
                border: none;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Texto principal
        main_text = RexusLabel("Cronograma de Obras", "title")
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
        sub_text = RexusLabel("Vista temporal de obras con fechas de inicio y fin", "caption")
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
        obras_list.setHorizontalHeaderLabels(["Obra",
"Inicio",
            "Fin",
            "Estado"])
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

        # Panel de control de presupuestos
        control_presupuestos = self.crear_panel_control_presupuestos()
        layout.addWidget(control_presupuestos)

        # Splitter para dividir la vista
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo - Lista de obras
        lista_obras = self.crear_widget_lista_obras_presupuestos()
        splitter.addWidget(lista_obras)

        # Panel derecho - Detalle del presupuesto
        detalle_presupuesto = self.crear_widget_detalle_presupuesto()
        splitter.addWidget(detalle_presupuesto)

        # Proporción 35-65 para mejor aprovechamiento
        splitter.setSizes([350, 650])

        layout.addWidget(splitter)
        self.tab_widget.addTab(tab_presupuestos, "Presupuestos")

    def crear_panel_control_presupuestos(self) -> QFrame:
        """Panel de control para gestión de presupuestos."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e8f4fd, stop:1 #f0f9ff);
                border: 2px solid #bfdbfe;
                border-radius: 12px;
                max-height: 80px;
            }
        """)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)

        # Filtros de presupuestos
        filtros_frame = QFrame()
        filtros_layout = QHBoxLayout(filtros_frame)

        # Estado del presupuesto
        estado_label = QLabel("[CHART] Estado:")
        estado_label.setStyleSheet("font-weight: 600; color: #1e40af;")
        filtros_layout.addWidget(estado_label)

        self.combo_estado_presupuesto = QComboBox()
        self.combo_estado_presupuesto.addItems([
            "[SEARCH] Todos",
            "[NOTE] Borrador",
            "[OK] Aprobado",
            "⏳ Pendiente",
            "🔄 Revisión",
            "[ERROR] Rechazado"
        ])
        self.combo_estado_presupuesto.setStyleSheet("min-width: 120px; padding: 4px;")
        filtros_layout.addWidget(self.combo_estado_presupuesto)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.VLine)
        separador.setStyleSheet("color: #bfdbfe;")
        filtros_layout.addWidget(separador)

        # Rango de montos
        monto_label = QLabel("[MONEY] Monto:")
        monto_label.setStyleSheet("font-weight: 600; color: #1e40af;")
        filtros_layout.addWidget(monto_label)

        self.combo_rango_monto = QComboBox()
        self.combo_rango_monto.addItems([
            "[SEARCH] Todos",
            "💵 Hasta $100K",
            "💴 $100K - $500K",
            "💶 $500K - $1M",
            "💷 Más de $1M"
        ])
        self.combo_rango_monto.setStyleSheet("min-width: 130px; padding: 4px;")
        filtros_layout.addWidget(self.combo_rango_monto)

        layout.addWidget(filtros_frame)
        layout.addStretch()

        # Acciones de presupuestos
        acciones_frame = QFrame()
        acciones_layout = QHBoxLayout(acciones_frame)

        btn_nuevo_presupuesto = StandardComponents.create_success_button("➕ Nuevo")
        btn_comparar_presupuestos = StandardComponents.create_info_button("⚖️ Comparar")
        btn_exportar_presupuestos = StandardComponents.create_primary_button("[CHART] Exportar")
        btn_imprimir_presupuestos = StandardComponents.create_secondary_button("🖨️ Imprimir")

        for btn in [btn_nuevo_presupuesto, btn_comparar_presupuestos, btn_exportar_presupuestos, btn_imprimir_presupuestos]:
            btn.setMaximumWidth(100)

        btn_nuevo_presupuesto.clicked.connect(self.crear_nuevo_presupuesto)
        btn_comparar_presupuestos.clicked.connect(self.comparar_presupuestos)
        btn_exportar_presupuestos.clicked.connect(self.exportar_presupuestos)
        btn_imprimir_presupuestos.clicked.connect(self.imprimir_presupuesto_actual)

        acciones_layout.addWidget(btn_nuevo_presupuesto)
        acciones_layout.addWidget(btn_comparar_presupuestos)
        acciones_layout.addWidget(btn_exportar_presupuestos)
        acciones_layout.addWidget(btn_imprimir_presupuestos)

        layout.addWidget(acciones_frame)

        return panel

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
        header_label = QLabel("[CONSTRUCTION] Obras para Presupuestar")
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
        self.presupuesto_header = QLabel("[MONEY] Seleccionar una obra para ver presupuesto")
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
        self.tab_widget.addTab(tab_stats, "Estadísticas")

    def crear_widget_resumen_obras(self) -> QWidget:
        """Widget de resumen de obras."""
        return self._crear_widget_estadistica(
            "[CONSTRUCTION] Resumen de Obras",
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
            "[TRENDING] Por Estado",
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
            "[MONEY] Presupuestos Mes",
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
        """Actualiza los datos del cronograma con obras reales."""
        if hasattr(self, 'cronograma_widget'):
            # Obtener datos de obras desde la tabla principal
            obras_data = self.obtener_datos_obras_ejemplo()  # Usar datos de ejemplo por ahora

            # Convertir formato para el cronograma
            obras_cronograma = []
            for obra in obras_data:
                obra_cronograma = {
                    'id': obra.get('id'),
                    'codigo': obra.get('codigo', ''),
                    'nombre': obra.get('nombre', ''),
                    'cliente': obra.get('cliente', ''),
                    'estado': obra.get('estado', 'Planificación'),
                    'tipo': obra.get('tipo', 'Residencial'),
                    'fecha_inicio': obra.get('fecha_inicio', '2024-01-01'),
                    'fecha_fin_estimada': obra.get('fecha_fin', '2024-12-31'),
                    'progreso': obra.get('progreso', 0),
                    'presupuesto': obra.get('presupuesto', 0)
                }
                obras_cronograma.append(obra_cronograma)

            # Cargar datos en el cronograma
            try:
                self.cronograma_widget.cargar_obras(obras_cronograma)
            except Exception as e:
                logger.info(f"Error al cargar obras en cronograma: {e}")

    def exportar_cronograma(self):
        """Exporta el cronograma actual."""
        try:
            from rexus.utils.export_manager import ExportManager

            export_manager = ExportManager()
            vista = self.combo_vista_cronograma.currentText()
            año = self.combo_año.currentText()
            self.combo_estado_cronograma.currentText()

            filename = f

            # Datos del cronograma para exportar
            datos_cronograma = self.obtener_datos_cronograma()
            export_manager.exportar_cronograma(datos_cronograma, filename)

            show_success(self, "Éxito", f"Cronograma exportado exitosamente como {filename}")
        except Exception as e:
            show_error(self, "Error", f"Error al exportar cronograma: {str(e)}")

    def imprimir_cronograma(self):
        """Imprime el cronograma actual."""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt6.QtGui import QPainter

            printer = QPrinter()
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                painter = QPainter(printer)

                # Crear contenido para imprimir
                if hasattr(self, 'cronograma_widget'):
                    self.cronograma_widget.render(painter)
                else:
                    # Fallback para imprimir información básica
                    painter.drawText(100, 100, )
                    painter.drawText(100, 150, f"Vista: {self.combo_vista_cronograma.currentText()}")
                    painter.drawText(100, 200, f"Año: {self.combo_año.currentText()}")

                painter.end()
                show_success(self, "Éxito", "Cronograma enviado a la impresora")
        except Exception as e:
            show_error(self, "Error", f"Error al imprimir cronograma: {str(e)}")

    def ir_periodo_anterior(self):
        """Navega al período anterior."""
        vista_actual = self.combo_vista_cronograma.currentText()
        año_actual = int(self.combo_año.currentText())

        if "Semanal" in vista_actual or "Mensual" in vista_actual:
            # Para vistas semanales/mensuales, retroceder 1 mes
            if hasattr(self, 'cronograma_widget'):
                # Implementar navegación específica del cronograma
                pass
        elif "Anual" in vista_actual:
            # Para vista anual, retroceder 1 año
            nuevo_año = año_actual - 1
            if nuevo_año >= año_actual - 5:  # Límite de años hacia atrás
                self.combo_año.setCurrentText(str(nuevo_año))

        self.actualizar_cronograma()

    def ir_a_hoy(self):
        """Navega al período actual (hoy)."""
        año_actual = datetime.datetime.now().year
        self.combo_año.setCurrentText(str(año_actual))
        self.actualizar_cronograma()

    def ir_periodo_siguiente(self):
        """Navega al período siguiente."""
        vista_actual = self.combo_vista_cronograma.currentText()
        año_actual = int(self.combo_año.currentText())

        if "Semanal" in vista_actual or "Mensual" in vista_actual:
            # Para vistas semanales/mensuales, avanzar 1 mes
            if hasattr(self, 'cronograma_widget'):
                # Implementar navegación específica del cronograma
                pass
        elif "Anual" in vista_actual:
            # Para vista anual, avanzar 1 año
            nuevo_año = año_actual + 1
            if nuevo_año <= datetime.datetime.now().year + 5:  # Límite de años hacia adelante
                self.combo_año.setCurrentText(str(nuevo_año))

        self.actualizar_cronograma()

    def obtener_datos_cronograma(self):
        """Obtiene los datos actuales del cronograma para exportar."""
        return {
            'vista': self.combo_vista_cronograma.currentText(),
            'año': self.combo_año.currentText(),
            'estado_filtro': self.combo_estado_cronograma.currentText(),
            'fecha_generacion': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'obras': []  # Aquí se cargarían las obras del cronograma
        }

    def crear_nuevo_presupuesto(self):
        """Crea un nuevo presupuesto."""
        try:
            from .dialogo_presupuesto import DialogoPresupuesto
            dialogo = DialogoPresupuesto(self, modo='nuevo')
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                dialogo.obtener_datos()
                # Aquí se enviarían los datos al controlador
                show_success(self, "Éxito", "Presupuesto creado exitosamente")
        except ImportError:
            # Fallback simple
            show_warning(self, "En desarrollo", "Funcionalidad de presupuesto en desarrollo")

    def comparar_presupuestos(self):
        """Abre diálogo para comparar presupuestos."""
        try:
            from .dialogo_comparacion_presupuestos import DialogoComparacionPresupuestos
            dialogo = DialogoComparacionPresupuestos(self)
            dialogo.exec()
        except ImportError:
            # Fallback simple
            show_warning(self, "En desarrollo", "Comparación de presupuestos en desarrollo")

    def exportar_presupuestos(self):
        """Exporta presupuestos filtrados."""
        try:
            estado = self.combo_estado_presupuesto.currentText()
            rango = self.combo_rango_monto.currentText()

            # Datos para exportar
            datos_export = {
                'filtro_estado': estado,
                'filtro_monto': rango,
                'fecha_export': datetime.datetime.now().strftime("%Y-%m-%d"),
                'presupuestos': []  # Cargar desde controlador
            }

            filename = f"presupuestos_{estado.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"

            # Usar export manager
            from rexus.utils.export_manager import ExportManager
            export_manager = ExportManager()
            export_manager.exportar_presupuestos(datos_export, filename)

            show_success(self, "Éxito", f"Presupuestos exportados como {filename}")
        except Exception as e:
            show_error(self, "Error", f"Error al exportar: {str(e)}")

    def imprimir_presupuesto_actual(self):
        """Imprime el presupuesto seleccionado."""
        try:
            if hasattr(self, 'lista_presupuestos'):
                item_actual = self.lista_presupuestos.currentItem()
                if item_actual:
                    from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
                    from PyQt6.QtGui import QPainter

                    printer = QPrinter()
                    dialog = QPrintDialog(printer, self)

                    if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                        painter = QPainter(printer)

                        # Crear contenido del presupuesto
                        painter.drawText(100, 100, f)
                        painter.drawText(100, 150, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d')}")

                        painter.end()
                        show_success(self, "Éxito", "Presupuesto enviado a la impresora")
                else:
                    show_warning(self, "Atención", "Seleccione un presupuesto para imprimir")
            else:
                show_warning(self, "Información", "No hay presupuestos disponibles")
        except Exception as e:
            show_error(self, "Error", f"Error al imprimir presupuesto: {str(e)}")

    def actualizar_detalle_presupuesto(self):
        """Actualiza los detalles del presupuesto seleccionado."""
        row = self.lista_presupuestos.currentRow()
        if row >= 0:
            codigo_item = self.lista_presupuestos.item(row, 0)
            if codigo_item:
                codigo = codigo_item.text()
                self.presupuesto_header.setText(f"[MONEY] Presupuesto: {codigo}")
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
        tabla_items.setHorizontalHeaderLabels(["Item",
"Descripción",
            "Cantidad",
            "Precio Unit.",
            "Total"])
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
        btn_aprobar = StandardComponents.create_success_button("[OK] Aprobar")

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
                    btn.clicked.connect(lambda checked, r=row: self.ver_detalle_obra_tabla(r))
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

    # === MÉTODOS DE PAGINACIÓN ===

    def crear_controles_paginacion(self) -> QFrame:
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
        self.info_label = QLabel("Mostrando 1-50 de 0 obras")
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
            self.info_label.setText(f"Mostrando {inicio}-{fin} de {total_registros} obras")

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
        """Carga datos en la tabla de obras para paginación."""
        if not datos:
            self.tabla_obras.setRowCount(0)
            return

        self.tabla_obras.setRowCount(len(datos))
        
        for row, obra in enumerate(datos):
            # Crear items para cada columna según la estructura de obras
            items = [
                str(obra.get('id', '')),
                str(obra.get('codigo', '')),
                str(obra.get('nombre', '')),
                str(obra.get('cliente', '')),
                str(obra.get('estado', '')),
                str(obra.get('tipo', '')),
                str(obra.get('fecha_inicio', '')),
                str(obra.get('fecha_fin', '')),
                f"{obra.get('progreso', 0)}%",
                f"${obra.get('presupuesto', 0):,.2f}"
            ]
            
            for col, item_text in enumerate(items):
                if col < len(items) - 1:  # No agregar botón en la última columna por ahora
                    item = QTableWidgetItem(item_text)
                    
                    # Colorear según estado (columna 4)
                    if col == 4:
                        if item_text == "En Curso":
                            item.setBackground(QColor("#dcfce7"))
                        elif item_text == "Pausada":
                            item.setBackground(QColor("#fef3c7"))
                        elif item_text == "Finalizada":
                            item.setBackground(QColor("#e0e7ff"))
                        elif item_text == "Planificación":
                            item.setBackground(QColor("#f3e8ff"))
                    
                    self.tabla_obras.setItem(row, col, item)


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
        self.tipo_combo.addItems(["Residencial",
"Comercial",
            "Industrial",
            "Público"])

        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Planificación",
"En Curso",
            "Pausada",
            "Finalizada",
            "Cancelada"])

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

    # === MÉTODO PARA BOTÓN CORREGIDO ===

    def ver_detalle_obra_tabla(self, row):
        """Ver detalle de obra desde tabla."""
        show_success(self, "Ver Obra", f"Mostrando detalle de la obra en fila {row + 1}")


# Alias para compatibilidad con importaciones existentes
ObrasView = ObrasModernView
