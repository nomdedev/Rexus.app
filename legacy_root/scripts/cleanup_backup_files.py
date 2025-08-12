#!/usr/bin/env python
"""
Script para limpiar archivos backup obsoletos
Estos archivos contienen queries hardcodeadas y son obsoletos según el checklist
"""

import os
import sys
from pathlib import Path
import shutil

def cleanup_backup_files():
    """Limpia archivos backup obsoletos de manera segura"""
    print("=== Limpieza de archivos backup obsoletos ===")
    
    root_dir = Path(__file__).parent.parent
    rexus_dir = root_dir / "rexus"
    
    # Crear directorio para archivar backups
    archive_dir = root_dir / "archive" / "obsolete_files"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Patrones de archivos backup a mover
    backup_patterns = [
        "*.backup*",
        "*_refactorizado.py",  # Solo si hay equivalente sin "_refactorizado"
        "*.backup_auth",
        "*.backup_decorators", 
        "*.backup_xss",
        "*.backup_mit",
        "*.backup_sql_injection"
    ]
    
    moved_files = 0
    kept_files = 0
    
    # Buscar archivos backup
    for pattern in backup_patterns:
        backup_files = list(rexus_dir.rglob(pattern))
        
        for backup_file in backup_files:
            # Verificar si es realmente un archivo backup obsoleto
            if should_archive_file(backup_file):
                # Crear estructura de directorios en archive
                relative_path = backup_file.relative_to(rexus_dir)
                archive_path = archive_dir / relative_path
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Mover archivo
                try:
                    shutil.move(str(backup_file), str(archive_path))
                    print(f"Archivado: {relative_path}")
                    moved_files += 1
                except Exception as e:
                    print(f"Error moviendo {backup_file}: {e}")
            else:
                print(f"Conservado: {backup_file.relative_to(rexus_dir)} (archivo activo)")
                kept_files += 1
    
    print(f"\n=== Resumen ===")
    print(f"Archivos archivados: {moved_files}")
    print(f"Archivos conservados: {kept_files}")
    print(f"Ubicación archivo: {archive_dir}")
    
    # Verificar que los módulos principales siguen funcionando
    print(f"\n=== Verificación de módulos ===")
    test_modules = ['inventario', 'compras', 'pedidos', 'herrajes', 'vidrios']
    
    for module in test_modules:
        try:
            __import__(f'rexus.modules.{module}.view')
            print(f"✅ {module}: OK")
        except Exception as e:
            print(f"❌ {module}: ERROR - {e}")
    
    return moved_files

def should_archive_file(file_path):
    """Determina si un archivo debe archivarse"""
    file_name = file_path.name
    
    # Archivar todos los archivos .backup*
    if '.backup' in file_name:
        return True
    
    # Para archivos _refactorizado.py, verificar si existe la versión principal
    if file_name.endswith('_refactorizado.py'):
        main_file = file_path.parent / file_name.replace('_refactorizado.py', '.py')
        if main_file.exists():
            return True
    
    return False

if __name__ == "__main__":
    try:
        moved_count = cleanup_backup_files()
        print(f"\n✅ Limpieza completada exitosamente")
        print(f"📊 {moved_count} archivos backup archivados")
        print(f"🎯 Queries hardcodeadas en backups eliminadas del código activo")
    except Exception as e:
        print(f"❌ Error durante limpieza: {e}")
        sys.exit(1)