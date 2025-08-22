#!/usr/bin/env python3
"""
Script comprehensivo para corregir decoradores problemáticos
"""

import os
import re
import glob

def fix_decorators_in_file(file_path):
    """Corrige decoradores problemáticos en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones a remover
        patterns = [
            r'^\s*@auth_required\s*\n',
            r'^\s*@permission_required\([^)]+\)\s*\n',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Corregido: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error en {file_path}: {e}")
        return False

def find_problematic_files():
    """Encuentra archivos con decoradores problemáticos."""
    patterns = [
        "rexus/modules/*/controller.py",
        "rexus/modules/*/model.py", 
        "rexus/modules/*/view.py",
        "rexus/modules/*/submodules/*.py",
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    return files

def check_file_has_problematic_decorators(file_path):
    """Verifica si un archivo tiene decoradores problemáticos."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar patrones problemáticos
        patterns = [
            r'@auth_required',
            r'@permission_required',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
        
    except Exception:
        return False

def fix_all_problematic_decorators():
    """Corrige decoradores problemáticos en todos los archivos relevantes."""
    print("Buscando archivos con decoradores problematicos...")
    
    all_files = find_problematic_files()
    problematic_files = []
    
    for file_path in all_files:
        if os.path.exists(file_path) and check_file_has_problematic_decorators(file_path):
            problematic_files.append(file_path)
    
    print(f"Encontrados {len(problematic_files)} archivos con decoradores problematicos")
    
    fixed_count = 0
    for file_path in problematic_files:
        if fix_decorators_in_file(file_path):
            fixed_count += 1
    
    print(f"\nArchivos corregidos: {fixed_count}/{len(problematic_files)}")
    
    return fixed_count

if __name__ == "__main__":
    print("Iniciando correccion comprehensiva de decoradores...")
    fixed = fix_all_problematic_decorators()
    print(f"Correccion completada. {fixed} archivos corregidos.")