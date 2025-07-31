#!/usr/bin/env python3
"""
Debug script to test inventario module instantiation and find specific errors
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_inventario_instantiation():
    """Test inventario module creation step by step"""
    try:
        print("=== DEBUGGING INVENTARIO MODULE ===")
        
        # Test PyQt6 import
        print("1. Testing PyQt6...")
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        print("   ✅ PyQt6 imported successfully")
        
        # Test inventario imports
        print("2. Testing inventario imports...")
        from src.modules.inventario.model import InventarioModel
        from src.modules.inventario.view import InventarioView
        from src.modules.inventario.controller import InventarioController
        print("   ✅ Inventario modules imported successfully")
        
        # Test model creation
        print("3. Testing model creation...")
        model = InventarioModel()
        print("   ✅ InventarioModel created successfully")
        
        # Test view creation
        print("4. Testing view creation...")
        view = InventarioView()
        print("   ✅ InventarioView created successfully")
        
        # Test controller creation
        print("5. Testing controller creation...")
        controller = InventarioController(model, view)
        print("   ✅ InventarioController created successfully")
        
        # Test signal connections
        print("6. Testing signal connections...")
        if hasattr(view, 'set_controller'):
            view.set_controller(controller)
            print("   ✅ Controller set on view successfully")
        else:
            print("   ⚠️  View has no set_controller method")
        
        # Check for specific methods
        print("7. Checking for specific methods...")
        methods_to_check = ['filtrar_inventario_tiempo_real', 'filtrar_disponibilidad', 'buscar_productos']
        for method in methods_to_check:
            if hasattr(view, method):
                print(f"   ✅ View has method: {method}")
            else:
                print(f"   ❌ View missing method: {method}")
        
        print("\n=== INVENTARIO MODULE DEBUG COMPLETE ===")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pedidos_debug():
    """Test pedidos module for rollback error"""
    try:
        print("\n=== DEBUGGING PEDIDOS MODULE ===")
        
        from src.modules.pedidos.model import PedidosModel
        from src.modules.pedidos.view import PedidosView
        from src.modules.pedidos.controller import PedidosController
        
        model = PedidosModel()
        view = PedidosView()
        controller = PedidosController(model, view)
        
        # Check for rollback method
        if hasattr(view, 'rollback'):
            print("   ✅ PedidosView has rollback method")
        else:
            print("   ❌ PedidosView missing rollback method")
            
        print("=== PEDIDOS MODULE DEBUG COMPLETE ===")
        return True
        
    except Exception as e:
        print(f"❌ PEDIDOS ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_inventario_instantiation()
    success2 = test_pedidos_debug()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Check errors above.")