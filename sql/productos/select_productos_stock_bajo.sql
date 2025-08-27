-- select_productos_stock_bajo.sql
-- Obtiene productos con stock bajo (stock <= stock_minimo)
-- Parámetros opcionales: :tipo_producto (si se filtra por tipo)

SELECT *, 
       (stock_minimo - stock) as deficit
FROM productos
WHERE stock <= stock_minimo 
  AND activo = 1 
  AND estado = 'ACTIVO'
ORDER BY (stock_minimo - stock) DESC, nombre