#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores de formato en el controller de logística
"""

import re

def fix_format_errors():
    """Corrige todos los errores de formato detectados por flake8."""
    
    # Leer el archivo
    with open('rexus/modules/logistica/controller.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Eliminar doble import de logging (F811)
    content = re.sub(r'except ImportError:\n    import logging\n    logger = logging\.getLogger\(__name__\)', 
                     'except ImportError:\n    logger = logging.getLogger(__name__)', content)
    
    # 2. Limpiar líneas en blanco con espacios (W293)
    lines = content.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() == '':
            clean_lines.append('')  # Línea completamente vacía
        else:
            clean_lines.append(line.rstrip())  # Quitar espacios al final
    
    content = '\n'.join(clean_lines)
    
    # 3. Agregar newline al final del archivo (W292)
    if not content.endswith('\n'):
        content += '\n'
    
    # 4. Corregir espaciado entre funciones y clases (E301, E302)
    # Agregar espacio antes de métodos dentro de clases
    content = re.sub(r'\n    def ', '\n\n    def ', content)
    # Pero evitar múltiples espacios seguidos
    content = re.sub(r'\n\n\n    def ', '\n\n    def ', content)
    
    # Agregar 2 espacios antes de clases
    content = re.sub(r'\nclass ', '\n\n\nclass ', content)
    content = re.sub(r'\n\n\n\nclass ', '\n\n\nclass ', content)
    
    # 5. Corregir líneas muy largas (E501) - casos más comunes
    # Dividir líneas de logging largas
    content = re.sub(r'logger\.warning\(f"([^"]{60,})"\)', 
                     lambda m: f'logger.warning(\n        f"{m.group(1)}")', content)
    
    content = re.sub(r'logger\.error\(f"([^"]{60,})"\)', 
                     lambda m: f'logger.error(\n        f"{m.group(1)}")', content)
    
    # Dividir show_error con mensajes largos
    content = re.sub(r'show_error\(([^,]+), "([^"]+)", "([^"]{40,})"\)', 
                     lambda m: f'show_error({m.group(1)}, "{m.group(2)}",\n                   "{m.group(3)}")', content)
    
    # Dividir show_success con mensajes largos  
    content = re.sub(r'show_success\(([^,]+), "([^"]+)", "([^"]{40,})"\)', 
                     lambda m: f'show_success({m.group(1)}, "{m.group(2)}",\n                     "{m.group(3)}")', content)
    
    # 6. Corregir indentación en continuaciones de línea (E128)
    # Buscar patrones de continuación mal indentados y corregirlos
    content = re.sub(r'(\n +[a-zA-Z_][a-zA-Z0-9_]*\([^)]*)\n +([^)]*\))', 
                     r'\1\n        \2', content)
    
    # Escribir el archivo corregido si hay cambios
    if content != original_content:
        with open('rexus/modules/logistica/controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Errores de formato corregidos en controller de logística")
        return True
    else:
        print("No se encontraron cambios que hacer")
        return False

if __name__ == "__main__":
    fix_format_errors()