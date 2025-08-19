SELECT
    p.id,
    p.numero_pedido,
    p.cliente_id,
    p.obra_id,
    p.fecha_pedido,
    p.fecha_entrega_solicitada,
    p.fecha_entrega_real,
    p.estado,
    p.tipo_pedido,
    p.prioridad,
    p.subtotal,
    p.descuento,
    p.impuestos,
    p.total,
    p.observaciones,
    p.direccion_entrega,
    p.responsable_entrega,
    p.telefono_contacto,
    p.usuario_creador,
    p.usuario_aprobador,
    p.fecha_aprobacion,
    p.fecha_creacion,
    p.fecha_modificacion,
    COUNT(pd.id) as total_items,
    CASE
        WHEN SUM(pd.cantidad - COALESCE(pd.cantidad_entregada, 0)) = 0 THEN 'COMPLETO'
        WHEN SUM(pd.cantidad_entregada) > 0 THEN 'PARCIAL'
        ELSE 'PENDIENTE'
    END as estado_entrega
FROM [pedidos] p
LEFT JOIN [pedidos_detalle] pd ON p.id = pd.pedido_id
WHERE p.activo = 1
    AND (@estado IS NULL OR p.estado = @estado)
    AND (@tipo_pedido IS NULL OR p.tipo_pedido = @tipo_pedido)
    AND (@cliente_id IS NULL OR p.cliente_id = @cliente_id)
    AND (@obra_id IS NULL OR p.obra_id = @obra_id)
    AND (@fecha_desde IS NULL OR p.fecha_pedido >= @fecha_desde)
    AND (@fecha_hasta IS NULL OR p.fecha_pedido <= @fecha_hasta)
    AND (@busqueda IS NULL OR (
        p.numero_pedido LIKE '%' + @busqueda + '%' OR
        p.observaciones LIKE '%' + @busqueda + '%' OR
        p.responsable_entrega LIKE '%' + @busqueda + '%'
    ))
GROUP BY
    p.id, p.numero_pedido, p.cliente_id, p.obra_id, p.fecha_pedido,
    p.fecha_entrega_solicitada, p.fecha_entrega_real, p.estado, p.tipo_pedido,
    p.prioridad, p.subtotal, p.descuento, p.impuestos, p.total,
    p.observaciones, p.direccion_entrega, p.responsable_entrega,
    p.telefono_contacto, p.usuario_creador, p.usuario_aprobador,
    p.fecha_aprobacion, p.fecha_creacion, p.fecha_modificacion
ORDER BY p.fecha_pedido DESC
OFFSET @offset ROWS FETCH NEXT @limit ROWS ONLY;