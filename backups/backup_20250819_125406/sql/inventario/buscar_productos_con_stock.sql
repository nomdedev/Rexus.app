SELECT
    i.id,
    i.codigo,
    i.descripcion,
    i.categoria,
    i.stock_actual,
    i.stock_minimo,
    i.precio_unitario,
    i.unidad_medida,
    i.activo,
    i.fecha_actualizacion,
    COALESCE(r.stock_reservado, 0) as stock_reservado,
    CASE
        WHEN i.stock_actual <= 0 THEN 'AGOTADO'
        WHEN i.stock_actual <= i.stock_minimo THEN 'BAJO'
        ELSE 'NORMAL'
    END as estado_stock
FROM inventario_perfiles i
LEFT JOIN (
    SELECT producto_id, SUM(cantidad_reservada) as stock_reservado
    FROM reserva_materiales
    WHERE estado = 'ACTIVA'
    GROUP BY producto_id
) r ON i.id = r.producto_id
WHERE i.activo = 1
    AND (@busqueda IS NULL OR i.descripcion LIKE '%' + @busqueda + '%' OR i.codigo LIKE '%' + @busqueda + '%')
    AND (@categoria IS NULL OR i.categoria = @categoria)
ORDER BY i.descripcion;