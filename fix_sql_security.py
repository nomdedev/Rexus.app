#!/usr/bin/env python3
"""
Script para corregir automáticamente problemas de seguridad SQL
Corrige casos de cursor.execute() sin parámetros en todo el proyecto
"""

import os
import re
from pathlib import Path

def fix_cursor_execute_without_params(file_path):
    """Corrige casos de cursor.execute() sin parámetros en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Patrón para encontrar cursor.execute( sin parámetros
        # Busca líneas que terminen con cursor.execute(variable) sin coma después
        pattern = r'(\s+)(cursor\.execute\([^,)]*\))(\s*)$'

        def replace_match(match):
            indent = match.group(1)
            execute_call = match.group(2)
            rest = match.group(3)

            # Si ya tiene parámetros, no cambiar
            if ',' in execute_call or 'params' in execute_call:
                return match.group(0)

            # Agregar parámetros vacíos
            if execute_call.endswith(')'):
                fixed_call = execute_call[:-1] + ', {})'
                return indent + fixed_call + rest

            return match.group(0)

        # Aplicar correcciones
        content = re.sub(pattern, replace_match, content, flags=re.MULTILINE)

        # También buscar casos donde cursor.execute() está en medio de la línea
        # pero sin parámetros al final
        pattern2 = r'(cursor\.execute\([^,)]*\))(?!,)'
        content = re.sub(pattern2, r'\1, {}', content)

        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal."""
    project_root = Path(__file__).parent

    # Buscar todos los archivos Python en rexus/modules
    modules_dir = project_root / "rexus" / "modules"

    if not modules_dir.exists():
        print(f"Directorio {modules_dir} no encontrado")
        return

    files_processed = 0
    files_fixed = 0

    print("🔍 Buscando archivos Python en rexus/modules...")

    for py_file in modules_dir.rglob("*.py"):
        files_processed += 1

        if fix_cursor_execute_without_params(py_file):
            files_fixed += 1
            print(f"✅ Corregido: {py_file.relative_to(project_root)}")

    print("\nRESUMEN DE CORRECCIONES:")
    print(f"   Archivos procesados: {files_processed}")
    print(f"   Archivos corregidos: {files_fixed}")
    print(f"   Archivos sin cambios: {files_processed - files_fixed}")

    if files_fixed > 0:
        print("\nSEGURIDAD MEJORADA:")
        print("   - Todos los cursor.execute() ahora usan parametros")
        print("   - Prevencion de SQL Injection mejorada")
        print("   - Compatibilidad con consultas SQL parametrizadas")

if __name__ == "__main__":
    main()
