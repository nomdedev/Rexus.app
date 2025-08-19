SELECT
    c.id,
    ISNULL(c.numero_orden, CAST(c.id AS VARCHAR(10))) as numero_orden,
    c.estado,
    c.fecha_orden as fecha_pedido,
    c.fecha_entrega_esperada as fecha_entrega_estimada,
    c.fecha_creacion,
    c.updated_at as fecha_actualizacion,
    CAST(ISNULL(c.observaciones, '') AS NVARCHAR(MAX)) as observaciones,
    ISNULL(c.usuario_creacion, 'SISTEMA') as usuario_creacion,
    ISNULL(c.subtotal, 0.0) as subtotal,
    ISNULL(c.impuestos, 0.0) as impuestos,
    ISNULL(c.total, 0.0) as total_final,
    c.proveedor_id,
    'PROVEEDOR_' + CAST(c.proveedor_id AS VARCHAR(10)) as proveedor,
    ISNULL(detalle_info.cantidad_items, 0) as cantidad_items,
    ISNULL(detalle_info.total_calculado, 0) as total_calculado
FROM compras c
LEFT JOIN (
    SELECT
        compra_id,
        COUNT(id) as cantidad_items,
        SUM(cantidad * precio_unitario) as total_calculado
    FROM detalle_compras
    GROUP BY compra_id
) detalle_info ON c.id = detalle_info.compra_id
ORDER BY c.fecha_creacion DESC