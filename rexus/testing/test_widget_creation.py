#!/usr/bin/env python3
"""
Test script to identify specific widget creation issues
"""

import sys
import os
from pathlib import Path

# Setup environment
sys.path.insert(0, str(Path(__file__).parent))

def test_widget_creation():
    """Test creation of individual module widgets"""
    print("TESTING WIDGET CREATION...")
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # Create minimal QApplication for widget testing
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    results = {}
    
    # Test modules one by one
    modules_to_test = [
        ('Inventario', 'rexus.modules.inventario'),
        ('Vidrios', 'rexus.modules.vidrios'), 
        ('Herrajes', 'rexus.modules.herrajes'),
        ('Usuarios', 'rexus.modules.usuarios'),
        ('Pedidos', 'rexus.modules.pedidos'),
        ('Obras', 'rexus.modules.obras'),
        ('Compras', 'rexus.modules.compras'),
        ('Configuracion', 'rexus.modules.configuracion'),
        ('Auditoria', 'rexus.modules.auditoria'),
        ('Logistica', 'rexus.modules.logistica'),
        ('Mantenimiento', 'rexus.modules.mantenimiento')
    ]
    
    for module_name, module_path in modules_to_test:
        print(f"\nTesting {module_name} widget creation...")
        
        try:
            # Import MVC components
            controller_module = __import__(f"{module_path}.controller", fromlist=[f"{module_name}Controller"])
            model_module = __import__(f"{module_path}.model", fromlist=[f"{module_name}Model"])
            view_module = __import__(f"{module_path}.view", fromlist=[f"{module_name}View"])
            
            # Get classes
            controller_class = getattr(controller_module, f"{module_name}Controller")
            
            # Try to get model class with variations
            model_class = None
            for variation in [f"{module_name}Model", f"Modelo{module_name}"]:
                try:
                    model_class = getattr(model_module, variation)
                    break
                except AttributeError:
                    continue
            
            if not model_class:
                raise AttributeError(f"No model class found for {module_name}")
            
            # Try to get view class with variations  
            view_class = None
            for variation in [f"{module_name}View", f"{module_name}ModernView"]:
                try:
                    view_class = getattr(view_module, variation)
                    break
                except AttributeError:
                    continue
            
            if not view_class:
                raise AttributeError(f"No view class found for {module_name}")
            
            print(f"  Classes found: {model_class.__name__}, {view_class.__name__}, {controller_class.__name__}")
            
            # Try to create instances
            model = model_class()
            view = view_class()
            
            # Create controller with correct parameters
            if module_name in ['Usuarios', 'Pedidos', 'Compras']:
                # These controllers require model and view parameters
                controller = controller_class(model, view)
            else:
                # Other controllers can be created without parameters
                controller = controller_class()
            
            print(f"  SUCCESS: {module_name} widgets created successfully")
            results[module_name] = "SUCCESS"
            
            # Clean up
            view.close()
            view.deleteLater()
            
        except Exception as e:
            print(f"  ERROR: {module_name} failed - {e}")
            results[module_name] = f"ERROR: {e}"
    
    # Summary
    print("\n" + "="*50)
    print("WIDGET CREATION RESULTS:")
    print("="*50)
    
    successful = 0
    for module, status in results.items():
        if status == "SUCCESS":
            print(f"[OK] {module}: SUCCESS")
            successful += 1
        else:
            print(f"[ERROR] {module}: {status}")
    
    print(f"\nSuccessful modules: {successful}/{len(results)}")
    
    return results

if __name__ == "__main__":
    results = test_widget_creation()