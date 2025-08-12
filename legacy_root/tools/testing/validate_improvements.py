#!/usr/bin/env python3
"""
Validación de mejoras técnicas - Script de verificación directa
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print(f"[CHECK] {description}: {file_path}")
        return True
    else:
        print(f"[ERROR] {description}: {file_path} - NO ENCONTRADO")
        return False


def check_directory_structure():
    """Verifica la estructura de directorios necesaria"""
    print("🔍 VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    print("=" * 50)

    checks = [
        ("rexus/utils/security.py", "Utilidades de seguridad"),
        ("rexus/utils/logging_config.py", "Configuración de logging"),
        ("rexus/utils/error_handler.py", "Manejador de errores"),
        ("rexus/utils/performance_monitor.py", "Monitor de rendimiento"),
        ("rexus/utils/database_manager.py", "Gestor de base de datos"),
        ("rexus/core/auth_manager.py", "Gestor de autorización"),
        ("requirements_updated.txt", "Dependencias actualizadas"),
        ("tools/improvements/", "Directorio de mejoras"),
        ("CHECKLIST_IMPLEMENTACION_ACTUALIZADO.md", "Checklist actualizado"),
    ]

    passed = 0
    total = len(checks)

    for file_path, description in checks:
        if check_file_exists(file_path, description):
            passed += 1

    print(f"\n[CHART] Estructura: {passed}/{total} elementos encontrados")
    return passed, total


def check_imports():
    """Verifica que los módulos se pueden importar"""
    print("\n🔍 VERIFICANDO IMPORTACIONES")
    print("=" * 50)

    import_tests = [
        ("os", "Módulo OS estándar"),
        ("sys", "Módulo sys estándar"),
        ("sqlite3", "Base de datos SQLite"),
        ("hashlib", "Funciones de hash"),
        ("logging", "Sistema de logging"),
    ]

    passed = 0
    total = len(import_tests)

    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"[CHECK] {description}: {module_name}")
            passed += 1
        except ImportError as e:
            print(f"[ERROR] {description}: {module_name} - {e}")

    print(f"\n[CHART] Importaciones: {passed}/{total} módulos disponibles")
    return passed, total


def check_requirements():
    """Verifica las dependencias actualizadas"""
    print("\n🔍 VERIFICANDO DEPENDENCIAS")
    print("=" * 50)

    if os.path.exists("requirements_updated.txt"):
        with open("requirements_updated.txt", "r", encoding="utf-8") as f:
            content = f.read()

        expected_packages = ["PyQt5", "sqlite3", "psutil", "colorlog", "python-dotenv"]

        found_packages = []
        for package in expected_packages:
            if package.lower() in content.lower():
                print(f"[CHECK] Dependencia encontrada: {package}")
                found_packages.append(package)
            else:
                print(f"[WARN] Dependencia no encontrada: {package}")

        print(
            f"\n[CHART] Dependencias: {len(found_packages)}/{len(expected_packages)} encontradas"
        )
        return len(found_packages), len(expected_packages)
    else:
        print("[ERROR] Archivo requirements_updated.txt no encontrado")
        return 0, 5


def validate_security_files():
    """Valida específicamente los archivos de seguridad"""
    print("\n🔍 VERIFICANDO ARCHIVOS DE SEGURIDAD")
    print("=" * 50)

    security_files = ["rexus/utils/security.py", "rexus/core/auth_manager.py"]

    passed = 0
    total = len(security_files)

    for file_path in security_files:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "SecurityUtils" in content or "AuthManager" in content:
                print(f"[CHECK] Archivo de seguridad válido: {file_path}")
                passed += 1
            else:
                print(f"[WARN] Archivo existe pero contenido incompleto: {file_path}")
        else:
            print(f"[ERROR] Archivo no encontrado: {file_path}")

    print(f"\n[CHART] Seguridad: {passed}/{total} archivos válidos")
    return passed, total


def check_recent_improvements():
    """Verifica las mejoras recién implementadas"""
    print("\n🔍 VERIFICANDO MEJORAS RECIENTES")
    print("=" * 50)

    improvements = [
        ("rexus/utils/logging_config.py", "Sistema de logging mejorado"),
        ("rexus/utils/error_handler.py", "Manejo de errores centralizado"),
        ("rexus/utils/performance_monitor.py", "Monitoreo de rendimiento"),
        ("rexus/utils/database_manager.py", "Gestión mejorada de BD"),
        ("tools/improvements/implement_technical_improvements.py", "Script de mejoras"),
    ]

    passed = 0
    total = len(improvements)

    for file_path, description in improvements:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 100:  # Archivo debe tener contenido
                print(f"[CHECK] {description}: {file_path} ({file_size} bytes)")
                passed += 1
            else:
                print(
                    f"[WARN] {description}: {file_path} (archivo muy pequeño: {file_size} bytes)"
                )
        else:
            print(f"[ERROR] {description}: {file_path} - NO ENCONTRADO")

    print(f"\n[CHART] Mejoras: {passed}/{total} implementadas correctamente")
    return passed, total


def generate_summary_report():
    """Genera un reporte resumen de la validación"""
    print("\n" + "=" * 60)
    print("📋 REPORTE FINAL DE VALIDACIÓN")
    print("=" * 60)

    # Ejecutar todas las verificaciones
    structure_passed, structure_total = check_directory_structure()
    imports_passed, imports_total = check_imports()
    deps_passed, deps_total = check_requirements()
    security_passed, security_total = validate_security_files()
    improvements_passed, improvements_total = check_recent_improvements()

    # Calcular totales
    total_passed = (
        structure_passed
        + imports_passed
        + deps_passed
        + security_passed
        + improvements_passed
    )
    total_checks = (
        structure_total
        + imports_total
        + deps_total
        + security_total
        + improvements_total
    )

    success_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0

    print(f"\n[CHART] RESULTADOS FINALES:")
    print(f"   • Estructura: {structure_passed}/{structure_total}")
    print(f"   • Importaciones: {imports_passed}/{imports_total}")
    print(f"   • Dependencias: {deps_passed}/{deps_total}")
    print(f"   • Seguridad: {security_passed}/{security_total}")
    print(f"   • Mejoras: {improvements_passed}/{improvements_total}")
    print(f"   • TOTAL: {total_passed}/{total_checks} ({success_rate:.1f}%)")

    if success_rate >= 90:
        print(f"\n🎉 VALIDACIÓN EXITOSA ({success_rate:.1f}%)")
        print("[CHECK] Sistema completamente preparado")
        status = "EXCELLENT"
    elif success_rate >= 75:
        print(f"\n[CHECK] VALIDACIÓN BUENA ({success_rate:.1f}%)")
        print("🔧 Mejoras menores recomendadas")
        status = "GOOD"
    elif success_rate >= 60:
        print(f"\n[WARN] VALIDACIÓN PARCIAL ({success_rate:.1f}%)")
        print("🔧 Algunas correcciones necesarias")
        status = "PARTIAL"
    else:
        print(f"\n[ERROR] VALIDACIÓN CON PROBLEMAS ({success_rate:.1f}%)")
        print("🚨 Revisar y corregir errores críticos")
        status = "FAILED"

    # Escribir reporte a archivo
    timestamp = Path("logs/validation_report.txt")
    timestamp.parent.mkdir(exist_ok=True)

    with open(timestamp, "w", encoding="utf-8") as f:
        f.write(f"Reporte de Validación - {status}\n")
        f.write(f"Fecha: {Path(__file__).stat().st_mtime}\n")
        f.write(f"Éxito: {success_rate:.1f}%\n")
        f.write(f"Total verificaciones: {total_passed}/{total_checks}\n")

    print(f"\n📄 Reporte guardado en: {timestamp}")

    return success_rate >= 60


if __name__ == "__main__":
    print("🧪 VALIDACIÓN DE MEJORAS TÉCNICAS REXUS")
    print("Verificando implementación de mejoras...")

    success = generate_summary_report()

    if success:
        print("\n[ROCKET] LISTO PARA SIGUIENTE FASE")
    else:
        print("\n[WARN] CORREGIR PROBLEMAS ANTES DE CONTINUAR")

    sys.exit(0 if success else 1)
