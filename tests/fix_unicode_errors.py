#!/usr/bin/env python3
"""
Script para corregir errores de codificación Unicode en prints
Reemplaza caracteres Unicode problemáticos con equivalentes ASCII
"""

import os
import re
import sys
from pathlib import Path

def fix_unicode_in_file(file_path):
    """Corrige los caracteres Unicode problemáticos en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazos de caracteres problemáticos
        replacements = {
            '[ERROR]': '[ERROR]',  # U+274C
            '[OK]': '[OK]',      # U+2713
            '[WARN]': '[WARN]',   # U+26A0
            '[LOCK]': '[LOCK]',   # U+1F512
            '[CHART]': '[CHART]',  # U+1F4CA
            '[ROCKET]': '[ROCKET]', # U+1F680
            '[CHECK]': '[CHECK]',  # U+2705
        }
        
        # Aplicar reemplazos
        for unicode_char, ascii_replacement in replacements.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        # Si hubo cambios, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    base_path = Path(__file__).parent
    
    # Patrones de archivos a procesar
    patterns = ['**/*.py']
    
    files_processed = 0
    files_fixed = 0
    fixed_files = []
    
    print("Buscando archivos con caracteres Unicode problemáticos...")
    
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                files_processed += 1
                
                if fix_unicode_in_file(file_path):
                    files_fixed += 1
                    fixed_files.append(str(file_path.relative_to(base_path)))
                    print(f"Corregido: {file_path.relative_to(base_path)}")
    
    print(f"\nResumen:")
    print(f"- Archivos procesados: {files_processed}")
    print(f"- Archivos corregidos: {files_fixed}")
    
    if fixed_files:
        print(f"\nArchivos modificados:")
        for file_path in fixed_files[:10]:  # Mostrar solo los primeros 10
            print(f"  - {file_path}")
        if len(fixed_files) > 10:
            print(f"  ... y {len(fixed_files) - 10} más")

if __name__ == '__main__':
    main()
