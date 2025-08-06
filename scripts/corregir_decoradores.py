#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los errores de decoradores @auth_required
en el proyecto Rexus.
"""

import glob
import os
import re


def corregir_decoradores_archivo(filepath):
    """Corrige los decoradores en un archivo específico."""
    print(f"Corrigiendo {filepath}...")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_original = contenido

        # Asegurar que tiene los imports correctos
        if "@auth_required" in contenido or "@admin_required" in contenido:
            # Verificar si ya tiene los imports
            if "from rexus.core.auth_manager import" not in contenido:
                # Buscar donde insertar los imports
                lines = contenido.split("\n")
                insert_pos = 0

                # Buscar después de los imports de PyQt6 y otros imports
                for i, line in enumerate(lines):
                    if (
                        line.startswith("from PyQt6")
                        or line.startswith("import logging")
                        or line.startswith("import os")
                        or line.startswith("from rexus.modules")
                    ):
                        insert_pos = i + 1

                # Insertar los imports necesarios
                import_line = "from rexus.core.auth_manager import auth_required, admin_required, manager_required"
                lines.insert(insert_pos, import_line)
                contenido = "\n".join(lines)

        # Patrones de corrección para decoradores
        correcciones = [
            # @auth_required(permission='CREATE') -> @auth_required
            (r"@auth_required\(permission=['\"]CREATE['\"]\)", "@auth_required"),
            (r"@auth_required\(permission=['\"]READ['\"]\)", "@auth_required"),
            (r"@auth_required\(permission=['\"]VIEW['\"]\)", "@auth_required"),
            # @auth_required(permission='UPDATE') -> @auth_required
            (r"@auth_required\(permission=['\"]UPDATE['\"]\)", "@auth_required"),
            (r"@auth_required\(permission=['\"]EDIT['\"]\)", "@auth_required"),
            # @auth_required(permission='DELETE') -> @admin_required
            (r"@auth_required\(permission=['\"]DELETE['\"]\)", "@admin_required"),
            # @auth_required(permission='MANAGE') -> @admin_required
            (r"@auth_required\(permission=['\"]MANAGE['\"]\)", "@admin_required"),
            (r"@auth_required\(permission=['\"]ADMIN['\"]\)", "@admin_required"),
            # @auth_required(permission='EXPORT') -> @manager_required
            (r"@auth_required\(permission=['\"]EXPORT['\"]\)", "@manager_required"),
            (r"@auth_required\(permission=['\"]REPORT['\"]\)", "@manager_required"),
        ]

        # Aplicar correcciones
        for patron, reemplazo in correcciones:
            contenido = re.sub(patron, reemplazo, contenido)

        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(contenido)
            print(f"✅ Corregido: {filepath}")
            return True
        else:
            print(f"⏭️ Sin cambios: {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False


def main():
    """Función principal."""
    print("🔧 Iniciando corrección automática de decoradores...")

    # Buscar todos los archivos Python en el proyecto
    archivos_python = []

    # Buscar en módulos específicos
    for patron in [
        "rexus/modules/*/controller.py",
        "rexus/modules/*/view.py",
        "rexus/modules/*/*.py",
    ]:
        archivos_python.extend(glob.glob(patron))

    # Filtrar archivos que existen
    archivos_python = [f for f in archivos_python if os.path.exists(f)]

    print(f"📁 Encontrados {len(archivos_python)} archivos para revisar")

    archivos_corregidos = 0

    for archivo in archivos_python:
        if corregir_decoradores_archivo(archivo):
            archivos_corregidos += 1

    print(f"✨ Corrección completada: {archivos_corregidos} archivos modificados")


if __name__ == "__main__":
    main()
