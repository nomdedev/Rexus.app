"""
Optimizador de Base de Datos SQL Server - Rexus.app v2.0.0

Sistema inteligente de optimización para SQL Server.
Proporciona análisis de rendimiento, sugerencias de índices, 
monitoreo de consultas lentas y optimización automática.

Características:
- Análisis de rendimiento de bases de datos SQL Server
- Sugerencias inteligentes de índices
- Monitoreo de consultas lentas
- Optimización automática de estadísticas
- Métricas de rendimiento históricas
- Perfilado de consultas con planes de ejecución

Fecha: 26/08/2025
Autor: Sistema Rexus
"""

import logging
import pyodbc
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import json
import time
import os

# Importar configuración de BD
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader
    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader
        def get_query(self, path, filename):
            return self.sql_loader.load_script(filename)

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Métricas de rendimiento de consultas."""
    query: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    database: str
    cpu_time: float = 0.0
    logical_reads: int = 0
    physical_reads: int = 0
    plan_hash: str = ""

@dataclass
class IndexSuggestion:
    """Sugerencia de índice para optimización."""
    table: str
    columns: List[str]
    reason: str
    estimated_improvement: float
    index_type: str = "NONCLUSTERED"
    include_columns: List[str] = field(default_factory=list)
    estimated_size_mb: float = 0.0

@dataclass
class DatabaseStats:
    """Estadísticas generales de la base de datos."""
    database_name: str
    size_mb: float
    table_count: int
    index_count: int
    used_space_mb: float
    free_space_mb: float
    fragmentation_avg: float
    last_backup: Optional[datetime] = None

class DatabaseOptimizer:
    """Optimizador inteligente para SQL Server."""
    
    def __init__(self, db_connection=None, connection_string: Optional[str] = None):
        """
        Inicializa el optimizador de SQL Server.
        
        Args:
            db_connection: Conexión existente a SQL Server
            connection_string: String de conexión para crear nueva conexión
        """
        self.db_connection = db_connection
        self.connection_string = connection_string
        self.sql_manager = SQLQueryManager()
        self.query_log: List[QueryMetrics] = []
        self.optimization_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        
        # Configuración por defecto
        self.slow_query_threshold = 1.0  # segundos
        self.max_query_log_size = 1000
        self.enable_auto_stats = True
        
        logger.info("DatabaseOptimizer para SQL Server inicializado")

    def _get_connection(self) -> Optional[pyodbc.Connection]:
        """Obtiene una conexión a SQL Server."""
        if self.db_connection:
            return self.db_connection
        
        if self.connection_string:
            try:
                return pyodbc.connect(self.connection_string)
            except Exception as e:
                logger.error(f"Error conectando a SQL Server: {e}")
                return None
        
        # Intentar usar variables de entorno
        try:
            server = os.getenv('DB_SERVER', 'localhost')
            database = os.getenv('DB_NAME', 'rexus')
            username = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            
            if username and password:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
            
            return pyodbc.connect(conn_str)
        except Exception as e:
            logger.error(f"Error conectando con variables de entorno: {e}")
            return None

    def init_metrics_db(self) -> bool:
        """
        Inicializa las tablas de métricas en SQL Server.
        
        Returns:
            True si se inicializó correctamente
        """
        try:
            conn = self._get_connection()
            if not conn:
                logger.error("No se pudo obtener conexión para inicializar métricas")
                return False
            
            cursor = conn.cursor()
            
            # Crear tabla de métricas de consultas usando SQL externalizado
            sql_create_metrics = self.sql_manager.get_query('optimizer', 'create_query_metrics_table')
            cursor.execute(sql_create_metrics)
            
            # Crear tabla de acciones de optimización usando SQL externalizado
            sql_create_actions = self.sql_manager.get_query('optimizer', 'create_optimization_actions_table')
            cursor.execute(sql_create_actions)
            
            conn.commit()
            logger.info("Tablas de métricas de SQL Server inicializadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando métricas de SQL Server: {e}")
            return False
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()

    def analyze_database_performance(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analiza el rendimiento actual de la base de datos SQL Server.
        
        Args:
            database_name: Nombre de la base de datos a analizar
            
        Returns:
            Diccionario con estadísticas de rendimiento
        """
        analysis = {
            'databases': [],
            'total_size_mb': 0,
            'table_count': 0,
            'index_count': 0,
            'fragmented_indexes': [],
            'missing_indexes': [],
            'slow_queries': [],
            'recommendations': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        try:
            conn = self._get_connection()
            if not conn:
                logger.error("No se pudo obtener conexión para análisis")
                return analysis
            
            cursor = conn.cursor()
            
            # Obtener información de bases de datos
            if database_name:
                sql_check_db = self.sql_manager.get_query('optimizer', 'check_database_exists')
                cursor.execute(sql_check_db, (database_name,))
                databases = [database_name] if cursor.fetchone() else []
            else:
                sql_get_dbs = self.sql_manager.get_query('optimizer', 'get_user_databases')
                cursor.execute(sql_get_dbs)
                databases = [row[0] for row in cursor.fetchall()]
            
            for db_name in databases:
                db_stats = self._analyze_single_database(cursor, db_name)
                if db_stats:
                    analysis['databases'].append(db_stats)
                    analysis['total_size_mb'] += db_stats.size_mb
                    analysis['table_count'] += db_stats.table_count
                    analysis['index_count'] += db_stats.index_count
            
            # Obtener índices fragmentados
            analysis['fragmented_indexes'] = self._get_fragmented_indexes(cursor)
            
            # Obtener sugerencias de índices faltantes
            analysis['missing_indexes'] = self._get_missing_indexes(cursor)
            
            # Obtener consultas lentas recientes
            analysis['slow_queries'] = self._get_slow_queries(cursor)
            
            # Generar recomendaciones
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            logger.info(f"Análisis de rendimiento completado para {len(databases)} base(s) de datos")
            
        except Exception as e:
            logger.error(f"Error analizando rendimiento: {e}")
            analysis['error'] = str(e)
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return analysis

    def _analyze_single_database(self, cursor: pyodbc.Cursor, db_name: str) -> Optional[DatabaseStats]:
        """Analiza una base de datos específica."""
        try:
            # Cambiar contexto a la base de datos
            cursor.execute(f"USE [{db_name}]")
            
            # Obtener tamaño de la base de datos
            sql_get_size = self.sql_manager.get_query('optimizer', 'get_database_size')
            cursor.execute(sql_get_size)
            size_result = cursor.fetchone()
            used_mb = size_result[0] if size_result and size_result[0] else 0
            total_mb = size_result[1] if size_result and size_result[1] else 0
            
            # Obtener número de tablas
            sql_count_tables = self.sql_manager.get_query('optimizer', 'count_user_tables')
            cursor.execute(sql_count_tables)
            table_result = cursor.fetchone()
            table_count = table_result[0] if table_result else 0
            
            # Obtener número de índices
            sql_count_indexes = self.sql_manager.get_query('optimizer', 'count_indexes')
            cursor.execute(sql_count_indexes)
            index_result = cursor.fetchone()
            index_count = index_result[0] if index_result else 0
            
            # Obtener fragmentación promedio
            sql_get_fragmentation = self.sql_manager.get_query('optimizer', 'get_average_fragmentation')
            cursor.execute(sql_get_fragmentation)
            fragmentation_result = cursor.fetchone()
            fragmentation_avg = fragmentation_result[0] if fragmentation_result and fragmentation_result[0] else 0
            
            return DatabaseStats(
                database_name=db_name,
                size_mb=total_mb,
                table_count=table_count,
                index_count=index_count,
                used_space_mb=used_mb,
                free_space_mb=total_mb - used_mb,
                fragmentation_avg=fragmentation_avg
            )
            
        except Exception as e:
            logger.error(f"Error analizando base de datos {db_name}: {e}")
            return None

    def _get_fragmented_indexes(self, cursor: pyodbc.Cursor) -> List[Dict[str, Any]]:
        """Obtiene índices con alta fragmentación."""
        try:
            sql_get_fragmented = self.sql_manager.get_query('optimizer', 'get_fragmented_indexes')
            cursor.execute(sql_get_fragmented)
            
            return [
                {
                    'schema': row[0],
                    'table': row[1],
                    'index': row[2],
                    'fragmentation_percent': round(row[3], 2),
                    'page_count': row[4]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error obteniendo índices fragmentados: {e}")
            return []

    def _get_missing_indexes(self, cursor: pyodbc.Cursor) -> List[IndexSuggestion]:
        """Obtiene sugerencias de índices faltantes."""
        try:
            sql_get_missing = self.sql_manager.get_query('optimizer', 'get_missing_indexes')
            cursor.execute(sql_get_missing)
            
            suggestions = []
            for row in cursor.fetchall():
                table_full = f"{row[0]}.{row[1]}"
                key_cols = [col.strip() for col in row[5].split(',') if col.strip()]
                include_cols = [col.strip() for col in row[6].split(',') if col.strip()]
                
                suggestions.append(IndexSuggestion(
                    table=table_full,
                    columns=key_cols,
                    reason=f"Missing index with {row[4]:.1f}% improvement potential",
                    estimated_improvement=row[4],
                    index_type="NONCLUSTERED",
                    include_columns=include_cols
                ))
            
            return suggestions
        except Exception as e:
            logger.error(f"Error obteniendo índices faltantes: {e}")
            return []

    def _get_slow_queries(self, cursor: pyodbc.Cursor) -> List[QueryMetrics]:
        """Obtiene consultas lentas recientes."""
        try:
            sql_get_slow_queries = self.sql_manager.get_query('optimizer', 'get_slow_queries')
            cursor.execute(sql_get_slow_queries, (self.slow_query_threshold * 1000000,))  # Convertir a microsegundos
            
            slow_queries = []
            for row in cursor.fetchall():
                # Obtener nombre de la base de datos actual
                sql_get_current_db = self.sql_manager.get_query('optimizer', 'get_current_database_name')
                cursor.execute(sql_get_current_db)
                current_db_result = cursor.fetchone()
                current_db = current_db_result[0] if current_db_result else "Unknown"
                
                slow_queries.append(QueryMetrics(
                    query=row[6][:500] + "..." if len(row[6]) > 500 else row[6],
                    execution_time=row[1] / 1000000.0,  # Convertir a segundos
                    rows_affected=0,
                    timestamp=row[5],
                    database=current_db,
                    logical_reads=row[3],
                    physical_reads=row[4]
                ))
            
            return slow_queries
        except Exception as e:
            logger.error(f"Error obteniendo consultas lentas: {e}")
            return []

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Recomendaciones basadas en fragmentación
        if analysis['fragmented_indexes']:
            high_frag = len([idx for idx in analysis['fragmented_indexes'] 
                           if idx['fragmentation_percent'] > 50])
            if high_frag > 0:
                recommendations.append(
                    f"Reorganizar o reconstruir {high_frag} índice(s) con alta fragmentación (>50%)"
                )
        
        # Recomendaciones basadas en índices faltantes
        if analysis['missing_indexes']:
            high_impact = len([idx for idx in analysis['missing_indexes'] 
                             if idx.estimated_improvement > 50])
            if high_impact > 0:
                recommendations.append(
                    f"Crear {high_impact} índice(s) con alto impacto potencial (>50% mejora)"
                )
        
        # Recomendaciones basadas en consultas lentas
        if analysis['slow_queries']:
            recommendations.append(
                f"Optimizar {len(analysis['slow_queries'])} consulta(s) lenta(s) identificada(s)"
            )
        
        # Recomendaciones basadas en tamaño
        if analysis['total_size_mb'] > 10240:  # 10GB
            recommendations.append(
                "Considerar particionamiento de tablas grandes o archivado de datos históricos"
            )
        
        return recommendations

    def create_performance_indexes(self, execute: bool = False) -> Dict[str, Any]:
        """
        Crea índices para mejorar el rendimiento.
        
        Args:
            execute: Si True, ejecuta las creaciones. Si False, solo genera scripts.
            
        Returns:
            Resultado de la operación
        """
        result = {
            'success': False,
            'indexes_created': 0,
            'indexes_failed': 0,
            'scripts_generated': [],
            'errors': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            conn = self._get_connection()
            if not conn:
                result['errors'].append("No se pudo obtener conexión")
                return result
            
            cursor = conn.cursor()
            
            # Obtener sugerencias de índices
            missing_indexes = self._get_missing_indexes(cursor)
            
            for suggestion in missing_indexes[:5]:  # Limitar a 5 índices por ejecución
                try:
                    # Generar script de creación
                    cols_str = ', '.join([f"[{col}]" for col in suggestion.columns])
                    include_str = ""
                    if suggestion.include_columns:
                        include_cols = ', '.join([f"[{col}]" for col in suggestion.include_columns])
                        include_str = f" INCLUDE ({include_cols})"
                    
                    index_name = f"IX_{suggestion.table.replace('.', '_')}_auto_{int(time.time())}"
                    create_script = f"""
                        CREATE NONCLUSTERED INDEX [{index_name}] 
                        ON [{suggestion.table}] ({cols_str}){include_str}
                        WITH (ONLINE = ON, FILLFACTOR = 90)
                    """
                    
                    result['scripts_generated'].append(create_script)
                    
                    if execute:
                        cursor.execute(create_script)
                        result['indexes_created'] += 1
                        logger.info(f"Índice creado: {index_name}")
                        
                        # Log de la acción
                        self._log_optimization_action(
                            "CREATE_INDEX",
                            suggestion.table,
                            f"Index: {index_name}, Columns: {cols_str}",
                            True,
                            time.time() - start_time
                        )
                
                except Exception as e:
                    error_msg = f"Error creando índice para {suggestion.table}: {e}"
                    result['errors'].append(error_msg)
                    result['indexes_failed'] += 1
                    logger.error(error_msg)
            
            if execute:
                conn.commit()
            
            result['success'] = result['indexes_failed'] == 0
            
        except Exception as e:
            result['errors'].append(f"Error general: {e}")
            logger.error(f"Error en create_performance_indexes: {e}")
        finally:
            result['execution_time'] = time.time() - start_time
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return result

    def vacuum_and_analyze(self) -> Dict[str, Any]:
        """
        Actualiza estadísticas de las tablas (equivalente a VACUUM ANALYZE en PostgreSQL).
        
        Returns:
            Resultado de la operación
        """
        result = {
            'success': False,
            'tables_updated': 0,
            'tables_failed': 0,
            'execution_time': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            conn = self._get_connection()
            if not conn:
                result['errors'].append("No se pudo obtener conexión")
                return result
            
            cursor = conn.cursor()
            
            # Obtener todas las tablas de usuario
            sql_get_tables = self.sql_manager.get_query('optimizer', 'get_user_tables_for_stats')
            cursor.execute(sql_get_tables)
            
            tables = cursor.fetchall()
            
            for schema_name, table_name in tables:
                try:
                    # Actualizar estadísticas de la tabla
                    full_table_name = f"[{schema_name}].[{table_name}]"
                    cursor.execute(f"UPDATE STATISTICS {full_table_name} WITH FULLSCAN")
                    result['tables_updated'] += 1
                    
                    logger.debug(f"Estadísticas actualizadas para {full_table_name}")
                    
                except Exception as e:
                    error_msg = f"Error actualizando estadísticas de {schema_name}.{table_name}: {e}"
                    result['errors'].append(error_msg)
                    result['tables_failed'] += 1
                    logger.error(error_msg)
            
            # Log de la acción
            if result['tables_updated'] > 0:
                self._log_optimization_action(
                    "UPDATE_STATISTICS",
                    None,
                    f"Updated {result['tables_updated']} tables",
                    result['tables_failed'] == 0,
                    time.time() - start_time
                )
            
            result['success'] = result['tables_failed'] == 0
            
        except Exception as e:
            result['errors'].append(f"Error general: {e}")
            logger.error(f"Error en vacuum_and_analyze: {e}")
        finally:
            result['execution_time'] = time.time() - start_time
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return result

    def create_performance_indexes(self, execute: bool = False) -> Dict[str, Any]:
        """
        Crea índices de rendimiento basados en las sugerencias del sistema.
        
        Args:
            execute: Si ejecutar realmente las creaciones de índices
            
        Returns:
            Resultado de la operación
        """
        result = {
            'success': False,
            'indexes_created': 0,
            'indexes_failed': 0,
            'suggested_indexes': [],
            'execution_time': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            conn = self._get_connection()
            if not conn:
                result['errors'].append("No se pudo obtener conexión")
                return result
            
            cursor = conn.cursor()
            
            # Obtener sugerencias de índices
            missing_indexes = self._get_missing_indexes(cursor)
            
            for suggestion in missing_indexes:
                try:
                    # Crear nombre único para el índice
                    table_parts = suggestion.table.split('.')
                    if len(table_parts) == 2:
                        schema, table = table_parts
                    else:
                        schema, table = 'dbo', suggestion.table
                    
                    index_name = f"IX_{table}_Performance_{result['indexes_created'] + 1}"
                    columns = ', '.join(f"[{col}]" for col in suggestion.columns)
                    
                    create_sql = f"CREATE NONCLUSTERED INDEX [{index_name}] ON [{schema}].[{table}] ({columns})"
                    
                    if suggestion.include_columns:
                        include_cols = ', '.join(f"[{col}]" for col in suggestion.include_columns)
                        create_sql += f" INCLUDE ({include_cols})"
                    
                    result['suggested_indexes'].append({
                        'table': suggestion.table,
                        'index_name': index_name,
                        'sql': create_sql,
                        'estimated_improvement': suggestion.estimated_improvement
                    })
                    
                    if execute:
                        cursor.execute(create_sql)
                        result['indexes_created'] += 1
                        logger.info(f"Índice creado: {index_name} en {suggestion.table}")
                        
                        # Log de la acción
                        self._log_optimization_action(
                            "CREATE_INDEX",
                            suggestion.table,
                            f"Created index {index_name}",
                            True,
                            time.time() - start_time
                        )
                    
                except Exception as e:
                    error_msg = f"Error creando índice en {suggestion.table}: {e}"
                    result['errors'].append(error_msg)
                    result['indexes_failed'] += 1
                    logger.error(error_msg)
            
            result['success'] = result['indexes_failed'] == 0
            
        except Exception as e:
            result['errors'].append(f"Error general: {e}")
            logger.error(f"Error en create_performance_indexes: {e}")
        finally:
            result['execution_time'] = time.time() - start_time
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return result

    def monitor_slow_queries(self, threshold_seconds: float = 1.0) -> List[QueryMetrics]:
        """
        Monitorea consultas lentas en SQL Server.
        
        Args:
            threshold_seconds: Umbral en segundos para considerar una consulta lenta
            
        Returns:
            Lista de métricas de consultas lentas
        """
        try:
            conn = self._get_connection()
            if not conn:
                logger.error("No se pudo obtener conexión para monitoreo")
                return []
            
            cursor = conn.cursor()
            
            # Consultar estadísticas de consultas
            sql_get_performance_stats = self.sql_manager.get_query('optimizer', 'get_query_performance_stats')
            cursor.execute(sql_get_performance_stats, (threshold_seconds * 1000000,))  # Convertir a microsegundos
            
            slow_queries = []
            
            # Obtener nombre de la base de datos actual
            sql_get_current_db = self.sql_manager.get_query('optimizer', 'get_current_database_name')
            cursor.execute(sql_get_current_db)
            current_db_result = cursor.fetchone()
            current_db = current_db_result[0] if current_db_result else "Unknown"
            
            for row in cursor.fetchall():
                query_metric = QueryMetrics(
                    query=row[6][:1000] + "..." if len(row[6]) > 1000 else row[6],
                    execution_time=row[0] / 1000000.0,  # Convertir a segundos
                    rows_affected=0,
                    timestamp=row[5],
                    database=current_db,
                    cpu_time=row[4] / 1000000.0,  # Convertir a segundos
                    logical_reads=row[2],
                    physical_reads=row[3]
                )
                slow_queries.append(query_metric)
            
            # Agregar al log local
            with self._lock:
                self.query_log.extend(slow_queries)
                # Mantener solo las últimas N consultas
                if len(self.query_log) > self.max_query_log_size:
                    self.query_log = self.query_log[-self.max_query_log_size:]
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Error monitoreando consultas lentas: {e}")
            return []
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()

    def log_query_performance(self, query: str, execution_time: float, rows_affected: int = 0):
        """
        Registra el rendimiento de una consulta.
        
        Args:
            query: Texto de la consulta
            execution_time: Tiempo de ejecución en segundos
            rows_affected: Número de filas afectadas
        """
        try:
            query_metric = QueryMetrics(
                query=query[:1000],  # Limitar longitud
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.now(),
                database="unknown"
            )
            
            # Agregar al log local
            with self._lock:
                self.query_log.append(query_metric)
                if len(self.query_log) > self.max_query_log_size:
                    self.query_log = self.query_log[-self.max_query_log_size:]
            
            # Si es una consulta lenta, registrar en BD
            if execution_time > self.slow_query_threshold:
                self._persist_query_metric(query_metric)
            
        except Exception as e:
            logger.error(f"Error registrando rendimiento de consulta: {e}")

    def _persist_query_metric(self, metric: QueryMetrics):
        """Persiste una métrica de consulta en la base de datos."""
        try:
            conn = self._get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Calcular hash de la consulta
            import hashlib
            query_hash = hashlib.md5(metric.query.encode(), usedforsecurity=False).hexdigest()
            
            sql_insert_metric = self.sql_manager.get_query('optimizer', 'insert_query_metrics')
            cursor.execute(sql_insert_metric, (
                query_hash, metric.query, metric.execution_time, metric.rows_affected,
                metric.cpu_time, metric.logical_reads, metric.physical_reads,
                metric.database, metric.timestamp
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error persistiendo métrica: {e}")
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()

    def _log_optimization_action(self, action_type: str, table_name: Optional[str], 
                                details: str, success: bool, execution_time: float):
        """Registra una acción de optimización."""
        try:
            conn = self._get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            sql_insert_action = self.sql_manager.get_query('optimizer', 'insert_optimization_action')
            cursor.execute(sql_insert_action, (action_type, table_name, details, success, execution_time, datetime.now()))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error registrando acción de optimización: {e}")
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()

    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Genera un reporte completo de optimización.
        
        Returns:
            Reporte detallado de optimización
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'query_metrics': {
                'total_queries_logged': len(self.query_log),
                'slow_queries_count': 0,
                'average_execution_time': 0,
                'top_slow_queries': []
            },
            'optimization_actions': [],
            'recommendations': [],
            'database_health': {}
        }
        
        try:
            # Análisis de consultas en memoria
            if self.query_log:
                slow_queries = [q for q in self.query_log if q.execution_time > self.slow_query_threshold]
                report['query_metrics']['slow_queries_count'] = len(slow_queries)
                
                total_time = sum(q.execution_time for q in self.query_log)
                report['query_metrics']['average_execution_time'] = total_time / len(self.query_log)
                
                # Top 10 consultas más lentas
                sorted_queries = sorted(self.query_log, key=lambda x: x.execution_time, reverse=True)[:10]
                report['query_metrics']['top_slow_queries'] = [
                    {
                        'query': q.query[:200] + "..." if len(q.query) > 200 else q.query,
                        'execution_time': q.execution_time,
                        'timestamp': q.timestamp.isoformat()
                    }
                    for q in sorted_queries
                ]
            
            # Obtener acciones de optimización recientes
            conn = self._get_connection()
            if conn:
                cursor = conn.cursor()
                sql_get_recent_actions = self.sql_manager.get_query('optimizer', 'get_recent_optimization_actions')
                cursor.execute(sql_get_recent_actions)
                
                report['optimization_actions'] = [
                    {
                        'action_type': row[0],
                        'table_name': row[1],
                        'details': row[2],
                        'success': bool(row[3]),
                        'execution_time': row[4],
                        'timestamp': row[5].isoformat() if row[5] else None
                    }
                    for row in cursor.fetchall()
                ]
            
            # Obtener análisis actual de rendimiento
            current_analysis = self.analyze_database_performance()
            report['database_health'] = {
                'total_size_mb': current_analysis.get('total_size_mb', 0),
                'table_count': current_analysis.get('table_count', 0),
                'index_count': current_analysis.get('index_count', 0),
                'fragmented_indexes_count': len(current_analysis.get('fragmented_indexes', [])),
                'missing_indexes_count': len(current_analysis.get('missing_indexes', []))
            }
            
            report['recommendations'] = current_analysis.get('recommendations', [])
            
        except Exception as e:
            logger.error(f"Error generando reporte de optimización: {e}")
            report['error'] = str(e)
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return report

    def auto_optimize(self, create_indexes: bool = True, update_statistics: bool = True,
                     reorganize_indexes: bool = True) -> Dict[str, Any]:
        """
        Ejecuta optimización automática de la base de datos.
        
        Args:
            create_indexes: Si crear índices sugeridos
            update_statistics: Si actualizar estadísticas
            reorganize_indexes: Si reorganizar índices fragmentados
            
        Returns:
            Resultado de la optimización automática
        """
        result = {
            'success': False,
            'actions_completed': [],
            'actions_failed': [],
            'total_time': 0,
            'summary': {}
        }
        
        start_time = time.time()
        
        try:
            logger.info("Iniciando optimización automática de SQL Server")
            
            # 1. Actualizar estadísticas
            if update_statistics:
                stats_result = self.vacuum_and_analyze()
                if stats_result['success']:
                    result['actions_completed'].append('update_statistics')
                    result['summary']['statistics_updated'] = stats_result['tables_updated']
                else:
                    result['actions_failed'].append('update_statistics')
                    result['summary']['statistics_errors'] = len(stats_result['errors'])
            
            # 2. Crear índices de rendimiento
            if create_indexes:
                index_result = self.create_performance_indexes(execute=True)
                if index_result['success']:
                    result['actions_completed'].append('create_indexes')
                    result['summary']['indexes_created'] = index_result['indexes_created']
                else:
                    result['actions_failed'].append('create_indexes')
                    result['summary']['index_errors'] = len(index_result['errors'])
            
            # 3. Reorganizar índices fragmentados
            if reorganize_indexes:
                reorg_result = self._reorganize_fragmented_indexes()
                if reorg_result['success']:
                    result['actions_completed'].append('reorganize_indexes')
                    result['summary']['indexes_reorganized'] = reorg_result['indexes_processed']
                else:
                    result['actions_failed'].append('reorganize_indexes')
                    result['summary']['reorganize_errors'] = len(reorg_result['errors'])
            
            result['success'] = len(result['actions_failed']) == 0
            
            # Log de la acción completa
            self._log_optimization_action(
                "AUTO_OPTIMIZE",
                None,
                f"Completed: {', '.join(result['actions_completed'])}, Failed: {', '.join(result['actions_failed'])}",
                result['success'],
                time.time() - start_time
            )
            
            logger.info(f"Optimización automática completada. Éxito: {result['success']}")
            
        except Exception as e:
            result['actions_failed'].append('general_error')
            result['error'] = str(e)
            logger.error(f"Error en optimización automática: {e}")
        finally:
            result['total_time'] = time.time() - start_time
        
        return result

    def _reorganize_fragmented_indexes(self) -> Dict[str, Any]:
        """Reorganiza índices con alta fragmentación."""
        result = {
            'success': False,
            'indexes_processed': 0,
            'indexes_failed': 0,
            'errors': []
        }
        
        try:
            conn = self._get_connection()
            if not conn:
                result['errors'].append("No se pudo obtener conexión")
                return result
            
            cursor = conn.cursor()
            fragmented_indexes = self._get_fragmented_indexes(cursor)
            
            for index_info in fragmented_indexes:
                try:
                    schema = index_info['schema']
                    table = index_info['table']
                    index_name = index_info['index']
                    fragmentation = index_info['fragmentation_percent']
                    
                    # Decidir si reorganizar o reconstruir
                    if fragmentation > 70:
                        # Reconstruir índice
                        sql = f"ALTER INDEX [{index_name}] ON [{schema}].[{table}] REBUILD WITH (ONLINE = ON)"
                        action = "REBUILD"
                    else:
                        # Reorganizar índice
                        sql = f"ALTER INDEX [{index_name}] ON [{schema}].[{table}] REORGANIZE"
                        action = "REORGANIZE"
                    
                    cursor.execute(sql)
                    result['indexes_processed'] += 1
                    logger.info(f"{action} index {index_name} on {schema}.{table}")
                    
                except Exception as e:
                    error_msg = f"Error procesando índice {index_info.get('index', 'unknown')}: {e}"
                    result['errors'].append(error_msg)
                    result['indexes_failed'] += 1
                    logger.error(error_msg)
            
            result['success'] = result['indexes_failed'] == 0
            
        except Exception as e:
            result['errors'].append(f"Error general: {e}")
            logger.error(f"Error en _reorganize_fragmented_indexes: {e}")
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return result

    def profile_query(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """
        Perfila una consulta específica obteniendo su plan de ejecución.
        
        Args:
            query: Consulta SQL a perfilar
            params: Parámetros de la consulta
            
        Returns:
            Información detallada del perfilado
        """
        profile_result = {
            'query': query[:500] + "..." if len(query) > 500 else query,
            'execution_time': 0,
            'rows_returned': 0,
            'execution_plan': {},
            'recommendations': [],
            'metrics': {}
        }
        
        try:
            conn = self._get_connection()
            if not conn:
                profile_result['error'] = "No se pudo obtener conexión"
                return profile_result
            
            cursor = conn.cursor()
            
            # Habilitar estadísticas
            cursor.execute("SET STATISTICS IO ON")
            cursor.execute("SET STATISTICS TIME ON")
            
            start_time = time.time()
            
            # Ejecutar consulta
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Obtener resultados
            try:
                results = cursor.fetchall()
                profile_result['rows_returned'] = len(results)
            except:
                profile_result['rows_returned'] = cursor.rowcount if cursor.rowcount >= 0 else 0
            
            execution_time = time.time() - start_time
            profile_result['execution_time'] = execution_time
            
            # Obtener plan de ejecución
            cursor.execute("SET SHOWPLAN_XML ON")
            cursor.execute(query, params) if params else cursor.execute(query)
            plan_result = cursor.fetchone()
            if plan_result:
                profile_result['execution_plan'] = {
                    'xml_plan': str(plan_result[0])[:1000] + "..." if len(str(plan_result[0])) > 1000 else str(plan_result[0])
                }
            cursor.execute("SET SHOWPLAN_XML OFF")
            
            # Generar recomendaciones básicas
            if execution_time > self.slow_query_threshold:
                profile_result['recommendations'].append("Consulta lenta detectada - considerar optimización")
            
            if profile_result['rows_returned'] > 10000:
                profile_result['recommendations'].append("Consulta retorna muchas filas - considerar paginación")
            
            # Métricas adicionales
            profile_result['metrics'] = {
                'is_slow': execution_time > self.slow_query_threshold,
                'high_row_count': profile_result['rows_returned'] > 10000,
                'query_length': len(query)
            }
            
            # Registrar en log
            self.log_query_performance(query, execution_time, profile_result['rows_returned'])
            
        except Exception as e:
            profile_result['error'] = str(e)
            logger.error(f"Error perfilando consulta: {e}")
        finally:
            if 'conn' in locals() and conn and not self.db_connection:
                conn.close()
        
        return profile_result


class QueryProfiler:
    """Perfilador avanzado de consultas SQL Server."""
    
    def __init__(self, optimizer: DatabaseOptimizer):
        self.optimizer = optimizer
        self.profile_history = []

    def profile_query(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """Versión extendida del perfilado de consultas."""
        return self.optimizer.profile_query(query, params)

    def analyze_query_patterns(self) -> Dict[str, Any]:
        """Analiza patrones en consultas ejecutadas."""
        analysis = {
            'total_queries': len(self.optimizer.query_log),
            'slow_queries_ratio': 0,
            'common_patterns': [],
            'performance_trends': {}
        }
        
        if self.optimizer.query_log:
            slow_count = len([q for q in self.optimizer.query_log 
                            if q.execution_time > self.optimizer.slow_query_threshold])
            analysis['slow_queries_ratio'] = slow_count / len(self.optimizer.query_log)
            
            # Análisis de patrones comunes (simplificado)
            query_types = {}
            for query_metric in self.optimizer.query_log:
                query_start = query_metric.query.strip().upper()[:20]
                query_types[query_start] = query_types.get(query_start, 0) + 1
            
            analysis['common_patterns'] = sorted(
                query_types.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        
        return analysis


# Instancia global del optimizador
_optimizer_instance = None

def get_database_optimizer(db_connection=None, connection_string: Optional[str] = None) -> DatabaseOptimizer:
    """
    Obtiene la instancia global del optimizador de SQL Server.
    
    Args:
        db_connection: Conexión existente a SQL Server
        connection_string: String de conexión para crear nueva conexión
        
    Returns:
        Instancia del DatabaseOptimizer
    """
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = DatabaseOptimizer(db_connection, connection_string)
    return _optimizer_instance


if __name__ == "__main__":
    # Test del optimizador SQL Server
    print("=== Test DatabaseOptimizer SQL Server ===")
    
    try:
        optimizer = DatabaseOptimizer()
        
        print("\n1. Inicializando métricas...")
        init_result = optimizer.init_metrics_db()
        print(f"Métricas inicializadas: {init_result}")
        
        print("\n2. Analizando rendimiento...")
        analysis = optimizer.analyze_database_performance()
        print(f"Bases de datos analizadas: {len(analysis.get('databases', []))}")
        print(f"Tamaño total: {analysis.get('total_size_mb', 0):.2f} MB")
        print(f"Tablas: {analysis.get('table_count', 0)}")
        print(f"Índices: {analysis.get('index_count', 0)}")
        
        print("\n3. Recomendaciones:")
        for rec in analysis.get('recommendations', []):
            print(f"- {rec}")
        
        print("\n4. Optimización automática...")
        result = optimizer.auto_optimize()
        print(f"Éxito: {result['success']}")
        print(f"Tiempo total: {result['total_time']:.2f}s")
        print(f"Acciones completadas: {', '.join(result['actions_completed'])}")
        
        if result['actions_failed']:
            print(f"Acciones fallidas: {', '.join(result['actions_failed'])}")
        
    except Exception as e:
        print(f"Error en test: {e}")