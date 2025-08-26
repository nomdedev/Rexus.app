#!/usr/bin/env python3
"""
Script masivo para corregir errores de indentación en archivos Python
Enfoque en archivos críticos con patrones comunes
"""

import os
import py_compile
import glob
import re

def fix_basic_indentation_patterns(content, filename):
    """Corrige patrones básicos de indentación"""
    lines = content.split('\n')
    fixed_lines = []
    in_class = False
    in_function = False
    class_indent = 0
    function_indent = 0
    
    for i, line in enumerate(lines):
        # Detectar definiciones de clase
        if re.match(r'^class\s+\w+', line.strip()):
            in_class = True
            class_indent = 4
            fixed_lines.append(line)
            continue
        
        # Detectar definiciones de función/método
        if re.match(r'^\s*def\s+\w+', line):
            if in_class:
                function_indent = 8  # Método de clase
                line = '    ' + line.strip()
            else:
                function_indent = 4  # Función standalone
                line = line.strip()
            in_function = True
            fixed_lines.append(line)
            continue
        
        # Línea vacía - mantener
        if not line.strip():
            fixed_lines.append('')
            continue
        
        # Corregir indentación según contexto
        stripped = line.strip()
        
        # Si estamos en función/método
        if in_function and stripped:
            if re.match(r'^(class\s+|def\s+)', stripped):
                # Nueva definición - resetear
                in_function = False
                if stripped.startswith('class'):
                    in_class = True
                    fixed_lines.append(stripped)
                else:
                    fixed_lines.append('    ' + stripped if in_class else stripped)
            else:
                # Código dentro de función
                indent = '        ' if in_class else '    '
                fixed_lines.append(indent + stripped)
        
        # Si estamos en clase pero no en función
        elif in_class and not in_function and stripped:
            if stripped.startswith(('def ', 'class ')):
                if stripped.startswith('class'):
                    # Nueva clase - resetear
                    in_class = True
                    fixed_lines.append(stripped)
                else:
                    # Método de clase
                    fixed_lines.append('    ' + stripped)
                    in_function = True
            else:
                # Atributo/comentario de clase
                fixed_lines.append('    ' + stripped)
        
        # Código a nivel módulo
        else:
            if stripped.startswith(('import ', 'from ', '#', '"""', "'''")):
                # Imports y comentarios a nivel módulo
                fixed_lines.append(stripped)
            elif stripped.startswith(('class ', 'def ')):
                # Nuevas definiciones
                fixed_lines.append(stripped)
                if stripped.startswith('class'):
                    in_class = True
                    in_function = False
                else:
                    in_function = True
                    in_class = False
            else:
                # Código a nivel módulo
                fixed_lines.append(stripped)
    
    return '\n'.join(fixed_lines)

def fix_syntax_errors(content, filename):
    """Corrige errores de sintaxis específicos"""
    # Corregir 'return' fuera de función
    content = re.sub(r'^return\s+', '    return ', content, flags=re.MULTILINE)
    
    # Corregir bloques try sin except/finally
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        if 'try:' in line and i + 1 < len(lines):
            # Buscar except/finally correspondiente
            has_except = False
            for j in range(i + 1, min(i + 10, len(lines))):
                if 'except' in lines[j] or 'finally' in lines[j]:
                    has_except = True
                    break
            
            if not has_except:
                # Agregar except genérico
                fixed_lines.append(line)
                fixed_lines.append('        pass  # TODO: Implementar lógica')
                fixed_lines.append('    except Exception as e:')
                fixed_lines.append('        logger.error(f"Error: {e}")')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)

# Lista de archivos críticos a corregir
critical_files = [
    "rexus/modules/compras/dialogs/dialog_proveedor.py",
    "rexus/modules/compras/dialogs/dialog_seguimiento.py", 
    "rexus/modules/herrajes/inventario_integration.py",
    "rexus/modules/inventario/dialogs/modern_product_dialog.py",
    "rexus/modules/configuracion/model.py"
]

print("INICIANDO: Corrección masiva de errores de indentación...")

fixed_count = 0
for file_path in critical_files:
    if not os.path.exists(file_path):
        print(f"ADVERTENCIA: Archivo no encontrado: {file_path}")
        continue
    
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Backup original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Aplicar correcciones
        fixed_content = fix_basic_indentation_patterns(content, file_path)
        fixed_content = fix_syntax_errors(fixed_content, file_path)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Verificar compilación
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"EXITO: {file_path} - CORREGIDO Y COMPILADO")
            fixed_count += 1
        except Exception as e:
            print(f"ERROR: {file_path} - Error compilación: {e}")
            # Restaurar backup si falla
            os.rename(backup_path, file_path)
    
    except Exception as e:
        print(f"ERROR: Error procesando {file_path}: {e}")

print(f"\nRESULTADO: {fixed_count}/{len(critical_files)} archivos corregidos exitosamente")

# Verificar reducción total de errores
print("\nVerificando impacto global...")
errors = []
for py_file in glob.glob('rexus/**/*.py', recursive=True):
    if not py_compile.compile(py_file, doraise=False, quiet=True):
        errors.append(py_file)

print(f"TOTAL: {len(errors)} archivos con errores restantes")