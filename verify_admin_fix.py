#!/usr/bin/env python3
"""
Simple verification that admin permissions are fixed
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def verify_admin_permissions():
    """Verify that admin permissions are working"""
    print("=== VERIFYING ADMIN PERMISSIONS FIX ===")
    
    try:
        from core.security import SecurityManager
        
        # Create SecurityManager and simulate admin login
        sm = SecurityManager()
        sm.current_role = 'ADMIN'
        sm.current_user = {'id': 1, 'username': 'admin', 'rol': 'ADMIN'}
        
        # Get modules for admin
        modules = sm.get_user_modules(1)
        
        print(f"Admin user can access {len(modules)} modules:")
        for i, module in enumerate(modules, 1):
            print(f"  {i:2d}. {module}")
        
        # Expected modules from UI
        expected_modules = [
            "Inventario", "Obras", "Herrajes", "Vidrios", "Logistica", "Pedidos", 
            "Compras", "Administracion", "Mantenimiento", "Auditoria", "Usuarios", "Configuracion"
        ]
        
        print(f"\nExpected {len(expected_modules)} modules from UI")
        
        # Check if we have all expected modules (allowing for accent differences)
        modules_normalized = [m.replace('í', 'i').replace('ó', 'o').replace('ú', 'u') for m in modules]
        expected_normalized = [m.replace('í', 'i').replace('ó', 'o').replace('ú', 'u') for m in expected_modules]
        
        missing = set(expected_normalized) - set(modules_normalized)
        extra = set(modules_normalized) - set(expected_normalized)
        
        if not missing and not extra:
            print("\nSUCCESS: All expected modules are available!")
            print("ADMIN PERMISSIONS FIX: WORKING")
            return True
        else:
            if missing:
                print(f"\nMissing modules: {missing}")
            if extra:
                print(f"Extra modules: {extra}")
            print("ADMIN PERMISSIONS FIX: NEEDS REVIEW")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = verify_admin_permissions()
    
    if success:
        print("\n" + "="*50)
        print("CONCLUSION:")
        print("- Admin user permissions have been FIXED")
        print("- Module names now match between UI and SecurityManager")
        print("- Admin can access all 12 modules in the sidebar")
        print("- The issue was case sensitivity in module names")
        print("="*50)
    else:
        print("\nFix verification failed - needs more work")