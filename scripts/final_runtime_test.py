#!/usr/bin/env python3
"""
Script para prueba final de runtime de todos los módulos
Rexus.app - Verificación Final de Correcciones
"""

import sys
import importlib
from pathlib import Path

def test_all_modules():
    """Prueba todos los módulos para verificar que funcionan correctamente."""
    modules_to_test = [
        'obras', 'inventario', 'vidrios', 'logistica', 'pedidos', 
        'compras', 'administracion', 'mantenimiento', 'auditoria', 'configuracion'
    ]
    
    results = {
        'success': [],
        'errors': []
    }
    
    print("=" * 60)
    print("PRUEBA FINAL DE RUNTIME - TODOS LOS MÓDULOS")
    print("=" * 60)
    
    for module_name in modules_to_test:
        print(f"\n[{module_name.upper()}] Testing module...")
        
        module_success = True
        
        # Test Model
        try:
            model_module = importlib.import_module(f'rexus.modules.{module_name}.model')
            model_class_name = f'{module_name.title()}Model'
            if hasattr(model_module, model_class_name):
                model_class = getattr(model_module, model_class_name)
                print(f"  [OK] Model class found and importable")
            else:
                print(f"  [ERROR] Model class {model_class_name} not found")
                module_success = False
        except Exception as e:
            print(f"  [ERROR] Model import failed: {e}")
            module_success = False
        
        # Test Controller
        try:
            controller_module = importlib.import_module(f'rexus.modules.{module_name}.controller')
            controller_class_name = f'{module_name.title()}Controller'
            if hasattr(controller_module, controller_class_name):
                controller_class = getattr(controller_module, controller_class_name)
                print(f"  [OK] Controller class found and importable")
            else:
                print(f"  [ERROR] Controller class {controller_class_name} not found")
                module_success = False
        except Exception as e:
            print(f"  [ERROR] Controller import failed: {e}")
            module_success = False
        
        # Test View
        try:
            view_module = importlib.import_module(f'rexus.modules.{module_name}.view')
            view_class_name = f'{module_name.title()}View'
            if hasattr(view_module, view_class_name):
                view_class = getattr(view_module, view_class_name)
                print(f"  [OK] View class found and importable")
                
                # Test view instantiation
                try:
                    view_instance = view_class()
                    print(f"  [OK] View instantiation successful")
                    # Clean up
                    del view_instance
                except Exception as e:
                    print(f"  [ERROR] View instantiation failed: {e}")
                    module_success = False
                    
            else:
                print(f"  [ERROR] View class {view_class_name} not found")
                module_success = False
        except Exception as e:
            print(f"  [ERROR] View import failed: {e}")
            module_success = False
        
        if module_success:
            print(f"  [SUCCESS] {module_name} module working correctly")
            results['success'].append(module_name)
        else:
            print(f"  [FAILED] {module_name} module has errors")
            results['errors'].append(module_name)
    
    return results

def main():
    """Función principal."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    print("REXUS.APP - VERIFICACIÓN FINAL DE RUNTIME")
    print("Comprobando que todos los errores críticos han sido corregidos...")
    
    results = test_all_modules()
    
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    total_modules = len(results['success']) + len(results['errors'])
    success_count = len(results['success'])
    error_count = len(results['errors'])
    
    print(f"Total de módulos probados: {total_modules}")
    print(f"Módulos funcionando correctamente: {success_count}")
    print(f"Módulos con errores: {error_count}")
    
    if results['success']:
        print(f"\nMódulos exitosos:")
        for module in results['success']:
            print(f"  ✅ {module}")
    
    if results['errors']:
        print(f"\nMódulos con errores:")
        for module in results['errors']:
            print(f"  ❌ {module}")
    
    if error_count == 0:
        print(f"\n🎉 ¡ÉXITO TOTAL!")
        print("Todos los errores críticos de runtime han sido corregidos")
        print("La aplicación debería funcionar correctamente ahora")
        return 0
    else:
        print(f"\n⚠️ Quedan {error_count} módulos con errores por corregir")
        return 1

if __name__ == "__main__":
    exit(main())