UPDATE reserva_materiales 
SET estado = @nuevo_estado, 
    observaciones = @observaciones,
    fecha_modificacion = @fecha_modificacion
WHERE id = @reserva_id
