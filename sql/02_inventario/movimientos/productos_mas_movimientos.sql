-- productos_mas_movimientos.sql
-- Top 10 productos con más movimientos en el último mes
-- Sin parámetros

SELECT TOP 10
    p.codigo, p.descripcion,
    COUNT(m.id) as total_movimientos
FROM inventario p
INNER JOIN movimientos_inventario m ON p.id = m.producto_id
WHERE m.fecha_movimiento >= DATEADD(MONTH, -1, GETDATE())
GROUP BY p.id, p.codigo, p.descripcion
ORDER BY COUNT(m.id) DESC