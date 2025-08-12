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
    
    try:
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
            if hasattr(integration, method):
                print(f"[OK] Método '{method}' disponible")
            else:
                print(f"[ERROR] Método '{method}' faltante")
                return False
                
        # Test 4: Probar resumen sin BD
        print("[4/4] Probando obtener resumen...")
        resumen = integration.obtener_resumen_integracion()
        if isinstance(resumen, dict):
            print(f"[OK] Resumen obtenido: {len(resumen)} claves")
            expected_keys = ['herrajes_total', 'herrajes_en_inventario', 'reservas_activas', 'valor_total_herrajes', 'discrepancias']
            for key in expected_keys:
                if key in resumen:
                    print(f"  [OK] {key}: {resumen[key]}")
                else:
                    print(f"  [ERROR] {key} faltante")
        else:
            print("[ERROR] Resumen no es un diccionario")
            return False
        
        print("\n[SUCCESS] Todas las importaciones y métodos básicos funcionan")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_controller_integration():
    """Prueba la integración en el controlador."""
    print("\n[TEST] Verificando integración en controlador")
    print("=" * 50)
    
    try:
        print("[1/3] Importando controlador...")
        from rexus.modules.herrajes.controller import HerrajesController
        print("[OK] HerrajesController importado")
        
        print("[2/3] Creando controlador sin vista...")
        # Crear controlador sin vista para evitar PyQt6
        controller = HerrajesController(view=None, db_connection=None)
        print("[OK] Controlador creado")
        
        print("[3/3] Verificando métodos de integración...")
        integration_methods = [
            'sincronizar_con_inventario',
            'transferir_a_inventario',
            'crear_reserva_para_obra', 
            'mostrar_resumen_integracion',
            'corregir_discrepancias',
            'get_integration_service'
        ]
        
        for method in integration_methods:
            if hasattr(controller, method):
                print(f"[OK] Método '{method}' disponible en controlador")
            else:
                print(f"[ERROR] Método '{method}' faltante en controlador")
                return False
                
        # Verificar que el servicio de integración existe
        if hasattr(controller, 'integracion_inventario'):
            print("[OK] Servicio de integración disponible en controlador")
            service = controller.get_integration_service()
            if service is not None:
                print("[OK] get_integration_service() retorna instancia válida")
            else:
                print("[ERROR] get_integration_service() retorna None")
                return False
        else:
            print("[ERROR] Servicio de integración no disponible en controlador")
            return False
        
        print("\n[SUCCESS] Integración del controlador funciona correctamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test controlador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_view_methods():
    """Prueba solo los métodos de la vista sin crear widgets."""
    print("\n[TEST] Verificando métodos de vista (sin crear widgets)")
    print("=" * 50)
    
    try:
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
            if hasattr(HerrajesView, method):
                print(f"[OK] Método '{method}' definido en HerrajesView")
            else:
                print(f"[ERROR] Método '{method}' no definido en HerrajesView")
                return False
        
        print("\n[SUCCESS] Métodos de integración definidos en vista")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verificando vista: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal del test."""
    print("[START] TEST INTEGRACIÓN HERRAJES-INVENTARIO (SIMPLIFICADO)")
    print("=" * 60)
    
    tests_results = []
    
    # Test 1: Importaciones y servicio básico
    print("\n1. SERVICIO DE INTEGRACIÓN")
    tests_results.append(test_integration_imports())
    
    # Test 2: Integración en controlador  
    print("\n2. CONTROLADOR CON INTEGRACIÓN")
    tests_results.append(test_controller_integration())
    
    # Test 3: Métodos en vista
    print("\n3. MÉTODOS DE VISTA")
    tests_results.append(test_view_methods())
    
    # Resumen
    print("\n" + "=" * 60)
    print("[SUMMARY] RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = sum(tests_results)
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