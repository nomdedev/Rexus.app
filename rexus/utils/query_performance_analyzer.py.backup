"""
Analizador de Rendimiento de Consultas SQL para Rexus.app

Detecta y optimiza consultas N+1, consultas lentas y problemas
de rendimiento en bases de datos.
"""

import logging
import time
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
import functools

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Métricas de rendimiento de una consulta SQL."""
    query_hash: str
    sql_query: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    last_executed: datetime = field(default_factory=datetime.now)
    caller_info: List[str] = field(default_factory=list)
    is_slow_query: bool = False
    is_n_plus_one: bool = False


@dataclass
class NPlusOneDetection:
    """Detección de problemas N+1."""
    pattern_hash: str
    base_query: str
    related_queries: List[str]
    execution_count: int
    detected_at: datetime
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'


class QueryPerformanceAnalyzer:
    """
    Analizador de rendimiento para consultas SQL.
    
    Detecta:
    - Consultas lentas (> threshold)
    - Problemas N+1 
    - Consultas duplicadas
    - Patrones de consultas ineficientes
    """

    def __init__(self, slow_query_threshold: float = 1.0):
        """
        Inicializa el analizador.
        
        Args:
            slow_query_threshold: Umbral en segundos para considerar consulta lenta
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.n_plus_one_detections: List[NPlusOneDetection] = []
        self.active_queries: Dict[str, float] = {}  # query_id -> start_time
        self._lock = threading.RLock()
        
        # Configuraciones de detección
        self.n_plus_one_threshold = 10  # Detectar si >10 consultas similares
        self.similar_query_window = 60  # Ventana de 60 segundos para detección
        
        # Estadísticas generales
        self.total_queries = 0
        self.total_slow_queries = 0
        self.total_n_plus_one = 0

    def start_query_tracking(self, sql_query: str, caller_info: str = None) -> str:
        """
        Inicia el tracking de una consulta.
        
        Args:
            sql_query: La consulta SQL
            caller_info: Información del caller (archivo:línea)
        
        Returns:
            query_id único para esta ejecución
        """
        query_id = f"{id(threading.current_thread())}_{time.time()}"
        
        with self._lock:
            self.active_queries[query_id] = time.time()
            self.total_queries += 1
        
        return query_id

    def end_query_tracking(self, query_id: str, sql_query: str, 
                          caller_info: str = None, error: bool = False):
        """
        Finaliza el tracking de una consulta y registra métricas.
        
        Args:
            query_id: ID de la consulta del start_tracking
            sql_query: La consulta SQL ejecutada
            caller_info: Información del caller
            error: Si la consulta terminó en error
        """
        if query_id not in self.active_queries:
            return
        
        start_time = self.active_queries.pop(query_id)
        execution_time = time.time() - start_time
        
        with self._lock:
            self._record_query_metrics(sql_query, execution_time, caller_info, error)
            self._detect_n_plus_one(sql_query, execution_time, caller_info)

    def _record_query_metrics(self, sql_query: str, execution_time: float, 
                             caller_info: str = None, error: bool = False):
        """Registra métricas de la consulta."""
        query_hash = self._normalize_and_hash_query(sql_query)
        
        if query_hash not in self.query_metrics:
            self.query_metrics[query_hash] = QueryMetrics(
                query_hash=query_hash,
                sql_query=sql_query
            )
        
        metrics = self.query_metrics[query_hash]
        metrics.execution_count += 1
        metrics.total_execution_time += execution_time
        metrics.avg_execution_time = metrics.total_execution_time / metrics.execution_count
        metrics.min_execution_time = min(metrics.min_execution_time, execution_time)
        metrics.max_execution_time = max(metrics.max_execution_time, execution_time)
        metrics.last_executed = datetime.now()
        
        if caller_info and caller_info not in metrics.caller_info:
            metrics.caller_info.append(caller_info)
        
        # Detectar consulta lenta
        if execution_time > self.slow_query_threshold:
            metrics.is_slow_query = True
            self.total_slow_queries += 1
            logger.warning(f"Consulta lenta detectada ({execution_time:.3f}s): {sql_query[:100]}...")

    def _normalize_and_hash_query(self, sql_query: str) -> str:
        """Normaliza y genera hash de consulta para detectar patrones."""
        import hashlib
        import re
        
        # Normalizar: convertir a minúsculas, eliminar espacios extra
        normalized = re.sub(r'\s+', ' ', sql_query.lower().strip())
        
        # Reemplazar valores literales con placeholders para detectar patrones
        # Números
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        # Strings entre comillas
        normalized = re.sub(r"'[^']*'", '?', normalized)
        normalized = re.sub(r'"[^"]*"', '?', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()

    def _detect_n_plus_one(self, sql_query: str, execution_time: float, caller_info: str = None):
        """Detecta problemas N+1 basado en patrones de consultas."""
        query_pattern = self._extract_query_pattern(sql_query)
        
        # Buscar consultas similares en ventana de tiempo reciente
        current_time = datetime.now()
        recent_queries = [
            metrics for metrics in self.query_metrics.values()
            if (current_time - metrics.last_executed).total_seconds() < self.similar_query_window
        ]
        
        similar_queries = [
            metrics for metrics in recent_queries
            if self._are_queries_similar_pattern(sql_query, metrics.sql_query)
        ]
        
        if len(similar_queries) >= self.n_plus_one_threshold:
            # Posible N+1 detectado
            pattern_hash = self._normalize_and_hash_query(query_pattern)
            
            # Verificar si ya fue detectado recientemente
            existing_detection = next(
                (d for d in self.n_plus_one_detections 
                 if d.pattern_hash == pattern_hash and 
                 (current_time - d.detected_at).total_seconds() < self.similar_query_window),
                None
            )
            
            if not existing_detection:
                severity = self._calculate_n_plus_one_severity(len(similar_queries), execution_time)
                
                detection = NPlusOneDetection(
                    pattern_hash=pattern_hash,
                    base_query=query_pattern,
                    related_queries=[m.sql_query for m in similar_queries[:5]],  # Solo primeras 5
                    execution_count=len(similar_queries),
                    detected_at=current_time,
                    severity=severity
                )
                
                self.n_plus_one_detections.append(detection)
                self.total_n_plus_one += 1
                
                logger.warning(f"Problema N+1 detectado: {len(similar_queries)} consultas similares")
                logger.warning(f"Patrón: {query_pattern[:100]}...")

    def _extract_query_pattern(self, sql_query: str) -> str:
        """Extrae el patrón base de una consulta SQL."""
        import re
        
        # Simplificar la consulta manteniendo estructura principal
        pattern = sql_query.lower()
        
        # Eliminar condiciones WHERE específicas pero mantener estructura
        pattern = re.sub(r'where\s+\w+\s*=\s*[?\'"][^\'"]*[?\'"]', 'where column = ?', pattern)
        pattern = re.sub(r'and\s+\w+\s*=\s*[?\'"][^\'"]*[?\'"]', 'and column = ?', pattern)
        pattern = re.sub(r'or\s+\w+\s*=\s*[?\'"][^\'"]*[?\'"]', 'or column = ?', pattern)
        
        return pattern

    def _are_queries_similar_pattern(self, query1: str, query2: str) -> bool:
        """Determina si dos consultas siguen un patrón similar."""
        pattern1 = self._extract_query_pattern(query1)
        pattern2 = self._extract_query_pattern(query2)
        
        # Comparar patrones normalizados
        return self._normalize_and_hash_query(pattern1) == self._normalize_and_hash_query(pattern2)

    def _calculate_n_plus_one_severity(self, query_count: int, avg_execution_time: float) -> str:
        """Calcula la severidad de un problema N+1."""
        if query_count > 100 or avg_execution_time > 2.0:
            return 'CRITICAL'
        elif query_count > 50 or avg_execution_time > 1.0:
            return 'HIGH'
        elif query_count > 20 or avg_execution_time > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Genera reporte completo de rendimiento.
        
        Returns:
            Dict con métricas y recomendaciones
        """
        with self._lock:
            # Consultas más lentas
            slowest_queries = sorted(
                [m for m in self.query_metrics.values() if m.is_slow_query],
                key=lambda x: x.max_execution_time,
                reverse=True
            )[:10]
            
            # Consultas más ejecutadas
            most_executed = sorted(
                self.query_metrics.values(),
                key=lambda x: x.execution_count,
                reverse=True
            )[:10]
            
            # Problemas N+1 recientes
            recent_n_plus_one = [
                d for d in self.n_plus_one_detections
                if (datetime.now() - d.detected_at).total_seconds() < 3600  # Última hora
            ]
            
            # Estadísticas generales
            avg_query_time = (
                sum(m.avg_execution_time for m in self.query_metrics.values()) /
                len(self.query_metrics) if self.query_metrics else 0
            )
            
            return {
                'summary': {
                    'total_queries_executed': self.total_queries,
                    'unique_query_patterns': len(self.query_metrics),
                    'slow_queries_detected': self.total_slow_queries,
                    'n_plus_one_issues': len(recent_n_plus_one),
                    'average_query_time': avg_query_time,
                    'slow_query_threshold': self.slow_query_threshold
                },
                'slowest_queries': [
                    {
                        'query': q.sql_query[:200] + '...' if len(q.sql_query) > 200 else q.sql_query,
                        'max_execution_time': q.max_execution_time,
                        'avg_execution_time': q.avg_execution_time,
                        'execution_count': q.execution_count,
                        'callers': q.caller_info
                    }
                    for q in slowest_queries
                ],
                'most_executed_queries': [
                    {
                        'query': q.sql_query[:200] + '...' if len(q.sql_query) > 200 else q.sql_query,
                        'execution_count': q.execution_count,
                        'total_time': q.total_execution_time,
                        'avg_time': q.avg_execution_time
                    }
                    for q in most_executed
                ],
                'n_plus_one_issues': [
                    {
                        'pattern': d.base_query[:200] + '...' if len(d.base_query) > 200 else d.base_query,
                        'execution_count': d.execution_count,
                        'severity': d.severity,
                        'detected_at': d.detected_at.isoformat(),
                        'sample_queries': d.related_queries[:3]
                    }
                    for d in recent_n_plus_one
                ],
                'recommendations': self._generate_recommendations()
            }

    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Recomendaciones para consultas lentas
        slow_queries_count = len([m for m in self.query_metrics.values() if m.is_slow_query])
        if slow_queries_count > 0:
            recommendations.append(f"Optimizar {slow_queries_count} consultas lentas identificadas")
            recommendations.append("Considerar agregar índices en columnas de filtro frecuentes")
        
        # Recomendaciones para N+1
        recent_n_plus_one = [
            d for d in self.n_plus_one_detections
            if (datetime.now() - d.detected_at).total_seconds() < 3600
        ]
        
        if recent_n_plus_one:
            recommendations.append(f"Resolver {len(recent_n_plus_one)} problemas N+1 detectados")
            recommendations.append("Implementar eager loading o consultas con JOIN")
        
        # Recomendaciones para consultas frecuentes
        frequent_queries = [m for m in self.query_metrics.values() if m.execution_count > 100]
        if frequent_queries:
            recommendations.append(f"Implementar caché para {len(frequent_queries)} consultas frecuentes")
        
        if not recommendations:
            recommendations.append("El rendimiento de las consultas está dentro de los parámetros normales")
        
        return recommendations

    def get_optimization_suggestions(self, query_hash: str) -> List[str]:
        """
        Obtiene sugerencias de optimización para una consulta específica.
        
        Args:
            query_hash: Hash de la consulta a optimizar
        
        Returns:
            Lista de sugerencias
        """
        if query_hash not in self.query_metrics:
            return ["Consulta no encontrada en métricas"]
        
        metrics = self.query_metrics[query_hash]
        suggestions = []
        
        if metrics.is_slow_query:
            suggestions.append("Analizar plan de ejecución de la consulta")
            suggestions.append("Verificar índices en columnas de WHERE y JOIN")
            suggestions.append("Considerar reescribir la consulta con subconsultas o CTEs")
        
        if metrics.execution_count > 50:
            suggestions.append("Implementar caché para esta consulta frecuente")
            suggestions.append("Considerar materializar resultados si los datos cambian poco")
        
        if metrics.is_n_plus_one:
            suggestions.append("Reemplazar múltiples consultas con una sola consulta JOIN")
            suggestions.append("Implementar eager loading para relaciones")
        
        return suggestions or ["No se detectaron problemas específicos para optimización"]

    def clear_old_metrics(self, days_to_keep: int = 7):
        """
        Limpia métricas antiguas para evitar acumulación de memoria.
        
        Args:
            days_to_keep: Días de métricas a mantener
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            # Limpiar métricas antiguas
            old_hashes = [
                hash_key for hash_key, metrics in self.query_metrics.items()
                if metrics.last_executed < cutoff_date
            ]
            
            for hash_key in old_hashes:
                del self.query_metrics[hash_key]
            
            # Limpiar detecciones N+1 antiguas
            self.n_plus_one_detections = [
                d for d in self.n_plus_one_detections
                if d.detected_at > cutoff_date
            ]
            
            logger.info(f"Limpiadas {len(old_hashes)} métricas antiguas")


# Instancia global del analizador
_global_analyzer = QueryPerformanceAnalyzer()


def query_performance_decorator(func):
    """
    Decorador para analizar automáticamente el rendimiento de funciones que ejecutan consultas.
    
    Usage:
        @query_performance_decorator
        def obtener_productos():
            cursor.execute("SELECT * FROM productos")
            return cursor.fetchall()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extraer información del caller
        import inspect
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        
        # Iniciar tracking
        query_id = _global_analyzer.start_query_tracking("", caller_info)
        
        try:
            result = func(*args, **kwargs)
            _global_analyzer.end_query_tracking(query_id, "", caller_info, error=False)
            return result
        except Exception as e:
            _global_analyzer.end_query_tracking(query_id, "", caller_info, error=True)
            raise
    
    return wrapper


def track_sql_query(sql_query: str, execution_time: float, caller_info: str = None):
    """
    Función de conveniencia para trackear una consulta SQL manualmente.
    
    Args:
        sql_query: La consulta SQL ejecutada
        execution_time: Tiempo de ejecución en segundos
        caller_info: Información del caller
    """
    _global_analyzer._record_query_metrics(sql_query, execution_time, caller_info)


def get_performance_report() -> Dict[str, Any]:
    """Obtiene el reporte de rendimiento global."""
    return _global_analyzer.get_performance_report()


def clear_performance_metrics():
    """Limpia todas las métricas de rendimiento."""
    _global_analyzer.query_metrics.clear()
    _global_analyzer.n_plus_one_detections.clear()
    _global_analyzer.total_queries = 0
    _global_analyzer.total_slow_queries = 0
    _global_analyzer.total_n_plus_one = 0


# Ejemplo de uso:
"""
# En modelo que ejecuta consultas:
from rexus.utils.query_performance_analyzer import track_sql_query

def obtener_productos():
    start_time = time.time()
    cursor.execute(, (categoria,))
    execution_time = time.time() - start_time
    
    # Trackear la consulta
    track_sql_query(
        "SELECT * FROM productos WHERE categoria = ?", 
        execution_time, 
        "inventario/model.py:obtener_productos"
    )
    
    return cursor.fetchall()

# Para generar reporte:
report = get_performance_report()
logger.info(f"Consultas ejecutadas: {report['summary']['total_queries_executed']}")
logger.info(f"Problemas N+1: {report['summary']['n_plus_one_issues']}")
"""