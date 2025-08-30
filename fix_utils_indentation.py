"""
Script para corregir masivamente errores de indentación en archivos utils/
Aplica correcciones específicas para resolver 'unexpected indent' errors
"""

import os
import re

def fix_file_indentation(file_path):
    """Corrige indentación excesiva en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Si la línea tiene indentación excesiva al inicio
            if line.startswith('        ') and not line.startswith('            '):
                # Es probable que sea un import o clase mal indentada
                stripped = line.lstrip()
                if (stripped.startswith('import ') or 
                    stripped.startswith('from ') or
                    stripped.startswith('class ') or
                    stripped.startswith('def ') or
                    stripped.startswith('logger =')):
                    # Mover a nivel raíz
                    fixed_lines.append(stripped)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Lista de archivos con errores de indentación
problematic_files = [
    "rexus/utils/backup_recovery.py",
    "rexus/utils/validation_utils.py", 
    "rexus/utils/theme_fixes.py",
    "rexus/utils/system_integration.py",
    "rexus/utils/style_unifier.py"
]

print("INICIANDO CORRECION MASIVA DE INDENTACION")
print("=" * 50)

fixed_count = 0
for file_path in problematic_files:
    if os.path.exists(file_path):
        print(f"Procesando: {file_path}")
        if fix_file_indentation(file_path):
            print(f"  -> CORREGIDO")
            fixed_count += 1
        else:
            print(f"  -> Sin cambios")
    else:
        print(f"No encontrado: {file_path}")

print("=" * 50)
print(f"TOTAL ARCHIVOS CORREGIDOS: {fixed_count}")
print("FINALIZANDO CORRECCION MASIVA")