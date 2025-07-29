#!/usr/bin/env python3
import sys
import os
import hashlib
from pathlib import Path

# Agregar el directorio raiz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables de entorno cargadas")
except ImportError:
    print("[WARNING] python-dotenv no instalado")

def create_admin_user():
    try:
        from src.core.database import UsersDatabaseConnection
        
        print("[INFO] Conectando a la base de datos...")
        db = UsersDatabaseConnection()
        db.connect()
        print("[OK] Conexion exitosa")
        
        # Verificar si existe la tabla usuarios
        tables = db.execute_query("SELECT name FROM sys.tables WHERE name = 'usuarios'")
        
        if not tables:
            print("[INFO] Creando tabla usuarios...")
            db.execute_non_query("""
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
                    estado VARCHAR(20) DEFAULT 'Activo',
                    nombre VARCHAR(100),
                    apellido VARCHAR(100),
                    email VARCHAR(100),
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    ultimo_login DATETIME
                )
            """)
            print("[OK] Tabla usuarios creada")
        else:
            print("[OK] Tabla usuarios ya existe")
        
        # Verificar si existe el usuario admin
        admin_user = db.execute_query("SELECT id, usuario FROM usuarios WHERE usuario = 'admin'")
        
        if not admin_user:
            print("[INFO] Creando usuario administrador...")
            
            # Crear hash de la contrasena 'admin'
            password_hash = hashlib.sha256('admin'.encode()).hexdigest()
            
            # Insertar usuario admin
            db.execute_non_query("""
                INSERT INTO usuarios (usuario, password_hash, rol, estado, nombre, apellido, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'admin',
                password_hash, 
                'admin',
                'Activo',
                'Administrador',
                'Sistema',
                'admin@rexus.app'
            ))
            
            print("[OK] Usuario administrador creado exitosamente")
            print("[INFO] Credenciales:")
            print("   Usuario: admin")
            print("   Contrasena: admin")
            print("   Rol: admin")
        else:
            print("[OK] Usuario admin ya existe")
            admin_data = admin_user[0]
            print(f"   ID: {admin_data[0]}")
            print(f"   Usuario: {admin_data[1]}")
        
        # Verificar la contrasena del admin
        admin_full = db.execute_query("SELECT id, usuario, password_hash, rol FROM usuarios WHERE usuario = 'admin'")
        
        if admin_full:
            admin_data = admin_full[0]
            expected_hash = hashlib.sha256('admin'.encode()).hexdigest()
            current_hash = admin_data[2]
            
            if current_hash != expected_hash:
                print("[INFO] Actualizando contrasena del admin...")
                db.execute_non_query("UPDATE usuarios SET password_hash = ? WHERE usuario = 'admin'", (expected_hash,))
                print("[OK] Contrasena actualizada")
            else:
                print("[OK] Contrasena del admin correcta")
        
        print("\n[SUCCESS] Configuracion de usuario administrador completada")
        print("[INFO] Ahora puedes iniciar sesion con:")
        print("   Usuario: admin")  
        print("   Contrasena: admin")
        
    except Exception as e:
        print(f"[ERROR] Error configurando usuario admin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()