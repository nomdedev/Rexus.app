#!/usr/bin/env python3
"""
Script final para corregir todos los errores de sintaxis restantes.
"""

import re
import os

def fix_final_syntax(file_path):
    """
    Corrige errores de sintaxis finales en un archivo.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir definiciones de funciones con comillas incorrectas
        content = re.sub(r'def (\w+)\([^)]*?"([^)]*)\) ->', r'def \1(\2) ->', content)
        content = re.sub(r'def (\w+)\([^)]*?\'([^\)]*)\) ->', r'def \1(\2) ->', content)
        
        # Corregir f-strings sin cerrar (más agresivo)
        content = re.sub(r'f"([^"]*\{[^}]+\}[^"]*)\)', r'f"\1"', content)
        content = re.sub(r"f'([^']*\{[^}]+\}[^']*)\)", r"f'\1'", content)
        
        # Corregir strings sin cerrar en cualquier contexto
        content = re.sub(r'"([^"]*?)\)\s*$', r'"\1"', content, flags=re.MULTILINE)
        content = re.sub(r"'([^']*?)\)\s*$", r"'\1'", content, flags=re.MULTILINE)
        
        # Corregir paréntesis sueltos al final de líneas
        content = re.sub(r'^\s*\)\s*$', '', content, flags=re.MULTILINE)
        
        # Corregir líneas que solo tienen comillas
        content = re.sub(r'^\s*"\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r"^\s*'\s*$", '', content, flags=re.MULTILINE)
        
        # Corregir strings sin cerrar después de return
        content = re.sub(r'return\s+"([^"]*?)\)', r'return "\1"', content)
        content = re.sub(r"return\s+'([^']*?)\)", r"return '\1'", content)
        
        # Corregir strings sin cerrar después de print
        content = re.sub(r'print\(\s*"([^"]*?)\)', r'print("\1")', content)
        content = re.sub(r"print\(\s*'([^']*?)\)", r"print('\1')", content)
        
        # Corregir strings sin cerrar después de raise
        content = re.sub(r'raise\s+\w+\([^)]*?"([^"]*?)\)', r'raise \1("\2")', content)
        
        # Corregir líneas con sintaxis rota
        content = re.sub(r'^(\s*)[^"\n]*"([^"\n]*?)\s*$', r'\1"\2"', content, flags=re.MULTILINE)
        
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
    print("Iniciando corrección final de sintaxis...")
    
    # Archivos a corregir
    files_to_fix = [
        'rexus/modules/11_usuarios/model.py',
        'rexus/modules/11_usuarios/security_features.py',
        'rexus/modules/04_vidrios/model.py'
    ]
    
    corrected_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_final_syntax(file_path):
                corrected_count += 1
        else:
            print(f"Archivo no encontrado: {file_path}")
    
    print(f"\nResumen:")
    print(f"Archivos corregidos: {corrected_count}")
    print(f"Total archivos: {len(files_to_fix)}")

if __name__ == "__main__":
    main()