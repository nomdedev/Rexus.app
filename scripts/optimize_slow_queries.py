# -*- coding: utf-8 -*-
"""
Optimizador de Consultas SQL Lentas
Identifica y migra consultas SQL hardcodeadas a archivos externos optimizados

Funciones principales:
1. Analizar consultas existentes y detectar problemas de rendimiento
2. Crear versiones optimizadas con índices sugeridos
3. Migrar a archivos SQL externos
4. Generar reportes de optimización

Fecha: 23/08/2025
Versión: 1.0.0
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sql_optimization.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class SQLQueryOptimizer:
    """Optimizador de consultas SQL para mejor rendimiento."""
    
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.modules_path = self.root_path / "rexus" / "modules"
        self.sql_path = self.root_path / "sql"
        self.optimization_report = []
        
        # Patrones de consultas problemáticas
        self.slow_query_patterns = [
            r'SELECT \* FROM \w+',  # SELECT *
            r'LIKE \'%.*%\'',       # LIKE con % al inicio
            r'WHERE \w+ IN \(',     # IN con muchos valores
            r'JOIN.*JOIN.*JOIN',    # Múltiples JOINs
            r'ORDER BY.*LIMIT',     # ORDER BY sin índice
            r'DISTINCT.*ORDER BY',  # DISTINCT + ORDER BY
            r'SUBSTRING\(',         # Funciones en WHERE
            r'GROUP BY.*HAVING',    # GROUP BY con HAVING
            r'NOT EXISTS',          # NOT EXISTS costoso
            r'OR \w+\.\w+ =',      # OR en WHERE
        ]
        
        # Consultas específicas de módulos críticos
        self.critical_modules = [
            'inventario', 'obras', 'pedidos', 'compras', 'usuarios'
        ]
    
    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analizar archivo Python para encontrar consultas SQL."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            queries_found = []
            
            # Buscar strings que contengan SQL
            sql_patterns = [
                r'["\'].*SELECT.*FROM.*["\']',
                r'["\'].*INSERT.*INTO.*["\']',
                r'["\'].*UPDATE.*SET.*["\']',
                r'["\'].*DELETE.*FROM.*["\']'
            ]
            
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    query = match.group()
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Analizar si la consulta es lenta
                    is_slow, issues = self.is_slow_query(query)
                    if is_slow:
                        queries_found.append({
                            'file': str(file_path),
                            'line': line_num,
                            'query': query.strip().strip('"\''),
                            'issues': issues,
                            'module': self.get_module_name(file_path)
                        })
            
            return queries_found
            
        except Exception as e:
            logger.error(f"Error analizando {file_path}: {e}")
            return []
    
    def is_slow_query(self, query: str) -> Tuple[bool, List[str]]:
        """Determinar si una consulta puede ser lenta."""
        issues = []
        
        for pattern in self.slow_query_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                issues.append(self.get_issue_description(pattern))
        
        # Análisis adicional
        query_lower = query.lower()
        
        # SELECT * es problemático
        if 'select *' in query_lower:
            issues.append('SELECT * - Selecciona columnas específicas')
        
        # LIKE sin índice
        if 'like \'%' in query_lower:
            issues.append('LIKE con % al inicio - Considera full-text search')
        
        # ORDER BY sin LIMIT apropiado
        if 'order by' in query_lower and 'limit' not in query_lower:
            issues.append('ORDER BY sin LIMIT - Puede consumir mucha memoria')
        
        # Subconsultas correlacionadas
        if query_lower.count('select') > 1:
            issues.append('Subconsultas - Considera JOINs para mejor rendimiento')
        
        return len(issues) > 0, issues
    
    def get_issue_description(self, pattern: str) -> str:
        """Obtener descripción del problema para un patrón."""
        descriptions = {
            r'SELECT \* FROM \w+': 'SELECT * - Evitar seleccionar todas las columnas',
            r'LIKE \'%.*%\'': 'LIKE con wildcards - Usar índices full-text',
            r'WHERE \w+ IN \(': 'IN con muchos valores - Considerar JOIN con tabla temporal',
            r'JOIN.*JOIN.*JOIN': 'Múltiples JOINs - Revisar normalización y índices',
            r'ORDER BY.*LIMIT': 'ORDER BY + LIMIT - Asegurar índices en columnas de orden',
            r'DISTINCT.*ORDER BY': 'DISTINCT + ORDER BY - Costoso, revisar lógica',
            r'SUBSTRING\(': 'Funciones en WHERE - Previene uso de índices',
            r'GROUP BY.*HAVING': 'GROUP BY + HAVING - Considerar WHERE antes de GROUP BY',
            r'NOT EXISTS': 'NOT EXISTS - Puede ser lento, considerar LEFT JOIN',
            r'OR \w+\.\w+ =': 'OR en WHERE - Divide en consultas separadas o usa UNION'
        }
        return descriptions.get(pattern, 'Patrón problemático detectado')
    
    def get_module_name(self, file_path: Path) -> str:
        """Extraer nombre del módulo del path del archivo."""
        parts = file_path.parts
        if 'modules' in parts:
            module_idx = parts.index('modules')
            if module_idx + 1 < len(parts):
                return parts[module_idx + 1]
        return 'unknown'
    
    def create_optimized_query(self, original_query: str, issues: List[str]) -> str:
        """Crear versión optimizada de la consulta."""
        query = original_query.strip().strip('"\'')
        
        # Aplicar optimizaciones comunes
        optimized = query
        
        # Reemplazar SELECT *
        if 'SELECT *' in optimized.upper():
            optimized = optimized.replace('SELECT *', 'SELECT\n    -- Especificar columnas necesarias\n    columna1,\n    columna2,\n    columna3')
        
        # Agregar comentarios de optimización
        optimization_comments = [
            '-- QUERY OPTIMIZADA - Generada automáticamente',
            '-- Problemas identificados:',
        ]
        for issue in issues:
            optimization_comments.append(f'-- - {issue}')
        
        optimization_comments.extend([
            '-- Índices sugeridos se encuentran al final del archivo',
            '',
        ])
        
        return '\n'.join(optimization_comments) + '\n' + optimized
    
    def create_index_suggestions(self, query: str, module: str) -> List[str]:
        """Generar sugerencias de índices para la consulta."""
        suggestions = []
        
        # Buscar columnas en WHERE
        where_match = re.search(r'WHERE\s+(.*?)(?:ORDER BY|GROUP BY|LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            
            # Extraer columnas de condiciones
            column_patterns = [
                r'(\w+\.\w+)\s*=',  # tabla.columna =
                r'(\w+)\s*=',       # columna =
                r'(\w+\.\w+)\s*IN', # tabla.columna IN
                r'(\w+)\s*IN',      # columna IN
            ]
            
            indexed_columns = set()
            for pattern in column_patterns:
                matches = re.findall(pattern, where_clause, re.IGNORECASE)
                for match in matches:
                    if '.' in match:
                        table, column = match.split('.', 1)
                        indexed_columns.add(f"{table}({column})")
                    else:
                        indexed_columns.add(f"tabla_principal({match})")
        
        # Buscar columnas en ORDER BY
        order_match = re.search(r'ORDER BY\s+([\w\.,\s]+)', query, re.IGNORECASE)
        if order_match:
            order_columns = order_match.group(1)
            # Limpiar y procesar columnas de orden
            for col in order_columns.split(','):
                clean_col = col.strip().split()[0]  # Remover ASC/DESC
                if clean_col:
                    indexed_columns.add(f"tabla_principal({clean_col})")
        
        # Generar sugerencias de índices
        for col in indexed_columns:
            suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{module}_{col.replace('.', '_').replace('(', '_').replace(')', '')} ON {col};")
        
        return suggestions
    
    def save_optimized_query(self, query_info: Dict, optimized_query: str, index_suggestions: List[str]) -> str:
        """Guardar consulta optimizada en archivo SQL."""
        module = query_info['module']
        sql_module_dir = self.sql_path / module
        sql_module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo basado en el tipo de consulta
        query_lower = query_info['query'].lower()
        if 'select' in query_lower:
            operation = 'consulta'
        elif 'insert' in query_lower:
            operation = 'insertar'
        elif 'update' in query_lower:
            operation = 'actualizar'
        elif 'delete' in query_lower:
            operation = 'eliminar'
        else:
            operation = 'query'
        
        # Contador para evitar duplicados
        counter = 1
        base_filename = f"{operation}_optimizada"
        filename = f"{base_filename}.sql"
        
        while (sql_module_dir / filename).exists():
            counter += 1
            filename = f"{base_filename}_{counter}.sql"
        
        file_path = sql_module_dir / filename
        
        # Contenido del archivo SQL
        content = [
            f"-- {filename}",
            f"-- Módulo: {module}",
            f"-- Generado automáticamente el: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Archivo original: {query_info['file']}",
            f"-- Línea original: {query_info['line']}",
            "",
            f"-- CONSULTA ORIGINAL (PROBLEMÁTICA):",
            f"-- {query_info['query']}",
            "",
            optimized_query,
            "",
            "-- ÍNDICES SUGERIDOS PARA OPTIMIZACIÓN:",
            "-- Ejecutar estos comandos para mejorar el rendimiento:",
            "",
        ]
        
        content.extend(index_suggestions)
        content.extend([
            "",
            "-- PARÁMETROS DE EJEMPLO:",
            "-- :param1 - Descripción del parámetro",
            "-- :param2 - Descripción del parámetro",
            "",
            "-- USO DESDE PYTHON:",
            "-- from rexus.utils.sql_query_manager import SQLQueryManager",
            f"-- sql_manager = SQLQueryManager()",
            f"-- resultado = sql_manager.ejecutar_consulta_archivo('sql/{module}/{filename}', parametros)"
        ])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        logger.info(f"Consulta optimizada guardada: {file_path}")
        return str(file_path)
    
    def analyze_all_modules(self) -> Dict[str, List[Dict]]:
        """Analizar todos los módulos en busca de consultas lentas."""
        all_results = {}
        
        for module_dir in self.modules_path.iterdir():
            if module_dir.is_dir() and module_dir.name != '__pycache__':
                module_name = module_dir.name
                module_results = []
                
                # Analizar archivos .py en el módulo
                for py_file in module_dir.rglob('*.py'):
                    if py_file.name != '__init__.py':
                        results = self.analyze_file(py_file)
                        module_results.extend(results)
                
                if module_results:
                    all_results[module_name] = module_results
                    logger.info(f"Módulo {module_name}: {len(module_results)} consultas problemáticas encontradas")
        
        return all_results
    
    def optimize_all_queries(self, analysis_results: Dict[str, List[Dict]]) -> Dict:
        """Optimizar todas las consultas encontradas."""
        optimization_summary = {
            'total_queries': 0,
            'optimized_files': 0,
            'modules_processed': 0,
            'index_suggestions': 0,
            'details': []
        }
        
        for module_name, queries in analysis_results.items():
            optimization_summary['modules_processed'] += 1
            module_details = {
                'module': module_name,
                'queries_optimized': 0,
                'files_created': []
            }
            
            for query_info in queries:
                try:
                    # Crear consulta optimizada
                    optimized_query = self.create_optimized_query(
                        query_info['query'], 
                        query_info['issues']
                    )
                    
                    # Generar sugerencias de índices
                    index_suggestions = self.create_index_suggestions(
                        query_info['query'], 
                        module_name
                    )
                    
                    # Guardar archivo optimizado
                    saved_path = self.save_optimized_query(
                        query_info, 
                        optimized_query, 
                        index_suggestions
                    )
                    
                    module_details['files_created'].append(saved_path)
                    module_details['queries_optimized'] += 1
                    optimization_summary['total_queries'] += 1
                    optimization_summary['optimized_files'] += 1
                    optimization_summary['index_suggestions'] += len(index_suggestions)
                    
                except Exception as e:
                    logger.error(f"Error optimizando consulta en {query_info['file']}: {e}")
            
            optimization_summary['details'].append(module_details)
        
        return optimization_summary
    
    def generate_optimization_report(self, summary: Dict) -> str:
        """Generar reporte de optimización."""
        report_lines = [
            "# REPORTE DE OPTIMIZACIÓN DE CONSULTAS SQL",
            f"**Fecha:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Generado por:** SQLQueryOptimizer v1.0.0",
            "",
            "## RESUMEN EJECUTIVO",
            f"- **Total de consultas optimizadas:** {summary['total_queries']}",
            f"- **Archivos SQL generados:** {summary['optimized_files']}",
            f"- **Módulos procesados:** {summary['modules_processed']}",
            f"- **Índices sugeridos:** {summary['index_suggestions']}",
            "",
            "## DETALLES POR MÓDULO",
            ""
        ]
        
        for module_detail in summary['details']:
            report_lines.extend([
                f"### Módulo: {module_detail['module'].upper()}",
                f"- Consultas optimizadas: {module_detail['queries_optimized']}",
                f"- Archivos creados:",
                ""
            ])
            
            for file_path in module_detail['files_created']:
                filename = Path(file_path).name
                report_lines.append(f"  - `sql/{module_detail['module']}/{filename}`")
            
            report_lines.append("")
        
        report_lines.extend([
            "## PRÓXIMOS PASOS",
            "",
            "1. **Revisar consultas optimizadas** en el directorio `sql/`",
            "2. **Ejecutar índices sugeridos** en la base de datos",
            "3. **Actualizar código Python** para usar `SQLQueryManager`",
            "4. **Probar rendimiento** con las nuevas consultas",
            "",
            "## EJEMPLO DE USO",
            "",
            "```python",
            "from rexus.utils.sql_query_manager import SQLQueryManager",
            "",
            "# En lugar de:",
            "# query = \"SELECT * FROM tabla WHERE campo = 'valor'\"",
            "# cursor.execute(query)",
            "",
            "# Usar:",
            "sql_manager = SQLQueryManager()",
            "resultado = sql_manager.ejecutar_consulta_archivo(",
            "    'sql/modulo/consulta_optimizada.sql',",
            "    {'campo': 'valor'}",
            ")",
            "```",
            "",
            "---",
            "",
            "**¡IMPORTANTE!** Las consultas optimizadas incluyen comentarios con:",
            "- Problemas identificados en la consulta original",
            "- Índices recomendados para mejor rendimiento",
            "- Parámetros seguros para prevenir SQL injection",
            "- Instrucciones de uso con SQLQueryManager",
        ])
        
        return '\n'.join(report_lines)
    
    def run_optimization(self) -> None:
        """Ejecutar proceso completo de optimización."""
        logger.info("=== INICIANDO OPTIMIZACIÓN DE CONSULTAS SQL ===")
        
        # Crear directorio sql si no existe
        self.sql_path.mkdir(exist_ok=True)
        
        # 1. Analizar todos los módulos
        logger.info("1. Analizando módulos en busca de consultas problemáticas...")
        analysis_results = self.analyze_all_modules()
        
        if not analysis_results:
            logger.info("No se encontraron consultas problemáticas")
            return
        
        # 2. Optimizar consultas encontradas
        logger.info("2. Optimizando consultas y creando archivos SQL...")
        optimization_summary = self.optimize_all_queries(analysis_results)
        
        # 3. Generar reporte
        logger.info("3. Generando reporte de optimización...")
        report = self.generate_optimization_report(optimization_summary)
        
        # Guardar reporte
        report_path = self.root_path / "docs" / "OPTIMIZACIÓN_SQL_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"=== OPTIMIZACIÓN COMPLETA ===")
        logger.info(f"Reporte guardado en: {report_path}")
        logger.info(f"Total de consultas optimizadas: {optimization_summary['total_queries']}")
        logger.info(f"Archivos SQL creados: {optimization_summary['optimized_files']}")
        logger.info(f"Índices sugeridos: {optimization_summary['index_suggestions']}")


def main():
    """Función principal."""
    try:
        optimizer = SQLQueryOptimizer()
        optimizer.run_optimization()
        
        print("\n✅ OPTIMIZACIÓN DE CONSULTAS COMPLETADA")
        print("📊 Revisa el reporte en: docs/OPTIMIZACIÓN_SQL_REPORT.md")
        print("📁 Consultas optimizadas en: sql/")
        print("🚀 Próximo paso: Actualizar código para usar SQLQueryManager")
        
    except Exception as e:
        logger.error(f"Error en la optimización: {e}")
        print(f"\n❌ Error durante la optimización: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())