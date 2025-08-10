-- Actualización segura de stock de producto
-- Utiliza la tabla consolidada 'productos'
-- Los parámetros se deben pasar usando prepared statements

UPDATE productos SET
    stock_actual = ?,
    stock_disponible = stock_actual - stock_reservado,
    fecha_actualizacion = GETDATE()
WHERE id = ? AND activo = 1;