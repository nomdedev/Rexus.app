"""
Sistema de monitoreo de rendimiento para Rexus.app v2.0.0
Optimizado para el proyecto post-reestructuración

Funcionalidades mejoradas:
- Monitoreo de SQL queries optimizado
- Cache inteligente de consultas frecuentes
- Análisis de cuellos de botella
- Alertas proactivas de rendimiento
"""

import time
import threading
from collections import defaultdict, deque
import functools

# Fallback para psutil si no está disponible
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Crear un mock de psutil para funcionalidad básica
    class MockPsutil:
        @staticmethod
        def cpu_percent(interval=None):
            return 0.0

        @staticmethod
        def virtual_memory():
            class MockMemory:
                percent = 0.0
                used = 1024 * 1024 * 1024  # 1GB mock
            return MockMemory()
        
        @staticmethod
        def Process():
            class MockProcess:
                def cpu_percent(self):
                    return 0.0
                def memory_percent(self):
                    return 0.0
                def memory_info(self):
                    class MockMemInfo:
                        rss = 1024 * 1024 * 50  # 50MB mock
                    return MockMemInfo()
            return MockProcess()

        @staticmethod
        def active_children():
            return []

    psutil = MockPsutil()
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from rexus.utils.logging_config import get_logger

@dataclass
class PerformanceMetric:
    """Métrica de rendimiento"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    active_threads: int
    db_connections: int = 0

class PerformanceMonitor:
    """Monitor de rendimiento optimizado de la aplicación"""

    def __init__(self):
        self.logger = get_logger('performance')
        self.metrics: List[PerformanceMetric] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Nuevas funcionalidades de optimización
        self.query_timings = defaultdict(deque)
        self.slow_operations = deque(maxlen=50)
        self.cache_hits = defaultdict(int)
        self.cache_misses = defaultdict(int)
        self.lock = threading.Lock()

    def start_monitoring(self, interval_seconds=60):
        """Inicia el monitoreo de rendimiento"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")

    def _monitor_loop(self, interval_seconds):
        """Loop principal de monitoreo"""
        while self.monitoring:
            try:
                metric = self._collect_metric()
                self.metrics.append(metric)

                # Mantener solo las últimas 100 métricas
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]

                # Log métricas críticas
                self._check_critical_thresholds(metric)

                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)

    def _collect_metric(self) -> PerformanceMetric:
        """Recolecta métricas actuales"""
        process = psutil.Process()

        return PerformanceMetric(
            timestamp=datetime.now(),
            cpu_percent=process.cpu_percent(),
            memory_percent=process.memory_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            active_threads=threading.active_count()
        )

    def _check_critical_thresholds(self, metric: PerformanceMetric):
        """Verifica umbrales críticos"""
        warnings = []

        if metric.cpu_percent > 80:
            warnings.append(f"High CPU usage: {metric.cpu_percent:.1f}%")

        if metric.memory_percent > 80:
            warnings.append(f"High memory usage: {metric.memory_percent:.1f}%")

        if metric.active_threads > 20:
            warnings.append(f"High thread count: {metric.active_threads}")

        for warning in warnings:
            self.logger.warning(warning)

    def get_current_stats(self) -> Dict:
        """Obtiene estadísticas actuales"""
        if not self.metrics:
            return {}

        recent_metrics = self.metrics[-10:]  # Últimas 10 métricas

        return {
            'avg_cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'current_memory_mb': recent_metrics[-1].memory_mb,
            'active_threads': recent_metrics[-1].active_threads,
            'last_update': recent_metrics[-1].timestamp
        }

    def record_query_timing(self, query_name: str, execution_time: float):
        """Registra tiempo de ejecución de consulta SQL"""
        with self.lock:
            if len(self.query_timings[query_name]) >= 100:
                self.query_timings[query_name].popleft()
            
            self.query_timings[query_name].append(execution_time)
            
            # Detectar operaciones lentas
            if execution_time > 1.0:
                self.slow_operations.append({
                    'query': query_name,
                    'time': execution_time,
                    'timestamp': time.time()
                })
                self.logger.warning(f"Slow SQL query: {query_name} ({execution_time:.3f}s)")
    
    def record_cache_hit(self, cache_key: str):
        """Registra hit de cache"""
        with self.lock:
            self.cache_hits[cache_key] += 1
    
    def record_cache_miss(self, cache_key: str):
        """Registra miss de cache"""
        with self.lock:
            self.cache_misses[cache_key] += 1
    
    def get_optimization_report(self) -> Dict:
        """Genera reporte de optimización"""
        with self.lock:
            report = {
                'sql_performance': {},
                'cache_performance': {},
                'slow_operations': list(self.slow_operations),
                'recommendations': []
            }
            
            # Análisis de rendimiento SQL
            for query, timings in self.query_timings.items():
                if timings:
                    avg_time = sum(timings) / len(timings)
                    report['sql_performance'][query] = {
                        'avg_time': avg_time,
                        'min_time': min(timings),
                        'max_time': max(timings),
                        'call_count': len(timings)
                    }
            
            # Análisis de cache
            total_hits = sum(self.cache_hits.values())
            total_misses = sum(self.cache_misses.values())
            total_requests = total_hits + total_misses
            
            if total_requests > 0:
                hit_rate = (total_hits / total_requests) * 100
                report['cache_performance'] = {
                    'hit_rate': hit_rate,
                    'total_hits': total_hits,
                    'total_misses': total_misses,
                    'efficiency': 'Excellent' if hit_rate > 90 else 'Good' if hit_rate > 75 else 'Poor'
                }
            
            # Generar recomendaciones
            report['recommendations'] = self._generate_optimization_recommendations(report)
            
            return report
    
    def _generate_optimization_recommendations(self, report: Dict) -> List[str]:
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Recomendaciones SQL
        for query, stats in report['sql_performance'].items():
            if stats['avg_time'] > 0.5:
                recommendations.append(f"Optimizar consulta '{query}' (promedio: {stats['avg_time']:.2f}s)")
        
        # Recomendaciones de cache
        cache_perf = report.get('cache_performance', {})
        if cache_perf.get('hit_rate', 0) < 75:
            recommendations.append("Mejorar estrategia de cache (hit rate bajo)")
        
        # Operaciones lentas
        if len(report['slow_operations']) > 5:
            recommendations.append("Múltiples operaciones lentas detectadas - revisar índices de BD")
        
        return recommendations

def performance_timer(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            if execution_time > 1.0:  # Log operaciones lentas
                logger = get_logger('performance')
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
    return wrapper

def sql_performance_monitor(query_name: str):
    """Decorador para monitorear rendimiento de consultas SQL"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_query_timing(query_name, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_query_timing(f"{query_name}_ERROR", execution_time)
                raise e
        return wrapper
    return decorator

# Instancia global del monitor
performance_monitor = PerformanceMonitor()
