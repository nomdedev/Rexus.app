#!/usr/bin/env python3
"""
Script para identificar y corregir problemas de logger en módulos de Rexus.app
"""

import os
import re
import glob

def analyze_file_for_logger_issues(file_path):
    """
    Analiza un archivo Python para identificar problemas de logger.
    Retorna información sobre los problemas encontrados.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': f"Error leyendo archivo: {e}"}
    
    issues = []
    lines = content.split('\n')
    
    # Verificar si hay definición de self.logger
    has_self_logger = bool(re.search(r'self\.logger\s*=', content))
    
    # Verificar si hay logger global
    has_global_logger = bool(re.search(r'^logger\s*=\s*logging\.getLogger', content, re.MULTILINE))
    
    # Buscar usos de logger.info, logger.error, etc.
    logger_usage = re.findall(r'logger\.(info|error|warning|debug|critical)', content)
    
    # Buscar métodos de clase (indentados)
    class_methods = []
    in_class = False
    for i, line in enumerate(lines, 1):
        # Detectar inicio de clase
        if re.match(r'^class\s+\w+.*:', line):
            in_class = True
        # Detectar método de clase
        elif in_class and re.match(r'\s+def\s+\w+.*:', line):
            class_methods.append(i)
        # Detectar fin de clase (nueva clase o línea no indentada que no sea comentario/vacía)
        elif in_class and re.match(r'^[a-zA-Z_]', line) and not line.strip().startswith('#'):
            in_class = False
    
    # Buscar usos incorrectos de logger. en métodos de clase
    incorrect_usage = []
    if has_self_logger and logger_usage:
        for i, line in enumerate(lines, 1):
            if 'logger.' in line and any(abs(i - method_line) <= 50 for method_line in class_methods):
                # Verificar que la línea esté indentada (dentro de un método)
                if line.startswith('    ') or line.startswith('\t'):
                    incorrect_usage.append((i, line.strip()))
    
    return {
        'file_path': file_path,
        'has_self_logger': has_self_logger,
        'has_global_logger': has_global_logger,
        'logger_usage_count': len(logger_usage),
        'incorrect_usage': incorrect_usage,
        'needs_fixing': has_self_logger and len(incorrect_usage) > 0
    }

def main():
    """Función principal para analizar todos los archivos en rexus/modules/"""
    base_path = r"D:\martin\Proyectos\Rexus.app\rexus\modules"
    
    # Buscar todos los archivos Python
    python_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Analizando {len(python_files)} archivos Python en rexus/modules/")
    print("=" * 80)
    
    files_with_issues = []
    total_issues = 0
    
    for file_path in sorted(python_files):
        analysis = analyze_file_for_logger_issues(file_path)
        
        if analysis.get('error'):
            print(f"ERROR: {file_path}")
            print(f"   {analysis['error']}")
            continue
            
        if analysis['needs_fixing']:
            files_with_issues.append(analysis)
            issue_count = len(analysis['incorrect_usage'])
            total_issues += issue_count
            
            rel_path = os.path.relpath(file_path, base_path)
            print(f"ISSUE: {rel_path}")
            print(f"   Self logger: {'YES' if analysis['has_self_logger'] else 'NO'}")
            print(f"   Global logger: {'YES' if analysis['has_global_logger'] else 'NO'}")
            print(f"   Issues found: {issue_count}")
            
            for line_num, line_content in analysis['incorrect_usage']:
                print(f"     Line {line_num}: {line_content}")
            print()
    
    print("=" * 80)
    print(f"RESUMEN:")
    print(f"   Archivos analizados: {len(python_files)}")
    print(f"   Archivos con problemas: {len(files_with_issues)}")
    print(f"   Total de líneas problemáticas: {total_issues}")
    
    if files_with_issues:
        print("\nArchivos que necesitan corrección:")
        for analysis in files_with_issues:
            rel_path = os.path.relpath(analysis['file_path'], base_path)
            print(f"   - {rel_path} ({len(analysis['incorrect_usage'])} issues)")

if __name__ == "__main__":
    main()