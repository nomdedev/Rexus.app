-- Consultas para estadísticas de inventario
-- Utiliza la tabla consolidada 'productos'

-- Total de productos activos
SELECT COUNT(*) as total_productos FROM productos WHERE activo = 1;

-- Productos con stock bajo
SELECT COUNT(*) as stock_bajo FROM productos
WHERE stock_actual <= stock_minimo AND activo = 1;

-- Valor total del inventario
SELECT SUM(stock_actual * precio_unitario) as valor_total FROM productos
WHERE activo = 1;