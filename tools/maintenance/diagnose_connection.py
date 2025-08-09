#!/usr/bin/env python3
"""
Diagnóstico detallado de conexión SQL Server
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

def test_pyodbc_drivers():
    """Lista los drivers ODBC disponibles"""
    print("=== DRIVERS ODBC DISPONIBLES ===")
    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        print(f"Drivers SQL Server encontrados: {len(drivers)}")
        for i, driver in enumerate(drivers, 1):
            print(f"  {i}. {driver}")
        return drivers
    except Exception as e:
        print(f"Error obteniendo drivers: {e}")
        return []

def test_basic_connection():
    """Prueba conexión básica sin especificar base de datos"""
    print("\n=== PRUEBA DE CONEXIÓN BÁSICA ===")
    
    server = os.getenv('DB_SERVER')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    drivers_to_try = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server"
    ]
    
    for driver in drivers_to_try:
        print(f"\nProbando con driver: {driver}")
        try:
            import pyodbc
            
            # Conexión sin especificar base de datos
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            print(f"String de conexión: DRIVER={{{driver}}};SERVER={server};UID={username};PWD=****;TrustServerCertificate=yes;")
            
            conn = pyodbc.connect(connection_string, timeout=10)
            
            # Probar consulta simple
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            result = cursor.fetchone()
            print(f"EXITO: Conectado con {driver}")
            print(f"Versión SQL Server: {result[0][:100]}...")
            
            # Listar bases de datos
            cursor.execute("SELECT name FROM sys.databases WHERE name IN ('users', 'inventario', 'auditoria')")
            dbs = cursor.fetchall()
            print(f"Bases de datos relevantes encontradas: {[db[0] for db in dbs]}")
            
            cursor.close()
            conn.close()
            return driver
            
        except Exception as e:
            print(f"FALLO con {driver}: {e}")
    
    return None

def test_specific_database_connection(working_driver):
    """Prueba conexión a bases de datos específicas"""
    print(f"\n=== PRUEBA DE CONEXIÓN A BASES ESPECÍFICAS ===")
    
    if not working_driver:
        print("No hay driver funcional disponible")
        return False
    
    server = os.getenv('DB_SERVER')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    databases = ['users', 'inventario', 'auditoria']
    
    for db_name in databases:
        print(f"\nProbando conexión a base de datos: {db_name}")
        try:
            import pyodbc
            
            connection_string = (
                f"DRIVER={{{working_driver}}};"
                f"SERVER={server};"
                f"DATABASE={db_name};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            conn = pyodbc.connect(connection_string, timeout=10)
            
            # Probar consulta simple
            cursor = conn.cursor()
            cursor.execute("SELECT DB_NAME()")
            result = cursor.fetchone()
            print(f"EXITO: Conectado a base de datos {result[0]}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"FALLO conectando a {db_name}: {e}")
    
    return True

if __name__ == "__main__":
    print("DIAGNÓSTICO DE CONEXIÓN SQL SERVER")
    print("=" * 50)
    
    # Mostrar configuración
    print(f"Servidor: {os.getenv('DB_SERVER', 'NO CONFIGURADO')}")
    print(f"Usuario: {os.getenv('DB_USERNAME', 'NO CONFIGURADO')}")
    print(f"Password: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'NO CONFIGURADO'}")
    
    # Verificar drivers
    available_drivers = test_pyodbc_drivers()
    
    # Probar conexión básica
    working_driver = test_basic_connection()
    
    # Probar bases específicas
    if working_driver:
        test_specific_database_connection(working_driver)
        print(f"\n[OK] DIAGNÓSTICO COMPLETO")
        print(f"Driver recomendado: {working_driver}")
        print("Actualiza tu .env con este driver si es necesario")
    else:
        print("\n✗ NO SE PUDO ESTABLECER CONEXIÓN")
        print("Verifica:")
        print("1. Que SQL Server esté ejecutándose")
        print("2. Que el servidor y puerto sean correctos")
        print("3. Que las credenciales sean válidas")
        print("4. Que los drivers ODBC estén instalados")