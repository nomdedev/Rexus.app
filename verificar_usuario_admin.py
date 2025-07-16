#!/usr/bin/env python3
"""
Script para verificar y crear el usuario admin en la tabla usuarios
"""

import sys
import os
import hashlib

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para verificar usuario admin"""
    print("VERIFICANDO USUARIO ADMIN")
    print("=" * 50)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexión a base de datos exitosa")
        
        cursor = db.cursor()
        
        # Verificar si existe el usuario admin
        cursor.execute("SELECT id, username, password_hash, rol FROM usuarios WHERE username = ?", ("admin",))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"[EXISTE] Usuario admin encontrado:")
            print(f"  ID: {admin_user[0]}")
            print(f"  Username: {admin_user[1]}")
            print(f"  Rol: {admin_user[3]}")
            
            # Verificar password
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            if admin_user[2] == password_hash:
                print(f"[OK] Password admin correcto")
            else:
                print(f"[ERROR] Password admin incorrecto")
                print(f"  Esperado: {password_hash}")
                print(f"  Actual: {admin_user[2]}")
                
                # Actualizar password
                cursor.execute("""
                    UPDATE usuarios 
                    SET password_hash = ? 
                    WHERE username = ?
                """, (password_hash, "admin"))
                db.commit()
                print(f"[OK] Password admin actualizado")
        else:
            print("[NO EXISTE] Usuario admin no encontrado, creando...")
            
            # Crear usuario admin
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, rol, nombre, apellido, email, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("admin", password_hash, "admin", "Administrador", "Sistema", "admin@rexus.app", 1))
            
            db.commit()
            print("[OK] Usuario admin creado exitosamente")
        
        # Verificar todos los usuarios
        cursor.execute("SELECT id, username, rol, activo FROM usuarios")
        users = cursor.fetchall()
        
        print(f"\n[USUARIOS] Total de usuarios en la base: {len(users)}")
        for user in users:
            status = "Activo" if user[3] else "Inactivo"
            print(f"  - {user[1]} ({user[2]}) - {status}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()