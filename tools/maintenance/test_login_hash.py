#!/usr/bin/env python3
"""
Probar el hash de login
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

def test_password_hash():
    """Probar el hash de contraseñas"""
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
        
        print("Conectando para verificar hashes...")
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # Obtener datos del usuario admin
        cursor.execute("""
            SELECT usuario, password_hash, rol, estado 
            FROM usuarios 
            WHERE usuario = 'admin'
        """)
        
        result = cursor.fetchone()
        if result:
            db_user, db_hash, db_rol, db_estado = result
            print(f"Usuario en DB: {db_user}")
            print(f"Hash en DB: {db_hash}")
            print(f"Rol: {db_rol}")
            print(f"Estado: {db_estado}")
            
            # Probar diferentes contraseñas
            test_passwords = ["admin", "Admin", "123456", "password"]
            
            print(f"\nProbando diferentes contraseñas:")
            for test_pwd in test_passwords:
                computed_hash = hashlib.sha256(test_pwd.encode()).hexdigest()
                matches = computed_hash == db_hash
                print(f"  '{test_pwd}' -> {computed_hash[:20]}... {'COINCIDE' if matches else 'NO COINCIDE'}")
                
                if matches:
                    print(f"  *** CONTRASEÑA CORRECTA: '{test_pwd}' ***")
        
        else:
            print("No se encontro usuario 'admin'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_auth_method():
    """Probar el método de autenticación directamente"""
    print(f"\nProbando método de autenticación...")
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        
        # Probar diferentes combinaciones
        test_combinations = [
            ("admin", "admin"),
            ("admin", "Admin"),
            ("admin", "123456"),
            ("supervisor", "supervisor"),
        ]
        
        for user, pwd in test_combinations:
            print(f"  Probando: {user}/{pwd}... ", end="")
            result = auth_manager.authenticate_user(user, pwd)
            if result:
                print(f"EXITO - Rol: {result['role']}")
            else:
                print("FALLO")
                
    except Exception as e:
        print(f"ERROR en autenticacion: {e}")

if __name__ == "__main__":
    print("VERIFICACION DE AUTENTICACION")
    print("=" * 40)
    test_password_hash()
    test_auth_method()