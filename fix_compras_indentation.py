#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir todos los problemas de indentación en compras/controller.py
"""

def fix_compras_indentation():
    """Corrige sistemáticamente todos los problemas de indentación."""
    
    with open('rexus/modules/compras/controller.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrected_lines = []
    inside_class = False
    inside_method = False
    inside_docstring = False
    docstring_type = None
    
    for i, line in enumerate(lines):
        original_line = line
        stripped = line.strip()
        
        # Detectar inicio de clase
        if stripped.startswith('class '):
            inside_class = True
            inside_method = False
            corrected_lines.append(line)
            continue
        
        # Si estamos dentro de una clase
        if inside_class:
            # Detectar docstring de clase
            if (stripped.startswith('"""') or stripped.startswith("'''")) and not inside_docstring:
                inside_docstring = True
                docstring_type = '"""' if stripped.startswith('"""') else "'''"
                corrected_lines.append('    ' + stripped + '\n')
                if stripped.count(docstring_type) >= 2:  # Docstring de una línea
                    inside_docstring = False
                continue
            
            # Dentro de docstring
            if inside_docstring:
                if docstring_type in stripped:
                    inside_docstring = False
                    corrected_lines.append('    ' + stripped + '\n')
                else:
                    corrected_lines.append('    ' + stripped + '\n')
                continue
            
            # Detectar inicio de método
            if stripped.startswith('def '):
                inside_method = True
                corrected_lines.append('    ' + stripped + '\n')
                continue
            
            # Si estamos dentro de un método
            if inside_method:
                # Detectar docstring de método
                if (stripped.startswith('"""') or stripped.startswith("'''")) and not inside_docstring:
                    inside_docstring = True
                    docstring_type = '"""' if stripped.startswith('"""') else "'''"
                    corrected_lines.append('        ' + stripped + '\n')
                    if stripped.count(docstring_type) >= 2:  # Docstring de una línea
                        inside_docstring = False
                    continue
                
                # Dentro de docstring de método
                if inside_docstring:
                    if docstring_type in stripped:
                        inside_docstring = False
                        corrected_lines.append('        ' + stripped + '\n')
                    else:
                        corrected_lines.append('        ' + stripped + '\n')
                    continue
                
                # Línea vacía dentro de método
                if not stripped:
                    corrected_lines.append('\n')
                    continue
                
                # Detectar bloques de control (if, try, for, while, etc.)
                if any(stripped.startswith(keyword) for keyword in ['if ', 'elif ', 'else:', 'try:', 'except', 'finally:', 'for ', 'while ', 'with ']):
                    corrected_lines.append('        ' + stripped + '\n')
                    continue
                
                # Líneas que deberían estar más indentadas (dentro de if, try, etc.)
                if (i > 0 and any(lines[i-1].strip().endswith(':') for keyword in ['if ', 'elif ', 'else:', 'try:', 'except', 'finally:', 'for ', 'while ', 'with '])):
                    corrected_lines.append('            ' + stripped + '\n')
                    continue
                
                # Líneas normales de código dentro de método
                corrected_lines.append('        ' + stripped + '\n')
                continue
            
            # Elementos de clase (fuera de métodos)
            if not stripped:
                corrected_lines.append('\n')
            else:
                # Detectar si es el inicio de un nuevo método
                if stripped.startswith('def '):
                    inside_method = True
                    corrected_lines.append('    ' + stripped + '\n')
                else:
                    corrected_lines.append('    ' + stripped + '\n')
        else:
            # Fuera de clase - mantener como está
            corrected_lines.append(line)
    
    # Escribir archivo corregido
    with open('rexus/modules/compras/controller.py', 'w', encoding='utf-8') as f:
        f.writelines(corrected_lines)
    
    print("Indentación de compras/controller.py corregida")

if __name__ == "__main__":
    fix_compras_indentation()