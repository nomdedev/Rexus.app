#!/usr/bin/env python3
"""
Script para ejecutar análisis de seguridad completo con safety y bandit
"""

def ejecutar_safety():
    """Ejecuta análisis de seguridad con safety"""
    print("[LOCK] EJECUTANDO ANÁLISIS DE SEGURIDAD CON SAFETY")
    print("-" * 50)
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

    try:
        # Ejecutar safety check
        result = subprocess.run([
            sys.executable, "-m", "safety", "check",
            "--json", "--output", "safety-report.json"
        ], capture_output=True, text=True, timeout=60)

        print(f"Código de salida: {result.returncode}")

        if result.stdout:
            print("📄 SALIDA:")
            print(result.stdout)

        if result.stderr:
            print("[WARN]  ERRORES:")
            print(result.stderr)

        # Leer el reporte si se generó
        if Path("safety-report.json").exists():
            with open("safety-report.json", "r") as f:
                safety_data = json.load(f)

            if isinstance(safety_data, list) and len(safety_data) > 0:
                print(f"\n[ERROR] VULNERABILIDADES ENCONTRADAS: {len(safety_data)}")
                for vuln in safety_data[:5]:  # Mostrar solo las primeras 5
                    print(f"   📦 {vuln.get('package_name', 'N/A')}: {vuln.get('vulnerability_id', 'N/A')}")
            else:
                print("[CHECK] NO SE ENCONTRARON VULNERABILIDADES EN DEPENDENCIAS")

    except subprocess.TimeoutExpired:
        print("⏰ Timeout ejecutando safety")
    except Exception as e:
        print(f"[ERROR] Error ejecutando safety: {e}")

def ejecutar_bandit():
    """Ejecuta análisis de código estático con bandit"""
    print("\n🔍 EJECUTANDO ANÁLISIS ESTÁTICO CON BANDIT")
    print("-" * 50)

    try:
        # Ejecutar bandit
        result = subprocess.run([
            sys.executable, "-m", "bandit",
            "-r", "modules/", "core/", "utils/",
            "-f", "json", "-o", "bandit-report.json"
        ], capture_output=True, text=True, timeout=120)

        print(f"Código de salida: {result.returncode}")

        if result.stdout:
            print("📄 SALIDA:")
            print(result.stdout)

        # Leer el reporte si se generó
        if Path("bandit-report.json").exists():
            with open("bandit-report.json", "r") as f:
                bandit_data = json.load(f)

            results = bandit_data.get("results", [])
            metrics = bandit_data.get("metrics", {})

            print(f"\n[CHART] MÉTRICAS BANDIT:")
            print(f"   📄 Archivos analizados: {metrics.get('_totals', {}).get('loc', 0)}")
            print(f"   🔍 Issues encontrados: {len(results)}")

            if results:
                print(f"\n[WARN]  ISSUES ENCONTRADOS:")
                for issue in results[:10]:  # Mostrar solo los primeros 10
                    severity = issue.get("issue_severity", "UNKNOWN")
                    confidence = issue.get("issue_confidence", "UNKNOWN")
                    test_id = issue.get("test_id", "UNKNOWN")
                    filename = issue.get("filename", "UNKNOWN")
                    print(f"   📄 {filename}: {test_id} [{severity}/{confidence}]")
            else:
                print("[CHECK] NO SE ENCONTRARON ISSUES DE SEGURIDAD")

    except subprocess.TimeoutExpired:
        print("⏰ Timeout ejecutando bandit")
    except Exception as e:
        print(f"[ERROR] Error ejecutando bandit: {e}")

def generar_reporte_consolidado():
    """Genera un reporte consolidado de seguridad"""
    print("\n📋 GENERANDO REPORTE CONSOLIDADO")
    print("-" * 50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = f"""# [LOCK] REPORTE DE SEGURIDAD CONSOLIDADO - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## [CHART] Resumen Ejecutivo

"""

    # Añadir datos de safety
    if Path("safety-report.json").exists():
        try:
            with open("safety-report.json", "r") as f:
                safety_data = json.load(f)

            if isinstance(safety_data, list):
                reporte += f"### 📦 Análisis de Dependencias (Safety)\n"
                reporte += f"- **Vulnerabilidades encontradas**: {len(safety_data)}\n"
                if len(safety_data) > 0:
                    reporte += f"- **Estado**: [WARN] REVISAR DEPENDENCIAS\n\n"
                    for vuln in safety_data[:5]:
                        reporte += f"  - {vuln.get('package_name', 'N/A')}: {vuln.get('vulnerability_id', 'N/A')}\n"
                else:
                    reporte += f"- **Estado**: [CHECK] DEPENDENCIAS SEGURAS\n"
                reporte += "\n"
        except:
            reporte += "### 📦 Análisis de Dependencias\n- [ERROR] Error leyendo reporte safety\n\n"

    # Añadir datos de bandit
    if Path("bandit-report.json").exists():
        try:
            with open("bandit-report.json", "r") as f:
                bandit_data = json.load(f)

            results = bandit_data.get("results", [])
            metrics = bandit_data.get("metrics", {})

            reporte += f"### 🔍 Análisis de Código Estático (Bandit)\n"
            reporte += f"- **Archivos analizados**: {metrics.get('_totals', {}).get('loc', 0)}\n"
            reporte += f"- **Issues encontrados**: {len(results)}\n"

            if len(results) > 0:
                reporte += f"- **Estado**: [WARN] REVISAR CÓDIGO\n\n"
                # Agrupar por severidad
                high = [r for r in results if r.get("issue_severity") == "HIGH"]
                medium = [r for r in results if r.get("issue_severity") == "MEDIUM"]
                low = [r for r in results if r.get("issue_severity") == "LOW"]

                reporte += f"  - HIGH: {len(high)} issues\n"
                reporte += f"  - MEDIUM: {len(medium)} issues\n"
                reporte += f"  - LOW: {len(low)} issues\n"
            else:
                reporte += f"- **Estado**: [CHECK] CÓDIGO SEGURO\n"
            reporte += "\n"
        except:
            reporte += "### 🔍 Análisis de Código Estático\n- [ERROR] Error leyendo reporte bandit\n\n"

    reporte += f"""## 🎯 Recomendaciones

1. **Dependencias**: Mantener actualizadas las librerías
2. **Código**: Revisar issues de alta prioridad
3. **Monitoreo**: Ejecutar análisis regularmente
4. **Automatización**: Integrar en CI/CD pipeline

## 📁 Archivos Generados

- `safety-report.json`: Reporte detallado de dependencias
- `bandit-report.json`: Reporte detallado de código estático
- `REPORTE_SEGURIDAD_{timestamp}.md`: Este archivo

---
*Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    filename = f"REPORTE_SEGURIDAD_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(reporte)

    print(f"📄 Reporte consolidado guardado: {filename}")

def main():
    print("[LOCK] ANÁLISIS DE SEGURIDAD COMPLETO")
    print("=" * 60)

    ejecutar_safety()
    ejecutar_bandit()
    generar_reporte_consolidado()

    print("\n🎉 ANÁLISIS DE SEGURIDAD COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
