#!/usr/bin/env python3
"""
Script para crear las tablas adicionales requeridas
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def crear_tablas():
    """Crea las tablas adicionales ejecutando el script SQL."""
    print("CREANDO TABLAS ADICIONALES - REXUS.APP")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        # Conectar a la base de datos
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexion a base de datos exitosa")
        
        # Leer el archivo SQL
        script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'database', 'crear_tablas_adicionales.sql')
        
        if not os.path.exists(script_path):
            print(f"[ERROR] No se encontro el archivo: {script_path}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("[OK] Script SQL cargado exitosamente")
        
        # Dividir el script en comandos individuales
        commands = sql_script.split('GO')
        
        cursor = db.cursor()
        executed_commands = 0
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--') and command != '':
                try:
                    cursor.execute(command)
                    executed_commands += 1
                except Exception as e:
                    if "already exists" in str(e) or "ya existe" in str(e):
                        print(f"[INFO] Elemento ya existe: {str(e)[:100]}...")
                    else:
                        print(f"[WARNING] Error ejecutando comando: {str(e)[:100]}...")
        
        db.commit()
        cursor.close()
        
        print(f"[OK] Script ejecutado exitosamente")
        print(f"[OK] Comandos ejecutados: {executed_commands}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creando tablas: {e}")
        return False

def verificar_tablas_creadas():
    """Verifica que las tablas se hayan creado correctamente."""
    print("\n" + "=" * 60)
    print("VERIFICANDO TABLAS CREADAS")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        
        # Tablas que deberían existir
        tablas_esperadas = [
            'empleados', 'departamentos', 'asistencias', 'nomina', 'bonos_descuentos', 'historial_laboral',
            'libro_contable', 'recibos', 'pagos_obra', 'pagos_materiales',
            'equipos', 'herramientas', 'mantenimientos', 'programacion_mantenimiento', 'tipos_mantenimiento',
            'estado_equipos', 'historial_mantenimiento',
            'transportes', 'entregas', 'detalle_entregas',
            'configuracion_sistema', 'parametros_modulos', 'auditoria_cambios', 'logs_sistema'
        ]
        
        # Obtener todas las tablas existentes
        cursor.execute("SELECT name FROM sysobjects WHERE xtype='U' ORDER BY name")
        tablas_existentes = [row[0] for row in cursor.fetchall()]
        
        print(f"Total de tablas en la base de datos: {len(tablas_existentes)}")
        
        # Verificar cada tabla esperada
        creadas = 0
        for tabla in tablas_esperadas:
            if tabla in tablas_existentes:
                print(f"[OK] {tabla}")
                creadas += 1
            else:
                print(f"[FALTA] {tabla}")
        
        print(f"\nEstadisticas:")
        print(f"  Tablas esperadas: {len(tablas_esperadas)}")
        print(f"  Tablas creadas: {creadas}")
        print(f"  Porcentaje: {(creadas/len(tablas_esperadas)*100):.1f}%")
        
        cursor.close()
        
        return creadas == len(tablas_esperadas)
        
    except Exception as e:
        print(f"[ERROR] Error verificando tablas: {e}")
        return False

def main():
    """Función principal."""
    print("INICIO DEL PROCESO DE CREACION DE TABLAS")
    print("=" * 60)
    
    # Crear tablas
    if crear_tablas():
        print("\n[OK] Tablas creadas exitosamente")
    else:
        print("\n[ERROR] Error creando tablas")
        return
    
    # Verificar tablas
    if verificar_tablas_creadas():
        print("\n[EXITO] Todas las tablas fueron creadas correctamente")
    else:
        print("\n[ATENCION] Algunas tablas pueden no haberse creado")
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()