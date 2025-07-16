#!/usr/bin/env python3
"""
Script para diagnosticar problemas de login
"""

import sys
import os
import hashlib

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para diagnosticar login"""
    print("DIAGNÓSTICO DE LOGIN")
    print("=" * 50)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexión a base de datos exitosa")
        
        cursor = db.cursor()
        
        # Verificar tabla usuarios
        print("\n[VERIFICANDO] Tabla usuarios...")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"[INFO] Total usuarios en tabla: {count}")
        
        # Verificar usuarios activos
        cursor.execute("SELECT id, username, password_hash, rol, activo FROM usuarios WHERE activo = 1")
        usuarios = cursor.fetchall()
        
        print(f"\n[USUARIOS ACTIVOS] {len(usuarios)} usuarios:")
        for user in usuarios:
            print(f"  ID: {user[0]}")
            print(f"  Username: '{user[1]}'")
            print(f"  Password Hash: {user[2]}")
            print(f"  Rol: {user[3]}")
            print(f"  Activo: {user[4]}")
            print("  ---")
        
        # Verificar hash de admin
        print("\n[VERIFICANDO] Hash de contraseña admin...")
        expected_hash = hashlib.sha256("admin".encode()).hexdigest()
        print(f"Hash esperado para 'admin': {expected_hash}")
        
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = 'admin'")
        actual_hash = cursor.fetchone()
        if actual_hash:
            print(f"Hash actual en BD: {actual_hash[0]}")
            print(f"¿Coinciden? {expected_hash == actual_hash[0]}")
        else:
            print("No se encontró usuario admin")
        
        # Simular login
        print("\n[SIMULANDO LOGIN] admin/admin...")
        cursor.execute("""
            SELECT id, username, password_hash, rol, activo, nombre, apellido, email
            FROM usuarios 
            WHERE username = ? AND activo = 1
        """, ("admin",))
        
        user_data = cursor.fetchone()
        if user_data:
            print("[OK] Usuario encontrado")
            print(f"  Data: {user_data}")
            
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            print(f"  Hash generado: {password_hash}")
            print(f"  Hash en BD: {user_data[2]}")
            
            if user_data[2] == password_hash:
                print("[OK] Password correcto - LOGIN EXITOSO")
            else:
                print("[ERROR] Password incorrecto")
        else:
            print("[ERROR] Usuario no encontrado")
        
        cursor.close()
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()