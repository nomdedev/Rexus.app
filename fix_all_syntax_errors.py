#!/usr/bin/env python3
"""
Script para corregir agresivamente todos los errores de sintaxis.
"""

import re
import os

def fix_file_syntax(file_path):
    """
    Corrige errores de sintaxis en un archivo.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir definiciones de funciones con comillas incorrectas
        content = re.sub(r'def (\w+)\([^)]*"([^)]*)\) ->', r'def \1(\2) ->', content)
        
        # Corregir f-strings sin cerrar
        content = re.sub(r'f"([^"]*\{[^}]+\}[^"]*)\)', r'f"\1"', content)
        content = re.sub(r"f'([^']*\{[^}]+\}[^']*)\)", r"f'\1'", content)
        
        # Corregir strings sin cerrar en prints
        content = re.sub(r'print\(\s*"([^"]*?)\s*\)', r'print("\1")', content)
        content = re.sub(r'print\(\s*\'([^\']*?)\s*\)', r"print('\1')", content)
        
        # Corregir strings sin cerrar en general
        content = re.sub(r'^(\s*)"([^"]*?)\s*$', r'\1"\2"', content, flags=re.MULTILINE)
        content = re.sub(r"^(\s*)'([^']*?)\s*$", r"\1'\2'", content, flags=re.MULTILINE)
        
        # Corregir paréntesis sueltos al final de líneas
        content = re.sub(r'\)\s*$', ')', content, flags=re.MULTILINE)
        
        # Corregir líneas que solo contienen paréntesis
        content = re.sub(r'^\s*\)\s*$', '', content, flags=re.MULTILINE)
        
        # Corregir líneas que solo contienen comillas
        content = re.sub(r'^\s*"\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r"^\s*'\s*$", '', content, flags=re.MULTILINE)
        
        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Corregido: {file_path}")
            return True
        else:
            print(f"Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """
    Función principal.
    """
    print("Iniciando corrección agresiva de sintaxis...")
    
    # Archivos a corregir
    files_to_fix = [
        'rexus/modules/11_usuarios/model.py',
        'rexus/modules/11_usuarios/security_features.py',
        'rexus/modules/04_vidrios/model.py'
    ]
    
    corrected_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file_syntax(file_path):
                corrected_count += 1
        else:
            print(f"Archivo no encontrado: {file_path}")
    
    print(f"\nResumen:")
    print(f"Archivos corregidos: {corrected_count}")
    print(f"Total archivos: {len(files_to_fix)}")

if __name__ == "__main__":
    main()