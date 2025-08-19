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
        WHEN SUM(pd.cantidad - ISNULL(pd.cantidad, 0)) = 0 THEN 'COMPLETO'
        WHEN COUNT(pd.id) > 0 THEN 'PARCIAL'
        ELSE 'PENDIENTE'
    END as estado_entrega
FROM [pedidos] p
LEFT JOIN [pedidos_detalle] pd ON p.id = pd.pedido_id
WHERE p.activo = 1
    AND (? IS NULL OR p.estado = ?)
    AND (? IS NULL OR p.tipo_pedido = ?)
    AND (? IS NULL OR p.cliente_id = ?)
    AND (? IS NULL OR p.obra_id = ?)
    AND (? IS NULL OR p.fecha_pedido >= ?)
    AND (? IS NULL OR p.fecha_pedido <= ?)
    AND (? IS NULL OR (
        p.numero_pedido LIKE '%' + ? + '%' OR
        p.observaciones LIKE '%' + ? + '%' OR
        p.responsable_entrega LIKE '%' + ? + '%'
    ))
GROUP BY
    p.id, p.numero_pedido, p.cliente_id, p.obra_id, p.fecha_pedido,
    p.fecha_entrega_solicitada, p.fecha_entrega_real, p.estado, p.tipo_pedido,
    p.prioridad, p.subtotal, p.descuento, p.impuestos, p.total,
    p.observaciones, p.direccion_entrega, p.responsable_entrega,
    p.telefono_contacto, p.usuario_creador, p.usuario_aprobador,
    p.fecha_aprobacion, p.fecha_creacion, p.fecha_modificacion
ORDER BY p.fecha_pedido DESC
OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;