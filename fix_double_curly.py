#!/usr/bin/env python3
"""
Script para corregir errores de dobles llaves en f-strings
"""
import os
import re

def fix_double_curly_errors(file_path):
    """Corrige errores específicos de dobles llaves en f-strings"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # Corregir {{variable")" -> {variable}
    pattern = r'\{\{([^}]*)\"\)\}'
    content = re.sub(pattern, r'{\1}', content)
    
    # Corregir {{variable") -> {variable}
    pattern = r'\{\{([^}]*)\"\)'
    content = re.sub(pattern, r'{\1}', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            pass
    
    return False

def main():
    print("Corrigiendo errores de dobles llaves...")
    
    total_changes = 0
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_double_curly_errors(file_path):
                    print(f"DOUBLE CURLY FIX: {file_path}")
                    total_changes += 1
    
    print(f"Total archivos corregidos: {total_changes}")

if __name__ == "__main__":
    main()