#!/usr/bin/env python3
"""
Script para reparar automáticamente las vulnerabilidades SQL injection
en MantenimientoModel reemplazando concatenaciones peligrosas
"""

import os
import re


def fix_sql_injections():
    """Repara automáticamente las SQL injections en MantenimientoModel"""

    file_path = r"C:\Users\Oficina\Documents\Proyectos\Apps\Rexus.app\rexus\modules\mantenimiento\model.py"

    if not os.path.exists(file_path):
        print(f"[ERROR] Archivo no encontrado: {file_path}")
        return

    # Leer el archivo
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Patrones de reemplazo para concatenaciones peligrosas
    replacements = [
        # INSERT INTO con concatenación
        (
            r'INSERT INTO """\s*\+\s*self\.tabla_mantenimientos\s*\+\s*"""',
            r"INSERT INTO [{self._validate_table_name(self.tabla_mantenimientos)}]",
        ),
        # UPDATE con concatenación
        (
            r'UPDATE """\s*\+\s*self\.tabla_mantenimientos\s*\+\s*"""',
            r"UPDATE [{self._validate_table_name(self.tabla_mantenimientos)}]",
        ),
        # FROM con concatenación en query multilinea
        (
            r'FROM """\s*\+\s*self\.tabla_mantenimientos\s*\+\s*"""',
            r"FROM [{self._validate_table_name(self.tabla_mantenimientos)}]",
        ),
        (
            r'FROM """\s*\+\s*self\.tabla_equipos\s*\+\s*"""',
            r"FROM [{self._validate_table_name(self.tabla_equipos)}]",
        ),
        # Query strings simples con concatenación triple
        (
            r'query = """\s*INSERT INTO """\s*\+\s*self\.tabla_mantenimientos\s*\+\s*"""',
            r'query = f"""\n                INSERT INTO [{self._validate_table_name(self.tabla_mantenimientos)}]',
        ),
        # Query strings con concatenación para cualquier tabla
        (
            r'"""\s*\+\s*self\.tabla_(\w+)\s*\+\s*"""',
            r"[{self._validate_table_name(self.tabla_\1)}]",
        ),
        # Queries que empiezan con query =
        (
            r'query = """\s*([A-Z]+)\s*([A-Z]*)\s*"""\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r'query = f"""\n                \1 \2 [{self._validate_table_name(self.\3)}]',
        ),
    ]

    # Aplicar reemplazos
    changes_made = 0
    for pattern, replacement in replacements:
        old_content = content
        content = re.sub(pattern,
replacement,
            content,
            flags=re.MULTILINE | re.DOTALL)
        if content != old_content:
            matches = len(
                re.findall(pattern, old_content, flags=re.MULTILINE | re.DOTALL)
            )
            changes_made += matches
            print(f"[CHECK] Reemplazado {matches} ocurrencias de: {pattern[:50]}...")

    # Guardar si hubo cambios
    if content != original_content:
        # Crear backup
        backup_path = f"{file_path}.backup_sql_fix"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        print(f"📁 Backup creado: {backup_path}")

        # Guardar archivo reparado
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(
            f"🎉 REPARACIÓN COMPLETADA: {changes_made} vulnerabilidades SQL corregidas"
        )
        print(f"📄 Archivo actualizado: {file_path}")

        return True
    else:
        print("ℹ️ No se encontraron patrones para reparar")
        return False


if __name__ == "__main__":
    print("🔧 INICIANDO REPARACIÓN AUTOMÁTICA DE SQL INJECTIONS")
    print("=" * 60)

    success = fix_sql_injections()

    print("\n" + "=" * 60)
    if success:
        print("[CHECK] PROCESO COMPLETADO EXITOSAMENTE")
        print("[WARN]  IMPORTANTE: Revisar manualmente las consultas complejas")
        print("🧪 RECOMENDADO: Ejecutar tests para validar funcionalidad")
    else:
        print("ℹ️ PROCESO COMPLETADO - Sin cambios necesarios")
