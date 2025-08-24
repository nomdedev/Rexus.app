#!/usr/bin/env python3
"""
Script para corregir bloques try-except incompletos
"""

import os
import ast

def fix_try_blocks(filepath):
    """Corrige bloques try sin except apropiados."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar compilar primero
        try:
            ast.parse(content)
            print(f"✅ {filepath} - Ya compila correctamente")
            return False
        except SyntaxError as e:
            print(f"🔧 {filepath} - Error en línea {e.lineno}: {e.msg}")
        
        lines = content.split('\n')
        modified = False
        
        # Buscar líneas problemáticas
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Si encontramos código fuera de un bloque try-except
            if (line.strip().startswith('if self.') and 
                i > 0 and 
                ('try:' in lines[i-5:i] if i >= 5 else False) and
                not any('except' in line_text for line_text in lines[max(0, i-10):i])):
                
                # Buscar el try anterior
                try_line = -1
                for j in range(i-1, max(0, i-10), -1):
                    if lines[j].strip().endswith('try:'):
                        try_line = j
                        break
                
                if try_line != -1:
                    # Indentar la línea problemática para que esté dentro del try
                    original_indent = len(lines[try_line]) - len(lines[try_line].lstrip())
                    new_indent = ' ' * (original_indent + 4)  # Indentar 4 espacios más
                    
                    if not line.startswith(new_indent):
                        lines[i] = new_indent + line.lstrip()
                        modified = True
                        print(f"   Corregida línea {i+1}: {line.strip()}")
            
            # Si encontramos líneas sueltas después de comentarios
            elif (line.strip() and 
                  not line.strip().startswith('#') and
                  not line.strip().startswith('def ') and
                  not line.strip().startswith('class ') and
                  not line.strip().startswith('except') and
                  not line.strip().startswith('finally') and
                  i > 0 and 
                  lines[i-1].strip().startswith('#')):
                
                # Buscar si estamos en un bloque try
                in_try = False
                try_indent = 0
                
                for j in range(i-1, max(0, i-20), -1):
                    if 'try:' in lines[j]:
                        try_indent = len(lines[j]) - len(lines[j].lstrip())
                        # Verificar si hay un except correspondiente después
                        has_except = False
                        for k in range(j+1, min(len(lines), j+50)):
                            if lines[k].strip().startswith('except') and len(lines[k]) - len(lines[k].lstrip()) == try_indent:
                                has_except = True
                                break
                            elif (lines[k].strip().startswith('def ') or lines[k].strip().startswith('class ')) and len(lines[k]) - len(lines[k].lstrip()) <= try_indent:
                                break
                        
                        if not has_except:
                            in_try = True
                            break
                
                if in_try:
                    # Agregar except antes de esta línea
                    except_line = ' ' * try_indent + 'except Exception as e:'
                    pass_line = ' ' * (try_indent + 4) + 'pass'
                    
                    lines.insert(i, except_line)
                    lines.insert(i+1, pass_line)
                    lines.insert(i+2, '')
                    modified = True
                    print(f"   Agregado except antes de línea {i+1}")
                    i += 3  # Saltar las líneas que agregamos
            
            i += 1
        
        if modified:
            # Intentar compilar el resultado
            try:
                ast.parse('\n'.join(lines))
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"✅ {filepath} - Corregido y guardado")
                return True
            except SyntaxError as e:
                print(f"❌ {filepath} - Aún tiene errores después de la corrección: {e.msg}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False

def main():
    """Función principal."""
    print("Corrigiendo bloques try-except incompletos...")
    
    archivos_problematicos = [
        'rexus/modules/administracion/controller.py',
        'rexus/modules/administracion/recursos_humanos/controller.py',
        'rexus/modules/compras/controller.py',
        'rexus/modules/herrajes/controller.py',
        'rexus/modules/mantenimiento/controller.py'
    ]
    
    corregidos = 0
    
    for archivo in archivos_problematicos:
        filepath = archivo.replace('/', os.sep)
        if os.path.exists(filepath):
            if fix_try_blocks(filepath):
                corregidos += 1
        else:
            print(f"❌ Archivo no encontrado: {filepath}")
    
    print(f"\nResultado: {corregidos} archivos corregidos.")

if __name__ == "__main__":
    main()
