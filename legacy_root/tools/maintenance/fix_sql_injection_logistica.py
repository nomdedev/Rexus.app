#!/usr/bin/env python3
"""
Script para reparar automáticamente las vulnerabilidades SQL injection
en LogisticaModel reemplazando concatenaciones peligrosas
"""

import os
import re


def fix_sql_injections_logistica():
    """Repara automáticamente las SQL injections en LogisticaModel"""

    file_path = r"C:\Users\Oficina\Documents\Proyectos\Apps\Rexus.app\rexus\modules\logistica\model.py"

    if not os.path.exists(file_path):
        print(f"[ERROR] Archivo no encontrado: {file_path}")
        return

    # Leer el archivo
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Reparaciones específicas para LogisticaModel
    replacements = [
        # 1. Concatenaciones simples con cursor.execute
        (
            r'cursor\.execute\("SELECT COUNT\(\*\) FROM " \+ self\.tabla_transportes \+ " WHERE activo = 1"\)',
            r'cursor.execute(f"SELECT COUNT(*) FROM [{self._validate_table_name(self.tabla_transportes)}] WHERE activo = 1")',
        ),
        (
            r'cursor\.execute\("SELECT COUNT\(\*\) FROM " \+ self\.tabla_transportes \+ " WHERE activo = 1 AND disponible = 1"\)',
            r'cursor.execute(f"SELECT COUNT(*) FROM [{self._validate_table_name(self.tabla_transportes)}] WHERE activo = 1 AND disponible = 1")',
        ),
        # 2. Query DELETE simple
        (
            r'query = "DELETE FROM " \+ self\.tabla_detalle_entregas \+ " WHERE id = \?"',
            r'query = f"DELETE FROM [{self._validate_table_name(self.tabla_detalle_entregas)}] WHERE id = ?"',
        ),
        # 3. Queries con triple quote - INSERT INTO
        (
            r'INSERT INTO """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r"INSERT INTO [{self._validate_table_name(self.\1)}]",
        ),
        # 4. Queries con triple quote - UPDATE
        (
            r'UPDATE """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r"UPDATE [{self._validate_table_name(self.\1)}]",
        ),
        # 5. Queries con triple quote - FROM
        (
            r'FROM """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r"FROM [{self._validate_table_name(self.\1)}]",
        ),
        # 6. SELECT COUNT(*) FROM con triple quote
        (
            r'SELECT COUNT\(\*\) FROM """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r"SELECT COUNT(*) FROM [{self._validate_table_name(self.\1)}]",
        ),
        # 7. SELECT SUM con triple quote
        (
            r'SELECT SUM\([^)]+\) FROM """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r"SELECT SUM(costo_envio) FROM [{self._validate_table_name(self.\1)}]",
        ),
    ]

    # Aplicar reemplazos
    changes_made = 0
    for pattern, replacement in replacements:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        if content != old_content:
            matches = len(
                re.findall(pattern, old_content, flags=re.MULTILINE | re.DOTALL)
            )
            changes_made += matches
            print(f"[CHECK] Reemplazado {matches} ocurrencias de: {pattern[:50]}...")

    # Aplicar reparaciones adicionales para f-strings
    additional_fixes = [
        # Convertir todas las queries a f-strings para usar _validate_table_name
        (
            r'query = """\s*INSERT INTO """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r'query = f"""\n                INSERT INTO [{self._validate_table_name(self.\1)}]',
        ),
        (
            r'query = """\s*UPDATE """\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r'query = f"""\n                UPDATE [{self._validate_table_name(self.\1)}]',
        ),
        (
            r'query = """\s*([A-Z][A-Z\s]*)\s*"""\s*\+\s*self\.(tabla_\w+)\s*\+\s*"""',
            r'query = f"""\n                \1 [{self._validate_table_name(self.\2)}]',
        ),
    ]

    for pattern, replacement in additional_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        if content != old_content:
            matches = len(
                re.findall(pattern, old_content, flags=re.MULTILINE | re.DOTALL)
            )
            changes_made += matches
            print(f"[CHECK] Reparación adicional: {matches} ocurrencias")

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
    print("🔧 INICIANDO REPARACIÓN AUTOMÁTICA DE SQL INJECTIONS - LOGÍSTICA")
    print("=" * 70)

    success = fix_sql_injections_logistica()

    print("\n" + "=" * 70)
    if success:
        print("[CHECK] PROCESO COMPLETADO EXITOSAMENTE")
        print("[CHART] PROGRESO TOTAL: MantenimientoModel + LogisticaModel REPARADOS")
        print("🧪 RECOMENDADO: Ejecutar tests para validar funcionalidad")
    else:
        print("ℹ️ PROCESO COMPLETADO - Sin cambios necesarios")
