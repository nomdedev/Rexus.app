"""
Tool: cleanup_duplicates (moved from project root)
"""

def notice():
    print('Versión operativa: scripts/tools/cleanup_duplicates.py')

if __name__ == '__main__':
    notice()
#!/usr/bin/env python3
"""
Script de limpieza de archivos duplicados - Rexus.app
Identifica y limpia archivos duplicados en los módulos.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Limpia archivos duplicados del proyecto."""
    modules_path = Path("rexus/modules")

    duplicates_removed = 0

    # Patrones de archivos duplicados a eliminar
    patterns_to_remove = [
        "*_backup*",
        "*_old*",
        "*_nuevo*",
        "*_simple*",
        "*_completa*",
        "*_modernized*",
        "*_integrated*",
        "*.backup*",
        "*_refactorizado*",
        "*_clean*"
    ]

    for module_dir in modules_path.iterdir():
        if not module_dir.is_dir():
            continue

        print(f"\n=== Limpiando módulo: {module_dir.name} ===")

        # Buscar archivos duplicados
        view_files = list(module_dir.glob("view*.py"))
        controller_files = list(module_dir.glob("controller*.py"))
        model_files = list(module_dir.glob("model*.py"))

        print(f"Views encontrados: {len(view_files)}")
        for f in view_files:
            print(f"  - {f.name}")

        print(f"Controllers encontrados: {len(controller_files)}")
        for f in controller_files:
            print(f"  - {f.name}")

        print(f"Models encontrados: {len(model_files)}")
        for f in model_files:
            print(f"  - {f.name}")

        # Leer __init__.py para ver qué archivos se usan
        init_file = module_dir / "__init__.py"
        if init_file.exists():
            init_content = init_file.read_text(encoding='utf-8')
            print(f"Contenido de __init__.py:")
            print(init_content)

        # Eliminar archivos con patrones específicos
        for pattern in patterns_to_remove:
            files_to_remove = list(module_dir.glob(pattern))
            for file_to_remove in files_to_remove:
                if file_to_remove.is_file():
                    print(f"  ELIMINANDO: {file_to_remove.name}")
                    file_to_remove.unlink()
                    duplicates_removed += 1

    print(f"\n✅ Limpieza completada. {duplicates_removed} archivos eliminados.")

if __name__ == "__main__":
    cleanup_project()
