#!/usr/bin/env python3
"""
Script para verificar todas las conexiones de base de datos
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para verificar conexiones"""
    print("VERIFICANDO CONEXIONES DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Verificar conexión a base de datos users
        print("\n[1] VERIFICANDO CONEXIÓN A BASE USERS")
        print("-" * 40)
        
        try:
            from src.core.database import DatabaseConnection
            db_users = DatabaseConnection('users')
            
            if db_users._connection:
                print("[OK] Conexión a base 'users' exitosa")
                
                cursor = db_users.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                count = cursor.fetchone()[0]
                print(f"[OK] Encontrados {count} usuarios en tabla usuarios")
                cursor.close()
            else:
                print("[ERROR] No se pudo conectar a base 'users'")
                
        except Exception as e:
            print(f"[ERROR] Error conectando a base 'users': {e}")
        
        # Verificar conexión a base de datos inventario
        print("\n[2] VERIFICANDO CONEXIÓN A BASE INVENTARIO")
        print("-" * 40)
        
        try:
            from src.core.database import InventarioDatabaseConnection
            db_inventario = InventarioDatabaseConnection()
            
            if db_inventario._connection:
                print("[OK] Conexión a base 'inventario' exitosa")
                
                cursor = db_inventario.cursor()
                cursor.execute("SELECT COUNT(*) FROM productos")
                count = cursor.fetchone()[0]
                print(f"[OK] Encontrados {count} productos en tabla productos")
                cursor.close()
            else:
                print("[ERROR] No se pudo conectar a base 'inventario'")
                
        except Exception as e:
            print(f"[ERROR] Error conectando a base 'inventario': {e}")
        
        # Verificar autenticación
        print("\n[3] VERIFICANDO SISTEMA DE AUTENTICACIÓN")
        print("-" * 40)
        
        try:
            from src.core.auth import get_auth_manager
            auth_manager = get_auth_manager()
            
            if auth_manager and auth_manager.db_connection:
                print("[OK] AuthManager inicializado correctamente")
                
                # Probar login
                user_data = auth_manager.authenticate_user("admin", "admin")
                if user_data:
                    print(f"[OK] Login admin/admin exitoso - Rol: {user_data['role']}")
                else:
                    print("[ERROR] Login admin/admin falló")
            else:
                print("[ERROR] AuthManager no se pudo inicializar")
                
        except Exception as e:
            print(f"[ERROR] Error en sistema de autenticación: {e}")
        
        # Verificar permisos
        print("\n[4] VERIFICANDO TABLA DE PERMISOS")
        print("-" * 40)
        
        try:
            db_users = DatabaseConnection('users')
            cursor = db_users.cursor()
            
            # Verificar tabla permisos
            cursor.execute("SELECT COUNT(*) FROM permisos")
            count = cursor.fetchone()[0]
            print(f"[OK] Encontrados {count} permisos en tabla permisos")
            
            # Verificar tabla rol_permisos
            cursor.execute("SELECT COUNT(*) FROM rol_permisos")
            count = cursor.fetchone()[0]
            print(f"[OK] Encontrados {count} rol_permisos en tabla rol_permisos")
            
            cursor.close()
            
        except Exception as e:
            print(f"[ERROR] Error verificando permisos: {e}")
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETA")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()