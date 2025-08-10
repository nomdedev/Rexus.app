-- scripts/sql/logistica/actualizar_estado_entrega_sin_fecha.sql
-- Actualiza el estado de una entrega sin cambiar fecha de entrega
UPDATE [entregas]
SET estado = ?, observaciones = ?
WHERE id = ?