#!/usr/bin/env python3
"""
Script para corregir masivamente errores de f-string en los archivos críticos.
"""

import re
import os

def fix_fstring_in_file(file_path):
    """
    Corrige errores de f-string en un archivo específico.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para encontrar f-strings sin cerrar
        # Busca f"texto {variable} sin cerrar
        pattern1 = r'f"([^"]*\{[^}]+\}[^"]*)\)'
        replacement1 = r'f"\1"'
        
        # Patrón para f-strings con comillas simples sin cerrar
        pattern2 = r"f'([^']*\{[^}]+\}[^']*)\)"
        replacement2 = r"f'\1'"
        
        # Aplicar correcciones
        content = re.sub(pattern1, replacement1, content)
        content = re.sub(pattern2, replacement2, content)
        
        # Correcciones específicas para patrones conocidos
        specific_fixes = [
            # Errores de print con f-string sin cerrar
            (r'print\(f"([^"]*\{[^}]+\}[^"]*)\)', r'print(f"\1")'),
            (r'print\(f\'([^\'\{]*\{[^}]+\}[^\'\{]*)\)', r"print(f'\1')"),
            
            # Errores de raise con f-string sin cerrar
            (r'raise ValueError\(f"([^"]*\{[^}]+\}[^"]*)\)', r'raise ValueError(f"\1")'),
            (r'raise Exception\(f"([^"]*\{[^}]+\}[^"]*)\)', r'raise Exception(f"\1")'),
            
            # Errores de return con f-string sin cerrar
            (r'return f"([^"]*\{[^}]+\}[^"]*)\)', r'return f"\1"'),
            
            # Corregir paréntesis desbalanceados después de f-string
            (r'f"([^"]*\{[^}]+\}[^"]*)\)\)', r'f"\1")'),
        ]
        
        for pattern, replacement in specific_fixes:
            content = re.sub(pattern, replacement, content)
        
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
    print("Iniciando corrección masiva de f-strings...")
    
    # Archivos a corregir
    files_to_fix = [
        'rexus/modules/11_usuarios/model.py',
        'rexus/modules/11_usuarios/security_features.py',
        'rexus/modules/04_vidrios/model.py'
    ]
    
    corrected_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_fstring_in_file(file_path):
                corrected_count += 1
        else:
            print(f"Archivo no encontrado: {file_path}")
    
    print(f"\nResumen:")
    print(f"Archivos corregidos: {corrected_count}")
    print(f"Total archivos: {len(files_to_fix)}")

if __name__ == "__main__":
    main()