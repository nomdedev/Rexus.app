# -*- coding: utf-8 -*-
"""
Widget de estadísticas para logística
Refactorizado de LogisticaView
"""

import logging
from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, 
    QProgressBar, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer

from .base_logistica_widget import BaseLogisticaWidget
from rexus.ui.components.base_components import RexusGroupBox

logger = logging.getLogger(__name__)


class EstadisticasWidget(BaseLogisticaWidget):
    """Widget para mostrar estadísticas de logística."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_data = {}
        self.update_timer = QTimer()
        self.setup_timer()
    
    def setup_timer(self):
        """Configurar timer para actualización automática."""
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
    
    def create_ui(self):
        """Crear interfaz de estadísticas."""
        layout = QVBoxLayout(self)
        
        # Crear scroll area para contenido
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Panel de métricas principales
        metricas_group = self.create_metricas_panel()
        scroll_layout.addWidget(metricas_group)
        
        # Panel de distribución por estado
        estados_group = self.create_estados_panel()
        scroll_layout.addWidget(estados_group)
        
        # Panel de rendimiento
        rendimiento_group = self.create_rendimiento_panel()
        scroll_layout.addWidget(rendimiento_group)
        
        # Panel de alertas
        alertas_group = self.create_alertas_panel()
        scroll_layout.addWidget(alertas_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
    
    def create_metricas_panel(self) -> RexusGroupBox:
        """Crear panel de métricas principales."""
        group = RexusGroupBox("Métricas Principales")
        layout = QGridLayout()
        
        # Métricas con valores por defecto
        metricas = [
            ("Transportes Activos", "transportes_activos", "15", "#4CAF50"),
            ("En Tránsito", "en_transito", "8", "#FF9800"),
            ("Programados", "programados", "12", "#2196F3"),
            ("Completados Hoy", "completados_hoy", "5", "#9C27B0")
        ]
        
        self.metric_labels = {}
        
        for i, (titulo, key, valor_default, color) in enumerate(metricas):
            # Crear frame para métrica
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
            
            # Título
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-weight: bold; color: #555;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Valor
            value_label = QLabel(valor_default)
            value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.metric_labels[key] = value_label
            
            metric_layout.addWidget(title_label)
            metric_layout.addWidget(value_label)
            
            # Posición en grid (2 columnas)
            row = i // 2
            col = i % 2
            layout.addWidget(frame, row, col)
        
        group.setLayout(layout)
        return group
    
    def create_estados_panel(self) -> RexusGroupBox:
        """Crear panel de distribución por estados."""
        group = RexusGroupBox("Distribución por Estados")
        layout = QVBoxLayout()
        
        # Estados con barras de progreso
        estados = [
            ("Programado", "programado", 45, "#2196F3"),
            ("En Tránsito", "en_transito", 30, "#FF9800"),
            ("En Destino", "en_destino", 15, "#4CAF50"),
            ("Retrasado", "retrasado", 10, "#F44336")
        ]
        
        self.progress_bars = {}
        
        for estado, key, porcentaje, color in estados:
            # Layout horizontal para cada estado
            estado_layout = QHBoxLayout()
            
            # Label del estado
            estado_label = QLabel(estado)
            estado_label.setMinimumWidth(100)
            estado_label.setStyleSheet("font-weight: bold;")
            
            # Barra de progreso
            progress = QProgressBar()
            progress.setValue(porcentaje)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    width: 20px;
                }}
            """)
            
            # Label de porcentaje
            percent_label = QLabel(f"{porcentaje}%")
            percent_label.setMinimumWidth(40)
            percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            percent_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            self.progress_bars[key] = (progress, percent_label)
            
            estado_layout.addWidget(estado_label)
            estado_layout.addWidget(progress, 1)
            estado_layout.addWidget(percent_label)
            
            layout.addLayout(estado_layout)
        
        group.setLayout(layout)
        return group
    
    def create_rendimiento_panel(self) -> RexusGroupBox:
        """Crear panel de rendimiento."""
        group = RexusGroupBox("Indicadores de Rendimiento")
        layout = QGridLayout()
        
        # Indicadores de rendimiento
        indicadores = [
            ("Tiempo Promedio Entrega", "2.5 horas", "#4CAF50"),
            ("Eficiencia de Rutas", "87%", "#2196F3"),
            ("Costos por Km", "$1.25", "#FF9800"),
            ("Satisfacción Cliente", "4.2/5", "#9C27B0")
        ]
        
        for i, (titulo, valor, color) in enumerate(indicadores):
            # Frame para indicador
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel)
            frame.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {color};
                    border-radius: 5px;
                    padding: 8px;
                }}
            """)
            
            ind_layout = QVBoxLayout(frame)
            
            title_label = QLabel(titulo)
            title_label.setStyleSheet("font-size: 12px; color: #666;")
            title_label.setWordWrap(True)
            
            value_label = QLabel(valor)
            value_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            ind_layout.addWidget(title_label)
            ind_layout.addWidget(value_label)
            
            row = i // 2
            col = i % 2
            layout.addWidget(frame, row, col)
        
        group.setLayout(layout)
        return group
    
    def create_alertas_panel(self) -> RexusGroupBox:
        """Crear panel de alertas y notificaciones."""
        group = RexusGroupBox("Alertas del Sistema")
        layout = QVBoxLayout()
        
        # Lista de alertas de ejemplo
        alertas = [
            ("Transporte T-005 con retraso de 2 horas", "warning"),
            ("Vehículo V-123 requiere mantenimiento", "info"),
            ("Ruta Norte con congestión reportada", "warning"),
            ("Sistema funcionando correctamente", "success")
        ]
        
        for alerta, tipo in alertas:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            
            # Colores según tipo
            colors = {
                "warning": "#FF9800",
                "info": "#2196F3", 
                "success": "#4CAF50",
                "error": "#F44336"
            }
            color = colors.get(tipo, "#666")
            
            frame.setStyleSheet(f"""
                QFrame {{
                    border-left: 4px solid {color};
                    background-color: rgba{(*self.hex_to_rgb(color), 0.1)};
                    padding: 8px;
                    margin: 2px;
                }}
            """)
            
            frame_layout = QHBoxLayout(frame)
            
            # Icono (simulado con texto)
            icons = {
                "warning": "⚠️",
                "info": "ℹ️",
                "success": "✅",
                "error": "❌"
            }
            icon_label = QLabel(icons.get(tipo, "•"))
            icon_label.setStyleSheet("font-size: 16px;")
            
            # Texto de alerta
            alert_label = QLabel(alerta)
            alert_label.setWordWrap(True)
            alert_label.setStyleSheet("color: #333;")
            
            frame_layout.addWidget(icon_label)
            frame_layout.addWidget(alert_label, 1)
            
            layout.addWidget(frame)
        
        group.setLayout(layout)
        return group
    
    def refresh_data(self):
        """Actualizar datos de estadísticas."""
        try:
            # Simular obtención de datos actualizados
            if hasattr(self.parent_view, 'controller'):
                # Obtener datos reales del controlador
                stats = self.parent_view.controller.get_estadisticas_logistica()
                self.update_statistics(stats)
            else:
                # Datos simulados para desarrollo
                self.update_with_sample_data()
                
        except Exception as e:
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Actualizar estadísticas con datos reales."""
        self.stats_data = stats
        
        # Actualizar métricas principales
        if hasattr(self, 'metric_labels'):
            for key, label in self.metric_labels.items():
                if key in stats:
                    label.setText(str(stats[key]))
        
        # Actualizar barras de progreso
        if hasattr(self, 'progress_bars'):
            for key, (progress, percent_label) in self.progress_bars.items():
                if key in stats:
                    value = int(stats[key])
                    progress.setValue(value)
                    percent_label.setText(f"{value}%")
        
        self.data_updated.emit()
    
    def update_with_sample_data(self):
        """Actualizar con datos de muestra."""
        import random
        
        # Generar datos aleatorios para simulación
        sample_stats = {
            'transportes_activos': random.randint(10, 20),
            'en_transito': random.randint(5, 15),
            'programados': random.randint(8, 18),
            'completados_hoy': random.randint(2, 10),
            'programado': random.randint(30, 60),
            'en_transito': random.randint(20, 40),
            'en_destino': random.randint(10, 25),
            'retrasado': random.randint(5, 15)
        }
        
        self.update_statistics(sample_stats)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convertir color hexadecimal a RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas actuales."""
        return self.stats_data.copy()
    
    def export_stats_report(self) -> bool:
        """Exportar reporte de estadísticas."""
        try:
            if not self.stats_data:
                self.error_occurred.emit("No hay estadísticas para exportar")
                return False
            
            # Preparar datos para exportación
            export_data = [
                {'Métrica': 'Transportes Activos', 'Valor': self.stats_data.get('transportes_activos', 0)},
                {'Métrica': 'En Tránsito', 'Valor': self.stats_data.get('en_transito', 0)},
                {'Métrica': 'Programados', 'Valor': self.stats_data.get('programados', 0)},
                {'Métrica': 'Completados Hoy', 'Valor': self.stats_data.get('completados_hoy', 0)},
            ]
            
            # Usar funcionalidad de exportación del parent
            if hasattr(self.parent_view, 'export_data'):
                return self.parent_view.export_data(export_data, 'excel')
            
            return True
            
        except Exception as e:
            return False