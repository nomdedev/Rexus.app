#!/usr/bin/env python3
"""
Verificacion simple de tabla usuarios
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

def simple_check():
    """Verificacion simple"""
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
        
        # Listar todas las tablas
        print("\nTablas en la base de datos 'users':")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        
        if not tables:
            print("  No hay tablas en la base de datos")
        else:
            for table in tables:
                print(f"  - {table[0]}")
        
        # Verificar tabla usuarios específicamente
        print(f"\nVerificando tabla 'usuarios':")
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            print(f"  Registros en usuarios: {count}")
            
            # Mostrar estructura
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'usuarios'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            print("  Columnas:")
            for col in columns:
                print(f"    - {col[0]} ({col[1]})")
            
            # Mostrar algunos datos (sin password)
            if count > 0:
                print("  Usuarios existentes:")
                cursor.execute("SELECT TOP 3 usuario, rol, estado FROM usuarios")
                users = cursor.fetchall()
                for user in users:
                    print(f"    - {user[0]} | {user[1]} | {user[2]}")
                    
        except Exception as e:
            print(f"  ERROR accediendo tabla usuarios: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR de conexion: {e}")

if __name__ == "__main__":
    simple_check()