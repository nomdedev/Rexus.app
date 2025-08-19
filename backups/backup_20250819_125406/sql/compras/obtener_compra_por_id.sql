SELECT TOP 1
    id, proveedor, numero_orden, fecha_pedido,
    fecha_entrega_estimada, estado, observaciones,
    usuario_creacion, fecha_creacion, descuento,
    impuestos
FROM compras
WHERE id = ?