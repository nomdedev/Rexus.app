#!/usr/bin/env python3
"""
Script para validar que la migración SQL se completó correctamente
Verifica que no queden queries hardcodeadas en el código

Fecha: 26/08/2025
"""

import re
from pathlib import Path
import json

class SQLMigrationValidator:
    def __init__(self):
        self.hardcoded_patterns = [
            r'cursor\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
        ]
        
        # Excluir estos patrones (ya externalizados o casos especiales)
        self.exclude_patterns = [
            r'sql_manager\.get_query',
            r'ejecutar_consulta_archivo',
            r'#.*',  # Comments
            r'""".*?"""',  # Docstrings
            r"'''.*?'''",  # Docstrings
            r'logger\.',  # Log messages
            r'print\(',   # Print statements
            r'\.error\(', # Error messages
            r'f["\'].*Error.*',  # Error messages
        ]

    def scan_file_for_hardcoded_sql(self, file_path: Path) -> list:
        """Scan file for remaining hardcoded SQL"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return []

        remaining_queries = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip excluded patterns
            skip_line = False
            for exclude in self.exclude_patterns:
                if re.search(exclude, line, re.IGNORECASE):
                    skip_line = True
                    break
            
            if skip_line:
                continue
            
            # Check for hardcoded SQL
            for pattern in self.hardcoded_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    sql_content = match.group(1).strip()
                    
                    # Validate it's real SQL
                    if len(sql_content) < 15:
                        continue
                    
                    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'UPDATE', 'SET', 'DELETE', 'JOIN']
                    keyword_count = sum(1 for kw in sql_keywords if kw in sql_content.upper())
                    
                    if keyword_count >= 2:
                        remaining_queries.append({
                            'line': line_num,
                            'sql': sql_content,
                            'context': line.strip()
                        })
        
        return remaining_queries

    def validate_project(self) -> dict:
        """Validate entire project for remaining hardcoded SQL"""
        results = {
            'total_files_scanned': 0,
            'files_with_issues': 0,
            'total_remaining_queries': 0,
            'issues_by_module': {}
        }
        
        # Scan modules
        modules_path = Path('rexus/modules')
        if modules_path.exists():
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('_'):
                    module_issues = self._scan_module(module_dir)
                    if module_issues['remaining_queries'] > 0:
                        results['issues_by_module'][module_dir.name] = module_issues
                        results['files_with_issues'] += module_issues['files_with_issues']
                        results['total_remaining_queries'] += module_issues['remaining_queries']
                    
                    results['total_files_scanned'] += module_issues['files_scanned']
        
        # Scan core and utils
        for core_dir in ['rexus/core', 'rexus/utils']:
            core_path = Path(core_dir)
            if core_path.exists():
                module_issues = self._scan_module(core_path)
                if module_issues['remaining_queries'] > 0:
                    results['issues_by_module'][core_dir.replace('/', '_')] = module_issues
                    results['files_with_issues'] += module_issues['files_with_issues']
                    results['total_remaining_queries'] += module_issues['remaining_queries']
                
                results['total_files_scanned'] += module_issues['files_scanned']
        
        return results

    def _scan_module(self, module_path: Path) -> dict:
        """Scan a module for issues"""
        module_results = {
            'files_scanned': 0,
            'files_with_issues': 0,
            'remaining_queries': 0,
            'issue_files': {}
        }
        
        for py_file in module_path.glob('**/*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            module_results['files_scanned'] += 1
            remaining = self.scan_file_for_hardcoded_sql(py_file)
            
            if remaining:
                module_results['files_with_issues'] += 1
                module_results['remaining_queries'] += len(remaining)
                module_results['issue_files'][str(py_file.relative_to(module_path))] = remaining
        
        return module_results

    def generate_report(self, results: dict):
        """Generate validation report"""
        print("=== VALIDACION DE MIGRACION SQL ===")
        print(f"Archivos escaneados: {results['total_files_scanned']}")
        print(f"Archivos con problemas: {results['files_with_issues']}")
        print(f"Queries SQL hardcodeadas restantes: {results['total_remaining_queries']}")
        
        if results['total_remaining_queries'] == 0:
            print("\n*** EXCELENTE ***")
            print("No se encontraron queries SQL hardcodeadas.")
            print("La migracion se completo exitosamente!")
            return True
        
        print(f"\n*** ATENCION REQUERIDA ***")
        print("Aun hay queries SQL hardcodeadas que necesitan migrar:")
        
        for module_name, issues in results['issues_by_module'].items():
            print(f"\n--- MODULO: {module_name.upper()} ---")
            print(f"Queries pendientes: {issues['remaining_queries']}")
            
            for file_path, file_issues in issues['issue_files'].items():
                print(f"\nArchivo: {file_path}")
                for issue in file_issues[:3]:  # Solo mostrar primeras 3 por archivo
                    print(f"  Linea {issue['line']}: {issue['sql'][:60]}...")
                
                if len(file_issues) > 3:
                    print(f"  ... y {len(file_issues) - 3} mas")
        
        # Save detailed report
        with open('tools/sql_validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte detallado guardado en: tools/sql_validation_report.json")
        return False

def main():
    validator = SQLMigrationValidator()
    results = validator.validate_project()
    success = validator.generate_report(results)
    
    if success:
        print("\n=== ESTADO: COMPLETO ===")
        return 0
    else:
        print("\n=== ESTADO: REQUIERE ATENCION ===")
        return 1

if __name__ == "__main__":
    exit(main())