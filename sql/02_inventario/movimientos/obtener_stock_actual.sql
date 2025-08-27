-- obtener_stock_actual.sql
-- Obtiene el stock actual de un producto
-- Parámetros: ? (producto_id)

SELECT stock_actual 
FROM inventario 
WHERE id = ?