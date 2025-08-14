#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis críticos detectados por PyLint
Se enfoca en los errores más graves que impiden el parsing
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple

class SyntaxErrorFixer:
    """Corrector automático de errores de sintaxis críticos"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors_fixed = 0
        self.files_processed = 0
        
    def fix_all_syntax_errors(self):
        """Corrige todos los errores de sintaxis detectados"""
        print("=== CORRIGIENDO ERRORES DE SINTAXIS CRITICOS ===")
        
        # Lista de archivos con errores conocidos de PyLint
        problem_files = [
            "rexus/api/server.py",
            "rexus/core/config.py", 
            "rexus/core/rate_limiter.py",
            "rexus/core/rbac_database.py",
            "rexus/modules/administracion/view.py",
            "rexus/modules/administracion/contabilidad/model.py",
            "rexus/modules/compras/model.py",
            "rexus/modules/compras/view_complete.py",
            "rexus/modules/compras/pedidos/view.py",
            "rexus/modules/configuracion/controller.py",
            "rexus/modules/configuracion/view.py",
            "rexus/modules/obras/produccion/view.py",
            "rexus/modules/pedidos/improved_dialogs.py",
            "rexus/modules/pedidos/model.py",
            "rexus/modules/pedidos/view_complete.py",
            "rexus/modules/usuarios/security_dialog.py",
            "rexus/security/csrf_protection.py",
            "rexus/security/user_enumeration_protection.py",
            "rexus/ui/advanced_feedback.py",
            "rexus/utils/backup_system.py",
            "rexus/utils/demo_mode.py",
            "rexus/utils/error_manager.py",
            "rexus/utils/form_styles.py",
            "rexus/utils/form_validators.py"
        ]
        
        for file_path in problem_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.fix_file_syntax_errors(full_path)
        
        print(f"\\n=== RESUMEN ===")
        print(f"Archivos procesados: {self.files_processed}")
        print(f"Errores corregidos: {self.errors_fixed}")
    
    def fix_file_syntax_errors(self, file_path: Path):
        """Corrige errores de sintaxis en un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            file_errors = 0
            
            # 1. Corregir strings no terminados (unterminated string literal)
            content, fixes = self.fix_unterminated_strings(content)
            file_errors += fixes
            
            # 2. Corregir bloques try/except malformados
            content, fixes = self.fix_malformed_try_except(content)
            file_errors += fixes
            
            # 3. Corregir indentación inesperada
            content, fixes = self.fix_unexpected_indent(content)
            file_errors += fixes
            
            # 4. Corregir f-strings con backslash
            content, fixes = self.fix_fstring_backslash(content)
            file_errors += fixes
            
            # 5. Corregir corchetes no balanceados
            content, fixes = self.fix_unmatched_brackets(content)
            file_errors += fixes
            
            # 6. Corregir literales decimales inválidos
            content, fixes = self.fix_invalid_decimal_literals(content)
            file_errors += fixes
            
            # 7. Corregir diccionarios malformados
            content, fixes = self.fix_malformed_dict(content)
            file_errors += fixes
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.errors_fixed += file_errors
                print(f"[FIXED] {file_path}: {file_errors} errores corregidos")
            
            self.files_processed += 1
            
        except Exception as e:
            print(f"[ERROR] Error procesando {file_path}: {e}")
    
    def fix_unterminated_strings(self, content: str) -> Tuple[str, int]:
        """Corrige strings no terminados"""
        fixes = 0
        lines = content.split('\\n')
        
        for i, line in enumerate(lines):
            # Buscar f-strings o strings multilínea problemáticos
            if 'f"' in line and line.count('"') % 2 == 1:
                # String no terminado - agregar comillas de cierre
                if not line.rstrip().endswith('"'):
                    lines[i] = line.rstrip() + '"'
                    fixes += 1
            
            elif "f'" in line and line.count("'") % 2 == 1:
                # String no terminado con comillas simples
                if not line.rstrip().endswith("'"):
                    lines[i] = line.rstrip() + "'"
                    fixes += 1
        
        return '\\n'.join(lines), fixes
    
    def fix_malformed_try_except(self, content: str) -> Tuple[str, int]:
        """Corrige bloques try/except malformados"""
        fixes = 0
        
        # Patrón para try sin except o finally
        pattern = r'(\\s+try:.*?)\\n(\\s*(?!except|finally|\\s+)\\w)'
        
        def replace_try(match):
            nonlocal fixes
            try_block = match.group(1)
            next_line = match.group(2)
            fixes += 1
            return f"{try_block}\\n        pass  # Auto-added\\n    except Exception as e:\\n        print(f'Error: {{e}}')\\n{next_line}"
        
        content = re.sub(pattern, replace_try, content, flags=re.MULTILINE | re.DOTALL)
        
        return content, fixes
    
    def fix_unexpected_indent(self, content: str) -> Tuple[str, int]:
        """Corrige indentación inesperada"""
        fixes = 0
        lines = content.split('\\n')
        
        for i in range(len(lines)):
            line = lines[i]
            if line.strip().startswith('    ') and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.endswith(':') and not prev_line.endswith('\\\\'):
                    # Indentación inesperada - reducir indentación
                    lines[i] = line.lstrip()
                    fixes += 1
        
        return '\\n'.join(lines), fixes
    
    def fix_fstring_backslash(self, content: str) -> Tuple[str, int]:
        """Corrige f-strings con backslash problemáticos"""
        fixes = 0
        
        # Buscar f-strings con backslashes
        pattern = r'f"([^"]*\\\\[^"]*)"'
        
        def replace_fstring(match):
            nonlocal fixes
            inner = match.group(1)
            # Reemplazar backslashes problemáticos con cadenas normales
            if '\\\\n' in inner:
                fixes += 1
                return f'"{inner}"'
            return match.group(0)
        
        content = re.sub(pattern, replace_fstring, content)
        
        return content, fixes
    
    def fix_unmatched_brackets(self, content: str) -> Tuple[str, int]:
        """Corrige corchetes no balanceados"""
        fixes = 0
        lines = content.split('\\n')
        
        for i, line in enumerate(lines):
            # Contar corchetes
            open_brackets = line.count('[')
            close_brackets = line.count(']')
            
            if open_brackets > close_brackets:
                # Agregar corchetes de cierre faltantes
                missing = open_brackets - close_brackets
                lines[i] = line + ']' * missing
                fixes += missing
            elif close_brackets > open_brackets:
                # Remover corchetes de cierre extra
                extra = close_brackets - open_brackets
                lines[i] = line.replace(']', '', extra)
                fixes += extra
        
        return '\\n'.join(lines), fixes
    
    def fix_invalid_decimal_literals(self, content: str) -> Tuple[str, int]:
        """Corrige literales decimales inválidos"""
        fixes = 0
        
        # Buscar patrones como 123.abc o similar
        pattern = r'\\b(\\d+)\\.(\\w+)(?!\\d)'
        
        def replace_decimal(match):
            nonlocal fixes
            number = match.group(1)
            suffix = match.group(2)
            
            # Si no es un número válido, separar
            if not suffix.replace('_', '').isdigit():
                fixes += 1
                return f"{number} {suffix}"
            return match.group(0)
        
        content = re.sub(pattern, replace_decimal, content)
        
        return content, fixes
    
    def fix_malformed_dict(self, content: str) -> Tuple[str, int]:
        """Corrige diccionarios malformados"""
        fixes = 0
        
        # Buscar patrones como {key: : value}
        content = re.sub(r':\\s*:', ':', content)
        if ':  :' in content or ': :' in content:
            fixes += content.count(':  :') + content.count(': :')
        
        return content, fixes

def main():
    fixer = SyntaxErrorFixer(".")
    fixer.fix_all_syntax_errors()
    
    print("\\n=== VALIDACION POST-CORRECCION ===")
    print("Verificando algunos archivos críticos...")
    
    # Verificar algunos archivos críticos
    test_files = [
        "rexus/api/server.py",
        "rexus/modules/compras/model.py", 
        "rexus/modules/pedidos/model.py"
    ]
    
    for file_path in test_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"[OK] {file_path} - Sintaxis válida")
        except SyntaxError as e:
            print(f"[FAIL] {file_path} - Error en línea {e.lineno}: {e.msg}")
        except FileNotFoundError:
            print(f"[SKIP] {file_path} - Archivo no encontrado")
        except Exception as e:
            print(f"[ERROR] {file_path} - {e}")

if __name__ == "__main__":
    main()