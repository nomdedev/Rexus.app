-- select_productos_stock_bajo_por_tipo.sql
-- Obtiene productos con stock bajo filtrados por tipo
-- Parámetros: ? (tipo_producto)

SELECT *, 
       (stock_minimo - stock) as deficit
FROM productos
WHERE stock <= stock_minimo 
  AND activo = 1 
  AND estado = 'ACTIVO'
  AND tipo_producto = ?
ORDER BY (stock_minimo - stock) DESC, nombre