#!/usr/bin/env python3
"""
Script para verificar esquemas de tablas reales en la base de datos
Compara con lo que el código espera encontrar
"""

import sys
import os
import re
sys.path.append(os.path.abspath('.'))

from rexus.core.database import get_inventario_connection

def check_table_schema(table_name: str):
    """Verifica el esquema de una tabla específica"""
    # Validar nombre de tabla
    if not re.match(r'^[a-zA-Z_]\w*$', table_name):
        print(f"ERROR: Nombre de tabla inválido: {table_name}")
        return
    
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        print(f"=== ESQUEMA DE TABLA: {table_name.upper()} ===")
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ?
        """, (table_name,))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print(f"❌ TABLA '{table_name}' NO EXISTE")
            return False
        
        print(f"✅ Tabla '{table_name}' existe")
        
        # Obtener columnas
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        print(f"\nColumnas encontradas ({len(columns)}):")
        for col in columns:
            name, dtype, nullable, default, max_len = col
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            length_str = f"({max_len})" if max_len else ""
            default_str = f", DEFAULT: {default}" if default else ""
            print(f"  - {name}: {dtype}{length_str} {nullable_str}{default_str}")
        
        # Obtener algunos registros de ejemplo para ver datos reales
        # Usar consulta segura con validación de nombre de tabla
        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")  # nosec B608
        total_records = cursor.fetchone()[0]
        print(f"\nTotal de registros: {total_records}")
        
        if total_records > 0:
            cursor.execute(f"SELECT TOP 3 * FROM [{table_name}]")  # nosec B608
            sample_records = cursor.fetchall()
            print("\nMuestra de datos (primeros 3 registros):")
            
            # Get column names for display
            column_names = [desc[0] for desc in cursor.description]
            print("  Columnas:", ", ".join(column_names))
            
            for i, record in enumerate(sample_records, 1):
                print(f"  Registro {i}: {record}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tabla {table_name}: {e}")
        return False

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Verifica si una columna específica existe en una tabla"""
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
        """, (table_name, column_name))
        
        exists = cursor.fetchone()[0] > 0
        cursor.close()
        
        status = "✅ EXISTE" if exists else "❌ NO EXISTE"
        print(f"Columna '{column_name}' en tabla '{table_name}': {status}")
        
        return exists
        
    except Exception as e:
        print(f"❌ Error verificando columna {table_name}.{column_name}: {e}")
        return False

def main():
    """Verifica esquemas de las tablas principales"""
    print("=== VERIFICACION DE ESQUEMAS DE TABLAS ===\n")
    
    # Tablas que el código espera que existan
    tables_to_check = [
        'inventario',
        'categorias', 
        'obras',
        'usuarios',
        'pedidos_compra',
        'detalle_compras',
        'vidrios',
        'herrajes'
    ]
    
    for table in tables_to_check:
        check_table_schema(table)
        print("\n" + "="*50 + "\n")
    
    # Verificar columnas específicas que el código usa frecuentemente
    print("=== VERIFICACION DE COLUMNAS ESPECIFICAS ===\n")
    
    critical_columns = [
        ('inventario', 'categoria'),
        ('inventario', 'activo'),
        ('inventario', 'stock_actual'),
        ('inventario', 'codigo'),
        ('usuarios', 'usuario'),
        ('usuarios', 'activo'),
        ('obras', 'estado'),
        ('obras', 'activo')
    ]
    
    for table, column in critical_columns:
        check_column_exists(table, column)
    
    print("\n=== VERIFICACION COMPLETADA ===")

if __name__ == "__main__":
    main()