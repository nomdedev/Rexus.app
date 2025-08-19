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

Vista de Mantenimiento - Interfaz de mantenimiento
"""

import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QLabel,
    QFrame,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QTabWidget,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QProgressBar,
    QFrame,
)

from rexus.utils.message_system import show_error, show_success
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusColors,
)

# Importar utilidades de sanitización

from rexus.utils.xss_protection import FormProtector, XSSProtection
from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager


class MantenimientoView(QWidget):
    """Vista principal del módulo de mantenimiento."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario con pestañas completas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Widget de pestañas principal
        self.tab_widget = QTabWidget()
        self.create_all_tabs()
        layout.addWidget(self.tab_widget)

        # Aplicar tema del módulo
        style_manager.apply_module_theme(self)

        # Aplicar estilos después de crear la interfaz
        self.aplicar_estilos()

        # Inicializar protección XSS
        self.init_xss_protection()

    def create_all_tabs(self):
        """Crea todas las pestañas del módulo."""
        # Pestaña 1: Órdenes de Trabajo
        ordenes_tab = self.create_ordenes_trabajo_tab()
        self.tab_widget.addTab(ordenes_tab, "Órdenes de Trabajo")

        # Pestaña 2: Mantenimiento Preventivo
        preventivo_tab = self.create_mantenimiento_preventivo_tab()
        self.tab_widget.addTab(preventivo_tab, "🔄 Mantenimiento Preventivo")

        # Pestaña 3: Inventario de Repuestos
        inventario_tab = self.create_inventario_repuestos_tab()
        self.tab_widget.addTab(inventario_tab, "Inventario Repuestos")

        # Pestaña 4: Equipos y Activos
        equipos_tab = self.create_equipos_activos_tab()
        self.tab_widget.addTab(equipos_tab, "Equipos y Activos")

        # Pestaña 5: Reportes y Análisis
        reportes_tab = self.create_reportes_analisis_tab()
        self.tab_widget.addTab(reportes_tab, "Reportes y Análisis")

        # Pestaña 6: Configuración
        config_tab = self.create_configuracion_tab()
        self.tab_widget.addTab(config_tab, "Configuración")

    def create_ordenes_trabajo_tab(self):
        """Crea la pestaña de órdenes de trabajo."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Panel de control
        control_panel = self.create_ordenes_control_panel()
        layout.addWidget(control_panel)

        # Tabla de órdenes
        self.tabla_ordenes = StandardComponents.create_standard_table()
        self.configurar_tabla_ordenes()
        layout.addWidget(self.tabla_ordenes)

        # Controles de paginación
        paginacion_panel = self.crear_controles_paginacion()
        layout.addWidget(paginacion_panel)

        return tab_widget

    def create_ordenes_control_panel(self):
        """Panel de control para órdenes de trabajo."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón nueva orden
        btn_nueva_orden = StandardComponents.create_primary_button("➕ Nueva Orden")
        btn_nueva_orden.clicked.connect(self.nueva_orden_trabajo)
        layout.addWidget(btn_nueva_orden)

        # Filtros
        self.filtro_estado = RexusComboBox()
        self.filtro_estado.addItems(["Todas",
"Pendiente",
            "En Progreso",
            "Completada",
            "Cancelada"])
        layout.addWidget(RexusLabel("Estado:"))
        layout.addWidget(self.filtro_estado)

        self.filtro_prioridad = RexusComboBox()
        self.filtro_prioridad.addItems(["Todas",
"Alta",
            "Media",
            "Baja",
            "Crítica"])
        layout.addWidget(RexusLabel("Prioridad:"))
        layout.addWidget(self.filtro_prioridad)

        # Búsqueda
        self.busqueda_ordenes = RexusLineEdit()
        self.busqueda_ordenes.setPlaceholderText("Buscar órdenes...")
        layout.addWidget(self.busqueda_ordenes)

        btn_buscar = StandardComponents.create_secondary_button("[SEARCH] Buscar")
        layout.addWidget(btn_buscar)

        btn_actualizar = StandardComponents.create_secondary_button("🔄 Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_ordenes)
        layout.addWidget(btn_actualizar)

        return panel

    def configurar_tabla_ordenes(self):
        """Configura la tabla de órdenes de trabajo."""
        self.tabla_ordenes.setColumnCount(8)
        self.tabla_ordenes.setHorizontalHeaderLabels([
            "ID", "Título", "Equipo", "Prioridad", "Estado", "Asignado", "Fecha", "Acciones"
        ])

        # Datos de ejemplo
        datos_ejemplo = [
            ["001", "Cambio de filtros", "Compresor A1", "Alta", "Pendiente", "Juan Pérez", "2024-01-15", "Ver"],
            ["002", "Revisión eléctrica", "Motor B2", "Media", "En Progreso", "Ana García", "2024-01-12", "Ver"],
            ["003", "Lubricación general", "Bomba C3", "Baja", "Completada", "Carlos López", "2024-01-10", "Ver"],
            ["004", "Reparación urgente", "Generador D4", "Crítica", "Pendiente", "María Rodríguez", "2024-01-16", "Ver"],
        ]

        self.tabla_ordenes.setRowCount(len(datos_ejemplo))
        for row, data in enumerate(datos_ejemplo):
            for col, value in enumerate(data):
                if col == 7:  # Acciones
                    btn_acciones = self.create_actions_button(row)
                    self.tabla_ordenes.setCellWidget(row, col, btn_acciones)
                else:
                    item = QTableWidgetItem(str(value))
                    # Colorear por prioridad y estado
                    if col == 3:  # Prioridad
                        if value == "Crítica":
                            item.setBackground(QColor(220, 38, 38, 50))
                        elif value == "Alta":
                            item.setBackground(QColor(245, 101, 101, 50))
                        elif value == "Media":
                            item.setBackground(QColor(251, 191, 36, 50))
                    elif col == 4:  # Estado
                        if value == "Completada":
                            item.setBackground(QColor(34, 197, 94, 50))
                        elif value == "En Progreso":
                            item.setBackground(QColor(59, 130, 246, 50))
                        elif value == "Pendiente":
                            item.setBackground(QColor(156, 163, 175, 50))
                    self.tabla_ordenes.setItem(row, col, item)

    def create_mantenimiento_preventivo_tab(self):
        """Crea la pestaña de mantenimiento preventivo."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Panel superior con programación
        programacion_panel = self.create_programacion_panel()
        layout.addWidget(programacion_panel)

        # Tabla de mantenimientos programados
        self.tabla_preventivo = StandardComponents.create_standard_table()
        self.configurar_tabla_preventivo()
        layout.addWidget(self.tabla_preventivo)

        return tab_widget

    def create_programacion_panel(self):
        """Panel de programación de mantenimiento preventivo."""
        panel = QGroupBox("📅 Programación de Mantenimiento Preventivo")
        layout = QGridLayout(panel)

        # Selector de equipo
        layout.addWidget(RexusLabel("Equipo:"), 0, 0)
        self.combo_equipo_preventivo = RexusComboBox()
        self.combo_equipo_preventivo.addItems(["Compresor A1",
"Motor B2",
            "Bomba C3",
            "Generador D4"])
        layout.addWidget(self.combo_equipo_preventivo, 0, 1)

        # Tipo de mantenimiento
        layout.addWidget(RexusLabel("Tipo:"), 0, 2)
        self.combo_tipo_preventivo = RexusComboBox()
        self.combo_tipo_preventivo.addItems(["Diario",
"Semanal",
            "Mensual",
            "Trimestral",
            "Semestral",
            "Anual"])
        layout.addWidget(self.combo_tipo_preventivo, 0, 3)

        # Frecuencia
        layout.addWidget(RexusLabel("Cada:"), 1, 0)
        self.spin_frecuencia = QSpinBox()
        self.spin_frecuencia.setRange(1, 365)
        self.spin_frecuencia.setValue(30)
        layout.addWidget(self.spin_frecuencia, 1, 1)

        layout.addWidget(RexusLabel("días"), 1, 2)

        # Botones
        btn_programar = StandardComponents.create_primary_button("📅 Programar Mantenimiento")
        btn_programar.clicked.connect(self.programar_mantenimiento)
        layout.addWidget(btn_programar, 1, 3)

        return panel

    def configurar_tabla_preventivo(self):
        """Configura tabla de mantenimiento preventivo."""
        self.tabla_preventivo.setColumnCount(7)
        self.tabla_preventivo.setHorizontalHeaderLabels([
            "Equipo", "Tipo", "Frecuencia", "Última Fecha", "Próxima Fecha", "Estado", "Acciones"
        ])

        datos = [
            ["Compresor A1", "Mensual", "30 días", "2023-12-15", "2024-01-15", "Vencido", "Ejecutar"],
            ["Motor B2", "Semanal", "7 días", "2024-01-08", "2024-01-15", "Próximo", "Ver"],
            ["Bomba C3", "Trimestral", "90 días", "2023-10-15", "2024-01-15", "Programado", "Ver"],
        ]

        self.tabla_preventivo.setRowCount(len(datos))
        for row, data in enumerate(datos):
            for col, value in enumerate(data):
                if col == 6:  # Acciones
                    btn = QPushButton(value)
                    btn.setStyleSheet("background: #10b981; color: white; border: none; border-radius: 4px; padding: 6px;")
                    btn.clicked.connect(lambda checked, r=row: self.ejecutar_accion_preventivo(r))
                    self.tabla_preventivo.setCellWidget(row, col, btn)
                else:
                    item = QTableWidgetItem(str(value))
                    if col == 5:  # Estado
                        if value == "Vencido":
                            item.setBackground(QColor(239, 68, 68, 50))
                        elif value == "Próximo":
                            item.setBackground(QColor(245, 158, 11, 50))
                        elif value == "Programado":
                            item.setBackground(QColor(34, 197, 94, 50))
                    self.tabla_preventivo.setItem(row, col, item)

    def create_inventario_repuestos_tab(self):
        """Crea pestaña de inventario de repuestos."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Panel de control de inventario
        inventario_control = self.create_inventario_control_panel()
        layout.addWidget(inventario_control)

        # Tabla de repuestos
        self.tabla_repuestos = StandardComponents.create_standard_table()
        self.configurar_tabla_repuestos()
        layout.addWidget(self.tabla_repuestos)

        return tab_widget

    def create_inventario_control_panel(self):
        """Panel de control de inventario."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(panel)

        btn_nuevo_repuesto = StandardComponents.create_primary_button("➕ Nuevo Repuesto")
        layout.addWidget(btn_nuevo_repuesto)

        btn_entrada = StandardComponents.create_secondary_button("📥 Entrada")
        layout.addWidget(btn_entrada)

        btn_salida = StandardComponents.create_secondary_button("📤 Salida")
        layout.addWidget(btn_salida)

        # Filtros de stock
        layout.addWidget(RexusLabel("Stock:"))
        self.filtro_stock = RexusComboBox()
        self.filtro_stock.addItems(["Todos",
"Stock Bajo",
            "Sin Stock",
            "Stock Normal",
            "Sobre Stock"])
        layout.addWidget(self.filtro_stock)

        # Búsqueda
        self.busqueda_repuestos = RexusLineEdit()
        self.busqueda_repuestos.setPlaceholderText("Buscar repuestos...")
        layout.addWidget(self.busqueda_repuestos)

        btn_buscar = StandardComponents.create_secondary_button("[SEARCH]")
        layout.addWidget(btn_buscar)

        return panel

    def configurar_tabla_repuestos(self):
        """Configura tabla de repuestos."""
        self.tabla_repuestos.setColumnCount(8)
        self.tabla_repuestos.setHorizontalHeaderLabels([
            "Código", "Descripción", "Stock Actual", "Stock Mínimo", "Precio", "Ubicación", "Estado", "Acciones"
        ])

        datos = [
            ["REP001", "Filtro de aire grande", "25", "10", "$45.00", "A-1-B", "Normal", "Ver"],
            ["REP002", "Aceite hidráulico", "5", "15", "$120.00", "B-2-C", "Bajo", "Ver"],
            ["REP003", "Correa de transmisión", "0", "5", "$85.00", "C-1-A", "Sin Stock", "Ver"],
            ["REP004", "Rodamiento 6205", "50", "20", "$25.00", "A-3-B", "Normal", "Ver"],
        ]

        self.tabla_repuestos.setRowCount(len(datos))
        for row, data in enumerate(datos):
            for col, value in enumerate(data):
                if col == 7:  # Acciones
                    btn = QPushButton("Ver")
                    btn.setStyleSheet("background: #3b82f6; color: white; border: none; border-radius: 4px; padding: 6px;")
                    btn.clicked.connect(lambda checked, r=row: self.ver_detalle_repuesto(r))
                    self.tabla_repuestos.setCellWidget(row, col, btn)
                else:
                    item = QTableWidgetItem(str(value))
                    if col == 6:  # Estado
                        if value == "Sin Stock":
                            item.setBackground(QColor(239, 68, 68, 50))
                        elif value == "Bajo":
                            item.setBackground(QColor(245, 158, 11, 50))
                        elif value == "Normal":
                            item.setBackground(QColor(34, 197, 94, 50))
                    self.tabla_repuestos.setItem(row, col, item)

    def create_equipos_activos_tab(self):
        """Crea pestaña de equipos y activos."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Panel de equipos
        equipos_control = self.create_equipos_control_panel()
        layout.addWidget(equipos_control)

        # Tabla de equipos
        self.tabla_equipos = StandardComponents.create_standard_table()
        self.configurar_tabla_equipos()
        layout.addWidget(self.tabla_equipos)

        return tab_widget

    def create_equipos_control_panel(self):
        """Panel de control de equipos."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(panel)

        btn_nuevo_equipo = StandardComponents.create_primary_button("➕ Nuevo Equipo")
        layout.addWidget(btn_nuevo_equipo)

        btn_historial = StandardComponents.create_secondary_button("[CLIPBOARD] Historial")
        layout.addWidget(btn_historial)

        # Filtros
        layout.addWidget(RexusLabel("Estado:"))
        self.filtro_estado_equipo = RexusComboBox()
        self.filtro_estado_equipo.addItems(["Todos", "Operativo", "En Mantenimiento", "Fuera de Servicio", "En Reparación"])
        layout.addWidget(self.filtro_estado_equipo)

        layout.addWidget(RexusLabel("Ubicación:"))
        self.filtro_ubicacion = RexusComboBox()
        self.filtro_ubicacion.addItems(["Todas",
"Planta A",
            "Planta B",
            "Almacén",
            "Oficinas"])
        layout.addWidget(self.filtro_ubicacion)

        return panel

    def configurar_tabla_equipos(self):
        """Configura tabla de equipos."""
        self.tabla_equipos.setColumnCount(8)
        self.tabla_equipos.setHorizontalHeaderLabels([
            "Código", "Nombre", "Tipo", "Marca", "Ubicación", "Estado", "Último Mant.", "Acciones"
        ])

        datos = [
            ["EQ001", "Compresor Principal", "Compresor", "Atlas Copco", "Planta A", "Operativo", "2023-12-15", "Ver"],
            ["EQ002", "Motor Bomba 1", "Motor", "Siemens", "Planta B", "En Mantenimiento", "2024-01-10", "Ver"],
            ["EQ003", "Generador Emergencia", "Generador", "Caterpillar", "Planta A", "Operativo", "2023-11-20", "Ver"],
            ["EQ004", "Bomba Centrífuga", "Bomba", "Grundfos", "Planta B", "En Reparación", "2024-01-05", "Ver"],
        ]

        self.tabla_equipos.setRowCount(len(datos))
        for row, data in enumerate(datos):
            for col, value in enumerate(data):
                if col == 7:  # Acciones
                    btn = QPushButton("Ver")
                    btn.setStyleSheet("background: #3b82f6; color: white; border: none; border-radius: 4px; padding: 6px;")
                    btn.clicked.connect(lambda checked, r=row: self.ver_detalle_equipo(r))
                    self.tabla_equipos.setCellWidget(row, col, btn)
                else:
                    item = QTableWidgetItem(str(value))
                    if col == 5:  # Estado
                        if value == "Operativo":
                            item.setBackground(QColor(34, 197, 94, 50))
                        elif value == "En Mantenimiento":
                            item.setBackground(QColor(59, 130, 246, 50))
                        elif value == "En Reparación":
                            item.setBackground(QColor(245, 158, 11, 50))
                        elif value == "Fuera de Servicio":
                            item.setBackground(QColor(239, 68, 68, 50))
                    self.tabla_equipos.setItem(row, col, item)

    def create_reportes_analisis_tab(self):
        """Crea pestaña de reportes y análisis."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Panel de reportes
        reportes_panel = self.create_reportes_panel()
        layout.addWidget(reportes_panel)

        # Panel de métricas
        metricas_panel = self.create_metricas_panel()
        layout.addWidget(metricas_panel)

        return tab_widget

    def create_reportes_panel(self):
        """Panel de generación de reportes."""
        panel = QGroupBox("[CHART] Generación de Reportes")
        layout = QGridLayout(panel)

        # Tipos de reporte
        layout.addWidget(RexusLabel("Tipo de Reporte:"), 0, 0)
        self.combo_tipo_reporte = RexusComboBox()
        self.combo_tipo_reporte.addItems([
            "Órdenes de Trabajo Completadas",
            "Mantenimiento Preventivo",
            "Costos de Mantenimiento",
            "Inventario de Repuestos",
            "Disponibilidad de Equipos",
            "Análisis de Fallos"
        ])
        layout.addWidget(self.combo_tipo_reporte, 0, 1)

        # Período
        layout.addWidget(RexusLabel("Período:"), 0, 2)
        self.combo_periodo = RexusComboBox()
        self.combo_periodo.addItems(["Última Semana",
"Último Mes",
            "Últimos 3 Meses",
            "Último Año",
            "Personalizado"])
        layout.addWidget(self.combo_periodo, 0, 3)

        # Botones de reportes
        btn_generar = StandardComponents.create_primary_button("[CHART] Generar Reporte")
        btn_generar.clicked.connect(self.generar_reporte)
        layout.addWidget(btn_generar, 1, 0)

        btn_exportar = StandardComponents.create_secondary_button("📤 Exportar Excel")
        layout.addWidget(btn_exportar, 1, 1)

        btn_imprimir = StandardComponents.create_secondary_button("🖨️ Imprimir")
        layout.addWidget(btn_imprimir, 1, 2)

        return panel

    def create_metricas_panel(self):
        """Panel de métricas clave."""
        panel = QGroupBox("[TRENDING] Métricas Clave de Mantenimiento")
        layout = QGridLayout(panel)

        # KPIs con barras de progreso
        kpis = [
            ("[TARGET] Disponibilidad de Equipos", 92, "%"),
            ("⏱️ Tiempo Promedio de Reparación", 4.5, "hrs"),
            ("[MONEY] Costo Promedio por Orden", 350, "$"),
            ("[OK] Cumplimiento Preventivo", 78, "%"),
        ]

        for i, (titulo, valor, unidad) in enumerate(kpis):
            # Título
            titulo_label = RexusLabel(titulo)
            layout.addWidget(titulo_label, i*2, 0, 1, 2)

            # Valor
            valor_label = RexusLabel(f"{valor}{unidad}")
            valor_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")
            layout.addWidget(valor_label, i*2, 2)

            # Barra de progreso (solo para porcentajes)
            if unidad == "%":
                progress = QProgressBar()
                progress.setValue(int(valor))
                progress.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #e5e7eb;
                        border-radius: 4px;
                        text-align: center;
                        font-size: 11px;
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #3b82f6, stop:1 #1d4ed8);
                        border-radius: 4px;
                    }
                """)
                layout.addWidget(progress, i*2+1, 0, 1, 3)

        return panel

    def create_configuracion_tab(self):
        """Crea pestaña de configuración."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Configuraciones generales
        config_panel = QGroupBox("[SETTINGS] Configuración General")
        config_layout = QGridLayout(config_panel)

        # Notificaciones
        config_layout.addWidget(RexusLabel("Notificaciones:"), 0, 0)
        self.check_notif_vencimiento = QCheckBox("Avisar vencimientos")
        self.check_notif_vencimiento.setChecked(True)
        config_layout.addWidget(self.check_notif_vencimiento, 0, 1)

        self.check_notif_stock = QCheckBox("Avisar stock bajo")
        self.check_notif_stock.setChecked(True)
        config_layout.addWidget(self.check_notif_stock, 0, 2)

        # Días de anticipación
        config_layout.addWidget(RexusLabel("Días de anticipación:"), 1, 0)
        self.spin_dias_anticipacion = QSpinBox()
        self.spin_dias_anticipacion.setRange(1, 30)
        self.spin_dias_anticipacion.setValue(7)
        config_layout.addWidget(self.spin_dias_anticipacion, 1, 1)

        # Auto-backup
        config_layout.addWidget(RexusLabel("Auto-backup:"), 2, 0)
        self.check_auto_backup = QCheckBox("Activar backup automático")
        config_layout.addWidget(self.check_auto_backup, 2, 1)

        self.combo_frecuencia_backup = RexusComboBox()
        self.combo_frecuencia_backup.addItems(["Diario", "Semanal", "Mensual"])
        config_layout.addWidget(self.combo_frecuencia_backup, 2, 2)

        # Botón guardar configuración
        btn_guardar_config = StandardComponents.create_primary_button("💾 Guardar Configuración")
        config_layout.addWidget(btn_guardar_config, 3, 0, 1, 3)

        layout.addWidget(config_panel)
        layout.addStretch()

        return tab_widget

    # Métodos de funcionalidad
    def nueva_orden_trabajo(self):
        """Abre diálogo para nueva orden de trabajo."""
        show_success(self, "Nueva Orden", "Abriendo formulario de nueva orden de trabajo...")

    def actualizar_ordenes(self):
        """Actualiza la tabla de órdenes."""
        show_success(self, "Actualizado", "Órdenes de trabajo actualizadas")

    def programar_mantenimiento(self):
        """Programa nuevo mantenimiento preventivo."""
        equipo = self.combo_equipo_preventivo.currentText()
        tipo = self.combo_tipo_preventivo.currentText()
        frecuencia = self.spin_frecuencia.value()
        show_success(self, "Programado", f"Mantenimiento {tipo} programado para {equipo} cada {frecuencia} días")

    def generar_reporte(self):
        """Genera reporte seleccionado."""
        tipo = self.combo_tipo_reporte.currentText()
        periodo = self.combo_periodo.currentText()
        show_success(self, "Reporte Generado", f"Reporte '{tipo}' generado para el período '{periodo}'")

    def create_actions_button(self, row):
        """Crea botón de acciones para tabla."""
        btn = QPushButton("[SETTINGS] Acciones")
        btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
        """)
        btn.clicked.connect(lambda: self.mostrar_acciones(row))
        return btn

    def mostrar_acciones(self, row):
        """Muestra menú de acciones para fila."""
        show_success(self, "Acciones", f"Mostrando acciones para fila {row + 1}")

    def editar_registro(self, row):
        """Edita un registro de la tabla."""
        show_success(self, "Editar", f"Editando registro de la fila {row + 1}")

    # Métodos heredados adaptados
    def setup_control_panel(self, panel):
        """Método heredado - ya no se usa con pestañas."""

    def configurar_tabla(self):
        """Método heredado - configuración en pestañas individuales."""

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
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                color: #586069;
                min-width: 80px;
                height: 24px;
                max-height: 24px;
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
                background: transparent;
                color: #1e293b;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px 6px;
                text-align: left;
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

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, "input_busqueda"):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")

        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def setup_control_panel(self, panel):
        """Configura el panel de control con componentes estandarizados."""
        layout = QHBoxLayout(panel)

        # Botón Nuevo estandarizado
        self.btn_nuevo = StandardComponents.create_primary_button("[TOOL] Nuevo Mantenimiento")
        self.btn_nuevo.clicked.connect(self.nuevo_registro)
        layout.addWidget(self.btn_nuevo)

        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar...")
        self.input_busqueda.returnPressed.connect(self.buscar)
        layout.addWidget(self.input_busqueda)

        # Botón buscar estandarizado
        self.btn_buscar = StandardComponents.create_secondary_button("[SEARCH] Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_secondary_button("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

    def configurar_tabla(self):
        """Configura la tabla principal."""
        self.tabla_principal.setColumnCount(5)
        self.tabla_principal.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Descripción", "Estado", "Acciones"]
        )

        # Configurar encabezados
        header = self.tabla_principal.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        # Desactivar filas alternadas para evitar problemas
        self.tabla_principal.setAlternatingRowColors(False)
        self.tabla_principal.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        # Cargar datos de ejemplo para verificar funcionalidad
        self.cargar_datos_ejemplo()

    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para mostrar funcionalidad."""
        datos_ejemplo = [
            ["1", "Mantenimiento Equipos", "Revisión general de equipos", "Pendiente", "Ver"],
            ["2", "Backup Database", "Respaldo semanal de base de datos", "Completado", "Ver"],
            ["3", "Limpieza Sistema", "Limpieza de archivos temporales", "En Progreso", "Ver"],
            ["4", "Update Software", "Actualización de sistema", "Programado", "Ver"],
        ]

        self.tabla_principal.setRowCount(len(datos_ejemplo))
        for row, data in enumerate(datos_ejemplo):
            for col, value in enumerate(data):
                if col == 4:  # Columna de acciones
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
                    btn.clicked.connect(lambda checked, r=row: self.ver_detalle(r))
                    self.tabla_principal.setCellWidget(row, col, btn)
                else:
                    item = QTableWidgetItem(str(value))
                    if col == 3:  # Columna Estado
                        if value == "Completado":
                            item.setBackground(QColor(46,
204,
                                113,
                                50))  # Verde claro
                        elif value == "En Progreso":
                            item.setBackground(QColor(243,
156,
                                18,
                                50))  # Amarillo claro
                        elif value == "Pendiente":
                            item.setBackground(QColor(231,
76,
                                60,
                                50))   # Rojo claro
                    self.tabla_principal.setItem(row, col, item)

    def ver_detalle(self, row):
        """Muestra detalle del elemento seleccionado."""
        from PyQt6.QtWidgets import QMessageBox
        item = self.tabla_principal.item(row, 1)
        if item:
            QMessageBox.information(
                self,
                "Detalle de Mantenimiento",
                f"Mostrando detalles de: {item.text()}"
            )

    def aplicar_estilo(self):
        """Aplica el estilo general."""
        self.setStyleSheet("""
            QWidget {
            background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
            background-color: #6f42c1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
            opacity: 0.8;
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

    def nuevo_registro(self):
        """Abre el diálogo para crear un nuevo mantenimiento."""
        dialog = NuevoMantenimientoDialog(self)
        if dialog.exec() == dialog.Accepted:
            datos = dialog.obtener_datos()
            if self.controller:
                resultado = self.controller.crear_mantenimiento(datos)
                if resultado:  # Éxito (devuelve ID)
                    show_success(self, "Mantenimiento Creado", f"Mantenimiento creado con ID: {resultado}")
                    self.actualizar_datos()
                else:  # Error
                    show_error(self, "Error", "No se pudo crear el mantenimiento")

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
            btn_editar.clicked.connect(lambda checked, r=row: self.editar_registro(r))
            self.tabla_principal.setCellWidget(row, 4, btn_editar)

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

    def cargar_equipos(self, equipos):
        """Carga los equipos en el combo selector."""
        try:
            if hasattr(self, 'combo_equipo_preventivo'):
                self.combo_equipo_preventivo.clear()
                for equipo in equipos:
                    if isinstance(equipo, dict):
                        self.combo_equipo_preventivo.addItem(equipo.get('nombre', str(equipo)))
                    else:
                        self.combo_equipo_preventivo.addItem(str(equipo))

            # También actualizar tabla de equipos si está visible
            if hasattr(self, 'tabla_equipos') and equipos:
                self.tabla_equipos.setRowCount(len(equipos))
                for row, equipo in enumerate(equipos):
                    if isinstance(equipo, dict):
                        cols = ['codigo', 'nombre', 'tipo', 'marca', 'ubicacion', 'estado', 'ultimo_mantenimiento']
                        for col, field in enumerate(cols):
                            if col < self.tabla_equipos.columnCount():
                                value = equipo.get(field, '')
                                self.tabla_equipos.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            print(f"Error cargando equipos en vista: {e}")

    def crear_controles_paginacion(self):
        """Crea los controles de paginación para las tablas."""
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
        self.info_label = QLabel("Mostrando registros")
        self.info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Botones de navegación
        self.btn_primera = QPushButton("⟪")
        self.btn_anterior = QPushButton("‹")
        self.btn_siguiente = QPushButton("›")
        self.btn_ultima = QPushButton("⟫")

        for btn in [self.btn_primera, self.btn_anterior, self.btn_siguiente, self.btn_ultima]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #475569;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                    border-color: #3b82f6;
                }
                QPushButton:disabled {
                    background: #f8fafc;
                    color: #cbd5e1;
                    border-color: #e2e8f0;
                }
            """)

        layout.addWidget(self.btn_primera)
        layout.addWidget(self.btn_anterior)
        layout.addWidget(self.btn_siguiente)
        layout.addWidget(self.btn_ultima)

        return panel


