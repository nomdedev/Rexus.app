"""
Pestaña de Estadísticas para el módulo de Logística

Maneja la visualización de estadísticas y métricas del sistema.
"""

from typing import Dict, Any
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QScrollArea

from .base_tab import BaseTab
from ..constants import ICONS
from ..widgets import LogisticaGroupBox, StatisticFrame
from ..styles import STATS_STYLE


class TabEstadisticas(BaseTab):
    """Pestaña para visualización de estadísticas."""
    
    # Señales específicas de estadísticas
    estadisticas_actualizadas = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        self.estadisticas_data = {}
        super().__init__("Estadísticas", ICONS["tabs"]["estadisticas"], parent)
    
    def init_ui(self):
        """Inicializa la interfaz de estadísticas."""
        # Aplicar estilos específicos
        self.setStyleSheet(self.styleSheet() + STATS_STYLE)
        
        # Área de scroll para las estadísticas
        scroll_area = QScrollArea(self)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Panel de resumen
        self.create_summary_panel(scroll_layout)
        
        # Panel de métricas detalladas
        self.create_detailed_metrics(scroll_layout)
        
        # Panel de gráficos (placeholder)
        self.create_charts_panel(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        self.main_layout.addWidget(scroll_area)
    
    def create_summary_panel(self, parent_layout):
        """Crea panel de resumen con métricas principales."""
        summary_group = LogisticaGroupBox("📊 Resumen General", self)
        
        # Layout horizontal para las tarjetas de estadísticas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Crear tarjetas de estadísticas
        self.stat_total_entregas = StatisticFrame("Total Entregas", "0", self)
        self.stat_entregas_pendientes = StatisticFrame("Pendientes", "0", self)  
        self.stat_entregas_completadas = StatisticFrame("Completadas", "0", self)
        self.stat_transportes_activos = StatisticFrame("Transportes", "0", self)
        
        cards_layout.addWidget(self.stat_total_entregas)
        cards_layout.addWidget(self.stat_entregas_pendientes)
        cards_layout.addWidget(self.stat_entregas_completadas)
        cards_layout.addWidget(self.stat_transportes_activos)
        cards_layout.addStretch()
        
        summary_group.add_layout(cards_layout)
        parent_layout.addWidget(summary_group)
    
    def create_detailed_metrics(self, parent_layout):
        """Crea panel de métricas detalladas."""
        details_group = LogisticaGroupBox("📈 Métricas Detalladas", self)
        
        # Layout para métricas con barras de progreso
        metrics_layout = QVBoxLayout()
        
        # Métricas de eficiencia (placeholder)
        efficiency_layout = QHBoxLayout()
        
        # Estadísticas de tiempo promedio
        self.stat_tiempo_promedio = StatisticFrame("Tiempo Promedio\\nEntrega", "2.5h", self)
        efficiency_layout.addWidget(self.stat_tiempo_promedio)
        
        # Estadísticas de costo promedio  
        self.stat_costo_promedio = StatisticFrame("Costo Promedio\\nEnvío", "$1,250", self)
        efficiency_layout.addWidget(self.stat_costo_promedio)
        
        # Estadísticas de satisfacción
        self.stat_satisfaccion = StatisticFrame("Satisfacción\\nCliente", "95%", self)
        efficiency_layout.addWidget(self.stat_satisfaccion)
        
        efficiency_layout.addStretch()
        
        metrics_layout.addLayout(efficiency_layout)
        details_group.add_layout(metrics_layout)
        parent_layout.addWidget(details_group)
    
    def create_charts_panel(self, parent_layout):
        """Crea panel con gráficos (placeholder)."""
        charts_group = LogisticaGroupBox("📊 Gráficos y Tendencias", self)
        
        # Placeholder para gráficos
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt
        
        placeholder_layout = QVBoxLayout()
        
        # Icono de gráfico
        chart_icon = QLabel("📊")
        chart_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_icon.setStyleSheet("font-size: 48px; margin: 20px;")
        placeholder_layout.addWidget(chart_icon)
        
        # Texto informativo
        chart_text = QLabel("Gráficos de tendencias\\n(En desarrollo)")
        chart_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_text.setStyleSheet("font-size: 14px; color: #6c757d; margin-bottom: 20px;")
        placeholder_layout.addWidget(chart_text)
        
        charts_group.add_layout(placeholder_layout)
        parent_layout.addWidget(charts_group)
    
    def actualizar_estadisticas(self, estadisticas: Dict[str, Any]):
        """Actualiza las estadísticas mostradas."""
        self.estadisticas_data = estadisticas
        
        # Actualizar tarjetas de resumen
        if hasattr(self, 'stat_total_entregas'):
            self.stat_total_entregas.update_value(str(estadisticas.get("total_entregas", 0)))
            self.stat_entregas_pendientes.update_value(str(estadisticas.get("entregas_pendientes", 0)))
            self.stat_entregas_completadas.update_value(str(estadisticas.get("entregas_completadas", 0)))
            self.stat_transportes_activos.update_value(str(estadisticas.get("transportes_activos", 0)))
        
        # Actualizar métricas detalladas si hay datos
        if "tiempo_promedio" in estadisticas:
            tiempo = estadisticas["tiempo_promedio"]
            self.stat_tiempo_promedio.update_value(f"{tiempo}h")
        
        if "costo_promedio" in estadisticas:
            costo = estadisticas["costo_promedio"]
            self.stat_costo_promedio.update_value(f"${costo:,.0f}")
        
        if "satisfaccion" in estadisticas:
            satisfaccion = estadisticas["satisfaccion"]
            self.stat_satisfaccion.update_value(f"{satisfaccion}%")
        
        # Emitir señal de actualización
        self.estadisticas_actualizadas.emit(estadisticas)
    
    def generar_estadisticas_demo(self):
        """Genera estadísticas de demostración."""
        import random
        
        demo_stats = {
            "total_entregas": random.randint(50, 200),
            "entregas_pendientes": random.randint(5, 25),
            "entregas_completadas": random.randint(40, 180),
            "transportes_activos": random.randint(8, 15),
            "tiempo_promedio": round(random.uniform(1.5, 4.0), 1),
            "costo_promedio": random.randint(800, 2000),
            "satisfaccion": random.randint(85, 98)
        }
        
        self.actualizar_estadisticas(demo_stats)
        self.show_success("Estadísticas actualizadas")
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna los datos actuales de estadísticas."""
        return self.estadisticas_data.copy()
    
    def refresh(self):
        """Refresca las estadísticas."""
        self.emit_action("cargar_estadisticas")
        
        # En modo demo, generar estadísticas aleatorias
        self.generar_estadisticas_demo()
    
    def clear(self):
        """Limpia las estadísticas."""
        empty_stats = {
            "total_entregas": 0,
            "entregas_pendientes": 0, 
            "entregas_completadas": 0,
            "transportes_activos": 0
        }
        self.actualizar_estadisticas(empty_stats)