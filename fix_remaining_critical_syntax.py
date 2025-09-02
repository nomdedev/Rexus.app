#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis críticos restantes
"""

import re
import os
import glob

def fix_file_errors(file_path, error_line, error_msg):
    """Corrige errores específicos de sintaxis en archivos"""
    print(f"Fixing {file_path}:{error_line} - {error_msg}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ajustar índice de línea (1-indexed to 0-indexed)
        line_idx = error_line - 1
        
        if line_idx >= len(lines):
            return False
            
        original_line = lines[line_idx]
        fixed_line = original_line
        
        # Patrones de corrección
        if "unterminated string literal" in error_msg:
            # Buscar f-strings incompletos
            if 'f"' in fixed_line and not fixed_line.count('"') % 2 == 0:
                # Agregar comilla faltante al final
                fixed_line = fixed_line.rstrip() + '"\n'
                
        elif "'(' was never closed" in error_msg:
            # Agregar paréntesis faltante
            fixed_line = fixed_line.rstrip() + ')\n'
            
        elif "f-string: single '}' is not allowed" in error_msg:
            # Duplicar llaves en CSS
            fixed_line = re.sub(r'(?<!\{)\{(?!\{)', '{{', fixed_line)
            fixed_line = re.sub(r'(?<!\})\}(?!\})', '}}', fixed_line)
            
        elif "f-string: unterminated string" in error_msg:
            # Corregir f-strings mal formados
            fixed_line = re.sub(r'f"([^"]*)"([^"])', r'f"\1"', fixed_line)
        
        # Aplicar corrección si cambió
        if fixed_line != original_line:
            lines[line_idx] = fixed_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"  [OK] Fixed: {original_line.strip()} -> {fixed_line.strip()}")
            return True
        else:
            print(f"  [WARN] No automatic fix available")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Error fixing {file_path}: {e}")
        return False

def main():
    """Función principal"""
    import ast
    
    print("Buscando y corrigiendo errores de sintaxis críticos...")
    
    errors_fixed = 0
    total_errors = 0
    
    for py_file in glob.glob('rexus/modules/**/*.py', recursive=True):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            total_errors += 1
            if fix_file_errors(py_file, e.lineno, e.msg):
                errors_fixed += 1
    
    print(f"\nResultado:")
    print(f"Total errores encontrados: {total_errors}")
    print(f"Errores corregidos: {errors_fixed}")
    print(f"Errores pendientes: {total_errors - errors_fixed}")

if __name__ == "__main__":
    main()