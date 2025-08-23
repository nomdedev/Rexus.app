"""
Dashboard Ejecutivo - Métricas Clave y Monitoreo en Tiempo Real
Proporciona una vista ejecutiva consolidada del sistema Rexus.app

Fecha: 23/08/2025
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame, QPushButton, QScrollArea, QProgressBar,
    QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen
# Importación condicional de QtChart (puede no estar disponible)
try:
    from PyQt6.QtChart import QChart, QChartView, QLineSeries, QPieSeries, QValueAxis
    QTCHART_AVAILABLE = True
except ImportError:
    QTCHART_AVAILABLE = False
    # Crear clases stub para evitar errores
    class QChart: pass
    class QChartView: 
        def __init__(self, parent=None): 
            super().__init__()
    class QLineSeries: pass
    class QPieSeries: pass
    class QValueAxis: pass

logger = logging.getLogger(__name__)

@dataclass
class KPIMetric:
    name: str
    current_value: float
    previous_value: float
    target_value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    status: str  # 'good', 'warning', 'critical'

class KPICard(QFrame):
    """Widget para mostrar una métrica KPI individual."""
    
    def __init__(self, metric: KPIMetric, parent=None):
        super().__init__(parent)
        self.metric = metric
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(200, 120)
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Título
        title_label = QLabel(self.metric.name)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valor principal
        value_label = QLabel(f"{self.metric.current_value:.1f} {self.metric.unit}")
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tendencia
        change = self.metric.current_value - self.metric.previous_value
        change_percent = (change / self.metric.previous_value * 100) if self.metric.previous_value > 0 else 0
        
        trend_text = f"{'↑' if change > 0 else '↓' if change < 0 else '→'} {abs(change_percent):.1f}%"
        trend_label = QLabel(trend_text)
        trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(trend_label)
        
        # Colores según estado
        self.update_colors()
        
    def update_colors(self):
        color_map = {
            'good': '#4CAF50',
            'warning': '#FF9800', 
            'critical': '#F44336'
        }
        
        color = color_map.get(self.metric.status, '#9E9E9E')
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }}
            QLabel {{
                border: none;
                background-color: transparent;
            }}
        """)

class PerformanceChart(QWidget):
    """Gráfico de rendimiento en tiempo real (fallback sin QtChart)."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.chart_title = title
        self.data_points = []
        self.setup_chart()
        
    def setup_chart(self):
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(self.chart_title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Área de gráfico simulado
        chart_area = QFrame()
        chart_area.setMinimumHeight(200)
        chart_area.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 4px;
            }
        """)
        
        chart_layout = QVBoxLayout(chart_area)
        
        # Etiquetas de datos
        self.current_value_label = QLabel("Valor actual: --")
        self.avg_value_label = QLabel("Promedio: --")
        self.max_value_label = QLabel("Máximo: --")
        
        chart_layout.addWidget(self.current_value_label)
        chart_layout.addWidget(self.avg_value_label)
        chart_layout.addWidget(self.max_value_label)
        chart_layout.addStretch()
        
        if not QTCHART_AVAILABLE:
            warning_label = QLabel("⚠ QtChart no disponible - Vista simplificada")
            warning_label.setStyleSheet("color: orange; font-size: 10px;")
            chart_layout.addWidget(warning_label)
        
        layout.addWidget(title_label)
        layout.addWidget(chart_area)
        
    def add_data_point(self, timestamp: float, value: float):
        """Añade un punto de datos al gráfico."""
        self.data_points.append((timestamp, value))
        
        # Mantener solo los últimos 60 puntos
        if len(self.data_points) > 60:
            self.data_points.pop(0)
            
        # Actualizar etiquetas
        if self.data_points:
            values = [point[1] for point in self.data_points]
            current = values[-1]
            avg = sum(values) / len(values)
            max_val = max(values)
            
            self.current_value_label.setText(f"Valor actual: {current:.1f}%")
            self.avg_value_label.setText(f"Promedio: {avg:.1f}%")
            self.max_value_label.setText(f"Máximo: {max_val:.1f}%")

