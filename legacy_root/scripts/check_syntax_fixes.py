#!/usr/bin/env python3
"""
Script de verificación rápida de errores de sintaxis críticos
"""

import ast
import os
from pathlib import Path

def check_syntax_errors():
    """Verifica errores de sintaxis en archivos Python del proyecto."""
    root_path = Path(".")
    syntax_errors = []

    # Lista de archivos que sabemos que tienen errores críticos
    critical_files = [
        "rexus/modules/administracion/view_integrated.py",
        "rexus/modules/compras/dialogs/dialog_proveedor.py",
        "rexus/modules/compras/dialogs/dialog_seguimiento.py",
        "rexus/modules/herrajes/view_simple.py",
        "rexus/modules/inventario/dialogs/missing_dialogs.py",
        "rexus/modules/inventario/dialogs/modern_product_dialog.py",
        "rexus/modules/obras/dialogs/modern_obra_dialog.py",
        "rexus/modules/usuarios/submodules/auth_manager.py",
        "rexus/modules/usuarios/submodules/permissions_manager.py",
        "rexus/modules/usuarios/submodules/profiles_manager.py"
    ]

    print("🔍 Verificando corrección de errores de sintaxis críticos...")

    for file_path in critical_files:
        py_file = root_path / file_path
        if not py_file.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {file_path}")
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"❌ {file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: Error inesperado - {e}")
            print(f"❌ {file_path}: Error inesperado - {e}")

    print(f"\n📊 RESULTADO:")
    if syntax_errors:
        print(f"❌ {len(syntax_errors)} archivos con errores de sintaxis")
        for error in syntax_errors:
            print(f"  • {error}")
    else:
        print(f"✅ Todos los archivos críticos tienen sintaxis correcta")

    return syntax_errors

if __name__ == "__main__":
    check_syntax_errors()
