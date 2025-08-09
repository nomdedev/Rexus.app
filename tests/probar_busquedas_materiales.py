#!/usr/bin/env python3
"""
Probar la funcionalidad de obras asociadas con los nuevos datos
"""

from rexus.core.database import get_inventario_connection

def probar_obras_asociadas():
    """Probar búsquedas de materiales en diferentes obras"""
    
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        # Materiales de prueba para buscar
        materiales_prueba = [
            ("Perfil", "Perfiles"),
            ("Vidrio", "Vidrios"), 
            ("Herraje", "Herrajes"),
            ("Burletes", "Accesorios"),
            ("templado", "Vidrios"),
            ("aluminio", "Perfiles")
        ]
        
        print("🔍 PROBANDO BÚSQUEDAS DE MATERIALES EN OBRAS\n")
        
        for termino, categoria_esperada in materiales_prueba:
            print(f"📋 Buscando: '{termino}' (esperando categoría: {categoria_esperada})")
            print("-" * 60)
            
            # Query igual que la del diálogo
            query = """
            SELECT DISTINCT 
                o.id as obra_id,
                o.nombre as obra_nombre,
                d.detalle,
                d.categoria,
                d.cantidad,
                d.precio_unitario,
                d.precio_total
            FROM obras o
            INNER JOIN detalles_obra d ON o.id = d.obra_id
            WHERE (
                d.detalle LIKE ? OR 
                d.categoria LIKE ? OR
                d.detalle LIKE ?
            )
            ORDER BY o.nombre, d.detalle
            """
            
            like_pattern = f"%{termino}%"
            cursor.execute(query, (like_pattern, like_pattern, like_pattern))
            resultados = cursor.fetchall()
            
            if resultados:
                obras_encontradas = set()
                total_cantidad = 0
                total_importe = 0
                
                for resultado in resultados:
                    obra_id, obra_nombre, detalle, categoria, cantidad, precio_unit, precio_total = resultado
                    obras_encontradas.add(f"{obra_id}: {obra_nombre}")
                    
                    print(f"   🏗️  {obra_nombre} (ID: {obra_id})")
                    print(f"      📦 {detalle} ({categoria})")
                    print(f"      [CHART] Cantidad: {cantidad}, Precio: ${precio_unit}, Total: ${precio_total}")
                    print()
                    
                    if cantidad:
                        total_cantidad += float(cantidad)
                    if precio_total:
                        total_importe += float(precio_total)
                
                print(f"   [CHECK] RESUMEN: {len(resultados)} materiales en {len(obras_encontradas)} obras")
                print(f"   [CHART] Total cantidad: {total_cantidad}, Total importe: ${total_importe:,.2f}")
                
            else:
                print("   [ERROR] No se encontraron materiales con ese término")
            
            print("\n" + "="*70 + "\n")
        
        # Estadísticas generales
        print("📈 ESTADÍSTICAS GENERALES")
        print("-" * 40)
        
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as cantidad_tipos,
                SUM(cantidad) as cantidad_total,
                SUM(precio_total) as importe_total
            FROM detalles_obra
            GROUP BY categoria
            ORDER BY importe_total DESC
        """)
        
        stats = cursor.fetchall()
        
        for categoria, tipos, cant_total, importe_total in stats:
            print(f"   {categoria}: {tipos} tipos, {cant_total} unidades, ${importe_total:,.2f}")
        
        conn.close()
        print("\n[CHECK] Pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_obras_asociadas()
