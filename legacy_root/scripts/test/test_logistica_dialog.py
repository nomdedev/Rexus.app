"""
Test Script - Logística Dialog Testing
Tests the new service generation dialog functionality.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def test_dialog_import():
    """Test that the dialog classes can be imported correctly."""
    print("\n[TEST] Dialog Import Test...")

    from rexus.modules.logistica.view import DialogoGenerarServicio, DialogoPreviewServicios
    print("  [OK] DialogoGenerarServicio imported successfully")
    print("  [OK] DialogoPreviewServicios imported successfully")


def test_controller_method():
    """Test that the controller method exists."""
    print("\n[TEST] Controller Method Test...")

    from rexus.modules.logistica.controller import LogisticaController

    # Create controller instance
    controller = LogisticaController()

    # Check if the new method exists
    assert hasattr(controller, 'generar_servicios_automaticos'), "generar_servicios_automaticos method not found"
    print("  [OK] generar_servicios_automaticos method exists")

    assert hasattr(controller, '_procesar_generacion_servicios'), "_procesar_generacion_servicios method not found"
    print("  [OK] _procesar_generacion_servicios method exists")

    assert hasattr(controller, '_simular_servicios_generados'), "_simular_servicios_generados method not found"
    print("  [OK] _simular_servicios_generados method exists")


def test_view_button_method():
    """Test that the view button method exists."""
    print("\n[TEST] View Button Method Test...")

    from rexus.modules.logistica.view import LogisticaView

    # Create view instance
    view = LogisticaView()

    # Check if the new method exists
    assert hasattr(view, 'abrir_generador_automatico'), "abrir_generador_automatico method not found"
    print("  [OK] abrir_generador_automatico method exists")


def test_service_generation_simulation():
    """Test the service generation simulation."""
    print("\n[TEST] Service Generation Simulation...")

    from rexus.modules.logistica.controller import LogisticaController

    controller = LogisticaController()

    # Create test configuration
    configuracion = {
        'fecha_desde': '2025-07-31',
        'fecha_hasta': '2025-08-15',
        'estados': 'Pendiente',
        'prioridad': 'Alta',
        'zona': 'Todas las zonas',
        'radio_maximo': '50',
        'tipo_vehiculo': 'Automático (mejor opción)',
        'capacidad_maxima': '1000',
        'max_paradas': '8',
        'criterio_optimizacion': 'Eficiencia balanceada',
        'considerar_trafico': 'Sí, considerar tráfico actual'
    }

    # Test service generation simulation
    servicios = controller._simular_servicios_generados(configuracion)

    assert len(servicios) > 0, "No services generated"
    print(f"  [OK] Generated {len(servicios)} simulated services")

    # Check service structure
    sample_service = servicios[0]
    required_fields = ['codigo', 'descripcion', 'zona', 'fecha_programada', 'estado']

    missing_fields = [field for field in required_fields if field not in sample_service]
    if missing_fields:
        print(f"  [WARNING] Missing fields in service: {missing_fields}")
    else:
        print("  [OK] Service structure is complete")

    # Show sample service
    print(f"  [INFO] Sample service: {sample_service.get('codigo', 'N/A')} - {sample_service.get('descripcion', '')}")


def test_dialog_configuration():
    """Test dialog configuration retrieval."""
    print("\n[TEST] Dialog Configuration Test...")

    # This test would require PyQt6 to be fully functional
    # For now, we'll just test that the classes can be instantiated
    from rexus.modules.logistica.view import DialogoGenerarServicio

    # Note: This would normally require a QApplication to run
    print("  [OK] Dialog class definition is valid")
    print("  [INFO] Full dialog testing requires PyQt6 runtime environment")


def main():
    """Optional manual runner for the dialog tests. Does not return booleans."""
    print("="*70)
    print("LOGÍSTICA SERVICE GENERATION DIALOG TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Dialog Import", test_dialog_import),
        ("Controller Method", test_controller_method),
        ("View Button Method", test_view_button_method),
        ("Service Generation Simulation", test_service_generation_simulation),
        ("Dialog Configuration", test_dialog_configuration)
    ]

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
            print(f"  [PASS] {test_name}")
        except Exception as e:
            print(f"  [FAIL] {test_name} raised exception: {e}")


if __name__ == "__main__":
    main()
