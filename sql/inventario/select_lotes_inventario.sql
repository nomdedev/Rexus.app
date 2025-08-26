SELECT 
    l.id,
    l.producto_id,
    l.numero_lote,
    l.cantidad,
    l.fecha_vencimiento,
    l.ubicacion,
    l.estado,
    l.fecha_ingreso,
    p.nombre as producto_nombre,
    p.codigo as producto_codigo
FROM lotes_inventario l
LEFT JOIN productos p ON l.producto_id = p.id
WHERE l.activo = ?
ORDER BY l.fecha_ingreso DESC;
