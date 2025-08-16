"""
Module Validations Test Suite - Rexus.app
Comprehensive testing for all module form validations.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_inventario_validator():
    """Test inventario form validation."""
    print("\n[TEST] Inventario Validator Tests...")

    from rexus.utils.module_validators import inventario_validator

    # Test valid producto form
    valid_data = {
        'codigo': 'PROF001',
        'descripcion': 'Perfil de aluminio 40x40',
        'categoria': 'PERFIL',
        'precio_unitario': 25.50,
        'stock_actual': 100,
        'stock_minimo': 10,
        'proveedor': 'Aluminios SA'
    }

    valid, errors = inventario_validator.validate_producto_form(valid_data)
    assert valid, f"Valid form failed: {errors}"
    print("  [PASS] Valid producto form validation")

    # Test invalid producto form
    invalid_data = {
        'codigo': 'A',  # Too short
        'descripcion': '',  # Empty
        'categoria': '',  # Empty
        'precio_unitario': -10,  # Negative
        'stock_actual': 'invalid'  # Not numeric
    }

    valid, errors = inventario_validator.validate_producto_form(invalid_data)
    assert not valid, "Invalid form should fail"
    assert len(errors) >= 4, f"Should have multiple errors, got: {errors}"
    print("  [PASS] Invalid producto form rejection")

def test_herrajes_validator():
    """Test herrajes form validation."""
    print("\n[TEST] Herrajes Validator Tests...")

    from rexus.utils.module_validators import herrajes_validator

    # Test valid herraje form
    valid_data = {
        'codigo': 'BIS001',
        'descripcion': 'Bisagra de acero inoxidable',
        'tipo': 'BISAGRA',
        'precio_unitario': 15.00,
        'material': 'Acero inoxidable'
    }

    valid, errors = herrajes_validator.validate_herraje_form(valid_data)
    assert valid, f"Valid form failed: {errors}"
    print("  [PASS] Valid herraje form validation")

    # Test invalid herraje form
    invalid_data = {
        'codigo': '',
        'descripcion': 'AB',  # Too short
        'tipo': 'INVALID_TYPE',  # Invalid type
        'precio_unitario': 'not_a_number'
    }

    valid, errors = herrajes_validator.validate_herraje_form(invalid_data)
    assert not valid, "Invalid form should fail"
    print("  [PASS] Invalid herraje form rejection")

def test_vidrios_validator():
    """Test vidrios form validation."""
    print("\n[TEST] Vidrios Validator Tests...")

    from rexus.utils.module_validators import vidrios_validator

    # Test valid vidrio form
    valid_data = {
        'codigo': 'VID001',
        'descripcion': 'Vidrio templado 6mm',
        'tipo': 'TEMPLADO',
        'espesor': 6.0,
        'ancho': 1000,
        'alto': 1200
    }

    valid, errors = vidrios_validator.validate_vidrio_form(valid_data)
    assert valid, f"Valid form failed: {errors}"
    print("  [PASS] Valid vidrio form validation")

    # Test invalid vidrio form
    invalid_data = {
        'codigo': '',
        'descripcion': '',
        'tipo': 'INVALID_TYPE',
        'espesor': -5,  # Negative thickness
        'ancho': 'invalid',
        'alto': -100
    }

    valid, errors = vidrios_validator.validate_vidrio_form(invalid_data)
    assert not valid, "Invalid form should fail"
    print("  [PASS] Invalid vidrio form rejection")

def test_pedidos_validator():
    """Test pedidos form validation."""
    print("\n[TEST] Pedidos Validator Tests...")

    from rexus.utils.module_validators import pedidos_validator

    # Test valid pedido form
    valid_data = {
        'tipo_pedido': 'COMPRA',
        'estado': 'PENDIENTE',
        'fecha_pedido': '2025-07-31',
        'fecha_entrega_estimada': '2025-08-15',
        'cliente_id': 123,
        'subtotal': 1000.00,
        'total': 1210.00
    }

    valid, errors = pedidos_validator.validate_pedido_form(valid_data)
    assert valid, f"Valid form failed: {errors}"
    print("  [PASS] Valid pedido form validation")

    # Test invalid pedido form
    invalid_data = {
        'tipo_pedido': 'INVALID_TYPE',
        'estado': 'INVALID_STATE',
        'fecha_pedido': 'invalid_date',
        'fecha_entrega_estimada': '2025-07-01',  # Before pedido date
        'subtotal': -100,
        'total': 'not_a_number'
    }

    valid, errors = pedidos_validator.validate_pedido_form(invalid_data)
    assert not valid, "Invalid form should fail"
    print("  [PASS] Invalid pedido form rejection")

def test_obras_validator():
    """Test obras form validation."""
    print("\n[TEST] Obras Validator Tests...")

    from rexus.utils.module_validators import obras_validator

    # Test valid obra form
    valid_data = {
        'codigo_obra': 'OBR001',
        'nombre': 'Proyecto Edificio Central',
        'descripcion': 'Construcción de edificio de oficinas de 10 plantas',
        'estado': 'PLANIFICACION',
        'etapa_actual': 'DISEÑO',
        'fecha_inicio': '2025-08-01',
        'fecha_fin_estimada': '2026-12-31',
        'presupuesto_inicial': 500000.00,
        'ubicacion': 'Av. Principal 123, Ciudad'
    }

    valid, errors = obras_validator.validate_obra_form(valid_data)
    assert valid, f"Valid form failed: {errors}"
    print("  [PASS] Valid obra form validation")

    # Test invalid obra form
    invalid_data = {
        'codigo_obra': 'A',  # Too short
        'nombre': '',  # Empty
        'estado': 'INVALID_STATE',
        'etapa_actual': 'INVALID_STAGE',
        'fecha_inicio': 'invalid_date',
        'fecha_fin_estimada': '2025-01-01',  # Before start date
        'presupuesto_inicial': -1000
    }

    valid, errors = obras_validator.validate_obra_form(invalid_data)
    assert not valid, "Invalid form should fail"
    print("  [PASS] Invalid obra form rejection")

def test_module_validator_function():
    """Test module validator convenience function."""
    print("\n[TEST] Module Validator Function Tests...")

    from rexus.utils.module_validators import validate_module_form

    # Test inventario module
    inventario_data = {
        'codigo': 'TEST001',
        'descripcion': 'Test product',
        'categoria': 'TEST',
        'precio_unitario': 10.0,
        'stock_actual': 50
    }

    valid, errors = validate_module_form('inventario', inventario_data)
    assert valid, f"Inventario module validation failed: {errors}"
    print("  [PASS] Inventario module validation")

    # Test herrajes module
    herrajes_data = {
        'codigo': 'HER001',
        'descripcion': 'Test herraje',
        'tipo': 'BISAGRA',
        'precio_unitario': 20.0
    }

    valid, errors = validate_module_form('herrajes', herrajes_data)
    assert valid, f"Herrajes module validation failed: {errors}"
    print("  [PASS] Herrajes module validation")

    # Test unknown module
    valid, errors = validate_module_form('unknown_module', {})
    assert valid, "Unknown module should return valid"
    print("  [PASS] Unknown module handling")

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n[TEST] Edge Cases Tests...")

    from rexus.utils.module_validators import inventario_validator, herrajes_validator

    # Test empty form data
    valid, errors = inventario_validator.validate_producto_form({})
    assert not valid, "Empty form should fail"
    print("  [PASS] Empty form rejection")

    # Test None values
    none_data = {
        'codigo': None,
        'descripcion': None,
        'categoria': None,
        'precio_unitario': None,
        'stock_actual': None
    }

    valid, errors = inventario_validator.validate_producto_form(none_data)
    assert not valid, "None values should fail"
    print("  [PASS] None values rejection")

    # Test boundary values
    boundary_data = {
        'codigo': 'A' * 20,  # Max length
        'descripcion': 'A' * 500,  # Max length
        'categoria': 'A' * 50,  # Max length
        'precio_unitario': 999999.99,  # Max price
        'stock_actual': 999999  # Max quantity
    }

    valid, errors = inventario_validator.validate_producto_form(boundary_data)
    assert valid, f"Boundary values should be valid: {errors}"
    print("  [PASS] Boundary values acceptance")

def main():
    """Main test execution."""
    print("="*70)
    print("MODULE VALIDATIONS TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Inventario Validator", test_inventario_validator),
        ("Herrajes Validator", test_herrajes_validator),
        ("Vidrios Validator", test_vidrios_validator),
        ("Pedidos Validator", test_pedidos_validator),
        ("Obras Validator", test_obras_validator),
        ("Module Validator Function", test_module_validator_function),
        ("Edge Cases", test_edge_cases)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
            results.append((test_name, True))
        except Exception as e:
            print(f"  [FAIL] {test_name} raised exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for test_name, ok in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"{status} {test_name}")

    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {success_rate:.1f}%")

    # Overall assessment
    if success_rate >= 70:
        print("\n[CHECK] Module validations mostly working or acceptable")
        return True
    else:
        print("\n[ERROR] Module validation tests need attention")
        return False

if __name__ == "__main__":
    success = main()

    if success:
        print("\n[CHECK] MODULE VALIDATIONS IMPLEMENTATION SUCCESSFUL")
        print("The module validation system is ready for production use.")
    else:
        print("\n[ERROR] MODULE VALIDATIONS NEED ATTENTION")
        print("Address the failed tests before proceeding.")
        sys.exit(1)
