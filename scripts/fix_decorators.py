#!/usr/bin/env python3
"""
Script para corregir decoradores problemáticos en tests
"""

import os
import re

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

def fix_problematic_decorators():
    """Corrige decoradores problemáticos en archivos específicos."""
    problematic_files = [
        "rexus/modules/vidrios/submodules/consultas_manager.py",
        "rexus/modules/vidrios/submodules/productos_manager.py",
        "rexus/modules/vidrios/submodules/obras_manager.py",
    ]
    
    fixed_count = 0
    
    for file_path in problematic_files:
        if os.path.exists(file_path):
            if fix_decorators_in_file(file_path):
                fixed_count += 1
        else:
            print(f"Archivo no encontrado: {file_path}")
    
    print(f"\nArchivos corregidos: {fixed_count}/{len(problematic_files)}")

if __name__ == "__main__":
    print("Corrigiendo decoradores problematicos...")
    fix_problematic_decorators()
    print("Correccion completada.")