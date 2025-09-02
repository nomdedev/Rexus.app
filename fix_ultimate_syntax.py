#!/usr/bin/env python3
"""
Corrección final y definitiva de todos los errores de sintaxis
"""
import os
import re

def fix_ultimate_syntax_errors(file_path):
    """Corrige todos los errores de sintaxis restantes de forma agresiva"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # 1. Corregir logger con )) extra al final
    pattern = r'(logger\.[a-z]+\(f?"[^"]*"\))\)'
    content = re.sub(pattern, r'\1', content)
    
    # 2. Corregir paréntesis extra en fin de logger statements
    pattern = r'(logger\.[a-z]+\([^)]*\))\)'
    content = re.sub(pattern, r'\1', content)
    
    # 3. Corregir strings sin terminar seguido de )
    pattern = r'(logger\.[a-z]+\(f?"[^"]*)\)$'
    content = re.sub(pattern, r'\1")', content, flags=re.MULTILINE)
    
    # 4. Corregir } sin comillas al final
    pattern = r'(logger\.[a-z]+\(f"[^"]*\{[^}]*\}[^"]*)\}'
    content = re.sub(pattern, r'\1")', content)
    
    # 5. Corregir comillas desbalanceadas con " extra
    pattern = r'(logger\.[a-z]+\(f"[^"]*")"\)'
    content = re.sub(pattern, r'\1)', content)
    
    # 6. Corregir }} extra
    pattern = r'(\{[^}]*\})\}'
    content = re.sub(pattern, r'\1', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            pass
    
    return False

def main():
    print("CORRECCIÓN FINAL AGRESIVA de errores de sintaxis...")
    
    total_changes = 0
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_ultimate_syntax_errors(file_path):
                    print(f"ULTIMATE FIX: {file_path}")
                    total_changes += 1
    
    print(f"Total archivos corregidos: {total_changes}")

if __name__ == "__main__":
    main()