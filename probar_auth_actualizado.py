#!/usr/bin/env python3
"""
Script para probar el sistema de autenticación actualizado
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para probar autenticación"""
    print("PROBANDO SISTEMA DE AUTENTICACIÓN")
    print("=" * 50)
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        
        if not auth_manager:
            print("[ERROR] No se pudo crear el AuthManager")
            return False
        
        print("[OK] AuthManager creado exitosamente")
        
        # Probar login con credenciales correctas
        print("\n[TEST] Probando login con admin/admin...")
        user_data = auth_manager.authenticate_user("admin", "admin")
        
        if user_data:
            print("[OK] Login exitoso!")
            print(f"  Usuario: {user_data['username']}")
            print(f"  Rol: {user_data['role']}")
            print(f"  Nombre: {user_data['nombre']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Estado: {user_data['status']}")
        else:
            print("[ERROR] Login fallido")
            return False
        
        # Probar login con credenciales incorrectas
        print("\n[TEST] Probando login con credenciales incorrectas...")
        user_data = auth_manager.authenticate_user("admin", "wrong_password")
        
        if user_data:
            print("[ERROR] Login no debería haber sido exitoso")
            return False
        else:
            print("[OK] Login fallido correctamente")
        
        # Probar permisos
        print("\n[TEST] Probando permisos...")
        if auth_manager.has_permission("read", "usuarios"):
            print("[OK] Permisos funcionando")
        else:
            print("[ERROR] Permisos no funcionan")
        
        print("\n[RESULTADO] Sistema de autenticación funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()