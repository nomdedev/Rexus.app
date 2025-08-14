#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los f-strings mal terminados
y otros errores de sintaxis comunes en el proyecto Rexus.
"""

import glob
import os
import re


def corregir_f_strings_archivo(filepath):
    """Corrige los f-strings mal terminados en un archivo específico."""
    print(f"Revisando f-strings en {filepath}...")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_original = contenido

        # Patrones comunes de f-strings mal terminados
        correcciones = [
            # f"texto... (sin comillas de cierre)
            (r'f"([^"]*)\n([^"]*)"', r'f"\1 \2"'),
            # f'texto... (sin comillas de cierre)
            (r"f'([^']*)\n([^']*)'", r"f'\1 \2'"),
            # Casos específicos encontrados
            (r'f"([^"]*)\.\n\n"', r'f"\1. "'),
            (r'f"([^"]*)\n"', r'f"\1 "'),
            # Strings normales mal terminados
            (r'"([^"]*)\n\n"', r'"\1 "'),
            (r"'([^']*)\n\n'", r"'\1 '"),
        ]

        # Aplicar correcciones
        for patron, reemplazo in correcciones:
            contenido = re.sub(patron,
reemplazo,
                contenido,
                flags=re.MULTILINE)

        # Corregir imports mal estructurados
        contenido = corregir_imports_mal_estructurados(contenido)

        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(contenido)
            print(f"[CHECK] Corregido: {filepath}")
            return True
        else:
            print(f"⏭️ Sin cambios: {filepath}")
            return False

    except Exception as e:
        print(f"[ERROR] Error procesando {filepath}: {e}")
        return False


def corregir_imports_mal_estructurados(contenido):
    """Corrige imports mal estructurados tipo 'from PyQt6.QtWidgets import (\nfrom rexus...'"""

    # Buscar y corregir imports mal estructurados
    patron_import_roto = r"from PyQt6\.QtWidgets import \(\nfrom rexus\."
    if re.search(patron_import_roto, contenido):
        # Necesita corrección manual específica
        print("[WARN] Encontrado import mal estructurado - requiere corrección manual")

    return contenido


def verificar_sintaxis_basica(filepath):
    """Verifica errores de sintaxis básicos sin compilar el archivo completo."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()

        errores = []

        # Verificar f-strings mal terminados
        if re.search(r'f"[^"]*\n[^"]*$', contenido, re.MULTILINE):
            errores.append("F-string mal terminado detectado")

        # Verificar strings mal terminados
        if re.search(r'"[^"]*\n\n"', contenido):
            errores.append("String mal terminado detectado")

        # Verificar triple quotes mal terminados
        if contenido.count('"""') % 2 != 0:
            errores.append("Triple quote mal terminado")

        return len(errores) == 0, errores

    except Exception as e:
        return False, [f"Error verificando sintaxis: {e}"]


def main():
    """Función principal."""
    print("🔧 Iniciando corrección de f-strings y sintaxis...")

    # Encontrar archivos con errores conocidos
    archivos_con_errores = [
        "rexus/modules/compras/view.py",
        "rexus/modules/herrajes/view.py",
        "rexus/modules/logistica/view.py",
        "rexus/modules/mantenimiento/view.py",
        "rexus/modules/obras/view.py",
        "rexus/utils/security_fixed.py",
    ]

    # También buscar todos los archivos view.py
    archivos_view = glob.glob("rexus/modules/*/view.py")

    todos_los_archivos = list(set(archivos_con_errores + archivos_view))
    todos_los_archivos = [f for f in todos_los_archivos if os.path.exists(f)]

    print(f"📁 Encontrados {len(todos_los_archivos)} archivos para revisar")

    archivos_corregidos = 0

    for archivo in todos_los_archivos:
        if corregir_f_strings_archivo(archivo):
            archivos_corregidos += 1

    print(f"✨ Corrección completada: {archivos_corregidos} archivos modificados")

    # Verificación rápida post-corrección
    print("\n🔍 Verificando resultados...")
    for archivo in todos_los_archivos:
        valido, errores = verificar_sintaxis_basica(archivo)
        if not valido:
            print(f"[WARN] {archivo} aún tiene problemas: {', '.join(errores)}")


if __name__ == "__main__":
    main()
