-- update_estado_reserva_fallback.sql
-- Actualiza el estado de una reserva (método fallback)
-- Parámetros: ? (nuevo_estado), ? (observaciones), ? (fecha_modificacion), ? (reserva_id)

UPDATE reservas_materiales 
SET estado = ?, 
    observaciones = ?,
    fecha_modificacion = ?
WHERE id = ?