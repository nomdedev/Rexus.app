#!/usr/bin/env python3
"""
Script para limpiar el archivo administracion/controller.py
"""

def fix_administracion_controller():
    filepath = 'rexus/modules/administracion/controller.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_until_def = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si encontramos la línea problemática 344, empezamos a saltar
        if line_num == 344 and 'if self.model and hasattr' in line:
            skip_until_def = True
            continue
            
        # Si estamos saltando y encontramos una nueva función, paramos de saltar
        if skip_until_def and line.strip().startswith('def '):
            skip_until_def = False
            new_lines.append(line)
            continue
            
        # Si no estamos saltando, agregamos la línea
        if not skip_until_def:
            new_lines.append(line)
    
    # Escribir el archivo limpio
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Limpiado: {filepath}")

if __name__ == "__main__":
    fix_administracion_controller()
