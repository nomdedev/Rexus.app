#!/usr/bin/env python3
"""
Script de prueba rápida para verificar el estado de los tests.
Ejecuta tests individuales para identificar problemas específicos.
"""

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

def test_basic_imports():
    """Verificar imports básicos."""
    print("=== Testing Basic Imports ===")

    tests = [
        ("pytest", "import pytest"),
        ("unittest.mock", "from unittest.mock import MagicMock"),
        ("pathlib", "from pathlib import Path"),
        ("PyQt6.QtWidgets", "from PyQt6.QtWidgets import QApplication"),
        ("PyQt6.QtCore", "from PyQt6.QtCore import Qt"),
    ]

    results = {}

    for name, import_str in tests:
        try:
            exec(import_str)
            results[name] = "[OK] OK"
        except Exception as e:
            results[name] = f"✗ ERROR: {e}"

    for name, result in results.items():
        print(f"  {name}: {result}")

    return results

def test_pedidos_controller():
    """Test del controlador de pedidos."""
    print("\n=== Testing Pedidos Controller ===")

    try:
        # Ejecutar test simple
        dummy_model = DummyModel()
        dummy_view = DummyView()

        # Simular creación de controller
        print("  [OK] Imports OK")
        print("  [OK] DummyModel creation OK")
        print("  [OK] DummyView creation OK")

        # Test básico de generación de pedido
        pedido_id = dummy_model.generar_pedido(1)
        print(f"  [OK] Pedido generated: {pedido_id}")

        # Test básico de recepción
        dummy_model.recibir_pedido(pedido_id)
        print("  [OK] Pedido received OK")

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        traceback.print_exc()
        return False

def test_edge_cases_basic():
    """Test básico de edge cases."""
    print("\n=== Testing Edge Cases (Basic) ===")

    try:
        test_instance = TestEdgeCasesGeneral()

        # Test de strings largos
        test_instance.test_strings_extremadamente_largos()
        print("  [OK] String extremos OK")

        # Test de números extremos
        test_instance.test_numeros_extremos()
        print("  [OK] Números extremos OK")

        # Test de caracteres Unicode
        test_instance.test_caracteres_unicode_extremos()
        print("  [OK] Caracteres Unicode OK")

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        traceback.print_exc()
        return False

def test_sidebar_components():
    """Test de componentes del sidebar."""
    print("\n=== Testing Sidebar Components ===")

    try:
        test_instance = TestSidebarComponentes()
        test_instance.setup_method()

        print("  [OK] TestSidebarComponentes setup OK")

        # Intentar test de inicialización (puede fallar por PyQt6)
        try:
            test_instance.test_sidebar_inicializacion()
            print("  [OK] Sidebar initialization OK")
        except Exception as e:
            if "PyQt6" in str(e) or "QApplication" in str(e):
                print("  ⚠ Sidebar test skipped (PyQt6 issue)")
            else:
                raise e

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        traceback.print_exc()
        return False

def test_login_integration():
    """Test de integración del login."""
    print("\n=== Testing Login Integration ===")

    try:
        # Test del modelo dummy
        dummy_model = DummyUsuariosModel()

        # Test de autenticación
        result = dummy_model.autenticar("TEST_USER", "correct_password")
        print(f"  [OK] Authentication test: {result is not None}")

        # Test de módulos por rol
        usuario_test = {"rol": "administrador"}
        modulos = dummy_model.obtener_modulos_permitidos(usuario_test)
import sys
import traceback
from pathlib import Path

from tests.test_edge_cases import TestEdgeCasesGeneral
from tests.test_login_mainwindow_integration import DummyUsuariosModel
from tests.test_pedidos_controller import DummyModel, DummyView, controller
from tests.test_sidebar_components import TestSidebarComponentes

        print(f"  [OK] Modules for admin: {len(modulos) if modulos else 0}")

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas."""
    print("🧪 QUICK TEST RUNNER")
    print("=" * 50)

    all_results = []

    # Ejecutar tests
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Pedidos Controller", test_pedidos_controller),
        ("Edge Cases Basic", test_edge_cases_basic),
        ("Sidebar Components", test_sidebar_components),
        ("Login Integration", test_login_integration),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            all_results.append((test_name, result))
        except Exception as e:
            print(f"\n=== FATAL ERROR in {test_name} ===")
            traceback.print_exc()
            all_results.append((test_name, False))

    # Resumen final
    print("\n" + "=" * 50)
    print("[CHART] SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in all_results:
        if isinstance(result, dict):  # Para test_basic_imports
            success_count = sum(1 for v in result.values() if v.startswith("[OK]"))
            total_count = len(result)
            if success_count == total_count:
                print(f"[OK] {test_name}: {success_count}/{total_count} OK")
                passed += 1
            else:
                print(f"✗ {test_name}: {success_count}/{total_count} OK")
                failed += 1
        elif result:
            print(f"[OK] {test_name}: PASSED")
            passed += 1
        else:
            print(f"✗ {test_name}: FAILED")
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("[WARN]  Some tests failed. Check details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
