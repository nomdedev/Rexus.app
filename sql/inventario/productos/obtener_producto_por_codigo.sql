-- Obtener producto por código
-- Archivo: obtener_producto_por_codigo.sql
-- Módulo: Inventario/Productos
-- Descripción: Busca producto por código exacto

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
    fecha_modificacion
FROM [inventario]
WHERE LOWER(codigo) = LOWER(@codigo) AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, {'codigo': codigo_sanitizado})
-- return cursor.fetchone()
