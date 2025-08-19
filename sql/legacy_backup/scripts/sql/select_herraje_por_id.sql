SELECT h.*, i.stock_actual, i.stock_reservado, i.ubicacion, i.fecha_ultima_entrada, i.fecha_ultima_salida
FROM herrajes h
LEFT JOIN herrajes_inventario i ON h.id = i.herraje_id
WHERE h.id = @id AND h.estado = 'ACTIVO';