class DataUpdateThread(QThread):
    """Hilo para actualizar datos del dashboard en tiempo real."""
    
    data_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        
    def run(self):
        self.running = True
        while self.running:
            try:
                # Obtener métricas del sistema
                data = self.collect_system_metrics()
                self.data_updated.emit(data)
                self.msleep(5000)  # Actualizar cada 5 segundos
                
            except Exception as e:
                logger.error(f"Error actualizando datos: {e}")
                self.msleep(10000)  # Esperar más tiempo si hay error
                
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Recolecta métricas del sistema."""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'active_connections': len(psutil.net_connections()),
                'timestamp': datetime.now().timestamp()
            }
        except ImportError:
            # Datos simulados si psutil no está disponible
            import random
            return {
                'cpu_percent': random.uniform(20, 80),
                'memory_percent': random.uniform(30, 90),
                'disk_usage': random.uniform(40, 85),
                'active_connections': random.randint(5, 25),
                'timestamp': datetime.now().timestamp()
            }
    
    def stop(self):
        self.running = False

class ExecutiveDashboard(QWidget):
    """Dashboard ejecutivo principal con métricas clave."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kpi_cards = {}
        self.performance_charts = {}
        self.data_thread = DataUpdateThread(self)
        self.start_time = datetime.now().timestamp()
        
        self.setup_ui()
        self.connect_signals()
        self.start_monitoring()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Dashboard Ejecutivo - Rexus.app")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Área con scroll
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Sección KPIs
        self.setup_kpi_section(scroll_layout)
        
        # Sección gráficos
        self.setup_charts_section(scroll_layout)
        
        # Sección tabla de actividad
        self.setup_activity_section(scroll_layout)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
    def setup_kpi_section(self, layout):
        kpi_group = QGroupBox("Métricas Clave del Sistema")
        kpi_layout = QHBoxLayout(kpi_group)
        
        # KPIs iniciales
        initial_kpis = [
            KPIMetric("CPU", 45.0, 40.0, 70.0, "%", "up", "good"),
            KPIMetric("Memoria", 65.0, 68.0, 85.0, "%", "down", "good"),
            KPIMetric("Disco", 58.0, 55.0, 90.0, "%", "up", "good"),
            KPIMetric("Usuarios", 12.0, 10.0, 50.0, "", "up", "good"),
            KPIMetric("Consultas/min", 34.0, 28.0, 100.0, "", "up", "good")
        ]
        
        for kpi in initial_kpis:
            card = KPICard(kpi)
            self.kpi_cards[kpi.name] = card
            kpi_layout.addWidget(card)
            
        kpi_layout.addStretch()
        layout.addWidget(kpi_group)
        
    def setup_charts_section(self, layout):
        charts_group = QGroupBox("Tendencias de Rendimiento")
        charts_layout = QHBoxLayout(charts_group)
        
        # Gráficos de rendimiento
        cpu_chart = PerformanceChart("CPU (%)")
        memory_chart = PerformanceChart("Memoria (%)")
        
        self.performance_charts['cpu'] = cpu_chart
        self.performance_charts['memory'] = memory_chart
        
        charts_layout.addWidget(cpu_chart)
        charts_layout.addWidget(memory_chart)
        
        layout.addWidget(charts_group)
        
    def setup_activity_section(self, layout):
        activity_group = QGroupBox("Actividad Reciente")
        activity_layout = QVBoxLayout(activity_group)
        
        # Tabla de actividad
        self.activity_table = QTableWidget(10, 4)
        self.activity_table.setHorizontalHeaderLabels([
            "Timestamp", "Módulo", "Acción", "Estado"
        ])
        self.activity_table.setMaximumHeight(250)
        
        activity_layout.addWidget(self.activity_table)
        layout.addWidget(activity_group)
        
    def connect_signals(self):
        self.data_thread.data_updated.connect(self.update_dashboard_data)
        
    def start_monitoring(self):
        self.data_thread.start()
        
    @pyqtSlot(dict)
    def update_dashboard_data(self, data: Dict[str, Any]):
        """Actualiza los datos del dashboard."""
        try:
            timestamp = data.get('timestamp', datetime.now().timestamp())
            elapsed_time = timestamp - self.start_time
            
            # Actualizar gráficos
            if 'cpu_percent' in data:
                self.performance_charts['cpu'].add_data_point(
                    elapsed_time, data['cpu_percent']
                )
                
            if 'memory_percent' in data:
                self.performance_charts['memory'].add_data_point(
                    elapsed_time, data['memory_percent']
                )
                
            # Actualizar KPIs
            self.update_kpi_cards(data)
            
            # Actualizar tabla de actividad
            self.update_activity_table(data)
            
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}")
            
    def update_kpi_cards(self, data: Dict[str, Any]):
        """Actualiza las tarjetas KPI."""
        updates = {
            'CPU': data.get('cpu_percent'),
            'Memoria': data.get('memory_percent'),
            'Disco': data.get('disk_usage'),
            'Usuarios': data.get('active_connections')
        }
        
        for kpi_name, new_value in updates.items():
            if kpi_name in self.kpi_cards and new_value is not None:
                card = self.kpi_cards[kpi_name]
                old_value = card.metric.current_value
                
                # Actualizar métrica
                card.metric.previous_value = old_value
                card.metric.current_value = new_value
                
                # Determinar estado
                if kpi_name in ['CPU', 'Memoria', 'Disco']:
                    if new_value > 90:
                        card.metric.status = 'critical'
                    elif new_value > 75:
                        card.metric.status = 'warning'
                    else:
                        card.metric.status = 'good'
                else:
                    card.metric.status = 'good'
                    
                # Actualizar UI
                card.setup_ui()
                
    def update_activity_table(self, data: Dict[str, Any]):
        """Actualiza la tabla de actividad."""
        timestamp = datetime.fromtimestamp(data.get('timestamp', datetime.now().timestamp()))
        
        # Insertar nueva fila al inicio
        self.activity_table.insertRow(0)
        self.activity_table.setItem(0, 0, QTableWidgetItem(timestamp.strftime("%H:%M:%S")))
        self.activity_table.setItem(0, 1, QTableWidgetItem("Sistema"))
        self.activity_table.setItem(0, 2, QTableWidgetItem("Monitoreo"))
        
        # Estado basado en CPU
        cpu_percent = data.get('cpu_percent', 0)
        status = "Normal" if cpu_percent < 80 else "Alto uso"
        self.activity_table.setItem(0, 3, QTableWidgetItem(status))
        
        # Mantener solo las últimas 10 filas
        while self.activity_table.rowCount() > 10:
            self.activity_table.removeRow(10)
            
    def closeEvent(self, event):
        """Limpia recursos al cerrar."""
        self.data_thread.stop()
        self.data_thread.wait()
        event.accept()

class DashboardManager:
    """Gestor del dashboard ejecutivo."""
    
    def __init__(self):
        self.dashboard = None
        
    def create_dashboard(self, parent=None) -> ExecutiveDashboard:
        """Crea una nueva instancia del dashboard."""
        if self.dashboard is None:
            self.dashboard = ExecutiveDashboard(parent)
        return self.dashboard
        
    def get_dashboard(self) -> Optional[ExecutiveDashboard]:
        """Obtiene la instancia actual del dashboard."""
        return self.dashboard
        
    def close_dashboard(self):
        """Cierra el dashboard actual."""
        if self.dashboard:
            self.dashboard.close()
            self.dashboard = None

# Instancia global del gestor
dashboard_manager = DashboardManager()

def get_dashboard_manager() -> DashboardManager:
    """Obtiene el gestor global del dashboard."""
    return dashboard_manager

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dashboard = ExecutiveDashboard()
    dashboard.setWindowTitle("Dashboard Ejecutivo - Rexus.app")
    dashboard.resize(1200, 800)
    dashboard.show()
    
    sys.exit(app.exec())