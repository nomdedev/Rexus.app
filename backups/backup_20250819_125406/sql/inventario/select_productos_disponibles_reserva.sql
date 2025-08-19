SELECT
    i.id,
    i.codigo,
    i.descripcion,
    i.categoria,
    i.stock_actual,
    i.precio_unitario,
    i.unidad_medida,
    COALESCE(r.stock_reservado, 0) as stock_reservado,
    (i.stock_actual - COALESCE(r.stock_reservado, 0)) as stock_disponible
FROM inventario_perfiles i
LEFT JOIN (
    SELECT
        producto_id,
        SUM(cantidad_reservada) as stock_reservado
    FROM reserva_materiales
    WHERE estado = 'ACTIVA'
    GROUP BY producto_id
) r ON i.id = r.producto_id
WHERE i.activo = 1
    AND (i.stock_actual - COALESCE(r.stock_reservado, 0)) > 0
ORDER BY i.codigo;