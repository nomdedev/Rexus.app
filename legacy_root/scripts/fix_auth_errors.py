#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los problemas de decoradores y sintaxis
en los módulos de Rexus.app
"""

import os
import re
import sys
from pathlib import Path


def fix_auth_imports_and_decorators():
    """Corrige los imports de auth y el uso incorrecto de decoradores"""

    # Directorio base de módulos
    modules_dir = Path("rexus/modules")

    # Archivos a procesar
    files_to_fix = []
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir():
            view_file = module_dir / "view.py"
            controller_file = module_dir / "controller.py"

            if view_file.exists():
                files_to_fix.append(view_file)
            if controller_file.exists():
                files_to_fix.append(controller_file)

    print(f"📋 Archivos a corregir: {len(files_to_fix)}")

    for file_path in files_to_fix:
        print(f"🔧 Corrigiendo: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 1. Corregir imports de auth
            if "from rexus.core.auth_manager import" not in content:
                # Buscar línea de imports PyQt6 para insertar después
                lines = content.split("\n")
                insert_index = 0

                for i, line in enumerate(lines):
                    if (
                        "from PyQt6" in line
                        or "from rexus.core" in line
                        or "import sys" in line
                    ):
                        insert_index = i + 1

                # Insertar import correcto
                auth_import = "from rexus.core.auth_manager import AuthManager, auth_required, admin_required, manager_required"
                lines.insert(insert_index, auth_import)
                content = "\n".join(lines)
                print(f"  [CHECK] Import de auth agregado")

            # 2. Corregir decoradores con argumentos incorrectos
            # @auth_required(permission='X') -> usar decorador específico
            patterns_to_fix = [
                (r"@auth_required\(permission=['\"]CREATE['\"])", "@auth_required"),
                (r"@auth_required\(permission=['\"]UPDATE['\"])", "@auth_required"),
                (r"@auth_required\(permission=['\"]DELETE['\"])", "@admin_required"),
                (r"@auth_required\(permission=['\"]MANAGE['\"])", "@admin_required"),
                (r"@auth_required\(permission=['\"]VIEW['\"])", "@auth_required"),
            ]

            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    print(f"  [CHECK] Decorador corregido: {pattern} -> {replacement}")

            # 3. Corregir errores de sintaxis comunes
            # Función sin def completo
            content = re.sub(
                r"@[a-zA-Z_]+\s*\n\s*def\s+([a-zA-Z_]+)\([^)]*:\s*#",
                r"@auth_required\n    def \1(self):\n        #",
                content,
            )

            # 4. Corregir f-strings no terminados
            # Buscar patrones como f" sin cierre
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if 'f"' in line or "f'" in line:
                    # Verificar si el f-string está cerrado
                    if line.count('"') % 2 == 1 or line.count("'") % 2 == 1:
                        # Intentar corregir
                        if line.endswith('f"') or line.endswith("f'"):
                            lines[i] = line + 'ERROR_STRING"'
                            print(f"  [WARN]  F-string corregido en línea {i + 1}")

            content = "\n".join(lines)

            # 5. Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  [CHECK] Archivo actualizado: {file_path}")
            else:
                print(f"  ℹ️  Sin cambios necesarios: {file_path}")

        except Exception as e:
            print(f"  [ERROR] Error procesando {file_path}: {e}")


def check_syntax_errors():
    """Verifica errores de sintaxis en archivos Python"""

    modules_dir = Path("rexus/modules")

    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir():
            for py_file in module_dir.glob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Intentar compilar
                    compile(content, str(py_file), "exec")
                    print(f"[CHECK] Sintaxis OK: {py_file}")

                except SyntaxError as e:
                    print(f"[ERROR] Error de sintaxis en {py_file}:{e.lineno}: {e.msg}")
                except Exception as e:
                    print(f"[WARN]  Error verificando {py_file}: {e}")


if __name__ == "__main__":
    print("🔧 INICIANDO CORRECCIÓN DE PROBLEMAS DE AUTENTICACIÓN Y SINTAXIS")
    print("=" * 70)

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent.parent)

    print("📋 Paso 1: Corrigiendo imports y decoradores...")
    fix_auth_imports_and_decorators()

    print("\n📋 Paso 2: Verificando sintaxis...")
    check_syntax_errors()

    print("\n[CHECK] CORRECCIÓN COMPLETADA")
