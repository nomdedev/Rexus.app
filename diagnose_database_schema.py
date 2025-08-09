#!/usr/bin/env python3
"""
Script para diagnosticar y corregir problemas de esquema de base de datos
Identifica columnas faltantes y genera los ALTER TABLE necesarios
"""

import pyodbc
from pathlib import Path

# Configuración de conexión (ajustar según tu configuración)
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'ITACHI\\SQLEXPRESS',
    'database': 'inventario',
    'uid': 'sa',
    'pwd': '123456',
    'TrustServerCertificate': 'yes'
}

def get_db_connection():
    """Establece conexión con la base de datos."""
    try:
        conn_str = f"DRIVER={{{DB_CONFIG['driver']}}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']};TrustServerCertificate={DB_CONFIG['TrustServerCertificate']};"
        connection = pyodbc.connect(conn_str)
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def check_table_columns(connection, table_name):
    """Verifica las columnas existentes en una tabla."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        columns = cursor.fetchall()
        return [(col[0], col[1], col[2], col[3]) for col in columns]
    except Exception as e:
        print(f"Error verificando tabla {table_name}: {e}")
        return []

def diagnose_schemas():
    """Diagnostica problemas de esquema en las tablas principales."""
    
    connection = get_db_connection()
    if not connection:
        return
    
    # Esquemas esperados basados en los errores del log
    expected_schemas = {
        'obras': [
            ('codigo_obra', 'VARCHAR', 'NO'),
            ('nombre_obra', 'VARCHAR', 'NO'), 
            ('fecha_actualizacion', 'DATETIME', 'YES'),
        ],
        'pedidos': [
            ('activo', 'BIT', 'NO'),
            ('numero_pedido', 'VARCHAR', 'NO'),
            ('fecha_entrega_solicitada', 'DATETIME', 'YES'),
            ('tipo_pedido', 'VARCHAR', 'YES'),
            ('prioridad', 'VARCHAR', 'YES'),
            ('total', 'DECIMAL', 'YES'),
            ('observaciones', 'TEXT', 'YES'),
            ('responsable_entrega', 'VARCHAR', 'YES'),
            ('cantidad_pendiente', 'INT', 'YES'),
        ],
        'vidrios': [
            ('tipo', 'VARCHAR', 'YES'),
            ('dimensiones', 'VARCHAR', 'YES'),
            ('color_acabado', 'VARCHAR', 'YES'),
            ('stock', 'INT', 'YES'),
            ('precio_m2', 'DECIMAL', 'YES'),
            ('estado', 'VARCHAR', 'YES'),
        ]
    }
    
    fixes = []
    
    for table_name, expected_columns in expected_schemas.items():
        print(f"\n🔍 Verificando tabla: {table_name}")
        existing_columns = check_table_columns(connection, table_name)
        existing_column_names = [col[0].lower() for col in existing_columns]
        
        if not existing_columns:
            print(f"❌ Tabla {table_name} no existe o no se puede acceder")
            continue
            
        print(f"✅ Tabla {table_name} encontrada con {len(existing_columns)} columnas")
        
        for col_name, col_type, nullable in expected_columns:
            if col_name.lower() not in existing_column_names:
                print(f"❌ Columna faltante: {col_name}")
                
                # Generar ALTER TABLE
                null_clause = "NULL" if nullable == "YES" else "NOT NULL"
                default_clause = ""
                
                if col_type == "BIT" and nullable == "NO":
                    default_clause = " DEFAULT 1"
                elif col_type == "DATETIME" and nullable == "YES":
                    default_clause = " DEFAULT NULL"
                elif col_type == "VARCHAR" and nullable == "NO":
                    default_clause = " DEFAULT ''"
                elif col_type == "INT" and nullable == "YES":
                    default_clause = " DEFAULT 0"
                elif col_type == "DECIMAL" and nullable == "YES":
                    default_clause = " DEFAULT 0.00"
                
                if col_type.startswith("VARCHAR"):
                    col_type = "VARCHAR(255)"
                elif col_type == "DECIMAL":
                    col_type = "DECIMAL(10,2)"
                elif col_type == "TEXT":
                    col_type = "NTEXT"
                    
                alter_sql = f"ALTER TABLE {table_name} ADD {col_name} {col_type}{default_clause} {null_clause};"
                fixes.append(alter_sql)
                print(f"   📝 SQL: {alter_sql}")
            else:
                print(f"✅ Columna existe: {col_name}")
    
    connection.close()
    
    # Guardar script de corrección
    if fixes:
        script_path = Path("fix_database_schema.sql")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("-- Script para corregir esquemas de base de datos\n")
            f.write("-- Generado automáticamente\n\n")
            for fix in fixes:
                f.write(fix + "\n")
        
        print(f"\n📄 Script de corrección guardado en: {script_path}")
        print(f"🔧 Total de correcciones: {len(fixes)}")
        
        # Opción de aplicar correcciones automáticamente
        response = input("\n¿Aplicar correcciones automáticamente? (s/N): ")
        if response.lower() == 's':
            apply_fixes(fixes)
    else:
        print("\n✅ No se encontraron problemas de esquema")

def apply_fixes(fixes):
    """Aplica las correcciones de esquema automáticamente."""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        for i, fix in enumerate(fixes, 1):
            print(f"Aplicando corrección {i}/{len(fixes)}: {fix[:50]}...")
            cursor.execute(fix)
        
        connection.commit()
        print("✅ Todas las correcciones aplicadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error aplicando correcciones: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    print("🔍 Iniciando diagnóstico de esquemas de base de datos...")
    diagnose_schemas()
