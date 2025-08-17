-- Obtener producto por ID
-- Archivo: obtener_producto_por_id.sql
-- Módulo: Inventario/Productos
-- Descripción: Obtiene un producto específico con todos sus datos

SELECT 
    id,
    codigo,
    descripcion,
    categoria,
    unidad_medida,
    precio_compra,
    precio_venta,
    stock_actual,
    stock_minimo,
    ubicacion,
    observaciones,
    qr_data,
    fecha_creacion,
    fecha_modificacion,
    activo
FROM [inventario]
WHERE id = @producto_id AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'producto_id': producto_id})
-- return cursor.fetchone()
