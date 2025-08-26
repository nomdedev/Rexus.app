#!/usr/bin/env python3
"""
Script para corregir la indentación sistemática en reserva_dialog.py
"""

def fix_indentation():
    archivo = "rexus/modules/inventario/dialogs/reserva_dialog.py"
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    indent_level = 0
    in_class = False
    in_method = False
    in_string = False
    
    for i, line in enumerate(lines):
        original_line = line
        stripped = line.strip()
        
        # Skip empty lines and comments that are properly positioned
        if not stripped or (stripped.startswith('#') and not in_method):
            fixed_lines.append(original_line)
            continue
        
        # Detect class definition
        if stripped.startswith('class '):
            indent_level = 0
            in_class = True
            in_method = False
            fixed_lines.append(stripped + '\n')
            continue
        
        # Detect method definition
        if stripped.startswith('def '):
            if in_class:
                indent_level = 4  # Methods in class get 4 spaces
                in_method = True
                fixed_lines.append('    ' + stripped + '\n')
                continue
            else:
                indent_level = 0
                in_method = True
                fixed_lines.append(stripped + '\n')
                continue
        
        # Handle docstrings
        if '"""' in stripped and in_method:
            fixed_lines.append(' ' * (indent_level + 4) + stripped + '\n')
            continue
        
        # Handle method content
        if in_method and in_class:
            # Regular method content gets 8 spaces (4 for class + 4 for method)
            base_indent = 8
            
            # Handle control structures
            if any(stripped.startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']):
                if stripped == 'else:':
                    # else should align with its corresponding if
                    fixed_lines.append(' ' * base_indent + stripped + '\n')
                else:
                    fixed_lines.append(' ' * base_indent + stripped + '\n')
            # Comments in methods
            elif stripped.startswith('#'):
                fixed_lines.append(' ' * base_indent + stripped + '\n')
            else:
                # Regular statements
                fixed_lines.append(' ' * base_indent + stripped + '\n')
        else:
            # Outside of methods, keep original if reasonable, otherwise fix
            if stripped.startswith(('import ', 'from ', '"""')):
                fixed_lines.append(stripped + '\n')
            else:
                fixed_lines.append(' ' * max(0, indent_level) + stripped + '\n')
    
    # Write corrected file
    with open(archivo, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Indentación corregida en {archivo}")

if __name__ == "__main__":
    fix_indentation()