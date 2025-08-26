SELECT id, producto_id, obra_id, cantidad_reservada, motivo,
       usuario_reserva, fecha_creacion, fecha_vencimiento, estado,
       cantidad_consumida, observaciones, fecha_modificacion
FROM reserva_materiales 
WHERE id = @reserva_id
