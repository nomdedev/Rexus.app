#!/usr/bin/env python3
"""
Verificación Simple del Estado del Proyecto Rexus.app
"""

import sys
from pathlib import Path


def verificar_estructura_proyecto():
    """Verifica la estructura básica del proyecto"""
    root_path = Path.cwd()
    print("=== VERIFICACIÓN RÁPIDA DEL PROYECTO REXUS ===")
    print(f"Directorio de trabajo: {root_path}")

    # Verificar directorios principales
    directorios_principales = [
        "rexus",
        "utils",
        "config",
        "scripts",
        "tests",
        "docs",
        "static",
        "logs",
        "backups",
    ]

    print("\n1. ESTRUCTURA DE DIRECTORIOS:")
    for directorio in directorios_principales:
        path = root_path / directorio
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {directorio}/")

    # Verificar módulos
    print("\n2. MÓDULOS DE REXUS:")
    modulos_path = root_path / "rexus" / "modules"
    if modulos_path.exists():
        modulos = [
            d
            for d in modulos_path.iterdir()
            if d.is_dir() and not d.name.startswith("__")
        ]
        print(f"  Encontrados {len(modulos)} módulos:")
        for modulo in sorted(modulos):
            view_file = modulo / "view.py"
            model_file = modulo / "model.py"
            status_view = "✅" if view_file.exists() else "❌"
            status_model = "✅" if model_file.exists() else "❌"
            print(f"    {modulo.name}: View {status_view} Model {status_model}")
    else:
        print("  ❌ Directorio rexus/modules no encontrado")

    # Verificar archivos críticos
    print("\n3. ARCHIVOS CRÍTICOS:")
    archivos_criticos = [
        "docker-compose.yml",
        "Dockerfile",
        "requirements.txt",
        "config/rexus_config.json",
        "utils/data_sanitizer.py",
        "utils/rexus_styles.py",
        "docs/UI_UX_STANDARDS.md",
        "REPORTE_PROGRESO_COMPLETO.md",
    ]

    for archivo in archivos_criticos:
        path = root_path / archivo
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  ✅ {archivo} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {archivo}")

    # Verificar tests
    print("\n4. INFRAESTRUCTURA DE TESTING:")
    test_dirs = ["tests/security", "tests/performance", "tests/edge_cases"]
    for test_dir in test_dirs:
        path = root_path / test_dir
        if path.exists():
            test_files = list(path.glob("test_*.py"))
            print(f"  ✅ {test_dir}: {len(test_files)} archivos de test")
        else:
            print(f"  ❌ {test_dir}")

    # Verificar scripts UI/UX
    print("\n5. SCRIPTS UI/UX:")
    uiux_scripts = [
        "scripts/ui_ux/audit_simple.py",
        "scripts/ui_ux/apply_fixes.py",
        "scripts/ui_ux/audit_accessibility.py",
    ]

    for script in uiux_scripts:
        path = root_path / script
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {script}")

    print("\n6. ESTADO GENERAL:")

    # Intentar importar componentes críticos
    try:
        sys.path.insert(0, str(root_path))
        from utils.data_sanitizer import DataSanitizer

        print("  ✅ DataSanitizer: Importación exitosa")
    except Exception as e:
        print(f"  ❌ DataSanitizer: Error - {e}")

    try:
        from utils.rexus_styles import RexusStyles

        print("  ✅ RexusStyles: Importación exitosa")
    except Exception as e:
        print(f"  ❌ RexusStyles: Error - {e}")

    try:
        from utils.two_factor_auth import TwoFactorAuth

        print("  ✅ TwoFactorAuth: Importación exitosa")
    except Exception as e:
        print(f"  ❌ TwoFactorAuth: Error - {e}")

    # Verificar archivos de configuración
    print("\n7. CONFIGURACIÓN:")
    config_files = [".env", "config/rexus_config.json"]
    for config_file in config_files:
        path = root_path / config_file
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {config_file}")

    print("\n" + "=" * 50)
    print("RESUMEN:")

    # Calcular puntuación general
    total_checks = (
        len(directorios_principales) + len(archivos_criticos) + 3
    )  # +3 por imports
    passed_checks = 0

    # Contar directorios existentes
    for directorio in directorios_principales:
        if (root_path / directorio).exists():
            passed_checks += 1

    # Contar archivos existentes
    for archivo in archivos_criticos:
        if (root_path / archivo).exists():
            passed_checks += 1

    # Contar imports exitosos
    import_tests = [
        "utils.data_sanitizer",
        "utils.rexus_styles",
        "utils.two_factor_auth",
    ]

    for import_test in import_tests:
        try:
            __import__(import_test)
            passed_checks += 1
        except:
            pass

    score = (passed_checks / total_checks) * 100

    if score >= 90:
        status = "🟢 EXCELENTE"
    elif score >= 75:
        status = "🟡 BUENO"
    elif score >= 50:
        status = "🟠 REGULAR"
    else:
        status = "🔴 CRÍTICO"

    print(f"Puntuación: {score:.1f}% - {status}")
    print(f"Componentes OK: {passed_checks}/{total_checks}")

    if score >= 75:
        print("\n✅ El proyecto está en buen estado para continuar")
        return True
    else:
        print(f"\n❌ Se requieren correcciones antes de continuar")
        return False


if __name__ == "__main__":
    exito = verificar_estructura_proyecto()
    exit(0 if exito else 1)
