SELECT h.*, i.stock_actual, i.stock_reservado, i.ubicacion, i.fecha_ultima_entrada, i.fecha_ultima_salida
FROM productos h
LEFT JOIN productos i ON h.id = i.herraje_id
WHERE h.id = @id AND h.estado = 'ACTIVO'; AND categoria = \'HERRAJE\'