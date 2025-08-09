#!/usr/bin/env python3
"""
Script de prueba para verificar conexión a base de datos
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

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("=== PRUEBA DE CONEXIÓN A BASE DE DATOS ===\n")
    
    try:
        from src.core.database import UsersDatabaseConnection
        
        print("1. Creando conexión a base de datos 'users'...")
        db = UsersDatabaseConnection(auto_connect=True)
        
        print("2. Probando consulta simple...")
        result = db.execute_query("SELECT 1 as test")
        if result:
            print(f"   [OK] Consulta exitosa: {result}")
        else:
            print("   ✗ Consulta falló")
            return False
            
        print("3. Cerrando conexión...")
        db.disconnect()
        print("   [OK] Conexión cerrada correctamente")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_system():
    """Prueba el sistema de autenticación"""
    print("\n=== PRUEBA DE SISTEMA DE AUTENTICACIÓN ===\n")
    
    try:
        from src.core.auth import get_auth_manager
        
        print("1. Obteniendo gestor de autenticación...")
        auth_manager = get_auth_manager()
        
        # Obtener credenciales de prueba desde variables de entorno
        test_user = os.getenv("TEST_USER", "admin")
        test_password = os.getenv("TEST_PASSWORD", "admin")
        
        print(f"2. Intentando autenticación con usuario '{test_user}'...")
        user = auth_manager.authenticate_user(test_user, test_password)
        
        if user:
            print(f"   [OK] Autenticación exitosa: {user}")
            return True
        else:
            print("   ✗ Autenticación falló")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de conectividad...\n")
    
    # Verificar variables de entorno
    print("Variables de entorno:")
    print(f"  DB_SERVER: {os.getenv('DB_SERVER', 'NO CONFIGURADO')}")
    print(f"  DB_DRIVER: {os.getenv('DB_DRIVER', 'NO CONFIGURADO')}")
    print(f"  DB_USERNAME: {os.getenv('DB_USERNAME', 'NO CONFIGURADO')}")
    db_password = os.getenv('DB_PASSWORD')
    print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'NO CONFIGURADO'}")
    print()
    
    # Ejecutar pruebas
    db_ok = test_database_connection()
    auth_ok = test_auth_system()
    
    print("\n=== RESUMEN ===")
    print(f"Conexión DB: {'[OK]' if db_ok else '✗'}")
    print(f"Autenticación: {'[OK]' if auth_ok else '✗'}")
    
    if db_ok and auth_ok:
        print("\n🎉 Todas las pruebas pasaron. El sistema está listo.")
        sys.exit(0)
    else:
        print("\n[ERROR] Algunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1)