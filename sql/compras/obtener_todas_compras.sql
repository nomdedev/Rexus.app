-- Obtener todas las órdenes de compra con totales calculados
SELECT
    c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
    c.fecha_entrega_estimada, c.estado, c.observaciones,
    c.usuario_creacion, c.descuento, c.impuestos,
    c.fecha_creacion, c.fecha_actualizacion,
    ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) as total_sin_descuento,
    ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) - c.descuento + c.impuestos as total_final
FROM compras c
LEFT JOIN detalle_compras dc ON c.id = dc.compra_id
GROUP BY c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
         c.fecha_entrega_estimada, c.estado, c.observaciones,
         c.usuario_creacion, c.descuento, c.impuestos,
         c.fecha_creacion, c.fecha_actualizacion
ORDER BY c.fecha_creacion DESC