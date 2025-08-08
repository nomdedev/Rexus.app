#!/usr/bin/env python3
"""
Crear usuario admin con permisos completos
"""

import os
import sys
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

def create_admin_user():
    """Crear usuario admin con todos los permisos"""
    print("CREANDO USUARIO ADMIN")
    print("=" * 30)
    
    try:
        import pyodbc
        
        server = os.getenv('DB_SERVER')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        driver = os.getenv('DB_DRIVER')
        
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE=users;"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        print("Conectando a base de datos 'users'...")
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # 1. Limpiar usuario admin existente
        print("1. Limpiando usuario admin existente...")
        cursor.execute("DELETE FROM usuarios WHERE usuario = 'admin'")
        conn.commit()
        
        # 🔒 SEGURIDAD: 2. Hash seguro de contraseña
        import getpass
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from rexus.utils.password_security import hash_password_secure
        
        admin_password = getpass.getpass("Ingrese contraseña para usuario admin: ")
        
        if not admin_password or len(admin_password) < 8:
            print("❌ Error: La contraseña debe tener al menos 8 caracteres")
            return
            
        password_hash = hash_password_secure(admin_password)
        print("✅ 2. Hash seguro de contraseña generado")
        
        # 3. Insertar usuario admin
        print("3. Insertando usuario admin...")
        cursor.execute("""
            INSERT INTO usuarios (
                nombre, apellido, email, usuario, password_hash, 
                rol, estado, fecha_creacion, ultima_conexion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), NULL)
        """, (
            'Administrador',
            'Admin', 
            'admin@rexus.app',
            'admin',
            password_hash,
            'admin',
            'Activo'
        ))
        
        # Obtener el ID del usuario creado
        cursor.execute("SELECT @@IDENTITY")
        admin_id = cursor.fetchone()[0]
        print(f"   Usuario admin creado con ID: {admin_id}")
        
        # 4. Verificar que se creó correctamente
        print("4. Verificando usuario creado...")
        cursor.execute("""
            SELECT id, nombre, apellido, usuario, rol, estado, email
            FROM usuarios WHERE usuario = 'admin'
        """)
        
        admin_data = cursor.fetchone()
        if admin_data:
            print("   Usuario admin verificado:")
            print(f"     ID: {admin_data[0]}")
            print(f"     Nombre: {admin_data[1]} {admin_data[2]}")
            print(f"     Usuario: {admin_data[3]}")
            print(f"     Rol: {admin_data[4]}")
            print(f"     Estado: {admin_data[5]}")
            print(f"     Email: {admin_data[6]}")
        
        # 5. Probar autenticación
        print("5. Probando autenticación...")
        test_hash = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute("""
            SELECT id, usuario, rol FROM usuarios 
            WHERE usuario = 'admin' AND password_hash = ?
        """, (test_hash,))
        
        auth_test = cursor.fetchone()
        if auth_test:
            print(f"   ✓ Autenticación exitosa: ID={auth_test[0]}, Usuario={auth_test[1]}, Rol={auth_test[2]}")
        else:
            print("   ✗ Error en autenticación")
            
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ USUARIO ADMIN CREADO EXITOSAMENTE")
        print("Credenciales:")
        print("  Usuario: admin")
        print("  Contraseña: [La que ingresó]")
        print("  Rol: admin")
        print("\n🔒 SEGURIDAD: Contraseña hasheada de forma segura")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_login():
    """Probar login con el usuario admin creado"""
    print(f"\n" + "=" * 30)
    print("PROBANDO LOGIN CON USUARIO ADMIN")
    print("=" * 30)
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        user_data = auth_manager.authenticate_user("admin", "admin")
        
        if user_data:
            print("✓ Login exitoso")
            print("Datos del usuario:")
            for key, value in user_data.items():
                print(f"  {key}: {value}")
            return True
        else:
            print("✗ Login falló")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Crear usuario admin
    admin_created = create_admin_user()
    
    if admin_created:
        # Probar login
        login_works = test_admin_login()
        
        if login_works:
            print(f"\n🎉 TODO FUNCIONANDO CORRECTAMENTE")
            print("Puedes usar la aplicación con admin/admin")
        else:
            print(f"\n❌ PROBLEMA CON EL LOGIN")
    else:
        print(f"\n❌ NO SE PUDO CREAR EL USUARIO ADMIN")