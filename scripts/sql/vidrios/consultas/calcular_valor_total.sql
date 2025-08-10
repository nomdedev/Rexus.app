-- Calcula el valor total del inventario de vidrios
SELECT COALESCE(SUM(v.precio * v.stock), 0) as valor_total
FROM vidrios v
WHERE v.activo = 1;
