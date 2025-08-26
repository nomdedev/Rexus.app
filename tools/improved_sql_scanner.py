#!/usr/bin/env python3
"""
Script mejorado para detectar y migrar SQL hardcodeado automáticamente
Incluye mejor detección de patrones y análisis completo del código

Fecha: 26/08/2025
Objetivo: Completar la externalización de queries SQL en todo el proyecto
"""

import os
import re
from pathlib import Path
import json
from typing import Dict, List, Tuple, Set

class ImprovedSQLScanner:
    def __init__(self):
        self.sql_patterns = [
            # Patrones mejorados para detectar SQL
            r'cursor\.execute\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'][^)]*\)',
            r'execute\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'][^)]*\)',
            r'query\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'sql\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'](?=.*execute)',
            # Multiline queries
            r'["\'"]{3}([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'"]{3}',
            r'f["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            # Queries con format o %
            r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*%[^"\']*)["\']',
            r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*\{[^}]*\}[^"\']*)["\']',
        ]
        
        self.exclude_patterns = [
            r'#.*',  # Comments
            r'""".*?"""',  # Docstrings
            r"'''.*?'''",  # Docstrings
            r'sql_manager\.get_query',  # Already using external SQL
            r'\.sql',  # SQL file references
        ]
        
        self.results = {
            'files_analyzed': 0,
            'files_with_sql': 0,
            'total_queries_found': 0,
            'modules': {}
        }

    def should_exclude_line(self, line: str) -> bool:
        """Check if line should be excluded from SQL detection"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def extract_sql_from_file(self, file_path: Path) -> List[Dict]:
        """Extract SQL queries from a Python file with improved detection"""
        print(f"Analyzing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        queries = []
        lines = content.split('\n')
        
        # Analyze line by line for better context
        for line_num, line in enumerate(lines, 1):
            if self.should_exclude_line(line.strip()):
                continue
                
            for pattern in self.sql_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    sql_content = match.group(1).strip()
                    
                    # Skip very short or obviously non-SQL strings
                    if len(sql_content) < 10:
                        continue
                        
                    # Check if it contains SQL keywords
                    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'JOIN']
                    if not any(keyword in sql_content.upper() for keyword in sql_keywords):
                        continue
                    
                    query_info = {
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'sql_content': sql_content,
                        'pattern_matched': pattern,
                        'full_match': match.group(0)
                    }
                    
                    queries.append(query_info)
                    print(f"  Found SQL at line {line_num}: {sql_content[:50]}...")
        
        return queries

    def analyze_module(self, module_path: Path) -> Dict:
        """Analyze a complete module for SQL queries"""
        module_name = module_path.name
        module_info = {
            'path': str(module_path),
            'files': {},
            'total_queries': 0
        }
        
        # Find Python files in module
        python_files = list(module_path.glob('**/*.py'))
        
        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue
                
            self.results['files_analyzed'] += 1
            queries = self.extract_sql_from_file(py_file)
            
            if queries:
                self.results['files_with_sql'] += 1
                relative_path = py_file.relative_to(module_path)
                module_info['files'][str(relative_path)] = {
                    'query_count': len(queries),
                    'queries': queries
                }
                module_info['total_queries'] += len(queries)
                self.results['total_queries_found'] += len(queries)
        
        return module_info

    def scan_project(self, base_path: Path = None) -> Dict:
        """Scan entire project for hardcoded SQL"""
        if base_path is None:
            base_path = Path('.')
            
        print("=== ANÁLISIS COMPLETO DE SQL HARDCODEADO ===\n")
        
        # Scan modules directory
        modules_path = base_path / 'rexus' / 'modules'
        if modules_path.exists():
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('_'):
                    print(f"\n--- Analizando módulo: {module_dir.name} ---")
                    module_info = self.analyze_module(module_dir)
                    if module_info['total_queries'] > 0:
                        self.results['modules'][module_dir.name] = module_info
        
        # Also scan core and utils directories
        for core_dir in ['rexus/core', 'rexus/utils', 'rexus/ui']:
            core_path = base_path / core_dir
            if core_path.exists():
                print(f"\n--- Analizando directorio: {core_dir} ---")
                module_info = self.analyze_module(core_path)
                if module_info['total_queries'] > 0:
                    dir_name = core_dir.replace('/', '_')
                    self.results['modules'][dir_name] = module_info
        
        return self.results

    def generate_report(self, output_file: str = 'sql_analysis_report.json'):
        """Generate detailed report of findings"""
        print(f"\n=== RESUMEN DEL ANÁLISIS ===")
        print(f"Archivos analizados: {self.results['files_analyzed']}")
        print(f"Archivos con SQL hardcodeado: {self.results['files_with_sql']}")
        print(f"Total queries encontradas: {self.results['total_queries_found']}")
        
        print(f"\n=== DESGLOSE POR MÓDULO ===")
        for module_name, module_info in self.results['modules'].items():
            print(f"\n{module_name}: {module_info['total_queries']} queries")
            for file_path, file_info in module_info['files'].items():
                print(f"  - {file_path}: {file_info['query_count']} queries")
        
        # Save detailed JSON report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte detallado guardado en: {output_file}")

    def generate_migration_plan(self):
        """Generate specific migration plan for each module"""
        print(f"\n=== PLAN DE MIGRACIÓN SQL ===")
        
        for module_name, module_info in self.results['modules'].items():
            if module_info['total_queries'] == 0:
                continue
                
            print(f"\n--- MÓDULO: {module_name.upper()} ---")
            print(f"Directorio SQL: sql/{module_name}/")
            print(f"Queries a migrar: {module_info['total_queries']}")
            
            for file_path, file_info in module_info['files'].items():
                print(f"\nArchivo: {file_path}")
                for i, query in enumerate(file_info['queries']):
                    sql_type = 'unknown'
                    sql_upper = query['sql_content'].upper()
                    
                    if 'SELECT' in sql_upper and 'COUNT' in sql_upper:
                        sql_type = 'count'
                    elif 'SELECT' in sql_upper:
                        sql_type = 'select'
                    elif 'INSERT' in sql_upper:
                        sql_type = 'insert'
                    elif 'UPDATE' in sql_upper:
                        sql_type = 'update'
                    elif 'DELETE' in sql_upper:
                        sql_type = 'delete'
                    
                    suggested_name = f"{sql_type}_{module_name}_{i+1}"
                    print(f"  Línea {query['line_number']}: {suggested_name}.sql")
                    print(f"    SQL: {query['sql_content'][:80]}...")

def main():
    """Main execution function"""
    scanner = ImprovedSQLScanner()
    
    # Scan the project
    results = scanner.scan_project()
    
    # Generate reports
    scanner.generate_report('tools/sql_analysis_complete.json')
    scanner.generate_migration_plan()
    
    # Summary
    if results['total_queries_found'] > 0:
        print(f"\n*** ACCION REQUERIDA ***")
        print(f"Se encontraron {results['total_queries_found']} queries SQL hardcodeadas")
        print(f"en {results['files_with_sql']} archivos que deben ser migradas.")
        print(f"\nProximo paso: ejecutar migrate_sql_to_files.py")
    else:
        print(f"\n*** EXCELENTE ***")
        print(f"No se encontraron queries SQL hardcodeadas.")
        print(f"El proyecto esta completamente externalizado.")

if __name__ == "__main__":
    main()