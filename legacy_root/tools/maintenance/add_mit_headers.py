#!/usr/bin/env python3
"""
Script para agregar headers MIT a todos los archivos principales de módulos
según el checklist de mejoras de Rexus.app
"""

import os
from pathlib import Path

# Header MIT completo
MIT_HEADER = '''"""
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

'''

# Archivos que necesitan headers MIT según el checklist
FILES_TO_UPDATE = [
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


def has_mit_license(content):
    """Verifica si el archivo ya tiene una licencia MIT"""
    return "MIT License" in content and "Copyright" in content


def get_existing_docstring(content):
    """Extrae el docstring existente del archivo si existe"""
    lines = content.split("\n")

    # Buscar el inicio del docstring
    docstring_start = None
    docstring_end = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Saltar imports y comentarios
        if (
            stripped.startswith("#")
            or stripped.startswith("import")
            or stripped.startswith("from")
        ):
            continue

        # Encontrar inicio de docstring
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_start = i
            # Buscar el final
            quote_type = '"""' if stripped.startswith('"""') else "'''"

            # Si el docstring está en una sola línea
            if stripped.count(quote_type) >= 2:
                docstring_end = i
                break

            # Buscar el final en líneas siguientes
            for j in range(i + 1, len(lines)):
                if quote_type in lines[j]:
                    docstring_end = j
                    break
            break

    if docstring_start is not None and docstring_end is not None:
        return "\n".join(lines[docstring_start : docstring_end + 1])

    return None


def add_mit_header(file_path):
    """Agrega header MIT al archivo especificado"""

    if not os.path.exists(file_path):
        print(f"[WARN]  Archivo no encontrado: {file_path}")
        return False

    # Leer contenido actual
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar si ya tiene licencia MIT
    if has_mit_license(content):
        print(f"ℹ️  Ya tiene licencia MIT: {file_path}")
        return False

    lines = content.split("\n")

    # Encontrar donde insertar el header
    insert_position = 0

    # Saltar shebang si existe
    if lines and lines[0].startswith("#!"):
        insert_position = 1

    # Saltar encoding si existe
    for i in range(insert_position, min(insert_position + 3, len(lines))):
        if i < len(lines) and \
            ("coding:" in lines[i] or "encoding:" in lines[i]):
            insert_position = i + 1
            break

    # Extraer docstring existente si existe
    existing_docstring = get_existing_docstring(content)

    if existing_docstring:
        # Construir nuevo contenido con MIT header + docstring existente
        new_header = MIT_HEADER + existing_docstring + '"""'

        # Remover el docstring original
        lines_copy = lines[:]
        for i, line in enumerate(lines_copy):
            if existing_docstring.split("\n")[0].strip() in line:
                # Encontrar el final del docstring original
                quote_count = 0
                for j in range(i, len(lines_copy)):
                    if '"""' in lines_copy[j] or "'''" in lines_copy[j]:
                        quote_count += lines_copy[j].count('"""') + lines_copy[j].count(
                            "'''"
                        )
                        if quote_count >= 2:
                            # Remover desde i hasta j (inclusive)
                            del lines_copy[i : j + 1]
                            break
                break

        lines = lines_copy
    else:
        new_header = MIT_HEADER + '"""'

    # Insertar el nuevo header
    lines.insert(insert_position, new_header)

    # Crear backup
    backup_path = f"{file_path}.backup_mit"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Guardar archivo actualizado
    new_content = "\n".join(lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[CHECK] Header MIT agregado: {file_path}")
    print(f"📁 Backup creado: {backup_path}")

    return True


def main():
    """Función principal para agregar headers MIT"""
    print("🔧 AGREGANDO HEADERS MIT A MÓDULOS PRINCIPALES")
    print("=" * 60)

    project_root = Path(__file__).parent.parent.parent

    success_count = 0
    skipped_count = 0

    for file_path in FILES_TO_UPDATE:
        full_path = project_root / file_path

        if add_mit_header(str(full_path)):
            success_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print(f"[CHECK] HEADERS MIT AGREGADOS: {success_count}")
    print(f"ℹ️  ARCHIVOS OMITIDOS: {skipped_count}")
    print(f"[CHART] TOTAL PROCESADOS: {success_count + skipped_count}")

    if success_count > 0:
        print("\n🎉 CUMPLIMIENTO LEGAL MIT LICENSE MEJORADO")
        print("📋 CHECKLIST: MIT License Headers - COMPLETADO")

    return success_count > 0


if __name__ == "__main__":
    main()
