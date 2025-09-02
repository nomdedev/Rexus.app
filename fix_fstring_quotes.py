#!/usr/bin/env python3
"""
Script para corregir f-strings con comillas malformadas
"""
import os
import re

def fix_fstring_quote_errors(file_path):
    """Corrige errores específicos de comillas en f-strings"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # Corregir logger.error(f"texto {variable}: {e")")
    pattern = r'(logger\.[a-z]+\(f"[^"]*\{[^}]*\}[^"]*\{[^}]*\}[^"]*)\"\"\)'
    content = re.sub(pattern, r'\1")', content)
    
    # Corregir logger.error(f"texto: {e")") con comillas extra
    pattern = r'(logger\.[a-z]+\(f"[^"]*\{[^}]*\}[^"]*)\"\"\)'
    content = re.sub(pattern, r'\1")', content)
    
    # Corregir {variable") con comillas extra
    pattern = r'(\{[^}]*\)\")\)'
    content = re.sub(pattern, r'{\1', content)
    
    # Específico para {e")")
    pattern = r'\{([^}]*)\"\"\}'
    content = re.sub(pattern, r'{\1}', content)
    
    # Más específico para {e")}
    pattern = r'\{([^}]*)\"\)\}'
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
    print("Corrigiendo errores de comillas en f-strings...")
    
    total_changes = 0
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_fstring_quote_errors(file_path):
                    print(f"QUOTE FIX: {file_path}")
                    total_changes += 1
    
    print(f"Total archivos corregidos: {total_changes}")

if __name__ == "__main__":
    main()