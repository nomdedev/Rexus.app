UPDATE reserva_materiales 
SET cantidad_reservada = @nueva_cantidad_reservada,
    cantidad_consumida = cantidad_consumida + @cantidad_consumida,
    observaciones = CONCAT(ISNULL(observaciones, ''), @observacion_parcial),
    fecha_modificacion = @fecha_modificacion
WHERE id = @reserva_id
