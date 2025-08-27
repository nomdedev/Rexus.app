-- Liberar reserva de material (marcar como liberada)
-- Parámetros: :reserva_id, :motivo_liberacion, :usuario
-- Retorna: filas afectadas

UPDATE reserva_materiales 
SET estado = 'LIBERADA', 
    fecha_liberacion = GETDATE(), 
    motivo_liberacion = :motivo_liberacion,
    usuario_liberacion = :usuario
WHERE id = :reserva_id AND estado = 'ACTIVA';