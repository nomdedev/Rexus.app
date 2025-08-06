#!/usr/bin/env python3
"""
Script para limpiar TODOs de @auth_required que ya están resueltos
"""

import os
import re
from pathlib import Path


class AuthTODOCleaner:
    def __init__(self):
        self.base_path = Path.cwd()
        self.processed_files = []
        self.todos_cleaned = 0

    def clean_all_modules(self):
        """Limpia TODOs de auth_required en todos los módulos"""
        modules_dir = self.base_path / "rexus" / "modules"
        
        for module_path in modules_dir.rglob("*.py"):
            if self.has_auth_todos_to_clean(module_path):
                print(f"[INFO] Limpiando: {module_path.relative_to(self.base_path)}")
                self.clean_todos(module_path)
        
        self.generate_report()

    def has_auth_todos_to_clean(self, file_path):
        """Verifica si el archivo tiene TODOs que se pueden limpiar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Si tiene decoradores y TODOs, se puede limpiar
                has_decorators = "@auth_required" in content or "@admin_required" in content
                has_todos = "TODO: Implementar @auth_required" in content
                return has_decorators and has_todos
        except Exception:
            return False

    def clean_todos(self, file_path):
        """Limpia TODOs ya resueltos en un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            
            # Patrón para encontrar sección completa de TODO a limpiar
            patterns_to_remove = [
                # Patrón 1: TODO con comentarios de verificación
                r'\s*# 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA\s*\n\s*# TODO: Implementar @auth_required o verificación manual\s*\n(\s*# if not AuthManager\.check_permission.*\n\s*# .*raise PermissionError.*\n\s*#?\s*\n?)?',
                # Patrón 2: Solo TODO
                r'\s*# TODO: Implementar @auth_required o verificación manual\s*\n',
                # Patrón 3: Comentarios de verificación solos
                r'\s*# if not AuthManager\.check_permission.*\n\s*# .*raise PermissionError.*\n'
            ]
            
            todos_removed = 0
            for pattern in patterns_to_remove:
                matches = re.findall(pattern, content)
                if matches:
                    todos_removed += len(matches)
                content = re.sub(pattern, '', content, flags=re.MULTILINE)
            
            # Limpiar líneas vacías duplicadas
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.processed_files.append(file_path)
                self.todos_cleaned += todos_removed
                print(f"  [OK] Limpiado: {todos_removed} TODOs")
            else:
                print(f"  [SKIP] Sin cambios")
                
        except Exception as e:
            print(f"[ERROR] Error limpiando {file_path}: {e}")

    def generate_report(self):
        """Genera reporte final de la limpieza"""
        print("\n" + "="*60)
        print("[CLEANUP] REPORTE DE LIMPIEZA DE TODOS")
        print("="*60)
        
        print(f"\n[STATS] ESTADISTICAS:")
        print(f"   Archivos procesados: {len(self.processed_files)}")
        print(f"   TODOs limpiados: {self.todos_cleaned}")
        
        if self.processed_files:
            print(f"\n[FILES] ARCHIVOS MODIFICADOS:")
            for file_path in self.processed_files:
                rel_path = file_path.relative_to(self.base_path)
                print(f"   [OK] {rel_path}")
        
        return len(self.processed_files) > 0


def main():
    """Función principal"""
    print("[CLEANUP] LIMPIADOR DE TODOS @auth_required RESUELTOS")
    print("=" * 60)
    
    cleaner = AuthTODOCleaner()
    
    try:
        cleaner.clean_all_modules()
        print("\n[SUCCESS] Limpieza completada exitosamente")
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la limpieza: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()