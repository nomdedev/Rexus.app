#!/usr/bin/env python3
"""
Script para eliminar la tabla usuarios duplicada de la base de datos principal
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para eliminar tabla duplicada"""
    print("ELIMINANDO TABLA USUARIOS DUPLICADA")
    print("=" * 50)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexión a base de datos exitosa")
        
        cursor = db.cursor()
        
        # Verificar si existe la tabla usuarios
        cursor.execute("SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U'")
        if cursor.fetchone():
            print("[ENCONTRADA] Tabla usuarios existe en base principal")
            
            # Eliminar tabla usuarios
            cursor.execute("DROP TABLE usuarios")
            db.commit()
            print("[OK] Tabla usuarios eliminada de la base principal")
        else:
            print("[INFO] No se encontró tabla usuarios en la base principal")
        
        # También eliminar otras tablas relacionadas que pueden causar conflictos
        tablas_a_eliminar = ['roles', 'permisos_usuario', 'modulos']
        
        for tabla in tablas_a_eliminar:
            cursor.execute(f"SELECT * FROM sysobjects WHERE name='{tabla}' AND xtype='U'")
            if cursor.fetchone():
                cursor.execute(f"DROP TABLE {tabla}")
                db.commit()
                print(f"[OK] Tabla {tabla} eliminada")
        
        cursor.close()
        print("\n[COMPLETADO] Limpieza de tablas duplicadas terminada")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()