#!/usr/bin/env python3
"""
Script para aplicar protección XSS automáticamente a módulos de Rexus.app

Aplica protección contra Cross-Site Scripting a formularios y campos de entrada.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class XSSProtectionApplier:
    """Aplicador automático de protección XSS."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.modules_dir = root_dir / "rexus" / "modules"
        self.protected_files = []
        self.protection_stats = {
            'files_processed': 0,
            'fields_protected': 0,
            'imports_added': 0,
            'methods_added': 0
        }
    
    def get_module_view_files(self) -> List[Path]:
        """Obtiene todos los archivos view.py de los módulos."""
        view_files = []
        
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir():
                view_file = module_dir / "view.py"
                if view_file.exists():
                    view_files.append(view_file)
        
        return view_files
    
    def has_xss_protection(self, file_path: Path) -> bool:
        """Verifica si un archivo ya tiene protección XSS."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return 'xss_protection' in content or 'FormProtector' in content
        except:
            return False
    
    def add_xss_imports(self, file_path: Path) -> bool:
        """Añade imports de protección XSS."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Buscar línea de imports existentes de rexus.utils
            import_pattern = r'(from rexus\.utils\.[^\s]+ import [^\n]+)'
            matches = list(re.finditer(import_pattern, content))
            
            if matches:
                # Añadir después del último import de utils
                last_match = matches[-1]
                insert_pos = last_match.end()
                
                xss_import = "\nfrom rexus.utils.xss_protection import FormProtector, XSSProtection, xss_protect"
                
                new_content = content[:insert_pos] + xss_import + content[insert_pos:]
                file_path.write_text(new_content, encoding='utf-8')
                return True
            else:
                # Buscar otros imports para insertar después
                from_pattern = r'(from PyQt6\.QtWidgets import[^\n]+\n)'
                match = re.search(from_pattern, content)
                
                if match:
                    insert_pos = match.end()
                    xss_import = "\nfrom rexus.utils.xss_protection import FormProtector, XSSProtection, xss_protect\n"
                    
                    new_content = content[:insert_pos] + xss_import + content[insert_pos:]
                    file_path.write_text(new_content, encoding='utf-8')
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error añadiendo imports a {file_path}: {e}")
            return False
    
    def find_form_fields(self, content: str) -> List[Tuple[str, str, int]]:
        """Encuentra campos de formulario en el contenido."""
        fields = []
        
        # Patrones para encontrar campos
        patterns = [
            r'self\.(\w+)\s*=\s*QLineEdit\(\)',
            r'self\.(\w+)\s*=\s*QTextEdit\(\)',
            r'self\.(\w+)\s*=\s*QPlainTextEdit\(\)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                field_name = match.group(1)
                field_type = 'QLineEdit' if 'QLineEdit' in match.group(0) else \
                           'QTextEdit' if 'QTextEdit' in match.group(0) else 'QPlainTextEdit'
                line_pos = content[:match.start()].count('\n') + 1
                fields.append((field_name, field_type, line_pos))
        
        return fields
    
    def add_form_protector_init(self, content: str) -> str:
        """Añade inicialización del FormProtector."""
        # Buscar método __init__ o init_ui
        init_pattern = r'(def (?:__init__|init_ui)\(self[^)]*\):[^\n]*\n)'
        match = re.search(init_pattern, content)
        
        if match:
            # Encontrar el final de la declaración del método
            method_start = match.end()
            
            # Buscar la primera línea de código real del método
            lines = content[method_start:].split('\n')
            insert_line = 0
            
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('"""') and not line.strip().startswith('\'\'\''):
                    insert_line = i
                    break
            
            # Insertar inicialización del form protector
            protector_init = '''        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(self._on_dangerous_content)
        '''
            
            lines.insert(insert_line, protector_init)
            new_method_content = '\n'.join(lines)
            
            return content[:method_start] + new_method_content
        
        return content
    
    def add_protection_methods(self, content: str) -> str:
        """Añade métodos de protección XSS."""
        # Buscar el final de la clase
        class_end_pattern = r'(\n    def [^:]+:[^}]+)$'
        
        protection_methods = '''
    def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja la detección de contenido peligroso en formularios."""
        from rexus.utils.security import log_security_event
        from rexus.utils.message_system import show_warning
        
        # Log del evento de seguridad
        log_security_event(
            "XSS_ATTEMPT",
            f"Contenido peligroso detectado en campo '{field_name}': {content[:100]}...",
            "unknown"
        )
        
        # Mostrar advertencia al usuario
        show_warning(
            self,
            "Contenido No Permitido",
            f"Se ha detectado contenido potencialmente peligroso en el campo '{field_name}'.\n\n"
            "El contenido ha sido automáticamente sanitizado por seguridad."
        )
    
    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, 'form_protector'):
            return self.form_protector.get_sanitized_data()
        else:
            return {}
'''
        
        return content + protection_methods
    
    def protect_fields_in_content(self, content: str, fields: List[Tuple[str, str, int]]) -> str:
        """Añade protección a campos encontrados."""
        if not fields:
            return content
        
        lines = content.split('\n')
        
        # Encontrar donde añadir las protecciones (después de crear los campos)
        protection_lines = []
        protection_lines.append('')
        protection_lines.append('        # Proteger campos contra XSS')
        
        for field_name, field_type, _ in fields:
            max_length = 100  # Por defecto
            if 'password' in field_name.lower():
                max_length = 50
            elif 'email' in field_name.lower():
                max_length = 100
            elif 'descripcion' in field_name.lower() or 'nota' in field_name.lower():
                max_length = 500
            elif 'codigo' in field_name.lower():
                max_length = 50
            
            protection_lines.append(f'        self.form_protector.protect_field(self.{field_name}, "{field_name}", {max_length})')
        
        # Encontrar lugar apropiado para insertar (después del último campo)
        last_field_line = max(line_pos for _, _, line_pos in fields)
        
        # Buscar la línea apropiada en el contenido
        for i, line in enumerate(lines):
            if i >= last_field_line + 5:  # Algunas líneas después del último campo
                if line.strip() == '' or line.strip().startswith('#'):
                    lines[i:i] = protection_lines
                    break
        
        return '\n'.join(lines)
    
    def apply_protection_to_file(self, file_path: Path) -> bool:
        """Aplica protección XSS a un archivo específico."""
        try:
            print(f"Procesando: {file_path.name}")
            
            if self.has_xss_protection(file_path):
                print(f"  [OK] Ya tiene proteccion XSS")
                return True
            
            # Leer contenido
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # 1. Añadir imports
            if self.add_xss_imports(file_path):
                content = file_path.read_text(encoding='utf-8')
                self.protection_stats['imports_added'] += 1
                print(f"  [OK] Imports anadidos")
            
            # 2. Encontrar campos de formulario
            fields = self.find_form_fields(content)
            if fields:
                print(f"  [OK] Encontrados {len(fields)} campos: {[f[0] for f in fields]}")
                self.protection_stats['fields_protected'] += len(fields)
            
            # 3. Añadir inicialización del protector
            content = self.add_form_protector_init(content)
            
            # 4. Proteger campos
            content = self.protect_fields_in_content(content, fields)
            
            # 5. Añadir métodos de protección
            content = self.add_protection_methods(content)
            self.protection_stats['methods_added'] += 1
            
            # Guardar cambios
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"  [OK] Proteccion aplicada exitosamente")
                self.protected_files.append(file_path)
                self.protection_stats['files_processed'] += 1
                return True
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            return False
    
    def apply_protection_to_all_modules(self):
        """Aplica protección XSS a todos los módulos."""
        print("=== APLICANDO PROTECCIÓN XSS A MÓDULOS ===")
        print()
        
        view_files = self.get_module_view_files()
        print(f"Encontrados {len(view_files)} archivos view.py")
        print()
        
        for view_file in view_files:
            self.apply_protection_to_file(view_file)
            print()
        
        # Mostrar estadísticas
        print("=== RESUMEN DE PROTECCIÓN XSS ===")
        print(f"Archivos procesados: {self.protection_stats['files_processed']}")
        print(f"Campos protegidos: {self.protection_stats['fields_protected']}")
        print(f"Imports añadidos: {self.protection_stats['imports_added']}")
        print(f"Métodos añadidos: {self.protection_stats['methods_added']}")
        print()
        
        if self.protected_files:
            print("Archivos modificados:")
            for file_path in self.protected_files:
                print(f"  - {file_path.relative_to(self.root_dir)}")


def main():
    """Función principal."""
    # Obtener directorio raíz del proyecto
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print(f"Directorio del proyecto: {root_dir}")
    print()
    
    # Crear aplicador y ejecutar
    applier = XSSProtectionApplier(root_dir)
    applier.apply_protection_to_all_modules()
    
    print("\n[EXITO] Proteccion XSS aplicada exitosamente a todos los modulos")


if __name__ == "__main__":
    main()