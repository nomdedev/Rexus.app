#!/usr/bin/env python3
"""
Script para agregar materiales variados a las obras existentes
"""

from rexus.core.database import get_inventario_connection

def agregar_materiales_obras():
    """Agregar materiales diversos a las obras existentes"""
    
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        print("=== AGREGANDO MATERIALES A OBRAS ===\n")
        
        # Datos de materiales para cada obra
        materiales_por_obra = {
            2: [  # Edificio Central
                ("Perfil de aluminio 80x60", "Perfiles", 40, 32.50, 1300.00),
                ("Vidrio laminado 4+4", "Vidrios", 25, 95.00, 2375.00),
                ("Herraje cerradura multipunto", "Herrajes", 15, 85.50, 1282.50),
                ("Sellador silicona estructural", "Accesorios", 8, 22.75, 182.00),
                ("Burletes EPDM negro", "Accesorios", 120, 8.90, 1068.00),
                ("Tornillería inoxidable M6", "Herrajes", 200, 1.25, 250.00),
                ("Marco de aluminio reforzado", "Perfiles", 18, 45.00, 810.00),
                ("Vidrio templado 8mm", "Vidrios", 12, 110.00, 1320.00)
            ],
            3: [  # Torre Norte
                ("Perfil de aluminio 100x50", "Perfiles", 60, 38.75, 2325.00),
                ("Vidrio doble hermético", "Vidrios", 35, 125.00, 4375.00),
                ("Herraje bisagra reforzada", "Herrajes", 45, 28.50, 1282.50),
                ("Cortina de aire automática", "Accesorios", 6, 180.00, 1080.00),
                ("Burletes de alta performance", "Accesorios", 85, 12.40, 1054.00),
                ("Manijas ergonómicas premium", "Herrajes", 20, 65.00, 1300.00),
                ("Travesaños estructurales", "Perfiles", 25, 28.90, 722.50),
                ("Vidrio control solar", "Vidrios", 18, 145.00, 2610.00)
            ],
            4: [  # Residencial Sur
                ("Perfil de aluminio 70x40", "Perfiles", 35, 25.80, 903.00),
                ("Vidrio templado claro", "Vidrios", 22, 88.00, 1936.00),
                ("Herraje cerradura estándar", "Herrajes", 18, 45.50, 819.00),
                ("Mosquiteros enrollables", "Accesorios", 12, 75.00, 900.00),
                ("Burletes económicos", "Accesorios", 90, 5.50, 495.00),
                ("Tornillería galvanizada", "Herrajes", 150, 0.85, 127.50),
                ("Perfiles decorativos", "Perfiles", 28, 18.90, 529.20),
                ("Vidrio esmerilado", "Vidrios", 8, 95.00, 760.00)
            ]
        }
        
        # Insertar materiales para cada obra
        total_insertados = 0
        
        for obra_id, materiales in materiales_por_obra.items():
            # Obtener nombre de la obra
            cursor.execute("SELECT nombre FROM obras WHERE id = ?", (obra_id,))
            obra_nombre = cursor.fetchone()[0]
            
            print(f"📋 OBRA {obra_id}: {obra_nombre}")
            print("-" * 50)
            
            obra_total = 0
            
            for detalle, categoria, cantidad, precio_unit, precio_total in materiales:
                try:
                    cursor.execute("""
                        INSERT INTO detalles_obra (obra_id, detalle, categoria, cantidad, precio_unitario, precio_total)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (obra_id, detalle, categoria, cantidad, precio_unit, precio_total))
                    
                    print(f"  ✅ {detalle} ({categoria})")
                    print(f"     Cantidad: {cantidad}, Precio: ${precio_unit}, Total: ${precio_total}")
                    
                    obra_total += precio_total
                    total_insertados += 1
                    
                except Exception as e:
                    print(f"  ❌ Error insertando {detalle}: {e}")
            
            print(f"  💰 TOTAL OBRA: ${obra_total:,.2f}")
            print()
        
        # Confirmar cambios
        conn.commit()
        
        print(f"✅ RESUMEN FINAL:")
        print(f"   Total materiales insertados: {total_insertados}")
        
        # Verificar totales por obra
        cursor.execute("""
            SELECT o.id, o.nombre, COUNT(d.id) as materiales, SUM(d.precio_total) as total
            FROM obras o
            LEFT JOIN detalles_obra d ON o.id = d.obra_id
            WHERE o.id IN (2, 3, 4)
            GROUP BY o.id, o.nombre
            ORDER BY o.id
        """)
        
        resumen = cursor.fetchall()
        print("\n📊 RESUMEN POR OBRA:")
        print("-" * 60)
        
        total_general = 0
        for obra_id, nombre, cant_materiales, total_obra in resumen:
            total_obra = total_obra or 0
            print(f"   Obra {obra_id} ({nombre}): {cant_materiales} materiales - ${total_obra:,.2f}")
            total_general += total_obra
        
        print("-" * 60)
        print(f"   TOTAL GENERAL: ${total_general:,.2f}")
        
        conn.close()
        print("\n🎉 ¡Datos agregados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agregar_materiales_obras()
