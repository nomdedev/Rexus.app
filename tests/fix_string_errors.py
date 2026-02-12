#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores de strings sin terminar en archivos Python
"""

import os
import re
from pathlib import Path

def fix_unterminated_strings(file_path):
    """Corrige strings sin terminar en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para encontrar strings sin terminar
        # Busca logger.error con f-string mal formado
        pattern1 = r'logger\.error\("([^"]*\{[^}]*\}[^"]*)\.\s*([^"]*)\)'
        replacement1 = r'logger.error(f"\1.\2")'
        
        content = re.sub(pattern1, replacement1, content)
        
        # Patrón para strings sin terminar al final
        pattern2 = r'logger\.(error|info|warning|debug)\("([^"]*[^"])\)\s*$'
        replacement2 = r'logger.\1(f"\2")'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern2, line):
                lines[i] = re.sub(pattern2, replacement2, line)
        
        content = '\n'.join(lines)
        
        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Corregido: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def find_and_fix_errors(root_dir):
    """Busca y corrige errores en todos los archivos Python"""
    root_path = Path(root_dir)
    fixed_count = 0
    
    # Buscar todos los archivos .py en los módulos
    for py_file in root_path.rglob("*.py"):
        # Ignorar algunos directorios
        if any(skip in str(py_file) for skip in ['.venv', '__pycache__', '.git']):
            continue
            
        if fix_unterminated_strings(py_file):
            fixed_count += 1
    
    print(f"\nTotal de archivos corregidos: {fixed_count}")

if __name__ == "__main__":
    # Corregir errores en el directorio de módulos
    find_and_fix_errors("rexus/modules")