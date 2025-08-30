"""
Script mejorado para corregir MASIVAMENTE todos los errores de indentación en utils/
Corrige 30+ archivos con IndentationError de una vez
"""

import os
import re

def fix_file_indentation_comprehensive(file_path):
    """Corrige todos los tipos de errores de indentación en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Detectar líneas con indentación incorrecta
            if line.strip() == "":
                # Líneas vacías - mantener
                fixed_lines.append(line)
                continue
                
            # Casos específicos de indentación excesiva
            stripped = line.lstrip()
            leading_spaces = len(line) - len(stripped)
            
            # Si tiene indentación excesiva y es un import/class/def/logger
            if (leading_spaces >= 8 and 
                (stripped.startswith('import ') or 
                 stripped.startswith('from ') or
                 stripped.startswith('class ') or
                 stripped.startswith('def ') or
                 stripped.startswith('logger ') or
                 stripped.startswith('COLORS ') or
                 stripped.startswith('SIZES '))):
                # Mover a nivel raíz (0 indentación)
                fixed_lines.append(stripped)
            
            # Si es un except statement que necesita contenido
            elif stripped.startswith('except ') and i + 1 < len(lines):
                # Mantener la línea except
                fixed_lines.append(line)
                # Verificar si la siguiente línea está vacía o mal indentada
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if next_line.strip() == "":
                    # Agregar un pass o return False apropiado
                    indent = " " * (leading_spaces + 4)
                    fixed_lines.append(f"{indent}pass")
            
            else:
                # Mantener línea como está
                fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Limpiar excepciones vacías adicionales
        fixed_content = re.sub(r'except[^:]*:\s*\n(\s*\n)*(?=\s*def|\s*class|\Z)', 
                             r'except \g<0>:\n        pass\n', fixed_content)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Lista completa de archivos con errores de indentación (extraída del output anterior)
problematic_files = [
    "rexus/utils/backup_compressor.py",
    "rexus/utils/backup_recovery.py", 
    "rexus/utils/contextual_error_manager.py",
    "rexus/utils/contextual_error_system.py",
    "rexus/utils/database_manager.py",
    "rexus/utils/data_integrity_validator.py",
    "rexus/utils/data_sanitizers.py",
    "rexus/utils/demo_data_generator.py",
    "rexus/utils/demo_mode.py",
    "rexus/utils/diagnostic_widget.py",
    "rexus/utils/dialogs.py",
    "rexus/utils/dialog_utils.py",
    "rexus/utils/encrypted_cache.py",
    "rexus/utils/error_handler.py",
    "rexus/utils/error_manager.py",
    "rexus/utils/error_notification_widget.py",
    "rexus/utils/error_recovery.py",
    "rexus/utils/format_utils.py",
    "rexus/utils/form_validators.py",
    "rexus/utils/input_validator.py",
    "rexus/utils/intelligent_cache.py",
    "rexus/utils/modern_form_components.py",
    "rexus/utils/module_loader_fixes.py",
    "rexus/utils/password_security.py",
    "rexus/utils/performance_optimizer.py",
    "rexus/utils/query_optimizer.py",
    "rexus/utils/realtime_dashboard.py",
    "rexus/utils/secure_logger.py",
    "rexus/utils/security_clean.py",
    "rexus/utils/smart_tooltips.py",
    "rexus/utils/style_unifier.py",
    "rexus/utils/system_integration.py",
    "rexus/utils/validation_utils.py"
]

print("INICIANDO CORRECION MASIVA COMPLETA")
print("=" * 60)
print(f"TOTAL ARCHIVOS A PROCESAR: {len(problematic_files)}")
print("=" * 60)

fixed_count = 0
error_count = 0

for file_path in problematic_files:
    if os.path.exists(file_path):
        print(f"Procesando: {file_path}")
        if fix_file_indentation_comprehensive(file_path):
            print(f"  -> CORREGIDO")
            fixed_count += 1
        else:
            print(f"  -> Sin cambios")
    else:
        print(f"No encontrado: {file_path}")
        error_count += 1

print("=" * 60)
print(f"ARCHIVOS CORREGIDOS: {fixed_count}")
print(f"ARCHIVOS NO ENCONTRADOS: {error_count}")
print(f"TOTAL PROCESADOS: {len(problematic_files)}")
print("FINALIZANDO CORRECION MASIVA")