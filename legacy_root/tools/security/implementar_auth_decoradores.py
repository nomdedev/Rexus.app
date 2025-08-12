#!/usr/bin/env python3
"""
Script para implementar automáticamente decoradores @auth_required
en todos los métodos que tienen TODOs pendientes
"""

import os
import re
from pathlib import Path


class AuthDecoratorImplementer:
    def __init__(self):
        self.base_path = Path.cwd()
        self.processed_files = []
        self.methods_updated = 0

    def process_all_modules(self):
        """Procesa todos los módulos con TODOs de auth_required"""
        modules_dir = self.base_path / "rexus" / "modules"
        
        for module_path in modules_dir.rglob("*.py"):
            if self.has_auth_todos(module_path):
                print(f"[INFO] Procesando: {module_path.relative_to(self.base_path)}")
                self.implement_decorators(module_path)
        
        self.generate_report()

    def has_auth_todos(self, file_path):
        """Verifica si el archivo tiene TODOs de auth_required"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return "TODO: Implementar @auth_required" in content
        except Exception:
            return False

    def implement_decorators(self, file_path):
        """Implementa decoradores en un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            
            # Verificar que tenga el import necesario
            if "from rexus.core.auth_decorators import" not in content:
                content = self.add_import(content)

            # Implementar decoradores según el tipo de método
            content = self.replace_auth_todos(content)
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.processed_files.append(file_path)
                print(f"[OK] Actualizado: {file_path.name}")
            else:
                print(f"[WARN] Sin cambios: {file_path.name}")
                
        except Exception as e:
            print(f"[ERROR] Error procesando {file_path}: {e}")

    def add_import(self, content):
        """Agrega el import de decoradores si no existe"""
        # Buscar la sección de imports
        import_section = []
        lines = content.split('\n')
        
        # Encontrar donde insertar el import
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('from rexus.') or line.startswith('import '):
                import_section.append(i)
                insert_index = i + 1
        
        # Si ya existe un import de rexus.core, insertarlo cerca
        for i, line in enumerate(lines):
            if 'from rexus.core' in line:
                insert_index = i + 1
                break
        
        # Insertar el import
        new_import = "from rexus.core.auth_decorators import auth_required, admin_required, permission_required"
        lines.insert(insert_index, new_import)
        
        return '\n'.join(lines)

    def replace_auth_todos(self, content):
        """Reemplaza TODOs con decoradores apropiados"""
        # Patrón para encontrar TODOs seguidos de definición de método
        pattern = r'(\s*)(# TODO: Implementar @auth_required o verificación manual\s*\n)(\s*)(def\s+(\w+)\s*\([^)]*\):)'
        
        def replace_function(match):
            indent = match.group(1)
            todo_line = match.group(2)
            method_indent = match.group(3)
            method_def = match.group(4)
            method_name = match.group(5)
            
            # Determinar el decorador apropiado según el nombre del método
            decorator = self.get_appropriate_decorator(method_name)
            
            # Construir reemplazo
            replacement = f"{indent}@{decorator}\n{method_indent}{method_def}"
            
            self.methods_updated += 1
            print(f"  [APPLY] {method_name}() -> @{decorator}")
            
            return replacement
        
        return re.sub(pattern, replace_function, content, flags=re.MULTILINE)

    def get_appropriate_decorator(self, method_name):
        """Determina el decorador apropiado según el nombre del método"""
        method_lower = method_name.lower()
        
        # Métodos que requieren permisos de admin
        admin_keywords = [
            'delete', 'eliminar', 'borrar', 'remove',
            'create_user', 'crear_usuario', 'add_user',
            'manage', 'gestionar', 'admin', 'configurar'
        ]
        
        # Métodos que requieren permisos específicos
        permission_methods = {
            'export': 'permission_required("export")',
            'backup': 'permission_required("backup")', 
            'restore': 'permission_required("restore")',
            'audit': 'permission_required("audit")'
        }
        
        # Verificar si requiere admin
        for keyword in admin_keywords:
            if keyword in method_lower:
                return "admin_required"
        
        # Verificar si requiere permiso específico
        for keyword, decorator in permission_methods.items():
            if keyword in method_lower:
                return decorator
        
        # Por defecto, auth_required
        return "auth_required"

    def generate_report(self):
        """Genera reporte final de la implementación"""
        print("\n" + "="*60)
        print("[SECURITY] REPORTE DE IMPLEMENTACION DE DECORADORES")
        print("="*60)
        
        print(f"\n[STATS] ESTADISTICAS:")
        print(f"   Archivos procesados: {len(self.processed_files)}")
        print(f"   Metodos actualizados: {self.methods_updated}")
        
        if self.processed_files:
            print(f"\n[FILES] ARCHIVOS MODIFICADOS:")
            for file_path in self.processed_files:
                rel_path = file_path.relative_to(self.base_path)
                print(f"   [OK] {rel_path}")
        
        print(f"\n[NEXT] PROXIMOS PASOS:")
        print("   1. Ejecutar tests para verificar funcionalidad")
        print("   2. Probar login en la aplicación")
        print("   3. Verificar que los permisos funcionen correctamente")
        print("   4. Revisar logs de auditoría")
        
        return len(self.processed_files) > 0


def main():
    """Función principal"""
    print("[SECURITY] IMPLEMENTADOR AUTOMATICO DE DECORADORES @auth_required")
    print("=" * 60)
    
    implementer = AuthDecoratorImplementer()
    
    try:
        implementer.process_all_modules()
        print("\n[SUCCESS] Implementacion completada exitosamente")
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la implementacion: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()