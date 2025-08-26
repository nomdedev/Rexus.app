#!/usr/bin/env python3
"""
Script para verificar esquema de base de datos directamente
Conecta a SQL Server y verifica las tablas que usan las consultas embebidas
"""

import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db(database_name):
    """Conectar a la base de datos especificada."""
    try:
        connection_string = (
            f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={database_name};"
            f"UID={os.getenv('DB_USERNAME')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            "TrustServerCertificate=yes;"
            "Encrypt=no;"
        )
        
        conn = pyodbc.connect(connection_string, timeout=10)
        print(f"✅ Conectado exitosamente a la base de datos: {database_name}")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a {database_name}: {e}")
        return None

def verificar_tablas(conn, database_name, tablas_esperadas):
    """Verificar que las tablas existan en la base de datos."""
    if not conn:
        return
    
    print(f"\n🔍 VERIFICANDO TABLAS EN: {database_name}")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    # Listar todas las tablas
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tablas_existentes = [row[0].lower() for row in cursor.fetchall()]
    print(f"📋 Tablas encontradas: {', '.join(tablas_existentes)}")
    
    # Verificar tablas específicas
    print(f"\n🎯 VERIFICACIÓN DE TABLAS ESPECÍFICAS:")
    for tabla in tablas_esperadas:
        if tabla.lower() in tablas_existentes:
            print(f"✅ {tabla}: EXISTE")
            
            # Obtener estructura de la tabla
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{tabla}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columnas = cursor.fetchall()
            print(f"   📊 Columnas ({len(columnas)}): {', '.join([col[0] for col in columnas[:5]])}{'...' if len(columnas) > 5 else ''}")
        else:
            print(f"❌ {tabla}: NO EXISTE")

def main():
    """Función principal."""
    print("🔍 VERIFICACIÓN DE ESQUEMA DE BASE DE DATOS")
    print("=" * 60)
    
    # Tablas que encontramos en las consultas embebidas
    tablas_users = [
        'usuarios',
        'sesiones_usuario', 
        'auditoria_eventos',
        'auditoria_sistema',
        'roles',
        'permisos_usuario'
    ]
    
    tablas_inventario = [
        'productos',
        'inventario',
        'herrajes',
        'ordenes_compra_detalles',
        'servicios_transporte',
        'obras',
        'reservas_materiales',
        'movimientos_inventario'
    ]
    
    # Verificar base de datos 'users'
    conn_users = conectar_db('users')
    verificar_tablas(conn_users, 'users', tablas_users)
    if conn_users:
        conn_users.close()
    
    # Verificar base de datos 'inventario'
    conn_inventario = conectar_db('inventario')
    verificar_tablas(conn_inventario, 'inventario', tablas_inventario)
    if conn_inventario:
        conn_inventario.close()
    
    print(f"\n✅ Verificación completada.")

if __name__ == "__main__":
    main()
