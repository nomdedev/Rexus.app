#!/usr/bin/env python3
"""
Script de verificación de seguridad completa
Ejecuta todos los tests de seguridad implementados en el proyecto
"""

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y reporta el resultado"""
    print(f"\n🔍 {descripcion}")
    print("=" * 60)
import json
import os
import subprocess
import sys
from datetime import datetime

    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode == 0:
            print(f"✅ {descripcion} - ÉXITO")
            # Extraer información de tests si está disponible
            if "passed" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "passed" in line and ("failed" in line or "error" in line):
                        print(f"📊 Resultado: {line.strip()}")
                        break
        else:
            print(f"❌ {descripcion} - FALLO")
            print(f"Error: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error ejecutando {descripcion}: {e}")
        return False

def main():
    print("🛡️ VERIFICACIÓN DE SEGURIDAD COMPLETA")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Verificar todos los tests de seguridad implementados")

    # Lista de verificaciones de seguridad
    tests_seguridad = [
        {
            "comando": "python -m pytest tests\\utils\\test_sql_utils.py -v",
            "descripcion": "Tests de Utilidades SQL"
        },
        {
            "comando": "python -m pytest tests\\utils\\test_validador_http.py -v",
            "descripcion": "Tests de Validación HTTP"
        },
        {
            "comando": "python -m pytest tests\\pedidos\\test_pedidos_security_simple.py -v",
            "descripcion": "Tests de Seguridad de Pedidos (Básicos)"
        },
        {
            "comando": "python -m pytest tests\\pedidos\\test_qr_security_advanced.py -v",
            "descripcion": "Tests de Seguridad QR (Avanzados)"
        },
        {
            "comando": "python -m pytest tests\\pedidos\\test_pedidos_view_security.py -v",
            "descripcion": "Tests de Seguridad Vista Pedidos"
        },
        {
            "comando": "python -m pytest tests\\inventario\\test_inventario_edge_cases.py -v",
            "descripcion": "Tests de Edge Cases Inventario"
        },
        {
            "comando": "python -m pytest tests\\test_schema_consistency.py -v",
            "descripcion": "Tests de Consistencia de Esquema BD"
        }
    ]

    # Contadores
    total_tests = len(tests_seguridad)
    exitosos = 0
    fallidos = 0

    # Ejecutar cada test de seguridad
    resultados = []

    for test in tests_seguridad:
        exito = ejecutar_comando(test["comando"], test["descripcion"])
        resultados.append({
            "test": test["descripcion"],
            "comando": test["comando"],
            "exito": exito,
            "timestamp": datetime.now().isoformat()
        })

        if exito:
            exitosos += 1
        else:
            fallidos += 1

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN DE SEGURIDAD")
    print("=" * 60)
    print(f"✅ Tests exitosos: {exitosos}/{total_tests}")
    print(f"❌ Tests fallidos: {fallidos}/{total_tests}")

    if fallidos == 0:
        print("🎉 ¡TODOS LOS TESTS DE SEGURIDAD PASARON!")
        print("🛡️ El sistema está completamente seguro y validado")
    else:
        print("⚠️ ALGUNOS TESTS DE SEGURIDAD FALLARON")
        print("🔧 Revisar y corregir los tests fallidos antes de continuar")

    # Guardar reporte
    reporte = {
        "fecha": datetime.now().isoformat(),
        "total_tests": total_tests,
        "exitosos": exitosos,
        "fallidos": fallidos,
        "porcentaje_exito": round((exitosos / total_tests) * 100, 2),
        "resultados": resultados
    }

    archivo_reporte = f"reporte_seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        print(f"📄 Reporte guardado en: {archivo_reporte}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {e}")

    # Test específico adicional: verificación de archivos críticos
    print("\n🔍 VERIFICACIÓN DE ARCHIVOS CRÍTICOS DE SEGURIDAD")
    print("=" * 60)

    archivos_criticos = [
        "utils/sql_seguro.py",
        "utils/sanitizador_sql.py",
        "utils/validador_http.py",
        "modules/pedidos/view.py",
        "tests/pedidos/test_pedidos_security_simple.py",
        "tests/pedidos/test_qr_security_advanced.py",
        "tests/utils/test_sql_utils.py",
        "tests/utils/test_validador_http.py"
    ]

    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - Presente")
        else:
            print(f"❌ {archivo} - FALTANTE")
            fallidos += 1

    # Código de salida
    sys.exit(0 if fallidos == 0 else 1)

if __name__ == "__main__":
    main()
