#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla usuarios en la base de datos users
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para verificar estructura"""
    print("VERIFICANDO ESTRUCTURA DE BD USERS")
    print("=" * 50)
    
    try:
        from src.core.database import DatabaseConnection
        
        db = DatabaseConnection('users')
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos users")
            return False
        
        print("[OK] Conexión a base de datos users exitosa")
        
        cursor = db.cursor()
        
        # Verificar estructura de la tabla usuarios
        print("\n[ESTRUCTURA] Tabla usuarios:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'usuarios'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        # Verificar datos de la tabla usuarios
        print(f"\n[DATOS] Usuarios en la tabla:")
        cursor.execute("SELECT TOP 5 * FROM usuarios")
        users = cursor.fetchall()
        
        if users:
            print(f"Total usuarios: {len(users)}")
            for i, user in enumerate(users):
                print(f"  Usuario {i+1}: {user}")
        else:
            print("No hay usuarios en la tabla")
        
        # Verificar si existe tabla de permisos
        print(f"\n[PERMISOS] Verificando tabla de permisos...")
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME LIKE '%permiso%' OR TABLE_NAME LIKE '%roles%'
        """)
        
        perm_tables = cursor.fetchall()
        if perm_tables:
            print("Tablas de permisos encontradas:")
            for table in perm_tables:
                print(f"  - {table[0]}")
        else:
            print("No se encontraron tablas de permisos")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()