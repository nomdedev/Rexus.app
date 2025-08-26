#!/usr/bin/env python3
"""
Script para corregir indentación en seleccionar_obra_dialog.py
"""

def fix_indentation():
    archivo = "rexus/modules/inventario/dialogs/seleccionar_obra_dialog.py"
    
    with open(archivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    in_class = False
    in_method = False
    
    for i, line in enumerate(lines):
        original = line
        stripped = line.strip()
        
        if not stripped:
            fixed_lines.append('')
            continue
            
        # Detectar definición de clase
        if stripped.startswith('class '):
            in_class = True
            in_method = False
            fixed_lines.append(stripped)
            continue
            
        # Detectar definición de método
        if stripped.startswith('def ') and in_class:
            in_method = True
            fixed_lines.append('    ' + stripped)
            continue
            
        # Docstring de método
        if '"""' in stripped and in_method and len(fixed_lines) > 0 and 'def ' in fixed_lines[-1]:
            fixed_lines.append('        ' + stripped)
            continue
            
        # Contenido de método
        if in_method and in_class:
            if stripped.startswith('#'):
                fixed_lines.append('        ' + stripped)
            elif any(stripped.startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']):
                fixed_lines.append('        ' + stripped)
            else:
                fixed_lines.append('        ' + stripped)
        else:
            # Fuera de métodos
            if stripped.startswith(('import ', 'from ', '"""', "'''", '#')):
                fixed_lines.append(stripped)
            else:
                fixed_lines.append(original)
    
    # Escribir archivo corregido
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("OK - Indentacion corregida")

if __name__ == "__main__":
    fix_indentation()