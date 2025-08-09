#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis comunes detectados en el proyecto
"""

import ast
import os
from pathlib import Path
import re

class SyntaxErrorFixer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.fixed_files = []
        self.error_files = []
        
    def check_syntax(self, file_path):
        """Verifica la sintaxis de un archivo Python."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def fix_common_syntax_errors(self, file_path):
        """Corrige errores de sintaxis comunes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_applied = []
            
            # 1. Fix unterminated triple-quoted strings
            if 'unterminated triple-quoted string' in str(self.check_syntax(file_path)[1]):
                # Buscar """ o ''' no cerrados
                content = re.sub(r'("""|\'\'\')\s*$', r'\1\n\1', content, flags=re.MULTILINE)
                fixes_applied.append("Fixed unterminated triple-quoted strings")
            
            # 2. Fix expected 'except' or 'finally' block
            if 'expected \'except\' or \'finally\' block' in str(self.check_syntax(file_path)[1]):
                # Buscar try: sin except/finally
                content = re.sub(r'(\s*)try:\s*\n(\s*)([^e].*?\n)', 
                                r'\1try:\n\2\3\2except Exception as e:\n\2    pass\n', 
                                content, flags=re.MULTILINE | re.DOTALL)
                fixes_applied.append("Added missing except blocks")
            
            # 3. Fix expected indented block
            if 'expected an indented block' in str(self.check_syntax(file_path)[1]):
                # Buscar funciones/clases/if/etc sin contenido
                patterns = [
                    (r'(\s*)(def [^:]+:)\s*\n(\s*\n|\s*#.*\n)*(\s*)([a-zA-Z])', r'\1\2\n\1    pass\n\4\5'),
                    (r'(\s*)(class [^:]+:)\s*\n(\s*\n|\s*#.*\n)*(\s*)([a-zA-Z])', r'\1\2\n\1    pass\n\4\5'),
                    (r'(\s*)(if [^:]+:)\s*\n(\s*\n|\s*#.*\n)*(\s*)([a-zA-Z])', r'\1\2\n\1    pass\n\4\5'),
                    (r'(\s*)(else:)\s*\n(\s*\n|\s*#.*\n)*(\s*)([a-zA-Z])', r'\1\2\n\1    pass\n\4\5'),
                    (r'(\s*)(except [^:]*:)\s*\n(\s*\n|\s*#.*\n)*(\s*)([a-zA-Z])', r'\1\2\n\1    pass\n\4\5'),
                ]
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                fixes_applied.append("Added missing indented blocks")
            
            # 4. Fix invalid syntax (common cases)
            if 'invalid syntax' in str(self.check_syntax(file_path)[1]):
                # Fix common f-string issues
                content = re.sub(r'f"[^"]*\{\s*\}[^"]*"', r'""', content)
                # Fix unmatched brackets
                content = re.sub(r'\[([^\[\]]*)\)', r'[\1]', content)
                content = re.sub(r'\(([^\(\)]*)\]', r'(\1)', content)
                fixes_applied.append("Fixed common invalid syntax")
            
            # 5. Fix unexpected indent
            if 'unexpected indent' in str(self.check_syntax(file_path)[1]):
                lines = content.split('\n')
                fixed_lines = []
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(' ') and i > 0:
                        # Línea sin indentación después de línea con código
                        prev_line = lines[i-1].strip()
                        if prev_line and not prev_line.endswith(':'):
                            fixed_lines.append(line)
                        else:
                            fixed_lines.append('    ' + line.lstrip())
                    else:
                        fixed_lines.append(line)
                content = '\n'.join(fixed_lines)
                fixes_applied.append("Fixed unexpected indentation")
            
            # Solo escribir si hubo cambios
            if content != original_content:
                # Verificar que la sintaxis esté correcta ahora
                try:
                    ast.parse(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixed_files.append((str(file_path), fixes_applied))
                    return True, fixes_applied
                except SyntaxError:
                    # Si aún hay errores, no guardar
                    return False, ["Automatic fix failed, manual intervention needed"]
            
            return False, ["No automatic fix available"]
            
        except Exception as e:
            return False, [f"Error processing file: {str(e)}"]
    
    def scan_and_fix(self):
        """Escanea y corrige errores de sintaxis en todo el proyecto."""
        print("🔍 Escaneando archivos Python para errores de sintaxis...")
        
        total_files = 0
        syntax_errors = 0
        
        for py_file in self.root_path.rglob("*.py"):
            # Saltar archivos de respaldo y temporales
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            total_files += 1
            
            # Verificar sintaxis
            is_valid, error = self.check_syntax(py_file)
            
            if not is_valid:
                syntax_errors += 1
                print(f"❌ Error en {py_file.relative_to(self.root_path)}: {error}")
                
                # Intentar corregir automáticamente
                fixed, fixes = self.fix_common_syntax_errors(py_file)
                
                if fixed:
                    print(f"   ✅ Corregido automáticamente: {', '.join(fixes)}")
                else:
                    print(f"   ⚠️  Requiere corrección manual: {', '.join(fixes)}")
                    self.error_files.append((str(py_file), error))
        
        print(f"\n📊 Resumen:")
        print(f"Total de archivos: {total_files}")
        print(f"Errores de sintaxis: {syntax_errors}")
        print(f"Archivos corregidos automáticamente: {len(self.fixed_files)}")
        print(f"Archivos que requieren corrección manual: {len(self.error_files)}")
        
        return self.fixed_files, self.error_files

def main():
    print("🔧 Iniciando corrección de errores de sintaxis...")
    
    fixer = SyntaxErrorFixer(".")
    fixed_files, error_files = fixer.scan_and_fix()
    
    # Generar reporte
    if fixed_files or error_files:
        with open('syntax_fixes_report.txt', 'w', encoding='utf-8') as f:
            f.write("REPORTE DE CORRECCIÓN DE ERRORES DE SINTAXIS\n")
            f.write("=" * 50 + "\n\n")
            
            if fixed_files:
                f.write("ARCHIVOS CORREGIDOS AUTOMÁTICAMENTE:\n")
                f.write("-" * 30 + "\n")
                for file_path, fixes in fixed_files:
                    f.write(f"\n{file_path}:\n")
                    for fix in fixes:
                        f.write(f"  - {fix}\n")
            
            if error_files:
                f.write("\n\nARCHIVOS QUE REQUIEREN CORRECCIÓN MANUAL:\n")
                f.write("-" * 30 + "\n")
                for file_path, error in error_files:
                    f.write(f"\n{file_path}:\n")
                    f.write(f"  Error: {error}\n")
        
        print(f"\n📄 Reporte guardado en: syntax_fixes_report.txt")
    
    if not error_files:
        print("\n✅ Todos los errores de sintaxis han sido corregidos!")
    else:
        print(f"\n⚠️  {len(error_files)} archivos requieren corrección manual")

if __name__ == "__main__":
    main()
