#!/usr/bin/env python3
"""
Script para detectar variables potencialmente undefined en archivos Python
"""

import os
import ast
import re
from pathlib import Path

class UndefinedVarDetector(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.defined_vars = set()
        self.used_vars = set()
        
    def visit_FunctionDef(self, node):
        # Resetear para cada función
        old_defined = self.defined_vars.copy()
        old_used = self.used_vars.copy()
        
        # Parámetros de función están definidos
        for arg in node.args.args:
            self.defined_vars.add(arg.arg)
            
        self.generic_visit(node)
        
        # Restaurar estado
        self.defined_vars = old_defined
        self.used_vars = old_used
        
    def visit_Assign(self, node):
        # Variables asignadas están definidas
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
            # Verificar si la variable está definida
            if node.id not in self.defined_vars and node.id not in ['self', 'cls']:
                # Variables problemáticas comunes
                if node.id in ['commit', 'rollback', 'cursor', 'connection']:
                    self.issues.append({
                        'type': 'undefined_var',
                        'var': node.id,
                        'line': node.lineno,
                        'severity': 'high'
                    })

def scan_file(filepath):
    """Escanea un archivo Python para detectar problemas"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Detectar problemas comunes con regex
        
        # 1. str(None) o concatenación con None
        none_issues = re.finditer(r'str\(.*None.*\)', content)
        for match in none_issues:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'type': 'str_none',
                'line': line_num,
                'text': match.group(),
                'severity': 'medium'
            })
            
        # 2. Variables commit/rollback sin self
        commit_issues = re.finditer(r'(?<!self\.)(?<!connection\.)commit\(\)', content)
        for match in commit_issues:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'type': 'undefined_commit',
                'line': line_num,
                'text': match.group(),
                'severity': 'high'
            })
            
        rollback_issues = re.finditer(r'(?<!self\.)(?<!connection\.)rollback\(\)', content)
        for match in rollback_issues:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'type': 'undefined_rollback',
                'line': line_num,
                'text': match.group(),
                'severity': 'high'
            })
            
        # 3. Variables cursor sin definir
        cursor_issues = re.finditer(r'(?<!self\.)cursor\.', content)
        for match in cursor_issues:
            line_num = content[:match.start()].count('\n') + 1
            # Verificar si cursor está definido en las líneas anteriores
            lines_before = content[:match.start()].split('\n')
            cursor_defined = any('cursor =' in line for line in lines_before[-20:])
            if not cursor_defined:
                issues.append({
                    'type': 'undefined_cursor',
                    'line': line_num,
                    'text': match.group(),
                    'severity': 'high'
                })
                
        # 4. Imports faltantes
        if 'sqlite3' in content and 'import sqlite3' not in content:
            issues.append({
                'type': 'missing_import',
                'line': 1,
                'text': 'sqlite3 used but not imported',
                'severity': 'high'
            })
            
        # Usar AST para detección más avanzada
        try:
            tree = ast.parse(content)
            detector = UndefinedVarDetector(str(filepath))
            detector.visit(tree)
            issues.extend(detector.issues)
        except SyntaxError:
            pass
            
    except Exception as e:
        issues.append({
            'type': 'scan_error',
            'line': 0,
            'text': f'Error escaneando archivo: {e}',
            'severity': 'low'
        })
        
    return issues

def main():
    print("DETECTANDO VARIABLES UNDEFINED Y PROBLEMAS DE TIPOS...")
    
    # Directorios a escanear
    dirs_to_scan = [
        'rexus/core',
        'rexus/models', 
        'rexus/modules',
        'rexus/utils'
    ]
    
    all_issues = {}
    total_files = 0
    total_issues = 0
    
    for dir_path in dirs_to_scan:
        full_path = Path(dir_path)
        if not full_path.exists():
            continue
            
        for py_file in full_path.rglob('*.py'):
            total_files += 1
            issues = scan_file(py_file)
            if issues:
                all_issues[str(py_file)] = issues
                total_issues += len(issues)
                
    # Mostrar resultados
    print(f"\nRESUMEN:")
    print(f"Archivos escaneados: {total_files}")
    print(f"Archivos con problemas: {len(all_issues)}")
    print(f"Total de problemas: {total_issues}")
    
    # Mostrar problemas por severidad
    high_severity = []
    medium_severity = []
    low_severity = []
    
    for filepath, issues in all_issues.items():
        for issue in issues:
            issue['file'] = filepath
            if issue['severity'] == 'high':
                high_severity.append(issue)
            elif issue['severity'] == 'medium':
                medium_severity.append(issue)
            else:
                low_severity.append(issue)
                
    print(f"\nPROBLEMAS CRITICOS ({len(high_severity)}):")
    for issue in high_severity[:10]:  # Mostrar solo los primeros 10
        print(f"  {issue['file']}:{issue['line']} - {issue['type']}")
        
    print(f"\nPROBLEMAS MEDIOS ({len(medium_severity)}):")
    for issue in medium_severity[:10]:  # Mostrar solo los primeros 10
        print(f"  {issue['file']}:{issue['line']} - {issue['type']}")
        
    # Guardar reporte detallado
    with open('tools/undefined_vars_report.txt', 'w', encoding='utf-8') as f:
        f.write("REPORTE DE VARIABLES UNDEFINED\n")
        f.write("=" * 50 + "\n\n")
        
        for filepath, issues in all_issues.items():
            f.write(f"\n {filepath}\n")
            f.write("-" * 50 + "\n")
            for issue in issues:
                f.write(f"  Linea {issue['line']:3d}: {issue['type']} - {issue.get('text', '')}\n")
                
    print(f"\nReporte detallado guardado en: tools/undefined_vars_report.txt")
    print(f"Empezando correcciones automaticas...")
    
    return high_severity, medium_severity

if __name__ == "__main__":
    main()