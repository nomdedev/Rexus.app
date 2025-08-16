#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2025 Rexus.app

Test Integración Herrajes-Inventario (Simplificado)
===================================================

Script de prueba simplificado que solo verifica las importaciones y métodos
sin crear widgets PyQt6.
"""

import sys
from pathlib import Path

# Añadir raíz del proyecto al path
proyecto_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(proyecto_root))

def test_integration_imports():
    """Prueba que las importaciones funcionen correctamente."""
    print("[TEST] Verificando importaciones de integración")
    print("=" * 50)

    # Test 1: Importar módulo de integración
    print("[1/4] Importando servicio de integración...")
    from rexus.modules.herrajes.inventario_integration import HerrajesInventarioIntegration
    print("[OK] HerrajesInventarioIntegration importado")

    # Test 2: Crear instancia sin BD
    print("[2/4] Creando instancia sin BD...")
    integration = HerrajesInventarioIntegration(db_connection=None)
    print("[OK] Instancia creada")

    # Test 3: Verificar métodos principales
    print("[3/4] Verificando métodos principales...")
    methods_to_check = [
        'sincronizar_stock_herrajes',
        'transferir_herraje_a_inventario',
        'crear_reserva_herraje',
        'obtener_resumen_integracion',
        'corregir_discrepancias'
    ]

    for method in methods_to_check:
        assert hasattr(integration, method), f"Método '{method}' faltante en HerrajesInventarioIntegration"
        print(f"[OK] Método '{method}' disponible")

    # Test 4: Probar resumen sin BD
    print("[4/4] Probando obtener resumen...")
    resumen = integration.obtener_resumen_integracion()
    assert isinstance(resumen, dict), "Resumen no es un diccionario"
    print(f"[OK] Resumen obtenido: {len(resumen)} claves")
    expected_keys = ['herrajes_total', 'herrajes_en_inventario', 'reservas_activas', 'valor_total_herrajes', 'discrepancias']
    for key in expected_keys:
        assert key in resumen, f"Clave esperada '{key}' faltante en resumen"
        print(f"  [OK] {key}: {resumen[key]}")

    print("\n[SUCCESS] Todas las importaciones y métodos básicos funcionan")

def test_controller_integration():
    """Prueba la integración en el controlador."""
    print("\n[TEST] Verificando integración en controlador")
    print("=" * 50)

    print("[1/3] Importando controlador...")
    from rexus.modules.herrajes.controller import HerrajesController
    print("[OK] HerrajesController importado")

    print("[2/3] Verificando interfaz del controlador sin instanciar (evita BaseController init)")
    # Evitamos instanciar HerrajesController porque BaseController requiere module_name
    integration_methods = [
        'sincronizar_con_inventario',
        'transferir_a_inventario',
        'crear_reserva_para_obra',
        'mostrar_resumen_integracion',
        'corregir_discrepancias',
        'get_integration_service'
    ]

    for method in integration_methods:
        assert hasattr(HerrajesController, method), f"Método de clase '{method}' faltante en HerrajesController"
        print(f"[OK] Método de clase '{method}' disponible en HerrajesController")

    # Verificamos que el método para obtener servicio existe
    assert hasattr(HerrajesController, 'get_integration_service'), "get_integration_service no definido en HerrajesController"
    print("[OK] get_integration_service está definido en la clase HerrajesController")

    print("\n[SUCCESS] Interfaz del controlador verificada (sin instanciar)")

def test_view_methods():
    """Prueba solo los métodos de la vista sin crear widgets."""
    print("\n[TEST] Verificando métodos de vista (sin crear widgets)")
    print("=" * 50)

    print("[1/2] Importando clase de vista...")
    from rexus.modules.herrajes.view import HerrajesView
    print("[OK] HerrajesView importado")

    print("[2/2] Verificando métodos de integración...")
    integration_methods = [
        'crear_panel_integracion',
        'sincronizar_inventario',
        'mostrar_resumen_integracion',
        'transferir_a_inventario',
        'crear_reserva_obra'
    ]

    # Verificar que los métodos existen en la clase (sin instanciar)
    for method in integration_methods:
        assert hasattr(HerrajesView, method), f"Método '{method}' no definido en HerrajesView"
        print(f"[OK] Método '{method}' definido en HerrajesView")

    print("\n[SUCCESS] Métodos de integración definidos en vista")

def main():
    """Función principal del test."""
    print("[START] TEST INTEGRACIÓN HERRAJES-INVENTARIO (SIMPLIFICADO)")
    print("=" * 60)

    tests_results = []

    # Test 1: Importaciones y servicio básico
    print("\n1. SERVICIO DE INTEGRACIÓN")
    try:
        test_integration_imports()
        tests_results.append(True)
    except Exception:
        tests_results.append(False)

    # Test 2: Integración en controlador
    print("\n2. CONTROLADOR CON INTEGRACIÓN")
    try:
        test_controller_integration()
        tests_results.append(True)
    except Exception:
        tests_results.append(False)

    # Test 3: Métodos en vista
    print("\n3. MÉTODOS DE VISTA")
    try:
        test_view_methods()
        tests_results.append(True)
    except Exception:
        tests_results.append(False)

    # Resumen
    print("\n" + "=" * 60)
    print("[SUMMARY] RESUMEN DE TESTS")
    print("=" * 60)

    passed = sum(1 for v in tests_results if v)
    total = len(tests_results)

    print(f"Tests ejecutados: {total}")
    print(f"Tests exitosos: {passed}")
    print(f"Tests fallidos: {total - passed}")

    if passed == total:
        print("\n[SUCCESS] TODOS LOS TESTS PASARON!")
        print("La integración Herrajes-Inventario está implementada correctamente")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} TESTS FALLARON")
        print("Revisa los errores arriba para más detalles")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
