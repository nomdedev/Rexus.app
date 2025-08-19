SELECT COUNT(DISTINCT obra_id) as obras_con_reservas
FROM reserva_materiales
WHERE estado = 'ACTIVA';