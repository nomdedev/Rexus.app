#!/usr/bin/env python3
"""
Script para validar y corregir archivos QSS (CSS de Qt).
"""

def validar_qss(ruta_archivo):
import re
from pathlib import Path

    """Valida la sintaxis de un archivo QSS."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        errores = []
        lineas = contenido.split('\n')

        # Verificar corchetes balanceados
        balance = 0
        for i, linea in enumerate(lineas, 1):
            for char in linea:
                if char == '{':
                    balance += 1
                elif char == '}':
                    balance -= 1
                    if balance < 0:
                        errores.append(f"Línea {i}: Corchete de cierre sin apertura")

        if balance > 0:
            errores.append(f"Faltan {balance} corchetes de cierre")
        elif balance < 0:
            errores.append(f"Sobran {abs(balance)} corchetes de cierre")

        # Verificar comentarios mal formados
        comentario_abierto = False
        for i, linea in enumerate(lineas, 1):
            if '/*' in linea and '*/' not in linea:
                comentario_abierto = True
            elif '*/' in linea and not comentario_abierto:
                errores.append(f"Línea {i}: Comentario cerrado sin apertura")
            elif '*/' in linea and comentario_abierto:
                comentario_abierto = False

        if comentario_abierto:
            errores.append("Comentario abierto sin cerrar")

        # Verificar declaraciones CSS básicas
        declaraciones = re.findall(r'([^{]*)\s*\{([^}]*)\}', contenido)
        for selector, propiedades in declaraciones:
            selector = selector.strip()
            if not selector:
                continue

            # Verificar propiedades
            props = [p.strip() for p in propiedades.split(';') if p.strip()]
            for prop in props:
                if ':' not in prop:
                    errores.append(f"Propiedad malformada: '{prop}' en selector '{selector}'")

        return errores
    except Exception as e:
        return [f"Error leyendo archivo: {e}"]

def corregir_qss_basico(ruta_archivo):
    """Aplica correcciones básicas a un archivo QSS."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        contenido_original = contenido

        # Eliminar líneas vacías excesivas
        contenido = re.sub(r'\n\s*\n\s*\n+', '\n\n', contenido)

        # Corregir espacios alrededor de corchetes
        contenido = re.sub(r'\s*{\s*', ' {\n    ', contenido)
        contenido = re.sub(r'\s*}\s*', '\n}\n', contenido)

        # Verificar si hubo cambios
        if contenido != contenido_original:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            return True

        return False
    except Exception as e:
        print(f"[ERROR] Error corrigiendo {ruta_archivo}: {e}")
        return False

def main():
    """Función principal."""
    print("[TOOL] Iniciando validación de archivos QSS...")

    base_path = Path(__file__).parent.parent.parent
    archivos_qss = list(base_path.glob("**/*.qss"))

    errores_encontrados = 0
    archivos_corregidos = 0

    for archivo in archivos_qss:
        print(f"\n[INFO] Validando: {archivo.relative_to(base_path)}")

        errores = validar_qss(archivo)
        if errores:
            errores_encontrados += 1
            print(f"[ERROR] Errores encontrados en {archivo.name}:")
            for error in errores:
                print(f"  - {error}")

            # Intentar corrección básica
            if corregir_qss_basico(archivo):
                print(f"[OK] Corrección básica aplicada")
                archivos_corregidos += 1
        else:
            print(f"[OK] Sin errores de sintaxis")

    print(f"\n[INFO] Validación completada:")
    print(f"  - Archivos procesados: {len(archivos_qss)}")
    print(f"  - Archivos con errores: {errores_encontrados}")
    print(f"  - Archivos corregidos: {archivos_corregidos}")

if __name__ == "__main__":
    main()
