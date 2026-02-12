#!/usr/bin/env python3
"""
Script para corregir problemas de codificación en archivos Python
"""

import os
import re

def fix_encoding_in_file(file_path):
    """Corrige problemas de codificación en un archivo específico"""
    try:
        # Leer el archivo con codificación utf-8
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Corregir caracteres problemáticos
        content = content.replace('inv�lido', 'inválido')
        content = content.replace('�', 'í')
        
        # Corregir f-strings con caracteres especiales
        content = re.sub(r'f"([^"]*?)inv�lido([^"]*?)"', r'f"\1inválido\2"', content)
        
        # Guardar el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"OK Archivo {file_path} corregido")
        return True
        
    except Exception as e:
        print(f"ERROR Corrigiendo archivo {file_path}: {e}")
        return False

def fix_usuarios_controller():
    """Corrige específicamente el controller de usuarios"""
    file_path = "rexus/modules/11_usuarios/controller.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        # Corregir la línea 357 específicamente
        for i, line in enumerate(lines):
            if i == 356:  # Línea 357 (índice 356)
                if 'inv�lido' in line:
                    lines[i] = line.replace('inv�lido', 'inválido')
                    print(f"Línea {i+1} corregida: {lines[i].strip()}")
        
        # Guardar el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"OK Archivo {file_path} corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"ERROR Corrigiendo archivo {file_path}: {e}")
        return False

if __name__ == "__main__":
    print("Corrigiendo problemas de codificación...")
    fix_usuarios_controller()