#!/usr/bin/env python3
"""
Analizador de Rendimiento de Consultas
Identifica consultas lentas, problemas N+1 y oportunidades de optimización.
"""

import os
import re
import ast
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, Counter


class QueryAnalyzer:
    """Analiza el código fuente para identificar problemas de rendimiento en consultas."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.module_dir = self.project_root / "rexus" / "modules"

        # Patrones problemáticos
        self.n_plus_one_patterns = [
            r'for\s+\w+\s+in\s+\w+.*cursor\.execute',  # Loop con consulta
            r'for\s+\w+\s+in\s+\w+.*\.get\(',          # Loop con get individual
            r'\.all\(\).*for\s+\w+\s+in',              # Obtener todo y luego loop
            r'fetchall\(\).*for\s+\w+\s+in',           # fetchall seguido de loop
        ]

        self.slow_query_indicators = [
            r'SELECT\s+\*\s+FROM',                      # SELECT *
            r'JOIN.*JOIN.*JOIN',                        # Múltiples JOINs
            r'WHERE.*LIKE.*OR.*LIKE',                   # Múltiples LIKE
            r'ORDER\s+BY.*,.*,',                        # Múltiples ORDER BY
            r'GROUP\s+BY.*HAVING',                      # GROUP BY con HAVING
            r'IN\s*\([^)]{100,}\)',                     # IN con muchos valores
        ]

        self.missing_pagination_indicators = [
            r'fetchall\(\)',                            # fetchall sin límite
            r'\.all\(\)',                               # ORM all() sin límite
            r'SELECT.*FROM.*(?!LIMIT)',                 # SELECT sin LIMIT
        ]

    def analyze_project(self) -> Dict[str, Any]:
        """Analiza todo el proyecto en busca de problemas de rendimiento."""
        print("="*60)
        print("[PERFORMANCE] ANÁLISIS DE RENDIMIENTO DE CONSULTAS")
        print("="*60)

        results = {
            'modules_analyzed': 0,
            'total_files': 0,
            'n_plus_one_issues': [],
            'slow_query_issues': [],
            'missing_pagination_issues': [],
            'optimization_opportunities': [],
            'performance_score': 0,
            'recommendations': []
        }

        if not self.module_dir.exists():
            print("[ERROR] Directorio de módulos no encontrado")
            return results

        # Analizar cada módulo
        for module_path in self.module_dir.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('.'):
                module_results = self._analyze_module(module_path)
                self._merge_results(results, module_results)
                results['modules_analyzed'] += 1

        # Calcular puntuación de rendimiento
        results['performance_score'] = self._calculate_performance_score(results)

        # Generar recomendaciones
        results['recommendations'] = self._generate_recommendations(results)

        self._print_results(results)
        return results

    def _analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """Analiza un módulo específico."""
        results = {
            'module_name': module_path.name,
            'files_analyzed': 0,
            'n_plus_one_issues': [],
            'slow_query_issues': [],
            'missing_pagination_issues': [],
            'optimization_opportunities': []
        }

        # Analizar archivos Python en el módulo
        for file_path in module_path.rglob("*.py"):
            if file_path.name.startswith('.'):
                continue

            try:
                file_results = self._analyze_file(file_path)
                if file_results:
                    results['files_analyzed'] += 1
                    for key in ['n_plus_one_issues', 'slow_query_issues',
                              'missing_pagination_issues', 'optimization_opportunities']:
                        results[key].extend(file_results.get(key, []))
            except Exception as e:
                print(f"[WARNING] Error analizando {file_path}: {e}")

        return results

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            relative_path = file_path.relative_to(self.project_root)

            results = {
                'file_path': str(relative_path),
                'n_plus_one_issues': [],
                'slow_query_issues': [],
                'missing_pagination_issues': [],
                'optimization_opportunities': []
            }

            # Buscar patrones N+1
            results['n_plus_one_issues'] = self._find_n_plus_one_issues(content, relative_path)

            # Buscar consultas lentas
            results['slow_query_issues'] = self._find_slow_query_issues(content, relative_path)

            # Buscar falta de paginación
            results['missing_pagination_issues'] = self._find_pagination_issues(content, relative_path)

            # Identificar oportunidades de optimización
            results['optimization_opportunities'] = self._find_optimization_opportunities(content, relative_path)

            return results

        except Exception as e:
            print(f"[ERROR] Error leyendo archivo {file_path}: {e}")
            return {}

    def _find_n_plus_one_issues(self,
content: str,
        file_path: Path) -> List[Dict[str,
        Any]]:
        """Encuentra potenciales problemas N+1."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in self.n_plus_one_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Buscar contexto adicional
                    context = self._get_context(lines, i-1, 3)

                    issues.append({
                        'type': 'N+1 Query',
                        'line': i,
                        'pattern': pattern,
                        'code': line.strip(),
                        'context': context,
                        'severity': 'HIGH',
                        'description': 'Posible problema N+1: consulta dentro de un loop'
                    })

        return issues

    def _find_slow_query_issues(self,
content: str,
        file_path: Path) -> List[Dict[str,
        Any]]:
        """Encuentra potenciales consultas lentas."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in self.slow_query_indicators:
                if re.search(pattern, line, re.IGNORECASE):
                    context = self._get_context(lines, i-1, 2)

                    severity = 'HIGH' if 'SELECT *' in line.upper() else 'MEDIUM'

                    issues.append({
                        'type': 'Slow Query',
                        'line': i,
                        'pattern': pattern,
                        'code': line.strip(),
                        'context': context,
                        'severity': severity,
                        'description': 'Consulta potencialmente lenta'
                    })

        return issues

    def _find_pagination_issues(self,
content: str,
        file_path: Path) -> List[Dict[str,
        Any]]:
        """Encuentra falta de paginación."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in self.missing_pagination_indicators:
                if re.search(pattern, line, re.IGNORECASE):
                    # Verificar si hay LIMIT en las siguientes líneas
                    context_lines = lines[max(0, i-3):i+3]
                    has_limit = any('LIMIT' in l.upper() or 'limit' in l for l in context_lines)

                    if not has_limit:
                        context = self._get_context(lines, i-1, 2)

                        issues.append({
                            'type': 'Missing Pagination',
                            'line': i,
                            'pattern': pattern,
                            'code': line.strip(),
                            'context': context,
                            'severity': 'MEDIUM',
                            'description': 'Consulta sin paginación puede retornar muchos registros'
                        })

        return issues

    def _find_optimization_opportunities(self,
content: str,
        file_path: Path) -> List[Dict[str,
        Any]]:
        """Identifica oportunidades de optimización."""
        opportunities = []

        # Buscar funciones que podrían beneficiarse de cache
        cache_opportunities = self._find_cache_opportunities(content)
        opportunities.extend(cache_opportunities)

        # Buscar consultas que podrían optimizarse con índices
        index_opportunities = self._find_index_opportunities(content)
        opportunities.extend(index_opportunities)

        return opportunities

    def _find_cache_opportunities(self, content: str) -> List[Dict[str, Any]]:
        """Encuentra oportunidades para aplicar cache."""
        opportunities = []
        lines = content.split('\n')

        # Buscar funciones que hacen consultas complejas sin cache
        cache_indicators = [
            r'def\s+obtener_estadisticas',
            r'def\s+generar_reporte',
            r'def\s+obtener_todos',
            r'def\s+buscar_',
            r'JOIN.*JOIN',  # Consultas con múltiples JOINs
        ]

        for i, line in enumerate(lines, 1):
            for pattern in cache_indicators:
                if re.search(pattern, line, re.IGNORECASE):
                    # Verificar si ya tiene cache
                    function_block = self._get_function_block(lines, i-1)
                    has_cache = any('cache' in l.lower() or '@cached' in l for l in function_block)

                    if not has_cache:
                        opportunities.append({
                            'type': 'Cache Opportunity',
                            'line': i,
                            'code': line.strip(),
                            'severity': 'LOW',
                            'description': 'Función podría beneficiarse de cache',
                            'suggestion': 'Agregar decorador @cached_query'
                        })

        return opportunities

    def _find_index_opportunities(self, content: str) -> List[Dict[str, Any]]:
        """Encuentra oportunidades para crear índices."""
        opportunities = []
        lines = content.split('\n')

        # Buscar WHERE clauses que podrían necesitar índices
        index_indicators = [
            r'WHERE\s+\w+\s*=',                    # WHERE column = value
            r'WHERE\s+\w+\s+LIKE',                 # WHERE column LIKE
            r'ORDER\s+BY\s+\w+',                  # ORDER BY column
            r'GROUP\s+BY\s+\w+',                  # GROUP BY column
        ]

        for i, line in enumerate(lines, 1):
            for pattern in index_indicators:
                if re.search(pattern, line, re.IGNORECASE):
                    opportunities.append({
                        'type': 'Index Opportunity',
                        'line': i,
                        'code': line.strip(),
                        'severity': 'LOW',
                        'description': 'Consulta podría beneficiarse de un índice',
                        'suggestion': 'Considerar crear índice en la columna utilizada'
                    })

        return opportunities

    def _get_context(self,
lines: List[str],
        line_idx: int,
        context_size: int = 2) -> List[str]:
        """Obtiene líneas de contexto alrededor de una línea específica."""
        start = max(0, line_idx - context_size)
        end = min(len(lines), line_idx + context_size + 1)
        return [f"{i+1}: {line}" for i, line in enumerate(lines[start:end], start)]

    def _get_function_block(self, lines: List[str], start_idx: int) -> List[str]:
        """Obtiene el bloque completo de una función."""
        function_lines = []
        indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx, min(len(lines), start_idx + 50)):  # Máximo 50 líneas
            line = lines[i]
            if line.strip() == '':
                continue

            current_indent = len(line) - len(line.lstrip())
            if i > start_idx and current_indent <= indent_level and line.strip():
                break

            function_lines.append(line)

        return function_lines

    def _merge_results(self, main_results: Dict, module_results: Dict):
        """Fusiona resultados de un módulo con los resultados principales."""
        main_results['total_files'] += module_results['files_analyzed']

        for key in ['n_plus_one_issues', 'slow_query_issues', 'missing_pagination_issues', 'optimization_opportunities']:
            main_results[key].extend(module_results[key])

    def _calculate_performance_score(self, results: Dict) -> int:
        """Calcula una puntuación de rendimiento del 0-100."""
        # Puntuación base
        score = 100

        # Penalizar problemas críticos
        score -= len(results['n_plus_one_issues']) * 15
        score -= len(results['slow_query_issues']) * 10
        score -= len(results['missing_pagination_issues']) * 5

        return max(0, score)

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []

        if results['n_plus_one_issues']:
            recommendations.append(
                f"[CRITICO] Resolver {len(results['n_plus_one_issues'])} problemas N+1 "
                "usando batch queries o eager loading"
            )

        if results['slow_query_issues']:
            recommendations.append(
                f"[ALTO] Optimizar {len(results['slow_query_issues'])} consultas lentas "
                "agregando indices o mejorando la logica"
            )

        if results['missing_pagination_issues']:
            recommendations.append(
                f"[MEDIO] Agregar paginacion a {len(results['missing_pagination_issues'])} consultas "
                "que podrian retornar muchos registros"
            )

        cache_opportunities = [o for o in results['optimization_opportunities'] if o['type'] == 'Cache Opportunity']
        if cache_opportunities:
            recommendations.append(
                f"[BAJO] Considerar cache en {len(cache_opportunities)} funciones "
                "para mejorar rendimiento"
            )

        if results['performance_score'] >= 80:
            recommendations.append("[OK] El rendimiento general es bueno")
        elif results['performance_score'] >= 60:
            recommendations.append("[WARNING] El rendimiento necesita mejoras menores")
        else:
            recommendations.append("[ERROR] El rendimiento necesita mejoras urgentes")

        return recommendations

    def _print_results(self, results: Dict):
        """Imprime los resultados del análisis."""
        print(f"\n[ANÁLISIS] Módulos analizados: {results['modules_analyzed']}")
        print(f"[ANÁLISIS] Archivos procesados: {results['total_files']}")
        print(f"[PUNTUACIÓN] Rendimiento: {results['performance_score']}/100")

        print(f"\n[PROBLEMAS ENCONTRADOS]")
        print(f"  [N+1] Problemas N+1: {len(results['n_plus_one_issues'])}")
        print(f"  [SLOW] Consultas lentas: {len(results['slow_query_issues'])}")
        print(f"  [PAGE] Paginacion faltante: {len(results['missing_pagination_issues'])}")
        print(f"  [OPT] Oportunidades optimizacion: {len(results['optimization_opportunities'])}")

        # Mostrar algunos ejemplos
        if results['n_plus_one_issues']:
            print(f"\n[EJEMPLOS N+1] Top 3 problemas:")
            for issue in results['n_plus_one_issues'][:3]:
                print(f"  - {issue['file_path']}:{issue['line']}: {issue['code']}")

        if results['slow_query_issues']:
            print(f"\n[EJEMPLOS SLOW QUERIES] Top 3 problemas:")
            for issue in results['slow_query_issues'][:3]:
                print(f"  - {issue['file_path']}:{issue['line']}: {issue['code']}")

        print(f"\n[RECOMENDACIONES]")
        for i, recommendation in enumerate(results['recommendations'], 1):
            print(f"  {i}. {recommendation}")


def main():
    """Función principal."""
    try:
        analyzer = QueryAnalyzer()
        results = analyzer.analyze_project()

        # Guardar resultados si es necesario
        if results['performance_score'] < 70:
            print(f"\n[ADVERTENCIA] Puntuación de rendimiento baja: {results['performance_score']}/100")
            print("Se recomienda implementar las optimizaciones sugeridas.")

        return results['performance_score'] >= 70

    except Exception as e:
        print(f"\n[ERROR] Error durante el análisis: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
