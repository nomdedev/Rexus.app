SELECT
    i.id,
    i.codigo,
    i.descripcion,
    i.categoria,
    i.unidad_medida,
    i.stock_actual,
    ISNULL(i.stock_reservado, 0) as stock_reservado,
    (i.stock_actual - ISNULL(i.stock_reservado, 0)) as stock_disponible,
    i.stock_minimo,
    i.stock_maximo,
    CASE
        WHEN (i.stock_actual - ISNULL(i.stock_reservado, 0)) <= i.stock_minimo THEN 'BAJO'
        WHEN (i.stock_actual - ISNULL(i.stock_reservado, 0)) = 0 THEN 'AGOTADO'
        ELSE 'NORMAL'
    END as estado_stock
FROM inventario_perfiles i
WHERE (@producto_id IS NULL OR i.id = @producto_id)
ORDER BY i.codigo;