#!/usr/bin/env python3
"""
Debug actual de carga de módulos para identificar problemas específicos
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def debug_module_loading():
    """Debug detallado de la carga de módulos"""
    print("=== DEBUG MODULE LOADING ISSUES ===\n")
    
    try:
        from core.database import InventarioDatabaseConnection
        
        # Test database connection
        print("1. Testing database connection...")
        db = InventarioDatabaseConnection()
        db.connect()
        print("   Database: OK")
        
        # Test each module individually
        modules_to_test = [
            ("inventario", "Inventario"),
            ("obras", "Obras"), 
            ("herrajes", "Herrajes"),
            ("vidrios", "Vidrios"),
            ("logistica", "Logística"),
            ("pedidos", "Pedidos"),
            ("configuracion", "Configuración"),
            ("administracion", "Administración"),
            ("compras", "Compras"),
            ("mantenimiento", "Mantenimiento"),
            ("auditoria", "Auditoría"),
            ("usuarios", "Usuarios")
        ]
        
        print("\n2. Testing individual module imports...")
        working_modules = []
        broken_modules = []
        
        for module_folder, module_name in modules_to_test:
            try:
                print(f"\n   Testing {module_name} ({module_folder})...")
                
                # Test model import
                try:
                    model_module = __import__(f'modules.{module_folder}.model', fromlist=[''])
                    print(f"     Model: OK")
                except ImportError as e:
                    print(f"     Model: ERROR - {e}")
                    broken_modules.append((module_name, f"Model import: {e}"))
                    continue
                
                # Test controller import  
                try:
                    controller_module = __import__(f'modules.{module_folder}.controller', fromlist=[''])
                    print(f"     Controller: OK")
                except ImportError as e:
                    print(f"     Controller: ERROR - {e}")
                    broken_modules.append((module_name, f"Controller import: {e}"))
                    continue
                
                # Test view import (might not exist for all modules)
                try:
                    view_module = __import__(f'modules.{module_folder}.view', fromlist=[''])
                    print(f"     View: OK")
                except ImportError as e:
                    print(f"     View: WARNING - {e} (might be optional)")
                
                # Test module manager loading
                try:
                    from core.module_manager import ModuleManager
                    mm = ModuleManager()  # No parameters needed
                    
                    # Get module classes
                    model_class = getattr(model_module, f"{module_name.replace(' ', '').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')}Model")
                    controller_class = getattr(controller_module, f"{module_name.replace(' ', '').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')}Controller")
                    
                    # Try to get view class (might not exist)
                    try:
                        view_class = getattr(view_module, f"{module_name.replace(' ', '').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')}View")
                    except:
                        view_class = None
                    
                    print(f"     Classes found: {model_class.__name__}, {controller_class.__name__}")
                    
                    # Try to load with module manager
                    controller = mm.load_module(module_folder, model_class, controller_class, view_class, db)
                    if controller:
                        print(f"     Module Manager: OK")
                        working_modules.append(module_name)
                    else:
                        print(f"     Module Manager: FAILED")
                        broken_modules.append((module_name, "Module manager failed to load"))
                        
                except Exception as e:
                    print(f"     Module Manager: ERROR - {e}")
                    broken_modules.append((module_name, f"Module manager error: {e}"))
                    
            except Exception as e:
                print(f"     CRITICAL ERROR: {e}")
                broken_modules.append((module_name, f"Critical error: {e}"))
        
        print(f"\n3. RESULTS:")
        print(f"   Working modules ({len(working_modules)}): {', '.join(working_modules)}")
        print(f"   Broken modules ({len(broken_modules)}):")
        for module_name, error in broken_modules:
            print(f"     - {module_name}: {error}")
        
        # Test security manager and permissions
        print(f"\n4. Testing permissions system...")
        try:
            from core.security import SecurityManager
            sm = SecurityManager()
            sm.current_role = 'ADMIN'
            sm.current_user = {'id': 1, 'username': 'admin', 'rol': 'ADMIN'}
            
            modules = sm.get_user_modules(1)
            print(f"   Modules allowed for admin: {len(modules)}")
            print(f"   Module list: {modules}")
            
        except Exception as e:
            print(f"   Permissions ERROR: {e}")
        
        db.disconnect()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_module_loading()