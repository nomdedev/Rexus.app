#!/usr/bin/env python3
"""
Script automatizado para corregir vulnerabilidades críticas de SQL injection
Aplicación masiva de correcciones seguras
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from datetime import datetime

class AutoSQLFixer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = Path("backups_security")
        self.fixes_count = 0
        
    def create_backup(self, file_path: Path):
        """Crea backup del archivo antes de modificarlo."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        backup_path = self.backup_dir / f"{file_path.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        
    def fix_f_string_sql(self, content: str) -> str:
        """Corrige f-strings en consultas SQL."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Detectar f-strings con SQL keywords
            if re.search(r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER).*\{.*\}.*["\']', line, re.IGNORECASE):
                # Intentar corrección automática simple
                # f"SELECT * FROM table WHERE id = {var}" -> "SELECT * FROM table WHERE id = ?", (var,)
                
                # Buscar patrón f"...{var}..."
                f_pattern = r'f"([^"]*)\{([^}]*)\}([^"]*)"'
                match = re.search(f_pattern, line)
                
                if match:
                    before_var = match.group(1)
                    var_name = match.group(2)
                    after_var = match.group(3)
                    
                    # Crear query segura
                    safe_query = f'"{before_var}?{after_var}"'
                    safe_params = f", ({var_name},)"
                    
                    # Reemplazar en la línea
                    old_part = match.group(0)
                    new_part = safe_query + safe_params
                    
                    fixed_line = line.replace(old_part, new_part)
                    fixed_lines.append(f"        # FIXED: SQL Injection vulnerability")
                    fixed_lines.append(fixed_line)
                    self.fixes_count += 1
                    continue
            
            # Detectar .format() en SQL
            if re.search(r'.*(?:SELECT|INSERT|UPDATE|DELETE).*\.format\(', line, re.IGNORECASE):
                # Marcar para revisión manual
                fixed_lines.append(f"        # TODO: MANUAL FIX REQUIRED - SQL Injection via .format()")
                fixed_lines.append(f"        # {line.strip()}")
                fixed_lines.append(line)
                continue
            
            # Detectar concatenación peligrosa
            if re.search(r'.*(?:SELECT|INSERT|UPDATE|DELETE).*\+.*["\']', line, re.IGNORECASE):
                fixed_lines.append(f"        # TODO: MANUAL FIX REQUIRED - SQL Injection via concatenation")
                fixed_lines.append(f"        # {line.strip()}")
                fixed_lines.append(line)
                continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def add_sql_security_imports(self, content: str, file_path: str) -> str:
        """Añade imports de seguridad SQL si no existen."""
        if "from rexus.core.sql_query_manager import SQLQueryManager" in content:
            return content
            
        # Buscar donde insertar el import
        lines = content.split('\n')
        import_index = -1
        
        for i, line in enumerate(lines):
            if line.startswith('from rexus.') or line.startswith('import rexus.'):
                import_index = i
            elif line.startswith('from PyQt6') or line.startswith('import PyQt6'):
                if import_index == -1:
                    import_index = i
        
        if import_index != -1:
            lines.insert(import_index + 1, "from rexus.core.sql_query_manager import SQLQueryManager")
            lines.insert(import_index + 2, "from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric")
            return '\n'.join(lines)
        
        return content
    
    def fix_file(self, file_path: Path) -> bool:
        """Corrige un archivo individual."""
        try:
            # Crear backup
            self.create_backup(file_path)
            
            # Leer contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar correcciones
            content = self.fix_f_string_sql(content)
            content = self.add_sql_security_imports(content, str(file_path))
            
            # Escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            
        return False
    
    def fix_critical_files(self):
        """Corrige archivos críticos del proyecto."""
        critical_patterns = [
            "rexus/modules/*/model.py",
            "rexus/modules/*/controller.py", 
            "rexus/core/*.py",
            "rexus/modules/*/submodules/*.py"
        ]
        
        files_fixed = []
        
        print("🔧 Iniciando corrección automática de vulnerabilidades SQL...")
        
        for pattern in critical_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.suffix == '.py':
                    # Saltar archivos de prueba y backup
                    if any(skip in str(file_path) for skip in ['test_', 'backup', '__pycache__']):
                        continue
                    
                    print(f"📁 Procesando: {file_path.relative_to(self.root_path)}")
                    
                    if self.fix_file(file_path):
                        files_fixed.append(str(file_path.relative_to(self.root_path)))
        
        print(f"\n✅ Archivos procesados: {len(files_fixed)}")
        print(f"🔧 Correcciones automáticas aplicadas: {self.fixes_count}")
        
        if files_fixed:
            print(f"\n📋 ARCHIVOS MODIFICADOS:")
            for file in files_fixed[:20]:  # Mostrar primeros 20
                print(f"  • {file}")
            if len(files_fixed) > 20:
                print(f"  • ... y {len(files_fixed) - 20} más")
        
        return files_fixed

def main():
    print("🛡️ CORRECTOR AUTOMÁTICO DE SQL INJECTION - REXUS.APP")
    print("=" * 60)
    
    fixer = AutoSQLFixer()
    files_fixed = fixer.fix_critical_files()
    
    print(f"\n📊 RESUMEN:")
    print(f"• Archivos modificados: {len(files_fixed)}")
    print(f"• Correcciones automáticas: {fixer.fixes_count}")
    print(f"• Backups creados en: {fixer.backup_dir}")
    
    if fixer.fixes_count > 0:
        print(f"\n⚠️ IMPORTANTE:")
        print(f"• Se aplicaron correcciones automáticas básicas")
        print(f"• Revisar manualmente todos los archivos modificados")
        print(f"• Buscar comentarios 'TODO: MANUAL FIX REQUIRED'")
        print(f"• Usar SQLQueryManager para consultas complejas")
        
    print(f"\n🔄 Recomendación: Ejecutar tests después de las correcciones")
    
    return files_fixed

if __name__ == "__main__":
    main()
