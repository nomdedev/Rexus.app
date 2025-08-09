"""
Script para actualizar la estructura de la tabla obras
Agrega las columnas faltantes que necesita el modelo refactorizado.
"""

import sys
import os

# Agregar el directorio raíz al path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.insert(0, root_dir)

from rexus.core.database import get_inventario_connection


def verificar_y_agregar_columnas():
    """Verificar y agregar columnas faltantes a la tabla obras."""
    
    try:
        db_conn = get_inventario_connection(auto_connect=True)
        connection = db_conn.connection
        cursor = connection.cursor()
        
        print("🔧 [DB UPDATE] Verificando y agregando columnas faltantes...")
        
        # Mapeo de columnas: modelo_esperado -> real_existente_o_nueva
        mapeo_columnas = {
            # Columnas que ya existen con nombre similar
            'codigo_obra': 'codigo',  # Ya existe como 'codigo'
            'cliente_id': 'cliente',  # Ya existe como 'cliente' (texto)
            'presupuesto_inicial': 'presupuesto_total',  # Ya existe
            'fecha_fin_real': None,  # Crear nueva
            'etapa_actual': None,  # Crear nueva
            'porcentaje_completado': 'progreso',  # Ya existe como 'progreso'
            'costo_actual': None,  # Crear nueva
            'margen_estimado': None,  # Crear nueva
            'responsable_obra': 'responsable',  # Ya existe
            'activo': None,  # Crear nueva - CRÍTICA
            'fecha_actualizacion': 'updated_at',  # Ya existe
        }
        
        # Columnas que necesitamos crear
        columnas_nuevas = [
            ("activo", "BIT NOT NULL DEFAULT 1", "Campo para soft delete"),
            ("fecha_fin_real", "DATE NULL", "Fecha real de finalización"),
            ("etapa_actual", "NVARCHAR(50) NULL DEFAULT 'PLANIFICACION'", "Etapa actual del proyecto"),
            ("costo_actual", "DECIMAL(18,2) NULL DEFAULT 0", "Costo actual acumulado"),
            ("margen_estimado", "DECIMAL(5,2) NULL DEFAULT 0", "Margen de ganancia estimado")
        ]
        
        # Verificar qué columnas ya existen
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'obras'
        """)
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        print(f"📋 [DB UPDATE] Columnas existentes: {len(columnas_existentes)}")
        
        # Agregar columnas faltantes
        for nombre_col, tipo_col, descripcion in columnas_nuevas:
            if nombre_col not in columnas_existentes:
                try:
                    sql_alter = f"ALTER TABLE obras ADD {nombre_col} {tipo_col}"
                    print(f"   ➕ Agregando columna: {nombre_col} ({descripcion})")
                    cursor.execute(sql_alter)
                    connection.commit()
                    print(f"   [CHECK] Columna '{nombre_col}' agregada correctamente")
                except Exception as e:
                    print(f"   [ERROR] Error agregando '{nombre_col}': {e}")
            else:
                print(f"   [WARN] Columna '{nombre_col}' ya existe")
        
        # Verificar que las obras existentes tengan valores por defecto
        print("\n🔄 [DB UPDATE] Actualizando valores por defecto en obras existentes...")
        
        # Contar obras antes de actualizar
        cursor.execute("SELECT COUNT(*) FROM obras")
        total_obras = cursor.fetchone()[0]
        print(f"   [CHART] Total de obras a actualizar: {total_obras}")
        
        if total_obras > 0:
            # Actualizar obras existentes con valores por defecto
            updates = [
                ("activo", "1", "Marcar todas las obras como activas"),
                ("etapa_actual", "'PLANIFICACION'", "Establecer etapa por defecto"),
                ("costo_actual", "0", "Inicializar costo actual"),
                ("margen_estimado", "15.0", "Establecer margen por defecto del 15%")
            ]
            
            for campo, valor, desc in updates:
                try:
                    if campo in [col[0] for col in columnas_nuevas]:
                        sql_update = f"UPDATE obras SET {campo} = {valor} WHERE {campo} IS NULL"
                        cursor.execute(sql_update)
                        filas_afectadas = cursor.rowcount
                        connection.commit()
                        print(f"   [CHECK] {desc}: {filas_afectadas} filas actualizadas")
                except Exception as e:
                    print(f"   [ERROR] Error actualizando {campo}: {e}")
        
        # Verificar estructura final
        print("\n📋 [DB UPDATE] Verificando estructura final...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'obras'
            ORDER BY ORDINAL_POSITION
        """)
        columnas_finales = cursor.fetchall()
        print(f"   [CHART] Total de columnas después: {len(columnas_finales)}")
        
        # Mostrar mapeo final
        print(f"\n🗺️ [DB UPDATE] Mapeo de columnas modelo -> base de datos:")
        mapeos_finales = {
            'id': 'id',
            'codigo_obra': 'codigo',
            'nombre': 'nombre',
            'descripcion': 'descripcion',
            'cliente_id': 'cliente',
            'fecha_inicio': 'fecha_inicio',
            'fecha_fin_estimada': 'fecha_fin_estimada',
            'fecha_fin_real': 'fecha_fin_real',
            'etapa_actual': 'etapa_actual',
            'estado': 'estado',
            'porcentaje_completado': 'progreso',
            'presupuesto_inicial': 'presupuesto_total',
            'costo_actual': 'costo_actual',
            'margen_estimado': 'margen_estimado',
            'ubicacion': 'ubicacion',
            'responsable_obra': 'responsable',
            'observaciones': 'observaciones',
            'activo': 'activo',
            'fecha_creacion': 'created_at',
            'fecha_actualizacion': 'updated_at'
        }
        
        for modelo, bd in mapeos_finales.items():
            print(f"   {modelo} -> {bd}")
        
        cursor.close()
        print(f"\n[CHECK] [DB UPDATE] Actualización de estructura completada")
        return True
        
    except Exception as e:
        print(f"[ERROR] [DB UPDATE] Error actualizando estructura: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal."""
    print("[ROCKET] [DB UPDATE] Iniciando actualización de estructura de tabla obras...")
    print("=" * 70)
    
    success = verificar_y_agregar_columnas()
    
    print("=" * 70)
    if success:
        print("[CHECK] [DB UPDATE] Actualización completada exitosamente")
        return 0
    else:
        print("[ERROR] [DB UPDATE] Actualización falló")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
