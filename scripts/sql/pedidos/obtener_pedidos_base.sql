-- Obtener pedidos con detalles (consulta base)
-- Archivo: obtener_pedidos_base.sql

SELECT 
    p.id, 
    p.numero_pedido, 
    p.fecha_pedido, 
    p.fecha_entrega_solicitada,
    p.estado, 
    p.tipo_pedido, 
    p.prioridad, 
    p.total, 
    p.observaciones,
    p.responsable_entrega, 
    p.obra_id,
    COUNT(pd.id) as cantidad_items,
    SUM(pd.cantidad) as total_cantidad,
    SUM(CASE WHEN (pd.cantidad - COALESCE(pd.cantidad_entregada, 0)) > 0 
         THEN (pd.cantidad - COALESCE(pd.cantidad_entregada, 0)) 
         ELSE 0 END) as cantidad_pendiente
FROM pedidos p
LEFT JOIN pedidos_detalle pd ON p.id = pd.pedido_id
WHERE p.activo = 1
GROUP BY p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
         p.estado, p.tipo_pedido, p.prioridad, p.total, p.observaciones,
         p.responsable_entrega, p.obra_id
ORDER BY p.fecha_pedido DESC;
