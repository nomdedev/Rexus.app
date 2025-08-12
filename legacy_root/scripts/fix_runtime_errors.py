#!/usr/bin/env python3
"""
Script para identificar y corregir errores críticos de runtime en módulos
Rexus.app - Corrección de Errores Runtime
"""

import sys
import importlib
from pathlib import Path

def test_module_imports():
    """Prueba las importaciones de todos los módulos para identificar errores."""
    modules_to_test = [
        'obras', 'inventario', 'vidrios', 'logistica', 'pedidos', 
        'compras', 'administracion', 'mantenimiento', 'auditoria', 'configuracion'
    ]
    
    results = {
        'success': [],
        'errors': []
    }
    
    for module_name in modules_to_test:
        print(f"\n=== Testing {module_name} ===")
        
        # Test Model
        try:
            model_module = importlib.import_module(f'rexus.modules.{module_name}.model')
            model_class_name = f'{module_name.title()}Model'
            if hasattr(model_module, model_class_name):
                model_class = getattr(model_module, model_class_name)
                print(f"[OK] Model: {model_class}")
                results['success'].append(f"{module_name}.model")
            else:
                print(f"[ERROR] Model class {model_class_name} not found in {module_name}.model")
                results['errors'].append(f"{module_name}.model: Class {model_class_name} not found")
        except Exception as e:
            print(f"[ERROR] Model import failed: {e}")
            results['errors'].append(f"{module_name}.model: {str(e)}")
        
        # Test View
        try:
            view_module = importlib.import_module(f'rexus.modules.{module_name}.view')
            view_class_name = f'{module_name.title()}View'
            if hasattr(view_module, view_class_name):
                view_class = getattr(view_module, view_class_name)
                print(f"[OK] View: {view_class}")
                results['success'].append(f"{module_name}.view")
            else:
                print(f"[ERROR] View class {view_class_name} not found in {module_name}.view")
                results['errors'].append(f"{module_name}.view: Class {view_class_name} not found")
        except Exception as e:
            print(f"[ERROR] View import failed: {e}")
            results['errors'].append(f"{module_name}.view: {str(e)}")
        
        # Test Controller
        try:
            controller_module = importlib.import_module(f'rexus.modules.{module_name}.controller')
            controller_class_name = f'{module_name.title()}Controller'
            if hasattr(controller_module, controller_class_name):
                controller_class = getattr(controller_module, controller_class_name)
                print(f"[OK] Controller: {controller_class}")
                results['success'].append(f"{module_name}.controller")
            else:
                print(f"[ERROR] Controller class {controller_class_name} not found in {module_name}.controller")
                results['errors'].append(f"{module_name}.controller: Class {controller_class_name} not found")
        except Exception as e:
            print(f"[ERROR] Controller import failed: {e}")
            results['errors'].append(f"{module_name}.controller: {str(e)}")
    
    return results

def test_view_instantiation():
    """Prueba la instanciación de vistas para identificar errores runtime."""
    modules_to_test = [
        'obras', 'inventario', 'vidrios', 'logistica', 'pedidos', 
        'compras', 'administracion', 'mantenimiento', 'auditoria', 'configuracion'
    ]
    
    results = {
        'success': [],
        'errors': []
    }
    
    for module_name in modules_to_test:
        print(f"\n=== Testing {module_name} View Instantiation ===")
        
        try:
            # Import view module
            view_module = importlib.import_module(f'rexus.modules.{module_name}.view')
            view_class_name = f'{module_name.title()}View'
            
            if hasattr(view_module, view_class_name):
                view_class = getattr(view_module, view_class_name)
                
                # Try to instantiate (this is where runtime errors occur)
                view_instance = view_class()
                print(f"[OK] {module_name} view instantiated successfully")
                results['success'].append(module_name)
                
                # Clean up
                del view_instance
                
            else:
                print(f"[ERROR] View class {view_class_name} not found")
                results['errors'].append(f"{module_name}: Class {view_class_name} not found")
                
        except Exception as e:
            print(f"[ERROR] {module_name} view instantiation failed: {e}")
            results['errors'].append(f"{module_name}: {str(e)}")
            
            # Print traceback for debugging
            import traceback
            traceback.print_exc()
    
    return results

def main():
    """Función principal."""
    print("=== DIAGNÓSTICO DE ERRORES RUNTIME ===")
    print("Identificando errores críticos en módulos...")
    
    # Test 1: Import test
    print("\n" + "="*60)
    print("FASE 1: Testing module imports")
    print("="*60)
    import_results = test_module_imports()
    
    # Test 2: View instantiation test
    print("\n" + "="*60) 
    print("FASE 2: Testing view instantiation")
    print("="*60)
    instantiation_results = test_view_instantiation()
    
    # Summary
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    print(f"\\nImportaciones exitosas: {len(import_results['success'])}")
    for success in import_results['success']:
        print(f"  [OK] {success}")
    
    print(f"\\nErrores de importación: {len(import_results['errors'])}")
    for error in import_results['errors']:
        print(f"  ✗ {error}")
    
    print(f"\\nVistas instanciadas exitosamente: {len(instantiation_results['success'])}")
    for success in instantiation_results['success']:
        print(f"  [OK] {success}")
    
    print(f"\\nErrores de instanciación: {len(instantiation_results['errors'])}")
    for error in instantiation_results['errors']:
        print(f"  ✗ {error}")
    
    total_errors = len(import_results['errors']) + len(instantiation_results['errors'])
    if total_errors == 0:
        print("\\n🎉 ¡Todos los módulos funcionan correctamente!")
        return 0
    else:
        print(f"\\n[WARN] Se encontraron {total_errors} errores que requieren corrección")
        return 1

if __name__ == "__main__":
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    exit(main())