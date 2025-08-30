"""
Script AGRESIVO para corregir errores de indentación en 30+ archivos
Aplica correcciones automáticas para los patrones más comunes
"""

import os
import re

def aggressive_indentation_fix(file_path):
    """Corrige indentación de manera agresiva."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Detectar y corregir patrones problemáticos
            
            # 1. Líneas con indentación excesiva (>= 12 espacios) que deberían estar en nivel 0
            if len(line) - len(line.lstrip()) >= 12:
                stripped = line.lstrip()
                if (stripped.startswith(('import ', 'from ', 'class ', 'def ', 'logger', 'COLORS', 'SIZES')) or 
                    stripped.startswith(('if __name__', '@', '#'))):
                    fixed_lines.append(stripped)
                    continue
            
            # 2. Líneas que empiezan con espacios pero deberían estar en nivel 0
            if line.startswith('    ') and not line.startswith('        '):
                stripped = line.lstrip()
                if (stripped.startswith(('import ', 'from ', 'class ', 'def ')) and 
                    i > 0 and not fixed_lines[-1].strip().endswith(':')):
                    fixed_lines.append(stripped)
                    continue
            
            # 3. Bloques except/try vacíos - agregar pass
            if line.strip() in ['except Exception as e:', 'except:', 'try:']:
                fixed_lines.append(line)
                # Verificar si la siguiente línea está vacía o mal indentada
                if i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if next_line.strip() == "" or not next_line.startswith('    '):
                        # Determinar indentación apropiada
                        indent = len(line) - len(line.lstrip()) + 4
                        fixed_lines.append(' ' * indent + 'pass')
                continue
            
            # 4. Funciones/métodos mal indentados
            if 'def ' in line and not line.lstrip().startswith('#'):
                # Si está mal indentado, corregir
                if line.startswith('def ') or (line.startswith('    ') and 'def ' in line):
                    # Determinar indentación correcta por contexto
                    indent = 0
                    if i > 0:
                        # Si está dentro de una clase, debería tener 4 espacios
                        for prev_i in range(i-1, -1, -1):
                            prev_line = lines[prev_i].strip()
                            if prev_line.startswith('class '):
                                indent = 4
                                break
                    
                    fixed_lines.append(' ' * indent + line.lstrip())
                    continue
            
            # 5. Mantener línea original si no necesita corrección
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Limpiezas adicionales con regex
        # Corregir dobles except
        fixed_content = re.sub(r'except except (.+?):', r'except \1:', fixed_content)
        
        # Corregir imports duplicados
        fixed_content = re.sub(r'(\nimport .+)\nimport (.+)', r'\1, \2', fixed_content)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Solo archivos que sabemos que tienen errores críticos
critical_files = [
    "rexus/utils/contextual_error_manager.py",
    "rexus/utils/contextual_error_system.py", 
    "rexus/utils/database_manager.py",
    "rexus/utils/data_sanitizers.py",
    "rexus/utils/demo_mode.py",
    "rexus/utils/dialogs.py",
    "rexus/utils/dialog_utils.py",
    "rexus/utils/encrypted_cache.py",
    "rexus/utils/error_manager.py",
    "rexus/utils/error_notification_widget.py",
    "rexus/utils/error_recovery.py",
    "rexus/utils/format_utils.py",
    "rexus/utils/password_security.py",
    "rexus/utils/security_clean.py",
    "rexus/utils/smart_tooltips.py"
]

print("INICIANDO CORRECION AGRESIVA")
print("=" * 50)

fixed_count = 0
for file_path in critical_files:
    if os.path.exists(file_path):
        print(f"Procesando: {file_path}")
        if aggressive_indentation_fix(file_path):
            print(f"  -> CORREGIDO")
            fixed_count += 1
        else:
            print(f"  -> Sin cambios")

print("=" * 50)
print(f"ARCHIVOS CORREGIDOS: {fixed_count}")
print("FINALIZANDO CORRECION AGRESIVA")