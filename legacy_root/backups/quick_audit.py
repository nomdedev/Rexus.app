#!/usr/bin/env python3
"""
Auditoría rápida para detectar problemas arquitecturales
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

def main():
    """Auditoría rápida del proyecto."""
    root = Path('.')
    issues = defaultdict(list)
    
    # Patrones críticos
    patterns = {
        'exec_eval': [r'\bexec\s*\(', r'\beval\s*\('],
        'sql_injection': [r'cursor\.execute\s*\(\s*f["\']', r'cursor\.execute\s*\([^,)]*\+'],
        'generic_exceptions': [r'except\s+Exception\s*:', r'except\s*:'],
        'print_statements': [r'\bprint\s*\('],
        'hardcoded_secrets': [r'password\s*=\s*["\'][^"\']+["\']'],
        'todos': [r'#\s*(TODO|FIXME|XXX|HACK)']
    }
    
    total_files = 0
    print("AUDITORIA COMPREHIVA - REXUS.APP")
    print("=" * 50)
    
    for py_file in root.rglob('*.py'):
        # Skip test files and tools for some patterns
        skip_for_prints = any(x in str(py_file) for x in ['test', 'tools', 'scripts'])
        
        total_files += 1
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for issue_type, type_patterns in patterns.items():
                # Skip print detection in test/tool files
                if issue_type == 'print_statements' and skip_for_prints:
                    continue
                    
                for pattern in type_patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues[issue_type].append({
                            'file': str(py_file.relative_to(root)),
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(0)[:50]
                        })
                        
            # Análisis AST para funciones largas y complejidad
            try:
                import ast
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Funciones largas
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            length = node.end_lineno - node.lineno
                            if length > 50:
                                issues['long_functions'].append({
                                    'file': str(py_file.relative_to(root)),
                                    'line': node.lineno,
                                    'function': node.name,
                                    'length': length
                                })
                        
                        # Complejidad alta (simplificada)
                        complexity = 1
                        for child in ast.walk(node):
                            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                                complexity += 1
                            elif isinstance(child, ast.Try):
                                complexity += len(getattr(child, 'handlers', []))
                        
                        if complexity > 15:
                            issues['high_complexity'].append({
                                'file': str(py_file.relative_to(root)),
                                'line': node.lineno,
                                'function': node.name,
                                'complexity': complexity
                            })
                            
                    # Bare except
                    elif isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                issues['bare_except'].append({
                                    'file': str(py_file.relative_to(root)),
                                    'line': handler.lineno
                                })
                                
            except Exception:
                pass
                
        except Exception:
            continue
    
    # Mostrar resultados
    total_issues = sum(len(issues_list) for issues_list in issues.values())
    
    print(f"Archivos analizados: {total_files}")
    print(f"TOTAL PROBLEMAS ENCONTRADOS: {total_issues}")
    print()
    
    # Problemas por severidad
    critical_count = len(issues['exec_eval']) + len(issues['sql_injection'])
    high_count = len(issues['generic_exceptions']) + len(issues['bare_except']) + len(issues['hardcoded_secrets'])
    medium_count = len(issues['high_complexity']) + len(issues['long_functions'])
    low_count = len(issues['print_statements']) + len(issues['todos'])
    
    print("PROBLEMAS POR SEVERIDAD:")
    print(f"  CRITICOS: {critical_count} (exec/eval, SQL injection)")
    print(f"  ALTOS: {high_count} (except genéricos, secrets)")
    print(f"  MEDIOS: {medium_count} (complejidad, funciones largas)")
    print(f"  BAJOS: {low_count} (prints, TODOs)")
    print()
    
    print("TOP PROBLEMAS POR CATEGORIA:")
    for category, items in issues.items():
        if items:
            print(f"  {category}: {len(items)} ocurrencias")
            # Mostrar primeros 3 ejemplos para categorías críticas
            if category in ['exec_eval', 'sql_injection', 'generic_exceptions'] and len(items) <= 10:
                for item in items[:3]:
                    print(f"    -> {item['file']}:{item['line']}")
    
    print()
    if total_issues > 100:
        print(f"CONFIRMADO: {total_issues} problemas arquitecturales encontrados")
        print("Estos son los problemas que los tests automaticos no detectan")
        print("Se requiere correccion manual y sistematica")
    
    return total_issues

if __name__ == '__main__':
    total = main()
    sys.exit(0)
