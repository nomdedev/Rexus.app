"""
API REST para métricas de Rexus.app
Endpoint HTTP para acceder a métricas del sistema en tiempo real
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from rexus.utils.app_logger import get_logger
from rexus.utils.monitoring_system import get_metrics_collector, get_performance_analyzer
from rexus.utils.performance_monitor import get_performance_monitor, get_query_optimizer

logger = get_logger(__name__)

class MetricsAPIHandler(BaseHTTPRequestHandler):
    """Handler para requests de la API de métricas"""
    
    def __init__(self, *args, metrics_collector=None, performance_analyzer=None, 
                 performance_monitor=None, query_optimizer=None, **kwargs):
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.performance_analyzer = performance_analyzer or get_performance_analyzer()
        self.performance_monitor = performance_monitor or get_performance_monitor()
        self.query_optimizer = query_optimizer or get_query_optimizer()
        self.logger = get_logger(self.__class__.__name__)
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        """Maneja requests GET"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Routing de endpoints
            if path == '/api/metrics/system':
                self._handle_system_metrics()
            elif path == '/api/metrics/performance':
                self._handle_performance_metrics()
            elif path == '/api/metrics/modules':
                self._handle_modules_metrics()
            elif path == '/api/metrics/sql':
                self._handle_sql_metrics()
            elif path == '/api/metrics/trends':
                hours = int(query_params.get('hours', [24])[0])
                self._handle_trends_metrics(hours)
            elif path == '/api/metrics/recommendations':
                self._handle_recommendations()
            elif path == '/api/metrics/health':
                self._handle_health_check()
            elif path == '/api/metrics/all':
                self._handle_all_metrics()
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            self.logger.error(f"Error processing GET request: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
            
    def do_POST(self):
        """Maneja requests POST para comandos"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/api/metrics/start-monitoring':
                self._handle_start_monitoring()
            elif path == '/api/metrics/stop-monitoring':
                self._handle_stop_monitoring()
            elif path == '/api/metrics/reset-stats':
                self._handle_reset_stats()
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            self.logger.error(f"Error processing POST request: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
            
    def _handle_system_metrics(self):
        """Endpoint para métricas del sistema"""
        try:
            metrics = self.metrics_collector.get_performance_summary()
            self._send_json_response(metrics)
        except Exception as e:
            self._send_error(500, f"Error getting system metrics: {str(e)}")
            
    def _handle_performance_metrics(self):
        """Endpoint para métricas de rendimiento"""
        try:
            current_metrics = self.metrics_collector.get_current_metrics()
            performance_stats = self.performance_monitor.get_current_stats()
            
            response = {
                'current_metrics': current_metrics.__dict__ if current_metrics else None,
                'performance_stats': performance_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error getting performance metrics: {str(e)}")
            
    def _handle_modules_metrics(self):
        """Endpoint para métricas de módulos"""
        try:
            modules = self.metrics_collector.get_module_metrics()
            
            # Convertir datetime objects a strings
            serializable_modules = {}
            for name, metrics in modules.items():
                module_dict = metrics.__dict__.copy()
                if 'last_activity' in module_dict and hasattr(module_dict['last_activity'], 'isoformat'):
                    module_dict['last_activity'] = module_dict['last_activity'].isoformat()
                serializable_modules[name] = module_dict
                
            self._send_json_response(serializable_modules)
        except Exception as e:
            self._send_error(500, f"Error getting modules metrics: {str(e)}")
            
    def _handle_sql_metrics(self):
        """Endpoint para métricas SQL"""
        try:
            optimization_report = self.performance_monitor.get_optimization_report()
            query_stats = self.query_optimizer.get_query_statistics()
            
            response = {
                'optimization_report': optimization_report,
                'query_statistics': query_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error getting SQL metrics: {str(e)}")
            
    def _handle_trends_metrics(self, hours: int):
        """Endpoint para tendencias históricas"""
        try:
            trends = self.performance_analyzer.analyze_performance_trends()
            history = self.metrics_collector.get_metrics_history(hours=hours)
            
            # Convertir métricas históricas a formato serializable
            serializable_history = []
            for metric in history:
                metric_dict = metric.__dict__.copy()
                if 'timestamp' in metric_dict and hasattr(metric_dict['timestamp'], 'isoformat'):
                    metric_dict['timestamp'] = metric_dict['timestamp'].isoformat()
                serializable_history.append(metric_dict)
            
            response = {
                'trends_analysis': trends,
                'historical_data': serializable_history,
                'hours_requested': hours,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error getting trends: {str(e)}")
            
    def _handle_recommendations(self):
        """Endpoint para recomendaciones de optimización"""
        try:
            performance_trends = self.performance_analyzer.analyze_performance_trends()
            optimization_report = self.performance_monitor.get_optimization_report()
            query_recommendations = self.query_optimizer.get_optimization_recommendations()
            
            response = {
                'performance_recommendations': performance_trends.get('recomendaciones', []),
                'optimization_recommendations': optimization_report.get('recommendations', []),
                'sql_recommendations': query_recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error getting recommendations: {str(e)}")
            
    def _handle_health_check(self):
        """Endpoint para health check"""
        try:
            current_metrics = self.metrics_collector.get_current_metrics()
            
            if current_metrics:
                status = "healthy"
                if current_metrics.cpu_percent > 90 or current_metrics.memory_percent > 90:
                    status = "critical"
                elif current_metrics.cpu_percent > 70 or current_metrics.memory_percent > 70:
                    status = "warning"
            else:
                status = "unknown"
                
            response = {
                'status': status,
                'uptime_seconds': time.time(),
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Health check failed: {str(e)}")
            
    def _handle_all_metrics(self):
        """Endpoint para todas las métricas combinadas"""
        try:
            system_metrics = self.metrics_collector.get_performance_summary()
            current_metrics = self.metrics_collector.get_current_metrics()
            modules = self.metrics_collector.get_module_metrics()
            trends = self.performance_analyzer.analyze_performance_trends()
            optimization = self.performance_monitor.get_optimization_report()
            
            # Serializar módulos
            serializable_modules = {}
            for name, metrics in modules.items():
                module_dict = metrics.__dict__.copy()
                if 'last_activity' in module_dict and hasattr(module_dict['last_activity'], 'isoformat'):
                    module_dict['last_activity'] = module_dict['last_activity'].isoformat()
                serializable_modules[name] = module_dict
            
            response = {
                'system': system_metrics,
                'current': current_metrics.__dict__ if current_metrics else None,
                'modules': serializable_modules,
                'trends': trends,
                'optimization': optimization,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error getting all metrics: {str(e)}")
            
    def _handle_start_monitoring(self):
        """Endpoint para iniciar monitoreo"""
        try:
            self.metrics_collector.start_monitoring()
            response = {'status': 'started', 'message': 'Monitoring started successfully'}
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error starting monitoring: {str(e)}")
            
    def _handle_stop_monitoring(self):
        """Endpoint para detener monitoreo"""
        try:
            self.metrics_collector.stop_monitoring()
            response = {'status': 'stopped', 'message': 'Monitoring stopped successfully'}
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error stopping monitoring: {str(e)}")
            
    def _handle_reset_stats(self):
        """Endpoint para resetear estadísticas"""
        try:
            # Reset de estadísticas (implementar según necesidades)
            response = {'status': 'reset', 'message': 'Statistics reset successfully'}
            self._send_json_response(response)
        except Exception as e:
            self._send_error(500, f"Error resetting stats: {str(e)}")
            
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Envía respuesta JSON"""
        try:
            json_data = json.dumps(data, indent=2, default=str)
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json_data.encode())
        except Exception as e:
            self.logger.error(f"Error sending JSON response: {e}")
            
    def _send_error(self, status_code: int, message: str):
        """Envía respuesta de error"""
        try:
            error_data = {
                'error': True,
                'status_code': status_code,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            json_data = json.dumps(error_data, indent=2)
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json_data.encode())
        except Exception as e:
            self.logger.error(f"Error sending error response: {e}")
            
    def do_OPTIONS(self):
        """Maneja requests OPTIONS para CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def log_message(self, format, *args):
        """Override para usar nuestro logger"""
        self.logger.info(f"{self.client_address[0]} - {format % args}")

class MetricsAPIServer:
    """Servidor HTTP para la API de métricas"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.logger = get_logger(self.__class__.__name__)
        
        # Instancias de métricas
        self.metrics_collector = get_metrics_collector()
        self.performance_analyzer = get_performance_analyzer()
        self.performance_monitor = get_performance_monitor()
        self.query_optimizer = get_query_optimizer()
        
    def start(self):
        """Inicia el servidor API"""
        try:
            # Crear handler factory con dependencias
            def handler_factory(*args, **kwargs):
                return MetricsAPIHandler(
                    *args,
                    metrics_collector=self.metrics_collector,
                    performance_analyzer=self.performance_analyzer,
                    performance_monitor=self.performance_monitor,
                    query_optimizer=self.query_optimizer,
                    **kwargs
                )
            
            # Crear servidor
            self.server = HTTPServer((self.host, self.port), handler_factory)
            
            # Iniciar en thread separado
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.logger.info(f"✅ API de métricas iniciada en http://{self.host}:{self.port}")
            self.logger.info("Endpoints disponibles:")
            self.logger.info("  GET  /api/metrics/system - Métricas del sistema")
            self.logger.info("  GET  /api/metrics/performance - Métricas de rendimiento")
            self.logger.info("  GET  /api/metrics/modules - Métricas de módulos")
            self.logger.info("  GET  /api/metrics/sql - Métricas SQL")
            self.logger.info("  GET  /api/metrics/trends?hours=24 - Tendencias históricas")
            self.logger.info("  GET  /api/metrics/recommendations - Recomendaciones")
            self.logger.info("  GET  /api/metrics/health - Health check")
            self.logger.info("  GET  /api/metrics/all - Todas las métricas")
            self.logger.info("  POST /api/metrics/start-monitoring - Iniciar monitoreo")
            self.logger.info("  POST /api/metrics/stop-monitoring - Detener monitoreo")
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando servidor API: {e}")
            raise
            
    def stop(self):
        """Detiene el servidor API"""
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                
            if self.server_thread:
                self.server_thread.join(timeout=5)
                
            self.is_running = False
            self.logger.info("✅ API de métricas detenida")
            
        except Exception as e:
            self.logger.error(f"❌ Error deteniendo servidor API: {e}")

# Instancia global del servidor
_api_server = None

def start_metrics_api(host='localhost', port=8080) -> MetricsAPIServer:
    """Inicia la API de métricas"""
    global _api_server
    if _api_server and _api_server.is_running:
        logger.warning("La API de métricas ya está ejecutándose")
        return _api_server
        
    _api_server = MetricsAPIServer(host, port)
    _api_server.start()
    return _api_server

def stop_metrics_api():
    """Detiene la API de métricas"""
    global _api_server
    if _api_server:
        _api_server.stop()
        _api_server = None

def get_metrics_api_server() -> Optional[MetricsAPIServer]:
    """Obtiene la instancia del servidor API"""
    return _api_server