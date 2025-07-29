#!/usr/bin/env python3
"""
Verificar estructura de la tabla usuarios
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

def check_users_table():
    """Verifica la estructura de la tabla usuarios"""
    print("VERIFICANDO TABLA USUARIOS")
    print("=" * 40)
    
    try:
        import pyodbc
        
        # Conectar a la base de datos users
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
        
        # Verificar si existe la tabla usuarios
        print("\n1. Verificando si existe la tabla 'usuarios'...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'usuarios'
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists == 0:
            print("   ❌ La tabla 'usuarios' NO existe")
            
            # Listar todas las tablas
            print("\n2. Listando todas las tablas en la base de datos 'users':")
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            for table in tables:
                print(f"   - {table[0]}")
            
            return False
        
        print("   ✅ La tabla 'usuarios' existe")
        
        # Verificar estructura de la tabla
        print("\n2. Estructura de la tabla 'usuarios':")
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'usuarios'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            length = f"({col[3]})" if col[3] else ""
            print(f"   - {col[0]:<15} {col[1]}{length:<10} {nullable}")
        
        # Verificar datos en la tabla
        print("\n3. Verificando datos en la tabla 'usuarios':")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"   Total de registros: {count}")
        
        if count > 0:
            print("\n4. Primeros registros (sin contraseñas):")
            cursor.execute("""
                SELECT TOP 5 
                    id, usuario, rol, estado, nombre, apellido, email
                FROM usuarios
            """)
            users = cursor.fetchall()
            
            for user in users:
                print(f"   ID: {user[0]}, Usuario: {user[1]}, Rol: {user[2]}, Estado: {user[3]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def suggest_fix():
    """Sugiere cómo arreglar el problema"""
    print("\n" + "=" * 50)
    print("POSIBLES SOLUCIONES:")
    print("=" * 50)
    print("1. Si la tabla no existe, necesitas crearla:")
    print("   - Ejecutar script de creación de base de datos")
    print("   - Poblar con datos iniciales")
    print("")
    print("2. Si la tabla tiene columnas diferentes:")
    print("   - Actualizar consultas en auth.py")
    print("   - Verificar nombres de columnas")
    print("")
    print("3. Si no hay datos:")
    print("   - Crear usuario administrador inicial")
    print("   - Ejecutar script de poblado de datos")

if __name__ == "__main__":
    success = check_users_table()
    if not success:
        suggest_fix()