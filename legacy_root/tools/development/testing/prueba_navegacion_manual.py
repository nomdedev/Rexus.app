#!/usr/bin/env python3
"""
Script simple para probar la navegación por módulos y detectar errores.
"""

def probar_navegacion_manual():
    """Guía para pruebas manuales de navegación"""

    print("🔍 GUÍA DE PRUEBAS DE NAVEGACIÓN MANUAL")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    modulos = [
        "Inventario",
        "Obras",
        "Pedidos/Compras",
        "Vidrios",
        "Herrajes",
        "Logística",
        "Mantenimiento",
        "Contabilidad",
        "Auditoría",
        "Usuarios",
        "Configuración"
    ]

    print("📋 MÓDULOS A PROBAR:")
    for i, modulo in enumerate(modulos, 1):
        print(f"  {i:2d}. {modulo}")

    print("\n" + "="*60)
    print("🎯 INSTRUCCIONES DE PRUEBA:")
    print("="*60)
    print("1. Navegue a cada módulo desde el sidebar")
    print("2. Intente abrir formularios/vistas principales")
    print("3. Pruebe funcionalidades básicas (buscar, filtrar, etc.)")
    print("4. Observe la consola y logs por errores")
    print("5. Anote cualquier comportamiento anómalo")

    print("\n🔧 ACCIONES ESPECÍFICAS A PROBAR:")
    print("-" * 40)
    print("• Inventario: Ver lista, buscar productos, abrir detalles")
    print("• Obras: Crear nueva obra, ver listado")
    print("• Vidrios: Consultar catálogo, aplicar filtros")
    print("• Herrajes: Explorar categorías")
    print("• Configuración: Abrir diferentes secciones")
    print("• Usuarios: Ver listado (si tiene permisos)")
    print("• Auditoría: Consultar logs de actividad")

    print("\n[WARN] ERRORES COMUNES A DETECTAR:")
    print("-" * 35)
    print("• Errores de importación/módulos no encontrados")
    print("• Errores de conexión a base de datos")
    print("• Problemas con iconos o estilos QSS")
    print("• Excepciones no manejadas")
    print("• Warnings de Qt/PyQt6")

    input("\n⏯️ Presione Enter cuando termine las pruebas para generar reporte...")

    return generar_reporte_manual()

def generar_reporte_manual():
    """Genera un reporte basado en los logs actuales"""

    print("\n[CHART] GENERANDO REPORTE DE NAVEGACIÓN...")

    # Leer logs recientes
    log_files = ['logs/app.log', 'logs/app_json.log']
    errores_encontrados = []
    warnings_encontrados = []

    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file,
'r',
                    encoding='utf-8',
                    errors='ignore') as f:
                    lines = f.readlines()

                    # Analizar últimas 100 líneas
                    recent_lines = lines[-100:] if len(lines) > 100 else lines

                    for line in recent_lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Detectar errores
                        if any(keyword in line.lower() for keyword in [
                            'error', 'exception', 'traceback', 'failed', 'critical'
                        ]):
                            errores_encontrados.append({
                                'archivo': log_file,
                                'linea': line
                            })

                        # Detectar warnings
                        elif any(keyword in line.lower() for keyword in [
                            'warning', 'qpixmap', 'stylesheet', 'deprecated'
                        ]):
                            warnings_encontrados.append({
                                'archivo': log_file,
                                'linea': line
                            })

            except Exception as e:
                print(f"[WARN] Error al leer {log_file}: {e}")

    # Mostrar reporte
    print("\n" + "="*60)
    print("📋 REPORTE DE NAVEGACIÓN MANUAL")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[ERROR] Errores detectados: {len(errores_encontrados)}")
    print(f"[WARN] Warnings detectados: {len(warnings_encontrados)}")

    if errores_encontrados:
        print("\n🚨 ERRORES ENCONTRADOS:")
        for i, error in enumerate(errores_encontrados[:10], 1):
            print(f"  {i}. [{error['archivo']}]")
            print(f"     {error['linea'][:80]}...")

    if warnings_encontrados:
        print("\n[WARN] WARNINGS ENCONTRADOS:")
        for i, warning in enumerate(warnings_encontrados[:5], 1):
            print(f"  {i}. [{warning['archivo']}]")
            print(f"     {warning['linea'][:80]}...")

    if not errores_encontrados and not warnings_encontrados:
        print("\n🎉 ¡No se detectaron errores ni warnings en logs recientes!")
        print("[CHECK] La navegación parece estar funcionando correctamente.")

    # Guardar reporte
    try:
        os.makedirs('tests/reports', exist_ok=True)

        reporte = {
            'fecha': datetime.now().isoformat(),
            'tipo': 'navegacion_manual',
            'errores': len(errores_encontrados),
            'warnings': len(warnings_encontrados),
            'errores_detalle': errores_encontrados[:20],  # Máximo 20
            'warnings_detalle': warnings_encontrados[:10]  # Máximo 10
        }

        with open('tests/reports/navegacion_manual.json', 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Reporte guardado en: tests/reports/navegacion_manual.json")
import json
import os
import subprocess
from datetime import datetime

    except Exception as e:
        print(f"[WARN] Error al guardar reporte: {e}")

    return len(errores_encontrados) == 0

def verificar_aplicacion_corriendo():
    """Verifica si la aplicación está ejecutándose"""
    try:
        # Verificar si hay procesos python con main.py
        result = subprocess.run([
            'powershell',
            '-Command',
            "Get-Process python* | Where-Object {$_.CommandLine -like '*main.py*'} | Measure-Object | Select-Object -ExpandProperty Count"
        ], capture_output=True, text=True)

        if result.returncode == 0 and result.stdout.strip().isdigit():
            return int(result.stdout.strip()) > 0
    except:
        pass

    # Verificar si existe el proceso de otra manera
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                              capture_output=True, text=True)
        return 'python.exe' in result.stdout
    except:
        pass

    return False

def main():
    """Función principal"""
    print("[ROCKET] PROBADOR DE NAVEGACIÓN POR MÓDULOS")
    print("="*50)

    # Verificar si la aplicación está corriendo
    if verificar_aplicacion_corriendo():
        print("[CHECK] Aplicación detectada ejecutándose")
    else:
        print("[WARN] No se detectó la aplicación ejecutándose")
        print("💡 Asegúrese de que main.py esté ejecutándose")

        respuesta = input("¿Continuar con las pruebas? (s/n): ").lower()
        if respuesta not in ['s', 'si', 'y', 'yes']:
            return

    # Verificar logs
    if not os.path.exists('logs'):
        print("[ERROR] Directorio 'logs' no encontrado")
        return

    print("\n📁 Archivos de log disponibles:")
    for log_file in ['app.log', 'app_json.log', 'audit.log']:
        path = f'logs/{log_file}'
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  [CHECK] {log_file} ({size} bytes)")
        else:
            print(f"  [ERROR] {log_file} (no encontrado)")

    print("\n" + "="*50)
    resultado = probar_navegacion_manual()

    if resultado:
        print("\n🎉 ¡Pruebas completadas exitosamente!")
    else:
        print("\n[WARN] Se detectaron algunos problemas durante las pruebas")
        print("Revise el reporte detallado para más información")

if __name__ == '__main__':
    main()
