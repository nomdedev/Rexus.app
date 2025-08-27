-- update_stock_producto.sql
-- Actualiza el stock de un producto
-- Parámetros: ? (nuevo_stock), ? (usuario_modificacion), ? (producto_id)

UPDATE productos
SET stock = ?, 
    fecha_modificacion = GETDATE(), 
    usuario_modificacion = ?
WHERE id = ?