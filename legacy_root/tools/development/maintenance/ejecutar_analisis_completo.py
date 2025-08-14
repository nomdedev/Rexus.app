"""
Script maestro para ejecutar análisis completo de módulos.
Este script ejecuta todos los análisis necesarios y genera los informes correspondientes.
"""

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

def ejecutar_comando(comando, descripcion):
    """
    Ejecuta un comando y maneja errores.

    Args:
        comando (list): Lista con el comando y argumentos
        descripcion (str): Descripción de lo que hace el comando

    Returns:
        bool: True si el comando se ejecutó exitosamente
    """
    print(f"\n[*] {descripcion}...")
    try:
        result = subprocess.run(comando,
capture_output=True,
            text=True,
            cwd=ROOT_DIR)
        if result.returncode == 0:
            print(f"  [CHECK] {descripcion} completado exitosamente")
            if result.stdout:
                print(f"  📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  [ERROR] Error en {descripcion}")
            if result.stderr:
                print(f"  🚨 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  [ERROR] Excepción en {descripcion}: {e}")
        return False

def crear_directorio_salida(directorio):
    """Crea el directorio de salida si no existe."""
    os.makedirs(directorio, exist_ok=True)
    print(f"  📁 Directorio de salida: {directorio}")

def mostrar_banner():
    """Muestra el banner inicial."""
    print("\n" + "=" * 80)
    print(" " * 25 + "ANÁLISIS COMPLETO DE MÓDULOS")
    print(" " * 32 + "Versión 1.0.0")
    print(" " * 24 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 80 + "\n")

    print("Este script ejecutará:")
    print("1. Análisis de estructura y funcionalidad de todos los módulos")
    print("2. Generación de informes individuales por módulo")
    print("3. Creación de índice general con estadísticas")
    print("4. Análisis de seguridad SQL (opcional)")
    print("5. Escaneo de vulnerabilidades (opcional)")

def mostrar_resumen_final(directorio_salida, exitos, total):
    """Muestra el resumen final de la ejecución."""
    print("\n" + "=" * 80)
    print(" " * 30 + "RESUMEN FINAL")
    print("=" * 80)

    print(f"\n[CHART] Análisis completado:")
    print(f"  • Procesos exitosos: {exitos}/{total}")
    print(f"  • Directorio de informes: {directorio_salida}")

    # Listar archivos generados
    if os.path.exists(directorio_salida):
        archivos = os.listdir(directorio_salida)
        html_files = [f for f in archivos if f.endswith('.html')]
        json_files = [f for f in archivos if f.endswith('.json')]

        print(f"\n📄 Archivos generados:")
        print(f"  • Informes HTML: {len(html_files)}")
        print(f"  • Datos JSON: {len(json_files)}")

        # Mostrar archivo principal
        indice_principal = os.path.join(directorio_salida, "00_indice_analisis_modulos.html")
        if os.path.exists(indice_principal):
            print(f"\n🎯 Archivo principal: {indice_principal}")
            print("  Abre este archivo para ver el resumen ejecutivo completo")

    print("\n" + "=" * 80)

def main():
    """Función principal del script maestro."""
    parser = argparse.ArgumentParser(description='Análisis completo de módulos del proyecto')
    parser.add_argument('--output', '-o', default='informes_modulos',
                        help='Directorio de salida para los informes')
    parser.add_argument('--skip-seguridad', action='store_true',
                        help='Omitir análisis de seguridad SQL')
    parser.add_argument('--skip-vulnerabilidades', action='store_true',
import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

                        help='Omitir escaneo de vulnerabilidades')
    parser.add_argument('--modulo', '-m',
                        help='Analizar solo un módulo específico')

    args = parser.parse_args()

    # Banner inicial
    mostrar_banner()

    # Crear directorio de salida
    directorio_salida = args.output
    crear_directorio_salida(directorio_salida)

    # Contadores para resumen
    total_procesos = 0
    procesos_exitosos = 0

    # 1. Análisis de módulos
    print("\n🔍 FASE 1: Análisis de Módulos")
    print("-" * 50)

    if args.modulo:
        # Analizar módulo específico
        comando = [
            'python', 'scripts/verificacion/analizador_modulos.py',
            '--modulo', args.modulo,
            '--output', directorio_salida
        ]
        descripcion = f"Analizando módulo {args.modulo}"
    else:
        # Analizar todos los módulos
        comando = [
            'python', 'scripts/verificacion/analizador_modulos.py',
            '--todos',
            '--output', directorio_salida
        ]
        descripcion = "Analizando todos los módulos"

    total_procesos += 1
    if ejecutar_comando(comando, descripcion):
        procesos_exitosos += 1

    # 2. Generar índice de módulos
    print("\n📋 FASE 2: Generación de Índice")
    print("-" * 50)

    comando = [
        'python', 'scripts/verificacion/generar_indice_modulos.py',
        '--dir', directorio_salida
    ]

    total_procesos += 1
    if ejecutar_comando(comando, "Generando índice de análisis de módulos"):
        procesos_exitosos += 1

    # 3. Análisis de seguridad SQL (opcional)
    if not args.skip_seguridad:
        print("\n🛡️ FASE 3: Análisis de Seguridad SQL")
        print("-" * 50)

        comando = [
            'python', 'scripts/verificacion/analizar_seguridad_sql_codigo.py',
            '--dir', '.',
            '--output', os.path.join(directorio_salida, 'seguridad_sql.html')
        ]

        total_procesos += 1
        if ejecutar_comando(comando, "Analizando seguridad SQL en código"):
            procesos_exitosos += 1
    else:
        print("\n⏭️ FASE 3: Análisis de Seguridad SQL (omitido)")

    # 4. Escaneo de vulnerabilidades (opcional)
    if not args.skip_vulnerabilidades:
        print("\n[LOCK] FASE 4: Escaneo de Vulnerabilidades")
        print("-" * 50)

        comando = [
            'python', 'scripts/verificacion/escanear_vulnerabilidades.py',
            '--output', os.path.join(directorio_salida, 'vulnerabilidades'),
            '--skip-bd'  # Omitir BD por defecto para evitar errores de conexión
        ]

        total_procesos += 1
        if ejecutar_comando(comando, "Ejecutando escaneo de vulnerabilidades"):
            procesos_exitosos += 1
    else:
        print("\n⏭️ FASE 4: Escaneo de Vulnerabilidades (omitido)")

    # 5. Generar reporte de tests existentes
    print("\n🧪 FASE 5: Análisis de Tests")
    print("-" * 50)

    # Ejecutar pytest con reporte de cobertura si está disponible
    comando = ['python', '-m', 'pytest', '--tb=short', '-v']

    total_procesos += 1
    if ejecutar_comando(comando, "Ejecutando tests existentes"):
        procesos_exitosos += 1
    else:
        print("  [WARN] No se pudieron ejecutar todos los tests (puede ser normal)")

    # Mostrar resumen final
    mostrar_resumen_final(directorio_salida, procesos_exitosos, total_procesos)

if __name__ == "__main__":
    main()
