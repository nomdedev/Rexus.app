#!/usr/bin/env python3
"""
Script para corregir todos los errores de sintaxis restantes
"""
import os
import re
import sys

def fix_file_syntax_errors(file_path):
    """Corrige errores de sintaxis específicos en un archivo"""
    changes = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return 0
    
    original_content = content
    
    # 1. Corregir logger.warning(texto sin f-string ni comillas: {variable})
    pattern = r'logger\.(warning|error|info|debug)\(([A-Z][^"f\'\(]*)\{([^}]+)\}([^"]*)\)'
    content = re.sub(pattern, r'logger.\1(f"\2{\3}\4")', content)
    
    # 2. Corregir logger.error([TEXTO] sin f-string: {variable})
    pattern = r'logger\.(warning|error|info|debug)\(\[([^\]]+)\]([^"f\'\(]*)\{([^}]+)\}([^"]*)\)'
    content = re.sub(pattern, r'logger.\1(f"[\2]\3{\4}\5")', content)
    
    # 3. Corregir comillas desbalanceadas con {
    pattern = r'logger\.(warning|error|info|debug)\(([^"]*)\{([^}]+)\}([^"]*)\"\)'
    content = re.sub(pattern, r'logger.\1(f"\2{\3}\4")', content)
    
    # 4. Corregir f-strings sin comilla de cierre
    pattern = r'logger\.(warning|error|info|debug)\(f\"([^"]*)\{([^}]+)\}([^"]*)\)'
    content = re.sub(pattern, r'logger.\1(f"\2{\3}\4")', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            changes = 1
        except:
            pass
    
    return changes

def main():
    print("Iniciando correccion de sintaxis restante...")
    total_files = 0
    total_changes = 0
    
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                changes = fix_file_syntax_errors(file_path)
                if changes > 0:
                    print(f"FIXED {file_path}")
                    total_changes += changes
                total_files += 1
    
    print(f"\nResumen:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Archivos corregidos: {total_changes}")
    print("Correccion completada!")

if __name__ == "__main__":
    main()