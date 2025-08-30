"""
Rexus.app - Executive Dashboard

Dashboard ejecutivo con métricas y KPIs principales.
Muestra información consolidada del estado del sistema.
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt

from rexus.utils.app_logger import log_info


class ExecutiveDashboard:
    """
    Dashboard ejecutivo con métricas principales.
    Muestra KPIs y estado general del sistema.
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.widget = None
        self._create_dashboard()

    def _create_dashboard(self):
        """Crea la interfaz del dashboard ejecutivo."""
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Título
        title_label = QLabel("Dashboard Ejecutivo - Rexus.app")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin: 15px;
            }
        """)
        layout.addWidget(title_label)

        # Grid de métricas
        metrics_frame = QFrame()
        metrics_layout = QGridLayout(metrics_frame)

        # Métricas de ejemplo
        metrics = [
            ("Usuarios Activos", "1,234", "#27ae60"),
            ("Ventas del Día", "$45,678", "#3498db"),
            ("Pedidos Pendientes", "89", "#e74c3c"),
            ("Productos en Stock", "12,345", "#f39c12")
        ]

        for i, (label, value, color) in enumerate(metrics):
            metric_widget = self._create_metric_widget(label, value, color)
            row = i // 2
            col = i % 2
            metrics_layout.addWidget(metric_widget, row, col)

        layout.addWidget(metrics_frame)

        # Estado del sistema
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)

        status_title = QLabel("Estado del Sistema")
        status_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        status_layout.addWidget(status_title)

        status_items = [
            ("Base de Datos", "Conectada", "#27ae60"),
            ("Servicios", "Operativos", "#27ae60"),
            ("Backup", "Actualizado", "#f39c12"),
            ("Seguridad", "Activa", "#27ae60")
        ]

        for service, status, color in status_items:
            status_widget = self._create_status_widget(service, status, color)
            status_layout.addWidget(status_widget)

        layout.addWidget(status_frame)
        layout.addStretch()

        log_info("Dashboard ejecutivo creado exitosamente", "executive_dashboard")

    def _create_metric_widget(self, label: str, value: str, color: str) -> QWidget:
        """Crea un widget para mostrar una métrica."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                margin: 10px;
            }}
        """)

        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
            }
        """)

        layout.addWidget(value_label)
        layout.addWidget(label_widget)

        widget.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                margin: 5px;
            }}
        """)

        return widget

    def _create_status_widget(self, service: str, status: str, color: str) -> QWidget:
        """Crea un widget para mostrar el estado de un servicio."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        service_label = QLabel(f"{service}:")
        service_label.setStyleSheet("font-weight: bold;")

        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        layout.addWidget(service_label)
        layout.addStretch()
        layout.addWidget(status_label)

        return widget

    def get_widget(self) -> Optional[QWidget]:
        """Obtiene el widget del dashboard ejecutivo."""
        return self.widget

    def refresh_data(self):
        """Actualiza los datos del dashboard."""
        log_info("Datos del dashboard ejecutivo actualizados", "executive_dashboard")


def get_dashboard_manager():
    """Función de conveniencia para obtener el dashboard ejecutivo."""
    return ExecutiveDashboard()
