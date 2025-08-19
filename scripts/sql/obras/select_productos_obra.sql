SELECT
    po.id, po.obra_id, po.producto_id, po.cantidad_requerida,
    po.cantidad_asignada, po.cantidad_utilizada, po.etapa_obra,
    po.fecha_asignacion, po.observaciones,
    p.codigo, p.descripcion, p.categoria, p.unidad_medida,
    p.precio_unitario, p.stock_actual
FROM productos_obra po
INNER JOIN productos p ON po.producto_id = p.id
WHERE po.obra_id = ? AND po.activo = 1
ORDER BY po.fecha_asignacion;