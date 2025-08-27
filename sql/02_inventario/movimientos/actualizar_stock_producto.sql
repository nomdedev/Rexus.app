-- actualizar_stock_producto.sql
-- Actualiza el stock actual de un producto en inventario
-- Parámetros: ? (nuevo_stock), ? (producto_id)

UPDATE inventario 
SET stock_actual = ?, 
    fecha_modificacion = GETDATE() 
WHERE id = ?