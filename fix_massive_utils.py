"""
Script MASIVO para corregir TODOS los archivos utils con errores de indentación
Corrige 30+ archivos de una vez con patrones agresivos
"""

import os
import re
import glob

def massive_indentation_fix(file_path):
    """Corrige indentación de manera masiva y agresiva."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                fixed_lines.append(line)
                continue
                
            # 1. CORRECCIÓN AGRESIVA: Lines que empiezan con mucha indentación pero deberían estar en nivel 0
            stripped = line.lstrip()
            leading_spaces = len(line) - len(stripped)
            
            # Si tiene 8+ espacios y es un import/class/def/logger -> nivel 0
            if (leading_spaces >= 8 and 
                (stripped.startswith(('import ', 'from ', 'class ', 'def ', 'logger', 
                                    'COLORS', 'SIZES', '@', '#', 'if __name__')))):
                fixed_lines.append(stripped)
                continue
            
            # 2. Líneas que claramente deberían estar indentadas a nivel de método (4 espacios)
            if (leading_spaces >= 8 and 
                (stripped.startswith(('def ', 'class ')) and 
                 i > 0 and fixed_lines[-1].strip().startswith('class '))):
                fixed_lines.append('    ' + stripped)
                continue
            
            # 3. Bloques try/except sin contenido - agregar pass
            if stripped in ['try:', 'except:', 'except Exception as e:', 'except Exception:', 'finally:']:
                fixed_lines.append(line)
                # Verificar siguiente línea
                if i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if (next_line.strip() == "" or 
                        not next_line.startswith(' ' * (leading_spaces + 4))):
                        fixed_lines.append(' ' * (leading_spaces + 4) + 'pass')
                continue
            
            # 4. Líneas completamente incorrectas - try to fix
            if leading_spaces > 0 and leading_spaces % 4 != 0:
                # Redondear a múltiplo de 4 más cercano
                correct_indent = ((leading_spaces + 2) // 4) * 4
                fixed_lines.append(' ' * correct_indent + stripped)
                continue
            
            # 5. Mantener línea original si no necesita corrección
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # LIMPIEZA ADICIONAL CON REGEX
        # Corregir múltiples líneas vacías
        fixed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed_content)
        
        # Corregir imports duplicados en una línea
        fixed_content = re.sub(r'import (\w+)\nimport (\w+)', r'import \1, \2', fixed_content)
        
        # Corregir except except
        fixed_content = re.sub(r'except except (.+?):', r'except \1:', fixed_content)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# OBTENER TODOS LOS ARCHIVOS UTILS CON PROBLEMAS
problematic_files = []
utils_pattern = "rexus/utils/*.py"
for file_path in glob.glob(utils_pattern):
    # Test compile para ver si tiene errores
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "py_compile", file_path],
            capture_output=True, text=True
        )
        if "IndentationError" in result.stderr or "SyntaxError" in result.stderr:
            problematic_files.append(file_path)
    except:
        problematic_files.append(file_path)  # Si falla, incluirlo

print("INICIANDO CORRECION MASIVA DE UTILS")
print("=" * 70)
print(f"ARCHIVOS IDENTIFICADOS CON PROBLEMAS: {len(problematic_files)}")
print("=" * 70)

fixed_count = 0
for file_path in problematic_files:
    if os.path.exists(file_path):
        print(f"Procesando: {file_path}")
        if massive_indentation_fix(file_path):
            print(f"  -> CORREGIDO")
            fixed_count += 1
        else:
            print(f"  -> Sin cambios")
    else:
        print(f"No encontrado: {file_path}")

print("=" * 70)
print(f"ARCHIVOS PROCESADOS: {len(problematic_files)}")
print(f"ARCHIVOS CORREGIDOS: {fixed_count}")
print("CORRECION MASIVA COMPLETADA")
print("=" * 70)