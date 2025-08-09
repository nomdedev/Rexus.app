#!/usr/bin/env python3
"""
Crear usuario admin - versión SEGURA
Usa hashing robusto y contraseñas no hardcodeadas
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

def create_admin():
    """Crear usuario admin"""
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
        
        print("Conectando...")
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # [LOCK] SEGURIDAD: Usar sistema de hashing seguro en lugar de SHA256 simple
        # Importar sistema seguro de contraseñas
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from rexus.utils.password_security import hash_password_secure
        
        # Solicitar contraseña admin de forma segura
        import getpass
        admin_password = getpass.getpass("Ingrese contraseña para usuario admin: ")
        
        if not admin_password or len(admin_password) < 8:
            print("[ERROR] Error: La contraseña debe tener al menos 8 caracteres")
            return
            
        # Hash seguro de contraseña
        password_hash = hash_password_secure(admin_password)
        print("[CHECK] Hash seguro generado")
        
        # Insertar usuario
        print("Insertando usuario admin...")
        cursor.execute("""
            INSERT INTO usuarios (
                nombre, apellido, email, usuario, password_hash, 
                rol, estado, fecha_creacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (
            'Administrador',
            'Admin', 
            'admin@rexus.app',
            'admin',
            password_hash,
            'admin',
            'Activo'
        ))
        
        print("Guardando...")
        conn.commit()
        
        # Verificar
        print("Verificando...")
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = 'admin'")
        count = cursor.fetchone()[0]
        print(f"Usuarios admin en DB: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, nombre, apellido, usuario, rol FROM usuarios WHERE usuario = 'admin'")
            user = cursor.fetchone()
            print(f"Usuario creado: ID={user[0]}, Nombre={user[1]} {user[2]}, Usuario={user[3]}, Rol={user[4]}")
        
        cursor.close()
        conn.close()
        
        return count > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if create_admin():
        print("EXITO: Usuario admin creado")
    else:
        print("ERROR: No se pudo crear usuario admin")