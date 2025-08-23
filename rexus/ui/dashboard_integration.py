"""
Integración del Dashboard Ejecutivo con la Aplicación Principal
Proporciona funciones para integrar el dashboard en diferentes módulos

Fecha: 23/08/2025
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QIcon

logger = logging.getLogger(__name__)

class DashboardWidget(QWidget):
    """Widget compacto para mostrar métricas en otros módulos."""
    
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics = {}
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Frame contenedor
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(8, 4, 8, 4)
        
        # Indicadores compactos
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("RAM: --")
        self.status_label = QLabel("Estado: OK")
        
        # Botón para abrir dashboard completo
        self.dashboard_btn = QPushButton("📊")
        self.dashboard_btn.setMaximumWidth(30)
        self.dashboard_btn.setToolTip("Abrir Dashboard Ejecutivo")
        self.dashboard_btn.clicked.connect(self.open_full_dashboard)
        
        frame_layout.addWidget(self.cpu_label)
        frame_layout.addWidget(QLabel("|"))
        frame_layout.addWidget(self.memory_label)
        frame_layout.addWidget(QLabel("|"))
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.dashboard_btn)
        
        layout.addWidget(frame)
        
    def setup_timer(self):
        """Configura el timer para actualizar métricas."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(10000)  # Actualizar cada 10 segundos
        
    def update_metrics(self):
        """Actualiza las métricas mostradas."""
        try:
            from ..utils.performance_monitor import PerformanceMonitor
            
            # Crear instancia temporal del monitor
            monitor = PerformanceMonitor()
            current_metrics = monitor.get_current_metrics()
            
            if current_metrics:
                self.metrics = current_metrics
                
                # Actualizar labels
                cpu_percent = current_metrics.get('cpu_percent', 0)
                memory_percent = current_metrics.get('memory_percent', 0)
                
                self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
                self.memory_label.setText(f"RAM: {memory_percent:.1f}%")
                
                # Actualizar estado
                if cpu_percent > 90 or memory_percent > 90:
                    self.status_label.setText("Estado: CRÍTICO")
                    self.status_label.setStyleSheet("color: red; font-weight: bold;")
                elif cpu_percent > 75 or memory_percent > 75:
                    self.status_label.setText("Estado: ALERTA")
                    self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                else:
                    self.status_label.setText("Estado: OK")
                    self.status_label.setStyleSheet("color: green;")
                    
                self.metrics_updated.emit(current_metrics)
                
        except Exception as e:
            logger.error(f"Error actualizando métricas del widget: {e}")
            self.status_label.setText("Estado: ERROR")
            self.status_label.setStyleSheet("color: red;")
            
    def open_full_dashboard(self):
        """Abre el dashboard ejecutivo completo."""
        try:
            from .executive_dashboard import get_dashboard_manager
            
            manager = get_dashboard_manager()
            dashboard = manager.create_dashboard()
            
            if dashboard:
                dashboard.setWindowTitle("Dashboard Ejecutivo - Rexus.app")
                dashboard.resize(1200, 800)
                dashboard.show()
                dashboard.raise_()
                
        except Exception as e:
            logger.error(f"Error abriendo dashboard completo: {e}")

class ModuleDashboardIntegration:
    """Clase para integrar dashboard en módulos específicos."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.dashboard_widget = None
        
    def add_to_module(self, parent_layout) -> Optional[DashboardWidget]:
        """Añade el widget de dashboard a un módulo."""
        try:
            if self.dashboard_widget is None:
                self.dashboard_widget = DashboardWidget()
                
            # Añadir al layout del módulo
            if hasattr(parent_layout, 'addWidget'):
                parent_layout.addWidget(self.dashboard_widget)
            else:
                logger.warning(f"Layout del módulo {self.module_name} no compatible")
                return None
                
            logger.info(f"Dashboard integrado en módulo {self.module_name}")
            return self.dashboard_widget
            
        except Exception as e:
            logger.error(f"Error integrando dashboard en {self.module_name}: {e}")
            return None
            
    def remove_from_module(self):
        """Remueve el widget de dashboard del módulo."""
        if self.dashboard_widget:
            self.dashboard_widget.setParent(None)
            self.dashboard_widget = None

def integrate_dashboard_in_module(module_name: str, parent_layout) -> Optional[DashboardWidget]:
    """Función de conveniencia para integrar dashboard en un módulo."""
    integration = ModuleDashboardIntegration(module_name)
    return integration.add_to_module(parent_layout)

def create_dashboard_button(parent=None) -> QPushButton:
    """Crea un botón para abrir el dashboard ejecutivo."""
    btn = QPushButton("📊 Dashboard", parent)
    btn.setToolTip("Abrir Dashboard Ejecutivo con métricas del sistema")
    
    def open_dashboard():
        try:
            from .executive_dashboard import get_dashboard_manager
            
            manager = get_dashboard_manager()
            dashboard = manager.create_dashboard()
            
            if dashboard:
                dashboard.setWindowTitle("Dashboard Ejecutivo - Rexus.app")
                dashboard.resize(1200, 800)
                dashboard.show()
                dashboard.raise_()
                
        except Exception as e:
            logger.error(f"Error abriendo dashboard desde botón: {e}")
    
    btn.clicked.connect(open_dashboard)
    return btn

class DashboardMetricsCollector:
    """Recolector de métricas específicas para el dashboard."""
    
    def __init__(self):
        self.module_metrics = {}
        
    def register_module_metrics(self, module_name: str, metrics_provider):
        """Registra un proveedor de métricas para un módulo."""
        self.module_metrics[module_name] = metrics_provider
        
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Recolecta métricas de todos los módulos registrados."""
        all_metrics = {}
        
        for module_name, provider in self.module_metrics.items():
            try:
                if callable(provider):
                    module_data = provider()
                    if isinstance(module_data, dict):
                        all_metrics[module_name] = module_data
                elif hasattr(provider, 'get_metrics'):
                    module_data = provider.get_metrics()
                    if isinstance(module_data, dict):
                        all_metrics[module_name] = module_data
                        
            except Exception as e:
                logger.error(f"Error recolectando métricas del módulo {module_name}: {e}")
                all_metrics[module_name] = {"error": str(e)}
                
        return all_metrics
        
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Obtiene un resumen de las métricas principales."""
        all_metrics = self.collect_all_metrics()
        
        summary = {
            'total_modules': len(all_metrics),
            'modules_with_errors': len([m for m in all_metrics.values() if 'error' in m]),
            'timestamp': datetime.now().isoformat()
        }
        
        return summary

# Instancia global del recolector
metrics_collector = DashboardMetricsCollector()

def get_metrics_collector() -> DashboardMetricsCollector:
    """Obtiene el recolector global de métricas."""
    return metrics_collector

if __name__ == "__main__":
    # Test básico de los componentes
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys
    
    app = QApplication(sys.argv)
    
    main_window = QMainWindow()
    main_window.setWindowTitle("Test Dashboard Integration")
    
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Añadir widget de dashboard
    dashboard_widget = DashboardWidget()
    layout.addWidget(dashboard_widget)
    
    # Añadir botón de dashboard
    dashboard_btn = create_dashboard_button()
    layout.addWidget(dashboard_btn)
    
    main_window.setCentralWidget(central_widget)
    main_window.show()
    
    sys.exit(app.exec())