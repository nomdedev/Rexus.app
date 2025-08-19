UPDATE reserva_materiales
SET
    estado = 'LIBERADA',
    fecha_liberacion = ?,
    motivo_liberacion = ?
WHERE id = ?
    AND estado = 'ACTIVA';