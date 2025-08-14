#!/usr/bin/env python3
"""
Script para crear el usuario administrador por defecto en Rexus.app

Este script verifica si existe la tabla de usuarios y el usuario admin,
y los crea si no existen.
"""

import sys
import os
import hashlib
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables de entorno cargadas")
except ImportError:
    print("[WARN]  python-dotenv no instalado")

def create_admin_user():
    """Crear usuario admin si no existe."""
    try:
        from src.core.database import UsersDatabaseConnection

        print("[INFO] Conectando a la base de datos...")
        db = UsersDatabaseConnection()
        db.connect()
        print("[OK] Conexion exitosa")

        # Verificar si existe la tabla usuarios
        tables = db.execute_query("""
            SELECT name FROM sys.tables WHERE name = 'usuarios'
        """)

        if not tables:
            print("📝 Creando tabla usuarios...")
            # Crear tabla usuarios
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
            print("[CHECK] Tabla usuarios creada")
        else:
            print("[CHECK] Tabla usuarios ya existe")

        # Verificar si existe el usuario admin
        admin_user = db.execute_query("""
            SELECT id, usuario FROM usuarios WHERE usuario = 'admin'
        """)

        if not admin_user:
            print("👤 Creando usuario administrador...")

            # [LOCK] SEGURIDAD: Hash seguro de contraseña
            import getpass
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from rexus.utils.password_security import hash_password_secure

            admin_password = getpass.getpass("Ingrese contraseña para usuario admin: ")

            if not admin_password or len(admin_password) < 8:
                print("[ERROR] Error: La contraseña debe tener al menos 8 caracteres")
                return False

            password_hash = hash_password_secure(admin_password)

            # Insertar usuario admin
            db.execute_non_query("""
                INSERT INTO usuarios (usuario,
password_hash,
                    rol,
                    estado,
                    nombre,
                    apellido,
                    email)
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

            print("[CHECK] Usuario administrador creado exitosamente")
            print("📋 Credenciales:")
            print("   Usuario: admin")
            print("   Contraseña: [La que ingresó]")
            print("   Rol: admin")
        else:
            print("[CHECK] Usuario admin ya existe")
            admin_data = admin_user[0]
            print(f"   ID: {admin_data[0]}")
            print(f"   Usuario: {admin_data[1]}")

        # Verificar que el hash almacenado sea seguro
        admin_full = db.execute_query("""
            SELECT id, usuario, password_hash, rol FROM usuarios WHERE usuario = 'admin'
        """)

        if admin_full:
            admin_data = admin_full[0]
            current_hash = admin_data[2]

            # Verificar si el hash es SHA256 inseguro (64 caracteres hex)
            if len(current_hash) == 64 and \
                all(c in '0123456789abcdef' for c in current_hash):
                print("SEGURIDAD CRÍTICA: Detectado hash SHA256 inseguro")
                print("Se requiere migración manual a bcrypt/Argon2")
                print("Ejecute: python scripts/security/migrate_passwords.py")
                print("[CHECK] Hash actual preservado - requiere migración")
            else:
                print("[CHECK] Hash de contraseña seguro detectado")

        print("\nConfiguración de usuario administrador completada")
        print("Ahora puedes iniciar sesión con:")
        print("   Usuario: admin")
        print("   Contraseña: [La contraseña que configuró]")

    except Exception as e:
        print(f"[ERROR] Error configurando usuario admin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()
