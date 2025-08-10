#!/usr/bin/env python3
"""
Script para corregir decoradores incorrectos
"""

import os
import re


def fix_decorators():
    """Corrige todos los decoradores @auth_required(permission=...) incorrectos"""

    # Lista de archivos a corregir basada en la búsqueda anterior
    files_to_fix = [
        r"rexus\modules\obras\controller.py",
        r"rexus\modules\usuarios\controller.py",
        r"rexus\modules\inventario\controller.py",
        r"rexus\modules\logistica\controller.py",
        r"rexus\modules\compras\controller.py",
    ]

    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"[ERROR] Archivo no encontrado: {file_path}")
            continue

        print(f"🔧 Corrigiendo decoradores en: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Patrones de reemplazo
            replacements = [
                # CREATE -> auth_required
                (r"@auth_required\(permission=['\"]CREATE['\"])", "@auth_required"),
                # UPDATE -> auth_required
                (r"@auth_required\(permission=['\"]UPDATE['\"])", "@auth_required"),
                # DELETE -> admin_required (más restrictivo)
                (r"@auth_required\(permission=['\"]DELETE['\"])", "@admin_required"),
                # MANAGE -> admin_required (más restrictivo)
                (r"@auth_required\(permission=['\"]MANAGE['\"])", "@admin_required"),
                # EXPORT -> auth_required
                (r"@auth_required\(permission=['\"]EXPORT['\"])", "@auth_required"),
                # VIEW -> auth_required
                (r"@auth_required\(permission=['\"]VIEW['\"])", "@auth_required"),
            ]

            original_content = content

            for pattern, replacement in replacements:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    print(f"  [CHECK] Reemplazado {len(matches)} ocurrencias de {pattern}")

            # Solo escribir si hay cambios
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  [CHECK] Archivo actualizado")
            else:
                print(f"  ℹ️  Sin cambios necesarios")

        except Exception as e:
            print(f"  [ERROR] Error procesando {file_path}: {e}")


if __name__ == "__main__":
    print("🔧 CORRIGIENDO DECORADORES INCORRECTOS")
    print("=" * 50)
    fix_decorators()
    print("[CHECK] CORRECCIÓN COMPLETADA")
