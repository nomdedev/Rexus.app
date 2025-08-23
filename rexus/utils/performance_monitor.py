"""
Sistema de monitoreo de rendimiento para Rexus.app v2.0.0
Optimizado para el proyecto post-reestructuración

Funcionalidades mejoradas:
- Monitoreo de SQL queries optimizado
- Cache inteligente de consultas frecuentes
- Análisis de cuellos de botella
- Alertas proactivas de rendimiento
"""


import logging
logger = logging.getLogger(__name__)

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
                self.                raise e
        return wrapper
    return decorator

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

# Factory functions
def get_performance_monitor() -> PerformanceMonitor:
    """Obtiene la instancia global del monitor de rendimiento"""
    return performance_monitor

def get_query_optimizer():
    """Obtiene una nueva instancia del optimizador de consultas"""
    class QueryOptimizer:
        """Analizador y optimizador de consultas SQL básico"""
        
        def __init__(self):
            self.slow_queries = []
            self.query_stats = {}
            self.logger = get_logger(self.__class__.__name__)
            
        def get_query_statistics(self):
            """Obtiene estadísticas básicas de consultas"""
            return {
                "message": "Sistema de optimización de consultas inicializado",
                "slow_queries_count": len(self.slow_queries),
                "total_queries": len(self.query_stats)
            }
            
        def get_optimization_recommendations(self):
            """Obtiene recomendaciones básicas"""
            return [
                "Revisar índices en tablas principales",
                "Optimizar consultas con múltiples JOINs",
                "Considerar paginación en consultas grandes"
            ]
    
    return QueryOptimizer()
