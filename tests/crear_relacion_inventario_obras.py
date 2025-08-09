#!/usr/bin/env python3
"""
Script para crear una relación directa entre inventario y obras
mediante códigos específicos
"""

from rexus.core.database import get_inventario_connection

def crear_relacion_inventario_obras():
    """Crear relación directa entre códigos de inventario y obras"""
    
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        print("🔗 CREANDO RELACIÓN DIRECTA INVENTARIO-OBRAS")
        print("-" * 50)
        
        # 1. Agregar columna codigo_inventario a detalles_obra si no existe
        print("1. Verificando estructura de tabla detalles_obra...")
        
        try:
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'detalles_obra' AND COLUMN_NAME = 'codigo_inventario'
            """)
            
            if not cursor.fetchall():
                print("   Agregando columna codigo_inventario...")
                cursor.execute("""
                    ALTER TABLE detalles_obra 
                    ADD codigo_inventario VARCHAR(50) NULL
                """)
                conn.commit()
                print("   [CHECK] Columna codigo_inventario agregada")
            else:
                print("   [CHECK] Columna codigo_inventario ya existe")
                
        except Exception as e:
            print(f"   [ERROR] Error modificando tabla: {e}")
        
        # 2. Crear mapeo entre códigos de inventario y materiales de obras
        print("\n2. Creando mapeo de códigos...")
        
        # Mapeo manual basado en los materiales que agregamos
        mapeos = [
            # Perfiles - usar códigos reales del inventario
            ("554002.376", "Perfil de aluminio 60x40"),
            ("564002.153", "Perfil de aluminio 80x60"), 
            ("564002.131", "Perfil de aluminio 100x50"),
            ("564002.130", "Perfil de aluminio 70x40"),
            ("564002.133", "Marco de aluminio reforzado"),
            ("554002.377", "Travesaños estructurales"),
            ("554002.378", "Perfiles decorativos"),
            
            # Vidrios - usar códigos del inventario
            ("564002.200", "Vidrio templado 6mm"),
            ("564002.201", "Vidrio templado 8mm"),
            ("564002.202", "Vidrio templado claro"),
            ("564002.203", "Vidrio laminado 4+4"),
            ("564002.204", "Vidrio doble hermético"),
            ("564002.205", "Vidrio control solar"),
            ("564002.206", "Vidrio esmerilado"),
            
            # Herrajes - usar códigos del inventario
            ("564002.300", "Herraje cerradura multipunto"),
            ("564002.301", "Herraje cerradura estándar"),
            ("564002.302", "Herraje bisagra reforzada"),
            ("564002.303", "Herraje bisagra europea"),
            ("564002.304", "Manijas ergonómicas premium"),
            ("564002.305", "Tornillería inoxidable M6"),
            ("564002.306", "Tornillería galvanizada"),
            
            # Accesorios - usar códigos del inventario
            ("564002.400", "Burletes EPDM negro"),
            ("564002.401", "Burletes de alta performance"),
            ("564002.402", "Burletes económicos"),
            ("564002.403", "Sellador silicona estructural"),
            ("564002.404", "Cortina de aire automática"),
            ("564002.405", "Mosquiteros enrollables")
        ]
        
        # 3. Actualizar detalles_obra con códigos de inventario
        print("3. Actualizando detalles_obra con códigos...")
        
        updates_realizados = 0
        
        for codigo, detalle_buscar in mapeos:
            cursor.execute("""
                UPDATE detalles_obra 
                SET codigo_inventario = ?
                WHERE detalle LIKE ? AND codigo_inventario IS NULL
            """, (codigo, f"%{detalle_buscar}%"))
            
            affected = cursor.rowcount
            if affected > 0:
                print(f"   [CHECK] {codigo} -> {detalle_buscar} ({affected} registros)")
                updates_realizados += affected
        
        conn.commit()
        
        # 4. Verificar resultado
        print(f"\n4. Verificación final:")
        print(f"   Total updates realizados: {updates_realizados}")
        
        cursor.execute("""
            SELECT 
                codigo_inventario, 
                detalle, 
                COUNT(*) as cantidad
            FROM detalles_obra 
            WHERE codigo_inventario IS NOT NULL
            GROUP BY codigo_inventario, detalle
            ORDER BY codigo_inventario
        """)
        
        resultados = cursor.fetchall()
        
        print(f"   Registros con código asignado: {len(resultados)}")
        
        for codigo, detalle, cant in resultados[:10]:  # Mostrar solo primeros 10
            print(f"   📋 {codigo}: {detalle} ({cant} obras)")
        
        if len(resultados) > 10:
            print(f"   ... y {len(resultados) - 10} más")
        
        conn.close()
        print("\n🎉 ¡Relación inventario-obras creada exitosamente!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_relacion_inventario_obras()
