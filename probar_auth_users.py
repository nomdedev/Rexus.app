#!/usr/bin/env python3
"""
Script para probar el sistema de autenticación con base de datos users
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para probar autenticación"""
    print("PROBANDO AUTENTICACIÓN CON BD USERS")
    print("=" * 50)
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        
        if not auth_manager:
            print("[ERROR] No se pudo crear el AuthManager")
            return False
        
        print("[OK] AuthManager creado exitosamente")
        
        # Probar login con admin/admin
        print("\n[TEST] Probando login con admin/admin...")
        user_data = auth_manager.authenticate_user("admin", "admin")
        
        if user_data:
            print("[OK] Login exitoso!")
            print(f"  ID: {user_data['id']}")
            print(f"  Usuario: {user_data['username']}")
            print(f"  Rol: {user_data['role']}")
            print(f"  Nombre: {user_data['nombre']}")
            print(f"  Apellido: {user_data['apellido']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Estado: {user_data['status']}")
        else:
            print("[ERROR] Login fallido con admin/admin")
        
        # Probar otros usuarios
        usuarios_test = [
            ("supervisor", "supervisor"),
            ("usuario", "usuario")
        ]
        
        for username, password in usuarios_test:
            print(f"\n[TEST] Probando login con {username}/{password}...")
            user_data = auth_manager.authenticate_user(username, password)
            
            if user_data:
                print(f"[OK] Login exitoso para {username}")
                print(f"  Rol: {user_data['role']}")
            else:
                print(f"[ERROR] Login fallido para {username}")
        
        # Probar obtener todos los usuarios
        print(f"\n[TEST] Probando get_all_users...")
        users = auth_manager.get_all_users()
        print(f"[OK] Se encontraron {len(users)} usuarios:")
        for user in users:
            print(f"  - {user['username']} ({user['role']}) - {user['status']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()