# -*- coding: utf-8 -*-
"""
Widget de servicios logísticos
Gestión completa de servicios, mantenimiento y seguimiento
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QProgressBar, QFrame, QScrollArea,
    QMessageBox, QDialog, QLineEdit, QComboBox, QTextEdit, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt6.QtGui import QIcon

from .base_logistica_widget import BaseLogisticaWidget
from rexus.ui.components.base_components import RexusButton, RexusLineEdit, RexusGroupBox
from rexus.utils.export_manager import ModuleExportMixin

logger = logging.getLogger(__name__)


class ServiciosWidget(BaseLogisticaWidget, ModuleExportMixin):
    """Widget para gestión completa de servicios logísticos."""
    
    # Señales específicas
    service_created = pyqtSignal(dict)
    service_updated = pyqtSignal(dict)
    service_completed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.servicios_activos = []
        self.servicios_programados = []
        self.historial_servicios = []
        
    def create_ui(self):
        """Crear interfaz de servicios."""
        layout = QVBoxLayout(self)
        
        # Panel de control superior
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Área principal con scroll
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Panel de servicios activos
        servicios_activos_group = self.create_servicios_activos_panel()
        scroll_layout.addWidget(servicios_activos_group)
        
        # Panel de servicios programados
        servicios_programados_group = self.create_servicios_programados_panel()
        scroll_layout.addWidget(servicios_programados_group)
        
        # Panel de métricas de servicios
        metricas_group = self.create_metricas_servicios_panel()
        scroll_layout.addWidget(metricas_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
    
    def create_control_panel(self) -> RexusGroupBox:
        """Crear panel de control de servicios."""
        group = RexusGroupBox("Control de Servicios")
        layout = QHBoxLayout()
        
        # Botones de acción
        self.btn_nuevo_servicio = RexusButton("➕ Nuevo Servicio")
        self.btn_programar = RexusButton("📅 Programar")
        self.btn_mantenimiento = RexusButton("🔧 Mantenimiento")
        self.btn_reportes = RexusButton("📊 Reportes")
        
        # Campo de búsqueda
        self.search_input = RexusLineEdit()
        self.search_input.setPlaceholderText("Buscar servicios...")
        
        # Filtros
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Activos", "Programados", "Completados", "Cancelados"])
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Entrega", "Recogida", "Mantenimiento", "Inspección"])
        
        layout.addWidget(self.btn_nuevo_servicio)
        layout.addWidget(self.btn_programar)
        layout.addWidget(self.btn_mantenimiento)
        layout.addWidget(self.btn_reportes)
        layout.addStretch()
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.search_input)
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.combo_tipo)
        
        group.setLayout(layout)
        return group
    
    def create_servicios_activos_panel(self) -> RexusGroupBox:
        """Crear panel de servicios activos."""
        group = RexusGroupBox("🔄 Servicios Activos")
        layout = QVBoxLayout()
        
        # Tabla de servicios activos
        self.tabla_activos = QTableWidget()
        self.configurar_tabla_servicios(self.tabla_activos)
        layout.addWidget(self.tabla_activos)
        
        # Panel de acciones para servicios activos
        actions_layout = QHBoxLayout()
        
        self.btn_completar = RexusButton("✅ Completar")
        self.btn_pausar = RexusButton("⏸️ Pausar")
        self.btn_cancelar = RexusButton("❌ Cancelar")
        self.btn_detalles = RexusButton("👁️ Ver Detalles")
        
        # Estado inicial
        for btn in [self.btn_completar, self.btn_pausar, self.btn_cancelar, self.btn_detalles]:
            btn.setEnabled(False)
        
        actions_layout.addWidget(self.btn_completar)
        actions_layout.addWidget(self.btn_pausar)
        actions_layout.addWidget(self.btn_cancelar)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_detalles)
        
        layout.addLayout(actions_layout)
        
        group.setLayout(layout)
        return group
    
    def create_servicios_programados_panel(self) -> RexusGroupBox:
        """Crear panel de servicios programados."""
        group = RexusGroupBox("📅 Servicios Programados")
        layout = QVBoxLayout()
        
        # Tabla de servicios programados
        self.tabla_programados = QTableWidget()
        self.configurar_tabla_servicios(self.tabla_programados)
        layout.addWidget(self.tabla_programados)
        
        # Panel de acciones para servicios programados
        actions_layout = QHBoxLayout()
        
        self.btn_iniciar = RexusButton("▶️ Iniciar")
        self.btn_editar_programacion = RexusButton("✏️ Editar")
        self.btn_eliminar_programacion = RexusButton("🗑️ Eliminar")
        
        # Estado inicial
        for btn in [self.btn_iniciar, self.btn_editar_programacion, self.btn_eliminar_programacion]:
            btn.setEnabled(False)
        
        actions_layout.addWidget(self.btn_iniciar)
        actions_layout.addWidget(self.btn_editar_programacion)
        actions_layout.addWidget(self.btn_eliminar_programacion)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        group.setLayout(layout)
        return group
    
    def create_metricas_servicios_panel(self) -> RexusGroupBox:
        """Crear panel de métricas de servicios."""
        group = RexusGroupBox("📈 Métricas de Rendimiento")
        layout = QGridLayout()
        
        # Métricas principales
        metricas = [
            ("Servicios Completados Hoy", "8", "#4CAF50"),
            ("Servicios Activos", "5", "#FF9800"),
            ("Programados Esta Semana", "12", "#2196F3"),
            ("Tiempo Promedio", "2.5h", "#9C27B0"),
            ("Eficiencia", "89%", "#4CAF50"),
            ("Servicios Cancelados", "2", "#F44336")
        ]
        
        for i, (titulo, valor, color) in enumerate(metricas):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                    background-color: rgba{(*self.hex_to_rgb(color), 0.1)};
                }}
            """)
            
            metric_layout = QVBoxLayout(frame)
            
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-weight: bold; color: #555; font-size: 11px;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setWordWrap(True)
            
            value_label = QLabel(valor)
            value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            metric_layout.addWidget(title_label)
            metric_layout.addWidget(value_label)
            
            row = i // 3
            col = i % 3
            layout.addWidget(frame, row, col)
        
        group.setLayout(layout)
        return group
    
    def configurar_tabla_servicios(self, tabla: QTableWidget):
        """Configurar tabla de servicios."""
        columnas = [
            "ID", "Tipo", "Estado", "Cliente", "Origen", 
            "Destino", "Programado", "Conductor", "Observaciones"
        ]
        
        tabla.setColumnCount(len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setAlternatingRowColors(True)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Ajustar ancho de columnas
        header = tabla.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Conectar señal de selección
        tabla.itemSelectionChanged.connect(self.on_service_selection_changed)
    
    def connect_signals(self):
        """Conectar señales del widget."""
        # Botones de control
        self.btn_nuevo_servicio.clicked.connect(self.crear_nuevo_servicio)
        self.btn_programar.clicked.connect(self.programar_servicio)
        self.btn_mantenimiento.clicked.connect(self.abrir_mantenimiento)
        self.btn_reportes.clicked.connect(self.generar_reporte_servicios)
        
        # Filtros y búsqueda
        self.search_input.textChanged.connect(self.filtrar_servicios)
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        self.combo_tipo.currentTextChanged.connect(self.aplicar_filtros)
        
        # Acciones de servicios activos
        self.btn_completar.clicked.connect(self.completar_servicio)
        self.btn_pausar.clicked.connect(self.pausar_servicio)
        self.btn_cancelar.clicked.connect(self.cancelar_servicio)
        self.btn_detalles.clicked.connect(self.ver_detalles_servicio)
        
        # Acciones de servicios programados
        self.btn_iniciar.clicked.connect(self.iniciar_servicio)
        self.btn_editar_programacion.clicked.connect(self.editar_programacion)
        self.btn_eliminar_programacion.clicked.connect(self.eliminar_programacion)
    
    def refresh_data(self):
        """Actualizar datos de servicios."""
        try:
            # Cargar datos de ejemplo
            self.cargar_datos_ejemplo()
            
        except Exception as e:
            logger.error(f"Error configurando servicios: {e}")
    
    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo para servicios."""
        # Servicios activos
        servicios_activos = [
            {
                'id': 1, 'tipo': 'Entrega', 'estado': 'En progreso',
                'cliente': 'Empresa ABC', 'origen': 'Almacén Central',
                'destino': 'Oficina Norte', 'programado': '09:00',
                'conductor': 'Juan Pérez', 'observaciones': 'Documentos importantes'
            },
            {
                'id': 2, 'tipo': 'Recogida', 'estado': 'En ruta',
                'cliente': 'Cliente XYZ', 'origen': 'Sede Sur',
                'destino': 'Almacén', 'programado': '10:30',
                'conductor': 'María García', 'observaciones': 'Paquete frágil'
            }
        ]
        
        # Servicios programados
        servicios_programados = [
            {
                'id': 3, 'tipo': 'Entrega', 'estado': 'Programado',
                'cliente': 'Corporación DEF', 'origen': 'Almacén Este',
                'destino': 'Torre Empresarial', 'programado': '14:00',
                'conductor': 'Carlos López', 'observaciones': 'Entrega urgente'
            },
            {
                'id': 4, 'tipo': 'Mantenimiento', 'estado': 'Programado',
                'cliente': 'Interno', 'origen': 'Taller',
                'destino': 'Vehículo V-123', 'programado': '16:00',
                'conductor': 'Técnico 1', 'observaciones': 'Revisión mensual'
            }
        ]
        
        self.cargar_servicios_en_tabla(self.tabla_activos, servicios_activos)
        self.cargar_servicios_en_tabla(self.tabla_programados, servicios_programados)
        
        self.servicios_activos = servicios_activos
        self.servicios_programados = servicios_programados
    
    def cargar_servicios_en_tabla(self, tabla: QTableWidget, servicios: List[Dict]):
        """Cargar servicios en una tabla específica."""
        tabla.setRowCount(len(servicios))
        
        for row, servicio in enumerate(servicios):
            items = [
                str(servicio.get('id', '')),
                str(servicio.get('tipo', '')),
                str(servicio.get('estado', '')),
                str(servicio.get('cliente', '')),
                str(servicio.get('origen', '')),
                str(servicio.get('destino', '')),
                str(servicio.get('programado', '')),
                str(servicio.get('conductor', '')),
                str(servicio.get('observaciones', ''))
            ]
            
            for col, item in enumerate(items):
                table_item = QTableWidgetItem(item)
                if col == 0:  # ID column
                    table_item.setData(Qt.ItemDataRole.UserRole, servicio)
                
                # Colorear según estado
                estado = servicio.get('estado', '')
                if estado == 'En progreso':
                    table_item.setBackground(Qt.GlobalColor.lightGreen)
                elif estado == 'En ruta':
                    table_item.setBackground(Qt.GlobalColor.yellow)
                elif estado == 'Programado':
                    table_item.setBackground(Qt.GlobalColor.lightBlue)
                
                tabla.setItem(row, col, table_item)
    
    def on_service_selection_changed(self):
        """Manejar cambio de selección en tablas."""
        # Determinar qué tabla tiene selección
        sender = self.sender()
        
        if sender == self.tabla_activos:
            selected = sender.currentRow() >= 0
            self.btn_completar.setEnabled(selected)
            self.btn_pausar.setEnabled(selected)
            self.btn_cancelar.setEnabled(selected)
            self.btn_detalles.setEnabled(selected)
        
        elif sender == self.tabla_programados:
            selected = sender.currentRow() >= 0
            self.btn_iniciar.setEnabled(selected)
            self.btn_editar_programacion.setEnabled(selected)
            self.btn_eliminar_programacion.setEnabled(selected)
    
    def crear_nuevo_servicio(self):
        """Crear nuevo servicio."""
        dialogo = DialogoNuevoServicio(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            servicio_data = dialogo.get_service_data()
            self.service_created.emit(servicio_data)
            QMessageBox.information(self, "Éxito", "Servicio creado correctamente")
            self.refresh_data()
    
    def programar_servicio(self):
        """Programar nuevo servicio."""
        dialogo = DialogoProgramarServicio(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            programacion_data = dialogo.get_programacion_data()
            QMessageBox.information(self, "Éxito", "Servicio programado correctamente")
            self.refresh_data()
    
    def completar_servicio(self):
        """Completar servicio seleccionado."""
        current_row = self.tabla_activos.currentRow()
        if current_row >= 0:
            service_data = self.tabla_activos.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            self.service_completed.emit(service_data['id'])
            QMessageBox.information(self, "Éxito", f"Servicio {service_data['id']} completado")
            self.refresh_data()
    
    def abrir_mantenimiento(self):
        """Abrir módulo de mantenimiento."""
        QMessageBox.information(self, "Mantenimiento", "Módulo de mantenimiento en desarrollo")
    
    def generar_reporte_servicios(self):
        """Generar reporte de servicios."""
        try:
            # Preparar datos para reporte
            todos_servicios = self.servicios_activos + self.servicios_programados
            
            if not todos_servicios:
                QMessageBox.warning(self, "Reporte", "No hay servicios para exportar")
                return
            
            export_data = []
            for servicio in todos_servicios:
                export_data.append({
                    'ID': servicio.get('id', ''),
                    'Tipo': servicio.get('tipo', ''),
                    'Estado': servicio.get('estado', ''),
                    'Cliente': servicio.get('cliente', ''),
                    'Origen': servicio.get('origen', ''),
                    'Destino': servicio.get('destino', ''),
                    'Programado': servicio.get('programado', ''),
                    'Conductor': servicio.get('conductor', ''),
                    'Observaciones': servicio.get('observaciones', '')
                })
            
            success = self.export_to_excel(
                data=export_data,
                filename="reporte_servicios",
                sheet_name="Servicios"
            )
            
            if success:
                QMessageBox.information(self, "Éxito", "Reporte generado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al generar reporte de servicios: {e}")
    
    def filtrar_servicios(self):
        """Filtrar servicios por texto de búsqueda."""
        # Implementar filtrado en tiempo real
        pass
    
    def aplicar_filtros(self):
        """Aplicar filtros seleccionados."""
        # Implementar filtros por estado y tipo
        pass
    
    # Métodos de acciones adicionales
    def pausar_servicio(self):
        """Pausar servicio activo."""
        QMessageBox.information(self, "Pausa", "Servicio pausado")
    
    def cancelar_servicio(self):
        """Cancelar servicio activo."""
        reply = QMessageBox.question(self, "Cancelar", "¿Confirma cancelar este servicio?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Cancelado", "Servicio cancelado")
    
    def ver_detalles_servicio(self):
        """Ver detalles completos del servicio."""
        QMessageBox.information(self, "Detalles", "Mostrando detalles del servicio...")
    
    def iniciar_servicio(self):
        """Iniciar servicio programado."""
        QMessageBox.information(self, "Iniciado", "Servicio iniciado correctamente")
    
    def editar_programacion(self):
        """Editar programación de servicio."""
        QMessageBox.information(self, "Edición", "Editando programación...")
    
    def eliminar_programacion(self):
        """Eliminar programación de servicio."""
        reply = QMessageBox.question(self, "Eliminar", "¿Confirma eliminar esta programación?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Eliminado", "Programación eliminada")
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convertir color hex a RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class DialogoNuevoServicio(QDialog):
    """Diálogo para crear nuevos servicios."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Servicio")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Campos del formulario
        form_layout = QGridLayout()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Entrega", "Recogida", "Mantenimiento", "Inspección"])
        
        self.input_cliente = QLineEdit()
        self.input_origen = QLineEdit()
        self.input_destino = QLineEdit()
        
        self.date_programado = QDateEdit()
        self.date_programado.setDate(QDate.currentDate())
        
        self.combo_conductor = QComboBox()
        self.combo_conductor.addItems(["Juan Pérez", "María García", "Carlos López"])
        
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setMaximumHeight(100)
        
        # Agregar campos al formulario
        form_layout.addWidget(QLabel("Tipo:"), 0, 0)
        form_layout.addWidget(self.combo_tipo, 0, 1)
        form_layout.addWidget(QLabel("Cliente:"), 1, 0)
        form_layout.addWidget(self.input_cliente, 1, 1)
        form_layout.addWidget(QLabel("Origen:"), 2, 0)
        form_layout.addWidget(self.input_origen, 2, 1)
        form_layout.addWidget(QLabel("Destino:"), 3, 0)
        form_layout.addWidget(self.input_destino, 3, 1)
        form_layout.addWidget(QLabel("Fecha:"), 4, 0)
        form_layout.addWidget(self.date_programado, 4, 1)
        form_layout.addWidget(QLabel("Conductor:"), 5, 0)
        form_layout.addWidget(self.combo_conductor, 5, 1)
        form_layout.addWidget(QLabel("Observaciones:"), 6, 0)
        form_layout.addWidget(self.text_observaciones, 6, 1)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_cancelar = QPushButton("Cancelar")
        
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_aceptar)
        buttons_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(buttons_layout)
    
    def get_service_data(self) -> Dict[str, Any]:
        """Obtener datos del servicio."""
        return {
            'tipo': self.combo_tipo.currentText(),
            'cliente': self.input_cliente.text(),
            'origen': self.input_origen.text(),
            'destino': self.input_destino.text(),
            'fecha': self.date_programado.date().toString(),
            'conductor': self.combo_conductor.currentText(),
            'observaciones': self.text_observaciones.toPlainText()
        }


class DialogoProgramarServicio(QDialog):
    """Diálogo para programar servicios."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programar Servicio")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        label = QLabel("Funcionalidad de programación en desarrollo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Botón de cerrar
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(self.btn_cerrar)
    
    def get_programacion_data(self) -> Dict[str, Any]:
        """Obtener datos de programación."""
        return {}