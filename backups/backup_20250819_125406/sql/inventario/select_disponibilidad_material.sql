SELECT
    i.id,
    i.codigo,
    i.descripcion,
    i.tipo as categoria,
    i.stock as stock_actual,
    i.stock_minimo,
    i.precio as precio_unitario,
    i.unidad_medida,
    COALESCE(r.stock_reservado, 0) as stock_reservado,
    (i.stock - COALESCE(r.stock_reservado, 0)) as stock_disponible
FROM inventario_perfiles i
LEFT JOIN (
    SELECT
        producto_id,
        SUM(cantidad_reservada) as stock_reservado
    FROM reserva_materiales
    WHERE estado = 'ACTIVA'
    GROUP BY producto_id
) r ON i.id = r.producto_id
WHERE i.id = ?
    AND i.activo = 1;