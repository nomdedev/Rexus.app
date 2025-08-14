#!/usr/bin/env python3
"""
Simple debug script to test module instantiation without Unicode issues
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_inventario_simple():
    """Test inventario module creation"""
    try:
        print("=== TESTING INVENTARIO MODULE ===")

        # Test PyQt6 import
        print("1. Testing PyQt6...")
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        print("   OK: PyQt6 imported successfully")

        # Test inventario imports
        print("2. Testing inventario imports...")
        from src.modules.inventario.model import InventarioModel
        from src.modules.inventario.view import InventarioView
        from src.modules.inventario.controller import InventarioController
        print("   OK: Inventario modules imported successfully")

        # Test model creation
        print("3. Testing model creation...")
        model = InventarioModel()
        print("   OK: InventarioModel created successfully")

        # Test view creation
        print("4. Testing view creation...")
        view = InventarioView()
        print("   OK: InventarioView created successfully")

        # Test controller creation
        print("5. Testing controller creation...")
        controller = InventarioController(model, view)
        print("   OK: InventarioController created successfully")

        # Check for specific methods
        print("6. Checking for specific methods...")
        methods_to_check = ['filtrar_inventario_tiempo_real', 'filtrar_disponibilidad', 'buscar_productos']
        for method in methods_to_check:
            if hasattr(view, method):
                print(f"   OK: View has method: {method}")
            else:
                print(f"   MISSING: View missing method: {method}")

        # Check controller methods
        print("7. Checking controller methods...")
        controller_methods = ['conectar_señales', 'cargar_inventario', 'buscar_productos']
        for method in controller_methods:
            if hasattr(controller, method):
                print(f"   OK: Controller has method: {method}")
            else:
                print(f"   MISSING: Controller missing method: {method}")

        print("=== INVENTARIO MODULE TEST COMPLETE ===")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inventario_simple()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed.")
