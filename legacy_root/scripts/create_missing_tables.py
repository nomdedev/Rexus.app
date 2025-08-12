#!/usr/bin/env python
"""
Script para crear las tablas faltantes en la base de datos
Específicamente: compras y detalle_compras
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.database import get_inventario_connection

def create_missing_tables():
    """Crea las tablas faltantes en la base de datos"""
    print("=== Creando tablas faltantes ===")
    
    # Obtener conexión a la base de datos
    try:
        conn = get_inventario_connection()
        if not conn:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor()
        print("[OK] Conexion a base de datos establecida")
        
        # Leer script de compras
        script_path = root_dir / "scripts" / "database" / "compras_complete_tables.sql"
        
        if not script_path.exists():
            print(f"[ERROR] Script no encontrado en {script_path}")
            return False
        
        print(f"[INFO] Leyendo script: {script_path}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir el script en comandos individuales
        commands = sql_content.split('GO')  # SQL Server utiliza GO como separador
        if len(commands) == 1:
            # Si no hay GO, dividir por punto y coma
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        success_count = 0
        total_commands = 0
        
        for command in commands:
            command = command.strip()
            if not command or command.startswith('--'):
                continue
                
            total_commands += 1
            
            try:
                # Ejecutar cada comando por separado
                cursor.execute(command)
                print(f"[OK] Comando ejecutado exitosamente")
                success_count += 1
                
            except Exception as e:
                # Algunos errores son esperados (como tablas ya existentes)
                if "already exists" in str(e) or "ya existe" in str(e):
                    print(f"[INFO] Tabla ya existe (esperado): {str(e)}")
                    success_count += 1
                else:
                    print(f"[WARNING] Error ejecutando comando: {str(e)}")
                    
        # Confirmar transacciones
        conn.commit()
        print(f"[OK] Transacciones confirmadas")
        
        # Verificar que las tablas existen ahora
        print("\n=== Verificando tablas creadas ===")
        
        tables_to_check = ['compras', 'detalle_compras', 'proveedores']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"[OK] Tabla '{table}' existe - {count} registros")
            except Exception as e:
                print(f"[ERROR] Tabla '{table}' no existe: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n=== Resumen ===")
        print(f"Comandos ejecutados exitosamente: {success_count}/{total_commands}")
        print("[OK] Proceso completado")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_tables()
    sys.exit(0 if success else 1)