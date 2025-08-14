#!/usr/bin/env python3
"""
Prueba diferentes configuraciones de SQL Server
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

def test_sql_server_variations():
    """Prueba diferentes configuraciones de servidor"""
    print("PROBANDO VARIACIONES DE CONFIGURACION SQL SERVER")
    print("=" * 60)

    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')

    # Diferentes configuraciones de servidor a probar
    server_configs = [
        "DESKTOP-QHMPTGO\\SQLEXPRESS",
        "DESKTOP-QHMPTGO",
        "localhost\\SQLEXPRESS",
        "localhost",
        "127.0.0.1\\SQLEXPRESS",
        "127.0.0.1",
        "(local)\\SQLEXPRESS",
        "(local)",
        "DESKTOP-QHMPTGO\\SQLEXPRESS,1433",
        "DESKTOP-QHMPTGO,1433",
        "localhost,1433",
        "127.0.0.1,1433",
    ]

    drivers = ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"]

    for driver in drivers:
        print(f"\n--- PROBANDO CON {driver} ---")

        for server in server_configs:
            try:
                import pyodbc

                connection_string = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"TrustServerCertificate=yes;"
                    f"Timeout=5;"
                )

                print(f"Probando: {server:<30} ", end="")

                conn = pyodbc.connect(connection_string, timeout=5)

                # Probar consulta
                cursor = conn.cursor()
                cursor.execute("SELECT @@SERVERNAME, @@VERSION")
                result = cursor.fetchone()

                print(f"[OK] EXITO - Servidor: {result[0]}")

                # Listar bases de datos
                cursor.execute("SELECT name FROM sys.databases")
                dbs = [row[0] for row in cursor.fetchall()]
                print(f"   Bases disponibles: {dbs}")

                cursor.close()
                conn.close()

                print(f"\n🎉 CONFIGURACION EXITOSA:")
                print(f"   Servidor: {server}")
                print(f"   Driver: {driver}")
                return server, driver

            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    print("✗ TIMEOUT")
                elif "server" in error_msg.lower():
                    print("✗ NO DISPONIBLE")
                elif "login" in error_msg.lower():
                    print("✗ CREDENCIALES")
                else:
                    print(f"✗ ERROR: {error_msg[:50]}...")

    return None, None

if __name__ == "__main__":
    working_server, working_driver = test_sql_server_variations()

    if working_server and working_driver:
        print(f"\n[OK] SOLUCION ENCONTRADA:")
        print(f"Actualiza tu .env con:")
        print(f"DB_SERVER={working_server}")
        print(f"DB_DRIVER={working_driver}")
    else:
        print(f"\n✗ NO SE ENCONTRO CONFIGURACION FUNCIONAL")
        print("Posibles soluciones:")
        print("1. Verificar que SQL Server Express esté ejecutándose")
        print("2. Habilitar TCP/IP en SQL Server Configuration Manager")
        print("3. Verificar que el puerto 1433 esté abierto")
        print("4. Comprobar las credenciales de sa")
        print("5. Verificar que la autenticación mixta esté habilitada")
