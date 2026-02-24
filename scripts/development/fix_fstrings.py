#!/usr/bin/env python3
import re
import os
from pathlib import Path

def fix_fstring_issues_comprehensive(file_path):
    """Corrige f-strings sin terminar en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        original = line
        
        # Patrón 1: f"...)  -> f"...")
        if 'f"' in line and ')' in line:
            # Buscar f" que no tenga " de cierre antes de )
            match = re.search(r'f"([^"]*?)\)', line)
            if match and 'f"' in line:
                # Contar comillas
                f_pos = line.find('f"')
                remaining = line[f_pos:]
                
                # Contar comillas desde f"
                quote_count = remaining.count('"') 
                paren_count = remaining.count(')')
                
                # Si hay ) sin pareja de comillas
                if quote_count % 2 == 0 and paren_count > 0:
                    # Reemplazar últimas )) con ")
                    if line.rstrip().endswith(')'):
                        # Buscar el patrón f"...keyword...)
                        line = re.sub(r'(f"[^"]*?\))\)', r'\1")', line)
                        
        if line != original:
            lines[i] = line
            modified = True
            print(f"  Línea {i+1}: Corregido")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return modified

def main():
    root_path = Path('d:/martin/Proyectos/Rexus.app/rexus/modules')
    
    # Buscar todos los .py files
    py_files = list(root_path.glob('**/*.py'))
    print(f"🔍 Verificando {len(py_files)} archivos Python\n")
    
    fixed_count = 0
    for file_path in py_files:
        try:
            # Compilar para detectar errores
            import py_compile
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as e:
            if 'unterminated' in str(e) or 'f-string' in str(e):
                rel_path = file_path.relative_to(root_path)
                print(f"Reparando: {rel_path}")
                if fix_fstring_issues_comprehensive(file_path):
                    fixed_count += 1

    print(f"\n✓ {fixed_count} archivos reparados")

if __name__ == '__main__':
    main()

