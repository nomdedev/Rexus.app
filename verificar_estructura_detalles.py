#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla detalles_obra
y entender la relación con inventario
"""

from rexus.core.database import get_inventario_connection

def verificar_estructura():
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        # Verificar estructura de tabla detalles_obra
        print("=== ESTRUCTURA TABLA detalles_obra ===")
        cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'detalles_obra'
        ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ La tabla detalles_obra no existe o no tiene columnas")
            
            # Verificar si existe la tabla
            cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME LIKE '%obra%' OR TABLE_NAME LIKE '%detalle%'
            """)
            related_tables = cursor.fetchall()
            print("\n=== TABLAS RELACIONADAS CON OBRAS ===")
            for table in related_tables:
                print(f"- {table[0]}")
                
            conn.close()
            return
            
        for col in columns:
            print(f"{col[0]}: {col[1]} (Nullable: {col[2]}, Default: {col[3]})")
        
        print("\n=== DATOS DE EJEMPLO ===")
        cursor.execute("SELECT TOP 5 * FROM detalles_obra")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(row)
        else:
            print("❌ No hay datos en la tabla detalles_obra")
            
        # Verificar estructura de inventario_perfiles
        print("\n=== ESTRUCTURA TABLA inventario_perfiles ===")
        cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'inventario_perfiles'
        ORDER BY ORDINAL_POSITION
        """)
        inv_columns = cursor.fetchall()
        
        for col in inv_columns:
            print(f"{col[0]}: {col[1]} (Nullable: {col[2]}, Default: {col[3]})")
            
        # Verificar si hay campos que conecten ambas tablas
        print("\n=== ANÁLISIS DE RELACIONES ===")
        detalle_cols = [col[0] for col in columns]
        inv_cols = [col[0] for col in inv_columns]
        
        print(f"Columnas en detalles_obra: {detalle_cols}")
        print(f"Columnas en inventario_perfiles: {inv_cols}")
        
        # Buscar campos comunes
        campos_comunes = set(detalle_cols) & set(inv_cols)
        if campos_comunes:
            print(f"Campos comunes: {campos_comunes}")
        else:
            print("❌ No hay campos comunes evidentes")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_estructura()
