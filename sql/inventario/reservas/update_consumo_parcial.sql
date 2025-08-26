UPDATE reservas_materiales
SET cantidad_reservada = ?,
    cantidad_consumida = ISNULL(cantidad_consumida, 0) + ?,
    observaciones_consumo = ISNULL(observaciones_consumo, '') + ?
WHERE id = ?
