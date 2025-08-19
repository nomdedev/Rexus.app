SELECT COUNT(*) as total_productos FROM productos WHERE activo = 1;
SELECT COUNT(*) as stock_bajo FROM productos
WHERE stock_actual <= stock_minimo AND activo = 1;
SELECT SUM(stock_actual * precio_unitario) as valor_total FROM productos
WHERE activo = 1;