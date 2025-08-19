SELECT
    c.id,
    ISNULL(c.numero_orden, CAST(c.id AS VARCHAR(10))) as numero_orden,
    c.estado,
    c.fecha_creacion,
    ISNULL(c.observaciones, '') as observaciones,
    ISNULL(c.usuario_creacion, 'SISTEMA') as usuario_creacion,
    0.0 as descuento,
    0.0 as impuestos,
    c.fecha_creacion as fecha_pedido,
    c.fecha_creacion as fecha_entrega_estimada,
    'PROVEEDOR_' + CAST(c.id AS VARCHAR(10)) as proveedor,
    ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) as total_sin_descuento,
    ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) as total_final
FROM compras c
LEFT JOIN detalle_compras dc ON c.id = dc.compra_id
GROUP BY c.id, c.numero_orden, c.estado, c.fecha_creacion, c.observaciones, c.usuario_creacion
ORDER BY c.fecha_creacion DESC