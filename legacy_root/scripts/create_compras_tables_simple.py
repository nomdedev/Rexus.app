#!/usr/bin/env python
"""
Script simple para crear las tablas compras y detalle_compras
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.database import get_inventario_connection

def create_compras_tables():
    """Crea las tablas compras y detalle_compras"""
    print("=== Creando tablas de compras ===")
    
    try:
        conn = get_inventario_connection()
        if not conn:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor()
        print("[OK] Conexion a base de datos establecida")
        
        # Leer script simplificado
        script_path = root_dir / "scripts" / "database" / "compras_simple.sql"
        
        if not script_path.exists():
            print(f"[ERROR] Script no encontrado en {script_path}")
            return False
        
        print(f"[INFO] Leyendo script: {script_path}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar todo el script de una vez
        try:
            cursor.execute(sql_content)
            print("[OK] Script ejecutado exitosamente")
            
        except Exception as e:
            print(f"[ERROR] Error ejecutando script: {str(e)}")
            return False
                    
        # Confirmar transacciones
        conn.commit()
        print("[OK] Transacciones confirmadas")
        
        # Verificar que las tablas existen ahora
        print("\n=== Verificando tablas creadas ===")
        
        tables_to_check = ['compras', 'detalle_compras']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"[OK] Tabla '{table}' existe - {count} registros")
            except Exception as e:
                print(f"[ERROR] Tabla '{table}' no existe: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n[OK] Proceso completado exitosamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

if __name__ == "__main__":
    success = create_compras_tables()
    sys.exit(0 if success else 1)