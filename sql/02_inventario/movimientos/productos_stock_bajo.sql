-- productos_stock_bajo.sql
-- Obtiene productos con stock por debajo del mínimo
-- Sin parámetros

SELECT
    id, codigo, descripcion, categoria,
    stock_actual, stock_minimo,
    (stock_minimo - stock_actual) as faltante
FROM inventario
WHERE stock_actual <= stock_minimo
  AND activo = 1
ORDER BY (stock_minimo - stock_actual) DESC