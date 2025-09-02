#!/usr/bin/env python3
"""
Script de corrección masiva de errores en Rexus.app
Corrige automáticamente los errores más comunes identificados
"""

import os
import re
import glob
from typing import List, Dict

class MassiveErrorFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        
    def fix_undefined_logger(self, file_path: str, content: str) -> str:
        """Corrige logger no definido agregando import"""
        if 'logger' in content and 'from rexus.utils.logging_config import get_logger' not in content:
            # Agregar import de logger después de otros imports
            lines = content.split('\n')
            import_section_end = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_section_end = i
                elif line.strip() == '' and import_section_end > 0:
                    break
                    
            if import_section_end > 0:
                lines.insert(import_section_end + 1, 'from rexus.utils.logging_config import get_logger')
                lines.insert(import_section_end + 2, 'logger = get_logger(__name__)')
                lines.insert(import_section_end + 3, '')
                self.fixes_applied += 1
                return '\\n'.join(lines)
        return content
    
    def fix_undefined_sqlite3(self, file_path: str, content: str) -> str:
        """Corrige sqlite3 no definido"""
        if 'sqlite3' in content and 'import sqlite3' not in content:
            content = 'import sqlite3\\n' + content
            self.fixes_applied += 1
        return content
    
    def fix_syntax_errors(self, file_path: str, content: str) -> str:
        """Corrige errores de sintaxis comunes"""
        original_content = content
        
        # 1. Corregir f-strings malformados
        # Patrón: logger.error(f"text {var")  ->  logger.error(f"text {var}")
        content = re.sub(r'f"([^"]*\{[^}]*)"([^"]*\{[^}]*)"\\)', r'f"\\1}\\2}")', content)
        
        # 2. Corregir paréntesis desbalanceados
        # Patrón: logger.error(f"text"  ->  logger.error(f"text")
        content = re.sub(r'(logger\\.[a-z]+\\(f?"[^"]*")(\\s*$)', r'\\1)', content, flags=re.MULTILINE)
        
        # 3. Corregir f-strings con llaves simples en CSS
        # Patrón: f"... {color} ..." con CSS -> f"... {{color}} ..."
        if 'QSS' in content or 'setStyleSheet' in content:
            # Escapar llaves en f-strings para CSS
            def escape_css_braces(match):
                f_string = match.group(0)
                # Solo escapar llaves que no son parte de variables {var}
                escaped = re.sub(r'(?<!\\{)\\{(?!\\w+\\})', '{{', f_string)
                escaped = re.sub(r'(?<!\\{\\w+)\\}(?!\\})', '}}', escaped)
                return escaped
            
            content = re.sub(r'f"""[^"]*"""', escape_css_braces, content)
            content = re.sub(r'f"[^"]*"', escape_css_braces, content)
        
        # 4. Corregir strings literales no terminados
        content = re.sub(r'logger\\.(\\w+)\\(f?"([^"]*)"([^)]*)$', r'logger.\\1(f"\\2")', content, flags=re.MULTILINE)
        
        if content != original_content:
            self.fixes_applied += 1
            
        return content
    
    def remove_duplicate_imports(self, file_path: str, content: str) -> str:
        """Elimina imports duplicados y redefiniciones"""
        lines = content.split('\\n')
        seen_imports = set()
        seen_functions = set()
        cleaned_lines = []
        
        for line in lines:
            # Detectar imports duplicados
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                if line.strip() not in seen_imports:
                    seen_imports.add(line.strip())
                    cleaned_lines.append(line)
                else:
                    self.fixes_applied += 1  # Skip duplicate
                    continue
            
            # Detectar redefiniciones de funciones
            elif line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                if func_name not in seen_functions:
                    seen_functions.add(func_name)
                    cleaned_lines.append(line)
                else:
                    # Skip redefinition, but keep track
                    self.fixes_applied += 1
                    continue
            else:
                cleaned_lines.append(line)
        
        return '\\n'.join(cleaned_lines)
    
    def fix_file(self, file_path: str) -> bool:
        """Aplica todas las correcciones a un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            
            # Aplicar todas las correcciones
            content = self.fix_undefined_logger(file_path, content)
            content = self.fix_undefined_sqlite3(file_path, content) 
            content = self.fix_syntax_errors(file_path, content)
            content = self.remove_duplicate_imports(file_path, content)
            
            # Escribir solo si hay cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            
        return False
    
    def fix_all_files(self):
        """Corrige todos los archivos Python en el proyecto"""
        python_files = glob.glob('rexus/**/*.py', recursive=True)
        
        print(f"Iniciando corrección masiva de {len(python_files)} archivos...")
        
        for file_path in python_files:
            self.files_processed += 1
            if self.fix_file(file_path):
                print(f"✓ {file_path}")
            
            # Progreso cada 20 archivos
            if self.files_processed % 20 == 0:
                print(f"Progreso: {self.files_processed}/{len(python_files)} archivos procesados...")
        
        print(f"\\nCorrecciones completadas:")
        print(f"- Archivos procesados: {self.files_processed}")
        print(f"- Correcciones aplicadas: {self.fixes_applied}")

def main():
    fixer = MassiveErrorFixer()
    fixer.fix_all_files()

if __name__ == "__main__":
    main()