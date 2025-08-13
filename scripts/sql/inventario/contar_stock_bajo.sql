-- Cuenta productos con stock bajo o crítico
SELECT COUNT(*) FROM inventario_perfiles
WHERE stock_actual <= stock_minimo