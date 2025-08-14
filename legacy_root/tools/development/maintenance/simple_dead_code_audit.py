#!/usr/bin/env python3
"""
Auditoría Simplificada de Código Muerto - Rexus.app

Identifica clases y utilidades específicas del checklist:
- BackupIntegration
- InventoryIntegration
- SmartTooltip
- Otros helpers no utilizados
"""

import os
import sys
import re
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

def find_references(item_name, root_path):
    """Encuentra todas las referencias a un item específico."""
    references = {
        'imports': [],
        'definitions': [],
        'usages': [],
        'total_files': 0
    }

    # Patrones de búsqueda
    import_patterns = [
        rf'from\s+\S+\s+import\s+.*{item_name}',
        rf'import\s+.*{item_name}',
    ]

    definition_patterns = [
        rf'class\s+{item_name}\b',
        rf'def\s+{item_name}\b',
    ]

    usage_patterns = [
        rf'{item_name}\s*\(',
        rf'\.{item_name}\b',
        rf'isinstance\([^,]+,\s*{item_name}\)',
    ]

    # Buscar en todos los archivos Python
    for py_file in root_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            file_has_reference = False
            relative_path = str(py_file.relative_to(root_path))

            # Buscar imports
            for pattern in import_patterns:
                if re.search(pattern, content):
                    references['imports'].append(relative_path)
                    file_has_reference = True
                    break

            # Buscar definiciones
            for pattern in definition_patterns:
                if re.search(pattern, content):
                    references['definitions'].append(relative_path)
                    file_has_reference = True
                    break

            # Buscar usos (excluyendo imports y definiciones)
            for pattern in usage_patterns:
                if re.search(pattern, content):
                    # Verificar que no sea solo un import o definición
                    lines_with_usage = [line.strip() for line in content.split('\n')
                                      if re.search(pattern, line) and
                                      not line.strip().startswith('import') and
                                      not line.strip().startswith('from') and
                                      not line.strip().startswith('class') and
                                      not line.strip().startswith('def')]

                    if lines_with_usage:
                        references['usages'].append(relative_path)
                        file_has_reference = True
                        break

            if file_has_reference:
                references['total_files'] += 1

        except Exception as e:
            print(f"Error procesando {py_file}: {e}")

    return references

def main():
    """Función principal."""
    print("AUDITORIA SIMPLIFICADA DE CODIGO MUERTO")
    print("=" * 50)

    # Items específicos a auditar
    target_items = [
        "BackupIntegration",
        "InventoryIntegration",
        "SmartTooltip",
        "DatabaseBackupManager",
        "AutomatedBackupScheduler",
        "AdvancedValidator",
        "XSSProtection",
        "StandardComponents",
        "ModuleFactory"
    ]

    results = {}

    for item in target_items:
        print(f"\nAnalizando: {item}")
        print("-" * 30)

        refs = find_references(item, root_dir)
        results[item] = refs

        total_refs = len(refs['imports']) + len(refs['usages'])

        if total_refs == 0:
            print(f"Estado: NO UTILIZADO")
        elif total_refs <= 2:
            print(f"Estado: POCO UTILIZADO ({total_refs} referencias)")
        else:
            print(f"Estado: UTILIZADO ({total_refs} referencias)")

        if refs['definitions']:
            print(f"Definido en: {', '.join(refs['definitions'])}")
        if refs['imports']:
            print(f"Importado en: {', '.join(refs['imports'])}")
        if refs['usages']:
            print(f"Usado en: {', '.join(refs['usages'])}")

    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN Y RECOMENDACIONES")
    print("=" * 50)

    dead_items = []
    low_usage_items = []
    active_items = []

    for item, refs in results.items():
        total_refs = len(refs['imports']) + len(refs['usages'])

        if total_refs == 0:
            dead_items.append(item)
        elif total_refs <= 2:
            low_usage_items.append(item)
        else:
            active_items.append(item)

    print(f"\nItems completamente muertos: {len(dead_items)}")
    if dead_items:
        for item in dead_items:
            print(f"  - {item}")
            if results[item]['definitions']:
                print(f"    Archivo a eliminar: {results[item]['definitions'][0]}")

    print(f"\nItems con poco uso: {len(low_usage_items)}")
    if low_usage_items:
        for item in low_usage_items:
            total_refs = len(results[item]['imports']) + len(results[item]['usages'])
            print(f"  - {item} ({total_refs} referencias)")

    print(f"\nItems activos: {len(active_items)}")
    if active_items:
        for item in active_items:
            total_refs = len(results[item]['imports']) + len(results[item]['usages'])
            print(f"  - {item} ({total_refs} referencias)")

    # Código de salida
    if dead_items:
        print(f"\nACCION REQUERIDA: {len(dead_items)} items pueden eliminarse")
        return 1
    else:
        print(f"\nCODIGO LIMPIO: No se encontraron items completamente muertos")
        return 0

if __name__ == "__main__":
    sys.exit(main())
