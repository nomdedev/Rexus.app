#!/usr/bin/env python3
"""
Test del sistema de usuarios y permisos en la base de datos
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_user_permissions_database():
    """Test the user permissions system against the database"""
    print("=== TESTING USER PERMISSIONS DATABASE ===\n")
    
    try:
        from core.database import UsersDatabaseConnection
        from core.auth import get_auth_manager
        from core.security import SecurityManager, initialize_security_manager
        
        print("1. Testing database connection...")
        # Try to connect to users database
        try:
            db = UsersDatabaseConnection()
            db.connect()
            print("   Users DB: Connected")
            
            # Check if connection is working
            if db._connection:
                print("   Users DB: Connection active")
            else:
                print("   Users DB: Connection failed, using demo mode")
                
        except Exception as e:
            print(f"   Users DB: ERROR - {e}")
            print("   Using demo/fallback mode")
            db = None
        
        print("\n2. Testing AuthManager...")
        try:
            auth_manager = get_auth_manager()
            if auth_manager:
                print("   AuthManager: OK")
                
                # Test admin user authentication
                admin_data = auth_manager.authenticate_user("admin", "admin123")
                if admin_data:
                    print(f"   Admin login: SUCCESS")
                    print(f"   Admin data: {admin_data}")
                else:
                    print("   Admin login: FAILED - user might not exist")
                    
                    # List all users
                    try:
                        users = auth_manager.get_all_users()
                        print(f"   Available users: {[u.get('username', '?') for u in users]}")
                    except:
                        print("   Could not list users")
                        
            else:
                print("   AuthManager: NOT AVAILABLE")
        except Exception as e:
            print(f"   AuthManager: ERROR - {e}")
        
        print("\n3. Testing SecurityManager...")
        try:
            # Try to initialize security manager
            security_manager = initialize_security_manager()
            if security_manager:
                print("   SecurityManager: Initialized OK")
                
                # Simulate admin login
                login_success = security_manager.login("admin", "admin123")
                print(f"   Admin login via SecurityManager: {login_success}")
                
                if login_success:
                    # Test permissions
                    current_user = security_manager.get_current_user()
                    current_role = security_manager.get_current_role()
                    print(f"   Current user: {current_user}")
                    print(f"   Current role: {current_role}")
                    
                    # Get user modules
                    if current_user:
                        user_id = current_user.get('id', 1)
                        modules = security_manager.get_user_modules(user_id)
                        print(f"   Modules for admin: {len(modules)}")
                        print(f"   Module list: {modules}")
                        
                        # Test individual permissions
                        test_permissions = ["view_inventario", "view_obras", "manage_usuarios"]
                        for perm in test_permissions:
                            has_perm = security_manager.has_permission(perm)
                            print(f"   Permission '{perm}': {has_perm}")
                    
                else:
                    print("   Could not login admin user")
                    
            else:
                print("   SecurityManager: NOT AVAILABLE")
                
        except Exception as e:
            print(f"   SecurityManager: ERROR - {e}")
            import traceback
            traceback.print_exc()
        
        print("\n4. Testing database tables (if available)...")
        if db and db._connection:
            try:
                cursor = db.cursor()
                
                # Check usuarios table
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                user_count = cursor.fetchone()[0]
                print(f"   Users in database: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT username, rol, activo FROM usuarios")
                    users = cursor.fetchall()
                    print("   User list:")
                    for username, rol, activo in users:
                        status = "ACTIVE" if activo else "INACTIVE"
                        print(f"     - {username} ({rol}) - {status}")
                
                # Check roles table
                try:
                    cursor.execute("SELECT COUNT(*) FROM roles")
                    role_count = cursor.fetchone()[0]
                    print(f"   Roles in database: {role_count}")
                except:
                    print("   Roles table: NOT FOUND")
                
                # Check permisos table
                try:
                    cursor.execute("SELECT COUNT(*) FROM permisos")
                    perm_count = cursor.fetchone()[0]
                    print(f"   Permissions in database: {perm_count}")
                except:
                    print("   Permissions table: NOT FOUND")
                
            except Exception as e:
                print(f"   Database tables: ERROR - {e}")
        else:
            print("   Database tables: CANNOT TEST (no connection)")
        
        if db:
            db.disconnect()
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_permissions_database()