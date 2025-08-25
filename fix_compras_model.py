#!/usr/bin/env python3
"""
Script para corregir problemas de indentación en compras/model.py
"""

import re

def fix_compras_model():
    """Corrige el archivo compras/model.py"""
    
    file_path = "rexus/modules/compras/model.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Separar en líneas
    lines = content.split('\n')
    fixed_lines = []
    in_class = False
    in_method = False
    method_indent = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detectar inicio de clase
        if line.strip().startswith('class ComprasModel'):
            in_class = True
            fixed_lines.append(line)
            i += 1
            continue
            
        # Si estamos en la clase
        if in_class:
            # Detectar métodos
            if re.match(r'^\s*def\s+', line.strip()) or line.strip().startswith('def '):
                # Corregir indentación del método
                method_name = line.strip()
                fixed_lines.append(f"    {method_name}")
                in_method = True
                method_indent = 8  # 4 espacios para clase + 4 para método
                i += 1
                continue
                
            # Si estamos en un método
            if in_method:
                stripped = line.strip()
                
                # Si la línea está vacía o es comentario
                if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    # Mantener comentarios y líneas vacías con indentación mínima
                    if stripped:
                        fixed_lines.append(f"        {stripped}")
                    else:
                        fixed_lines.append(line)
                    i += 1
                    continue
                
                # Detectar bloques especiales
                if stripped.startswith('try:'):
                    fixed_lines.append(f"        try:")
                    i += 1
                    continue
                elif stripped.startswith('except'):
                    fixed_lines.append(f"        except Exception as e:")
                    i += 1
                    continue
                elif stripped.startswith('return'):
                    fixed_lines.append(f"            {stripped}")
                    i += 1
                    continue
                elif 'cursor.execute' in stripped or 'cursor.fetchone' in stripped:
                    fixed_lines.append(f"            {stripped}")
                    i += 1
                    continue
                elif stripped.startswith('if ') or stripped.startswith('for ') or stripped.startswith('while '):
                    fixed_lines.append(f"            {stripped}")
                    i += 1
                    continue
                    
                # Otras líneas de código
                if stripped and not line.startswith(' '):
                    # Línea sin indentación, probablemente necesita indentación de método
                    fixed_lines.append(f"            {stripped}")
                else:
                    # Mantener línea tal como está si ya tiene alguna indentación
                    fixed_lines.append(line)
                    
            else:
                # No estamos en método, agregar a clase
                if line.strip():
                    fixed_lines.append(f"    {line.strip()}")
                else:
                    fixed_lines.append(line)
        else:
            # Fuera de clase
            fixed_lines.append(line)
            
        i += 1
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Archivo {file_path} corregido")

if __name__ == "__main__":
    fix_compras_model()