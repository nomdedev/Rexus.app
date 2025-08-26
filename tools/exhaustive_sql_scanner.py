#!/usr/bin/env python3
"""
Scanner exhaustivo para encontrar TODAS las queries SQL hardcodeadas
Sin filtros restrictivos - encuentra todo lo que puede ser SQL
"""

import re
from pathlib import Path
import json

class ExhaustiveSQLScanner:
    def __init__(self):
        # Patrones más amplios para capturar TODO tipo de SQL
        self.sql_patterns = [
            # Queries básicas con execute
            r'execute\s*\([^)]*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            r'cursor\.execute\s*\([^)]*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            
            # Variables que contienen SQL  
            r'(?:sql|query)\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            
            # F-strings con SQL
            r'f["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\']',
            
            # Strings multilinea con SQL
            r'["\'"]{3}([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[^"\']*)["\'"]{3}',
            
            # SQL en cualquier string que contenga palabras clave
            r'["\']([^"\']*(?:FROM|WHERE|JOIN|GROUP BY|ORDER BY|HAVING|VALUES|SET)[^"\']*)["\']',
            
            # Queries que empiezan directamente con SQL keywords
            r'["\']((SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+[^"\']+)["\']',
            
            # SQL con format strings
            r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)\s+[^"\']*\{[^}]*\}[^"\']*)["\']',
            
            # Cualquier string largo que contenga múltiples keywords SQL
            r'["\']([^"\']{20,}(?:SELECT|INSERT|UPDATE|DELETE)[^"\']{10,})["\']',
        ]
        
        # Solo excluir cosas obvias - ser muy permisivo
        self.exclude_patterns = [
            r'#.*',  # Comments  
            r'sql_manager\.get_query',  # Ya migrado
            r'ejecutar_consulta_archivo',  # Ya migrado
            r'\.sql["\']',  # Referencias a archivos .sql
        ]

    def scan_file(self, file_path: Path) -> dict:
        """Scan archivo individual de manera exhaustiva"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return {'queries': [], 'error': 'Could not read file'}

        queries = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip solo cosas muy obvias
            skip = False
            for exclude in self.exclude_patterns:
                if re.search(exclude, line, re.IGNORECASE):
                    skip = True
                    break
            
            if skip:
                continue

            # Buscar con todos los patrones
            for pattern_num, pattern in enumerate(self.sql_patterns):
                try:
                    matches = re.finditer(pattern, line, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        sql_content = match.group(1).strip()
                        
                        # Validaciones mínimas - ser muy permisivo
                        if len(sql_content) < 5:
                            continue
                            
                        queries.append({
                            'line': line_num,
                            'pattern': pattern_num + 1,
                            'sql': sql_content,
                            'context': line.strip(),
                            'full_match': match.group(0)
                        })
                except Exception as e:
                    continue
        
        return {'queries': queries, 'total': len(queries)}

    def scan_project(self) -> dict:
        """Scan todo el proyecto de manera exhaustiva"""
        results = {
            'total_files': 0,
            'files_with_sql': 0,
            'total_queries': 0,
            'modules': {}
        }
        
        # Scanear todo rexus/
        rexus_path = Path('rexus')
        if rexus_path.exists():
            for py_file in rexus_path.glob('**/*.py'):
                if '__pycache__' in str(py_file):
                    continue
                
                results['total_files'] += 1
                file_result = self.scan_file(py_file)
                
                if file_result['total'] > 0:
                    results['files_with_sql'] += 1
                    results['total_queries'] += file_result['total']
                    
                    # Organizar por módulo
                    parts = py_file.parts
                    if len(parts) >= 2:
                        module = parts[1] if parts[1] != 'modules' else (parts[2] if len(parts) >= 3 else 'unknown')
                    else:
                        module = 'root'
                    
                    if module not in results['modules']:
                        results['modules'][module] = {'files': {}, 'total_queries': 0}
                    
                    rel_path = str(py_file.relative_to(Path('rexus')))
                    results['modules'][module]['files'][rel_path] = file_result
                    results['modules'][module]['total_queries'] += file_result['total']
        
        return results

    def generate_detailed_report(self, results: dict):
        """Generar reporte detallado de findings"""
        print("=== ANÁLISIS EXHAUSTIVO DE SQL HARDCODEADO ===")
        print(f"Archivos escaneados: {results['total_files']}")
        print(f"Archivos con SQL: {results['files_with_sql']}")
        print(f"Total queries encontradas: {results['total_queries']}")
        
        if results['total_queries'] == 0:
            print("\n✅ No se encontraron queries SQL hardcodeadas")
            return
        
        print(f"\n*** QUERIES SQL HARDCODEADAS ENCONTRADAS ***")
        
        for module_name, module_data in results['modules'].items():
            if module_data['total_queries'] > 0:
                print(f"\n--- MÓDULO: {module_name.upper()} ---")
                print(f"Total queries: {module_data['total_queries']}")
                
                for file_path, file_data in module_data['files'].items():
                    print(f"\nArchivo: {file_path}")
                    print(f"Queries: {file_data['total']}")
                    
                    # Mostrar algunas queries como ejemplo
                    for query in file_data['queries'][:3]:  # Solo primeras 3
                        print(f"  Línea {query['line']}: {query['sql'][:80]}...")
                    
                    if len(file_data['queries']) > 3:
                        print(f"  ... y {len(file_data['queries']) - 3} más")
        
        # Guardar reporte completo
        with open('tools/exhaustive_sql_report.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte completo guardado en: tools/exhaustive_sql_report.json")

def main():
    scanner = ExhaustiveSQLScanner()
    results = scanner.scan_project()
    scanner.generate_detailed_report(results)
    
    return results['total_queries']

if __name__ == "__main__":
    total = main()
    print(f"\n*** RESULTADO: {total} queries SQL hardcodeadas encontradas ***")