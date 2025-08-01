#!/usr/bin/env python3
"""
Inspección simple de la base de datos 'users' con configuración automática
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def inspect_users_db_simple():
    """Inspect users database with automatic configuration"""
    print("=== INSPECCION SIMPLE DE BD USERS ===\n")
    
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify required environment variables are set
        required_vars = ["DB_SERVER", "DB_USERNAME", "DB_PASSWORD", "DB_USERS"]
        for var in required_vars:
            if not os.getenv(var):
                print(f"ERROR: Environment variable {var} not set. Check your .env file.")
                return False
        
        from core.database import UsersDatabaseConnection
        
        print("1. Connecting to users database...")
        db = UsersDatabaseConnection()
        
        # Try to connect
        if not db.connect():
            print("   Connection failed - check environment variables")
            print("   Set DB_PASSWORD to correct SQL Server password")
            return False
        
        print("   Connected successfully!")
        cursor = db.cursor()
        
        print("\n2. Listing all tables...")
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"   Found {len(tables)} tables:")
        for table in table_names:
            print(f"     - {table}")
        
        print("\n3. Checking key tables...")
        
        # Users table
        if 'usuarios' in [t.lower() for t in table_names]:
            print("\n   USUARIOS TABLE:")
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            print(f"     Total users: {count}")
            
            if count > 0:
                cursor.execute("SELECT username, rol, activo FROM usuarios ORDER BY username")
                users = cursor.fetchall()
                print("     User list:")
                for username, rol, activo in users:
                    status = "ACTIVE" if activo else "INACTIVE"
                    print(f"       {username:<15} | {rol:<12} | {status}")
        
        # Roles table
        if 'roles' in [t.lower() for t in table_names]:
            print("\n   ROLES TABLE:")
            cursor.execute("SELECT COUNT(*) FROM roles")
            count = cursor.fetchone()[0]
            print(f"     Total roles: {count}")
            
            if count > 0:
                cursor.execute("SELECT nombre, descripcion FROM roles ORDER BY nombre")
                roles = cursor.fetchall()
                print("     Available roles:")
                for nombre, desc in roles:
                    print(f"       {nombre:<15} | {desc or 'No description'}")
        
        # Permissions table
        if 'permisos' in [t.lower() for t in table_names]:
            print("\n   PERMISOS TABLE:")
            cursor.execute("SELECT COUNT(*) FROM permisos")
            count = cursor.fetchone()[0]
            print(f"     Total permissions: {count}")
            
            if count > 0:
                cursor.execute("SELECT DISTINCT modulo FROM permisos ORDER BY modulo")
                modules = cursor.fetchall()
                print("     Modules with permissions:")
                for module in modules:
                    print(f"       - {module[0]}")
        
        # Role-permissions table
        if 'rol_permisos' in [t.lower() for t in table_names]:
            print("\n   ROL_PERMISOS TABLE:")
            cursor.execute("SELECT COUNT(*) FROM rol_permisos")
            count = cursor.fetchone()[0]
            print(f"     Total role-permission assignments: {count}")
            
            if count > 0:
                cursor.execute("""
                    SELECT r.nombre, COUNT(rp.permiso_id) as total_perms
                    FROM roles r
                    LEFT JOIN rol_permisos rp ON r.id = rp.rol_id
                    GROUP BY r.nombre
                    ORDER BY total_perms DESC
                """)
                role_perms = cursor.fetchall()
                print("     Permissions by role:")
                for rol, total in role_perms:
                    print(f"       {rol:<15} | {total} permissions")
        
        db.disconnect()
        print("\n=== INSPECTION COMPLETED ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("NOTE: Make sure to set the correct SQL Server password")
    print("Edit this script and replace 'tu_password_aqui' with the real password\n")
    
    success = inspect_users_db_simple()
    if success:
        print("\nDatabase inspection completed successfully")
    else:
        print("\nDatabase inspection failed - check connection settings")