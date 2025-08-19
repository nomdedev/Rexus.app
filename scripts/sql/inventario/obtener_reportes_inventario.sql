SELECT
    ip.id,
    ip.codigo,
    ip.tipo,
    ip.ancho_mm,
    ip.alto_mm,
    ip.largo_mm,
    ip.peso_kg,
    ip.color,
    ip.descripcion,
    ip.precio_unitario,
    ip.stock_actual,
    ip.stock_minimo,
    ip.proveedor,
    ip.fecha_creacion,
    ip.fecha_modificacion,
    CASE
        WHEN ip.stock_actual = 0 THEN 'Sin Stock'
        WHEN ip.stock_actual <= ip.stock_minimo THEN 'Stock Bajo'
        ELSE 'En Stock'
    END as estado_stock
FROM inventario_perfiles ip
WHERE ip.activo = 1
ORDER BY ip.tipo, ip.codigo