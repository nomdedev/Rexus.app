SELECT
    v.proveedor,
    COUNT(*) as total_productos,
    SUM(v.stock * v.precio) as valor_inventario,
    AVG(v.precio) as precio_promedio,
    COUNT(CASE WHEN v.stock < v.stock_minimo THEN 1 END) as productos_stock_bajo
FROM vidrios v
WHERE v.activo = 1
GROUP BY v.proveedor
ORDER BY valor_inventario DESC;