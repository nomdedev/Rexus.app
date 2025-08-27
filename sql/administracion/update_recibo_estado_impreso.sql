-- update_recibo_estado_impreso.sql
-- Actualiza el estado de impresión de un recibo
-- Parámetros: ? (fecha_actualizacion), ? (usuario_actualizacion), ? (recibo_id)

UPDATE recibos
SET impreso = 1,
    fecha_actualizacion = ?,
    usuario_actualizacion = ?
WHERE id = ?