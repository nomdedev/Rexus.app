#!/usr/bin/env python3
"""
Script de ejemplo para generar reportes de tests
Todos los reportes se guardan en tests/reports/
"""

def generar_reporte_completo():
    """Genera un reporte completo de tests y lo guarda en tests/reports/"""

import json
import os
import subprocess
from datetime import datetime

    # Crear directorio de reportes si no existe
    os.makedirs("tests/reports", exist_ok=True)

    print("[CHART] GENERANDO REPORTE COMPLETO DE TESTS")
    print("=" * 50)

    # Ejecutar tests con cobertura
    print("🧪 Ejecutando tests con cobertura...")
    resultado_coverage = subprocess.run([
        "python", "-m", "pytest",
        "--cov=modules",
        "--cov=utils",
        "--cov-report=html:tests/reports/coverage_html",
        "--cov-report=json:tests/reports/coverage.json",
        "--junitxml=tests/reports/junit.xml",
        "-v"
    ], capture_output=True, text=True)

    # Generar reporte de seguridad
    print("🛡️ Ejecutando tests de seguridad...")
    resultado_seguridad = subprocess.run([
        "python", "-m", "pytest",
        "tests/pedidos/test_*security*.py",
        "--junitxml=tests/reports/security_junit.xml",
        "-v"
    ], capture_output=True, text=True)

    # Crear reporte resumen
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reporte = {
        "timestamp": timestamp,
        "tests_ejecutados": True,
        "coverage_generado": resultado_coverage.returncode == 0,
        "security_tests": resultado_seguridad.returncode == 0,
        "archivos_generados": [
            "tests/reports/coverage_html/index.html",
            "tests/reports/coverage.json",
            "tests/reports/junit.xml",
            "tests/reports/security_junit.xml"
        ]
    }

    # Guardar reporte resumen
    with open("tests/reports/reporte_resumen.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    # Crear README para la carpeta de reportes
    readme_content = f"""# Reportes de Tests

Esta carpeta contiene todos los reportes generados por los tests del proyecto.

## Archivos generados:

### Cobertura
- `coverage_html/index.html` - Reporte HTML de cobertura de código
- `coverage.json` - Datos de cobertura en formato JSON

### Results de Tests
- `junit.xml` - Resultados de tests en formato JUnit
- `security_junit.xml` - Resultados de tests de seguridad

### Reportes Resumen
- `reporte_resumen.json` - Resumen de la última ejecución

## Última actualización: {timestamp}

## Uso:

```bash
# Generar reporte completo
python scripts/testing/generar_reporte_ejemplo.py

# Ver cobertura en navegador
open tests/reports/coverage_html/index.html
```
"""

    with open("tests/reports/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("[CHECK] REPORTE COMPLETADO")
    print(f"📁 Archivos guardados en: tests/reports/")
    print(f"🌐 Ver cobertura: tests/reports/coverage_html/index.html")

if __name__ == "__main__":
    generar_reporte_completo()
