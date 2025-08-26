SELECT
    r.id, r.producto_id, r.obra_id, r.cantidad_reservada,
    r.motivo, r.usuario_reserva, r.fecha_creacion, r.fecha_vencimiento,
    r.estado, r.cantidad_consumida,
    p.codigo as producto_codigo, p.descripcion as producto_descripcion,
    p.stock_actual, p.unidad_medida,
    o.nombre as obra_nombre
FROM reserva_materiales r
INNER JOIN inventario p ON r.producto_id = p.id
LEFT JOIN obras o ON r.obra_id = o.id
WHERE r.estado = 'ACTIVA' AND r.obra_id = @obra_id
ORDER BY r.fecha_vencimiento ASC
