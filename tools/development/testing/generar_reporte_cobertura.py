#!/usr/bin/env python3
"""
Script para generar reporte de cobertura completo
Ejecuta pytest con análisis de cobertura detallado
"""

def main():
    # Crear directorio de reportes si no existe
    os.makedirs("tests/reports", exist_ok=True)

    print("🔍 GENERANDO REPORTE DE COBERTURA COMPLETO")
    print("=" * 60)
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

    # Directorio del proyecto
    project_dir = Path(__file__).parent.parent.parent
    os.chdir(project_dir)

    print(f"📁 Directorio de trabajo: {project_dir}")

    # Comando para pytest con cobertura
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=modules",
        "--cov=core",
        "--cov=utils",
        "--cov-report=html:coverage_html",
        "--cov-report=term-missing",
        "--cov-report=json:coverage.json",
        "-v",
        "--tb=short"
    ]

    print(f"[ROCKET] Ejecutando: {' '.join(cmd)}")
    print("-" * 60)

    start_time = time.time()

    try:
        # Ejecutar pytest
        result = subprocess.run(cmd, capture_output=True, text=True)

        execution_time = time.time() - start_time

        print("[CHART] RESULTADO DE EJECUCIÓN:")
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"🔄 Código de salida: {result.returncode}")
        print()

        # Mostrar salida estándar
        if result.stdout:
            print("📄 SALIDA ESTÁNDAR:")
            print(result.stdout)
            print()

        # Mostrar errores si los hay
        if result.stderr:
            print("[WARN]  ERRORES/ADVERTENCIAS:")
            print(result.stderr)
            print()

        # Generar reporte adicional
        generar_reporte_adicional(result.returncode == 0, execution_time)

        # Intentar leer reporte JSON si existe
        leer_reporte_json()

    except Exception as e:
        print(f"[ERROR] Error al ejecutar pytest: {e}")
        return False

    return result.returncode == 0

def generar_reporte_adicional(success, execution_time):
    """Genera reporte adicional con estadísticas"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = f"""# [CHART] REPORTE DE COBERTURA - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## [CHECK] Estado de Ejecución
- **Exitoso**: {'[CHECK] SÍ' if success else '[ERROR] NO'}
- **Tiempo de ejecución**: {execution_time:.2f} segundos
- **Timestamp**: {timestamp}

## 📁 Archivos Generados
- `coverage_html/`: Reporte HTML detallado
- `coverage.json`: Datos de cobertura en JSON
- `.coverage`: Archivo de datos de cobertura

## 🔍 Próximos Pasos
1. Revisar reporte HTML en `coverage_html/index.html`
2. Analizar módulos con baja cobertura
3. Implementar tests adicionales si es necesario
4. Configurar CI/CD para ejecución automática

---
*Generado automáticamente por generar_reporte_cobertura.py*
"""

    with open(f"tests/reports/REPORTE_TESTS.md", "w", encoding="utf-8") as f:
        f.write(reporte)

    print(f"📄 Reporte adicional guardado: REPORTE_COBERTURA_{timestamp}.md")

def leer_reporte_json():
    """Intenta leer y mostrar estadísticas del reporte JSON"""

    try:
        if os.path.exists("coverage.json"):
            with open("coverage.json", "r") as f:
                data = json.load(f)

            print("📈 ESTADÍSTICAS DE COBERTURA:")
            print(f"   🎯 Cobertura total: {data.get('totals', {}).get('percent_covered', 0):.1f}%")
            print(f"   📄 Líneas cubiertas: {data.get('totals', {}).get('covered_lines', 0)}")
            print(f"   📄 Líneas totales: {data.get('totals', {}).get('num_statements', 0)}")
            print(f"   📄 Líneas faltantes: {data.get('totals', {}).get('missing_lines', 0)}")
            print()

            # Módulos con menor cobertura
            files = data.get('files', {})
            low_coverage = []

            for file_path, file_data in files.items():
                coverage = file_data.get('summary', {}).get('percent_covered', 0)
                if coverage < 90:  # Menos del 90%
                    low_coverage.append((file_path, coverage))

            if low_coverage:
                print("[WARN]  MÓDULOS CON COBERTURA < 90%:")
                for file_path, coverage in sorted(low_coverage, key=lambda x: x[1]):
                    print(f"   📄 {file_path}: {coverage:.1f}%")
            else:
                print("🎉 ¡Todos los módulos tienen cobertura >= 90%!")

    except Exception as e:
        print(f"[WARN]  No se pudo leer coverage.json: {e}")

def contar_tests_ejecutados():
    """Cuenta el número total de tests en el proyecto"""

    test_files = list(Path("tests").rglob("test_*.py"))
    total_tests = 0

    print("📋 INVENTARIO DE TESTS:")
    for test_file in test_files:
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Contar funciones que empiecen con test_
                test_count = content.count("def test_")
                total_tests += test_count
                if test_count > 0:
                    print(f"   📄 {test_file.relative_to(Path('tests'))}: {test_count} tests")
        except Exception as e:
            print(f"   [WARN]  Error leyendo {test_file}: {e}")

    print(f"\n🎯 TOTAL DE TESTS: {total_tests}")
    return total_tests

if __name__ == "__main__":
    print("🔍 INICIANDO ANÁLISIS DE COBERTURA...")

    # Contar tests primero
    total_tests = contar_tests_ejecutados()

    # Ejecutar análisis
    success = main()

    if success:
        print("\n[CHECK] ANÁLISIS DE COBERTURA COMPLETADO CON ÉXITO")
    else:
        print("\n[ERROR] ANÁLISIS FALLÓ - REVISAR ERRORES ARRIBA")

    print("=" * 60)
