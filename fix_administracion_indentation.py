#!/usr/bin/env python3
"""
Script para arreglar indentación específica del archivo model.py de administración
"""
import re

def fix_administracion_model():
    file_path = 'rexus/modules/administracion/model.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        in_class = False
        current_indent = 0
        
        for i, line in enumerate(lines):
            # Detectar definiciones de clase
            if line.startswith('class '):
                in_class = True
                current_indent = 0
                fixed_lines.append(line)
                continue
            
            # Detectar métodos de clase
            if line.startswith('    def '):
                current_indent = 4
                fixed_lines.append(line)
                continue
            
            # Detectar funciones que deberían ser métodos (sin indentación)
            if line.startswith('def ') and in_class:
                # Convertir a método
                fixed_lines.append(f"    {line}")
                current_indent = 4
                continue
            
            # Arreglar indentación dentro de métodos/funciones
            if in_class and current_indent > 0:
                # Si la línea no está vacía y no empieza con espacios suficientes
                if line.strip() and not line.startswith(' ' * (current_indent + 4)):
                    # Si es código que debería estar dentro del método
                    if (line.strip().startswith(('try:', 'except', 'if ', 'else:', 'elif ', 
                                              'for ', 'while ', 'with ', 'return ', 'raise ',
                                              'cursor', 'self.', 'logger.', 'print(')) or
                        line.strip().endswith((':', '"""', "'''")) or
                        '=' in line or line.strip().startswith(('"""', "'''"))):
                        
                        # Determinar indentación apropiada
                        if line.strip().startswith(('except ', 'else:', 'elif ', 'finally:')):
                            # Misma indentación que try/if
                            fixed_lines.append(f"        {line.strip()}")
                        elif line.strip().startswith('"""') and line.strip().endswith('"""'):
                            # Docstring en una línea
                            fixed_lines.append(f"        \"{line.strip()[3:-3]}\"")
                        else:
                            # Contenido normal del método
                            fixed_lines.append(f"        {line.strip()}")
                        continue
            
            # Mantener la línea como está
            fixed_lines.append(line)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"✅ Indentación corregida en {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo indentación: {e}")
        return False

if __name__ == '__main__':
    fix_administracion_model()
