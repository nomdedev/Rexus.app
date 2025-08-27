#!/usr/bin/env python3
"""
Script para encontrar posibles variables no definidas en archivos Python
Se enfoca en archivos con muchas queries SQL hardcodeadas
"""

import ast
import re
from pathlib import Path

def analyze_file_for_undefined_vars(file_path):
    """Analiza un archivo Python buscando variables potencialmente no definidas"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Buscar patrones comunes de variables no definidas
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith('#'):
                continue
            
            # Look for undefined variables in common patterns
            patterns = [
                r'cursor\.execute\([^)]*\bparams\b',  # usando params sin definir
                r'cursor\.execute\([^)]*\bquery\b.*\bparams\b',  # query y params
                r'self\.\w+\([^)]*\bparams\b',  # métodos con params no definido
                r'return\s+\w+$',  # return de variable que puede no estar definida
                r'except.*\be\b.*:',  # except sin as e
                r'\.commit\(\)\s*$',  # commit sin verificar conexión
            ]
            
            for pattern in patterns:
                if re.search(pattern, line):
                    issues.append({
                        'line': line_num,
                        'content': stripped,
                        'type': 'potential_undefined_var',
                        'pattern': pattern
                    })
        
        # Also try AST parsing to catch real syntax errors
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                'line': e.lineno,
                'content': 'SyntaxError',
                'type': 'syntax_error', 
                'error': str(e)
            })
        except Exception as e:
            issues.append({
                'line': 0,
                'content': 'ParseError',
                'type': 'parse_error',
                'error': str(e)
            })
        
        return issues
        
    except Exception as e:
        return [{'line': 0, 'content': f'FileError: {e}', 'type': 'file_error', 'error': str(e)}]

def main():
    """Busca archivos problemáticos y los analiza"""
    
    # Archivos con muchas queries que pueden tener problemas
    problematic_files = [
        'rexus/core/security.py',
        'rexus/core/auth.py',
        'rexus/modules/07_vidrios/model.py',
        'rexus/modules/02_inventario/model.py',
        'rexus/modules/12_administracion/model.py',
        'rexus/modules/01_obras/model.py'
    ]
    
    print("=== ANÁLISIS DE VARIABLES NO DEFINIDAS ===\n")
    
    total_issues = 0
    
    for file_path in problematic_files:
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
            
        print(f"Analizando: {file_path}")
        issues = analyze_file_for_undefined_vars(path_obj)
        
        if issues:
            print(f"  *** {len(issues)} posibles problemas encontrados ***")
            for issue in issues[:5]:  # Show first 5
                print(f"    Línea {issue['line']}: {issue['content'][:60]}...")
                if 'error' in issue:
                    print(f"      Error: {issue['error']}")
            
            if len(issues) > 5:
                print(f"    ... y {len(issues) - 5} más")
            
            total_issues += len(issues)
        else:
            print(f"  ✓ Sin problemas detectados")
        
        print()
    
    print(f"*** TOTAL: {total_issues} posibles problemas encontrados ***")
    
    if total_issues > 0:
        print("\n*** RECOMENDACIÓN ***")
        print("Revisar archivos manualmente para confirmar problemas reales.")

if __name__ == "__main__":
    main()