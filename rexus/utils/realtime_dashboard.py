"""
Dashboard en Tiempo Real para Rexus.app
Sistema de métricas visuales en tiempo real para monitoreo del sistema
"""

import json
import time
import threading
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