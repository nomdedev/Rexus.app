#!/usr/bin/env python3
"""
Test simplificado para verificar que la query de obras asociadas funciona
"""

from rexus.core.database import get_inventario_connection

def test_query_obras_asociadas():
    """Probar directamente la query que usará el diálogo"""
    
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        # Simular los datos de un ítem del inventario
        item_descripcion = "Perfil de aluminio"
        item_categoria = "Perfiles"
        
        print(f"🔍 Buscando obras que usen: {item_descripcion} (categoría: {item_categoria})")
        
        # Query que usa el diálogo
        query = """
        SELECT DISTINCT 
            o.id as obra_id,
            o.nombre as obra_nombre,
            d.cantidad,
            d.precio_unitario,
            d.precio_total,
            'Activa' as estado
        FROM obras o
        INNER JOIN detalles_obra d ON o.id = d.obra_id
        WHERE (
            d.detalle LIKE ? OR 
            d.categoria LIKE ? OR
            d.detalle LIKE ?
        )
        ORDER BY o.nombre
        """
        
        # Parámetros de búsqueda
        like_codigo = f"%{item_descripcion}%"
        like_categoria = f"%{item_categoria}%"
        like_descripcion = f"%{item_descripcion}%"
        
        cursor.execute(query, (like_codigo, like_categoria, like_descripcion))
        obras = cursor.fetchall()
        
        print(f"\n✅ Encontradas {len(obras)} relaciones:")
        
        if obras:
            total_cantidad = 0
            total_importe = 0
            
            for obra in obras:
                obra_id, obra_nombre, cantidad, precio_unit, precio_total, estado = obra
                print(f"   📋 Obra {obra_id}: {obra_nombre}")
                print(f"      Cantidad: {cantidad}, Precio Unit: ${precio_unit}, Total: ${precio_total}")
                
                if cantidad:
                    total_cantidad += float(cantidad)
                if precio_total:
                    total_importe += float(precio_total)
            
            print(f"\n📊 RESUMEN:")
            print(f"   Total cantidad usada: {total_cantidad}")
            print(f"   Total importe: ${total_importe:.2f}")
            print(f"   Obras que lo usan: {len(obras)}")
            
        else:
            print("❌ No se encontraron obras que usen este material")
            
            # Verificar qué hay en detalles_obra
            cursor.execute("SELECT detalle, categoria FROM detalles_obra")
            detalles = cursor.fetchall()
            print(f"\n📋 Detalles disponibles en BD:")
            for detalle in detalles:
                print(f"   - {detalle[0]} ({detalle[1]})")
        
        conn.close()
        print("\n✅ Test de query completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_obras_asociadas()
