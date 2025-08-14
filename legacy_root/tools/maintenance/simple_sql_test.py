#!/usr/bin/env python3
"""
Prueba simple de SQL Server - sin caracteres Unicode
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

def simple_connection_test():
    """Prueba conexión simple"""
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')

    # Configuraciones a probar (de más específica a más general)
    configs = [
        ("DESKTOP-QHMPTGO\\SQLEXPRESS", "ODBC Driver 17 for SQL Server"),
        ("DESKTOP-QHMPTGO", "ODBC Driver 17 for SQL Server"),
        ("localhost\\SQLEXPRESS", "ODBC Driver 17 for SQL Server"),
        ("localhost", "ODBC Driver 17 for SQL Server"),
        ("127.0.0.1,1433", "ODBC Driver 17 for SQL Server"),
        ("DESKTOP-QHMPTGO\\SQLEXPRESS", "ODBC Driver 18 for SQL Server"),
        ("localhost\\SQLEXPRESS", "ODBC Driver 18 for SQL Server"),
    ]

    print("Probando configuraciones SQL Server...")
    print("=====================================")

    for server, driver in configs:
        print(f"\nServidor: {server}")
        print(f"Driver: {driver}")

        try:
            import pyodbc

            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
                f"Timeout=10;"
            )

            print("Conectando...", end=" ")
            conn = pyodbc.connect(connection_string, timeout=10)

            cursor = conn.cursor()
            cursor.execute("SELECT @@SERVERNAME")
            server_name = cursor.fetchone()[0]

            print("EXITO!")
            print(f"Nombre del servidor: {server_name}")

            # Verificar bases de datos
            cursor.execute("SELECT name FROM sys.databases WHERE name IN ('users', 'inventario', 'auditoria')")
            dbs = cursor.fetchall()
            found_dbs = [db[0] for db in dbs]
            print(f"Bases encontradas: {found_dbs}")

            cursor.close()
            conn.close()

            print(f"\n*** CONFIGURACION EXITOSA ***")
            print(f"DB_SERVER={server}")
            print(f"DB_DRIVER={driver}")

            return server, driver

        except Exception as e:
            error_str = str(e)
            print("FALLO")
            if "timeout" in error_str.lower():
                print("Razon: Tiempo de espera agotado")
            elif "instance" in error_str.lower():
                print("Razon: Instancia no disponible")
            elif "login" in error_str.lower():
                print("Razon: Error de credenciales")
            else:
                print(f"Razon: {error_str[:80]}...")

    return None, None

if __name__ == "__main__":
    print("DIAGNÓSTICO SIMPLE SQL SERVER")
    print("Variables actuales:")
    print(f"  DB_SERVER: {os.getenv('DB_SERVER')}")
    print(f"  DB_USERNAME: {os.getenv('DB_USERNAME')}")
    print(f"  DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")

    server, driver = simple_connection_test()

    if server and driver:
        print(f"\nSolucion encontrada! Actualiza tu archivo .env:")
        print(f"DB_SERVER={server}")
        print(f"DB_DRIVER={driver}")
    else:
        print(f"\nNo se pudo conectar. Verifica que:")
        print("1. SQL Server Express este ejecutandose")
        print("2. TCP/IP este habilitado")
        print("3. Las credenciales sean correctas")
        print("4. El firewall permita conexiones")
