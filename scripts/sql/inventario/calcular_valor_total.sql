-- Calcula el valor total del inventario
SELECT SUM(stock_actual * ISNULL(importe, 0)) FROM inventario_perfiles