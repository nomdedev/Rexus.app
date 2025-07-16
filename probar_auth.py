#!/usr/bin/env python3
"""
Script para probar el nuevo sistema de autenticación
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para probar autenticación"""
    print("PROBANDO NUEVO SISTEMA DE AUTENTICACION")
    print("=" * 50)
    
    try:
        from src.core.auth import get_auth_manager
        
        # Obtener gestor de autenticación
        auth = get_auth_manager()
        
        print("1. Probando login con admin/admin...")
        user = auth.authenticate_user('admin', 'admin')
        
        if user:
            print("   [OK] Login exitoso")
            print(f"   Usuario: {user['username']}")
            print(f"   Rol: {user['role']}")
            print(f"   Nombre: {user['nombre']} {user['apellido']}")
            print(f"   Email: {user['email']}")
            
            # Probar permisos
            print("\n2. Probando permisos...")
            print(f"   Inventario (read): {auth.has_permission('inventario', 'read')}")
            print(f"   Inventario (write): {auth.has_permission('inventario', 'write')}")
            print(f"   Usuarios (admin): {auth.has_permission('usuarios', 'admin')}")
            
            # Probar obtener todos los usuarios
            print("\n3. Obteniendo lista de usuarios...")
            users = auth.get_all_users()
            print(f"   Total usuarios: {len(users)}")
            for u in users:
                print(f"   - {u['username']} ({u['role']}) - {u['status']}")
            
            # Probar crear usuario
            print("\n4. Creando usuario de prueba...")
            success = auth.create_user(
                username='nuevo_usuario',
                password='123456',
                role='usuario',
                nombre='Nuevo',
                apellido='Usuario',
                email='nuevo@rexus.com'
            )
            
            if success:
                print("   [OK] Usuario creado exitosamente")
                
                # Probar login con nuevo usuario
                print("\n5. Probando login con nuevo usuario...")
                auth.logout()  # Cerrar sesión actual
                
                new_user = auth.authenticate_user('nuevo_usuario', '123456')
                if new_user:
                    print("   [OK] Login con nuevo usuario exitoso")
                    print(f"   Usuario: {new_user['username']}")
                    print(f"   Rol: {new_user['role']}")
                    
                    # Probar permisos limitados
                    print("\n6. Probando permisos de usuario normal...")
                    print(f"   Inventario (read): {auth.has_permission('inventario', 'read')}")
                    print(f"   Inventario (write): {auth.has_permission('inventario', 'write')}")
                    print(f"   Usuarios (admin): {auth.has_permission('usuarios', 'admin')}")
                    
                else:
                    print("   [ERROR] Login con nuevo usuario falló")
            else:
                print("   [ERROR] Error creando usuario")
                
        else:
            print("   [ERROR] Login falló")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()