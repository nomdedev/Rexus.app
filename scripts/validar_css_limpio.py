#!/usr/bin/env python3
"""
Script para validar que no haya propiedades CSS no soportadas
"""

import os
import sys
import re

def validar_css_limpio():
    """Valida que los archivos QSS no tengan propiedades no soportadas."""

    # Propiedades CSS no soportadas por Qt (excluyendo subcontrol-position que sí es válido)
    propiedades_invalidas = [
        r'\bdisplay\s*:\s*(?!none\s*;?\s*/\*)',  # display: excepto comentarios
        r'\bbox-shadow\s*:\s*(?![^;]*/\*)',      # box-shadow excepto comentarios
        r'\brow-height\s*:',                     # row-height
        r'\btext-shadow\s*:',                    # text-shadow
        r'\bbox-sizing\s*:',                     # box-sizing
        r'\bfloat\s*:',                          # float
        r'\bclear\s*:',                          # clear
        r'\bz-index\s*:',                        # z-index
        r'\boverflow\s*:',                       # overflow
        r'\bcursor\s*:',                         # cursor
        r'\bposition\s*:\s*(?!subcontrol)',      # position: excepto subcontrol-position
    ]

    archivos_problematicos = []
    total_errores = 0

    # Buscar en archivos QSS
    qss_dirs = ['ui/resources/qss', 'resources/qss']

    for qss_dir in qss_dirs:
        if not os.path.exists(qss_dir):
            continue

        for archivo in os.listdir(qss_dir):
            if not archivo.endswith('.qss'):
                continue

            ruta_archivo = os.path.join(qss_dir, archivo)

            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                errores_archivo = []

                for i, linea in enumerate(contenido.split('\n'), 1):
                    for patron in propiedades_invalidas:
                        if re.search(patron, linea, re.IGNORECASE):
                            errores_archivo.append(f"Línea {i}: {linea.strip()}")
                            total_errores += 1

                if errores_archivo:
                    archivos_problematicos.append({
                        'archivo': archivo,
                        'ruta': ruta_archivo,
                        'errores': errores_archivo
                    })

            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")

    # Mostrar resultados
    if archivos_problematicos:
        print("❌ ARCHIVOS CON PROPIEDADES CSS NO SOPORTADAS:")
        print("=" * 60)

        for item in archivos_problematicos:
            print(f"\n📄 {item['archivo']}:")
            for error in item['errores']:
                print(f"   {error}")

        print(f"\n💥 Total de errores encontrados: {total_errores}")
        return False

    else:
        print("✅ VALIDACIÓN EXITOSA: No se encontraron propiedades CSS no soportadas")
        print("✅ Todos los archivos QSS están limpios")
        return True

if __name__ == "__main__":
    exito = validar_css_limpio()
    sys.exit(0 if exito else 1)
