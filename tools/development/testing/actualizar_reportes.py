#!/usr/bin/env python3
"""
Script para actualizar scripts de testing para que guarden reportes en tests/reports/
"""


def actualizar_scripts_testing():
    """Actualiza scripts de testing para usar la nueva carpeta de reportes"""

    print("📊 ACTUALIZANDO SCRIPTS DE TESTING")
    print("=" * 50)

    # Scripts a actualizar
    scripts_testing = [
        "scripts/testing/generar_reporte_cobertura.py",
        "scripts/testing/metricas_rapidas.py",
        "scripts/testing/verificacion_completa.py",
        "scripts/testing/verificar_seguridad_completa.py",
    ]

    # Patrones a reemplazar para dirigir reportes a tests/reports/
    patrones_reemplazo = [
        # Archivos HTML
        (r'["\']reporte_[^"\']*\.html["\']', '"tests/reports/reporte_cobertura.html"'),
        (r'["\']coverage_html["\']', '"tests/reports/coverage_html"'),
        (r'["\']informe_[^"\']*\.html["\']', '"tests/reports/informe_seguridad.html"'),
        # Archivos JSON
        (r'["\']reporte_[^"\']*\.json["\']', '"tests/reports/reporte_metricas.json"'),
        (r'["\']metricas_[^"\']*\.json["\']', '"tests/reports/metricas_tests.json"'),
        (r'["\']estado_[^"\']*\.json["\']', '"tests/reports/estado_tests.json"'),
        # Archivos MD
        (r'["\']REPORTE_[^"\']*\.md["\']', '"tests/reports/REPORTE_TESTS.md"'),
        (r'["\']METRICAS_[^"\']*\.md["\']', '"tests/reports/METRICAS_TESTS.md"'),
    ]

    contador_actualizados = 0

    for script_path in scripts_testing:
        if os.path.exists(script_path):
            print(f"\n🔧 Actualizando: {script_path}")

            # Leer contenido actual
            with open(script_path, "r", encoding="utf-8") as f:
                contenido = f.read()

            contenido_original = contenido

            # Aplicar reemplazos
            for patron, reemplazo in patrones_reemplazo:
                contenido = re.sub(patron, reemplazo, contenido)

            # Agregar creación de directorio si no existe
            if "tests/reports/" in contenido and "os.makedirs" not in contenido:
                # Buscar imports de os
                if "import os" in contenido:
                    # Agregar después de los imports
                    lines = contenido.split("\n")
                    for i, line in enumerate(lines):
                        if line.strip().startswith("def ") and "main" in line:
                            lines.insert(
                                i, "    # Crear directorio de reportes si no existe"
                            )
                            lines.insert(
                                i + 1, '    os.makedirs("tests/reports", exist_ok=True)'
                            )
                            lines.insert(i + 2, "")
                            break
                    contenido = "\n".join(lines)
                else:
                    # Agregar import de os al inicio
                    contenido = "import os\n" + contenido

            # Escribir solo si hubo cambios
            if contenido != contenido_original:
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                print(f"   ✅ Actualizado para usar tests/reports/")
                contador_actualizados += 1
            else:
                print(f"   ℹ️ No necesita cambios")
        else:
            print(f"   ❌ No encontrado: {script_path}")

    # Crear script de ejemplo para generar reportes
    script_ejemplo = """#!/usr/bin/env python3
\"\"\"
Script de ejemplo para generar reportes de tests
Todos los reportes se guardan en tests/reports/
\"\"\"

def generar_reporte_completo():
    \"\"\"Genera un reporte completo de tests y lo guarda en tests/reports/\"\"\"

    # Crear directorio de reportes si no existe
    os.makedirs("tests/reports", exist_ok=True)

    print("📊 GENERANDO REPORTE COMPLETO DE TESTS")
    print("=" * 50)

    # Ejecutar tests con cobertura
    print("🧪 Ejecutando tests con cobertura...")
    resultado_coverage = subprocess.run([
from datetime import datetime
import json
import os
import os
import re

import subprocess
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
    readme_content = f\"\"\"# Reportes de Tests

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
\"\"\"

    with open("tests/reports/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ REPORTE COMPLETADO")
    print(f"📁 Archivos guardados en: tests/reports/")
    print(f"🌐 Ver cobertura: tests/reports/coverage_html/index.html")

if __name__ == "__main__":
    generar_reporte_completo()
"""

    with open("scripts/testing/generar_reporte_ejemplo.py", "w", encoding="utf-8") as f:
        f.write(script_ejemplo)

    print(f"\n📄 Creado script de ejemplo: scripts/testing/generar_reporte_ejemplo.py")

    # Actualizar README de testing
    readme_testing = """# Testing Scripts

Scripts para ejecución y generación de reportes de tests.

**📍 IMPORTANTE:** Todos los reportes se guardan en `tests/reports/`

## Scripts disponibles:

- `generar_reporte_cobertura.py` - Genera reportes de cobertura de código
- `generar_reporte_ejemplo.py` - Ejemplo completo de generación de reportes
- `metricas_rapidas.py` - Métricas rápidas de tests
- `verificacion_completa.py` - Verificación completa del proyecto
- `verificar_seguridad_completa.py` - Verificación de seguridad

## Uso:

```bash
# Desde la raíz del proyecto
python scripts/testing/[script_name].py

# Ejemplo: Generar reporte completo
python scripts/testing/generar_reporte_ejemplo.py
```

## Estructura de Reportes:

```
tests/reports/
├── coverage_html/          # Reportes HTML de cobertura
├── coverage.json          # Datos de cobertura JSON
├── junit.xml              # Resultados JUnit
├── security_junit.xml     # Tests de seguridad
├── reporte_resumen.json   # Resumen de ejecución
└── README.md              # Documentación de reportes
```

---
*Los reportes se organizan automáticamente en tests/reports/ para mantener orden*
"""

    with open("scripts/testing/README.md", "w", encoding="utf-8") as f:
        f.write(readme_testing)

    print("📄 Actualizado README de testing")

    # Resumen final
    print("\n" + "=" * 50)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("=" * 50)
    print(f"📊 Scripts actualizados: {contador_actualizados}")
    print("📁 Directorio de reportes: tests/reports/")
    print("📄 Script de ejemplo creado")
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Ejecutar: python scripts/testing/generar_reporte_ejemplo.py")
    print("   2. Verificar reportes en: tests/reports/")
    print("   3. Abrir cobertura: tests/reports/coverage_html/index.html")


if __name__ == "__main__":
    actualizar_scripts_testing()
