SELECT SUM(r.cantidad_reservada * i.precio_unitario) as valor_total_reservado
FROM reserva_materiales r
INNER JOIN inventario_perfiles i ON r.producto_id = i.id
WHERE r.estado = 'ACTIVA';