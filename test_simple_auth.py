#!/usr/bin/env python3
"""
Test del SimpleSecurityManager para verificar login admin
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_simple_auth():
    """Test SimpleSecurityManager login"""
    print("=== TESTING SIMPLE AUTH SYSTEM ===\n")
    
    # Import SimpleSecurityManager
    from main.app import SimpleSecurityManager
    
    print("1. Creating SimpleSecurityManager...")
    auth = SimpleSecurityManager()
    print("   SimpleSecurityManager created")
    
    print("\n2. Testing admin login...")
    
    # Check current environment
    admin_pwd = os.environ.get("FALLBACK_ADMIN_PASSWORD", "admin")
    print(f"   Expected admin password: '{admin_pwd}'")
    
    # Test login with default password
    login_result = auth.login("admin", "admin")
    print(f"   Login with 'admin'/'admin': {login_result}")
    
    if login_result:
        print("   SUCCESS: Admin can login")
        
        # Check user data
        current_user = auth.get_current_user()
        current_role = auth.get_current_role()
        print(f"   Current user: {current_user}")
        print(f"   Current role: {current_role}")
        
        # Check modules
        modules = auth.get_user_modules(1)
        print(f"   Available modules: {len(modules)}")
        print(f"   Module list: {modules}")
        
        # Check permissions
        has_all_perms = auth.has_permission("any_permission")
        print(f"   Has all permissions: {has_all_perms}")
        
    else:
        print("   FAILED: Admin cannot login")
        print("   This explains why you can't see all modules!")
        
        # Try to fix by setting environment variable
        print("\n3. Attempting fix...")
        os.environ["FALLBACK_ADMIN_PASSWORD"] = "admin"
        print("   Set FALLBACK_ADMIN_PASSWORD=admin")
        
        # Test again
        login_result2 = auth.login("admin", "admin")
        print(f"   Login attempt 2: {login_result2}")
        
        if login_result2:
            print("   SUCCESS: Admin can now login after fix")
            modules = auth.get_user_modules(1)
            print(f"   Available modules: {len(modules)}")
        else:
            print("   STILL FAILED: There's another issue")

def test_app_login_flow():
    """Test the complete app login flow"""
    print("\n=== TESTING COMPLETE APP LOGIN FLOW ===\n")
    
    try:
        from core.auth import get_auth_manager
        
        print("1. Getting AuthManager...")
        auth_manager = get_auth_manager()
        print(f"   AuthManager type: {type(auth_manager).__name__}")
        
        # Ensure environment variable is set
        os.environ["FALLBACK_ADMIN_PASSWORD"] = "admin"
        
        print("\n2. Testing admin authentication...")
        user_data = auth_manager.authenticate_user("admin", "admin")
        print(f"   Authentication result: {user_data}")
        
        if user_data:
            print("   SUCCESS: Complete flow working")
            print(f"   User data: {user_data}")
        else:
            print("   FAILED: Complete flow not working")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_auth()
    test_app_login_flow()