"""
Dashboard en Tiempo Real para Rexus.app
Sistema de métricas visuales en tiempo real para monitoreo del sistema
"""

from datetime import datetime
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTextEdit, QGroupBox, QSplitter
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCloseEvent


class RealtimeDashboard(QWidget):
    """
    Dashboard en tiempo real para monitoreo del sistema Rexus
    """

    # Constantes para estilos
    STYLE_RED_BOLD = "color: red; font-weight: bold;"
    STYLE_ORANGE_BOLD = "color: orange; font-weight: bold;"
    STYLE_GREEN = "color: green;"

    # Señales para comunicación
    metrics_updated = pyqtSignal(dict)
    alert_triggered = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.metrics_data = {}
        self.update_timer = None
        self.init_ui()
        self.setup_timer()
        self.connect_signals()

    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Dashboard en Tiempo Real - Rexus.app")
        self.setGeometry(100, 100, 1200, 800)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Dashboard de Monitoreo en Tiempo Real")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Splitter para dividir la interfaz
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel superior: métricas principales
        top_widget = self._create_metrics_panel()
        splitter.addWidget(top_widget)

        # Panel inferior: detalles
        bottom_widget = self._create_details_panel()
        splitter.addWidget(bottom_widget)

        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)

        # Barra de estado
        self.status_bar = QLabel("Estado: Conectado")
        self.status_bar.setStyleSheet("color: green; font-weight: bold;")
        main_layout.addWidget(self.status_bar)

    def _create_metrics_panel(self) -> QWidget:
        """Crear panel de métricas principales"""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Grupo de rendimiento
        perf_group = QGroupBox("Rendimiento del Sistema")
        perf_layout = QVBoxLayout(perf_group)

        self.cpu_label = QLabel("CPU: --%")
        self.memory_label = QLabel("Memoria: --%")
        self.disk_label = QLabel("Disco: --%")
        self.network_label = QLabel("Red: -- KB/s")

        perf_layout.addWidget(self.cpu_label)
        perf_layout.addWidget(self.memory_label)
        perf_layout.addWidget(self.disk_label)
        perf_layout.addWidget(self.network_label)

        layout.addWidget(perf_group)

        # Grupo de respuesta
        response_group = QGroupBox("Tiempo de Respuesta")
        response_layout = QVBoxLayout(response_group)

        self.avg_response_label = QLabel("Promedio: -- ms")
        self.max_response_label = QLabel("Máximo: -- ms")
        self.min_response_label = QLabel("Mínimo: -- ms")

        response_layout.addWidget(self.avg_response_label)
        response_layout.addWidget(self.max_response_label)
        response_layout.addWidget(self.min_response_label)

        layout.addWidget(response_group)

        # Grupo de estado
        status_group = QGroupBox("Estado General")
        status_layout = QVBoxLayout(status_group)

        self.active_users_label = QLabel("Usuarios activos: --")
        self.active_sessions_label = QLabel("Sesiones: --")
        self.last_update_label = QLabel("Última actualización: --")

        status_layout.addWidget(self.active_users_label)
        status_layout.addWidget(self.active_sessions_label)
        status_layout.addWidget(self.last_update_label)

        layout.addWidget(status_group)

        return panel

    def _create_details_panel(self) -> QWidget:
        """Crear panel de detalles"""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Tabla de módulos
        modules_group = QGroupBox("Módulos del Sistema")
        modules_layout = QVBoxLayout(modules_group)

        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(6)
        self.modules_table.setHorizontalHeaderLabels([
            "Módulo", "Tiempo de Carga", "Consultas", "Errores", "Vistas", "Última Actividad"
        ])
        self.modules_table.setAlternatingRowColors(True)

        modules_layout.addWidget(self.modules_table)
        layout.addWidget(modules_group)

        # Panel derecho: alertas y recomendaciones
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Recomendaciones
        rec_group = QGroupBox("Recomendaciones de Optimización")
        rec_layout = QVBoxLayout(rec_group)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)

        rec_layout.addWidget(self.recommendations_text)
        right_layout.addWidget(rec_group)

        # Alertas
        alerts_group = QGroupBox("Alertas del Sistema")
        alerts_layout = QVBoxLayout(alerts_group)

        self.alerts_text = QTextEdit()
        self.alerts_text.setMaximumHeight(150)
        self.alerts_text.setReadOnly(True)

        alerts_layout.addWidget(self.alerts_text)
        right_layout.addWidget(alerts_group)

        layout.addWidget(right_panel)

        return panel

    def setup_timer(self):
        """Configurar timer para actualizaciones periódicas"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(5000)  # Actualizar cada 5 segundos

    def connect_signals(self):
        """Conectar señales"""
        self.metrics_updated.connect(self._on_metrics_updated)
        self.alert_triggered.connect(self._on_alert_triggered)

    def _update_metrics(self):
        """Actualizar métricas del sistema"""
        try:
            # Simular obtención de métricas (en producción vendría de un servicio)
            metrics = self._get_system_metrics()

            # Actualizar métricas principales
            self._update_main_metrics(metrics)

            # Actualizar tabla de módulos
            self._update_modules_table(metrics.get('modules', {}))

            # Actualizar recomendaciones
            performance = metrics.get('performance', {})
            recommendations = performance.get('recomendaciones', [])
            self._update_recommendations(recommendations)

            # Actualizar timestamp
            self.last_update_label.setText(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

            # Emitir señal de actualización
            self.metrics_updated.emit(metrics)

        except Exception as e:
            self._handle_error(f"Error al actualizar métricas: {str(e)}")

    def _update_main_metrics(self, metrics: Dict[str, Any]):
        """Actualizar métricas principales en la UI"""
        system = metrics.get('system', {})

        # CPU
        cpu_usage = system.get('cpu_percent', 0)
        self.cpu_label.setText(f"CPU: {cpu_usage:.1f}%")
        self._set_metric_color(self.cpu_label, cpu_usage, 80)

        # Memoria
        memory_usage = system.get('memory_percent', 0)
        self.memory_label.setText(f"Memoria: {memory_usage:.1f}%")
        self._set_metric_color(self.memory_label, memory_usage, 85)

        # Disco
        disk_usage = system.get('disk_percent', 0)
        self.disk_label.setText(f"Disco: {disk_usage:.1f}%")
        self._set_metric_color(self.disk_label, disk_usage, 90)

        # Red
        network_speed = system.get('network_speed', 0)
        self.network_label.setText(f"Red: {network_speed:.1f} KB/s")

        # Respuesta
        response_time = metrics.get('avg_response_time', 0)
        self.avg_response_label.setText(f"Promedio: {response_time:.2f} ms")
        self._set_response_color(self.avg_response_label, response_time)

        # Usuarios y sesiones
        users = metrics.get('active_users', 0)
        sessions = metrics.get('active_sessions', 0)
        self.active_users_label.setText(f"Usuarios activos: {users}")
        self.active_sessions_label.setText(f"Sesiones: {sessions}")

    def _set_metric_color(self, label: QLabel, value: float, threshold: float):
        """Establecer color según el valor y umbral"""
        if value > threshold:
            label.setStyleSheet("color: red; font-weight: bold;")
        elif value > threshold * 0.8:
            label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            label.setStyleSheet("color: green;")

    def _set_response_color(self, label: QLabel, response_time: float):
        """Establecer color para tiempo de respuesta"""
        if response_time > 2.0:
            label.setStyleSheet("color: red; font-weight: bold;")
        elif response_time > 1.0:
            label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            label.setStyleSheet("color: green;")

    def _update_modules_table(self, modules_metrics: Dict[str, Any]):
        """Actualiza la tabla de módulos"""
        self.modules_table.setRowCount(len(modules_metrics))

        for row, (module_name, metrics) in enumerate(modules_metrics.items()):
            self.modules_table.setItem(row, 0, QTableWidgetItem(module_name))
            self.modules_table.setItem(row, 1, QTableWidgetItem(f"{metrics.get('load_time', 0):.3f}s"))
            self.modules_table.setItem(row, 2, QTableWidgetItem(str(metrics.get('query_count', 0))))
            self.modules_table.setItem(row, 3, QTableWidgetItem(str(metrics.get('error_count', 0))))
            self.modules_table.setItem(row, 4, QTableWidgetItem(str(metrics.get('active_views', 0))))

            last_activity = metrics.get('last_activity', 'N/A')
            if isinstance(last_activity, datetime):
                last_activity = last_activity.strftime('%H:%M:%S')
            self.modules_table.setItem(row, 5, QTableWidgetItem(str(last_activity)))

    def _update_recommendations(self, recommendations: List[str]):
        """Actualiza las recomendaciones de optimización"""
        if recommendations:
            text = "\n".join(f"• {rec}" for rec in recommendations)
        else:
            text = "No hay recomendaciones específicas en este momento."
        self.recommendations_text.setText(text)

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema (simulado)"""
        # En producción, esto obtendría datos reales del sistema
        return {
            'system': {
                'cpu_percent': 45.2,
                'memory_percent': 62.8,
                'disk_percent': 34.1,
                'network_speed': 1250.5
            },
            'avg_response_time': 0.8,
            'active_users': 12,
            'active_sessions': 18,
            'modules': {
                'inventario': {
                    'load_time': 0.234,
                    'query_count': 45,
                    'error_count': 0,
                    'active_views': 3,
                    'last_activity': datetime.now()
                },
                'pedidos': {
                    'load_time': 0.156,
                    'query_count': 23,
                    'error_count': 1,
                    'active_views': 2,
                    'last_activity': datetime.now()
                }
            },
            'performance': {
                'recomendaciones': [
                    'Optimizar consultas de inventario',
                    'Implementar caché para pedidos frecuentes',
                    'Revisar índices de base de datos'
                ]
            }
        }

    def _handle_error(self, error_message: str):
        """Maneja errores del sistema"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alerts_text.append(f"[{timestamp}] ERROR: {error_message}")
        self.status_bar.setText("Estado: Error detectado")
        self.status_bar.setStyleSheet("color: red; font-weight: bold;")

    def _handle_alert(self, alert_type: str, message: str):
        """Maneja alertas de rendimiento"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alerts_text.append(f"[{timestamp}] {alert_type.upper()}: {message}")

    def _on_metrics_updated(self, metrics: Dict[str, Any]):
        """Manejador de señal de métricas actualizadas"""
        self.metrics_data = metrics
        self.status_bar.setText("Estado: Conectado")
        self.status_bar.setStyleSheet("color: green; font-weight: bold;")

    def _on_alert_triggered(self, alert_type: str, message: str):
        """Manejador de señal de alerta"""
        self._handle_alert(alert_type, message)

    def closeEvent(self, a0):
        """Manejador de cierre de ventana"""
        if self.update_timer:
            self.update_timer.stop()
        a0.accept()


def create_realtime_dashboard() -> RealtimeDashboard:
    """Factory function para crear el dashboard"""
    return RealtimeDashboard()


def show_dashboard():
    """Muestra el dashboard en tiempo real"""
    dashboard = create_realtime_dashboard()
    dashboard.show()
    return dashboard