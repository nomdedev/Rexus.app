#!/usr/bin/env python3
"""
Verificador de Estructura de Tablas - Rexus.app
==============================================

Script para verificar la estructura real de las tablas en las bases de datos
y corregir los nombres de columnas para la creación de índices.
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Módulos de base de datos no disponibles: {e}")
    DATABASE_AVAILABLE = False

def obtener_columnas_tabla(conexion, tabla_nombre: str):
    """Obtiene las columnas de una tabla específica"""
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (tabla_nombre,))
        
        columnas = cursor.fetchall()
        cursor.close()
        return columnas
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo columnas de {tabla_nombre}: {e}")
        return []

def listar_tablas(conexion):
    """Lista todas las tablas en la base de datos"""
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tablas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tablas
        
    except Exception as e:
        print(f"[ERROR] Error listando tablas: {e}")
        return []

def verificar_base_datos(db_name: str, get_connection_func):
    """Verifica la estructura de una base de datos"""
    
    print(f"\n{'='*50}")
    print(f"[DATABASE] Verificando estructura: {db_name.upper()}")
    print(f"{'='*50}")
    
    try:
        # Obtener conexión
        conexion = get_connection_func()
        if not conexion:
            print(f"[ERROR] No se pudo conectar a {db_name}")
            return
        
        # Listar todas las tablas
        tablas = listar_tablas(conexion)
        print(f"[INFO] Encontradas {len(tablas)} tablas en {db_name}")
        
        # Tablas de interés para índices
        tablas_interes = ['usuarios', 'users', 'productos', 'obras', 'pedidos', 'herrajes', 'vidrios', 'compras', 'audit_log', 'auditoria']
        
        for tabla in tablas:
            if tabla.lower() in [t.lower() for t in tablas_interes]:
                print(f"\n[TABLE] {tabla}")
                columnas = obtener_columnas_tabla(conexion, tabla)
                
                if columnas:
                    print(f"  Columnas ({len(columnas)}):")
                    for col_name, data_type, nullable, default in columnas:
                        null_str = "NULL" if nullable == "YES" else "NOT NULL"
                        default_str = f" DEFAULT {default}" if default else ""
                        print(f"    - {col_name}: {data_type} {null_str}{default_str}")
                else:
                    print(f"    Sin columnas encontradas")
        
        conexion.close()
        
    except Exception as e:
        print(f"[ERROR] Error verificando {db_name}: {e}")

def main():
    """Función principal"""
    
    print("[TABLE STRUCTURE] Verificando estructura de tablas - Rexus.app")
    print("=" * 70)
    
    if not DATABASE_AVAILABLE:
        print("[ERROR] Módulos de base de datos no disponibles")
        return
    
    # Bases de datos a verificar
    databases = {
        "users": get_users_connection,
        "inventario": get_inventario_connection,
        "auditoria": get_auditoria_connection
    }
    
    # Verificar cada base de datos
    for db_name, connection_func in databases.items():
        verificar_base_datos(db_name, connection_func)
    
    print("\n" + "=" * 70)
    print("[COMPLETE] Verificación de estructura completada")

if __name__ == "__main__":
    main()