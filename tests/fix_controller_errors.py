#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores específicos en archivos controller
"""

import os
import re
from pathlib import Path

def fix_controller_syntax(file_path):
    """Corrige errores de sintaxis específicos en archivos controller"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir error específico: f"Rol inválido. Debe ser uno de: {', '.join(self.model.ROLES.keys()})"
        pattern1 = r'f"Rol inválido\. Debe ser uno de: \{\'\\, \'\.join\(self\.model\.ROLES\.keys\(\)\}"'
        replacement1 = r"f\"Rol inválido. Debe ser uno de: {', '.join(self.model.ROLES.keys())}\""
        
        content = re.sub(pattern1, replacement1, content)
        
        # Corregir error similar para ESTADOS
        pattern2 = r'f"Estado inválido\. Debe ser uno de: \{\'\\, \'\.join\(self\.model\.ESTADOS\.keys\(\)\}"'
        replacement2 = r"f\"Estado inválido. Debe ser uno de: {', '.join(self.model.ESTADOS.keys())}\""
        
        content = re.sub(pattern2, replacement2, content)
        
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

def find_and_fix_controller_errors(root_dir):
    """Busca y corrige errores en archivos controller"""
    root_path = Path(root_dir)
    fixed_count = 0
    
    # Buscar todos los archivos controller.py
    for controller_file in root_path.rglob("controller.py"):
        # Ignorar algunos directorios
        if any(skip in str(controller_file) for skip in ['.venv', '__pycache__', '.git', 'modules.backup']):
            continue
            
        if fix_controller_syntax(controller_file):
            fixed_count += 1
    
    print(f"\nTotal de archivos controller corregidos: {fixed_count}")

if __name__ == "__main__":
    # Corregir errores en el directorio de módulos
    find_and_fix_controller_errors("rexus/modules")