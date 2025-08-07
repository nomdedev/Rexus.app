#!/usr/bin/env python3
"""
Query Performance Analyzer - Rexus.app

Analiza el performance de consultas críticas antes y después de índices.
Identifica consultas lentas y recomienda optimizaciones.
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class QueryPerformanceAnalyzer:
    """Analizador de performance de consultas SQL."""
    
    def __init__(self, db_connection):
        """
        Inicializa el analizador.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.results = []
        
    def analyze_critical_queries(self) -> Dict:
        """
        Analiza queries críticas identificadas en auditoría.
        
        Returns:
            Dict: Resultados del análisis de performance
        """
        print("🔍 ANALIZANDO PERFORMANCE DE CONSULTAS CRÍTICAS")
        print("=" * 50)
        
        # Definir consultas críticas a analizar
        critical_queries = {
            "inventario_search": {
                "name": "Búsqueda en Inventario por Código",
                "query": "SELECT * FROM inventario WHERE codigo LIKE ?",
                "params": ('%TEST%',),
                "expected_improvement": "Con índice idx_inventario_codigo"
            },
            "obras_filter_estado": {
                "name": "Filtro Obras por Estado", 
                "query": "SELECT * FROM obras WHERE estado = ?",
                "params": ('EN_PROCESO',),
                "expected_improvement": "Con índice idx_obras_estado"
            },
            "usuarios_auth": {
                "name": "Autenticación Usuario",
                "query": "SELECT * FROM usuarios WHERE usuario = ?",
                "params": ('admin',),
                "expected_improvement": "Con índice idx_usuarios_username"
            },
            "pedidos_date_range": {
                "name": "Pedidos por Rango de Fechas",
                "query": "SELECT * FROM pedidos WHERE fecha_creacion >= ? ORDER BY fecha_creacion DESC",
                "params": ('2024-01-01',),
                "expected_improvement": "Con índice idx_pedidos_fecha"
            },
            "obras_responsable": {
                "name": "Obras por Responsable",
                "query": "SELECT * FROM obras WHERE responsable LIKE ?",
                "params": ('%admin%',),
                "expected_improvement": "Con índice idx_obras_responsable"
            },
            "vidrios_tipo": {
                "name": "Vidrios por Tipo",
                "query": "SELECT * FROM vidrios WHERE tipo = ?",
                "params": ('Templado',),
                "expected_improvement": "Con índice idx_vidrios_tipo"
            }
        }
        
        analysis_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "queries_analyzed": len(critical_queries),
            "results": [],
            "recommendations": []
        }
        
        for query_id, query_info in critical_queries.items():
            print(f"\n📊 Analizando: {query_info['name']}")
            
            try:
                # Medir tiempo de ejecución
                start_time = time.time()
                
                cursor = self.db_connection.cursor()
                cursor.execute(query_info['query'], query_info['params'])
                results = cursor.fetchall()
                
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # en milisegundos
                
                # Obtener plan de ejecución (si está disponible)
                execution_plan = self._get_execution_plan(query_info['query'], query_info['params'])
                
                result = {
                    "query_id": query_id,
                    "name": query_info['name'],
                    "execution_time_ms": round(execution_time, 2),
                    "rows_returned": len(results),
                    "expected_improvement": query_info['expected_improvement'],
                    "execution_plan": execution_plan
                }
                
                analysis_results["results"].append(result)
                
                # Evaluación de performance
                if execution_time > 1000:  # > 1 segundo
                    status = "🔴 LENTA"
                elif execution_time > 100:  # > 100ms
                    status = "🟡 MODERADA"
                else:
                    status = "🟢 RÁPIDA"
                
                print(f"   Tiempo: {execution_time:.2f}ms - {status}")
                print(f"   Filas: {len(results)}")
                print(f"   Mejora esperada: {query_info['expected_improvement']}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                analysis_results["results"].append({
                    "query_id": query_id,
                    "name": query_info['name'],
                    "error": str(e),
                    "expected_improvement": query_info['expected_improvement']
                })
        
        # Generar recomendaciones
        analysis_results["recommendations"] = self._generate_recommendations(analysis_results["results"])
        
        return analysis_results
    
    def _get_execution_plan(self, query: str, params: Tuple) -> Optional[str]:
        """
        Obtiene el plan de ejecución de una query (si está disponible).
        
        Args:
            query: Query SQL
            params: Parámetros de la query
            
        Returns:
            Plan de ejecución o None si no está disponible
        """
        try:
            cursor = self.db_connection.cursor()
            
            # Para SQL Server, intentar obtener plan estimado
            cursor.execute("SET SHOWPLAN_TEXT ON")
            cursor.execute(query, params)
            plan = cursor.fetchall()
            cursor.execute("SET SHOWPLAN_TEXT OFF")
            
            return str(plan) if plan else None
            
        except Exception:
            # Si no se puede obtener el plan, no es crítico
            return None
    
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """
        Genera recomendaciones basadas en los resultados del análisis.
        
        Args:
            results: Resultados del análisis
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        slow_queries = [r for r in results if r.get('execution_time_ms', 0) > 100]
        
        if slow_queries:
            recommendations.append("🚀 CREAR ÍNDICES CRÍTICOS para mejorar consultas lentas")
            recommendations.append("📊 Ejecutar script create_performance_indexes.sql")
            
            for query in slow_queries:
                if query.get('execution_time_ms', 0) > 1000:
                    recommendations.append(f"⚡ URGENTE: Optimizar '{query['name']}' ({query['execution_time_ms']}ms)")
        
        if not slow_queries:
            recommendations.append("✅ Performance actual es BUENA")
            recommendations.append("📈 Considerar índices preventivos para escalabilidad")
        
        # Recomendaciones específicas por tipo de consulta
        for result in results:
            if 'error' not in result:
                time_ms = result.get('execution_time_ms', 0)
                rows = result.get('rows_returned', 0)
                
                if time_ms > 50 and rows > 1000:
                    recommendations.append(f"🔄 Implementar paginación en '{result['name']}'")
                
                if 'inventario' in result['query_id'] and time_ms > 100:
                    recommendations.append("📦 Considerar cache para búsquedas de inventario")
                
                if 'usuarios' in result['query_id'] and time_ms > 50:
                    recommendations.append("🔐 Cache de sesiones para autenticación")
        
        return recommendations
    
    def benchmark_before_after_indexes(self, queries_to_test: List[str]) -> Dict:
        """
        Benchmark de queries antes y después de crear índices.
        
        Args:
            queries_to_test: Lista de queries a probar
            
        Returns:
            Resultados del benchmark
        """
        print("\n🏁 BENCHMARK ANTES/DESPUÉS DE ÍNDICES")
        print("=" * 40)
        
        # Este método requeriría ejecutar las queries antes de crear índices,
        # crear los índices, y luego ejecutar de nuevo para comparar.
        # Por simplicidad, solo documentamos el proceso
        
        benchmark_results = {
            "status": "requires_manual_execution",
            "process": [
                "1. Ejecutar analyze_critical_queries() ANTES de crear índices",
                "2. Ejecutar create_performance_indexes.sql",
                "3. Ejecutar analyze_critical_queries() DESPUÉS de crear índices", 
                "4. Comparar resultados para medir mejora"
            ],
            "expected_improvements": {
                "inventario_search": "50-80% mejora con idx_inventario_codigo",
                "obras_filter_estado": "60-90% mejora con idx_obras_estado",
                "usuarios_auth": "70-95% mejora con idx_usuarios_username",
                "pedidos_date_range": "40-70% mejora con idx_pedidos_fecha"
            }
        }
        
        return benchmark_results
    
    def generate_performance_report(self, analysis_results: Dict) -> str:
        """
        Genera un reporte detallado de performance.
        
        Args:
            analysis_results: Resultados del análisis
            
        Returns:
            Reporte formateado
        """
        report = []
        report.append("📈 REPORTE DE PERFORMANCE - REXUS.APP")
        report.append("=" * 50)
        report.append(f"Fecha: {analysis_results['timestamp']}")
        report.append(f"Consultas analizadas: {analysis_results['queries_analyzed']}")
        report.append("")
        
        # Resumen por query
        report.append("📊 RESULTADOS POR CONSULTA:")
        report.append("-" * 30)
        
        for result in analysis_results['results']:
            if 'error' in result:
                report.append(f"❌ {result['name']}: ERROR - {result['error']}")
            else:
                time_ms = result['execution_time_ms']
                rows = result['rows_returned']
                
                if time_ms > 1000:
                    status = "🔴 CRÍTICA"
                elif time_ms > 100:
                    status = "🟡 LENTA"
                else:
                    status = "🟢 BUENA"
                
                report.append(f"{status} {result['name']}: {time_ms}ms ({rows} filas)")
                report.append(f"    Mejora esperada: {result['expected_improvement']}")
        
        report.append("")
        report.append("💡 RECOMENDACIONES:")
        report.append("-" * 20)
        for rec in analysis_results['recommendations']:
            report.append(f"  {rec}")
        
        return "\n".join(report)


def main():
    """Función principal para análisis de performance."""
    print("🔍 INICIANDO ANÁLISIS DE PERFORMANCE DE CONSULTAS")
    print("Este script requiere conexión a la base de datos")
    
    # En un entorno real, aquí se conectaría a la BD
    print("⚠️  Para usar este analizador:")
    print("1. Conectar a la base de datos de Rexus")
    print("2. analyzer = QueryPerformanceAnalyzer(db_connection)")
    print("3. results = analyzer.analyze_critical_queries()")
    print("4. print(analyzer.generate_performance_report(results))")
    
    print("\n📋 CONSULTAS CRÍTICAS IDENTIFICADAS PARA ANÁLISIS:")
    critical_queries = [
        "• Búsqueda en Inventario por Código",
        "• Filtro Obras por Estado", 
        "• Autenticación Usuario",
        "• Pedidos por Rango de Fechas",
        "• Obras por Responsable",
        "• Vidrios por Tipo"
    ]
    
    for query in critical_queries:
        print(f"  {query}")
    
    print(f"\n📄 Crear índices ejecutando: scripts/database/create_performance_indexes.sql")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())