class NuevoMantenimientoDialog(QDialog):
    """Diálogo para crear un nuevo mantenimiento."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Mantenimiento")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        from PyQt6.QtCore import QDate

        layout = QVBoxLayout(self)

        # Título
        titulo = RexusLabel("Crear Nuevo Mantenimiento", "title")
        layout.addWidget(titulo)

        # Formulario
        form_layout = QFormLayout()

        # Equipo ID (obligatorio)
        self.equipo_id_input = QSpinBox()
        self.equipo_id_input.setRange(1, 999999)
        self.equipo_id_input.setValue(1)
        form_layout.addRow("ID del Equipo*:", self.equipo_id_input)

        # Tipo de mantenimiento
        self.tipo_input = RexusComboBox()
        self.tipo_input.addItems([
            "PREVENTIVO",
            "CORRECTIVO",
            "PREDICTIVO",
            "EMERGENCIA",
            "INSPECCION"
        ])
        form_layout.addRow("Tipo*:", self.tipo_input)

        # Descripción (obligatorio)
        self.descripcion_input = RexusLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción del mantenimiento")
        self.descripcion_input.setMaxLength(500)
        form_layout.addRow("Descripción*:", self.descripcion_input)

        # Fecha programada
        self.fecha_programada_input = QDateEdit()
        self.fecha_programada_input.setDate(QDate.currentDate())
        self.fecha_programada_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Programada:", self.fecha_programada_input)

        # Estado
        self.estado_input = RexusComboBox()
        self.estado_input.addItems([
            "PROGRAMADO",
            "EN_PROGRESO",
            "COMPLETADO",
            "CANCELADO",
            "PENDIENTE"
        ])
        form_layout.addRow("Estado:", self.estado_input)

        # Costo estimado
        self.costo_estimado_input = QDoubleSpinBox()
        self.costo_estimado_input.setRange(0.0, 999999.99)
        self.costo_estimado_input.setPrefix("$ ")
        self.costo_estimado_input.setDecimals(2)
        form_layout.addRow("Costo Estimado:", self.costo_estimado_input)

        # Responsable
        self.responsable_input = RexusLineEdit()
        self.responsable_input.setPlaceholderText("Nombre del responsable")
        self.responsable_input.setMaxLength(100)
        form_layout.addRow("Responsable:", self.responsable_input)

        # Observaciones
        self.observaciones_input = RexusLineEdit()
        self.observaciones_input.setPlaceholderText("Observaciones adicionales")
        self.observaciones_input.setMaxLength(500)
        form_layout.addRow("Observaciones:", self.observaciones_input)

        layout.addLayout(form_layout)

        # Nota de campos obligatorios
        nota = RexusLabel("* Campos obligatorios", "caption")
        nota.setStyleSheet(f"color: {RexusColors.TEXT_SECONDARY}; font-style: italic;")
        layout.addWidget(nota)

        layout.addStretch()

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_cancelar = RexusButton("Cancelar", "secondary")
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_cancelar)

        botones_layout.addStretch()

        self.btn_crear = RexusButton("Crear Mantenimiento", "primary")
        self.btn_crear.clicked.connect(self.validar_y_aceptar)
        botones_layout.addWidget(self.btn_crear)

        layout.addLayout(botones_layout)

    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar."""
        # Validar campos obligatorios
        if self.equipo_id_input.value() <= 0:
            show_error(self, "Error", "Debe especificar un ID de equipo válido")
            self.equipo_id_input.setFocus()
            return

        if not self.descripcion_input.text().strip():
            show_error(self, "Error", "La descripción es obligatoria")
            self.descripcion_input.setFocus()
            return

        self.accept()

    def obtener_datos(self):
        """Retorna los datos del formulario."""
        return {
            "equipo_id": self.equipo_id_input.value(),
            "tipo": self.tipo_input.currentText(),
            "descripcion": self.descripcion_input.text().strip(),
            "fecha_programada": self.fecha_programada_input.date().toString("yyyy-MM-dd"),
            "estado": self.estado_input.currentText(),
            "costo_estimado": self.costo_estimado_input.value(),
            "responsable": self.responsable_input.text().strip() or "",
            "observaciones": self.observaciones_input.text().strip() or "",
        }

    # === MÉTODOS PARA BOTONES CORREGIDOS ===

    def ejecutar_accion_preventivo(self, row):
        """Ejecuta acción para mantenimiento preventivo."""
        show_success(self, "Acción Ejecutada", f"Procesando acción para fila {row + 1}")

    def ver_detalle_repuesto(self, row):
        """Ver detalle de repuesto."""
        show_success(self, "Ver Repuesto", f"Mostrando detalle del repuesto en fila {row + 1}")

    def ver_detalle_equipo(self, row):
        """Ver detalle de equipo."""
        show_success(self, "Ver Equipo", f"Mostrando detalle del equipo en fila {row + 1}")

    def ver_detalle(self, row):
        """Ver detalle general."""
        show_success(self, "Ver Detalle", f"Mostrando detalle para fila {row + 1}")

    # === MÉTODOS DE PAGINACIÓN ===
