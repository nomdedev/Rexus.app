#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores específicos de sintaxis en archivos Python
"""

import os
import re
from pathlib import Path

def fix_specific_errors(file_path):
    """Corrige errores específicos en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir error específico: logger.error("...{e}... .)
        pattern1 = r'logger\.error\("([^"]*\{e\}[^"]*)\.\s*\)'
        replacement1 = r'logger.error(f"\1.")'
        
        content = re.sub(pattern1, replacement1, content)
        
        # Corregir error: logger.error("...{e}... .) sin f-string
        pattern2 = r'logger\.error\("([^"]*\{e\}[^"]*)\.\s*\)'
        replacement2 = r'logger.error(f"\1.")'
        
        content = re.sub(pattern2, replacement2, content)
        
        # Corregir strings sin terminar con )
        pattern3 = r'logger\.(error|info|warning|debug)\("([^"]*[^"])\)\s*$'
        replacement3 = r'logger.\1(f"\2")'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern3, line):
                lines[i] = re.sub(pattern3, replacement3, line)
        
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
            
        if fix_specific_errors(py_file):
            fixed_count += 1
    
    print(f"\nTotal de archivos corregidos: {fixed_count}")

if __name__ == "__main__":
    # Corregir errores en el directorio de módulos
    find_and_fix_errors("rexus")