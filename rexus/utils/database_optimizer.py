"""
Optimizador de Base de Datos - Sistema Inteligente de Optimización
Proporciona herramientas avanzadas para optimizar el rendimiento de la base de datos

Fecha: 23/08/2025
"""

import sqlite3
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import json

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    query: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    database: str

@dataclass
class IndexSuggestion:
    table: str
    columns: List[str]
    reason: str
    estimated_improvement: float

class DatabaseOptimizer:
    """Optimizador inteligente de base de datos."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path("rexus.db")
        self.metrics_db = Path("db_optimization_metrics.db")
        self.query_log = []
        self.optimization_history = []
        self.init_metrics_db()
        
    def init_metrics_db(self):
        """Inicializa la base de datos de métricas."""
        try:
            with sqlite3.connect(str(self.metrics_db)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS query_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        execution_time REAL NOT NULL,
                        rows_affected INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        database_name TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_type TEXT NOT NULL,
                        table_name TEXT,
                        details TEXT,
                        performance_gain REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS table_stats (
                        table_name TEXT PRIMARY KEY,
                        row_count INTEGER,
                        avg_query_time REAL,
                        most_frequent_queries TEXT,
                        last_analyzed DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Base de datos de métricas inicializada correctamente")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos de métricas: {e}")
            
    def analyze_database_performance(self) -> Dict[str, Any]:
        """Analiza el rendimiento actual de la base de datos."""
        analysis = {
            'database_size': 0,
            'table_count': 0,
            'index_count': 0,
            'slow_queries': [],
            'table_statistics': {},
            'recommendations': []
        }
        
        try:
            if not self.db_path.exists():
                logger.warning(f"Base de datos no encontrada: {self.db_path}")
                return analysis
                
            with sqlite3.connect(str(self.db_path)) as conn:
                # Tamaño de la base de datos
                analysis['database_size'] = self.db_path.stat().st_size / (1024 * 1024)  # MB
                
                # Contar tablas
                cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                analysis['table_count'] = cursor.fetchone()[0]
                
                # Contar índices
                cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
                analysis['index_count'] = cursor.fetchone()[0]
                
                # Estadísticas de tablas
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    try:
                        # Contar filas
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]
                        
                        # Información de la tabla
                        cursor = conn.execute(f"PRAGMA table_info({table})")
                        columns = cursor.fetchall()
                        
                        analysis['table_statistics'][table] = {
                            'row_count': row_count,
                            'column_count': len(columns),
                            'columns': [col[1] for col in columns]
                        }
                        
                    except Exception as e:
                        logger.warning(f"Error analizando tabla {table}: {e}")
                        
                # Generar recomendaciones
                analysis['recommendations'] = self._generate_recommendations(analysis)
                
                logger.info(f"Análisis completado: {analysis['table_count']} tablas, {analysis['database_size']:.2f}MB")
                
        except Exception as e:
            logger.error(f"Error analizando base de datos: {e}")
            
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de optimización."""
        recommendations = []
        
        # Recomendación por tamaño
        if analysis['database_size'] > 100:  # MB
            recommendations.append("Base de datos grande (>100MB): Considerar particionado de tablas")
            
        # Recomendación por número de tablas
        if analysis['table_count'] > 50:
            recommendations.append("Muchas tablas detectadas: Revisar normalización")
            
        # Recomendaciones específicas por tabla
        for table, stats in analysis['table_statistics'].items():
            if stats['row_count'] > 10000 and stats['row_count'] / max(analysis['index_count'], 1) > 5000:
                recommendations.append(f"Tabla '{table}': Considerar añadir índices (>{stats['row_count']} filas)")
                
        if not recommendations:
            recommendations.append("Base de datos en buen estado, sin optimizaciones críticas necesarias")
            
        return recommendations
    
    def create_performance_indexes(self) -> Dict[str, Any]:
        """Crea índices para mejorar el rendimiento."""
        results = {
            'indexes_created': 0,
            'indexes_failed': 0,
            'details': []
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Índices sugeridos basados en patrones comunes
                suggested_indexes = [
                    ("idx_users_username", "usuarios", ["username"]),
                    ("idx_users_email", "usuarios", ["email"]),
                    ("idx_inventario_codigo", "inventario", ["codigo"]),
                    ("idx_obras_fecha", "obras", ["fecha_inicio"]),
                    ("idx_compras_fecha", "compras", ["fecha"]),
                    ("idx_pedidos_estado", "pedidos", ["estado"]),
                    ("idx_notificaciones_usuario", "notificaciones", ["usuario_id"]),
                    ("idx_log_timestamp", "system_logs", ["timestamp"])
                ]
                
                for index_name, table_name, columns in suggested_indexes:
                    try:
                        # Verificar si la tabla existe
                        cursor = conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                            (table_name,)
                        )
                        if not cursor.fetchone():
                            continue
                            
                        # Verificar si el índice ya existe
                        cursor = conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='index' AND name=?", 
                            (index_name,)
                        )
                        if cursor.fetchone():
                            continue
                            
                        # Crear índice
                        columns_str = ", ".join(columns)
                        query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
                        
                        start_time = time.time()
                        conn.execute(query)
                        execution_time = time.time() - start_time
                        
                        results['indexes_created'] += 1
                        results['details'].append({
                            'index': index_name,
                            'table': table_name,
                            'columns': columns,
                            'time': execution_time,
                            'status': 'created'
                        })
                        
                        logger.info(f"Índice creado: {index_name} en {table_name}")
                        
                    except Exception as e:
                        results['indexes_failed'] += 1
                        results['details'].append({
                            'index': index_name,
                            'table': table_name,
                            'error': str(e),
                            'status': 'failed'
                        })
                        logger.warning(f"Error creando índice {index_name}: {e}")
                        
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error creando índices de rendimiento: {e}")
            
        return results
    
    def vacuum_and_analyze(self) -> Dict[str, Any]:
        """Ejecuta VACUUM y ANALYZE para optimizar la base de datos."""
        results = {
            'vacuum_completed': False,
            'analyze_completed': False,
            'size_before': 0,
            'size_after': 0,
            'time_taken': 0
        }
        
        try:
            if not self.db_path.exists():
                logger.warning("Base de datos no encontrada para optimización")
                return results
                
            start_time = time.time()
            results['size_before'] = self.db_path.stat().st_size
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # VACUUM para desfragmentar
                logger.info("Ejecutando VACUUM...")
                conn.execute("VACUUM")
                results['vacuum_completed'] = True
                
                # ANALYZE para actualizar estadísticas
                logger.info("Ejecutando ANALYZE...")
                conn.execute("ANALYZE")
                results['analyze_completed'] = True
                
            results['size_after'] = self.db_path.stat().st_size
            results['time_taken'] = time.time() - start_time
            
            size_saved = results['size_before'] - results['size_after']
            logger.info(f"Optimización completada en {results['time_taken']:.2f}s")
            logger.info(f"Espacio liberado: {size_saved / 1024:.2f} KB")
            
            # Registrar optimización
            self._log_optimization_action(
                "vacuum_analyze", 
                None, 
                f"Size reduction: {size_saved} bytes",
                size_saved / max(results['size_before'], 1) * 100
            )
            
        except Exception as e:
            logger.error(f"Error en optimización VACUUM/ANALYZE: {e}")
            
        return results
    
    def monitor_slow_queries(self, threshold_seconds: float = 1.0) -> List[QueryMetrics]:
        """Monitorea y registra consultas lentas."""
        slow_queries = []
        
        try:
            with sqlite3.connect(str(self.metrics_db)) as conn:
                cursor = conn.execute("""
                    SELECT query, execution_time, rows_affected, timestamp, database_name
                    FROM query_metrics 
                    WHERE execution_time > ? 
                    ORDER BY execution_time DESC 
                    LIMIT 50
                """, (threshold_seconds,))
                
                for row in cursor.fetchall():
                    slow_queries.append(QueryMetrics(
                        query=row[0],
                        execution_time=row[1],
                        rows_affected=row[2] or 0,
                        timestamp=datetime.fromisoformat(row[3]),
                        database=row[4] or "unknown"
                    ))
                    
        except Exception as e:
            logger.error(f"Error monitoreando consultas lentas: {e}")
            
        return slow_queries
    
    def log_query_performance(self, query: str, execution_time: float, rows_affected: int = 0):
        """Registra el rendimiento de una consulta."""
        try:
            with sqlite3.connect(str(self.metrics_db)) as conn:
                conn.execute("""
                    INSERT INTO query_metrics (query, execution_time, rows_affected, database_name)
                    VALUES (?, ?, ?, ?)
                """, (query[:500], execution_time, rows_affected, str(self.db_path.name)))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error registrando métricas de consulta: {e}")
    
    def _log_optimization_action(self, action_type: str, table_name: Optional[str], 
                                details: str, performance_gain: float = 0.0):
        """Registra una acción de optimización."""
        try:
            with sqlite3.connect(str(self.metrics_db)) as conn:
                conn.execute("""
                    INSERT INTO optimization_actions (action_type, table_name, details, performance_gain)
                    VALUES (?, ?, ?, ?)
                """, (action_type, table_name, details, performance_gain))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error registrando acción de optimización: {e}")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Genera un reporte completo de optimización."""
        report = {
            'database_analysis': self.analyze_database_performance(),
            'slow_queries': self.monitor_slow_queries(),
            'optimization_history': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with sqlite3.connect(str(self.metrics_db)) as conn:
                # Historial de optimizaciones
                cursor = conn.execute("""
                    SELECT action_type, table_name, details, performance_gain, timestamp
                    FROM optimization_actions 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                """)
                
                for row in cursor.fetchall():
                    report['optimization_history'].append({
                        'action': row[0],
                        'table': row[1],
                        'details': row[2],
                        'gain': row[3],
                        'timestamp': row[4]
                    })
                    
        except Exception as e:
            logger.error(f"Error generando reporte de optimización: {e}")
            
        return report
    
    def auto_optimize(self, create_indexes: bool = True, vacuum_analyze: bool = True) -> Dict[str, Any]:
        """Ejecuta optimización automática completa."""
        optimization_results = {
            'started_at': datetime.now().isoformat(),
            'indexes_result': {},
            'vacuum_result': {},
            'total_time': 0,
            'success': False
        }
        
        start_time = time.time()
        
        try:
            logger.info("Iniciando optimización automática de base de datos")
            
            # Crear índices de rendimiento
            if create_indexes:
                logger.info("Creando índices de rendimiento...")
                optimization_results['indexes_result'] = self.create_performance_indexes()
                
            # VACUUM y ANALYZE
            if vacuum_analyze:
                logger.info("Ejecutando VACUUM y ANALYZE...")
                optimization_results['vacuum_result'] = self.vacuum_and_analyze()
                
            optimization_results['total_time'] = time.time() - start_time
            optimization_results['success'] = True
            optimization_results['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"Optimización automática completada en {optimization_results['total_time']:.2f}s")
            
        except Exception as e:
            optimization_results['error'] = str(e)
            optimization_results['total_time'] = time.time() - start_time
            logger.error(f"Error en optimización automática: {e}")
            
        return optimization_results

class QueryProfiler:
    """Profiler para analizar y optimizar consultas SQL."""
    
    def __init__(self, optimizer: DatabaseOptimizer):
        self.optimizer = optimizer
        
    def profile_query(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """Perfila una consulta específica."""
        profile_result = {
            'query': query,
            'execution_time': 0,
            'explain_plan': [],
            'suggestions': []
        }
        
        try:
            with sqlite3.connect(str(self.optimizer.db_path)) as conn:
                # Ejecutar EXPLAIN QUERY PLAN
                explain_cursor = conn.execute(f"EXPLAIN QUERY PLAN {query}", params)
                profile_result['explain_plan'] = explain_cursor.fetchall()
                
                # Medir tiempo de ejecución
                start_time = time.time()
                cursor = conn.execute(query, params)
                cursor.fetchall()  # Asegurar ejecución completa
                profile_result['execution_time'] = time.time() - start_time
                
                # Generar sugerencias
                profile_result['suggestions'] = self._analyze_query_plan(
                    profile_result['explain_plan'], query
                )
                
        except Exception as e:
            profile_result['error'] = str(e)
            logger.error(f"Error perfilando consulta: {e}")
            
        return profile_result
    
    def _analyze_query_plan(self, explain_plan: List, query: str) -> List[str]:
        """Analiza el plan de ejecución y sugiere optimizaciones."""
        suggestions = []
        
        for row in explain_plan:
            detail = str(row).lower()
            
            if 'scan table' in detail and 'using index' not in detail:
                table_name = self._extract_table_name(detail)
                suggestions.append(f"Considerar agregar índice a la tabla '{table_name}'")
                
            if 'temp b-tree' in detail:
                suggestions.append("Consulta requiere ordenamiento temporal - considerar índice para ORDER BY")
                
            if 'nested loop' in detail:
                suggestions.append("Join anidado detectado - verificar índices en claves foráneas")
                
        if not suggestions:
            suggestions.append("Plan de ejecución eficiente")
            
        return suggestions
    
    def _extract_table_name(self, detail: str) -> str:
        """Extrae el nombre de tabla del detalle del plan."""
        try:
            words = detail.split()
            table_idx = words.index('table') + 1
            return words[table_idx] if table_idx < len(words) else "unknown"
        except (ValueError, IndexError):
            return "unknown"

# Instancia global del optimizador
_optimizer_instance = None

def get_database_optimizer(db_path: Optional[str] = None) -> DatabaseOptimizer:
    """Obtiene la instancia global del optimizador."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = DatabaseOptimizer(db_path)
    return _optimizer_instance

if __name__ == "__main__":
    # Test del optimizador
    optimizer = DatabaseOptimizer()
    
    print("=== Análisis de Base de Datos ===")
    analysis = optimizer.analyze_database_performance()
    print(f"Tablas: {analysis['table_count']}")
    print(f"Tamaño: {analysis['database_size']:.2f} MB")
    print(f"Índices: {analysis['index_count']}")
    
    print("\n=== Recomendaciones ===")
    for rec in analysis['recommendations']:
        print(f"- {rec}")
    
    print("\n=== Optimización Automática ===")
    result = optimizer.auto_optimize()
    print(f"Completada en: {result['total_time']:.2f}s")
    print(f"Éxito: {result['success']}")