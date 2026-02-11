"""
Query Plan Analyzer - Rexus.app
Analiza planes de ejecución de queries SQL Server

Características:
- Análisis de planes de ejecución
- Detección de problemas (Table Scan, Index Scan)
- Recomendaciones de optimización
- Estimación de costos
- Sugerencias de índices
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class PlanSeverity(Enum):
    """Severidad de un problema en el plan."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PlanOperator(Enum):
    """Operadores de planes de ejecución SQL Server."""
    TABLE_SCAN = "Table Scan"
    INDEX_SCAN = "Index Scan"
    INDEX_SEEK = "Index Seek"
    CLUSTERED_INDEX_SEEK = "Clustered Index Seek"
    CLUSTERED_INDEX_SCAN = "Clustered Index Scan"
    KEY_LOOKUP = "Key Lookup"
    NESTED_LOOPS = "Nested Loops"
    HASH_MATCH = "Hash Match"
    MERGE_JOIN = "Merge Join"
    SORT = "Sort"
    COMPUTE_SCALAR = "Compute Scalar"
    FILTER = "Filter"
    TOP = "Top"


@dataclass
class PlanIssue:
    """Problema detectado en el plan de ejecución."""
    severity: PlanSeverity
    operator: str
    table: Optional[str]
    index: Optional[str]
    description: str
    recommendation: str
    estimated_cost: float = 0.0
    row_count: int = 0


