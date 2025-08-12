#!/usr/bin/env python3
"""
Debug detallado de la consulta de autenticación
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

def debug_auth_query():
    """Debug paso a paso de la consulta de autenticación"""
    print("DEBUG DETALLADO DE AUTENTICACION")
    print("=" * 50)
    
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
        
        print("1. Conectando a la base de datos...")
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # Ejecutar exactamente la misma consulta que usa auth.py
        test_username = "admin"
        print(f"\n2. Ejecutando consulta para usuario: '{test_username}'")
        
        query = """
            SELECT id, usuario, password_hash, rol, estado, nombre, apellido, email
            FROM usuarios 
            WHERE usuario = ? AND estado = 'Activo'
        """
        
        print(f"   Consulta SQL: {query.strip()}")
        print(f"   Parametros: ('{test_username}',)")
        
        cursor.execute(query, (test_username,))
        user_data = cursor.fetchall()
        
        print(f"\n3. Resultados de la consulta:")
        print(f"   Número de registros encontrados: {len(user_data)}")
        
        if not user_data:
            print("   [ERROR] NO SE ENCONTRO NINGUN USUARIO")
            
            # Verificar qué usuarios existen
            print("\n4. Verificando usuarios existentes:")
            cursor.execute("SELECT usuario, estado FROM usuarios")
            all_users = cursor.fetchall()
            for user in all_users:
                print(f"     - {user[0]} | Estado: {user[1]}")
            
            return False
        
        # Mostrar datos encontrados
        user_record = user_data[0]
        print(f"\n4. Datos del usuario encontrado:")
        print(f"   ID: {user_record[0]}")
        print(f"   Usuario: {user_record[1]}")
        print(f"   Password Hash: {user_record[2]}")
        print(f"   Rol: {user_record[3]}")
        print(f"   Estado: {user_record[4]}")
        print(f"   Nombre: {user_record[5]}")
        print(f"   Apellido: {user_record[6]}")
        print(f"   Email: {user_record[7]}")
        
        # [LOCK] SEGURIDAD: Verificar password con sistema seguro
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from rexus.utils.password_security import verify_password_secure
        
        # SEGURIDAD: No usar contraseñas hardcodeadas
        import getpass
        test_password = getpass.getpass("Ingrese contraseña para verificar: ")
        
        print(f"\n5. Verificación de contraseña (sistema seguro):")
        print(f"   Password ingresado: [OCULTO]")
        print(f"   Hash en BD: {user_record[2][:20]}...")
        
        try:
            # [CHECK] Verificación segura
            password_matches = verify_password_secure(test_password, user_record[2])
            print(f"   Verificación segura: {'SI' if password_matches else 'NO'}")
        except Exception:
            # Fallback para hashes legacy SHA256
            computed_hash = hashlib.sha256(test_password.encode()).hexdigest()
            password_matches = computed_hash == user_record[2]
            print(f"   Hash calculado (legacy): {computed_hash}")
            print(f"   Coinciden (legacy): {'SI' if password_matches else 'NO'}")
            if password_matches:
                print(f"   [WARN]  HASH LEGACY DETECTADO - Recomiende migración a sistema seguro")
        
        if password_matches:
            print(f"\n6. Creando diccionario de usuario:")
            user_info = {
                'id': user_record[0],
                'username': user_record[1],
                'role': user_record[3],  # Nota: usando 'role' no 'rol'
                'status': user_record[4],
                'nombre': user_record[5] or '',
                'apellido': user_record[6] or '',
                'email': user_record[7] or ''
            }
            
            print(f"   Diccionario creado: {user_info}")
            print(f"   [CHECK] AUTENTICACION EXITOSA")
            
            return user_info
        else:
            print(f"   [ERROR] CONTRASEÑA INCORRECTA")
            return None
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_auth_manager():
    """Probar el AuthManager directamente"""
    print(f"\n" + "=" * 50)
    print("PROBANDO AUTH MANAGER DIRECTAMENTE")
    print("=" * 50)
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        
        print("1. Intentando autenticación con admin/admin...")
        result = auth_manager.authenticate_user("admin", "admin")
        
        if result:
            print(f"   [CHECK] EXITO")
            print(f"   Datos retornados: {result}")
            
            # Verificar si tiene las claves necesarias
            required_keys = ['id', 'username', 'role']
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"   [WARN]  FALTAN CLAVES: {missing_keys}")
            else:
                print(f"   [CHECK] TODAS LAS CLAVES NECESARIAS PRESENTES")
                
        else:
            print(f"   [ERROR] FALLO - No se retornaron datos")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Debug paso a paso
    user_data = debug_auth_query()
    
    # Probar AuthManager
    test_auth_manager()
    
    if user_data:
        print(f"\n🎉 EL PROBLEMA ESTA RESUELTO")
        print(f"El usuario se autentica correctamente")
    else:
        print(f"\n[ERROR] AUN HAY PROBLEMAS")
        print(f"Revisar los errores mostrados arriba")