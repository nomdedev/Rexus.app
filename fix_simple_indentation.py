#!/usr/bin/env python3
"""
Script para arreglar errores de indentación específicos
Enfoque en archivos con IndentationError simples
"""
import os
import ast

def fix_simple_indentation_errors(file_path):
    """Arregla errores simples de indentación"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Primero verificar si ya compila
        try:
            ast.parse(content)
            print(f"✅ {file_path} ya compila correctamente")
            return True
        except:
            pass
        
        lines = content.split('\n')
        fixed_lines = []
        in_class = False
        class_indent = 0
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Detectar clases
            if line.strip().startswith('class '):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue
            
            # Si estamos en una clase
            if in_class and line.strip():
                current_indent = len(line) - len(line.lstrip())
                
                # Funciones de clase deberían tener 4 espacios más que la clase
                if line.strip().startswith('def '):
                    expected_indent = class_indent + 4
                    if current_indent != expected_indent:
                        fixed_lines.append(' ' * expected_indent + line.strip())
                        continue
                
                # Contenido de función debería tener 8 espacios más que la clase
                elif (line.strip() and not line.strip().startswith(('#', '"""', "'''")) and
                      current_indent != class_indent + 8 and
                      not line.strip().startswith(('class ', 'def ', 'except ', 'finally:', 'else:', 'elif '))):
                    
                    # Si parece contenido de función
                    if (line.strip().startswith(('self.', 'return ', 'if ', 'for ', 'while ', 'try:', 'with ',
                                              'print(', 'logger.', 'raise ', 'pass', 'break', 'continue')) or
                        '=' in line.strip() or line.strip().endswith(':')):
                        
                        expected_indent = class_indent + 8
                        fixed_lines.append(' ' * expected_indent + line.strip())
                        continue
                
                # except, else, elif deberían alinearse con try/if correspondiente
                elif line.strip().startswith(('except ', 'else:', 'elif ', 'finally:')):
                    # Buscar el try/if correspondiente hacia atrás
                    expected_indent = class_indent + 8  # Asumiendo que están en función
                    fixed_lines.append(' ' * expected_indent + line.strip())
                    continue
            
            # Mantener línea como está si no aplicamos cambios
            fixed_lines.append(original_line)
        
        # Intentar parsear el resultado
        fixed_content = '\n'.join(fixed_lines)
        try:
            ast.parse(fixed_content)
            # Si compila, escribir el archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ {file_path} corregido y compilado")
            return True
        except Exception as e:
            print(f"⚠️ {file_path} no se pudo arreglar automáticamente: {type(e).__name__}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    # Archivos con errores simples de indentación
    target_files = [
        'rexus/modules/herrajes/model.py',
        'rexus/modules/compras/model.py',
        'rexus/modules/compras/controller.py',
        'rexus/modules/compras/view.py',
        'rexus/modules/herrajes/controller.py',
        'rexus/modules/herrajes/view.py',
        'rexus/modules/obras/controller.py',
        'rexus/modules/obras/view.py'
    ]
    
    fixed = 0
    failed = 0
    
    for file_path in target_files:
        if os.path.exists(file_path):
            if fix_simple_indentation_errors(file_path):
                fixed += 1
            else:
                failed += 1
        else:
            print(f"⚪ No existe: {file_path}")
    
    print(f"\n📊 Resultado: {fixed} archivos corregidos, {failed} fallaron")

if __name__ == '__main__':
    main()
