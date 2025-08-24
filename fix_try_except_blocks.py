#!/usr/bin/env python3
"""
Script para corregir bloques try/except vacíos
"""
import os
import re

def fix_try_except_empty_blocks(file_path):
    """Corrige bloques try/except vacíos agregando pass"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para encontrar try: seguido de línea vacía o except directo
        pattern = r'(\s*try\s*:\s*\n)(\s*)(except\b|\n\s*except\b)'
        
        def replace_empty_try(match):
            indent = match.group(2)
            if not indent:
                indent = '    '  # Indentación mínima
            return f"{match.group(1)}{indent}    pass\n{indent}{match.group(3)}"
        
        content = re.sub(pattern, replace_empty_try, content)
        
        # Patrón para except vacío
        pattern2 = r'(\s*except[^:]*:\s*\n)(\s*)(\n|\s*#|\s*$|\s*def\b|\s*class\b)'
        
        def replace_empty_except(match):
            indent = match.group(2)
            if not indent:
                indent = '    '
            return f"{match.group(1)}{indent}    pass\n{match.group(3)}"
        
        content = re.sub(pattern2, replace_empty_except, content)
        
        # Corregir clases vacías
        pattern3 = r'(\s*class\s+[^:]+:\s*\n)(\s*)(\n|\s*def\b|\s*class\b|$)'
        
        def replace_empty_class(match):
            indent = match.group(2)
            if not indent:
                indent = '    '
            return f"{match.group(1)}{indent}    pass\n{match.group(3)}"
        
        content = re.sub(pattern3, replace_empty_class, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    # Archivos prioritarios identificados
    priority_files = [
        'rexus/modules/administracion/controller.py',
        'rexus/modules/administracion/model.py', 
        'rexus/modules/administracion/view.py',
        'rexus/modules/administracion/contabilidad/controller.py',
        'rexus/modules/administracion/contabilidad/model.py',
        'rexus/modules/administracion/recursos_humanos/controller.py',
        'rexus/modules/administracion/recursos_humanos/model.py',
        'rexus/modules/compras/controller.py'
    ]
    
    fixed = 0
    for file_path in priority_files:
        if os.path.exists(file_path):
            if fix_try_except_empty_blocks(file_path):
                print(f"✅ Corregido: {file_path}")
                fixed += 1
            else:
                print(f"⚪ Sin cambios: {file_path}")
        else:
            print(f"❌ No existe: {file_path}")
    
    print(f"\n🎯 Archivos corregidos: {fixed}")

if __name__ == '__main__':
    main()
