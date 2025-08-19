SELECT
    SUM(CASE WHEN estado = 'BORRADOR' THEN 1 ELSE 0 END) as total_borradores,
    SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as total_pendientes,
    SUM(CASE WHEN estado = 'APROBADO' THEN 1 ELSE 0 END) as total_aprobados,
    SUM(CASE WHEN estado = 'EN_PREPARACION' THEN 1 ELSE 0 END) as total_preparacion,
    SUM(CASE WHEN estado = 'LISTO_ENTREGA' THEN 1 ELSE 0 END) as total_listos,
    SUM(CASE WHEN estado = 'EN_TRANSITO' THEN 1 ELSE 0 END) as total_transito,
    SUM(CASE WHEN estado = 'ENTREGADO' THEN 1 ELSE 0 END) as total_entregados,
    SUM(CASE WHEN estado = 'CANCELADO' THEN 1 ELSE 0 END) as total_cancelados,
    SUM(CASE WHEN estado = 'FACTURADO' THEN 1 ELSE 0 END) as total_facturados,
    SUM(CASE WHEN tipo_pedido = 'MATERIAL' THEN 1 ELSE 0 END) as total_material,
    SUM(CASE WHEN tipo_pedido = 'HERRAMIENTA' THEN 1 ELSE 0 END) as total_herramientas,
    SUM(CASE WHEN tipo_pedido = 'SERVICIO' THEN 1 ELSE 0 END) as total_servicios,
    SUM(CASE WHEN tipo_pedido = 'VIDRIO' THEN 1 ELSE 0 END) as total_vidrios,
    SUM(CASE WHEN tipo_pedido = 'HERRAJE' THEN 1 ELSE 0 END) as total_herrajes,
    SUM(CASE WHEN tipo_pedido = 'MIXTO' THEN 1 ELSE 0 END) as total_mixtos,
    SUM(CASE WHEN prioridad = 'BAJA' THEN 1 ELSE 0 END) as total_baja,
    SUM(CASE WHEN prioridad = 'NORMAL' THEN 1 ELSE 0 END) as total_normal,
    SUM(CASE WHEN prioridad = 'ALTA' THEN 1 ELSE 0 END) as total_alta,
    SUM(CASE WHEN prioridad = 'URGENTE' THEN 1 ELSE 0 END) as total_urgente,
    COUNT(*) as total_pedidos,
    SUM(total) as monto_total,
    AVG(total) as monto_promedio,
    SUM(CASE WHEN estado IN ('ENTREGADO', 'FACTURADO') THEN total ELSE 0 END) as monto_entregado,
    SUM(CASE WHEN estado = 'CANCELADO' THEN total ELSE 0 END) as monto_cancelado,
    AVG(DATEDIFF(DAY, fecha_pedido, COALESCE(fecha_entrega_real, GETDATE()))) as dias_promedio_entrega,
    COUNT(CASE WHEN fecha_entrega_real > fecha_entrega_solicitada THEN 1 END) as entregas_tardias
FROM [pedidos]
WHERE activo = 1
    AND (@fecha_desde IS NULL OR fecha_pedido >= @fecha_desde)
    AND (@fecha_hasta IS NULL OR fecha_pedido <= @fecha_hasta);