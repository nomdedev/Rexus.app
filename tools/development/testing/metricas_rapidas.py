#!/usr/bin/env python3
"""
Script para obtener métricas rápidas del proyecto sin ejecutar todos los tests
"""

def contar_archivos_por_tipo():
    """Cuenta archivos por tipo en el proyecto"""
import os
from datetime import datetime
from pathlib import Path

    tipos = {
        "tests": 0,
        "modules": 0,
        "core": 0,
        "utils": 0,
        "scripts": 0,
        "docs": 0
    }

    # Contar tests
    test_dir = Path("tests")
    if test_dir.exists():
        tipos["tests"] = len(list(test_dir.rglob("*.py")))

    # Contar módulos
    modules_dir = Path("modules")
    if modules_dir.exists():
        tipos["modules"] = len(list(modules_dir.rglob("*.py")))

    # Contar core
    core_dir = Path("core")
    if core_dir.exists():
        tipos["core"] = len(list(core_dir.rglob("*.py")))

    # Contar utils
    utils_dir = Path("utils")
    if utils_dir.exists():
        tipos["utils"] = len(list(utils_dir.rglob("*.py")))

    # Contar scripts
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        tipos["scripts"] = len(list(scripts_dir.rglob("*.py")))

    # Contar docs
    docs_dir = Path("docs")
    if docs_dir.exists():
        tipos["docs"] = len(list(docs_dir.rglob("*.md")))

    return tipos

def contar_funciones_test():
    """Cuenta funciones de test específicas"""

    test_files = list(Path("tests").rglob("test_*.py"))
    contadores = {
        "archivos_test": len(test_files),
        "funciones_test": 0,
        "clases_test": 0,
        "tests_criticos": 0,
        "tests_edge_case": 0,
        "tests_integracion": 0
    }

    for test_file in test_files:
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Contar funciones test
                contadores["funciones_test"] += content.count("def test_")

                # Contar clases test
                contadores["clases_test"] += content.count("class Test")

                # Detectar tests críticos
                if "critico" in content.lower() or "critical" in content.lower():
                    contadores["tests_criticos"] += 1

                # Detectar edge cases
                if "edge" in content.lower() or "edge_case" in content.lower():
                    contadores["tests_edge_case"] += 1

                # Detectar tests de integración
                if "integracion" in content.lower() or "integration" in content.lower():
                    contadores["tests_integracion"] += 1

        except Exception as e:
            print(f"⚠️  Error leyendo {test_file}: {e}")

    return contadores

def analizar_modulos_coverage():
    """Analiza qué módulos tienen tests"""

    modules_with_tests = {}
    modules_dir = Path("modules")

    if modules_dir.exists():
        for module_path in modules_dir.iterdir():
            if module_path.is_dir():
                module_name = module_path.name
                test_path = Path("tests") / module_name

                has_tests = test_path.exists() and any(test_path.rglob("test_*.py"))
                test_count = len(list(test_path.rglob("test_*.py"))) if has_tests else 0

                modules_with_tests[module_name] = {
                    "has_tests": has_tests,
                    "test_files": test_count
                }

    return modules_with_tests

def generar_reporte_metricas():
    """Genera reporte completo de métricas"""

    print("📊 GENERANDO MÉTRICAS RÁPIDAS DEL PROYECTO")
    print("=" * 60)

    # Contar archivos
    tipos = contar_archivos_por_tipo()
    print("📁 ARCHIVOS POR TIPO:")
    for tipo, count in tipos.items():
        print(f"   {tipo}: {count} archivos")
    print()

    # Contar tests
    test_stats = contar_funciones_test()
    print("🧪 ESTADÍSTICAS DE TESTS:")
    for stat, count in test_stats.items():
        print(f"   {stat}: {count}")
    print()

    # Analizar módulos
    module_coverage = analizar_modulos_coverage()
    print("📋 COBERTURA DE MÓDULOS:")

    modules_with_tests = 0
    total_modules = len(module_coverage)

    for module, stats in module_coverage.items():
        status = "✅" if stats["has_tests"] else "❌"
        print(f"   {status} {module}: {stats['test_files']} archivos de test")
        if stats["has_tests"]:
            modules_with_tests += 1

    coverage_percent = (modules_with_tests / total_modules * 100) if total_modules > 0 else 0
    print(f"\n🎯 COBERTURA DE MÓDULOS: {modules_with_tests}/{total_modules} ({coverage_percent:.1f}%)")

    # Calcular métricas totales
    total_files = sum(tipos.values())
    test_to_code_ratio = tipos["tests"] / (tipos["modules"] + tipos["core"] + tipos["utils"]) if (tipos["modules"] + tipos["core"] + tipos["utils"]) > 0 else 0

    print(f"\n📈 MÉTRICAS GENERALES:")
    print(f"   📄 Total archivos: {total_files}")
    print(f"   🧪 Ratio test/código: {test_to_code_ratio:.2f}")
    print(f"   🎯 Funciones de test: {test_stats['funciones_test']}")
    print(f"   📊 Calidad de tests: {'EXCELENTE' if test_stats['funciones_test'] > 400 else 'BUENA' if test_stats['funciones_test'] > 200 else 'REGULAR'}")

    # Generar reporte en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = f"""# 📊 REPORTE DE MÉTRICAS - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🎯 Resumen Ejecutivo
- **Total de funciones test**: {test_stats['funciones_test']}
- **Archivos de test**: {test_stats['archivos_test']}
- **Cobertura de módulos**: {coverage_percent:.1f}%
- **Ratio test/código**: {test_to_code_ratio:.2f}

## 📁 Distribución de Archivos
- Tests: {tipos['tests']} archivos
- Módulos: {tipos['modules']} archivos
- Core: {tipos['core']} archivos
- Utils: {tipos['utils']} archivos
- Scripts: {tipos['scripts']} archivos
- Docs: {tipos['docs']} archivos

## 🧪 Análisis de Tests
- Funciones test: {test_stats['funciones_test']}
- Clases test: {test_stats['clases_test']}
- Tests críticos: {test_stats['tests_criticos']}
- Edge cases: {test_stats['tests_edge_case']}
- Tests integración: {test_stats['tests_integracion']}

## 📋 Módulos con Tests
"""

    for module, stats in module_coverage.items():
        status = "✅" if stats["has_tests"] else "❌"
        reporte += f"- {status} **{module}**: {stats['test_files']} archivos de test\n"

    reporte += f"""
## 🎯 Conclusiones
- **Estado general**: {'EXCELENTE' if test_stats['funciones_test'] > 400 else 'BUENO' if test_stats['funciones_test'] > 200 else 'REGULAR'}
- **Cobertura de módulos**: {'COMPLETA' if coverage_percent >= 90 else 'PARCIAL' if coverage_percent >= 70 else 'INSUFICIENTE'}
- **Calidad de tests**: {'ROBUSTA' if test_stats['tests_edge_case'] > 5 else 'BÁSICA'}

---
*Generado automáticamente por metricas_rapidas.py*
"""

    with open(f"tests/reports/METRICAS_TESTS.md", "w", encoding="utf-8") as f:
        f.write(reporte)

    print(f"\n📄 Reporte guardado: METRICAS_RAPIDAS_{timestamp}.md")
    print("=" * 60)

if __name__ == "__main__":
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent.parent.parent
    os.chdir(project_dir)

    print(f"📁 Analizando proyecto en: {project_dir}")
    generar_reporte_metricas()
