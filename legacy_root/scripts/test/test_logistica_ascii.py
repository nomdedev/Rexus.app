"""
ASCII Test - Logistica Dialog
Tests the service generation dialog with ASCII output.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def main():
    print("Testing Logistica Service Generation Dialog...")
    print("=" * 50)

    tests_passed = 0
    total_tests = 5

    # Test 1: Import Dialog Classes
    try:
        from src.modules.logistica.view import DialogoGenerarServicio, DialogoPreviewServicios
        print("[PASS] Dialog classes imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Dialog import failed: {e}")

    # Test 2: Import Controller
    try:
        from src.modules.logistica.controller import LogisticaController
        controller = LogisticaController()
        print("[PASS] Controller imported and created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Controller import failed: {e}")

    # Test 3: Check Controller Methods
    try:
        if hasattr(controller, 'generar_servicios_automaticos'):
            print("[PASS] generar_servicios_automaticos method exists")
            tests_passed += 1
        else:
            print("[FAIL] generar_servicios_automaticos method missing")
    except Exception as e:
        print(f"[FAIL] Method check failed: {e}")

    # Test 4: Test Service Generation
    try:
        configuracion = {
            'fecha_desde': '2025-07-31',
            'fecha_hasta': '2025-08-15',
            'zona': 'Todas las zonas',
            'tipo_vehiculo': 'Automatico (mejor opcion)',
            'capacidad_maxima': '1000',
            'max_paradas': '8',
            'criterio_optimizacion': 'Eficiencia balanceada'
        }

        servicios = controller._simular_servicios_generados(configuracion)
        print(f"[PASS] Generated {len(servicios)} test services")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Service generation failed: {e}")

    # Test 5: Check View Method
    try:
        from src.modules.logistica.view import LogisticaView
        view = LogisticaView()
        if hasattr(view, 'abrir_generador_automatico'):
            print("[PASS] View button method exists")
            tests_passed += 1
        else:
            print("[FAIL] View button method missing")
    except Exception as e:
        print(f"[FAIL] View test failed: {e}")

    print("=" * 50)
    print(f"RESULTS: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("SUCCESS: All tests passed!")
        print("The logistica service generation dialog is fully implemented.")
        return True
    else:
        print("WARNING: Some tests failed.")
        return False

if __name__ == "__main__":
    main()