@dataclass
class PlanAnalysis:
    """Resultado del análisis de un plan."""
    query: str
    query_hash: str
    analyzed_at: datetime
    total_cost: float
    estimated_rows: int
    issues: List[PlanIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    missing_indexes: List[Dict] = field(default_factory=list)

    @property
    def has_critical_issues(self) -> bool:
        """Si hay problemas críticos."""
        return any(i.severity == PlanSeverity.CRITICAL for i in self.issues)

    @property
    def has_high_issues(self) -> bool:
        """Si hay problemas de alta prioridad."""
        return any(i.severity in [PlanSeverity.CRITICAL, PlanSeverity.HIGH] for i in self.issues)

    @property
    def optimization_potential(self) -> float:
        """Potencial de optimización (0-100)."""
        if self.total_cost == 0:
            return 0

        critical_cost = sum(i.estimated_cost for i in self.issues
                          if i.severity == PlanSeverity.CRITICAL)
        high_cost = sum(i.estimated_cost for i in self.issues
                       if i.severity == PlanSeverity.HIGH)

        problem_cost = critical_cost + (high_cost * 0.5)
        return min(100, (problem_cost / self.total_cost) * 100)


class QueryPlanAnalyzer:
    """
    Analizador de planes de ejecución de SQL Server.

    Características:
    - Análisis de SHOWPLAN
    - Detección de problemas comunes
    - Sugerencias de índices
    - Estimación de costos

    Example:
        analyzer = QueryPlanAnalyzer()

        analysis = analyzer.analyze_query(
            "SELECT * FROM usuarios WHERE nombre = 'Juan'",
            connection
        )

        if analysis.has_high_issues:
            for issue in analysis.issues:
                print(f"{issue.severity.value}: {issue.recommendation}")
    """

    # Patrones de búsqueda de problemas
    PROBLEM_PATTERNS = {
        PlanOperator.TABLE_SCAN: {
            'severity': PlanSeverity.HIGH,
            'description': 'Escaneo completo de tabla',
            'recommendation': 'Crear índice en las columnas de filtro'
        },
        PlanOperator.INDEX_SCAN: {
            'severity': PlanSeverity.MEDIUM,
            'description': 'Escaneo de índice (no Seek)',
            'recommendation': 'Considerar incluir columnas en índice o usar covering index'
        },
        PlanOperator.CLUSTERED_INDEX_SCAN: {
            'severity': PlanSeverity.MEDIUM,
            'description': 'Escaneo de índice agrupado',
            'recommendation': 'Crear índice no agrupado en columnas de búsqueda'
        },
        PlanOperator.KEY_LOOKUP: {
            'severity': PlanSeverity.MEDIUM,
            'description': 'Lookup para obtener columnas',
            'recommendation': 'Incluir columnas en índice (covering index)'
        },
        PlanOperator.SORT: {
            'severity': PlanSeverity.LOW,
            'description': 'Operación Sort explícita',
            'recommendation': 'Crear índice con columnas en orden de clasificación'
        },
    }

    def __init__(self):
        """Inicializa el analizador."""
        self._analysis_cache: Dict[str, PlanAnalysis] = {}

    def analyze_query(self,
                     query: str,
                     connection,
                     params: tuple = None) -> PlanAnalysis:
        """
        Analiza el plan de ejecución de una query.

        Args:
            query: Query SQL a analizar
            connection: Conexión a la base de datos
            params: Parámetros de la query

        Returns:
            Análisis del plan
        """
        query_hash = self._hash_query(query)

        # Verificar caché
        if query_hash in self._analysis_cache:
            return self._analysis_cache[query_hash]

        try:
            # Obtener plan de ejecución
            plan_xml = self._get_query_plan(query, connection, params)

            # Analizar plan
            analysis = self._analyze_plan_xml(query, plan_xml)

            # Guardar en caché
            self._analysis_cache[query_hash] = analysis

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return self._create_error_analysis(query, str(e))

    def _hash_query(self, query: str) -> str:
        """Genera hash de la query para caché."""
        import hashlib
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _get_query_plan(self, query: str, connection, params: tuple = None) -> str:
        """Obtiene el plan de ejecución XML de SQL Server."""
        # Usar SET SHOWPLAN_XML ON
        plan_query = f"SET SHOWPLAN_XML ON; {query}; SET SHOWPLAN_XML OFF;"

        cursor = connection.cursor()
        try:
            cursor.execute(plan_query, params or ())
            row = cursor.fetchone()
            if row and row[0]:
                # El plan viene como XML
                return row[0]
            return ""
        finally:
            cursor.close()

    def _analyze_plan_xml(self, query: str, plan_xml: str) -> PlanAnalysis:
        """Analiza el XML del plan de ejecución."""
        import xml.etree.ElementTree as ET

        analysis = PlanAnalysis(
            query=query,
            query_hash=self._hash_query(query),
            analyzed_at=datetime.now(),
            total_cost=0.0,
            estimated_rows=0
        )

        if not plan_xml:
            analysis.suggestions.append("No se pudo obtener el plan de ejecución")
            return analysis

        try:
            root = ET.fromstring(plan_xml)

            # Extraer información del plan
            self._extract_cost_info(root, analysis)
            self._find_plan_issues(root, analysis)
            self._find_missing_indexes(root, analysis)

        except ET.ParseError as e:
            logger.error(f"Error parsing plan XML: {e}")
            analysis.suggestions.append(f"Error al analizar plan XML: {e}")

        return analysis

    def _extract_cost_info(self, root, analysis: PlanAnalysis):
        """Extrae información de costos del plan."""
        # Buscar elementos Statement
        for stmt in root.findall('.//{http://schemas.microsoft.com/sqlserver/2004/07/showplan}Statement'):
            # Costo estimado
            cost_elem = stmt.find('.//{http://schemas.microsoft.com/sqlserver/2004/07/showplan}EstimatedExecutionMode')
            if cost_elem is not None:
                # Buscar QueryPlan
                qp = stmt.find('.//{http://schemas.microsoft.com/sqlserver/2004/07/showplan}QueryPlan')
                if qp is not None:
                    cached_cost = qp.get('CachedPlanSize')
                    if cached_cost:
                        analysis.total_cost += float(cached_cost)

            # Filas estimadas
            for rel in stmt.findall('.//{http://schemas.microsoft.com/sqlserver/2004/07/showplan}RelOp'):
                estimate = rel.get('EstimateRows')
                if estimate:
                    analysis.estimated_rows += float(estimate)

    def _find_plan_issues(self, root, analysis: PlanAnalysis):
        """Busca problemas en el plan de ejecución."""
        ns = {'sp': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}

        for rel_op in root.findall('.//sp:RelOp', ns):
            physical_op = rel_op.get('PhysicalOp')
            logical_op = rel_op.get('LogicalOp')

            # Verificar operadores problemáticos
            for operator, info in self.PROBLEM_PATTERNS.items():
                if physical_op == operator.value or logical_op == operator.value:
                    # Extraer información adicional
                    table_name = self._extract_table_name(rel_op)
                    index_name = self._extract_index_name(rel_op)
                    estimated_cost = float(rel_op.get('EstimateTotalCost', 0))
                    row_count = int(float(rel_op.get('EstimateRows', 0)))

                    issue = PlanIssue(
                        severity=info['severity'],
                        operator=operator.value,
                        table=table_name,
                        index=index_name,
                        description=info['description'],
                        recommendation=info['recommendation'],
                        estimated_cost=estimated_cost,
                        row_count=row_count
                    )

                    analysis.issues.append(issue)

    def _extract_table_name(self, rel_op) -> Optional[str]:
        """Extrae el nombre de la tabla de un RelOp."""
        ns = {'sp': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}

        # Buscar elemento Object
        for obj in rel_op.findall('.//sp:Object', ns):
            table = obj.get('Table')
            if table:
                return table

        return None

    def _extract_index_name(self, rel_op) -> Optional[str]:
        """Extrae el nombre del índice de un RelOp."""
        ns = {'sp': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}

        for obj in rel_op.findall('.//sp:Object', ns):
            index = obj.get('Index')
            if index:
                return index

        return None

    def _find_missing_indexes(self, root, analysis: PlanAnalysis):
        """Busca índices faltantes sugeridos por el optimizador."""
        ns = {'sp': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}

        for missing in root.findall('.//sp:MissingIndex', ns):
            table = missing.get('Table')
            if not table:
                continue

            # Extraer columnas
            columns = []
            for col in missing.findall('.//sp:Column', ns):
                col_name = col.get('Name')
                usage = col.get('Usage')
                if col_name:
                    columns.append(f"{col_name} ({usage})")

            # Crear sugerencia de índice
            analysis.missing_indexes.append({
                'table': table,
                'columns': columns,
                'impact': missing.get('Impact', 0)
            })

            # Agregar recomendación
            if columns:
                index_cols = ', '.join(c for c in columns if 'EQUALITY' in c or 'INEQUALITY' in c)
                include_cols = ', '.join(c for c in columns if 'INCLUDE' in c)

                if index_cols:
                    suggestion = f"Crear índice en {table}({index_cols})"
                    if include_cols:
                        suggestion += f" INCLUDE ({include_cols})"
                    analysis.suggestions.append(suggestion)

    def _create_error_analysis(self, query: str, error: str) -> PlanAnalysis:
        """Crea un análisis de error."""
        return PlanAnalysis(
            query=query,
            query_hash="",
            analyzed_at=datetime.now(),
            total_cost=0.0,
            estimated_rows=0,
            suggestions=[f"Error de análisis: {error}"]
        )

    def analyze_from_text(self, query: str, plan_text: str) -> PlanAnalysis:
        """
        Analiza desde texto de plan (SHOWPLAN_ALL o SHOWPLAN_TEXT).

        Args:
            query: Query analizada
            plan_text: Texto del plan

        Returns:
            Análisis del plan
        """
        analysis = PlanAnalysis(
            query=query,
            query_hash=self._hash_query(query),
            analyzed_at=datetime.now(),
            total_cost=0.0,
            estimated_rows=0
        )

        # Buscar operadores problemáticos en texto
        for line in plan_text.split('\n'):
            line_upper = line.upper()

            for operator, info in self.PROBLEM_PATTERNS.items():
                if operator.value.upper() in line_upper:
                    # Extraer información si está disponible
                    table_match = re.search(r'TABLE:\[(\w+)\]', line_upper)
                    table = table_match.group(1) if table_match else None

                    analysis.issues.append(PlanIssue(
                        severity=info['severity'],
                        operator=operator.value,
                        table=table,
                        index=None,
                        description=info['description'],
                        recommendation=info['recommendation']
                    ))

        return analysis

    def get_optimization_sql(self, analysis: PlanAnalysis) -> List[str]:
        """Genera SQL de optimización basado en el análisis."""
        sql_statements = []

        for index in analysis.missing_indexes:
            table = index['table']
            columns = index['columns']

            # Separar equality/inequality de include
            index_cols = [c for c in columns if 'EQUALITY' in c or 'INEQUALITY' in c]
            include_cols = [c for c in columns if 'INCLUDE' in c]

            if index_cols:
                col_names = ', '.join(
                    c.replace(' (EQUALITY)', '').replace(' (INEQUALITY)', '')
                    for c in index_cols
                )
                index_name = f"idx_{table}_{len(sql_statements)}"

                sql = f"CREATE INDEX [{index_name}] ON [{table}] ({col_names})"

                if include_cols:
                    include_names = ', '.join(
                        c.replace(' (INCLUDE)', '')
                        for c in include_cols
                    )
                    sql += f" INCLUDE ({include_names})"

                sql_statements.append(sql)

        # Agregar sugerencias basadas en issues
        for issue in analysis.issues:
            if issue.table:
                if issue.operator == PlanOperator.TABLE_SCAN.value:
                    # Recomendar índice básico
                    sql = f"-- Considerar crear índice en [{issue.table}]"
                    sql += "\n-- Analizar columnas WHERE y JOIN de la query"
                    sql_statements.append(sql)

        return sql_statements

    def clear_cache(self):
        """Limpia la caché de análisis."""
        self._analysis_cache.clear()


# Función de conveniencia para análisis rápido
def analyze_query(query: str, connection, params: tuple = None) -> PlanAnalysis:
    """
    Analiza una query de forma rápida.

    Args:
        query: Query SQL
        connection: Conexión a BD
        params: Parámetros

    Returns:
        Análisis del plan
    """
    analyzer = QueryPlanAnalyzer()
    return analyzer.analyze_query(query, connection, params)


# Decorador para análisis automático
def track_query_plan(analyze_on_slow: bool = True, slow_threshold_ms: float = 1000):
    """
    Decorador para analizar plan de ejecución de queries lentas.

    Args:
        analyze_on_slow: Solo analizar si es lenta
        slow_threshold_ms: Umbral de lentitud

    Example:
        @track_query_plan(slow_threshold_ms=500)
        def get_usuarios(nombre):
            return db.execute("SELECT * FROM usuarios WHERE nombre = ?", nombre)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start = time.time()

            result = func(*args, **kwargs)

            duration_ms = (time.time() - start) * 1000

            if not analyze_on_slow or duration_ms > slow_threshold_ms:
                # Intentar analizar
                try:
                    # Obtener connection si está disponible
                    connection = kwargs.get('connection') or (
                        args[0] if args and hasattr(args[0], 'cursor') else None
                    )

                    if connection:
                        # Obtener query del contexto (requiere implementación específica)
                        pass
                except Exception as e:
                    logger.debug(f"Could not analyze query plan: {e}")

            return result

        return wrapper
    return decorator
