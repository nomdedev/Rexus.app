-- Actualización segura para liberar reserva de material
-- Cambia el estado a LIBERADA y registra información de liberación
-- Utiliza parámetros seguros para prevenir SQL injection

UPDATE reserva_materiales 
SET 
    estado = 'LIBERADA',
    fecha_liberacion = ?,
    motivo_liberacion = ?
WHERE id = ?
    AND estado = 'ACTIVA';