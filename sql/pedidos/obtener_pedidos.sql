-- Consulta para obtener pedidos con filtros
-- Parámetros: :estado, :obra_id, :fecha_desde, :fecha_hasta, :activo
-- Retorna: Lista de pedidos filtrados

SELECT 
    p.id,
    p.numero_pedido,
    p.obra_id,
    p.fecha_pedido,
    p.fecha_entrega_estimada,
    p.estado,
    p.total,
    p.proveedor,
    CAST(p.observaciones AS NVARCHAR(MAX)) as observaciones,
    p.usuario_creacion,
    p.fecha_creacion,
    p.activo,
    o.nombre as obra_nombre,
    CASE 
        WHEN p.fecha_entrega_estimada < GETDATE() AND p.estado != 'Entregado' THEN 'Atrasado'
        WHEN p.estado = 'Entregado' THEN 'Completado'
        ELSE p.estado
    END as estado_actual
FROM pedidos p
LEFT JOIN obras o ON p.obra_id = o.id
WHERE p.activo = ISNULL(:activo, 1)
  AND (:estado IS NULL OR p.estado = :estado)
  AND (:obra_id IS NULL OR p.obra_id = :obra_id)
  AND (:fecha_desde IS NULL OR p.fecha_pedido >= :fecha_desde)
  AND (:fecha_hasta IS NULL OR p.fecha_pedido <= :fecha_hasta)
ORDER BY p.fecha_creacion DESC;