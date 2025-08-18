#!/usr/bin/env python3
"""
Deep Module Diagnostics Tool for Rexus.app
Identifies actual production failures, not just import issues
"""

import sys
import os
import traceback
from pathlib import Path

# Setup environment
sys.path.insert(0, str(Path(__file__).parent))

def analyze_module_factory_failures():
    """Test actual module creation as the main app does it"""
    print("=== DEEP MODULE FACTORY ANALYSIS ===")
    
    # Import the actual main app components
    from rexus.main.app import MainWindow
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # Create QApplication (required for widgets)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create realistic user data (as the real app does)
    user_data = {
        'id': 1, 
        'username': 'admin', 
        'rol': 'ADMIN',
        'nombre': 'Test Admin',
        'email': 'admin@test.com'
    }
    
    modulos_permitidos = [
        'Inventario', 'Obras', 'Administración', 'Logística', 'Herrajes', 
        'Vidrios', 'Pedidos', 'Usuarios', 'Configuración', 'Compras', 
        'Mantenimiento', 'Auditoría'
    ]
    
    results = {}
    
    try:
        # Create MainWindow exactly as the real app does
        print("Creating MainWindow with real parameters...")
        main_window = MainWindow(user_data, modulos_permitidos)
        print("MainWindow created successfully")
        
        # Test each module factory method
        for module_name in modulos_permitidos:
            print(f"\n=== TESTING MODULE: {module_name} ===")
            
            try:
                # Call the actual factory method that the app uses
                widget = main_window._create_module_widget(module_name)
                
                if widget is None:
                    results[module_name] = {
                        'status': 'FALLBACK',
                        'error': 'Factory returned None - fallback widget created',
                        'widget_type': 'None'
                    }
                    print(f"[FALLBACK] {module_name}: Factory returned None (FALLBACK)")
                else:
                    results[module_name] = {
                        'status': 'SUCCESS',
                        'error': None,
                        'widget_type': type(widget).__name__
                    }
                    print(f"[SUCCESS] {module_name}: Widget created - {type(widget).__name__}")
                    
                    # Clean up widget
                    widget.deleteLater()
                    
            except Exception as e:
                error_msg = str(e)
                stack_trace = traceback.format_exc()
                results[module_name] = {
                    'status': 'ERROR',
                    'error': error_msg,
                    'stack_trace': stack_trace,
                    'widget_type': None
                }
                print(f"[ERROR] {module_name}: ERROR - {error_msg}")
                print(f"Stack trace: {stack_trace}")
        
        # Clean up
        main_window.deleteLater()
        
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to create MainWindow - {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return None
    
    return results

def analyze_fallback_conditions():
    """Analyze when and why modules fall back to placeholder widgets"""
    print("\n=== FALLBACK CONDITIONS ANALYSIS ===")
    
    # Read the main app file to understand fallback logic
    try:
        app_file = Path("rexus/main/app.py")
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for fallback patterns
        fallback_patterns = [
            "_create_fallback_module",
            "except Exception",
            "return None",
            "QWidget()",
            "fallback"
        ]
        
        print("Fallback patterns found in main app:")
        for pattern in fallback_patterns:
            count = content.count(pattern)
            if count > 0:
                print(f"  {pattern}: {count} occurrences")
                
    except Exception as e:
        print(f"Error analyzing fallback conditions: {e}")

def test_individual_module_components():
    """Test each module's components individually to find root causes"""
    print("\n=== INDIVIDUAL COMPONENT TESTING ===")
    
    modules = [
        'inventario', 'obras', 'herrajes', 'vidrios', 'pedidos', 
        'usuarios', 'compras', 'configuracion', 'auditoria', 
        'logistica', 'mantenimiento'
    ]
    
    component_results = {}
    
    for module in modules:
        print(f"\n--- Testing {module.upper()} components ---")
        
        component_results[module] = {
            'model': {'status': 'UNKNOWN', 'error': None},
            'view': {'status': 'UNKNOWN', 'error': None},
            'controller': {'status': 'UNKNOWN', 'error': None}
        }
        
        # Test Model
        try:
            model_module = __import__(f"rexus.modules.{module}.model", fromlist=[""])
            # Try to find the model class
            model_classes = [attr for attr in dir(model_module) if 'Model' in attr and not attr.startswith('_')]
            if model_classes:
                model_class = getattr(model_module, model_classes[0])
                model_instance = model_class()
                component_results[module]['model'] = {'status': 'SUCCESS', 'error': None, 'class': model_classes[0]}
                print(f"  [OK] Model: {model_classes[0]}")
            else:
                component_results[module]['model'] = {'status': 'ERROR', 'error': 'No model class found'}
                print(f"  [ERROR] Model: No model class found")
        except Exception as e:
            component_results[module]['model'] = {'status': 'ERROR', 'error': str(e)}
            print(f"  [FAIL] Model: {e}")
        
        # Test View
        try:
            view_module = __import__(f"rexus.modules.{module}.view", fromlist=[""])
            view_classes = [attr for attr in dir(view_module) if 'View' in attr and not attr.startswith('_')]
            if view_classes:
                view_class = getattr(view_module, view_classes[0])
                # Don't instantiate view without QApplication context
                component_results[module]['view'] = {'status': 'SUCCESS', 'error': None, 'class': view_classes[0]}
                print(f"  [OK] View: {view_classes[0]}")
            else:
                component_results[module]['view'] = {'status': 'ERROR', 'error': 'No view class found'}
                print(f"  [ERROR] View: No view class found")
        except Exception as e:
            component_results[module]['view'] = {'status': 'ERROR', 'error': str(e)}
            print(f"  [FAIL] View: {e}")
        
        # Test Controller
        try:
            controller_module = __import__(f"rexus.modules.{module}.controller", fromlist=[""])
            controller_classes = [attr for attr in dir(controller_module) if 'Controller' in attr and not attr.startswith('_')]
            if controller_classes:
                controller_class = getattr(controller_module, controller_classes[0])
                component_results[module]['controller'] = {'status': 'SUCCESS', 'error': None, 'class': controller_classes[0]}
                print(f"  [OK] Controller: {controller_classes[0]}")
            else:
                component_results[module]['controller'] = {'status': 'ERROR', 'error': 'No controller class found'}
                print(f"  [ERROR] Controller: No controller class found")
        except Exception as e:
            component_results[module]['controller'] = {'status': 'ERROR', 'error': str(e)}
            print(f"  [FAIL] Controller: {e}")
    
    return component_results

def generate_comprehensive_report(factory_results, component_results):
    """Generate detailed report with actionable fixes"""
    print("\n" + "="*80)
    print("COMPREHENSIVE DIAGNOSTIC REPORT")
    print("="*80)
    
    if factory_results:
        print("\n📊 FACTORY RESULTS SUMMARY:")
        success_count = sum(1 for r in factory_results.values() if r['status'] == 'SUCCESS')
        fallback_count = sum(1 for r in factory_results.values() if r['status'] == 'FALLBACK')
        error_count = sum(1 for r in factory_results.values() if r['status'] == 'ERROR')
        
        print(f"  [OK] Working: {success_count}")
        print(f"  [WARN] Fallback: {fallback_count}")
        print(f"  [ERROR] Errors: {error_count}")
        
        print("\nMODULES REQUIRING FIXES:")
        for module, result in factory_results.items():
            if result['status'] != 'SUCCESS':
                print(f"  {module}: {result['status']} - {result['error']}")
    
    if component_results:
        print("\nCOMPONENT ANALYSIS:")
        for module, components in component_results.items():
            errors = [comp for comp, data in components.items() if data['status'] == 'ERROR']
            if errors:
                print(f"  {module.upper()}: Issues with {', '.join(errors)}")
                for comp in errors:
                    print(f"    {comp}: {components[comp]['error']}")
    
    print("\nRECOMMENDED ACTIONS:")
    print("1. Fix module factory methods that return None")
    print("2. Ensure all MVC components exist and are importable")
    print("3. Add proper error handling in module creation")
    print("4. Create comprehensive integration tests")
    print("5. Implement graceful degradation instead of fallbacks")

def main():
    """Run comprehensive diagnostics"""
    print("REXUS.APP - DEEP MODULE DIAGNOSTICS")
    print("Analyzing real production failures...\n")
    
    # Run diagnostics
    analyze_fallback_conditions()
    component_results = test_individual_module_components()
    factory_results = analyze_module_factory_failures()
    
    # Generate report
    generate_comprehensive_report(factory_results, component_results)
    
    return factory_results, component_results

if __name__ == "__main__":
    factory_results, component_results = main()