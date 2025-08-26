UPDATE reservas_materiales
SET estado = 'CONSUMIDA',
    fecha_consumo = ?,
    cantidad_consumida = ?,
    observaciones_consumo = ?,
    fecha_modificacion = ?
WHERE id = ?
