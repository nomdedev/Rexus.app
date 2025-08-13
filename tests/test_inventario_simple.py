#!/usr/bin/env python3
"""
Test simple para el módulo inventario después de las correcciones de DataSanitizer
"""

import sys
import os
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_inventario_import():
    """Test que el módulo inventario se importe correctamente."""
    try:
        from rexus.modules.inventario.view import InventarioView
        print("OK - InventarioView importado correctamente")
        return True
    except Exception as e:
        print(f"ERROR - Error al importar InventarioView: {e}")
        return False

def test_inventario_submodules():
    """Test que los submódulos del inventario funcionen."""
    try:
        from rexus.modules.inventario.submodules.consultas_manager import ConsultasManager
        from rexus.modules.inventario.submodules.categorias_manager import CategoriasManager
        from rexus.modules.inventario.submodules.reportes_manager import ReportesManager
        from rexus.modules.inventario.submodules.reservas_manager import ReservasManager
        
        print("OK - Todos los submodulos importados correctamente")
        return True
    except Exception as e:
        print(f"ERROR - Error al importar submodulos: {e}")
        return False

def test_data_sanitizer():
    """Test que el DataSanitizer funcione en los submódulos."""
    try:
        from rexus.modules.inventario.submodules.consultas_manager import ConsultasManager
        
        # Crear instancia sin conexión DB para test
        manager = ConsultasManager()
        
        # Verificar que tenga sanitizer
        if hasattr(manager, 'sanitizer'):
            print("OK - ConsultasManager tiene sanitizer configurado")
            
            # Test básico de sanitización
            if hasattr(manager.sanitizer, 'sanitize_string'):
                result = manager.sanitizer.sanitize_string("test string")
                print(f"OK - Sanitizacion funciona: '{result}'")
                return True
            else:
                print("ERROR - Sanitizer no tiene metodo sanitize_string")
                return False
        else:
            print("ERROR - ConsultasManager no tiene sanitizer")
            return False
    except Exception as e:
        print(f"ERROR - Error al probar DataSanitizer: {e}")
        return False

def run_tests():
    """Ejecuta todos los tests."""
    print("=== TESTS DEL MÓDULO INVENTARIO ===")
    print()
    
    tests = [
        ("Import InventarioView", test_inventario_import),
        ("Import Submódulos", test_inventario_submodules),  
        ("DataSanitizer funcionando", test_data_sanitizer)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Test: {name}")
        result = test_func()
        results.append(result)
        print()
    
    # Resumen
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"RESUMEN: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("OK - TODOS LOS TESTS PASARON")
        print("OK - Modulo inventario funcionando correctamente")
    else:
        print("ERROR - ALGUNOS TESTS FALLARON")
    
    return passed == total

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)