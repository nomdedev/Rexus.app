"""
Dashboard en Tiempo Real para Rexus.app
Sistema de métricas visuales en tiempo real para monitoreo del sistema
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QTextEdit, QTabWidget, QTableWidget, 
                            QTableWidgetItem, QPushButton, QGroupBox)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QColor

from rexus.utils.app_logger import get_logger
from rexus.utils.monitoring_system import get_metrics_collector, get_performance_analyzer
from rexus.utils.performance_monitor import get_performance_monitor

logger = get_logger(__name__)

class MetricUpdateSignal(QObject):
    """Señales para actualizar métricas en tiempo real"""
    metrics_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    performance_alert = pyqtSignal(str, str)  # tipo, mensaje

class RealtimeDashboard(QWidget):
    """Dashboard principal de métricas en tiempo real"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = get_metrics_collector()
        self.performance_analyzer = get_performance_analyzer()
        self.performance_monitor = get_performance_monitor()
        
        # Configurar señales
        self.signal_emitter = MetricUpdateSignal()
        self.signal_emitter.metrics_updated.connect(self._update_dashboard)
        self.signal_emitter.error_occurred.connect(self._handle_error)
        self.signal_emitter.performance_alert.connect(self._handle_alert)
        
        # Timer para actualización
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._fetch_metrics)
        
        self.is_monitoring = False
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del dashboard"""
        self.setWindowTitle("Rexus.app - Dashboard de Métricas en Tiempo Real")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Panel de control
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)
        
        # Tabs principales
        tab_widget = QTabWidget()
        
        # Tab de métricas del sistema
        system_tab = self._create_system_metrics_tab()
        tab_widget.addTab(system_tab, "Sistema")
        
        # Tab de rendimiento de módulos
        modules_tab = self._create_modules_tab()
        tab_widget.addTab(modules_tab, "Módulos")
        
        # Tab de consultas SQL
        sql_tab = self._create_sql_performance_tab()
        tab_widget.addTab(sql_tab, "SQL")
        
        # Tab de alertas
        alerts_tab = self._create_alerts_tab()
        tab_widget.addTab(alerts_tab, "Alertas")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
    def _create_control_panel(self) -> QWidget:
        """Crea panel de control del dashboard"""
        panel = QGroupBox("Control de Monitoreo")
        layout = QHBoxLayout()
        
        # Botón start/stop
        self.start_stop_btn = QPushButton("Iniciar Monitoreo")
        self.start_stop_btn.clicked.connect(self._toggle_monitoring)
        layout.addWidget(self.start_stop_btn)
        
        # Estado del sistema
        self.system_status_label = QLabel("Estado: Detenido")
        self.system_status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.system_status_label)
        
        # Última actualización
        self.last_update_label = QLabel("Última actualización: --")
        layout.addWidget(self.last_update_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def _create_system_metrics_tab(self) -> QWidget:
        """Crea tab de métricas del sistema"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Métricas principales
        metrics_layout = QHBoxLayout()
        
        # CPU
        cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout()
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_label)
        cpu_group.setLayout(cpu_layout)
        metrics_layout.addWidget(cpu_group)
        
        # Memoria
        memory_group = QGroupBox("Memoria")
        memory_layout = QVBoxLayout()
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_label = QLabel("0%")
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_label)
        memory_group.setLayout(memory_layout)
        metrics_layout.addWidget(memory_group)
        
        # Disco
        disk_group = QGroupBox("Disco")
        disk_layout = QVBoxLayout()
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        self.disk_label = QLabel("0%")
        disk_layout.addWidget(self.disk_progress)
        disk_layout.addWidget(self.disk_label)
        disk_group.setLayout(disk_layout)
        metrics_layout.addWidget(disk_group)
        
        layout.addLayout(metrics_layout)
        
        # Información adicional
        info_group = QGroupBox("Información del Sistema")
        info_layout = QVBoxLayout()
        
        self.connections_label = QLabel("Conexiones activas: 0")
        self.sessions_label = QLabel("Sesiones de usuario: 0")
        self.queries_label = QLabel("Consultas ejecutadas: 0")
        self.errors_label = QLabel("Errores: 0")
        
        info_layout.addWidget(self.connections_label)
        info_layout.addWidget(self.sessions_label)
        info_layout.addWidget(self.queries_label)
        info_layout.addWidget(self.errors_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_modules_tab(self) -> QWidget:
        """Crea tab de rendimiento de módulos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabla de módulos
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(6)
        self.modules_table.setHorizontalHeaderLabels([
            "Módulo", "Tiempo Carga (s)", "Consultas", "Errores", "Vistas Activas", "Última Actividad"
        ])
        
        layout.addWidget(self.modules_table)
        widget.setLayout(layout)
        return widget
        
    def _create_sql_performance_tab(self) -> QWidget:
        """Crea tab de rendimiento SQL"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Métricas SQL
        sql_metrics_layout = QHBoxLayout()
        
        # Tiempo promedio
        avg_time_group = QGroupBox("Tiempo Promedio de Respuesta")
        avg_time_layout = QVBoxLayout()
        self.avg_response_label = QLabel("0.000s")
        self.avg_response_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        avg_time_layout.addWidget(self.avg_response_label)
        avg_time_group.setLayout(avg_time_layout)
        sql_metrics_layout.addWidget(avg_time_group)
        
        # Consultas por minuto
        qpm_group = QGroupBox("Consultas por Minuto")
        qpm_layout = QVBoxLayout()
        self.qpm_label = QLabel("0")
        self.qpm_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        qpm_layout.addWidget(self.qpm_label)
        qpm_group.setLayout(qpm_layout)
        sql_metrics_layout.addWidget(qpm_group)
        
        layout.addLayout(sql_metrics_layout)
        
        # Tabla de consultas lentas
        slow_queries_group = QGroupBox("Consultas Más Lentas")
        slow_queries_layout = QVBoxLayout()
        
        self.slow_queries_table = QTableWidget()
        self.slow_queries_table.setColumnCount(3)
        self.slow_queries_table.setHorizontalHeaderLabels([
            "Consulta", "Tiempo (s)", "Frecuencia"
        ])
        
        slow_queries_layout.addWidget(self.slow_queries_table)
        slow_queries_group.setLayout(slow_queries_layout)
        layout.addWidget(slow_queries_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_alerts_tab(self) -> QWidget:
        """Crea tab de alertas y logs"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Log de alertas
        alerts_group = QGroupBox("Alertas Recientes")
        alerts_layout = QVBoxLayout()
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setMaximumHeight(200)
        
        alerts_layout.addWidget(self.alerts_text)
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)
        
        # Recomendaciones
        recommendations_group = QGroupBox("Recomendaciones de Optimización")
        recommendations_layout = QVBoxLayout()
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        
        recommendations_layout.addWidget(self.recommendations_text)
        recommendations_group.setLayout(recommendations_layout)
        layout.addWidget(recommendations_group)
        
        widget.setLayout(layout)
        return widget
        
    def _toggle_monitoring(self):
        """Inicia o detiene el monitoreo"""
        if not self.is_monitoring:
            self._start_monitoring()
        else:
            self._stop_monitoring()
            
    def _start_monitoring(self):
        """Inicia el monitoreo en tiempo real"""
        try:
            # Iniciar recolector de métricas
            self.metrics_collector.start_monitoring(interval=5)
            
            # Iniciar timer de actualización UI
            self.update_timer.start(2000)  # Actualizar cada 2 segundos
            
            self.is_monitoring = True
            self.start_stop_btn.setText("Detener Monitoreo")
            self.system_status_label.setText("Estado: Activo")
            self.system_status_label.setStyleSheet("color: green; font-weight: bold;")
            
            self.logger.info("Dashboard de monitoreo iniciado")
            
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
            self.signal_emitter.error_occurred.emit(f"Error iniciando monitoreo: {e}")
            
    def _stop_monitoring(self):
        """Detiene el monitoreo"""
        self.update_timer.stop()
        self.metrics_collector.stop_monitoring()
        
        self.is_monitoring = False
        self.start_stop_btn.setText("Iniciar Monitoreo")
        self.system_status_label.setText("Estado: Detenido")
        self.system_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.logger.info("Dashboard de monitoreo detenido")
        
    def _fetch_metrics(self):
        """Obtiene métricas actuales y emite señal"""
        try:
            # Obtener métricas del sistema
            system_metrics = self.metrics_collector.get_performance_summary()
            
            # Obtener métricas de módulos
            module_metrics = self.metrics_collector.get_module_metrics()
            
            # Obtener análisis de rendimiento
            performance_analysis = self.performance_analyzer.analyze_performance_trends()
            
            # Combinar todas las métricas
            all_metrics = {
                'system': system_metrics,
                'modules': module_metrics,
                'performance': performance_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            self.signal_emitter.metrics_updated.emit(all_metrics)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            self.signal_emitter.error_occurred.emit(f"Error obteniendo métricas: {e}")
            
    def _update_dashboard(self, metrics: Dict[str, Any]):
        """Actualiza el dashboard con nuevas métricas"""
        try:
            system_metrics = metrics.get('system', {})
            
            # Actualizar métricas del sistema
            if system_metrics:
                cpu = system_metrics.get('cpu_promedio', 0)
                memory = system_metrics.get('memoria_promedio', 0)
                
                self.cpu_progress.setValue(int(cpu))
                self.cpu_label.setText(f"{cpu:.1f}%")
                
                self.memory_progress.setValue(int(memory))
                self.memory_label.setText(f"{memory:.1f}%")
                
                # Simular disco (no disponible en métricas actuales)
                self.disk_progress.setValue(50)
                self.disk_label.setText("50%")
                
                # Información adicional
                self.connections_label.setText(f"Conexiones activas: {system_metrics.get('conexiones_activas', 0)}")
                self.sessions_label.setText(f"Sesiones de usuario: {system_metrics.get('sesiones_activas', 0)}")
                self.queries_label.setText(f"Consultas ejecutadas: {system_metrics.get('total_consultas', 0)}")
                self.errors_label.setText(f"Errores: {system_metrics.get('total_errores', 0)}")
                
                # Métricas SQL
                response_time = system_metrics.get('tiempo_respuesta_promedio', 0)
                self.avg_response_label.setText(f"{response_time:.3f}s")
                
                # Color coding para tiempo de respuesta
                if response_time > 2.0:
                    self.avg_response_label.setStyleSheet("color: red;")
                elif response_time > 1.0:
                    self.avg_response_label.setStyleSheet("color: orange;")
                else:
                    self.avg_response_label.setStyleSheet("color: green;")
            
            # Actualizar tabla de módulos
            self._update_modules_table(metrics.get('modules', {}))
            
            # Actualizar recomendaciones
            performance = metrics.get('performance', {})
            recommendations = performance.get('recomendaciones', [])
            self._update_recommendations(recommendations)
            
            # Actualizar timestamp
            self.last_update_label.setText(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")
            
    def _update_modules_table(self, modules_metrics: Dict[str, Any]):
        """Actualiza la tabla de módulos"""
        self.modules_table.setRowCount(len(modules_metrics))
        
        for row, (module_name, metrics) in enumerate(modules_metrics.items()):
            self.modules_table.setItem(row, 0, QTableWidgetItem(module_name))
            self.modules_table.setItem(row, 1, QTableWidgetItem(f"{metrics.get('load_time', 0):.3f}"))
            self.modules_table.setItem(row, 2, QTableWidgetItem(str(metrics.get('query_count', 0))))
            self.modules_table.setItem(row, 3, QTableWidgetItem(str(metrics.get('error_count', 0))))
            self.modules_table.setItem(row, 4, QTableWidgetItem(str(metrics.get('active_views', 0))))
            
            last_activity = metrics.get('last_activity', 'N/A')
            if isinstance(last_activity, datetime):
                last_activity = last_activity.strftime('%H:%M:%S')
            self.modules_table.setItem(row, 5, QTableWidgetItem(str(last_activity)))
            
    def _update_recommendations(self, recommendations: List[str]):
        """Actualiza las recomendaciones de optimización"""
        text = "\\n".join(f"• {rec}" for rec in recommendations) if recommendations else "No hay recomendaciones específicas en este momento."
        self.recommendations_text.setText(text)
        
    def _handle_error(self, error_message: str):
        """Maneja errores del sistema"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alerts_text.append(f"[{timestamp}] ERROR: {error_message}")
        
    def _handle_alert(self, alert_type: str, message: str):
        """Maneja alertas de rendimiento"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alerts_text.append(f"[{timestamp}] {alert_type.upper()}: {message}")

def create_realtime_dashboard() -> RealtimeDashboard:
    """Factory function para crear el dashboard"""
    return RealtimeDashboard()

def show_dashboard():
    """Muestra el dashboard en tiempo real"""
    dashboard = create_realtime_dashboard()
    dashboard.show()
    return dashboard