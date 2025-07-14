#!/usr/bin/env python3
"""
Script de validación de estilos QSS y widgets para detectar problemas comunes.
Detecta:
- setStyleSheet("") (vacíos que pueden causar warnings)
- Concatenación de estilos con + que puede fallar
- Selectores complejos inválidos en setStyleSheet directo
- Uso de QPixmap sin validación de archivo
- Reglas QSS incompatibles con PyQt6

Uso: python scripts/maintenance/validar_estilos_qss.py
"""

def buscar_problemas_estilos():
    """Busca problemas comunes en estilos y QSS."""
import re
import sys
from pathlib import Path

    problemas = []
    proyecto_root = Path(__file__).parent.parent.parent

    # Patrones problemáticos
    patrones = {
        'setStyleSheet_vacio': r'\.setStyleSheet\(["\'][\s]*["\']\)',
        'concatenacion_estilos': r'\.setStyleSheet\([^)]*\+[^)]*\)',
        'selector_complejo': r'\.setStyleSheet\(["\'][^"\']*::[^"\']*["\']\)',
        'pixmap_directo': r'QPixmap\([^)]*\)\.scaled\(',
        'qss_box_shadow': r'box-shadow\s*:',
    }

    # Buscar en archivos Python
    for archivo_py in proyecto_root.rglob("*.py"):
        if "tests" in str(archivo_py) or "__pycache__" in str(archivo_py):
            continue

        try:
            with open(archivo_py, 'r', encoding='utf-8') as f:
                contenido = f.read()

            for nombre_patron, patron in patrones.items():
                matches = re.finditer(patron, contenido, re.MULTILINE)
                for match in matches:
                    linea_num = contenido[:match.start()].count('\n') + 1
                    linea_texto = contenido.split('\n')[linea_num - 1].strip()
                    problemas.append({
                        'archivo': str(archivo_py.relative_to(proyecto_root)),
                        'linea': linea_num,
                        'problema': nombre_patron,
                        'texto': linea_texto[:100] + "..." if len(linea_texto) > 100 else linea_texto
                    })
        except Exception as e:
            print(f"Error leyendo {archivo_py}: {e}")

    # Buscar en archivos QSS
    for archivo_qss in proyecto_root.rglob("*.qss"):
        try:
            with open(archivo_qss, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Buscar reglas problemáticas en QSS
            if 'box-shadow' in contenido:
                problemas.append({
                    'archivo': str(archivo_qss.relative_to(proyecto_root)),
                    'linea': 'N/A',
                    'problema': 'box_shadow_en_qss',
                    'texto': 'box-shadow no soportado en Qt'
                })
        except Exception as e:
            print(f"Error leyendo {archivo_qss}: {e}")

    return problemas

def validar_recursos_iconos():
    """Valida que los recursos de iconos existan."""
    proyecto_root = Path(__file__).parent.parent.parent
    recursos_faltantes = []

    # Buscar referencias a recursos
    patron_recursos = r'["\'](resources/icons/[^"\']+)["\']'

    for archivo_py in proyecto_root.rglob("*.py"):
        if "tests" in str(archivo_py) or "__pycache__" in str(archivo_py):
            continue

        try:
            with open(archivo_py, 'r', encoding='utf-8') as f:
                contenido = f.read()

            matches = re.finditer(patron_recursos, contenido)
            for match in matches:
                ruta_recurso = match.group(1)
                ruta_completa = proyecto_root / ruta_recurso

                if not ruta_completa.exists():
                    linea_num = contenido[:match.start()].count('\n') + 1
                    recursos_faltantes.append({
                        'archivo': str(archivo_py.relative_to(proyecto_root)),
                        'linea': linea_num,
                        'recurso': ruta_recurso,
                        'ruta_completa': str(ruta_completa)
                    })
        except Exception as e:
            print(f"Error validando recursos en {archivo_py}: {e}")

    return recursos_faltantes

def main():
    """Ejecuta todas las validaciones y reporta resultados."""
    print("=== VALIDADOR DE ESTILOS QSS Y RECURSOS ===")
    print()

    # Validar problemas de estilos
    problemas = buscar_problemas_estilos()

    if problemas:
        print(f"❌ ENCONTRADOS {len(problemas)} PROBLEMAS DE ESTILOS:")
        print()

        for problema in problemas:
            print(f"📁 {problema['archivo']}:{problema['linea']}")
            print(f"🔍 Problema: {problema['problema']}")
            print(f"📝 Código: {problema['texto']}")
            print()
    else:
        print("✅ NO SE ENCONTRARON PROBLEMAS DE ESTILOS")
        print()

    # Validar recursos faltantes
    recursos_faltantes = validar_recursos_iconos()

    if recursos_faltantes:
        print(f"❌ ENCONTRADOS {len(recursos_faltantes)} RECURSOS FALTANTES:")
        print()

        for recurso in recursos_faltantes:
            print(f"📁 {recurso['archivo']}:{recurso['linea']}")
            print(f"🔍 Recurso faltante: {recurso['recurso']}")
            print(f"📝 Ruta esperada: {recurso['ruta_completa']}")
            print()
    else:
        print("✅ TODOS LOS RECURSOS DE ICONOS EXISTEN")
        print()

    # Resumen final
    total_problemas = len(problemas) + len(recursos_faltantes)

    if total_problemas == 0:
        print("🎉 VALIDACIÓN COMPLETADA SIN ERRORES")
        print("La aplicación no debería mostrar warnings de QSS o QPixmap.")
        return 0
    else:
        print(f"⚠️  VALIDACIÓN COMPLETADA CON {total_problemas} PROBLEMAS")
        print("Revisa y corrige los problemas reportados para eliminar warnings.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
