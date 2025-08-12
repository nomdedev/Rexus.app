#!/usr/bin/env python3
"""
Script para agregar MIT license headers a archivos principales de Rexus
=====================================================================
"""

import os
import shutil
from pathlib import Path


def create_mit_header():
    """Crea el header MIT estándar."""
    return '''"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

{descripcion_original}
"""'''


def get_files_to_process():
    """Lista los archivos principales que necesitan MIT headers."""
    return [
        "rexus/modules/obras/view.py",
        "rexus/modules/usuarios/view.py",
        "rexus/modules/administracion/view.py",
        "rexus/modules/herrajes/view.py",
        "rexus/modules/logistica/view.py",
        "rexus/modules/pedidos/view.py",
        "rexus/modules/compras/view.py",
        "rexus/modules/mantenimiento/view.py",
        "rexus/modules/auditoria/view.py",
        "rexus/modules/configuracion/view.py",
        "rexus/modules/vidrios/view.py",
    ]


def add_mit_header_to_file(file_path: str) -> bool:
    """Agrega MIT header a un archivo si no lo tiene."""
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"[WARNING] Archivo no encontrado: {file_path}")
            return False

        # Leer contenido actual
        with open(file_path_obj, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Verificar si ya tiene MIT header
        if "MIT License" in contenido:
            print(f"[OK] {file_path}: Ya tiene MIT header")
            return True

        # Crear backup
        backup_dir = Path("backups_mit")
        backup_dir.mkdir(exist_ok=True)
        backup_file = backup_dir / f"{file_path_obj.name}.backup_mit"
        shutil.copy2(file_path_obj, backup_file)

        # Buscar descripción original del módulo
        lines = contenido.split("\n")
        descripcion_original = ""

        # Buscar docstring existente
        in_docstring = False
        docstring_start = -1
        docstring_end = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') and not in_docstring:
                docstring_start = i
                in_docstring = True
                if stripped.count('"""') == 2:  # Docstring de una línea
                    docstring_end = i
                    break
            elif stripped.endswith('"""') and in_docstring:
                docstring_end = i
                break

        # Extraer descripción original si existe
        if docstring_start >= 0 and docstring_end >= 0:
            descripcion_lines = lines[docstring_start : docstring_end + 1]
            descripcion_original = "\n".join(descripcion_lines)
        else:
            # Crear descripción básica
            module_name = file_path_obj.stem.replace("_", " ").title()
            descripcion_original = f'"""\n{module_name} - Módulo de {file_path_obj.parent.name.title()}\n"""'

        # Crear nuevo header MIT
        mit_header = create_mit_header().format(
            descripcion_original=descripcion_original
        )

        # Remover docstring original si existía
        if docstring_start >= 0 and docstring_end >= 0:
            lines = lines[:docstring_start] + lines[docstring_end + 1 :]

        # Insertar MIT header al inicio
        lines.insert(0, mit_header)

        # Guardar archivo modificado
        nuevo_contenido = "\n".join(lines)
        with open(file_path_obj, "w", encoding="utf-8") as f:
            f.write(nuevo_contenido)

        print(f"[OK] {file_path}: MIT header agregado")
        return True

    except Exception as e:
        print(f"[ERROR] Error procesando {file_path}: {e}")
        return False


def main():
    """Función principal."""
    print("AGREGANDO MIT LICENSE HEADERS")
    print("=" * 50)

    files_to_process = get_files_to_process()
    files_processed = 0
    files_updated = 0

    for file_path in files_to_process:
        print(f"Procesando: {file_path}")
        files_processed += 1

        if add_mit_header_to_file(file_path):
            files_updated += 1

    print("\n" + "=" * 50)
    print(f"RESUMEN:")
    print(f"   Archivos procesados: {files_processed}")
    print(f"   Archivos actualizados: {files_updated}")
    print(f"   Backups creados en: backups_mit/")

    if files_updated > 0:
        print(f"\n[EXITO] MIT HEADERS AGREGADOS EXITOSAMENTE")
        print(f"Archivos modificados: {files_updated}")
        print("\nPROXIMOS PASOS:")
        print("   1. Revisar los headers agregados")
        print("   2. Hacer commit de los cambios")
        print("   3. Continuar con tests y validación")
    else:
        print(f"\n[INFO] TODOS LOS ARCHIVOS YA TIENEN MIT HEADERS")


if __name__ == "__main__":
    main()
