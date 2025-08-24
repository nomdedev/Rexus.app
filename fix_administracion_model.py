#!/usr/bin/env python3
"""
Script para corregir la indentación completa del archivo administracion/model.py
"""
import re

def fix_administracion_model():
    """Corrige completamente el archivo model.py de administración"""
    file_path = 'rexus/modules/administracion/model.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir en líneas
        lines = content.split('\n')
        fixed_lines = []
        
        current_indent = 0
        in_class = False
        in_method = False
        in_try = False
        in_docstring = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detectar inicio de clase
            if stripped.startswith('class '):
                current_indent = 0
                in_class = True
                fixed_lines.append(line.strip())
                continue
            
            # Detectar método de clase
            if in_class and stripped.startswith('def '):
                current_indent = 4
                in_method = True
                fixed_lines.append(' ' * current_indent + stripped)
                continue
            
            # Detectar docstring
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    fixed_lines.append(' ' * (current_indent + 4) + stripped)
                    if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                        in_docstring = False
                else:
                    in_docstring = False
                    fixed_lines.append(' ' * (current_indent + 4) + stripped)
                continue
            
            # Si estamos en docstring
            if in_docstring:
                fixed_lines.append(' ' * (current_indent + 4) + stripped)
                continue
            
            # Detectar try/except
            if stripped.startswith('try:'):
                in_try = True
                fixed_lines.append(' ' * (current_indent + 4) + stripped)
                continue
            
            if stripped.startswith('except ') or stripped.startswith('finally:'):
                in_try = False
                fixed_lines.append(' ' * (current_indent + 4) + stripped)
                continue
            
            # Ajustar indentación según contexto
            if in_method:
                if stripped == '':
                    fixed_lines.append('')
                elif stripped.startswith('#'):
                    fixed_lines.append(' ' * (current_indent + 8) + stripped)
                elif stripped.startswith('if ') or stripped.startswith('elif ') or stripped.startswith('else:'):
                    fixed_lines.append(' ' * (current_indent + 8) + stripped)
                elif stripped.startswith('for ') or stripped.startswith('while '):
                    fixed_lines.append(' ' * (current_indent + 8) + stripped)
                elif stripped.startswith('with '):
                    fixed_lines.append(' ' * (current_indent + 8) + stripped)
                elif stripped.startswith('return '):
                    if in_try:
                        fixed_lines.append(' ' * (current_indent + 12) + stripped)
                    else:
                        fixed_lines.append(' ' * (current_indent + 8) + stripped)
                else:
                    if in_try:
                        fixed_lines.append(' ' * (current_indent + 12) + stripped)
                    else:
                        fixed_lines.append(' ' * (current_indent + 8) + stripped)
            elif in_class:
                fixed_lines.append(' ' * 4 + stripped)
            else:
                fixed_lines.append(stripped)
        
        # Escribir el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"✅ Archivo {file_path} corregido exitosamente")
        
    except Exception as e:
        print(f"❌ Error corrigiendo archivo: {e}")

if __name__ == '__main__':
    fix_administracion_model()
