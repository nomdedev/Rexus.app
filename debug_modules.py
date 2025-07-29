#!/usr/bin/env python3
"""
Debug script to test module loading issues
"""

import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    print("Testing PyQt6 import...")
    from PyQt6.QtWidgets import QApplication, QWidget
    print("[OK] PyQt6 import successful")
    
    print("Testing app creation...")
    app = QApplication([])
    print("[OK] QApplication created")
    
    print("Testing module imports...")
    
    # Test inventario module
    try:
        from src.modules.inventario.model import InventarioModel
        from src.modules.inventario.view import InventarioView
        from src.modules.inventario.controller import InventarioController
        print("[OK] Inventario module imports successful")
    except Exception as e:
        print(f"[ERROR] Inventario module import error: {e}")
    
    # Test usuarios module
    try:
        from src.modules.usuarios.model import UsuariosModel
        from src.modules.usuarios.view import UsuariosView
        from src.modules.usuarios.controller import UsuariosController
        print("[OK] Usuarios module imports successful")
    except Exception as e:
        print(f"[ERROR] Usuarios module import error: {e}")
    
    # Test pedidos module
    try:
        from src.modules.pedidos.model import PedidosModel
        from src.modules.pedidos.view import PedidosView
        from src.modules.pedidos.controller import PedidosController
        print("[OK] Pedidos module imports successful")
    except Exception as e:
        print(f"[ERROR] Pedidos module import error: {e}")
        
    # Test compras module
    try:
        from src.modules.compras.model import ComprasModel
        from src.modules.compras.view import ComprasView
        from src.modules.compras.controller import ComprasController
        print("[OK] Compras module imports successful")
    except Exception as e:
        print(f"[ERROR] Compras module import error: {e}")
        
    # Test configuracion module
    try:
        from src.modules.configuracion.model import ConfiguracionModel
        from src.modules.configuracion.view import ConfiguracionView
        from src.modules.configuracion.controller import ConfiguracionController
        print("[OK] Configuracion module imports successful")
    except Exception as e:
        print(f"[ERROR] Configuracion module import error: {e}")
    
    print("Testing module instantiation...")
    
    # Test inventario instantiation
    try:
        model = InventarioModel()
        view = InventarioView()
        controller = InventarioController(model, view)
        print("[OK] Inventario module instantiation successful")
    except Exception as e:
        print(f"[ERROR] Inventario module instantiation error: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"[CRITICAL] Critical error: {e}")
    import traceback
    traceback.print_exc()