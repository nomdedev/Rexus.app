"""
Sistema de Monitoreo y Métricas en Tiempo Real para Rexus.app
Proporciona métricas de rendimiento, uso de recursos y estadísticas del sistema
"""

import time
import threading
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json

from rexus.utils.app_logger import get_logger
from rexus.core.database import get_inventario_connection, get_users_connection

logger = get_logger(__name__)

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: float
    disk_usage_percent: float
    active_connections: int
    query_count: int
    error_count: int
    response_time_avg: float
    user_sessions: int

@dataclass
class ModuleMetrics:
    """Métricas por módulo"""
    module_name: str
    load_time: float
    query_count: int
    error_count: int
    active_views: int
    cache_hits: int
    cache_misses: int
    last_activity: datetime

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.is_running = False
        self.collection_thread = None
        self.metrics_storage = []
        self.module_metrics = {}
        self.query_times = []
        self.error_count = 0
        self.user_sessions = set()
        
    def start_monitoring(self, interval: int = 30):
        """Inicia el monitoreo de métricas"""
        if self.is_running:
            self.logger.warning("El sistema de monitoreo ya está ejecutándose")
            return
            
        self.is_running = True
        self.collection_thread = threading.Thread(
            target=self._collect_metrics_loop,
            args=(interval,),
            daemon=True
        )
        self.collection_thread.start()
        self.logger.info(f"Sistema de monitoreo iniciado con intervalo de {interval} segundos")
        
    def stop_monitoring(self):
        """Detiene el monitoreo de métricas"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        self.logger.info("Sistema de monitoreo detenido")
        
    def _collect_metrics_loop(self, interval: int):
        """Loop principal de recolección de métricas"""
        while self.is_running:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_storage.append(metrics)
                
                # Mantener solo las últimas 1000 métricas
                if len(self.metrics_storage) > 1000:
                    self.metrics_storage = self.metrics_storage[-1000:]
                    
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error recolectando métricas: {e}")
                time.sleep(interval)
                
    def _collect_system_metrics(self) -> SystemMetrics:
        """Recolecta métricas del sistema"""
        try:
            # Métricas de CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            # Métricas de base de datos
            active_connections = self._get_active_connections()
            query_count = len(self.query_times)
            
            # Tiempo de respuesta promedio
            if self.query_times:
                response_time_avg = sum(self.query_times) / len(self.query_times)
                self.query_times = self.query_times[-100:]  # Mantener últimas 100
            else:
                response_time_avg = 0.0
                
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available / (1024**3),  # GB
                disk_usage_percent=disk.percent,
                active_connections=active_connections,
                query_count=query_count,
                error_count=self.error_count,
                response_time_avg=response_time_avg,
                user_sessions=len(self.user_sessions)
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error recolectando métricas del sistema: {e}")
            # Retornar métricas vacías en caso de error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available=0.0,
                disk_usage_percent=0.0,
                active_connections=0,
                query_count=0,
                error_count=self.error_count,
                response_time_avg=0.0,
                user_sessions=0
            )
            
    def _get_active_connections(self) -> int:
        """Obtiene el número de conexiones activas a la base de datos"""
        try:
            # Simular conteo de conexiones activas
            return 2  # Conexiones base: inventario y usuarios
        except:
            return 0
            
    def record_query_time(self, duration: float):
        """Registra el tiempo de una consulta"""
        self.query_times.append(duration)
        
    def record_error(self):
        """Registra un error"""
        self.error_count += 1
        
    def record_user_session(self, user_id: str):
        """Registra una sesión de usuario"""
        self.user_sessions.add(user_id)
        
    def remove_user_session(self, user_id: str):
        """Remueve una sesión de usuario"""
        self.user_sessions.discard(user_id)
        
    def record_module_metrics(self, module_name: str, metrics: Dict[str, Any]):
        """Registra métricas de un módulo específico"""
        module_metrics = ModuleMetrics(
            module_name=module_name,
            load_time=metrics.get('load_time', 0.0),
            query_count=metrics.get('query_count', 0),
            error_count=metrics.get('error_count', 0),
            active_views=metrics.get('active_views', 0),
            cache_hits=metrics.get('cache_hits', 0),
            cache_misses=metrics.get('cache_misses', 0),
            last_activity=datetime.now()
        )
        self.module_metrics[module_name] = module_metrics
        
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Obtiene las métricas actuales del sistema"""
        if self.metrics_storage:
            return self.metrics_storage[-1]
        return None
        
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Obtiene el historial de métricas de las últimas horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_storage if m.timestamp >= cutoff_time]
        
    def get_module_metrics(self) -> Dict[str, ModuleMetrics]:
        """Obtiene métricas de todos los módulos"""
        return self.module_metrics.copy()
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de rendimiento del sistema"""
        if not self.metrics_storage:
            return {"status": "No hay datos disponibles"}
            
        recent_metrics = self.get_metrics_history(hours=1)
        if not recent_metrics:
            recent_metrics = [self.metrics_storage[-1]]
            
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_response = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
        
        total_errors = sum(m.error_count for m in recent_metrics)
        total_queries = sum(m.query_count for m in recent_metrics)
        
        # Determinar estado del sistema
        status = "OPTIMO"
        if avg_cpu > 80 or avg_memory > 80:
            status = "SOBRECARGADO"
        elif avg_cpu > 60 or avg_memory > 60:
            status = "ALTO USO"
        elif avg_response > 2.0:
            status = "RESPUESTA LENTA"
            
        return {
            "status": status,
            "cpu_promedio": round(avg_cpu, 2),
            "memoria_promedio": round(avg_memory, 2),
            "tiempo_respuesta_promedio": round(avg_response, 3),
            "total_errores": total_errors,
            "total_consultas": total_queries,
            "sesiones_activas": len(self.user_sessions),
            "modulos_activos": len(self.module_metrics),
            "timestamp": datetime.now().isoformat()
        }

class PerformanceAnalyzer:
    """Analizador de rendimiento del sistema"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = get_logger(self.__class__.__name__)
        
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analiza tendencias de rendimiento"""
        metrics_24h = self.metrics_collector.get_metrics_history(hours=24)
        metrics_1h = self.metrics_collector.get_metrics_history(hours=1)
        
        if len(metrics_24h) < 2:
            return {"status": "Datos insuficientes para análisis"}
            
        # Análisis de CPU
        cpu_trend = self._calculate_trend([m.cpu_percent for m in metrics_24h])
        memory_trend = self._calculate_trend([m.memory_percent for m in metrics_24h])
        response_trend = self._calculate_trend([m.response_time_avg for m in metrics_24h])
        
        # Picos de uso
        cpu_peak = max(m.cpu_percent for m in metrics_24h)
        memory_peak = max(m.memory_percent for m in metrics_24h)
        
        # Recomendaciones
        recommendations = []
        if cpu_trend > 5:
            recommendations.append("CPU en tendencia ascendente - considerar optimización")
        if memory_trend > 5:
            recommendations.append("Memoria en tendencia ascendente - revisar memory leaks")
        if response_trend > 0.5:
            recommendations.append("Tiempo de respuesta aumentando - optimizar consultas")
        if cpu_peak > 90:
            recommendations.append("Picos de CPU detectados - revisar procesos intensivos")
        if memory_peak > 90:
            recommendations.append("Picos de memoria detectados - revisar uso de memoria")
            
        return {
            "tendencia_cpu": round(cpu_trend, 2),
            "tendencia_memoria": round(memory_trend, 2),
            "tendencia_respuesta": round(response_trend, 3),
            "pico_cpu": round(cpu_peak, 2),
            "pico_memoria": round(memory_peak, 2),
            "recomendaciones": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcula la tendencia de una serie de valores"""
        if len(values) < 2:
            return 0.0
            
        # Regresión lineal simple
        n = len(values)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Pendiente de la línea de tendencia
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0.0
            
        return slope

