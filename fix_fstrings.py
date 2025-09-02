#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los f-strings malformados
"""
import os
import re
import sys

def fix_fstring_patterns(file_path):
    """Corrige patrones comunes de f-strings malformados"""
    changes_made = 0
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_content = content
    
    # Patrón 1: logger.error([{variable}] texto: {error})
    pattern1 = r'logger\.(error|warning|info|debug)\(\[{([^}]+)}\]\s*([^{]*){([^}]+)}\)'
    def replace1(match):
        log_level = match.group(1)
        var1 = match.group(2)
        text = match.group(3).strip()
        var2 = match.group(4)
        return f'logger.{log_level}(f"[{{{var1}}}] {text}{{{var2}}}")'
    
    content = re.sub(pattern1, replace1, content)
    
    # Patrón 2: logger.error(texto sin comillas: {error})
    pattern2 = r'logger\.(error|warning|info|debug)\(([^"f][^{]*){([^}]+)}\)'
    def replace2(match):
        log_level = match.group(1)
        text = match.group(2).strip()
        var = match.group(3)
        return f'logger.{log_level}(f"{text}{{{var}}}")'
    
    content = re.sub(pattern2, replace2, content)
    
    # Patrón 3: logger.error(Error texto: {error}) sin f-string
    pattern3 = r'logger\.(error|warning|info|debug)\(([A-Z][^f"{]*){([^}]+)}\)'
    def replace3(match):
        log_level = match.group(1)
        text = match.group(2).strip()
        var = match.group(3)
        return f'logger.{log_level}(f"{text}{{{var}}}")'
    
    content = re.sub(pattern3, replace3, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        changes_made = content.count('logger.') - original_content.count('logger.')
        return changes_made
    
    return 0

def main():
    print("Iniciando correccion automatica de f-strings...")
    total_files = 0
    total_changes = 0
    
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                changes = fix_fstring_patterns(file_path)
                if changes > 0:
                    print(f"OK {file_path}: {changes} correcciones")
                    total_changes += changes
                total_files += 1
    
    print(f"\nResumen:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Correcciones realizadas: {total_changes}")
    print("Correccion de f-strings completada!")

if __name__ == "__main__":
    main()