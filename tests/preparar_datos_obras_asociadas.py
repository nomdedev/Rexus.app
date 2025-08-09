#!/usr/bin/env python3
"""
Script para verificar y preparar datos de prueba para obras asociadas
"""

from rexus.core.database import get_inventario_connection

def verificar_y_preparar_datos():
    try:
        conn = get_inventario_connection()
        cursor = conn.cursor()
        
        # Verificar estructura de tabla obras
        print("=== ESTRUCTURA TABLA OBRAS ===")
        cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'obras'
        ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"- {col[0]}")
        
        # Verificar datos existentes en obras
        print("\n=== OBRAS EXISTENTES ===")
        cursor.execute("SELECT id, nombre FROM obras")
        obras = cursor.fetchall()
        
        if not obras:
            print("[ERROR] No hay obras en la base de datos")
            return
            
        for obra in obras:
            print(f"ID: {obra[0]}, Nombre: {obra[1]}")
        
        # Verificar si ya hay detalles_obra
        cursor.execute("SELECT COUNT(*) FROM detalles_obra")
        count_detalles = cursor.fetchone()[0]
        print(f"\nRegistros existentes en detalles_obra: {count_detalles}")
        
        if count_detalles == 0:
            # Insertar datos de prueba usando IDs de obras que existen
            obra_ids = [obra[0] for obra in obras[:3]]  # Usar máximo 3 obras
            
            test_data = [
                (obra_ids[0], 'Perfil de aluminio 60x40', 'Perfiles', 50, 25.50, 1275.00),
                (obra_ids[0], 'Vidrio templado 6mm', 'Vidrios', 10, 80.00, 800.00),
            ]
            
            if len(obra_ids) > 1:
                test_data.append((obra_ids[1], 'Perfil de aluminio 60x40', 'Perfiles', 30, 25.50, 765.00))
            
            if len(obra_ids) > 2:
                test_data.append((obra_ids[2], 'Herraje bisagra europea', 'Herrajes', 20, 15.75, 315.00))
            
            print("\n=== INSERTANDO DATOS DE PRUEBA ===")
            for obra_id, detalle, categoria, cantidad, precio_unit, precio_total in test_data:
                cursor.execute('''
                    INSERT INTO detalles_obra (obra_id, detalle, categoria, cantidad, precio_unitario, precio_total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (obra_id, detalle, categoria, cantidad, precio_unit, precio_total))
                print(f"[CHECK] Insertado: {detalle} para obra ID {obra_id}")
            
            conn.commit()
            print("[CHECK] Datos de prueba insertados exitosamente")
        
        # Verificar los datos finales
        print("\n=== VERIFICACIÓN FINAL ===")
        cursor.execute("""
        SELECT o.id, o.nombre, d.detalle, d.categoria, d.cantidad, d.precio_total
        FROM obras o
        INNER JOIN detalles_obra d ON o.id = d.obra_id
        ORDER BY o.id, d.detalle
        """)
        
        relaciones = cursor.fetchall()
        for rel in relaciones:
            obra_id, obra_nombre, detalle, categoria, cantidad, precio_total = rel
            print(f"Obra {obra_id} ({obra_nombre}): {detalle} ({categoria}) - Cant: {cantidad}, Total: ${precio_total}")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_y_preparar_datos()