# Instancia global del sistema de monitoreo
_metrics_collector = None
_performance_analyzer = None

def get_metrics_collector() -> MetricsCollector:
    """Obtiene la instancia global del recolector de métricas"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_performance_analyzer() -> PerformanceAnalyzer:
    """Obtiene la instancia global del analizador de rendimiento"""
    global _performance_analyzer
    if _performance_analyzer is None:
        _performance_analyzer = PerformanceAnalyzer(get_metrics_collector())
    return _performance_analyzer

def start_monitoring(interval: int = 30):
    """Inicia el sistema de monitoreo global"""
    collector = get_metrics_collector()
    collector.start_monitoring(interval)

def stop_monitoring():
    """Detiene el sistema de monitoreo global"""
    global _metrics_collector
    if _metrics_collector:
        _metrics_collector.stop_monitoring()

def get_system_status() -> Dict[str, Any]:
    """Obtiene el estado actual del sistema"""
    collector = get_metrics_collector()
    return collector.get_performance_summary()

def get_performance_report() -> Dict[str, Any]:
    """Obtiene un reporte completo de rendimiento"""
    collector = get_metrics_collector()
    analyzer = get_performance_analyzer()
    
    return {
        "sistema": collector.get_performance_summary(),
        "tendencias": analyzer.analyze_performance_trends(),
        "modulos": {name: asdict(metrics) for name, metrics in collector.get_module_metrics().items()},
        "timestamp": datetime.now().isoformat()
    }