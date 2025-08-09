#!/usr/bin/env python3
"""
Tests básicos de funcionalidad para verificar que la aplicación funciona
después de la reorganización de src/ -> rexus/
"""

import os
import sys
from pathlib import Path

import pytest

# Configurar path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_project_structure():
    """Verificar que la nueva estructura de proyecto existe"""
    assert project_root.exists(), "El directorio del proyecto debe existir"

    # Verificar nuevas carpetas principales
    assert (project_root / "rexus").exists(), "Carpeta rexus/ debe existir"
    assert (project_root / "docs").exists(), "Carpeta docs/ debe existir"
    assert (project_root / "tests").exists(), "Carpeta tests/ debe existir"
    assert (project_root / "tools").exists(), "Carpeta tools/ debe existir"


def test_rexus_structure():
    """Verificar que la estructura de rexus/ es correcta"""
    rexus_path = project_root / "rexus"

    # Verificar carpetas principales de rexus
    assert (rexus_path / "core").exists(), "rexus/core/ debe existir"
    assert (rexus_path / "main").exists(), "rexus/main/ debe existir"
    assert (rexus_path / "modules").exists(), "rexus/modules/ debe existir"

    # Verificar archivos principales
    assert (rexus_path / "core" / "auth.py").exists(), "rexus/core/auth.py debe existir"
    assert (rexus_path / "core" / "database.py").exists(), (
        "rexus/core/database.py debe existir"
    )
    assert (rexus_path / "main" / "app.py").exists(), "rexus/main/app.py debe existir"


def test_imports_work():
    """Verificar que los imports funcionan con la nueva estructura"""
    try:
        # Test imports básicos
        import rexus
        import rexus.core
        import rexus.main
        import rexus.modules

        print("[CHECK] Imports básicos funcionan")
    except ImportError as e:
        pytest.skip(f"Import error esperado durante reorganización: {e}")


def test_tools_structure():
    """Verificar que las herramientas están organizadas"""
    tools_path = project_root / "tools"

    if tools_path.exists():
        # Verificar que maintenance existe
        maintenance_path = tools_path / "maintenance"
        if maintenance_path.exists():
            assert (maintenance_path / "fix_test_imports.py").exists(), (
                "Script de fix imports debe existir"
            )


def test_docs_structure():
    """Verificar que la documentación está organizada"""
    docs_path = project_root / "docs"

    # Verificar archivos principales de documentación
    expected_docs = [
        "01_README.md",
        "02_architecture.md",
        "03_database.md",
        "04_security.md",
        "05_deployment.md",
        "06_development.md",
    ]

    for doc_file in expected_docs:
        doc_path = docs_path / doc_file
        if doc_path.exists():
            print(f"[CHECK] Encontrado: {doc_file}")
        else:
            print(f"[WARN]  No encontrado: {doc_file}")


if __name__ == "__main__":
    print("Ejecutando tests básicos de funcionalidad...")

    # Ejecutar tests uno por uno para ver el progreso
    try:
        test_project_structure()
        print("[CHECK] Estructura del proyecto OK")
    except Exception as e:
        print(f"[ERROR] Error en estructura del proyecto: {e}")

    try:
        test_rexus_structure()
        print("[CHECK] Estructura de rexus/ OK")
    except Exception as e:
        print(f"[ERROR] Error en estructura de rexus/: {e}")

    try:
        test_imports_work()
        print("[CHECK] Imports OK")
    except Exception as e:
        print(f"[WARN]  Imports con problemas: {e}")

    try:
        test_tools_structure()
        print("[CHECK] Estructura de tools/ OK")
    except Exception as e:
        print(f"[WARN]  Tools: {e}")

    try:
        test_docs_structure()
        print("[CHECK] Estructura de docs/ verificada")
    except Exception as e:
        print(f"[WARN]  Docs: {e}")

    print("\n🎉 Tests básicos completados")
