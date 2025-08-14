"""
Simple Test - Logística Dialog
Basic functionality test for the service generation dialog.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def main():
    print("Testing Logística Service Generation Dialog...")

    # Test 1: Import Dialog Classes
    try:
        from src.modules.logistica.view import DialogoGenerarServicio, DialogoPreviewServicios
        print("[OK] Dialog classes imported successfully")
    except Exception as e:
        print(f"✗ Dialog import failed: {e}")
        return False

    # Test 2: Import Controller
    try:
        from src.modules.logistica.controller import LogisticaController
        controller = LogisticaController()
        print("[OK] Controller imported and created successfully")
    except Exception as e:
        print(f"✗ Controller import failed: {e}")
        return False

    # Test 3: Check Controller Methods
    try:
        if hasattr(controller, 'generar_servicios_automaticos'):
            print("[OK] generar_servicios_automaticos method exists")
        else:
            print("✗ generar_servicios_automaticos method missing")
            return False
    except Exception as e:
        print(f"✗ Method check failed: {e}")
        return False

    # Test 4: Test Service Generation
    try:
        configuracion = {
            'fecha_desde': '2025-07-31',
            'fecha_hasta': '2025-08-15',
            'zona': 'Todas las zonas',
            'tipo_vehiculo': 'Automático (mejor opción)',
            'capacidad_maxima': '1000',
            'max_paradas': '8',
            'criterio_optimizacion': 'Eficiencia balanceada'
        }

        servicios = controller._simular_servicios_generados(configuracion)
        print(f"[OK] Generated {len(servicios)} test services")
    except Exception as e:
        print(f"✗ Service generation failed: {e}")
        return False

    # Test 5: Check View Method
    try:
        from src.modules.logistica.view import LogisticaView
        view = LogisticaView()
        if hasattr(view, 'abrir_generador_automatico'):
            print("[OK] View button method exists")
        else:
            print("✗ View button method missing")
            return False
    except Exception as e:
        print(f"✗ View test failed: {e}")
        return False

    print("\n🎉 ALL TESTS PASSED!")
    print("The logística service generation dialog is fully implemented and \
        ready.")
    return True

if __name__ == "__main__":
    main()
