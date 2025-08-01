#!/usr/bin/env python3
"""
Test script to verify admin permissions are working correctly
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

from core.auth import get_auth_manager
from core.security import get_security_manager, init_security_manager
from core.database import UsersDatabaseConnection

def test_admin_permissions():
    """Test admin user permissions and module access"""
    print("=== TESTING ADMIN PERMISSIONS ===\n")
    
    try:
        # Initialize database connection
        print("1. Connecting to database...")
        db = UsersDatabaseConnection()
        db.connect()
        print("   ✅ Database connected")
        
        # Initialize security manager
        print("\n2. Initializing security manager...")
        security_manager = init_security_manager(db)
        print("   ✅ Security manager initialized")
        
        # Test login for admin user
        print("\n3. Testing admin login...")
        login_success = security_manager.login("admin", "admin123")
        print(f"   Login result: {login_success}")
        
        if login_success:
            print("   ✅ Admin login successful")
            
            # Check current user and role
            current_user = security_manager.get_current_user()
            current_role = security_manager.get_current_role()
            print(f"   Current user: {current_user}")
            print(f"   Current role: {current_role}")
            
            # Get user modules
            print("\n4. Testing module permissions...")
            if current_user:
                user_id = current_user.get('id', 1)
                modules = security_manager.get_user_modules(user_id)
                print(f"   Modules for user ID {user_id}:")
                for i, module in enumerate(modules):
                    print(f"   {i+1:2d}. {module}")
                
                print(f"\n   Total modules: {len(modules)}")
                
                # Test individual permissions
                print("\n5. Testing individual permissions...")
                test_permissions = [
                    "view_inventario",
                    "view_obras", 
                    "view_configuracion",
                    "manage_usuarios",
                    "view_auditoria"
                ]
                
                for perm in test_permissions:
                    has_perm = security_manager.has_permission(perm)
                    status = "✅" if has_perm else "❌"
                    print(f"   {status} {perm}: {has_perm}")
                    
            else:
                print("   ❌ No current user data available")
                
        else:
            print("   ❌ Admin login failed")
            
            # Try getting auth manager directly
            print("\n   Trying AuthManager directly...")
            auth_manager = get_auth_manager()
            if auth_manager:
                user_data = auth_manager.authenticate_user("admin", "admin123")
                print(f"   AuthManager result: {user_data}")
            else:
                print("   ❌ Could not get AuthManager")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            if 'db' in locals():
                db.disconnect()
                print("\n✅ Database disconnected")
        except:
            pass

def test_ui_module_names():
    """Test that UI module names match SecurityManager module names"""
    print("\n=== TESTING MODULE NAME CONSISTENCY ===\n")
    
    # Module names from UI (app.py lines 260-275)
    ui_modules = [
        "Inventario", "Obras", "Herrajes", "Vidrios", "Logística", "Pedidos", 
        "Compras", "Administración", "Mantenimiento", "Auditoría", "Usuarios", "Configuración"
    ]
    
    # Module names from SecurityManager
    sys.path.insert(0, 'rexus')
    from core.security import SecurityManager
    sm = SecurityManager()
    sm.current_role = 'ADMIN'
    sm.current_user = {'id': 1, 'username': 'admin', 'rol': 'ADMIN'}
    security_modules = sm.get_user_modules(1)
    
    print("UI Module Names:")
    for i, module in enumerate(sorted(ui_modules)):
        print(f"   {i+1:2d}. '{module}'")
    
    print(f"\nSecurityManager Module Names:")
    for i, module in enumerate(sorted(security_modules)):
        print(f"   {i+1:2d}. '{module}'")
    
    # Check for matches
    print(f"\nMatching Analysis:")
    ui_set = set(ui_modules)
    security_set = set(security_modules)
    
    matches = ui_set & security_set
    ui_only = ui_set - security_set
    security_only = security_set - ui_set
    
    print(f"   Matches: {len(matches)}")
    for module in sorted(matches):
        print(f"     ✅ '{module}'")
    
    if ui_only:
        print(f"   UI only: {len(ui_only)}")
        for module in sorted(ui_only):
            print(f"     🔸 '{module}'")
    
    if security_only:
        print(f"   Security only: {len(security_only)}")
        for module in sorted(security_only):
            print(f"     🔹 '{module}'")

if __name__ == "__main__":
    test_ui_module_names()
    test_admin_permissions()