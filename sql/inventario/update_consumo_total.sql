UPDATE reserva_materiales 
SET estado = 'CONSUMIDA',
    cantidad_consumida = @cantidad_consumida,
    observaciones = @observaciones,
    fecha_modificacion = @fecha_modificacion
WHERE id = @reserva_id
