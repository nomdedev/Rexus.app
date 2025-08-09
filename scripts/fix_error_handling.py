#!/usr/bin/env python3
"""
Script para corregir problemas de manejo de errores y gestión de recursos
Específicamente para Try/Except/Pass y cursor management
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from datetime import datetime

class ErrorHandlingFixer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.fixes_applied = []
        
    def fix_try_except_pass_patterns(self, content: str) -> str:
        """Corrige patrones try/except/pass problemáticos."""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detectar try: seguido de except: pass
            if re.search(r'^\s*try:\s*$', line):
                try_indent = len(line) - len(line.lstrip())
                
                # Buscar el except correspondiente
                j = i + 1
                found_except_pass = False
                
                while j < len(lines):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 0
                    
                    # Si encontramos except: pass en el mismo nivel de indentación
                    if (re.search(r'^\s*except\s*(Exception\s*)?:\s*$', next_line) and 
                        next_indent == try_indent):
                        
                        # Verificar si la siguiente línea es pass
                        if j + 1 < len(lines):
                            pass_line = lines[j + 1]
                            if re.search(r'^\s*pass\s*$', pass_line):
                                found_except_pass = True
                                
                                # Reemplazar con logging apropiado
                                fixed_lines.append(line)  # try:
                                
                                # Agregar contenido del try
                                k = i + 1
                                while k < j:
                                    fixed_lines.append(lines[k])
                                    k += 1
                                
                                # Reemplazar except: pass con except con logging
                                indent_str = ' ' * (try_indent + 4)
                                fixed_lines.append(next_line)  # except:
                                fixed_lines.append(f"{indent_str}logger.error(f\"Error en operación de base de datos: {{e}}\")")
                                fixed_lines.append(f"{indent_str}return None")
                                
                                i = j + 2  # Saltar el pass
                                self.fixes_applied.append("try/except/pass pattern fixed")
                                break
                        break
                    elif next_indent <= try_indent and next_line.strip():
                        break
                    j += 1
                
                if not found_except_pass:
                    fixed_lines.append(line)
                    i += 1
            else:
                fixed_lines.append(line)
                i += 1
        
        return '\n'.join(fixed_lines)
    
    def fix_cursor_management(self, content: str) -> str:
        """Mejora el manejo de cursors para evitar warnings."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Detectar patrones de cursor.close() que pueden estar desvinculados
            if 'cursor.close()' in line and 'if cursor:' not in line:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Reemplazar con verificación segura
                fixed_lines.append(f"{indent_str}if cursor:")
                fixed_lines.append(f"{indent_str}    cursor.close()")
                self.fixes_applied.append("cursor.close() pattern fixed")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def add_proper_logging_imports(self, content: str) -> str:
        """Añade imports de logging si no existen."""
        if "import logging" in content or "from logging import" in content:
            return content
        
        lines = content.split('\n')
        
        # Buscar donde insertar el import
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('"""') and '"""' in line[3:]:
                insert_index = i + 1
                break
            elif line.startswith('"""'):
                # Buscar el cierre del docstring
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j]:
                        insert_index = j + 1
                        break
                break
        
        # Insertar import de logging
        lines.insert(insert_index, "import logging")
        lines.insert(insert_index + 1, "")
        lines.insert(insert_index + 2, "logger = logging.getLogger(__name__)")
        lines.insert(insert_index + 3, "")
        
        return '\n'.join(lines)
    
    def fix_type_annotations(self, content: str) -> str:
        """Corrige problemas de anotaciones de tipo."""
        # Corregir get() calls con validación de None
        pattern = r'(\w+)\.get\([\'"](\w+)[\'"]\)'
        
        def replace_get_call(match):
            var_name = match.group(1)
            key = match.group(2)
            return f"({var_name}.get('{key}') or '')"
        
        content = re.sub(pattern, replace_get_call, content)
        return content
    
    def fix_file(self, file_path: Path) -> bool:
        """Corrige un archivo individual."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar todas las correcciones
            content = self.add_proper_logging_imports(content)
            content = self.fix_try_except_pass_patterns(content)
            content = self.fix_cursor_management(content)
            content = self.fix_type_annotations(content)
            
            # Escribir si hubo cambios
            if content != original_content:
                # Crear backup
                backup_dir = Path("backups_error_handling")
                backup_dir.mkdir(exist_ok=True)
                
                backup_path = backup_dir / f"{file_path.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(file_path, backup_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            
        return False
    
    def fix_problematic_files(self):
        """Corrige archivos con problemas conocidos."""
        problematic_files = [
            "rexus/modules/usuarios/submodules/profiles_manager.py",
            "rexus/modules/usuarios/submodules/auth_manager.py", 
            "rexus/modules/usuarios/submodules/permissions_manager.py"
        ]
        
        files_fixed = []
        
        print("🔧 Corrigiendo problemas de manejo de errores...")
        
        for file_rel_path in problematic_files:
            file_path = self.root_path / file_rel_path
            if file_path.exists():
                print(f"📁 Procesando: {file_rel_path}")
                
                if self.fix_file(file_path):
                    files_fixed.append(file_rel_path)
                    print(f"  ✅ Corregido")
                else:
                    print(f"  ℹ️ Sin cambios necesarios")
        
        return files_fixed

def main():
    print("🛠️ CORRECTOR DE MANEJO DE ERRORES - REXUS.APP")
    print("=" * 55)
    
    fixer = ErrorHandlingFixer()
    files_fixed = fixer.fix_problematic_files()
    
    print(f"\n📊 RESUMEN:")
    print(f"• Archivos procesados: {len(files_fixed)}")
    print(f"• Correcciones aplicadas: {len(fixer.fixes_applied)}")
    
    if files_fixed:
        print(f"\n📋 ARCHIVOS MODIFICADOS:")
        for file in files_fixed:
            print(f"  • {file}")
    
    if fixer.fixes_applied:
        print(f"\n🔧 TIPOS DE CORRECCIONES:")
        for fix_type in set(fixer.fixes_applied):
            count = fixer.fixes_applied.count(fix_type)
            print(f"  • {fix_type}: {count}")
    
    print(f"\n✅ Corrección de manejo de errores completada")
    
    return files_fixed

if __name__ == "__main__":
    main()
